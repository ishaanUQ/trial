# Preflight Checklist

Do all of this before you start the one-shot run. If any item is missing, the pass will stall partway through and you will have to fix it by hand, which defeats the point. Work top to bottom. Each item says what to set up and how to confirm it is actually working.

## 1. Local tooling

Python 3.11 or newer.
Confirm: `python3 --version` prints 3.11 or higher.

Git, configured with your name and email.
Confirm: `git config user.name` and `git config user.email` both return values. If not, set them with `git config --global user.name "Your Name"` and the same for user.email. These are what the commit history will be attributed to.

Docker Desktop or Docker Engine, running.
Confirm: `docker ps` returns without error. If it errors, Docker is not running. Start Docker Desktop and wait for it to finish booting.

Docker Compose v2.
Confirm: `docker compose version` prints a version. Note it is `docker compose` with a space, not the old `docker-compose`.

## 2. GitHub access

A GitHub account and an empty remote repository created for this project. Do not initialise it with a README or licence, because the one-shot pass creates the initial history itself and an existing commit will get in the way. Copy the empty repo URL somewhere handy.

If you already have a non-empty remote (for example GitHub auto-created a README commit), see the second note at the top of DELIVERY_PLAN.md for how that was handled here rather than starting over.

The GitHub CLI, authenticated. This is the simplest path for creating issues and pull requests from the command line during the run.
Confirm: `gh auth status` shows you are logged in. If not, run `gh auth login` and follow the prompts. Give it repo scope.

## 3. GitHub MCP server (optional but recommended)

If you want the orchestrator to manage issues, pull requests, and the project board directly rather than shelling out to gh, connect the GitHub MCP server in your Claude client.

Confirm it is connected by asking Claude to list your repositories before you start. If it can, the connection is live. If you would rather keep things simple, skip the MCP and let the run use the gh CLI instead. The delivery plan works either way. Pick one and be consistent.

## 4. Claude Code project setup

Clone your empty repo locally and drop the contents of this scaffold into it, so the .claude directory, the docs, and the scripts all sit at the repo root.
Confirm: from the repo root, `ls .claude/agents` lists the four agent files and `ls .claude/skills` lists the three skill folders.

Open the repo in Claude Code from that root, so the skills and subagents are discovered.

## 5. Decisions to make before you start

Repository name and the remote URL, ready to paste.

Author identity for the commit history. The commits will use your configured git identity. Confirm it is the one you want to appear in the log.

Whether you are backdating the commit timeline. The delivery plan includes a script that stamps commits across 12 to 19 August. Before you run that, confirm your course permits AI assistance and does not require the commit history to reflect the real authoring time. If you are unsure, run the build with normal live timestamps instead, which the script also supports.

## Quick confirm block

Run these six commands. If all six succeed, you are ready.

```bash
python3 --version
git config user.name && git config user.email
docker ps >/dev/null && echo "docker ok"
docker compose version
gh auth status
ls .claude/agents && ls .claude/skills
```

Once every line comes back clean, open ONESHOT_PROMPT.md and start the run.
