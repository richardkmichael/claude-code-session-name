---
description: Name the current session
argument-hint: [session-name]
disable-model-invocation: true
allowed-tools: Bash(claude:*)
model: claude-3-5-haiku-latest
---

!`claude --session-name '$ARGUMENTS' --session-id $CLAUDE_CODE_SESSION_ID --no-exec-claude`
