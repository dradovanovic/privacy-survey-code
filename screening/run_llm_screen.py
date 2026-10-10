#!/usr/bin/env python3
"""LLM title/abstract screening through Claude Code print mode.

Setup: docs/screening_spec.md §2.1 (output schema) and §4.1 (run setup).
One `claude -p` call per record, each a new session in a new empty temporary
folder outside the project, with all tools, MCP servers and user customizations
disabled. Standard library only.

Example (from the project root):
    python code/screening/run_llm_screen.py \
        --sheet code/data/screening/stream-a-v1.csv \
        --ids code/data/screening/stream-a-v1.pilot-selection.csv \
        --prompt code/prompts/screen-A-v1.md \
        --model claude-opus-5-5 --run 1 \
        --out code/data/screening/llm/stream-a-v1.pilot.screen-A-v1.run1.jsonl
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RECORD_COLUMNS = ("record_id", "title", "year", "venue", "content_type", "keywords", "abstract")
VALID_DECISIONS = {"include", "exclude", "maybe"}
VALID_CODES = {f"A-I{i}" for i in range(1, 6)} | {f"A-E{i}" for i in range(1, 7)}
VALID_ROUTES = {"B", "C", "none"}
CODE_LIST_FIELDS = ("criteria_met", "criteria_failed", "criteria_unclear")
ABSTRACT_PLACEHOLDER = '{abstract_or_"(no abstract)"}'
# Environment variables that would make the CLI bill an API key instead of the subscription login.
STRIPPED_ENV = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")
CALL_TIMEOUT_S = 900
# Found in the pre-run checks (2026-10-10): with subscription login, print mode adds these
# around the SYSTEM text, which itself arrives verbatim. No flag removes them without API-key auth.
CONTEXT_ADDITIONS = [
    "identity sentence prepended to the system prompt: \"You are a Claude agent, built on Anthropic's Claude Agent SDK.\"",
    "system reminder with account context (user email)",
    "environment block (temporary working folder, platform, OS, model name, knowledge cutoff, date)",
]


def load_prompt(path: Path) -> tuple[str, str, str]:
    """Return (system_text, user_template, sha256 of the prompt file)."""
    raw = path.read_bytes()
    lines = raw.decode("utf-8").splitlines()
    sys_idx = lines.index("## SYSTEM")
    user_idx = lines.index("## USER (per record)")
    sep_idx = max(i for i in range(sys_idx, user_idx) if lines[i].strip() == "---")
    system = "\n".join(lines[sys_idx + 1 : sep_idx]).strip("\n")
    user = "\n".join(lines[user_idx + 1 :]).strip("\n")
    return system, user, hashlib.sha256(raw).hexdigest()


def load_records(sheet: Path, wanted: set[str]) -> dict[str, dict[str, str]]:
    records = {}
    with sheet.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if row["record_id"] in wanted:
                records[row["record_id"]] = {c: (row.get(c) or "") for c in RECORD_COLUMNS}
    return records


def load_ids(path: Path) -> list[str]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if rows and "n" in rows[0]:
        rows.sort(key=lambda r: int(r["n"]))
    return [r["record_id"] for r in rows]


def fill_user(template: str, rec: dict[str, str]) -> str:
    text = template
    for field in ("title", "year", "venue", "content_type", "keywords"):
        text = text.replace("{" + field + "}", rec[field].strip())
    abstract = rec["abstract"].strip()
    return text.replace(ABSTRACT_PLACEHOLDER, abstract if abstract else "(no abstract)")


def build_args(claude: str, model: str, system_prompt: str) -> list[str]:
    return [
        claude,
        "-p",
        "--model", model,
        "--output-format", "json",
        "--system-prompt", system_prompt,  # replaces the default system prompt
        "--tools", "",  # no built-in tools
        "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',  # no MCP servers
        "--safe-mode",  # no CLAUDE.md, memory, skills, plugins, hooks, custom agents
        "--disable-slash-commands",
        "--no-session-persistence",
    ]


def loggable_args(args: list[str]) -> list[str]:
    out = list(args[1:])
    i = out.index("--system-prompt")
    out[i + 1] = "<SYSTEM section of prompt file>"
    return out


def claude_version(claude: str) -> str:
    return subprocess.run([claude, "--version"], capture_output=True, text=True,
                          encoding="utf-8", check=True).stdout.strip()


def call_claude(args: list[str], message: str) -> tuple[dict | None, str | None]:
    """Run one print-mode call in a fresh empty folder. Return (cli_json, error)."""
    env = {k: v for k, v in os.environ.items() if k not in STRIPPED_ENV}
    workdir = tempfile.mkdtemp(prefix="llm-screen-")
    try:
        proc = subprocess.run(args, input=message, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", cwd=workdir, env=env,
                              timeout=CALL_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return None, f"timeout after {CALL_TIMEOUT_S}s"
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    try:
        out = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None, f"exit {proc.returncode}; CLI output not JSON: {(proc.stdout + proc.stderr)[:500]}"
    if proc.returncode != 0 or out.get("is_error"):
        return out, f"exit {proc.returncode}; CLI error: {str(out.get('result'))[:500]}"
    return out, None


def strip_fence(text: str) -> str:
    m = re.fullmatch(r"\s*```(?:json)?\s*\n(.*?)\n?```\s*", text, flags=re.S)
    return m.group(1) if m else text.strip()


def parse_answer(text: str) -> tuple[dict | None, str | None]:
    try:
        obj = json.loads(strip_fence(text))
    except json.JSONDecodeError as e:
        return None, f"invalid JSON: {e}"
    if not isinstance(obj, dict):
        return None, "answer is not a JSON object"
    problems = []
    if obj.get("decision") not in VALID_DECISIONS:
        problems.append(f"decision {obj.get('decision')!r}")
    pc = obj.get("primary_code")
    if pc is not None and pc not in VALID_CODES:
        problems.append(f"primary_code {pc!r}")
    codes = set()
    for field in CODE_LIST_FIELDS:
        val = obj.get(field)
        if not isinstance(val, list):
            problems.append(f"{field} is not a list")
            continue
        bad = [c for c in val if c not in VALID_CODES]
        if bad:
            problems.append(f"{field} has invalid codes {bad}")
        codes.update(c for c in val if isinstance(c, str))
    route = obj.get("route")
    if route is not None:
        if route not in VALID_ROUTES:
            problems.append(f"route {route!r}")
        elif pc != "A-E1" and "A-E1" not in codes:
            problems.append(f"route {route!r} without A-E1")
    if problems:
        return obj, "schema check failed: " + "; ".join(problems)
    return obj, None


def screen_one(args: list[str], message: str) -> dict:
    """One attempt: call, extract answer text, parse and check."""
    cli, err = call_claude(args, message)
    raw = cli.get("result") if isinstance(cli, dict) else None
    parsed = None
    if err is None:
        parsed, err = parse_answer(raw if isinstance(raw, str) else "")
    usage = {k: v for k, v in cli.items() if k != "result"} if isinstance(cli, dict) else None
    model_reported = sorted((cli or {}).get("modelUsage", {}) or {}) if isinstance(cli, dict) else []
    return {"raw_text": raw, "parsed": parsed if err is None else None, "parse_error": err,
            "usage": usage, "model_reported": model_reported}


def done_ids(out: Path) -> set[str]:
    if not out.exists():
        return set()
    with out.open(encoding="utf-8") as fh:
        return {json.loads(line)["record_id"] for line in fh if line.strip()}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sheet", type=Path, required=True)
    ap.add_argument("--ids", type=Path, required=True, help="CSV with a record_id column (and optional n)")
    ap.add_argument("--prompt", type=Path, required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--run", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--limit", type=int, help="screen only the first N ids (smoke tests)")
    a = ap.parse_args(argv)

    claude = shutil.which("claude")
    if not claude:
        sys.exit("claude executable not found on PATH")
    system, template, prompt_sha = load_prompt(a.prompt)
    prompt_version = a.prompt.stem
    ids = load_ids(a.ids)[: a.limit] if a.limit else load_ids(a.ids)
    records = load_records(a.sheet, set(ids))
    missing = [i for i in ids if i not in records]
    if missing:
        sys.exit(f"record ids not in sheet: {missing}")

    args = build_args(claude, a.model, system)
    version = claude_version(claude)
    skip = done_ids(a.out)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    todo = [i for i in ids if i not in skip]
    print(f"run {a.run}: {len(todo)} to screen, {len(ids) - len(todo)} already in {a.out}", flush=True)

    with a.out.open("a", encoding="utf-8", newline="\n") as fh:
        for k, rid in enumerate(todo, 1):
            message = fill_user(template, records[rid])
            res = screen_one(args, message)
            retried = res["parse_error"] is not None
            first_error = res["parse_error"]
            if retried:
                res = screen_one(args, message)
            line = {
                "record_id": rid,
                "run": a.run,
                "prompt_version": prompt_version,
                "prompt_sha256": prompt_sha,
                "model_requested": a.model,
                "model_reported": res["model_reported"],
                "claude_code_version": version,
                "cli_args": loggable_args(args),
                "context_additions": CONTEXT_ADDITIONS,
                "screened_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                "status": "ok" if res["parse_error"] is None else "error",
                "raw_text": res["raw_text"],
                "parsed": res["parsed"],
                "parse_error": res["parse_error"],
                "retried": retried,
                "first_attempt_error": first_error,
                "usage": res["usage"],
            }
            fh.write(json.dumps(line, ensure_ascii=False) + "\n")
            fh.flush()
            decision = (res["parsed"] or {}).get("decision", "ERROR")
            print(f"[{k}/{len(todo)}] {rid}: {decision}{' (retried)' if retried else ''}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
