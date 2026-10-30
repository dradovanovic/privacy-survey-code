#!/usr/bin/env python3
"""LLM full-text eligibility check through Claude Code print mode.

Same call setup as run_llm_screen.py (imported from it unchanged): one `claude -p`
call per paper, each a new session in a new empty temporary folder, no tools, no
MCP servers, safe mode. The user message is the prompt's USER template with the
title, year and the per-page text from ft_extract_text.py. Quotes are checked
against the page they cite; the check is recorded only. Standard library only.

Example (from the project root):
    python code/screening/run_llm_fulltext.py \
        --input code/data/screening/stream-a-v1.ft-pilot.input.csv \
        --text-dir code/data/fulltext/text \
        --prompt code/prompts/screen-A-ft-v1.md \
        --model claude-opus-5-5 --run 1 \
        --out code/data/screening/llm/stream-a-v1.ft-pilot.screen-A-ft-v1.run1.jsonl
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path

from run_llm_screen import (CONTEXT_ADDITIONS, build_args, call_claude, claude_version, done_ids,
                            loggable_args, strip_fence)

CRITERIA = tuple(f"A-I{i}" for i in range(1, 6))
VALID_DECISIONS = {"include", "exclude", "unclear"}
VALID_CODES = {f"A-E{i}" for i in range(1, 7)} | {"A-I5"}
VALID_JUDGMENTS = {"met", "not_met", "unclear"}
VALID_ROUTES = {"B", "C", "none"}
VALID_FLAGS = {"nilm_only", "mechanism_only", "ambiguous_ami", "text_incomplete"}
PAGE_MARKER = re.compile(r"^\[\[page (\d+)\]\]$", flags=re.M)


def load_prompt(path: Path) -> tuple[str, str, str]:
    """Return (system_text, user_template, sha256 of the prompt file)."""
    raw = path.read_bytes()
    lines = raw.decode("utf-8").splitlines()
    sys_idx = lines.index("## SYSTEM")
    user_idx = lines.index("## USER (per paper)")
    sep_idx = max(i for i in range(sys_idx, user_idx) if lines[i].strip() == "---")
    system = "\n".join(lines[sys_idx + 1 : sep_idx]).strip("\n")
    user = "\n".join(lines[user_idx + 1 :]).strip("\n")
    return system, user, hashlib.sha256(raw).hexdigest()


def load_input(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    rows.sort(key=lambda r: int(r["n"]))
    return rows


def split_pages(text: str) -> dict[int, str]:
    marks = list(PAGE_MARKER.finditer(text))
    return {int(m.group(1)): text[m.end() : marks[k + 1].start() if k + 1 < len(marks) else len(text)]
            for k, m in enumerate(marks)}


def normalize(text: str) -> str:
    """Apply NFKC (so ligatures such as "ﬁ" match a plain "fi"), join words hyphenated
    across a line break, then collapse all whitespace."""
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"-[ \t]*\r?\n\s*", "", text)
    return re.sub(r"\s+", " ", text).strip()


def check_quotes(parsed: dict, pages: dict[int, str]) -> dict[str, dict]:
    norm_pages = {n: normalize(t) for n, t in pages.items()}
    checks = {}
    for code in CRITERIA:
        c = parsed["criteria"][code]
        quote = normalize(c["quote"])
        if not quote:
            result = "empty"
        elif c["page"] in norm_pages and quote in norm_pages[c["page"]]:
            result = "on_page"
        else:
            other = next((n for n, t in sorted(norm_pages.items()) if quote in t), None)
            result = f"other_page:{other}" if other is not None else "not_found"
        checks[code] = {"quote_check": result, "quote_words": len(c["quote"].split())}
    return checks


def parse_answer(text: str) -> tuple[dict | None, str | None]:
    try:
        obj = json.loads(strip_fence(text))
    except json.JSONDecodeError as e:
        return None, f"invalid JSON: {e}"
    if not isinstance(obj, dict):
        return None, "answer is not a JSON object"
    problems = []
    decision = obj.get("decision")
    if decision not in VALID_DECISIONS:
        problems.append(f"decision {decision!r}")
    pc = obj.get("primary_code")
    if pc is not None and pc not in VALID_CODES:
        problems.append(f"primary_code {pc!r}")
    if decision == "exclude" and pc is None:
        problems.append("exclude without primary_code")
    if decision in ("include", "unclear") and pc is not None:
        problems.append(f"{decision} with primary_code {pc!r}")

    judgments = []
    crit = obj.get("criteria")
    if not isinstance(crit, dict) or set(crit) != set(CRITERIA):
        problems.append(f"criteria keys {sorted(crit) if isinstance(crit, dict) else crit!r}")
    else:
        for code in CRITERIA:
            c = crit[code]
            if not isinstance(c, dict):
                problems.append(f"{code} is not an object")
                continue
            if c.get("judgment") not in VALID_JUDGMENTS:
                problems.append(f"{code} judgment {c.get('judgment')!r}")
            else:
                judgments.append(c["judgment"])
            if not isinstance(c.get("quote"), str):
                problems.append(f"{code} quote is not a string")
            page = c.get("page")
            if page is not None and (not isinstance(page, int) or isinstance(page, bool)):
                problems.append(f"{code} page {page!r}")
        if len(judgments) == len(CRITERIA):
            if decision == "include" and any(j != "met" for j in judgments):
                problems.append("include while a judgment is not met")
            if decision == "exclude" and "not_met" not in judgments:
                problems.append("exclude while no judgment is not_met")
            if decision == "unclear" and ("not_met" in judgments or "unclear" not in judgments):
                problems.append("unclear inconsistent with judgments")

    route = obj.get("route")
    if route is not None and route not in VALID_ROUTES:
        problems.append(f"route {route!r}")
    elif route is not None and pc != "A-E1":
        problems.append(f"route {route!r} without A-E1")
    if pc == "A-E1" and route is None:
        problems.append("A-E1 without route")

    flags = obj.get("flags")
    if not isinstance(flags, list):
        problems.append("flags is not a list")
    elif any(f not in VALID_FLAGS for f in flags):
        problems.append(f"flags has invalid values {[f for f in flags if f not in VALID_FLAGS]}")
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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--text-dir", type=Path, required=True)
    ap.add_argument("--prompt", type=Path, required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--run", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--limit", type=int, help="check only the first N papers (smoke tests)")
    a = ap.parse_args(argv)

    claude = shutil.which("claude")
    if not claude:
        sys.exit("claude executable not found on PATH")
    system, template, prompt_sha = load_prompt(a.prompt)
    prompt_version = a.prompt.stem
    rows = load_input(a.input)[: a.limit] if a.limit else load_input(a.input)
    missing = [r["pdf_file"] for r in rows if not (a.text_dir / f"{Path(r['pdf_file']).stem}.txt").exists()]
    if missing:
        sys.exit(f"text files missing for: {missing}")

    args = build_args(claude, a.model, system)
    version = claude_version(claude)
    skip = done_ids(a.out)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    todo = [r for r in rows if r["record_id"] not in skip]
    print(f"run {a.run}: {len(todo)} to check, {len(rows) - len(todo)} already in {a.out}", flush=True)

    with a.out.open("a", encoding="utf-8", newline="\n") as fh:
        for k, row in enumerate(todo, 1):
            text_file = a.text_dir / f"{Path(row['pdf_file']).stem}.txt"
            data = text_file.read_bytes()
            fulltext = data.decode("utf-8")
            pages = split_pages(fulltext)
            message = (template.replace("{title}", row["title"].strip())
                       .replace("{year}", row["year"].strip())
                       .replace("{fulltext}", fulltext))
            res = screen_one(args, message)
            retried = res["parse_error"] is not None
            first_error = res["parse_error"]
            if retried:
                res = screen_one(args, message)
            line = {
                "record_id": row["record_id"],
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
                "text_file": text_file.as_posix(),
                "text_sha256": hashlib.sha256(data).hexdigest(),
                "pages_used": f"{min(pages)}-{max(pages)}" if pages else "",
                "quote_checks": check_quotes(res["parsed"], pages) if res["parsed"] else None,
            }
            fh.write(json.dumps(line, ensure_ascii=False) + "\n")
            fh.flush()
            decision = (res["parsed"] or {}).get("decision", "ERROR")
            print(f"[{k}/{len(todo)}] {row['record_id']}: {decision}{' (retried)' if retried else ''}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
