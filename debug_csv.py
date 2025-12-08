#!/usr/bin/env python3
"""Debug script to inspect INMET CSV structure."""

from pathlib import Path

data_dir = Path("/app/data/inmet/processed")

# Find first PE station CSV
for year_dir in sorted(data_dir.glob("*/")):
    for csv_file in year_dir.glob("INMET_NE_PE_*.CSV"):
        print(f"Found PE file: {csv_file.name}")
        print("\nFirst 10 lines:")
        with open(csv_file, "r", encoding="iso-8859-1") as f:
            for i, line in enumerate(f):
                if i >= 10:
                    break
                print(f"{i}: {line.rstrip()}")
        break
    else:
        continue
    break
