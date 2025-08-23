import requests
import pandas as pd
import os
from dotenv import load_dotenv

import pulp

def run():

    print("--- Suggesting Transfers for your team---")

    # --- Load Secrets from .env file ---
    load_dotenv()

    TEAM_ID = os.getenv("FPL_TEAM_ID")
    fpl_cookie = os.getenv("FPL_COOKIE")
    auth_token = os.getenv("FPL_AUTH_TOKEN")
    user_agent = os.getenv("FPL_USER_AGENT")

    # --- Authentication ---
    headers = {
        "Cookie": fpl_cookie,
        "User-Agent": user_agent,
        "X-Api-Authorization": auth_token
    }

    # --- Fetch Your FPL Team Data ---
    url = f"https://fantasy.premierleague.com/api/my-team/{TEAM_ID}/"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        my_team_data = response.json()
        
        my_player_ids = [player['element'] for player in my_team_data['picks']]
        free_transfers = my_team_data['transfers']['limit']
        bank = my_team_data['transfers']['bank'] / 10.0
        
        print("✅ Successfully fetched your FPL team data!")
        print(f"   Free Transfers Available: {free_transfers}")
        print(f"   Money in the Bank: £{bank}m")

    else:
        print(f"❌ Error: Could not fetch your team. Status code: {response.status_code}")
        print("   Check that your .env file is in the root directory and the variable names are correct.")

    # --- Load Predictions and Master Player List ---

    # Load the predictions you saved from the other notebook
    predictions_df = pd.read_csv('../../data/gw2_predictions.csv')

    # We also need a master list of all players with their current price, position, and team ID
    # We can build this from the source files we've used before
    SEASON_CURRENT = "2025-2026"
    players_url = f'https://raw.githubusercontent.com/olbauday/FPL-Elo-Insights/main/data/{SEASON_CURRENT}/players.csv'
    teams_url = f'https://raw.githubusercontent.com/olbauday/FPL-Elo-Insights/main/data/{SEASON_CURRENT}/teams.csv'
    player_stats_url = f'https://raw.githubusercontent.com/olbauday/FPL-Elo-Insights/main/data/{SEASON_CURRENT}/playerstats.csv'

    players_df = pd.read_csv(players_url)
    teams_df = pd.read_csv(teams_url)
    player_stats_df = pd.read_csv(player_stats_url)

    # Get the latest stats for each player
    latest_stats_df = player_stats_df.sort_values('gw', ascending=False).drop_duplicates('id', keep='first')

    # Create the master player list
    master_player_list = pd.merge(
        latest_stats_df[['id', 'now_cost']],
        players_df[['player_id', 'position', 'team_code']],
        left_on='id',
        right_on='player_id'
    )
    master_player_list = pd.merge(
        master_player_list,
        teams_df[['code', 'id']],
        left_on='team_code',
        right_on='code'
    )
    master_player_list.rename(columns={'id_y': 'team_id'}, inplace=True)

    # Finally, merge the master list with our predictions
    all_players_with_xp = pd.merge(
        master_player_list[['player_id', 'now_cost', 'position', 'team_id']],
        predictions_df[['player_id', 'web_name', 'xP_adjusted']],
        on='player_id'
    )

    print("Successfully created a master list of all players with their predicted points (xP).")
    all_players_with_xp.head()

    # --- Step 1: User Settings & Custom Constraints ---
    palmer_id = all_players_with_xp[all_players_with_xp['web_name'] == 'Palmer'].index[0]
    wirtz_id = all_players_with_xp[all_players_with_xp['web_name'] == 'Wirtz'].index[0]
    joaopedro_id = all_players_with_xp[all_players_with_xp['web_name'] == 'João Pedro'].index[0]

    USER_CONSTRAINTS = {
        "players_to_keep": [palmer_id, wirtz_id, joaopedro_id],
        "players_to_sell": [],
        "players_to_consider": []
    }

    gameweeks_url = 'https://raw.githubusercontent.com/olbauday/FPL-Elo-Insights/main/data/2025-2026/gameweek_summaries.csv'
    gameweeks_df = pd.read_csv(gameweeks_url)
    next_gw = gameweeks_df[gameweeks_df['is_next'] == True].iloc[0]['id']

    # --- Step 2: Set Up the Optimization Problem ---
    prob = pulp.LpProblem("FPL_Optimizer_Advanced", pulp.LpMaximize)

    all_players_with_xp.reset_index(inplace=True, drop=False)
    all_players_with_xp.set_index('player_id', inplace=True)

    players = all_players_with_xp.to_dict('index')
    player_ids = list(players.keys())

    # --- Step 3: Define the Decision Variables ---
    in_squad = pulp.LpVariable.dicts("in_squad", player_ids, cat='Binary')
    is_starting = pulp.LpVariable.dicts("is_starting", player_ids, cat='Binary')
    is_captain = pulp.LpVariable.dicts("is_captain", player_ids, cat='Binary')
    is_vice_captain = pulp.LpVariable.dicts("is_vice_captain", player_ids, cat='Binary')
    players_sold = pulp.LpVariable.dicts("players_sold", my_player_ids, cat='Binary')
    players_bought = pulp.LpVariable.dicts("players_bought", player_ids, cat='Binary')

    # --- Step 4: Define the Objective Function ---
    starting_xi_xp = pulp.lpSum(players[i]['xP_adjusted'] * is_starting[i] for i in player_ids)
    captain_xp = pulp.lpSum(players[i]['xP_adjusted'] * is_captain[i] for i in player_ids)
    transfer_hits = (pulp.lpSum(players_bought) - free_transfers) * 4
    prob += starting_xi_xp + captain_xp - transfer_hits, "Total Score"

    # --- Step 5: Add FPL Constraints ---
    # (All constraints remain the same)
    total_squad_value = sum(p['now_cost'] for p_id, p in players.items() if p_id in my_player_ids)
    total_money = total_squad_value + bank
    prob += pulp.lpSum(players[i]['now_cost'] * in_squad[i] for i in player_ids) <= total_money, "Budget"
    prob += pulp.lpSum(in_squad[i] for i in player_ids) == 15, "Squad Size"

    prob += pulp.lpSum(in_squad[i] for i in player_ids if players[i]['position'] == 'Goalkeeper') == 2
    prob += pulp.lpSum(in_squad[i] for i in player_ids if players[i]['position'] == 'Defender') == 5
    prob += pulp.lpSum(in_squad[i] for i in player_ids if players[i]['position'] == 'Midfielder') == 5
    prob += pulp.lpSum(in_squad[i] for i in player_ids if players[i]['position'] == 'Forward') == 3

    team_ids = all_players_with_xp['team_id'].unique()
    for team_id in team_ids:
        prob += pulp.lpSum(in_squad[i] for i in player_ids if players[i]['team_id'] == team_id) <= 3, f"Team_{team_id}_Limit"

    for i in player_ids:
        is_in_old_squad = 1 if i in my_player_ids else 0
        if is_in_old_squad:
            prob += in_squad[i] == is_in_old_squad - players_sold[i] + players_bought[i]
        else:
            prob += in_squad[i] == players_bought[i]

    prob += pulp.lpSum(is_starting[i] for i in player_ids) == 11, "Starting XI Size"
    prob += pulp.lpSum(is_captain[i] for i in player_ids) == 1, "Captain Count"
    prob += pulp.lpSum(is_vice_captain[i] for i in player_ids) == 1, "Vice Captain Count"

    for i in player_ids:
        prob += is_starting[i] <= in_squad[i]
        prob += is_captain[i] <= is_starting[i]
        prob += is_vice_captain[i] <= is_starting[i]
        prob += is_captain[i] + is_vice_captain[i] <= 1

    prob += pulp.lpSum(is_starting[i] for i in player_ids if players[i]['position'] == 'Goalkeeper') == 1
    prob += pulp.lpSum(is_starting[i] for i in player_ids if players[i]['position'] == 'Defender') >= 3
    prob += pulp.lpSum(is_starting[i] for i in player_ids if players[i]['position'] == 'Midfielder') >= 2
    prob += pulp.lpSum(is_starting[i] for i in player_ids if players[i]['position'] == 'Forward') >= 1

    for player_id in USER_CONSTRAINTS["players_to_keep"]:
        if player_id in my_player_ids:
            prob += players_sold[player_id] == 0, f"Force_Keep_{player_id}"
    for player_id in USER_CONSTRAINTS["players_to_sell"]:
        if player_id in my_player_ids:
            prob += players_sold[player_id] == 1, f"Force_Sell_{player_id}"
    if USER_CONSTRAINTS["players_to_consider"]:
        prob += pulp.lpSum(players_bought[i] for i in USER_CONSTRAINTS["players_to_consider"]) >= 1, "Force_Consider"

    # --- Step 6: Solve and Display ---
    prob.solve()
    print(f"Solver Status: {pulp.LpStatus[prob.status]}")

    if pulp.LpStatus[prob.status] == 'Optimal':
        
        # *** NEW: Define output path and create directory ***
        output_dir = '../../suggested_transfers'
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f'gw{next_gw}_suggestions.txt')

        # Open the file to write the output
        with open(output_file, 'w') as f:
            # --- Calculate Old Team's Score ---
            old_team_score = 0
            old_team_starters = sorted(my_player_ids, key=lambda x: players[x]['xP_adjusted'], reverse=True)[:11]
            old_team_captain = old_team_starters[0]
            for pid in old_team_starters:
                old_team_score += players[pid]['xP_adjusted']
            old_team_score += players[old_team_captain]['xP_adjusted']
            
            # --- Get New Team's Score ---
            new_team_score = prob.objective.value()
            points_gain = new_team_score - old_team_score
            
            # --- Write Summary to file ---
            f.write("="*40 + "\n")
            f.write("--- Points Gain Summary ---\n")
            f.write("="*40 + "\n")
            f.write(f"Predicted score for CURRENT team: {old_team_score:.2f}\n")
            f.write(f"Predicted score for NEW team (after hits): {new_team_score:.2f}\n")
            f.write(f"Predicted points GAIN from transfers: {points_gain:+.2f}\n")
            f.write("="*40 + "\n\n")

            # --- Write Transfer Suggestions to file ---
            players_to_sell = [p_id for p_id in my_player_ids if players_sold[p_id].varValue == 1]
            players_to_buy = [p_id for p_id in player_ids if players_bought[p_id].varValue == 1]
            
            f.write("--- Optimal Transfer Suggestions ---\n")
            if not players_to_sell and not players_to_buy:
                f.write("Suggestion: Make no transfers.\n")
            else:
                for pid in players_to_sell: f.write(f"  🔴 SELL: {players[pid]['web_name']}\n")
                for pid in players_to_buy: f.write(f"  🟢 BUY:  {players[pid]['web_name']}\n")

            # --- Write Final Squad to file ---
            f.write("\n--- Optimal Team for Next Gameweek ---\n")
            starting_xi_ids = [i for i in player_ids if is_starting[i].varValue == 1]
            captain_id = [i for i in player_ids if is_captain[i].varValue == 1][0]
            vice_captain_id = [i for i in player_ids if is_vice_captain[i].varValue == 1][0]
            
            squad_df = all_players_with_xp.loc[[i for i in player_ids if in_squad[i].varValue == 1]]
            squad_df['Status'] = 'Sub'
            squad_df.loc[starting_xi_ids, 'Status'] = 'STARTER'
            squad_df.loc[captain_id, 'Status'] = 'CAPTAIN'
            squad_df.loc[vice_captain_id, 'Status'] = 'VICE'
            squad_df.loc[captain_id, 'xP_adjusted'] *= 2
            
            f.write(squad_df[['web_name', 'position', 'now_cost', 'xP_adjusted', 'Status']].sort_values('Status', ascending=False).to_string())

        print(f"✅ Suggestions successfully saved to '{output_file}'")

    else:
        print("Could not find an optimal solution.")

