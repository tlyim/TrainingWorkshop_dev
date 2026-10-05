// Cloudflare Worker — LLM API proxy for the marimo WASM notebook.
//
// Paste this file into the Cloudflare dashboard:
//   Workers & Pages -> Create -> "Hello World" template -> Deploy
//   -> Edit code -> replace everything with this file -> Deploy
//
// Then add your provider keys as SECRETS:
//   Settings -> Variables and Secrets -> Add -> type "Secret"
//   GOOGLE_API_KEY, OLLAMA_API_KEY, OPENCODE_GO_API_KEY
//
// This Worker ONLY proxies API calls. It does NOT serve the notebook page
// (the page lives on GitHub Pages). Requests to any non-/api path return 404.
//
// Security model:
//   - Provider secrets live only in Worker environment variables (secrets).
//   - A visitor's own key (BYO) is sent DIRECTLY to the provider from the
//     browser and never reaches this Worker.
//   - This Worker never logs or stores any key.
//   - CORS is restricted to the origins listed below (a speed bump, not
//     authentication — curl can spoof the Origin header).

// ---------------------------------------------------------------------------
// CONFIG — edit these two values
// ---------------------------------------------------------------------------

// Origins allowed to call this Worker. Add your GitHub Pages origin, e.g.
// "https://alice.github.io" (no path, no trailing slash). Keep
// "http://localhost:2718" (or your local marimo port) for local testing.
const ALLOWED_ORIGINS = [
  "http://localhost:2718",
  "http://localhost:8787",
  // "https://<your-username>.github.io",  // <-- add your GitHub Pages origin
];

// Provider whitelist: name -> { base_url, api_key_env }.
// base_url is a fixed constant (SSRF-safe: we never forward a URL from the
// client). api_key_env is the Worker secret that holds the key.
const PROVIDERS = {
  "Google Gemini": {
    base_url: "https://generativelanguage.googleapis.com/v1beta/openai",
    api_key_env: "GOOGLE_API_KEY",
  },
  "Ollama Cloud": {
    base_url: "https://ollama.com/v1",
    api_key_env: "OLLAMA_API_KEY",
  },
  "OpenCode Go": {
    base_url: "https://opencode.ai/zen/go/v1",
    api_key_env: "OPENCODE_GO_API_KEY",
  },
};

// Rate limits advertised to the notebook (in-memory per-isolate counters).
const RATE_LIMIT_INFO = { chat_limit: 50, models_limit: 10, period: 90 };

// Hard cap on max_tokens forwarded to providers (protects the default key).
const MAX_TOKENS_CAP = 8192;

const USER_AGENT = "marimo-llm-example/0.1";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function json(data, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      ...extraHeaders,
    },
  });
}

// CORS headers for an allowed origin (or none if the origin is not allowed).
function corsHeaders(request) {
  const origin = request.headers.get("Origin") || "";
  if (ALLOWED_ORIGINS.includes(origin)) {
    return {
      "Access-Control-Allow-Origin": origin,
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
      "Vary": "Origin",
    };
  }
  return {};
}

// Resolve the API key for a provider: the visitor's key (if provided) wins;
// otherwise the Worker secret. Never logs the key.
function resolveKey(providerName, bodyApiKey, env) {
  const provider = PROVIDERS[providerName];
  if (!provider) {
    return { error: `unknown provider: ${providerName}` };
  }
  if (typeof bodyApiKey === "string" && bodyApiKey.trim()) {
    return { key: bodyApiKey.trim(), source: "user" };
  }
  const secret = env[provider.api_key_env];
  if (secret) {
    return { key: secret, source: "server" };
  }
  return { error: `no API key configured for ${providerName}` };
}

// In-memory per-IP rate limiter (per Cloudflare isolate). A speed bump, not
// a guarantee — the real cost cap is the provider-side quota on the key.
function makeRateLimiter(limit, period) {
  const buckets = new Map();
  return async (ip) => {
    const now = Date.now();
    const windowMs = period * 1000;
    const bucket = buckets.get(ip);
    if (!bucket || now - bucket.start > windowMs) {
      buckets.set(ip, { start: now, count: 1 });
      return true;
    }
    if (bucket.count >= limit) {
      return false;
    }
    bucket.count += 1;
    return true;
  };
}

// Created ONCE at module scope so the counters persist across requests
// within a Cloudflare isolate.
const chatLimiter = makeRateLimiter(
  RATE_LIMIT_INFO.chat_limit,
  RATE_LIMIT_INFO.period,
);
const modelsLimiter = makeRateLimiter(
  RATE_LIMIT_INFO.models_limit,
  RATE_LIMIT_INFO.period,
);

// ---------------------------------------------------------------------------
// Worker
// ---------------------------------------------------------------------------

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const headers = corsHeaders(request);

    // CORS preflight.
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers });
    }

    // Only /api/* paths are handled; everything else is 404 (the page is
    // served by GitHub Pages, not this Worker).
    if (!url.pathname.startsWith("/api/")) {
      return json({ error: "not found" }, 404, headers);
    }

    // Which providers hold a secret, and what rate limits apply.
    // Deliberately contains NO keys.
    if (url.pathname === "/api/config" && request.method === "GET") {
      const providers = {};
      for (const [name, p] of Object.entries(PROVIDERS)) {
        providers[name] = { configured: Boolean(env[p.api_key_env]) };
      }
      return json({ providers, rate_limit: RATE_LIMIT_INFO }, 200, headers);
    }

    // Proxy: list models for a provider.
    if (url.pathname === "/api/models" && request.method === "POST") {
      const ip = request.headers.get("CF-Connecting-IP") || "unknown";
      if (!(await modelsLimiter(ip))) {
        return json(
          { error: `rate limit exceeded: ${RATE_LIMIT_INFO.models_limit} model-list requests per ${RATE_LIMIT_INFO.period}s` },
          429,
          headers,
        );
      }
      const body = await request.json();
      const resolved = resolveKey(body.provider, body.api_key, env);
      if (resolved.error) {
        return json({ error: resolved.error }, 400, headers);
      }
      const provider = PROVIDERS[body.provider];
      try {
        const upstream = await fetch(`${provider.base_url}/models`, {
          headers: {
            Authorization: `Bearer ${resolved.key}`,
            "User-Agent": USER_AGENT,
          },
        });
        const text = await upstream.text();
        let data;
        try {
          data = JSON.parse(text);
        } catch {
          return json(
            { error: `upstream returned non-JSON (HTTP ${upstream.status})` },
            upstream.status >= 400 ? upstream.status : 502,
            headers,
          );
        }
        return json({ data: data.data || [] }, upstream.status, headers);
      } catch (e) {
        return json({ error: `upstream fetch failed: ${e.message}` }, 502, headers);
      }
    }

    // Proxy: chat completion for a provider.
    if (url.pathname === "/api/chat/completions" && request.method === "POST") {
      const ip = request.headers.get("CF-Connecting-IP") || "unknown";
      if (!(await chatLimiter(ip))) {
        return json(
          { error: `rate limit exceeded: ${RATE_LIMIT_INFO.chat_limit} chat requests per ${RATE_LIMIT_INFO.period}s` },
          429,
          headers,
        );
      }
      const body = await request.json();
      const resolved = resolveKey(body.provider, body.api_key, env);
      if (resolved.error) {
        return json({ error: resolved.error }, 400, headers);
      }
      const provider = PROVIDERS[body.provider];
      const headersUpstream = {
        "Content-Type": "application/json",
        Authorization: `Bearer ${resolved.key}`,
        "User-Agent": USER_AGENT,
      };
      if (body.session_id) {
        headersUpstream["x-opencode-session"] = body.session_id;
      }
      const payload = {
        model: body.model,
        messages: body.messages,
        temperature: body.temperature,
        max_tokens: Math.min(Number(body.max_tokens) || 512, MAX_TOKENS_CAP),
      };
      try {
        const upstream = await fetch(`${provider.base_url}/chat/completions`, {
          method: "POST",
          headers: headersUpstream,
          body: JSON.stringify(payload),
        });
        const text = await upstream.text();
        let data;
        try {
          data = JSON.parse(text);
        } catch {
          return json(
            { error: `upstream returned non-JSON (HTTP ${upstream.status})` },
            upstream.status >= 400 ? upstream.status : 502,
            headers,
          );
        }
        return json(data, upstream.status, headers);
      } catch (e) {
        return json({ error: `upstream fetch failed: ${e.message}` }, 502, headers);
      }
    }

    return json({ error: "not found" }, 404, headers);
  },
};