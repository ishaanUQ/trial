#!/usr/bin/env bash
# Commit date helper for the merge sort demo build.
#
# Source this file, then use dcommit to make commits that carry a chosen
# author and committer date. Git reads GIT_AUTHOR_DATE and GIT_COMMITTER_DATE
# from the environment, so setting both stamps the commit with that time.
#
# Usage:
#   source scripts/backdate_commits.sh
#   git add <files>
#   dcommit "2025-08-13 11:15:00" "feat: add recursive merge sort engine"
#
# Toggle backdating with the BACKDATE variable. When BACKDATE=0 the date
# argument is ignored and the commit lands with the current live timestamp,
# which is the honest mode to use if your course expects real history.
#
#   BACKDATE=1   apply the supplied date  (default)
#   BACKDATE=0   ignore the date, commit live

: "${BACKDATE:=1}"

dcommit() {
  local when="$1"
  local msg="$2"
  if [ -z "$msg" ]; then
    echo "dcommit: need a date and a message" >&2
    return 1
  fi
  if [ "$BACKDATE" = "1" ]; then
    GIT_AUTHOR_DATE="$when" GIT_COMMITTER_DATE="$when" git commit -m "$msg"
  else
    git commit -m "$msg"
  fi
}

# Date a merge commit as well, useful right after merging a feature branch.
#   dmerge "2025-08-13 23:00:00" feature/engine "merge: land merge sort engine"
dmerge() {
  local when="$1"
  local branch="$2"
  local msg="$3"
  if [ "$BACKDATE" = "1" ]; then
    GIT_AUTHOR_DATE="$when" GIT_COMMITTER_DATE="$when" \
      git merge --no-ff "$branch" -m "$msg"
  else
    git merge --no-ff "$branch" -m "$msg"
  fi
}
