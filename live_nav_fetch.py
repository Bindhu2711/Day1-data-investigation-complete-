"""
live_nav_fetch.py
Day 1 — Fetch live NAV data from mfapi.in for key mutual fund schemes.
Parses JSON responses and saves each as a raw CSV in data/raw/.
"""

import os
import time
import requests
import pandas as pd

# ── Configuration ─────────────────────────────────────────────────────────────
BASE_URL = "https://api.mfapi.in/mf/{scheme_code}"
RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "raw")

# Key schemes to fetch  {display_name: amfi_code}
SCHEMES = {
    "HDFC_Top100_Direct":    125497,
    "SBI_Bluechip":          119551,
    "ICICI_Bluechip":        120503,
    "Nippon_LargeCap":       118632,
    "Axis_Bluechip":         119092,
    "Kotak_Bluechip":        120841,
}

REQUEST_DELAY_SECONDS = 0.5   # be polite to the free API


def fetch_nav(scheme_code: int, scheme_name: str) -> pd.DataFrame | None:
    """Fetch NAV history for one scheme; return as DataFrame."""
    url = BASE_URL.format(scheme_code=scheme_code)
    print(f"  Fetching [{scheme_code}] {scheme_name} ... ", end="", flush=True)

    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"FAILED — {exc}")
        return None

    payload = resp.json()

    # mfapi structure: {"meta": {...}, "data": [{"date": "...", "nav": "..."}, ...]}
    meta = payload.get("meta", {})
    nav_records = payload.get("data", [])

    if not nav_records:
        print("EMPTY response.")
        return None

    df = pd.DataFrame(nav_records)
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    df["scheme_code"] = scheme_code
    df["scheme_name"] = meta.get("scheme_name", scheme_name)
    df["fund_house"] = meta.get("fund_house", "")
    df["scheme_type"] = meta.get("scheme_type", "")
    df["scheme_category"] = meta.get("scheme_category", "")

    df.sort_values("date", inplace=True)
    df.reset_index(drop=True, inplace=True)

    print(f"OK  ({len(df):,} NAV records)")
    return df


def save_csv(df: pd.DataFrame, scheme_name: str) -> str:
    """Save DataFrame to data/raw/ and return the filepath."""
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    filename = f"nav_{scheme_name}.csv"
    filepath = os.path.join(RAW_DATA_DIR, filename)
    df.to_csv(filepath, index=False)
    print(f"    Saved → {filepath}")
    return filepath


def print_snapshot(df: pd.DataFrame):
    """Print a quick summary of the fetched NAV data."""
    print(f"    Date range : {df['date'].min().date()} → {df['date'].max().date()}")
    print(f"    Latest NAV : ₹{df['nav'].iloc[-1]:.4f}  (as of {df['date'].iloc[-1].date()})")
    print(f"    All-time high : ₹{df['nav'].max():.4f}")
    print(f"    All-time low  : ₹{df['nav'].min():.4f}")


def main():
    print("\n" + "█" * 60)
    print("  MUTUAL FUND ANALYSIS — Day 1: Live NAV Fetch")
    print("█" * 60 + "\n")

    results = {}

    for name, code in SCHEMES.items():
        df = fetch_nav(code, name)

        if df is not None:
            print_snapshot(df)
            save_csv(df, name)
            results[name] = df

        time.sleep(REQUEST_DELAY_SECONDS)

    print(f"\n{'='*60}")
    print(f"  Done. {len(results)}/{len(SCHEMES)} schemes fetched successfully.")
    print(f"{'='*60}\n")

    # ── Optional: combined file ───────────────────────────────────────────────
    if results:
        combined = pd.concat(results.values(), ignore_index=True)
        combined_path = os.path.join(RAW_DATA_DIR, "nav_all_schemes_combined.csv")
        combined.to_csv(combined_path, index=False)
        print(f"  Combined file saved → {combined_path}")
        print(f"  Total rows in combined file: {len(combined):,}\n")

    return results


if __name__ == "__main__":
    main()
