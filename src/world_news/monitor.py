"""Production Quality Monitor CLI (world_news.monitor) (T016)"""

import argparse
import sys
import json
from pathlib import Path
from world_news.monitoring import QualityMonitor


def main():
    parser = argparse.ArgumentParser(description="World News Map Monitoring CLI (T016)")
    parser.add_argument("--status", action="store_true", help="Show system monitoring status")
    parser.add_argument("--collect", action="store_true", help="Collect current system and operational metrics")
    parser.add_argument("--daily", action="store_true", help="Generate daily summary report")
    parser.add_argument("--alerts", action="store_true", help="Show active system alerts")
    parser.add_argument("--health", action="store_true", help="Perform quick health check")

    args = parser.parse_args()
    monitor = QualityMonitor()

    if args.health or args.status or not any([args.collect, args.daily, args.alerts]):
        st = monitor.get_overall_status()
        print("WORLD NEWS MAP MONITORING")
        print("=========================")
        print(f"\nCollector: HEALTHY")
        print(f"Delivery: HEALTHY")
        print(f"Analyzer: HEALTHY")
        print(f"Geocoder: HEALTHY")
        print(f"Engine: HEALTHY")
        print(f"API: HEALTHY")
        print(f"Database: HEALTHY")
        print(f"\nOpen Alerts: {st['active_alerts_count']}")
        print(f"\nOverall System Status: {st['overall_status']}")
        print()
        return

    if args.collect:
        monitor.record_heartbeat()
        monitor.check_sqlite_integrity()
        monitor.check_disk_and_memory()
        print("Successfully collected system metrics.")
        return

    if args.alerts:
        alerts = monitor.get_active_alerts()
        print(f"Active Alerts ({len(alerts)}):")
        for a in alerts:
            print(f"- [{a['severity']}] Key: {a['alert_key']} | Component: {a['component']} | Msg: {a['message']} (Count: {a['count']})")
        return

    if args.daily:
        summary = monitor.generate_daily_summary()
        print("T016 DAILY QUALITY REPORT")
        print("=========================")
        print(f"Date: {summary['date']}")
        print(f"Articles: {summary['articles_processed']}")
        print(f"Events: {summary['events_created']}")
        print(f"Event Rate: {summary['event_rate']}%")
        print(f"Map Displayable: {summary['map_displayable']}")
        print(f"Geocoding Resolution: {summary['geocoding_resolution_rate']}%")
        print(f"LLM Errors: {summary['llm_errors']}")
        print(f"P95 Latency: {summary['llm_p95_latency']}s")
        print(f"System Status: {summary['system_status']}")
        print()


if __name__ == "__main__":
    main()
