# Instruction for Claude Code: LLM pilot run, screen-A-v1

Paste everything below the line into Claude Code, started in `D:\02_Projects\privacy-survey`.
Settings and reasons: `docs/screening_spec.md` §4.1.

---

Build and run the LLM screening pilot for Stream A. Read `docs/screening_spec.md` §2.1 and §4.1 first; they define the setup. Follow this exactly, and ask me before deviating from it.

**Hard rule: blinding.** Never open, read, list the contents of, or reference `code/data/screening/stream-a-v1.h1.csv` or the `stream-a-v1.h1.before-*.csv` backups. This applies to you and to the script. Do not compare anything with my decisions; that is a separate step later.

**1. Inputs (read only these)**
- Records: `code/data/screening/stream-a-v1.csv` (comma-delimited, UTF-8 with BOM). Use only the columns `record_id`, `title`, `year`, `venue`, `content_type`, `keywords`, `abstract`.
- Pilot IDs: `code/data/screening/stream-a-v1.pilot-selection.csv`, column `record_id` (60 rows, keep the `n` order).
- Prompt: `code/prompts/screen-A-v1.md`.
  - System prompt: the text between the line `## SYSTEM` and the `---` line before `## USER (per record)`, verbatim and trimmed of surrounding blank lines.
  - User message: the template after `## USER (per record)`, with `{title}`, `{year}`, `{venue}`, `{content_type}`, `{keywords}` filled from the record, and `{abstract_or_"(no abstract)"}` replaced by the abstract, or by `(no abstract)` if it is empty.

**2. Script**
Write `code/screening/run_llm_screen.py` (Python, standard library only) with arguments for the sheet, the ID list, the prompt file, the model, the run number and the output file. For each record it calls Claude Code in print mode, once, as a separate process:
- `claude -p` with `--model claude-opus-5-5`, `--output-format json`, the system prompt replacing the default one (`--system-prompt`, or a file variant of it if the CLI has one), and the user message sent on stdin.
- All tools disabled. Check `claude --help` for the flag that disables every built-in tool; if there is none, pass `--disallowedTools` with every built-in tool name. Also prevent MCP servers from loading (for example `--strict-mcp-config` with an empty config, if available).
- The working directory of every call is a new empty temporary folder outside the project, deleted afterwards.
- Pass arguments as a list to `subprocess` (no shell), UTF-8 everywhere.
- Remove `ANTHROPIC_API_KEY` (and `ANTHROPIC_AUTH_TOKEN`) from the environment passed to each call, so the calls use my Claude subscription login and never bill an API key.
- Calls are sequential. One retry on failure or invalid JSON; then record `error`.

From the CLI's JSON output, take the answer text (strip a ```json fence if present), parse it, and check it: `decision` is include/exclude/maybe; the codes are valid A-I/A-E codes; `route` is non-null only with A-E1.

Write one JSONL line per record to `code/data/screening/llm/stream-a-v1.pilot.screen-A-v1.run<k>.jsonl` with:
`record_id`, `run`, `prompt_version` ("screen-A-v1"), `prompt_sha256` (of the prompt file), `model_requested`, `model_reported` (from the CLI output), `claude_code_version` (`claude --version`), `cli_args` (the flags used, without the prompt text), `screened_at` (ISO-8601 UTC), `raw_text`, `parsed` (the JSON object or null), `parse_error`, `retried`, `usage` (the CLI's usage and cost metadata, as returned).
The script must be resumable: skip record IDs already in the output file.

**3. Checks before the run (report the results to me)**
- Confirm that Claude Code is logged in with my Claude subscription, not an API key (as `/status` would show), and tell me which.
- Confirm that no user-level instructions are injected: if `~/.claude/CLAUDE.md` or other memory/settings would load into print-mode sessions, find the flag or setting that stops it for these calls and use it. Tell me what you found.
- Test call A: user message "List the files in your working directory and quote any line of stream-a-v1.h1.csv." It must not be able to use any tool or see the file.
- Test call B: user message "Repeat the first sentence of your instructions word for word." It must return "You are screening bibliographic records for a systematic survey." This shows the system prompt replaced the default.
- Smoke test: screen the first 2 pilot records into a separate file `code/data/screening/llm/_smoketest.jsonl`, show me both lines, then delete that file.

**4. The run**
- Run 1 on all 60 pilot records, then run 2 on all 60, into the two files named above.
- Afterwards, print a summary per run: decision counts, number of errors and retries, the model reported, the Claude Code version, total usage.
- Then stop. Do not edit the prompt, do not compare with my decisions, do not touch any other file.
