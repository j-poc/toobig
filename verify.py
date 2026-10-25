"""Check a toobig ledger and its anchors with the Python standard library: python3 verify.py ledger/forecasts.jsonl [old.jsonl]

Line i is one forecast. Its "hash" is the sha256 of the line's other fields as JSON with sorted keys and no spaces,
its "prev" is the hash of line i-1 (64 zeros for the first line), and its "seq" is i. anchors/<seq>.json holds
{"seq":N,"hash":H}: the hash of entry N, which commits to every entry before it. Its .ots file timestamps that file.
Given a copy of the ledger saved earlier, it also checks the ledger still starts with it byte for byte.
"""
import hashlib
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
if len(sys.argv) > 2 and not path.read_bytes().startswith(Path(sys.argv[2]).read_bytes()):
    sys.exit(f"CHANGED: {path} does not start with {sys.argv[2]}, so a forecast in it was edited or removed")
entries = [json.loads(line) for line in path.open() if line.strip()]
prev = "0" * 64
for i, e in enumerate(entries):
    body = {k: v for k, v in e.items() if k != "hash"}
    digest = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if e.get("seq") != i or e.get("prev") != prev or e.get("hash") != digest:
        sys.exit(f"BROKEN: line {i + 1} does not chain (seq {e.get('seq')})")
    prev = digest
print(f"{len(entries)} entries, chain intact, head {prev}")

bad = 0
for f in sorted((path.parent / "anchors").glob("*.json"), key=lambda f: int(f.stem)):
    a = json.loads(f.read_text())
    ok = int(f.stem) == a["seq"] < len(entries) and entries[a["seq"]]["hash"] == a["hash"]
    bad += not ok
    print(f"anchor {f.name}: {'matches entry ' + str(a['seq']) if ok else 'DOES NOT MATCH the ledger'}"
          f"{'' if Path(f'{f}.ots').exists() else ', no .ots proof yet'}")
sys.exit(1 if bad else 0)
