# One-Shot Run

Once the preflight checklist passes, open this repo in Claude Code and paste the prompt below. It hands control to the orchestrator, which drives the entire build.

## Before pasting

Fill in the two blanks: your empty remote repo URL, and your backdating choice. Backdating on means the commit history is stamped across 12 to 19 August. Backdating off means live timestamps. Read the note at the top of docs/DELIVERY_PLAN.md before you decide.

## The prompt

```
Use the orchestrator subagent to build this project end to end.

Repository remote: <PASTE YOUR EMPTY REPO URL>
Backdating: <on or off>

Follow docs/DELIVERY_PLAN.md exactly. Before doing anything, run the quick
confirm block from docs/PREFLIGHT.md and stop if any prerequisite is missing.

Then, for each issue in the plan in order: create the GitHub issue, cut its
feature branch from main, delegate the implementation to the matching
specialist subagent, commit the work with the messages and timestamps from
the plan, open a pull request that closes the issue, merge it into main, and
move the issue to Done.

The specialists must read their matching skill before writing code:
backend-engineer uses mergesort-backend, frontend-engineer uses
streamlit-static-ui, devops-engineer uses docker-ci-quality.

When everything is merged, run the full test suite, bring the app up with
docker compose, confirm the frontend reaches the backend, and give me a
completion report with the issue and pull request numbers and the final
commit count.
```

## What you should see when it finishes

A working repo on your GitHub account with twelve closed issues, twelve merged pull requests, a populated project board, and a commit history that matches the timeline in the delivery plan. Locally, docker compose up brings the app to life at the Streamlit URL, where you can paste an array and see it sorted with its metrics.

If the run stops early, it will name the prerequisite or step that failed. Fix that one thing and resume by pointing the orchestrator at the next unmerged issue in the plan.
