# simple_logging_interceptor/parser.py
"""
Parser utility for simple_logging_interceptor logs.

Programmatic usage:

    from pathlib import Path
    from simple_logging_interceptor.parser import parse_and_save

    records = parse_and_save(Path("logs/interceptor_2025-09-07_12-36-26.log"))
    print(records[0])  # structured dict
"""

import ast
import json
import re
from pathlib import Path
from typing import Any, Dict, List

# Timestamp prefix:
RE_PREFIX = (
    r"(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:[.,]\d{3})?)\s*-\s*(?P<level>[A-Z]+)\s*-\s*"
)

RE_CALL = re.compile(
    RE_PREFIX
    + r"Calling:\s*(?P<func>[A-Za-z_]\w*)\s*with args=(?P<args>\(.*?\)),\s*kwargs=(?P<kwargs>\{.*?\})\s*$"
)

RE_RETURN = re.compile(
    RE_PREFIX
    + r"Returned from\s+(?P<func>[A-Za-z_]\w*)\s*->\s*(?P<result>.*?)\s*\(took\s+(?P<elapsed_ms>[\d.]+)\s+ms\)\s*$"
)

RE_EXCEPTION = re.compile(
    RE_PREFIX + r"Exception in\s+(?P<func>[A-Za-z_]\w*):\s*(?P<error>.*)\s*$"
)

# Allow optional leading whitespace before a new record
RE_START_OF_RECORD = re.compile(
    r"^\s*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:[.,]\d{3})?\s*-\s*[A-Z]+\s*-\s*"
)


def _literal_or_text(text: str) -> Any:
    """Try ast.literal_eval; if it fails, return the raw string."""
    try:
        return ast.literal_eval(text)
    except Exception:
        return text


def parse_log(path: Path) -> List[Dict[str, Any]]:
    """Parse the log file into structured records."""
    records: List[Dict[str, Any]] = []
    pending: Dict[str, List[Dict[str, Any]]] = {}

    raw = path.read_text(encoding="utf-8", errors="replace").splitlines()
    i = 0

    while i < len(raw):
        line_stripped = raw[i].lstrip()

        m_call = RE_CALL.match(line_stripped)
        if m_call:
            d = m_call.groupdict()
            func = d["func"]
            rec = {
                "func": func,
                "args": _literal_or_text(d["args"]),
                "kwargs": _literal_or_text(d["kwargs"]),
                "start_ts": d["ts"].replace(",", "."),
                "start_level": d["level"],
                "end_ts": None,
                "end_level": None,
                "result": None,
                "elapsed_ms": None,
                "exception": None,
                "traceback": None,
            }
            pending.setdefault(func, []).append(rec)
            i += 1
            continue

        m_ret = RE_RETURN.match(line_stripped)
        if m_ret:
            d = m_ret.groupdict()
            func = d["func"]
            if func in pending and pending[func]:
                rec = pending[func].pop()
            else:
                rec = {"func": func}
            rec.update(
                {
                    "end_ts": d["ts"].replace(",", "."),
                    "end_level": d["level"],
                    "result": _literal_or_text(d["result"].strip()),
                    "elapsed_ms": float(d["elapsed_ms"]),
                }
            )
            records.append(rec)
            i += 1
            continue

        m_exc = RE_EXCEPTION.match(line_stripped)
        if m_exc:
            d = m_exc.groupdict()
            func = d["func"]
            if func in pending and pending[func]:
                rec = pending[func].pop()
            else:
                rec = {"func": func}
            rec.update(
                {
                    "end_ts": d["ts"].replace(",", "."),
                    "end_level": d["level"],
                    "exception": d["error"],
                }
            )
            # collect traceback lines
            tb_lines: List[str] = []
            j = i + 1
            while j < len(raw) and not RE_START_OF_RECORD.match(raw[j].lstrip()):
                tb_lines.append(raw[j])
                j += 1
            rec["traceback"] = "\n".join(tb_lines).strip() or None
            records.append(rec)
            i = j
            continue

        i += 1

    # add any unfinished calls
    for stack in pending.values():
        for rec in stack:
            records.append(rec)

    return records


def parse_and_save(path: Path) -> List[Dict[str, Any]]:
    """
    Parse the log file and also save results to `.parsed_logs/<filename>.jsonl`.
    Returns the list of structured records.
    """
    records = parse_log(path)

    out_dir = Path(".parsed_logs")
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / (path.stem + ".jsonl")

    with out_file.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")

    print(f"✅ Parsed {len(records)} records, saved to {out_file}")
    return records

def parse_folder(
    folder: Path | str,
    *,
    pattern: str = "*.log",
    recursive: bool = False,
) -> List[Dict[str, Any]]:
    """
    Parse all matching .log files in a folder and save JSONL to .parsed_logs.
    Returns a list of summaries, one per processed file:
        [{"input": "...", "output": "...", "count": N}, ...]

    Args:
        folder: Directory containing .log files.
        pattern: Glob pattern to match log files (default: "*.log").
        recursive: If True, search subfolders (uses rglob).
    """
    base = Path(folder)
    if not base.exists() or not base.is_dir():
        raise ValueError(f"Folder not found or not a directory: {base}")

    # Find files (sorted for stable order)
    files = sorted(
        (base.rglob(pattern) if recursive else base.glob(pattern)),
        key=lambda p: str(p).lower(),
    )

    out_dir = Path(".parsed_logs")
    out_dir.mkdir(exist_ok=True)

    results: List[Dict[str, Any]] = []
    if not files:
        print(f"ℹ️ No files matched {pattern} in {base} (recursive={recursive}).")
        return results

    for f in files:
        try:
            records = parse_log(f)
            out_file = out_dir / (f.stem + ".jsonl")
            with out_file.open("w", encoding="utf-8") as fp:
                for rec in records:
                    fp.write(json.dumps(rec) + "\n")
            results.append({"input": str(f), "output": str(out_file), "count": len(records)})
            print(f"✅ {f.name}: {len(records)} records → {out_file}")
        except Exception as e:
            # Continue on errors; record the failure
            results.append({"input": str(f), "output": None, "count": 0, "error": str(e)})
            print(f"❌ {f.name}: {e}")

    # Summary
    total = sum(r.get("count", 0) for r in results)
    succeeded = sum(1 for r in results if r.get("output"))
    failed = sum(1 for r in results if not r.get("output"))
    print(f"\n📊 Done. Files: {len(results)} | OK: {succeeded} | Failed: {failed} | Records: {total}")
    return results
