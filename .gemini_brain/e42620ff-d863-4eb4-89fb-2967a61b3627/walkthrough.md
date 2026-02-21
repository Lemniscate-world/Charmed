# Git Push Blocked — Secret Scanning

## Problem

`git push origin main` is rejected by GitHub's **secret scanning push protection**.

The error is **not** a branch divergence issue — `git pull --rebase` confirms the branch is up to date.

## Root Cause

Commit `ff1679d` ("Updates") added this file to the repo:

```
docs/client_secret_318032290599-h56kne5fnokgoipf1if13q1okono0hdg.apps.googleusercontent.com.json
```

It contains a **Google OAuth Client ID** and **Client Secret**. Even though a later commit (`d741642`) removed the file, the secret still exists in the git history, so GitHub blocks the push.

## Current State

```
d741642 (HEAD -> main) security: remove leaked Google OAuth client_secret...
ff1679d Updates                          <-- ⚠️ contains the secret
b590681 docs: add Google Docs API synchronization script
a6ebbff docs: add script to automate session summary export to docx
54a34a5 (origin/main) ci: automate CodeQL/SonarCloud/Windows builds...
```

Local branch is **4 commits ahead** of `origin/main`.

## Resolution Options

### Option A — Rewrite history to remove the secret (recommended)

Use interactive rebase to squash or amend commit `ff1679d` so the secret file never appears in history:

```bash
# Interactive rebase starting from the parent of the offending commit
git rebase -i ff1679d~1

# In the editor, mark ff1679d as "edit", then:
git rm --cached "docs/client_secret_318032290599-h56kne5fnokgoipf1if13q1okono0hdg.apps.googleusercontent.com.json"
git commit --amend --no-edit
git rebase --continue

# Then push
git push origin main
```

> [!IMPORTANT]
> After rewriting, make sure the credential file is in `.gitignore` and stored securely outside the repo (e.g., environment variables or a secrets manager).

### Option B — Allow the secret on GitHub (quick, less secure)

Visit these URLs to whitelist the secrets:
- [Unblock Client ID](https://github.com/Lemniscate-world/Charmed/security/secret-scanning/unblock-secret/39ylxnbpSPooVpI1HPxL3CjwDu2)
- [Unblock Client Secret](https://github.com/Lemniscate-world/Charmed/security/secret-scanning/unblock-secret/39ylxkSEhi8TJEmhxyAo1vKAWqI)

> [!CAUTION]
> This means the secret remains in your public git history. Anyone can extract it. You should rotate the credentials afterward.
