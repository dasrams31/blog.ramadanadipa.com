#!/bin/bash
# Backup harian blog.ramadanadipa.com ke GitHub
set -e
STAGE="$HOME/workspace/releases/blog.ramadanadipa.com"
TOKEN_FILE="$HOME/workspace/mc-portal/config/github_token"

cp "$HOME/workspace/blog/build.py" "$STAGE/"
cp "$HOME/workspace/blog/serve.py" "$STAGE/"
rm -rf "$STAGE/content" "$STAGE/static" "$STAGE/templates"
cp -r "$HOME/workspace/blog/content" "$HOME/workspace/blog/static" "$HOME/workspace/blog/templates" "$STAGE/"
cp "$HOME/workspace/blog/topics.md" "$STAGE/"

cd "$STAGE"
git add -A
if git diff --cached --quiet; then
  echo "no changes"
  exit 0
fi
git -c user.name="dasrams31" -c user.email="ramadanadipa176@gmail.com" \
  commit -qm "Daily backup $(date +%F)"

TOKEN="$(cat "$TOKEN_FILE")"
git push "https://dasrams31:${TOKEN}@github.com/dasrams31/blog.ramadanadipa.com.git" main 2>&1 | tail -2
echo "pushed $(date -Is)"

# Mirror ke GitLab (RamsNotes31) - ditambahkan 2026-10-22, bareng GitHub
GL_TOKEN_FILE="$HOME/workspace/mc-portal/config/gitlab_token"
if [ -f "$GL_TOKEN_FILE" ]; then
  GLTOKEN=$(tr -d '\n' < "$GL_TOKEN_FILE")
  git push "https://oauth2:${GLTOKEN}@gitlab.com/RamsNotes31/blog.ramadanadipa.com.git" main 2>&1 | tail -2 || echo "gitlab push failed (github push ok)"
  unset GLTOKEN
fi
