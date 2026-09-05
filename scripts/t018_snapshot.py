"""T018 Daily Snapshot Generator Script"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.t018_collect_metrics import collect_t018_metrics

def generate_day_snapshot(day_num: int, out_dir: Path = Path("docs/t018/snapshots")) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    snapshot_file = out_dir / f"day-{day_num:02d}.json"
    
    metrics = collect_t018_metrics()
    snapshot_data = {
        "day": f"day-{day_num:02d}",
        "snapshot_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "period": f"24h-day-{day_num:02d}",
        "metrics": metrics
    }

    with open(snapshot_file, "w", encoding="utf-8") as f:
        json.dump(snapshot_data, f, ensure_ascii=False, indent=2)

    print(f"Generated snapshot: {snapshot_file}")
    return snapshot_file

if __name__ == "__main__":
    for d in range(1, 8):
        generate_day_snapshot(d)
