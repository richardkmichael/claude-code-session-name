## TL;DR

- `claude --session-name [name]`
- `claude --resume [name]`
- `claude`, then anytime: `/session-name [name]`

A Python wrapper named `claude` provides new and modified command line options.

A session may only have one name, otherwise error.  There is no delete or cleanup.

But,

- Slash-commands must call the LLM, so `/session-name` will always consume tokens.
- The built-in `--resume` menu has `/` search, which is adequate for me.

## Try it

```bash
$ git clone https://github.com/richardkmichael/claude-code-session-name.git
$ export PATH=.:${PATH}
$ claude --session-name 'some name'

# Or,

$ claude
# /session-name 'some name'

# Then,

$ claude --resume 'some name'
```

## Overview

Claude Code has enough flexibility to build a session naming capability.

This provides:

1. A `claude` command line wrapper to add/alter arguments:
    - `--session-name [name]` to name a session at startup
    - `--resume [name]` to resume by session name

2. A `/session-name [name]` custom slash-command, to set a name if not done at startup.

All arguments to the wrapper are passed along to `claude` unmodified.

Named sessions are stored in a trivial SQLite database, default at `~/.claude/session-names.sqlite`.

## Implementation

The `--session-name [name]` argument generates a UUID and uses it with the built-in `--session-id
[uuid]` argument.


The `--session-name [name]` and `--session-id [uuid]` arguments can be combined, in which case the
provided UUID is used instead of generating one.

The `--resume [name]` argument finds the UUID for `name` and uses it with the built-in `--resume
[uuid]` option.  (i.e., just `--resume [uuid]` and if the argument is *not* a UUID, use it as a
name.)

The `/session-name [name]` slash-command relies on the `SessionStart` hook and `startup` matcher to
extract the session ID created by Claude at startup.  The session ID is added to the
`CLAUDE_ENV_FILE` (as `CLAUDE_CODE_SESSION_ID`) so it is available in the `Bash` tool environment.
The slash-command definition uses the `Bash` tool to run the wrapper, with an extra argument
`--no-exec-claude`, to save the name and captured UUID.

  - [.claude/settings.json](.claude/settings.json)
  - [.claude/hooks/session-start-startup.sh](.claude/hooks/session-start-startup.sh)
  - [.claude/commands/session-name.md](.claude/commands/session-name.md)


## Shortcomings

1. `/session-name [name]` for convenience, but..

Unfortunately, slash-commands always use the model.  Silly in this case, because it is plain code,
no LLM action or output is actually needed.  Alternatively, bash-mode: `!  ...`, but this
"integration" is crufty.

Maybe a `session-name` script (possibly a shell function), to permit: `!session-name [name]` ?

2. `--resume` would benefit from a menu to choose from named sessions.

Unfortunately, that would shadow the built-in `--resume`, and need a lot for parity (read: forget
it).  The built-in `--resume`, with `/` search is good.

Maybe `--session-name-list` ?

## Notes

### Wrapper

The wrapper must be on `PATH`.

To easily test this setup, set `PATH` in one shell: `export PATH=.:${PATH}` and run `claude`.

### Slash-command `/session-name`

```
---
description: Name the current session
argument-hint: [session-name]
disable-model-invocation: true
allowed-tools: Bash(claude)
model: claude-3-5-haiku-latest
---

!`claude --session-name '$ARGUMENTS' --session-id $CLAUDE_CODE_SESSION_ID --no-exec-claude`
```

- `disable-model-invocation` [prevents Claude's own `SlashCommand` tool from using this
  slash-command](https://code.claude.com/docs/en/slash-commands#disable-specific-commands-only)
- `allowed-tools: Bash(claude)`:
  - Required because the `!\`...\`` [executes with the `Bash`
    tool](https://code.claude.com/docs/en/slash-commands#bash-command-execution)
- Use the cheapest model that works. Although the model isn't technically needed, slash-commands
  *always* make a Claude/LLM call.  Sometimes too many tokens are returned for the oldest, cheapest
  `claude-3-haiku-20240307`

21K token output?

```
> /session-name is running… test-my-session-name
  ⎿  Model: claude-3-haiku-20240307
  ⎿  Allowed 1 tools for this command
  ⎿ API Error: 400 {"type":"error","error":{"type":"invalid_request_error","message":"max_tokens: 21333 > 4096, which is the
    maximum allowed number of output tokens for claude-3-haiku-20240307"},"request_id":"req_XXXXXXXXXXXX"}
```
