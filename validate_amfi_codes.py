"""
validate_amfi_codes.py
Day 1 — Validate that every AMFI scheme code in fund_master.csv
         exists in nav_history.csv. Writes a short data quality summary.
"""

import os
import pandas as pd

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "raw")
REPORTS_DIR  = os.path.join(os.path.dirname(__file__), "reports")

FUND_MASTER_FILE  = os.path.join(RAW_DATA_DIR, "fund_master.csv")
NAV_HISTORY_FILE  = os.path.join(RAW_DATA_DIR, "nav_history.csv")
SUMMARY_FILE      = os.path.join(REPORTS_DIR, "data_quality_summary.txt")


def load_or_warn(filepath: str, name: str) -> pd.DataFrame | None:
    if not os.path.exists(filepath):
        print(f"  [WARNING] {name} not found at {filepath}")
        return None
    df = pd.read_csv(filepath, low_memory=False)
    print(f"  Loaded {name}: {df.shape[0]:,} rows × {df.shape[1]} cols")
    return df


def validate(fund_master: pd.DataFrame, nav_history: pd.DataFrame) -> dict:
    """Cross-check scheme codes between the two datasets."""

    # Detect scheme-code column names (flexible)
    def find_col(df, candidates):
        for c in candidates:
            if c in df.columns:
                return c
        return df.columns[0]   # fallback to first column

    fm_col = find_col(fund_master, ["scheme_code", "amfi_code", "code", "SchemeCode"])
    nh_col = find_col(nav_history,  ["scheme_code", "amfi_code", "code", "SchemeCode"])

    fm_codes = set(fund_master[fm_col].dropna().astype(int))
    nh_codes = set(nav_history[nh_col].dropna().astype(int))

    in_both   = fm_codes & nh_codes
    only_in_fm = fm_codes - nh_codes
    only_in_nh = nh_codes - fm_codes

    return {
        "fund_master_total":     len(fm_codes),
        "nav_history_total":     len(nh_codes),
        "matched":               len(in_both),
        "missing_from_nav":      sorted(only_in_fm),
        "extra_in_nav":          sorted(only_in_nh),
    }


def write_summary(stats: dict, fund_master: pd.DataFrame, nav_history: pd.DataFrame):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    lines = []

    lines.append("=" * 60)
    lines.append("  DATA QUALITY SUMMARY — Day 1")
    lines.append("=" * 60)
    lines.append("")

    # ── Dataset overview ──────────────────────────────────────────────────────
    lines.append("DATASET OVERVIEW")
    lines.append(f"  fund_master  : {fund_master.shape[0]:>6,} rows × {fund_master.shape[1]} columns")
    lines.append(f"  nav_history  : {nav_history.shape[0]:>6,} rows × {nav_history.shape[1]} columns")
    lines.append("")

    # ── Null value audit ─────────────────────────────────────────────────────
    for label, df in [("fund_master", fund_master), ("nav_history", nav_history)]:
        nulls = df.isnull().sum()
        nulls = nulls[nulls > 0]
        lines.append(f"NULL VALUES — {label}")
        if nulls.empty:
            lines.append("  None found ✓")
        else:
            for col, cnt in nulls.items():
                pct = cnt / len(df) * 100
                lines.append(f"  {col:<35} {cnt:>6,}  ({pct:.1f}%)")
        lines.append("")

    # ── Duplicate rows ────────────────────────────────────────────────────────
    for label, df in [("fund_master", fund_master), ("nav_history", nav_history)]:
        dupes = df.duplicated().sum()
        lines.append(f"DUPLICATE ROWS — {label}  :  {dupes:,}  {'✓' if dupes == 0 else '⚠'}")
    lines.append("")

    # ── AMFI code validation ──────────────────────────────────────────────────
    lines.append("AMFI CODE VALIDATION")
    lines.append(f"  Codes in fund_master           : {stats['fund_master_total']:>6,}")
    lines.append(f"  Codes in nav_history           : {stats['nav_history_total']:>6,}")
    lines.append(f"  Codes present in BOTH          : {stats['matched']:>6,}  ✓")

    missing = stats["missing_from_nav"]
    lines.append(f"  Codes in fund_master NOT in nav: {len(missing):>6,}  {'✓' if not missing else '⚠'}")
    if missing:
        lines.append("    Missing codes (first 20): " + ", ".join(str(c) for c in missing[:20]))

    extra = stats["extra_in_nav"]
    lines.append(f"  Extra codes only in nav_history: {len(extra):>6,}  (informational)")
    lines.append("")

    # ── Fund master structure ─────────────────────────────────────────────────
    for col in ["fund_house", "category", "sub_category", "risk_grade"]:
        if col in fund_master.columns:
            unique_vals = fund_master[col].dropna().unique()
            lines.append(f"UNIQUE {col.upper()} VALUES ({len(unique_vals)})")
            for v in sorted(unique_vals):
                lines.append(f"  • {v}")
            lines.append("")

    # ── Overall verdict ───────────────────────────────────────────────────────
    issues = len(missing)
    lines.append("OVERALL VERDICT")
    if issues == 0:
        lines.append("  ✅  All AMFI codes validated. Data quality looks good.")
    else:
        lines.append(f"  ⚠️   {issues} scheme(s) in fund_master have no NAV history — investigate.")
    lines.append("")
    lines.append("=" * 60)

    report = "\n".join(lines)
    print("\n" + report)

    with open(SUMMARY_FILE, "w") as f:
        f.write(report)
    print(f"\n  Report saved → {SUMMARY_FILE}")


def main():
    print("\n" + "█" * 60)
    print("  MUTUAL FUND ANALYSIS — Day 1: AMFI Code Validation")
    print("█" * 60 + "\n")

    fund_master = load_or_warn(FUND_MASTER_FILE, "fund_master")
    nav_history  = load_or_warn(NAV_HISTORY_FILE, "nav_history")

    if fund_master is None or nav_history is None:
        print("\n  Cannot validate — one or both files missing. Run data_ingestion.py first.")
        return

    stats = validate(fund_master, nav_history)
    write_summary(stats, fund_master, nav_history)


if __name__ == "__main__":
    main()
