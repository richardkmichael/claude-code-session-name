#!/usr/bin/env bash

# Hook input on STDIN, and processed with `jq`.

# SessionStart hook input example:
#
# {
#   "session_id": "abc123",
#   "transcript_path": "~/.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
#   "permission_mode": "default",
#   "hook_event_name": "SessionStart",
#   "source": "startup"
# }


# Debugging: inspect relevant env
#
# env | sort > /tmp/session-start-hook-env
#
#   grep CLAUDE:
#
#   CLAUDE_CODE_ENTRYPOINT=cli
#   CLAUDE_ENV_FILE=/Users/rmichael/.claude/session-env/ada7bbf9-eddd-4152-8f89-d387332e2786/hook-0.sh
#   CLAUDE_PROJECT_DIR=/Users/rmichael/Documents/Personal/Source/claude-session-name/development


# The SessionStart hook has access to the `CLAUDE_ENV_FILE` variable.
# https://code.claude.com/docs/en/hooks#persisting-environment-variables
#
# The CLAUDE_ENV_FILE contains environment variables which will be set in the invoked Bash tool
# environment.
#
# Environment variables must be exported to be available to *sub-processes* started by the `Bash`
# tool.  Without export, they will be available to only Bash itself.
#
# e.g.,
#
#   !`echo $CLAUDE_CODE_SESSION_ID`                             -- works without export Bash(echo
#   $CLAUDE_CODE_SESSION_ID)                          -- works without export Bash(python -c
#   'print(os.getenv("CLAUDE_CODE_SESSION_ID"))) -- not set without export, prints `None`
#

if [[ -n "${CLAUDE_ENV_FILE}" ]] ; then
  # The SessionStart hook input has the session ID; make it available to slash commands.
  jq -r '"export CLAUDE_CODE_SESSION_ID=\(.session_id)"' >> "${CLAUDE_ENV_FILE}"

  # The `CLAUDE_PROJECT_DIR` variable is only in hooks; use it for the wrapper path in this repo.
  echo "export CLAUDE_CODE_WRAPPER=${CLAUDE_PROJECT_DIR}/claude" >> "${CLAUDE_ENV_FILE}"
fi
