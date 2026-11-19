# Git Branch Workflow — Assistant-Service

A practical, safe, step-by-step guide for working with `main` and feature branches.

## 1. Understand the branch story

Think of `main` as the stable road for your project. Whenever you build a new feature, create or use a separate feature branch. You can work there without directly changing `main`.

Current branches:

```text
main
feature/chat-features
feature/web-assistant-reference-capabilities
```

Each local branch tracks its matching GitHub remote branch:

```text
main                                      -> origin/main
feature/chat-features                    -> origin/feature/chat-features
feature/web-assistant-reference-capabilities -> origin/feature/web-assistant-reference-capabilities
```

`origin` is simply the conventional name Git gives to your GitHub remote.

---

## 2. Start from main and update it

When you begin a new work session, first go to `main` and get the latest remote changes.

```bash
git switch main
git status
git pull origin main
```

What each command does:

- `git switch main` — moves you to your local `main` branch.
- `git status` — shows whether you have uncommitted changes.
- `git pull origin main` — downloads and integrates the latest `main` changes.

**Important:** If `git status` shows changes you want to keep, commit or safely stash them before switching branches or pulling. Do not discard work just to make the command succeed.

---

## 3. Move to an existing feature branch

For chat work:

```bash
git switch feature/chat-features
```

For web-assistant reference capability work:

```bash
git switch feature/web-assistant-reference-capabilities
```

These commands switch to branches that already exist locally. They do not create a new branch.

Check where you are:

```bash
git branch --show-current
git status
```

---

## 4. Make changes and save them in Git

After editing or adding files in your feature branch:

```bash
git status
git diff
```

- `git status` — lists changed, new, and untracked files.
- `git diff` — reviews unstaged changes before saving them.

Stage the files you intend to commit:

```bash
git add .
```

Or stage only selected files:

```bash
git add path/to/file.py
```

Review what is staged:

```bash
git diff --cached
git status
```

Commit your work:

```bash
git commit -m "Add chat feature functionality"
```

A commit is a saved checkpoint in your branch's history.

---

## 5. Push your feature branch to GitHub

For the chat branch:

```bash
git push
```

For the web-assistant branch:

```bash
git push
```

Because the branches were created with upstream tracking (`git push -u origin ...`), plain `git push` normally knows which remote branch to update.

If upstream tracking has not been configured yet, use the first-push form:

```bash
git push -u origin feature/chat-features
```

or:

```bash
git push -u origin feature/web-assistant-reference-capabilities
```

After that, plain `git push` and `git pull` work for that branch.

---

## 6. Bring the latest main changes into your feature branch

If other work has updated `main` while you were developing, you may want to bring those changes into your feature branch.

First, make sure your feature work is committed or safely stashed. Then:

```bash
git switch main
git pull origin main
git switch feature/chat-features
git merge main
```

For the other feature branch, use:

```bash
git switch main
git pull origin main
git switch feature/web-assistant-reference-capabilities
git merge main
```

If Git reports merge conflicts:

1. Run `git status` to see the conflicted files.
2. Open each conflicted file and resolve the conflict markers.
3. Stage the resolved files with `git add <file>`.
4. Complete the merge with `git commit` if Git asks you to create a merge commit.
5. Push the updated feature branch with `git push`.

Do not blindly choose one side of a conflict; inspect the code and preserve the intended changes.

---

## 7. Merge completed feature work into main

**Recommended team workflow: use a GitHub Pull Request (PR).**

1. Push your feature branch:

   ```bash
   git switch feature/chat-features
   git push
   ```

2. Open GitHub and create a Pull Request:
   - Base: `main`
   - Compare: `feature/chat-features`

3. Review the changed files and run tests.
4. Merge the PR after approval and successful checks.
5. Repeat with the other feature branch when its work is ready.

After the PR is merged, update your local `main`:

```bash
git switch main
git pull origin main
```

A PR is generally safer than directly merging unfinished feature work into `main`, especially when CI/CD checks are configured.

---

## 8. Verify local and remote branches

List local and remote branches:

```bash
git branch -a
```

See the current branch:

```bash
git branch --show-current
```

See upstream tracking and working-tree status:

```bash
git status -sb
```

See recent commits:

```bash
git log --oneline --graph --decorate -10
```

Fetch remote branch updates without merging them:

```bash
git fetch origin
```

Prune remote-tracking references for branches deleted from GitHub:

```bash
git fetch origin --prune
```

---

## 9. Create a brand-new feature branch (when needed)

Start from an updated `main`:

```bash
git switch main
git pull origin main
git switch -c feature/new-feature-name
```

The `-c` option creates the branch and switches to it.

Publish it to GitHub and set upstream tracking:

```bash
git push -u origin feature/new-feature-name
```

After this first push, use `git push` for later pushes.

---

## 10. Quick command sequence for your existing chat branch

Use this when you are ready to continue chat-feature development:

```bash
git switch main
git status
git pull origin main

git switch feature/chat-features
git status

# Make your code changes, then:
git add .
git diff --cached
git commit -m "Update chat features"
git push
```

When you want to return to `main`:

```bash
git switch main
git status
git pull origin main
```

The same workflow applies to `feature/web-assistant-reference-capabilities`; replace the branch name.

---

## 11. Important safety rules

- Always check your current branch with `git branch --show-current`.
- Run `git status` before switching branches, merging, or pulling.
- Commit or stash work you want to keep before changing branches.
- Do not use `git reset --hard` or `git clean -fd` unless you fully understand that they can permanently discard local work.
- Do not delete an old remote branch until the replacement is pushed and verified on GitHub.
- A local branch and a remote-tracking branch are different things. `origin/feature/chat-features` is your local reference to the branch on GitHub.
- Prefer Pull Requests for merging feature branches into `main`.

## The simple story to remember

```text
MAIN
  |
  | switch to feature branch
  v
FEATURE BRANCH
  |
  | edit files
  | git add
  | git commit
  | git push
  v
GITHUB FEATURE BRANCH
  |
  | create and review Pull Request
  v
MAIN (after PR merge)
  |
  | git switch main
  | git pull origin main
  v
LOCAL MAIN UPDATED
```

**Golden rule:** `git switch` changes your working branch; `git add` stages changes; `git commit` saves a local checkpoint; `git push` sends commits to GitHub; `git pull` brings remote changes into your current branch; and a Pull Request is the review-and-merge process on GitHub.
