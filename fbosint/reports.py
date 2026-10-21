"""JSON and CSV report export."""
import csv, json
from pathlib import Path
from .storage import data_dir

def export_case(case: dict, fmt: str, out_dir: str | Path | None = None) -> Path:
    folder = Path(out_dir) if out_dir else data_dir() / "reports"
    folder.mkdir(parents=True, exist_ok=True)
    stem = f"case_{case['id']}"
    if fmt == "json":
        path = folder / f"{stem}.json"
        path.write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return path
    if fmt != "csv":
        raise ValueError("Format must be json or csv")
    path = folder / f"{stem}.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["record_type", "id", "timestamp", "label_or_description", "value", "sha256", "size_bytes"])
        writer.writerow(["case", case["id"], case["created_at"], case["title"], case["owner"], "", ""])
        for row in case["urls"]:
            writer.writerow(["url", row["id"], row["added_at"], row["label"], row["url"], "", ""])
        for row in case["notes"]:
            writer.writerow(["note", row["id"], row["added_at"], "Investigation note", row["note"], "", ""])
        for row in case["evidence"]:
            writer.writerow(["evidence", row["id"], row["added_at"], row["description"], row["filename"], row["sha256"], row["size_bytes"]])
    return path
