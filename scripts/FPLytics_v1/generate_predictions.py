import pandas as pd
import joblib

from datetime import datetime

def run():

    print("---Generating predictions for the next gameweek---")

    # URL to the player statistics file
    players_stats_url = 'https://raw.githubusercontent.com/olbauday/FPL-Elo-Insights/main/data/2025-2026/playerstats.csv'

    players_url = 'https://raw.githubusercontent.com/olbauday/FPL-Elo-Insights/main/data/2025-2026/players.csv'


    # Load the data
    players_stats_df = pd.read_csv(players_stats_url)
    players_df = pd.read_csv(players_url)

    print("Player stats loaded successfully!")
    players_stats_df.head()

    print("Player information loaded!")
    players_df.head()

    # List of essential columns to select (with new features added)
    core_features = [
        # IDs and Context
        'id', 'web_name', 'now_cost', 'selected_by_percent', 'form',
        'gw', 

        # FPL Performance Metrics
        'minutes', 'total_points', 'bonus', 'bps',

        # Underlying Performance (Per 90)
        'expected_goals_per_90', 'expected_assists_per_90',
        'expected_goal_involvements_per_90', 'expected_goals_conceded_per_90',
        'starts_per_90', 'clean_sheets_per_90', 'saves_per_90',

        # Set Piece Threat
        'corners_and_indirect_freekicks_order', 'direct_freekicks_order', 'penalties_order',

        # --- NEW FEATURES ---
        # ICT Index
        'influence', 'creativity', 'threat', 'ict_index',

        # Player Status
        'status', 'chance_of_playing_next_round', 
        
        # New season important rule change 
        'defensive_contribution_per_90' 
    ]

    # Create the new DataFrame
    selected_df = players_stats_df[core_features].copy()

    # Fill missing values for set piece takers and chance of playing
    # (A null value for chance_of_playing usually means 100%)
    selected_df['chance_of_playing_next_round'] = selected_df['chance_of_playing_next_round'].fillna(100)
    for col in ['corners_and_indirect_freekicks_order', 'direct_freekicks_order', 'penalties_order']:
        selected_df[col] = selected_df[col].fillna(0)

    print("Core features selected, including ICT and player status.")
    selected_df.head()

    # Select only the columns we need from players_df to avoid clutter
    player_info_df = players_df[['player_id', 'position', 'team_code']]

    # Merge the two DataFrames
    merged_df = pd.merge(selected_df, player_info_df, left_on='id', right_on='player_id')

    # Clean up the ID columns in one step
    merged_df.drop(columns=['player_id'], inplace=True)
    merged_df.rename(columns={'id': 'player_id'}, inplace=True)


    print("Successfully merged and cleaned ID columns.")
    merged_df.head()

    # --- Load Helper Files ---
    # Teams data for team strength (CORRECTED URL)
    teams_url = 'https://raw.githubusercontent.com/olbauday/FPL-Elo-Insights/main/data/2025-2026/teams.csv'
    teams_df = pd.read_csv(teams_url)

    # Gameweeks summary to find the next GW (CORRECTED FILENAME)
    gameweeks_url = 'https://raw.githubusercontent.com/olbauday/FPL-Elo-Insights/main/data/2025-2026/gameweek_summaries.csv'
    gameweeks_df = pd.read_csv(gameweeks_url)


    # --- Step 1: Add Player's Own Team Strength ---
    # Merge teams_df into your main DataFrame
    final_df = pd.merge(merged_df, teams_df[['code', 'id', 'name', 'elo']], left_on='team_code', right_on='code')
    final_df.drop(columns=['code'], inplace=True)
    final_df.rename(columns={'id': 'team_id', 'name': 'team_name', 'elo': 'team_elo'}, inplace=True)


    # --- Step 2: Find Next GW and Load Correct Fixtures ---
    # Find the row where 'is_next' is True and get the 'id' (gameweek number)
    next_gw = gameweeks_df[gameweeks_df['is_next'] == True].iloc[0]['id']
    print(f"Next gameweek is GW{next_gw}. Fetching fixtures...")

    # Construct the correct URL for the next gameweek's fixtures
    fixtures_url = f'https://raw.githubusercontent.com/olbauday/FPL-Elo-Insights/main/data/2025-2026/By%20Gameweek/GW{next_gw}/fixtures.csv'
    next_gw_fixtures = pd.read_csv(fixtures_url)


    # --- Step 3: Add Opponent Info ---
    def get_opponent_info(team_id, fixtures):
        match = fixtures[(fixtures['home_team'] == team_id) | (fixtures['away_team'] == team_id)]
        if not match.empty:
            if match.iloc[0]['home_team'] == team_id:
                return match.iloc[0]['away_team'], match.iloc[0]['away_team_elo'], True # Home
            else:
                return match.iloc[0]['home_team'], match.iloc[0]['home_team_elo'], False # Away
        return None, None, None

    opponent_info = final_df['team_id'].apply(lambda x: get_opponent_info(x, next_gw_fixtures))
    final_df[['opponent_team_id', 'opponent_elo', 'is_home']] = pd.DataFrame(opponent_info.tolist(), index=final_df.index)


    # --- Step 4: Create Final 'elo_diff' Feature ---
    final_df['elo_diff'] = final_df['team_elo'] - final_df['opponent_elo']

    print("Opponent information and final features added.")
    final_df[['web_name', 'team_name', 'team_elo', 'opponent_elo', 'elo_diff', 'is_home']].head()

    # Get the list of all column names from your final DataFrame
    all_columns = list(final_df.columns)

    # Print the total number of columns
    print(f"You have a total of {len(all_columns)} columns in your final_df.")

    # Print each column name, one per line, for easy reading
    print("\n--- Column List ---")
    for column in all_columns:
        print(column)

    
    # --- Step 1: Load All Necessary Source Files ---
    SEASON_CURRENT = "2025-2026"
    player_stats_url = f'https://raw.githubusercontent.com/olbauday/FPL-Elo-Insights/main/data/{SEASON_CURRENT}/playerstats.csv'
    players_url = f'https://raw.githubusercontent.com/olbauday/FPL-Elo-Insights/main/data/{SEASON_CURRENT}/players.csv'
    teams_url = f'https://raw.githubusercontent.com/olbauday/FPL-Elo-Insights/main/data/{SEASON_CURRENT}/teams.csv'
    gameweeks_url = f'https://raw.githubusercontent.com/olbauday/FPL-Elo-Insights/main/data/{SEASON_CURRENT}/gameweek_summaries.csv'

    player_stats_df = pd.read_csv(player_stats_url)
    players_df = pd.read_csv(players_url)
    teams_df = pd.read_csv(teams_url)
    gameweeks_df = pd.read_csv(gameweeks_url)

    # --- Step 2: Build the Base DataFrame ---
    latest_stats_df = player_stats_df.sort_values('gw', ascending=False).drop_duplicates('id', keep='first')
    base_df = pd.merge(latest_stats_df, players_df[['player_id', 'position', 'team_code']], left_on='id', right_on='player_id')
    base_df = pd.merge(base_df, teams_df[['code', 'id', 'name', 'elo']], left_on='team_code', right_on='code')
    base_df.rename(columns={'id_y': 'team_id', 'name': 'team_name', 'elo': 'team_elo'}, inplace=True)

    # --- Step 3: Add Opponent Information ---
    next_gw = gameweeks_df[gameweeks_df['is_next'] == True].iloc[0]['id']
    fixtures_url = f'https://raw.githubusercontent.com/olbauday/FPL-Elo-Insights/main/data/{SEASON_CURRENT}/By%20Gameweek/GW{next_gw}/fixtures.csv'
    next_gw_fixtures = pd.read_csv(fixtures_url)

    def get_opponent_info(team_id, fixtures):
        match = fixtures[(fixtures['home_team'] == team_id) | (fixtures['away_team'] == team_id)]
        if not match.empty:
            return (match.iloc[0]['away_team_elo'], True) if match.iloc[0]['home_team'] == team_id else (match.iloc[0]['home_team_elo'], False)
        return (None, None)

    opponent_info = base_df['team_id'].apply(lambda x: get_opponent_info(x, next_gw_fixtures))
    base_df[['opponent_elo', 'is_home']] = pd.DataFrame(opponent_info.tolist(), index=base_df.index)

    # --- Step 4: Add Blended Form ---
    SEASON_LAST = "2024-2025"
    last_season_stats_url = f'https://raw.githubusercontent.com/olbauday/FPL-Elo-Insights/main/data/{SEASON_LAST}/playerstats/playerstats.csv'
    last_season_players_url = f'https://raw.githubusercontent.com/olbauday/FPL-Elo-Insights/main/data/{SEASON_LAST}/players/players.csv'
    last_season_df = pd.read_csv(last_season_stats_url)
    last_season_players_df = pd.read_csv(last_season_players_url)
    last_season_final_df = last_season_df[last_season_df['gw'] == 38]
    last_season_final_with_names = pd.merge(last_season_final_df, last_season_players_df[['player_id', 'web_name']], left_on='id', right_on='player_id')[['web_name', 'points_per_game']]
    last_season_final_with_names.rename(columns={'points_per_game': 'ppg_last_season'}, inplace=True)

    prediction_df = pd.merge(base_df, last_season_final_with_names, on='web_name', how='left')
    prediction_df['ppg_last_season'] = prediction_df['ppg_last_season'].fillna(2.0)

    current_gw = next_gw - 1

    if current_gw <= 3:
        weight_last_season = 0.85  # Trust last season's data even more
        weight_current_season = 0.15 # Be less influenced by the first few games

    elif 5 <= current_gw <= 10:
        weight_last_season = 0.6
        weight_current_season = 0.4

    else:
        weight_last_season = 0.0
        weight_current_season = 1.0


    prediction_df['form'] = (weight_last_season * prediction_df['ppg_last_season']) + (weight_current_season * prediction_df['form'].astype(float))
    prediction_df.drop_duplicates('player_id', keep='first', inplace=True)

    # --- Step 5: Load Model and Make Predictions ---
    model = joblib.load('../models/fpl_model_v1.joblib')
    prediction_df['is_home'] = prediction_df['is_home'].fillna(0).astype(int)
    features_the_model_expects = model.feature_names_in_
    X_predict = prediction_df[features_the_model_expects]

    predictions = model.predict(X_predict)
    prediction_df['xP'] = predictions

    # --- Step 6: Apply Defensive Bonus and Finalize ---
    def calculate_defensive_bonus(row):
        def_cons = row.get('defensive_contribution_per_90', 0)
        return 2.0 if (row['position'] == 'DEF' and def_cons >= 10) or (row['position'] == 'MID' and def_cons >= 12) else 0.0

    prediction_df['defensive_bonus'] = prediction_df.apply(calculate_defensive_bonus, axis=1)
    prediction_df['xP_adjusted'] = prediction_df['xP'] + prediction_df['defensive_bonus']

    final_predictions_df = prediction_df[['player_id', 'web_name', 'team_name', 'position', 'now_cost', 'xP', 'defensive_bonus', 'xP_adjusted']].sort_values('xP_adjusted', ascending=False)
    predictions_file = f'../data/gw{next_gw}_predictions.csv'
    final_predictions_df.to_csv(predictions_file, index=False)

    print(f"\nFinal predictions for GW{next_gw} saved to '{predictions_file}'")
    print(f"\n--- Top 20 Predicted Players for GW{next_gw} ---")
    print(final_predictions_df.head(50))

    print("\n--- Players Receiving Defensive Bonus ---")
    defensive_bonus_players = final_predictions_df[final_predictions_df['defensive_bonus'] > 0]
    if defensive_bonus_players.empty:
        print("No players met the threshold for a defensive bonus this gameweek.")
    else:
        print(defensive_bonus_players)

    
    print("--- Displaying Top Players by Position ---") 

    # Filter for Forwards and get the top 10
    forwards_df = final_predictions_df[final_predictions_df['position'] == 'Forward'].head(10)

    # Filter for Midfielders and get the top 10
    midfielders_df = final_predictions_df[final_predictions_df['position'] == 'Midfielder'].head(10)

    # Filter for Defenders and get the top 10
    defenders_df = final_predictions_df[final_predictions_df['position'] == 'Defender'].head(10)

    # Filter for Goalkeepers and get the top 5
    goalkeepers_df = final_predictions_df[final_predictions_df['position'] == 'Goalkeeper'].head(5)


    # --- Print the Results ---
    print("\n" + "="*40)
    print("--- Top 10 Predicted Forwards ---")
    print("="*40)
    print(forwards_df)

    print("\n" + "="*40)
    print("--- Top 10 Predicted Midfielders ---")
    print("="*40)
    print(midfielders_df)

    print("\n" + "="*40)
    print("--- Top 10 Predicted Defenders ---")
    print("="*40)
    print(defenders_df)

    print("\n" + "="*40)
    print("--- Top 5 Predicted Goalkeepers ---")
    print("="*40)
    print(goalkeepers_df)