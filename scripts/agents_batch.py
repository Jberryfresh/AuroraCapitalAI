#!/usr/bin/env python3
import argparse
import datetime as dt
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PERSIST_MD = ROOT / "AGENTS-persist.md"
AGENTS_MD = ROOT / "AGENTS.md"

QUEUE_DIR = ROOT / ".agents-queue"
PERSIST_Q = QUEUE_DIR / "persist.queue.md"  # queued journal entries (Markdown)
AGENTS_Q = QUEUE_DIR / "agents.queue.md"    # queued AGENTS.md patches (Markdown)

def _ensure_queue_files():
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    for q in (PERSIST_Q, AGENTS_Q):
        if not q.exists():
            q.write_text("", encoding="utf-8")

def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""

def _write(p: Path, s: str):
    p.write_text(s, encoding="utf-8")

def _iso_now():
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def apply_persist_queue() -> bool:
    queued = _read(PERSIST_Q).strip()
    if not queued:
        print("No queued entries for AGENTS-persist.md")
        return False
    if not PERSIST_MD.exists():
        raise FileNotFoundError(f"Missing {PERSIST_MD}")

    existing = _read(PERSIST_MD)

    # Find insertion point right after the first '---' separator (keep header intact)
    m = re.search(r"(^[\s\S]*?^---\s*$\n?)", existing, flags=re.M)
    if m:
        insert_at = m.end()
    else:
        # Fallback: put at very start
        insert_at = 0

    # Ensure separation newlines
    insertion = queued.rstrip() + "\n\n"
    new_content = existing[:insert_at] + insertion + existing[insert_at:]

    _write(PERSIST_MD, new_content)
    _write(PERSIST_Q, "")  # clear queue
    print(f"Applied queued entries to {PERSIST_MD.name}")
    return True

def apply_agents_queue() -> bool:
    queued = _read(AGENTS_Q).strip()
    if not queued:
        print("No queued updates for AGENTS.md")
        return False
    if not AGENTS_MD.exists():
        raise FileNotFoundError(f"Missing {AGENTS_MD}")

    existing = _read(AGENTS_MD)
    stamp = _iso_now()
    appended = f"\n\n<!-- Batch update applied {stamp} -->\n\n" + queued.rstrip() + "\n"
    _write(AGENTS_MD, existing + appended)
    _write(AGENTS_Q, "")  # clear queue
    print(f"Applied queued updates to {AGENTS_MD.name}")
    return True

def status():
    persist_bytes = len(_read(PERSIST_Q).strip())
    agents_bytes = len(_read(AGENTS_Q).strip())
    print("Queue status:")
    print(f"  AGENTS-persist.md: {'pending' if persist_bytes else 'empty'} "
          f"({persist_bytes} chars)")
    print(f"  AGENTS.md: {'pending' if agents_bytes else 'empty'} "
          f"({agents_bytes} chars)")

def main():
    parser = argparse.ArgumentParser(description="Apply batched updates to AGENTS files.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("apply", help="Apply all queued updates")
    sub.add_parser("status", help="Show queue status")
    args = parser.parse_args()

    _ensure_queue_files()

    if args.cmd == "status":
        status()
    elif args.cmd == "apply":
        any_applied = False
        try:
            any_applied |= apply_persist_queue()
            any_applied |= apply_agents_queue()
        finally:
            if not any_applied:
                print("Nothing to apply.")

if __name__ == "__main__":
    main()
