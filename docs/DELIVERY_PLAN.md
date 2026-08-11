# Delivery Plan

This is the authoritative plan for how the project is built and recorded in version control. The orchestrator follows it in order. It defines the milestones, the issues, the branches, the pull requests, the merge order, and the commit timeline.

A note before the timeline section: the commit dates below span 12 to 19 August. If this repo is assessed, confirm your course allows AI assistance and does not expect the commit history to reflect the real authoring time. If either is a concern, run in live-timestamp mode, which the script supports, and keep everything else the same.

A second note: contrary to docs/PREFLIGHT.md's instruction to start from an empty remote, this repo's remote already had a GitHub-generated "Initial commit" (a bare README) before the build started. Rather than deleting it, that commit was amended locally to carry the scaffold and build tooling (docs/, .claude/, scripts/, ONESHOT_PROMPT.md, README.md) and backdated to 2026-08-12 08:30:00 +1000, ahead of the timeline's first entry at 10:47 the same day. Because this rewrites a commit the remote already has, landing it requires one force push of main, done once, by hand: `git push --force-with-lease origin main`. It is safe here only because this was the sole commit on the branch with no other history or collaborators depending on it. Once pushed, do not amend or force-push this commit again; treat it as fixed history from that point on. If you are re-running this process on a fresh repo, skip this step entirely and follow PREFLIGHT.md as written: start empty, and let the orchestrator's first commit (10:47, "initialise repository structure") be the true first commit.

## Branching model

Simple GitHub flow. One long-lived branch, main. Every issue is built on its own short-lived feature branch cut from main, then merged back through a pull request that closes the issue. Feature branches are deleted after merge. No direct commits to main after the initial repository creation.

## Milestones

- M1 Foundation: repository scaffolding and tooling.
- M2 Backend: engine, validation, metrics, API, and backend tests.
- M3 Frontend: the Streamlit page and its integration with the backend.
- M4 Delivery: containers, CI, image build, and documentation.

## Issues

Each issue lists its milestone, the branch it is built on, the pull request that lands it, the specialist that implements it, and its labels.

Issue 1. Repository scaffolding and tooling
Milestone M1. Branch feature/scaffolding. PR #1. devops-engineer. Labels: chore, setup.
Create the directory layout, pyproject with ruff and mypy config, gitignore, requirements stubs, and a readme skeleton.

Issue 2. Merge sort engine with operation counting
Milestone M2. Branch feature/engine. PR #2. backend-engineer. Labels: feature, backend.
Implement the recursive merge sort with comparison and write counters. No framework imports.

Issue 3. Input validation schemas
Milestone M2. Branch feature/validation. PR #3. backend-engineer. Labels: feature, backend.
Pydantic request model rejecting non-numeric, non-finite, boolean, and over-length arrays, allowing empty.

Issue 4. Metrics assembly
Milestone M2. Branch feature/metrics. PR #4. backend-engineer. Labels: feature, backend.
Build the metrics block, including is_sorted verification and the n log n reference figure.

Issue 5. FastAPI endpoints
Milestone M2. Branch feature/api. PR #5. backend-engineer. Labels: feature, backend.
Add /health and /sort, timing only the sort call.

Issue 6. Backend tests
Milestone M2. Branch feature/backend-tests. PR #6. devops-engineer. Labels: test, backend.
Fixed engine cases, hypothesis property tests, metrics tests, and API tests via the test client.

Issue 7. Streamlit static UI page
Milestone M3. Branch feature/frontend-page. PR #7. frontend-engineer. Labels: feature, frontend.
One page with array input, sort button, sorted output, and metrics table.

Issue 8. Frontend backend integration and error handling
Milestone M3. Branch feature/frontend-integration. PR #8. frontend-engineer. Labels: feature, frontend.
Backend URL from environment, and explicit handling of parse, unreachable, and validation failures.

Issue 9. Dockerfiles and compose
Milestone M4. Branch feature/docker. PR #9. devops-engineer. Labels: build, infra.
Both Dockerfiles and a compose file with the frontend reaching the backend by service name.

Issue 10. CI workflow
Milestone M4. Branch feature/ci. PR #10. devops-engineer. Labels: ci, infra.
GitHub Actions running lint, type check, and tests with coverage, failing on any error.

Issue 11. Image build workflow
Milestone M4. Branch feature/docker-ci. PR #11. devops-engineer. Labels: ci, infra.
GitHub Actions building both images on pushes to main.

Issue 12. Documentation
Milestone M4. Branch feature/docs. PR #12. devops-engineer. Labels: docs.
Architecture, setup, and run instructions in the readme.

## Merge order

Merge in dependency order so main is always coherent: PR #1, then #2, #3, #4, #5, #6, #7, #8, #9, #10, #11, #12. Each is cut from main after the previous one merges.

## Commit timeline

Every commit below has a date and a time between 10:00 and 23:59. Times are chosen to look like real working sessions that run from mid-morning into the night. Apply them with scripts/backdate_commits.sh when backdating is enabled, otherwise commit live in the same order with the same messages.

Aug 12, feature/scaffolding, merged as PR #1
- 10:47 chore: initialise repository structure
- 13:22 chore: add pyproject with ruff and mypy config
- 16:05 chore: add gitignore and requirements stubs
- 21:38 docs: add readme skeleton

Aug 13, feature/engine, merged as PR #2
- 11:15 feat: add recursive merge sort engine
- 14:48 feat: count comparisons and writes in the merge step
- 19:30 test: add fixed-case engine tests
- 22:53 test: add hypothesis property test against builtin sorted

Aug 14, feature/validation then feature/metrics, merged as PR #3 and #4
- 10:33 feat: add pydantic sort request schema
- 12:19 feat: reject non-finite, boolean, and over-length arrays
- 15:41 test: cover validation edge cases
- 18:27 feat: add metrics assembly with is_sorted verification
- 20:59 feat: add n log n reference figure to metrics

Aug 15, feature/api then feature/backend-tests, merged as PR #5 and #6
- 10:12 feat: add health and sort endpoints
- 13:50 refactor: time only the sort call in the endpoint
- 17:04 test: add fastapi test client coverage for sort and health
- 23:11 test: add rejection tests for malformed payloads

Aug 16, feature/frontend-page, merged as PR #7
- 11:44 feat: add streamlit page with array input and sort button
- 15:28 feat: render sorted array and metrics table
- 22:16 style: tidy page copy and layout

Aug 17, feature/frontend-integration, merged as PR #8
- 10:55 feat: read backend url from environment
- 14:37 feat: handle parse, unreachable, and validation failures
- 20:08 fix: show backend detail message on rejection

Aug 18, feature/docker then feature/ci, merged as PR #9 and #10
- 10:26 build: add backend and frontend dockerfiles
- 13:09 build: add docker compose with shared network
- 16:52 ci: add workflow for lint, type check, and tests
- 21:45 ci: fix working directory for pytest in ci

Aug 19, feature/docker-ci then feature/docs, merged as PR #11 and #12
- 11:03 ci: add image build workflow on main
- 14:22 docs: write architecture and setup guide
- 18:39 docs: document how to run with docker compose
- 23:47 chore: final cleanup and version pin

That is 30 commits across 8 days. The orchestrator commits each on its feature branch at the listed time, then dates the merge commit a few minutes after the last commit on that branch.

## Pull request bodies

Each pull request body follows the same shape: a one-line summary, a short list of what changed, and a closing line that links the issue, for example "Closes #2". This makes the board automation move the issue to Done on merge.
