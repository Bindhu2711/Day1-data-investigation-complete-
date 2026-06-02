"""
data_ingestion.py
Day 1 — Load and inspect all 10 CSV datasets.
Prints .shape, .dtypes, and .head() for each file and notes any anomalies.
"""

import os
import pandas as pd

# ── Configuration ────────────────────────────────────────────────────────────
RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "raw")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "data", "processed")

# Expected CSV filenames (place your 10 CSVs in data/raw/)
CSV_FILES = [
    "nav_history.csv",
    "fund_master.csv",
    "transactions.csv",
    "portfolio.csv",
    "benchmark.csv",
    "sip_data.csv",
    "investor_profile.csv",
    "market_index.csv",
    "dividend_history.csv",
    "expense_ratio.csv",
]


def load_and_inspect(filepath: str) -> pd.DataFrame | None:
    """Load a CSV, print shape/dtypes/head, and flag basic anomalies."""
    filename = os.path.basename(filepath)
    print(f"\n{'='*60}")
    print(f"  FILE : {filename}")
    print(f"{'='*60}")

    if not os.path.exists(filepath):
        print(f"  [WARNING] File not found — skipping: {filepath}")
        return None

    df = pd.read_csv(filepath, low_memory=False)

    print(f"\n  Shape   : {df.shape[0]:,} rows × {df.shape[1]} columns")

    print("\n  dtypes:")
    for col, dtype in df.dtypes.items():
        print(f"    {col:<35} {dtype}")

    print("\n  head(3):")
    print(df.head(3).to_string(index=False))

    # ── Anomaly checks ──────────────────────────────────────────────────────
    anomalies = []

    # 1. Missing values
    null_counts = df.isnull().sum()
    cols_with_nulls = null_counts[null_counts > 0]
    if not cols_with_nulls.empty:
        anomalies.append(
            f"Null values detected in: "
            + ", ".join(
                f"{c} ({v})" for c, v in cols_with_nulls.items()
            )
        )

    # 2. Duplicate rows
    dupe_count = df.duplicated().sum()
    if dupe_count:
        anomalies.append(f"{dupe_count:,} fully duplicate rows found")

    # 3. Negative numerics (likely invalid for financial data)
    numeric_cols = df.select_dtypes(include="number").columns
    for col in numeric_cols:
        neg = (df[col] < 0).sum()
        if neg:
            anomalies.append(f"Column '{col}' has {neg} negative value(s)")

    if anomalies:
        print("\n  [ANOMALIES]")
        for a in anomalies:
            print(f"    • {a}")
    else:
        print("\n  [OK] No obvious anomalies detected.")

    return df


def main():
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    print("\n" + "█" * 60)
    print("  MUTUAL FUND ANALYSIS — Day 1: Data Ingestion")
    print("█" * 60)

    loaded: dict[str, pd.DataFrame] = {}

    for fname in CSV_FILES:
        fpath = os.path.join(RAW_DATA_DIR, fname)
        df = load_and_inspect(fpath)
        if df is not None:
            loaded[fname] = df

    print(f"\n\n{'='*60}")
    print(f"  SUMMARY: {len(loaded)}/{len(CSV_FILES)} files loaded successfully")
    print(f"{'='*60}\n")

    return loaded


if __name__ == "__main__":
    main()
