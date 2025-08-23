# FPL AI Manager

A toolkit for Fantasy Premier League (FPL) managers who want to leverage data science to optimize decision‑making. It uses an XGBoost model to predict player performance (expected points, xP) and a mixed‑integer linear programming optimizer to suggest transfers, captaincy, and starting lineups. The workflow is a clean, repeatable pipeline controlled by a single CLI entry point.

## Overview

- Script‑based pipeline from data prep to transfer suggestions
- Advanced predictive model with a custom “blended form” feature for early‑season accuracy
- Intelligent squad optimization (MILP) that respects FPL rules
- User‑customizable constraints (keep/sell/consider specific players)
- Secure credential management via `.env`

## Technology stack

- Language: Python 3.10+
- Core libraries: pandas, scikit‑learn, xgboost, pulp, python‑dotenv
- Environment: Virtual environment (venv)

## Data source & acknowledgements

This project is inspired by and benefits from the comprehensive dataset provided by the FPL‑Elo‑Insights ecosystem, which combines official FPL API data, detailed match statistics, and historical team Elo ratings.

## Setup & installation

### 1) Clone the repository

```bash
git clone https://github.com/your-username/FPLytics.git
cd FPLytics
```

### 2) Set up a virtual environment

It’s recommended to use a virtual environment to manage dependencies.

```bash
# Create the virtual environment
python -m venv .venv

# Activate it (macOS/Linux)
source .venv/bin/activate

# On Windows
# .venv\Scripts\activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Set up your FPL credentials

Your FPL login credentials (cookie and tokens) are needed to fetch your team data. A helper script parses a copied cURL command and writes a `.env` file.

1. Log in at https://fantasy.premierleague.com.
2. Open DevTools → Network tab.
3. Find a request like `my-team/{YOUR_ID}` → right‑click → Copy → Copy as cURL (bash).
4. In the project root, create `curl_input.txt` and paste the entire cURL command.
5. Run the secrets updater:

```bash
python update_secrets.py
```

This parses `curl_input.txt` and creates a `.env` with your secrets. Repeat when your FPL session expires.

Note: If `update_secrets.py` is not present in this repo, add it or adjust to your local secrets workflow.

## Project workflow

All commands are run via `main.py`.

### One‑time setup: build data and train model

```bash
python main.py --build-data --train
```

Outputs:

- `data/master_training_data.csv`
- `models/fpl_model_v1.joblib`

### Weekly workflow

1. Update secrets if needed (session expired):

```bash
python update_secrets.py
```

2. Get suggestions (predict + optimize):

```bash
python main.py --predict --suggest
```

This will:

- Generate player predictions and save to `data/`
- Fetch your current team
- Run the optimizer
- Save final suggestions to `suggested_transfers/`

## Repository structure

- `main.py` — CLI entry for the pipeline
- `data/` — datasets and generated predictions
- `models/` — serialized models (e.g., joblib)
- `scripts/` — pipeline scripts (build, train, predict, suggest)
- `notebooks/` — exploration and model development
- `suggested_transfers/` — saved recommendation outputs
- `requirements.txt` — Python dependencies
- `Dockerfile` — containerized environment

## Troubleshooting

- Authentication errors: re‑run `python update_secrets.py` to refresh cookies/tokens
- Missing dependencies: ensure the virtual environment is active and re‑install `requirements.txt`
- Paths: run commands from the project root so relative paths resolve correctly

## License

This project is for educational and personal use. Review and adapt before production use.
