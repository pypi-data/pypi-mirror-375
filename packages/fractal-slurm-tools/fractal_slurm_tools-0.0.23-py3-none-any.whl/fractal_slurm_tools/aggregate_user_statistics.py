import json
import csv
from pathlib import Path

def aggregate_stats(base_folder: Path, output_csv: Path):
    # Prepare data list
    records = []

    # Loop through user folders
    for user_folder in base_folder.iterdir():
        if user_folder.is_dir():
            # Find all *_stats.json files
            for stats_file in sorted(user_folder.glob("*_stats.json")):
                try:
                    with open(stats_file, "r") as f:
                        data = json.load(f)
                    
                    record = {
                        "user_email": data.get("user_email", user_folder.name),
                        "year": data.get("year"),
                        "month": data.get("month"),
                        "tot_number_jobs": data.get("tot_number_jobs"),
                        "tot_number_tasks": data.get("tot_number_tasks"),
                        "tot_cpu_hours": data.get("tot_cpu_hours"),
                        "tot_diskread_GB": data.get("tot_diskread_GB"),
                        "tot_diskwrite_GB": data.get("tot_diskwrite_GB"),
                    }
                    records.append(record)
                except Exception as e:
                    print(f"Error reading {stats_file}: {e}")

    # Sort by user_email, then year and month
    records.sort(key=lambda x: (x["user_email"], x["year"], x["month"]))

    # Write to CSV
    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

    print(f"Aggregated CSV written to {output_csv}")
