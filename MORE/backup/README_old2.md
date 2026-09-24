# TrainingWorkshop

---
---

### Lightning.ai-specific requirements

To clone GitHub repo as a Lightning.ai Studio (/teamspace/studios/this_studio) directly, not as a subfolder of this_studio/, follow the steps below:

- Create a new Lightning.ai Studio
- In the Explorer, delete all visible files (do NOT delete hidden files with a terminal)
- Use terminal commands below to clone the GitHub repo:

```bash
cd /teamspace/studios/this_studio
git init
git remote add origin https://github.com/DrAYim/TrainingWorkshop.git
git fetch origin
# replace 'main' with the repo default branch if needed (e.g., master)
git checkout -f -t origin/main
```

- Put the Studio into sleep, then restart it to activate the first-time `on_start.sh`
- Change the `Live Preview: Open Preview Target` setting from `Embedded Preview` to `External Browser`

- Use `Port viewer, then +Add new port` to enable the ports below for viewing rendered html pages and web apps
    - Ports:
        - marimo 2718
        - local http server 8000
        - live preview 3000 (note: do not work)

---

To stop tracking the `.lightning_studio/.setup_done` file in your Git repository, add it to your .gitignore file. 

If the file is already tracked, run the terminal command below to remove it from version control but keeps the file locally:

```bash
git rm --cached .lightning_studio/.setup_done
```

---
---

### In general

Steps to turn a private repo into a public image on GitHub Container Registry (GHCR):

0. Once you have everything working, 

- Create a `Dockerfile` in your repo based on the flow of `.devcontainer.json`.
- Place `Dockerfile` in repo root (for registering with GHCR/Docker Hub)

1. Create a Personal Access Token (PAT)

- Go to GitHub → Settings → Developer Settings → Personal Access Tokens
- Create a token with the `write:packages`, `read:packages`, and `delete:packages` scopes

2. Log in to GHCR

```bash
echo ghp_xxxxxxxxxxxxxxxxxxxx | docker login ghcr.io -u DrAYim --password-stdin
```

3. Navigate to the correct folder where your `Dockerfile` is. Then build and tag the image 

- note the trailing dot `.`; 
- repo name must be lowercase
- use `--no-cache` to force a full rebuild

```bash
docker build -t ghcr.io/DrAYim/TrainingWorkshop:latest . --no-cache
```

4. Push the image

```bash
docker push ghcr.io/DrAYim/TrainingWorkshop:latest
```

5. Make the package public

- Go to your GitHub profile → Packages → click your image
- Click Package settings (bottom right)
- Scroll to Danger Zone → Change visibility → set to Public

---

To have context-aware Copy with `Ctrl+c` in VS Code terminal (instead of the Interrupt `^c`), do the below:

- Ensure the line `"terminal.integrated.sendKeybindingsToShell": true,` is removed from the file `.vscode/settings.json`
    - Use `Ctrl+` to open VS Code Settings, search for `terminal.integrated.sendKeybindingsToShell`, and uncheck it
- In the VS Code editor panel, `Ctrl+Shift+P` and type and select `Open Keyboard Shortcuts (JSON)` to open the `keybindings.json`
- Add the below to the beginning of `keybindings.json` and `Ctrl-s` to save it:

```keybindings.json
    // conttext-aware copy in terminal (instead of the ^c interrupt)
    {
    "key": "ctrl+c",
    "command": "workbench.action.terminal.copySelection",
    "when": "terminalFocus && terminalTextSelectedInFocusedTerminal"
    },
```
- Optionally, can add the below for Paste-with-Ctrl+v if not already there:

```keybindings.json
    {
      "key": "ctrl+v",
      "command": "-workbench.action.terminal.sendSequence",
      "when": "terminalFocus && !accessibilityModeEnabled && terminalShellType == 'pwsh'"
    },
```

---

To manage trusted domains, 

- Use `Ctrl-Shift-P` to open command palette 
- type `Manage Trusted Domains`

---

To push changes for the first time, first find the email alias provided on GitHub. Go to account `Settings | Emails` and look for the sentence beginning with "All web-based Git operations will be linked to". The format of the email alias (without the square brackets) is `12345678+[username]@users.noreply.github.com`. Next, configure the identity using terminal commands:

```bash
git config --global user.name "Your Name"
git config --global user.email "12345678+[username]@users.noreply.github.com"
```

---

To check / change your default Git editor:

```bash
# Check current editor
git config --global core.editor

# Set to nano (recommended if unsure)
git config --global core.editor "nano"
```

---

**Use with caution!** Reinitiate commit history fully

- Run the below in a terminal (better than a step-by-step manual run): 

```bash
bash resetGitHist.sh
```

