# Merge Sort Demo: Build Scaffold

This scaffold sets up a one-pass build of a small full-stack merge sort demo: a Streamlit page that sends an array to a FastAPI backend, which validates it, sorts it with merge sort, and returns the sorted array along with performance metrics. No animation, one page, one endpoint that matters.

## What is in here

- docs/PROJECT_OVERVIEW.md: the full technical overview, architecture, and success criteria.
- docs/PREFLIGHT.md: what you need running before the build starts.
- docs/DELIVERY_PLAN.md: every issue, branch, pull request, merge, and commit, including the timeline.
- ONESHOT_PROMPT.md: the prompt that starts the whole build.
- .claude/skills: three skills carrying the reference code for backend, frontend, and delivery.
- .claude/agents: three specialist subagents plus the orchestrator that runs everything.
- scripts/backdate_commits.sh: the commit date helper.

## How to use it

Read docs/PROJECT_OVERVIEW.md, work through docs/PREFLIGHT.md, then open ONESHOT_PROMPT.md and run it. The orchestrator does the rest, building the app and recording it through a normal issue and pull request process.

The app itself, backend and frontend directories, is created during the build. This scaffold is the plan and the instructions that produce it.
