#!/usr/bin/env python3
"""Download and extract all data for AvitoTech ML CUP 2026."""

import os
import subprocess
import sys
from pathlib import Path

BASE_URL = "https://storage.yandexcloud.net/datafest2026/datafest_2026_v2_v4"

FILES = [
    # Small files
    "item_features.parquet",
    "contact_eids.csv",
    "eval_users.csv",
    "prepare_local_eval.py",
    "popular.py",
    "submission_popular.csv",
    # Archives
    "eval_user_events.zip",
    "train_000-019.zip",
    "train_020-039.zip",
    "train_040-059.zip",
    "train_060-079.zip",
    "train_080-099.zip",
]


def download_file(filename: str, data_dir: Path, resume: bool = True):
    """Download a single file using curl with resume support."""
    url = f"{BASE_URL}/{filename}"
    dest = data_dir / filename

    if dest.exists() and resume:
        print(f"  Already exists: {filename}")
        return

    print(f"  Downloading: {filename}...")
    cmd = ["curl", "-L", "-C", "-", "-o", str(dest), url]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"  ERROR: Failed to download {filename}")
        sys.exit(1)


def extract_archives(data_dir: Path):
    """Extract all zip archives."""
    train_dir = data_dir / "train_data"

    for zip_file in sorted(data_dir.glob("*.zip")):
        out_file = data_dir / zip_file.name.replace(".zip", ".pq")
        if out_file.exists():
            print(f"  Already extracted: {zip_file.name}")
            continue

        print(f"  Extracting: {zip_file.name}...")
        subprocess.run(["unzip", "-o", str(zip_file), "-d", str(data_dir)], check=True)


def main():
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    print("=== Downloading files ===")
    for f in FILES:
        download_file(f, data_dir)

    print("\n=== Extracting archives ===")
    extract_archives(data_dir)

    # Rename eval_user_events.pq if needed (some archives may produce different names)
    eval_events = data_dir / "eval_user_events.pq"
    if not eval_events.exists():
        for alt in data_dir.glob("eval_user_events*"):
            if alt.suffix in (".pq", ".parquet"):
                alt.rename(eval_events)
                break

    print("\n=== Done! ===")
    print("Files in data/:")
    for p in sorted(data_dir.iterdir()):
        size = p.stat().st_size if p.is_file() else 0
        print(f"  {p.name} ({size / 1e9:.2f} GB)" if size > 1e6 else f"  {p.name}")


if __name__ == "__main__":
    main()
