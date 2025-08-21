# scripts/data_fetcher.py
import requests
import pandas as pd
from .database import get_db_engine

FPL_API_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"

def fetch_and_store_players():
    """Fetches player data and stores it in the database."""
    print("Fetching player data from FPL API...")
    response = requests.get(FPL_API_URL)
    response.raise_for_status()  # Raises an error for bad responses
    data = response.json()

    # Convert players data to a pandas DataFrame
    players_df = pd.DataFrame(data['elements'])
    
    # Get the database engine
    engine = get_db_engine()
    
    # Store the DataFrame in a table named 'players'
    players_df.to_sql('players', engine, if_exists='replace', index=False)
    print(f"Successfully stored {len(players_df)} players in the database.")

# You can add more functions here to fetch fixtures, teams, etc.