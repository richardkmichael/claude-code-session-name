---
description: Name the current session
argument-hint: [session-name]
disable-model-invocation: true
allowed-tools: Bash
---

!`"${CLAUDE_CODE_WRAPPER}" --session-name '$ARGUMENTS' --session-id $CLAUDE_CODE_SESSION_ID --no-exec-claude`
