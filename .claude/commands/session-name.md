---
description: Name the current session
argument-hint: [session-name]
disable-model-invocation: true
allowed-tools: Bash(claude:*)
---

!`claude --session-name '$ARGUMENTS' --session-id $CLAUDE_CODE_SESSION_ID --no-exec-claude`
