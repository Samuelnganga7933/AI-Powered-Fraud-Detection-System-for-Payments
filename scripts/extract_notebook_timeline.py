"""Extract development evidence from Jupyter notebook execution metadata.

This reports dates recorded inside notebooks; it does not alter Git timestamps.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

KEYWORDS = (
    "dataset", "preprocess", "normalize", "encode", "split", "gan", "synthetic",
    "randomforest", "classifier", "accuracy", "precision", "recall", "f1", "roc", "model saved",
)


def source_text(cell: dict) -> str:
    source = cell.get("source", [])
    return "".join(source) if isinstance(source, list) else str(source)


def extract(path: Path) -> list[dict]:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for index, cell in enumerate(notebook.get("cells", [])):
        info = cell.get("metadata", {}).get("executionInfo", {})
        timestamp = info.get("timestamp")
        source = source_text(cell)
        if not timestamp:
            continue
        lowered = source.lower()
        if not any(keyword in lowered for keyword in KEYWORDS):
            continue
        recorded = datetime.fromtimestamp(timestamp / 1000, timezone.utc)
        rows.append(
            {
                "notebook": path.name,
                "cell": index,
                "timestamp_utc": recorded.isoformat(timespec="seconds"),
                "author": info.get("user", {}).get("displayName", "unknown"),
                "summary": next((line.strip().lstrip("# ") for line in source.splitlines() if line.strip()), "code cell"),
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebooks", nargs="+", type=Path)
    args = parser.parse_args()
    records = [record for path in args.notebooks for record in extract(path)]
    for record in sorted(records, key=lambda item: item["timestamp_utc"]):
        print(
            f"{record['timestamp_utc']} | {record['notebook']} | "
            f"cell {record['cell']} | {record['author']} | {record['summary']}"
        )


if __name__ == "__main__":
    main()
