# [use with caution] full reinit 
# *** Run this in a terminal: bash resetGitHist.sh
# (better than a step-by-step manual run)

echo "Removing .git and reinitializing ..."

REMOTE=$(git remote get-url origin 2>/dev/null)

rm -rf .git
git init
git add -A
git commit -m "Initial commit — fresh history"
git branch -M main

if [ -n "$REMOTE" ]; then
  git remote add origin "$REMOTE"
  git push -u --force origin main
else
  echo "WARNING: No remote origin found. Skipping push."
  echo "To push manually, run:"
  echo "  git remote add origin <your_.git_repo-url>"
  echo "  git push -u --force origin main"
fi