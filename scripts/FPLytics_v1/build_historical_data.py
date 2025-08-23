import pandas as pd
import os

def run():
    print("---Starting to build historical training data---")

    # --- Configuration ---
    SEASON = "2024-2025"

    # --- Load Master Files ---
    # The main logbook of player stats for every gameweek
    playerstats_url = f'https://raw.githubusercontent.com/olbauday/FPL-Elo-Insights/main/data/{SEASON}/playerstats/playerstats.csv'
    all_player_stats_df = pd.read_csv(playerstats_url)

    # Helper file for player info (position, team_code)
    players_url = f'https://raw.githubusercontent.com/olbauday/FPL-Elo-Insights/main/data/{SEASON}/players/players.csv'
    players_df = pd.read_csv(players_url)

    # Helper file for team info (elo, name)
    teams_url = f'https://raw.githubusercontent.com/olbauday/FPL-Elo-Insights/main/data/{SEASON}/teams/teams.csv'
    teams_df = pd.read_csv(teams_url)

    print("Master files for the 2024-2025 season loaded successfully!")

    # --- Create a single, comprehensive player data table ---

    # 1. Merge player stats with player info to get team_code and position
    # *** ADD 'web_name' TO THIS LIST ***
    comp_df = pd.merge(all_player_stats_df, players_df[['player_id', 'web_name', 'position', 'team_code']], left_on='id', right_on='player_id')

    # 2. Merge the result with team info to get team_id, name, and elo
    comp_df = pd.merge(comp_df, teams_df[['code', 'id', 'name', 'elo']], left_on='team_code', right_on='code')

    # 3. Clean up the DataFrame
    comp_df.drop(columns=['player_id', 'code'], inplace=True)
    comp_df.rename(columns={'id_y': 'team_id', 'name': 'team_name', 'elo': 'team_elo'}, inplace=True)

    print("Comprehensive player DataFrame created.")
    # This line will now work correctly
    comp_df[['web_name', 'gw', 'total_points', 'team_name', 'team_elo']].head()

    # List to hold the processed DataFrame for each gameweek
    processed_gws = []

    print("--- Starting to add opponent information for each gameweek ---")

    # Loop through each gameweek of the 2024-2025 season
    for gw in range(1, 39):
        try:
            # *** CORRECTED URL STRUCTURE FOR MATCHES ***
            matches_url = f'https://raw.githubusercontent.com/olbauday/FPL-Elo-Insights/main/data/2024-2025/matches/GW{gw}/matches.csv'
            matches_df = pd.read_csv(matches_url)

            # Filter your main DataFrame for the current gameweek
            gw_player_stats = comp_df[comp_df['gw'] == gw].copy()

            # Define the function to get opponent info
            def get_opponent_info(team_id, fixtures):
                match = fixtures[(fixtures['home_team'] == team_id) | (fixtures['away_team'] == team_id)]
                if not match.empty:
                    if match.iloc[0]['home_team'] == team_id:
                        return match.iloc[0]['away_team_elo'], True # Home
                    else:
                        return match.iloc[0]['home_team_elo'], False # Away
                return None, None

            # Apply the function to add opponent_elo and is_home
            opponent_info = gw_player_stats['team_id'].apply(lambda x: get_opponent_info(x, matches_df))
            gw_player_stats[['opponent_elo', 'is_home']] = pd.DataFrame(opponent_info.tolist(), index=gw_player_stats.index)
            
            # Store the processed DataFrame
            processed_gws.append(gw_player_stats)
            print(f"Successfully processed GW{gw}")

        except Exception as e:
            print(f"Could not process GW{gw}. Error: {e}")

    # --- Final Step: Combine all processed gameweeks into the master training DataFrame ---
    if processed_gws:
        master_training_df = pd.concat(processed_gws, ignore_index=True)
        print("\n-----------------------------------------")
        print("Master training DataFrame created successfully!")
        print(f"Shape of the final DataFrame: {master_training_df.shape}")
        print(master_training_df[['web_name', 'gw', 'total_points', 'opponent_elo', 'is_home']].head())
    else:
        print("\nNo data was processed. The master DataFrame is empty.")

    # Get the list of all column names
    all_columns = list(master_training_df.columns)

    # Print the total number of columns
    print(f"Total columns in master_training_df: {len(all_columns)}")

    # Print each column name
    print("\n--- Column List ---")
    for column in all_columns:
        print(column)

    # --- Save the final DataFrame to a CSV file ---

    # Define the path to the root data folder
    output_dir = '../../data'
    output_file = os.path.join(output_dir, 'master_training_data.csv')

    # Create the data directory in the root if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Save the DataFrame to the correct location
    master_training_df.to_csv(output_file, index=False)

    print(f"Master training DataFrame successfully saved to '{output_file}'")