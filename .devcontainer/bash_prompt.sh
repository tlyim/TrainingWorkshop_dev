__bash_prompt() {
    local userpart='`export XIT=$? \
        && [ -n "${GITHUB_USER:-}" ] && echo -n "\[\033[0;32m\]@${GITHUB_USER} " || echo -n "\[\033[0;32m\]\u " \
        && [ "$XIT" -ne 0 ] && echo -n "\[\033[1;31m\]➜" || echo -n "\[\033[0m\]➜"`'

    local gitbranch='`\
        BRANCH="$(git --no-optional-locks symbolic-ref --short HEAD 2>/dev/null || git --no-optional-locks rev-parse --short HEAD 2>/dev/null)"
        [ -n "$BRANCH" ] && printf "\[\033[0;36m\](\[\033[1;31m\]%s\[\033[0;36m\]) " "$BRANCH"`'

    PS1="${userpart} \[\033[1;34m\]\w\[\033[0m\] ${gitbranch}\$ "
}

__bash_prompt
export PROMPT_DIRTRIM=4
