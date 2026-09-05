import os
import sys
import time
import sqlite3
import subprocess
from datetime import datetime, timezone

METRICS_CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "t011_metrics.csv")

def get_pi3_metrics():
    try:
        cmd = "ssh worldnews-pi3 \"free -m | grep Mem; uptime; df -m /; cd ~/world_news && ./venv/bin/python get_initial_stats.py\""
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        lines = res.stdout.strip().split("\n")
        
        ram_used, ram_avail = "0", "0"
        for l in lines:
            if l.startswith("Mem:"):
                p = l.split()
                ram_used = p[2] if len(p) > 2 else "0"
                ram_avail = p[6] if len(p) > 6 else "0"

        up_line = [l for l in lines if "load average:" in l]
        load_avg = up_line[0].split("load average:")[1].strip() if up_line else "0.0"

        df_line = [l for l in lines if "/dev/" in l or "root" in l or l.endswith("/")]
        disk_used = df_line[0].split()[2] if df_line else "0"

        art, pend, sent, fail = 0, 0, 0, 0
        for l in lines:
            if "pi3_total_articles:" in l: art = int(l.split(":")[1].strip())
            if "pi3_pending_articles:" in l: pend = int(l.split(":")[1].strip())
            if "pi3_sent_articles:" in l: sent = int(l.split(":")[1].strip())
            if "pi3_failed_articles:" in l: fail = int(l.split(":")[1].strip())

        return {
            "ram_used_mb": ram_used,
            "ram_avail_mb": ram_avail,
            "load_avg": load_avg,
            "disk_used_mb": disk_used,
            "articles": art,
            "pending": pend,
            "sent": sent,
            "failed": fail,
        }
    except Exception as e:
        return {"ram_used_mb": "0", "ram_avail_mb": "0", "load_avg": "0", "disk_used_mb": "0", "articles": 0, "pending": 0, "sent": 0, "failed": 0}

def get_pi4_metrics():
    try:
        cmd = "ssh worldnews-pi4 \"free -m | grep Mem; uptime; df -m /; cd ~/world_news && ./venv/bin/python get_full_summary.py\""
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        lines = res.stdout.strip().split("\n")

        ram_used, ram_avail = "0", "0"
        for l in lines:
            if l.startswith("Mem:"):
                p = l.split()
                ram_used = p[2] if len(p) > 2 else "0"
                ram_avail = p[6] if len(p) > 6 else "0"

        up_line = [l for l in lines if "load average:" in l]
        load_avg = up_line[0].split("load average:")[1].strip() if up_line else "0.0"

        df_line = [l for l in lines if "/dev/" in l or "root" in l or l.endswith("/")]
        disk_used = df_line[0].split()[2] if df_line else "0"

        art, pend_j, comp_j, fail_j, ana, act_e, exp_e = 0, 0, 0, 0, 0, 0, 0
        for l in lines:
            if "Pi4 articles:" in l: art = int(l.split(":")[1].strip())
            if "processing jobs:" in l: pend_j = int(l.split(":")[1].strip())
            if "jobs completed:" in l: comp_j = int(l.split(":")[1].strip())
            if "jobs failed:" in l: fail_j = int(l.split(":")[1].strip())
            if "analyses:" in l: ana = int(l.split(":")[1].strip())
            if "active events:" in l: act_e = int(l.split(":")[1].strip())
            if "expired events:" in l: exp_e = int(l.split(":")[1].strip())

        return {
            "ram_used_mb": ram_used,
            "ram_avail_mb": ram_avail,
            "load_avg": load_avg,
            "disk_used_mb": disk_used,
            "articles": art,
            "pending_jobs": pend_j,
            "completed_jobs": comp_j,
            "failed_jobs": fail_j,
            "analyses": ana,
            "active_events": act_e,
            "expired_events": exp_e,
        }
    except Exception as e:
        return {"ram_used_mb": "0", "ram_avail_mb": "0", "load_avg": "0", "disk_used_mb": "0", "articles": 0, "pending_jobs": 0, "completed_jobs": 0, "failed_jobs": 0, "analyses": 0, "active_events": 0, "expired_events": 0}

def record_sample():
    now_str = datetime.now(timezone.utc).isoformat()
    pi3 = get_pi3_metrics()
    pi4 = get_pi4_metrics()

    header = "timestamp,pi3_ram_used_mb,pi3_ram_avail_mb,pi3_load,pi3_articles,pi3_pending,pi3_sent,pi4_ram_used_mb,pi4_ram_avail_mb,pi4_load,pi4_articles,pi4_pending_jobs,pi4_completed_jobs,pi4_failed_jobs,pi4_analyses,pi4_active_events,pi4_expired_events,disk_used_pi3,disk_used_pi4\n"
    
    file_exists = os.path.exists(METRICS_CSV_PATH)
    with open(METRICS_CSV_PATH, "a", encoding="utf-8") as f:
        if not file_exists:
            f.write(header)
        row = f"{now_str},{pi3['ram_used_mb']},{pi3['ram_avail_mb']},\"{pi3['load_avg']}\",{pi3['articles']},{pi3['pending']},{pi3['sent']},{pi4['ram_used_mb']},{pi4['ram_avail_mb']},\"{pi4['load_avg']}\",{pi4['articles']},{pi4['pending_jobs']},{pi4['completed_jobs']},{pi4['failed_jobs']},{pi4['analyses']},{pi4['active_events']},{pi4['expired_events']},{pi3['disk_used_mb']},{pi4['disk_used_mb']}\n"
        f.write(row)
    print(f"[{now_str}] Metrics recorded: Pi3 Articles={pi3['articles']}, Pi4 Articles={pi4['articles']}, Active Evts={pi4['active_events']}")

if __name__ == "__main__":
    record_sample()
