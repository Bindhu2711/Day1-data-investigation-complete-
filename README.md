project Structure
mutual_fund_analysis/
├── data/
│   ├── raw/           # Original CSVs & live-fetched NAV files
│   └── processed/     # Cleaned & transformed datasets
├── notebooks/         # Jupyter notebooks for exploration
├── sql/               # SQL queries and schema
├── dashboard/         # Plotly / Dash dashboard code
├── reports/           # Auto-generated quality & analysis reports
├── data_ingestion.py      # Load & inspect all 10 CSVs
├── live_nav_fetch.py      # Fetch live NAV from mfapi.in
├── validate_amfi_codes.py # Data quality validation
└── requirements.txt
Setup
# 1. Clone the repo
git clone <your-repo-url>
cd mutual_fund_analysis

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
Day 1 — Data Ingestion
Place your 10 CSV datasets inside data/raw/, then run:

# Inspect all CSVs
python data_ingestion.py

# Fetch live NAV from mfapi.in
python live_nav_fetch.py

# Validate AMFI codes & write data quality report
python validate_amfi_codes.py
Schemes fetched by live_nav_fetch.py:

Scheme	AMFI Code
HDFC Top 100 Direct	125497
SBI Bluechip	119551
ICICI Bluechip	120503
Nippon Large Cap	118632
Axis Bluechip	119092
Kotak Bluechip	120841
Day 1 Deliverables:

data_ingestion.py
live_nav_fetch.py
validate_amfi_codes.py
requirements.txt
GitHub repo with Day 1 commit
Git Workflow
git add .
git commit -m "Day 1: Data ingestion complete"
git push origin main
