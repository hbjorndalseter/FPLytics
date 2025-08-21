FPL AI Manager 🤖⚽
Overview
FPL AI Manager is a comprehensive toolkit for Fantasy Premier League (FPL) managers who want to leverage data science to optimize their decision-making. This project uses a machine learning model to predict player performance (Expected Points - xP) and an optimization algorithm to suggest the best possible transfers, captaincy choices, and starting lineups.

The entire pipeline is containerized with Docker for easy and reproducible execution.

Core Features
Automated Data Pipeline: Fetches the latest player stats, fixture details, and performance data from the official FPL API and other sources.

Predictive Modeling: Uses an XGBoost model trained on historical data to forecast player points for future gameweeks.

Squad Optimization: Implements a Mixed-Integer Linear Programming (MILP) solver to recommend the optimal weekly transfers and team structure, considering budget, transfer costs, and formation constraints.

Reproducible Environment: The entire project is containerized with Docker, ensuring the environment is consistent and easy to set up.

Technology Stack
Language: Python 3.10

Data Manipulation: pandas, numpy

Data Acquisition: requests

Machine Learning: scikit-learn, xgboost

Optimization: PuLP

Database: SQLite

Environment: Docker

Setup & Installation
Prerequisites
Docker installed on your machine.

A code editor like VS Code.

A Git client.

Installation Steps
Clone the repository:

git clone https://github.com/your-username/fpl-ai-manager.git
cd fpl-ai-manager

Build the Docker Image:
This command builds a Docker image named fpl-pipeline based on the Dockerfile. It will install all the necessary Python libraries and set up the environment. This only needs to be run once, or whenever you update requirements.txt.

docker build -t fpl-pipeline .

Initialize the Database:
The first time you run the project, you'll need to fetch historical data to create and populate your SQLite database.

docker run --rm -v $(pwd)/data:/app/data fpl-pipeline python main.py --setup

Note: The -v $(pwd)/data:/app/data command mounts the local ./data directory into the container. This ensures that your SQLite database (fpl_data.db) is saved on your machine, not just inside the temporary container.

Weekly Workflow
Here is the recommended operational loop for using the tool each gameweek.

1. Fetch Latest Gameweek Data
   After the final match of a gameweek has concluded, run this command to pull the latest results, price changes, and stats.

docker run --rm -v $(pwd)/data:/app/data fpl-pipeline python main.py --fetch-data

2. Generate New Predictions
   With the latest data ingested, you can now generate fresh Expected Points (xP) predictions for the upcoming gameweeks.

docker run --rm -v $(pwd)/data:/app/data fpl-pipeline python main.py --predict

3. Get Transfer Suggestions
   This is the final step. Run the optimizer to get concrete advice for your team. You will need to provide your FPL Team ID.

docker run --rm -v $(pwd)/data:/app/data fpl-pipeline python main.py --suggest-transfers --team-id YOUR_TEAM_ID

The script will output the recommended transfers, captain, and vice-captain to your terminal.

(Optional) Model Retraining
It is recommended to retrain the model periodically (e.g., every 4-6 gameweeks or during an international break) to incorporate the latest season's trends.

docker run --rm -v $(pwd)/data:/app/data -v $(pwd)/models:/app/models fpl-pipeline python main.py --train-model

Note: This command also mounts a ./models directory to ensure your newly trained model file is saved locally.
