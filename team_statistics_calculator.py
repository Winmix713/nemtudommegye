import json
import csv
from collections import defaultdict

# Define the team names and their corresponding IDs
team_names = [
    "Aston Oroszlán", "Brentford", "Brighton", "Chelsea", "Crystal Palace",
    "Everton", "Fulham", "London Ágyúk", "Liverpool", "Manchester Kék",
    "Newcastle", "Nottingham", "Tottenham", "Vörös Ördögök", "West Ham", "Wolverhampton"
]

# Create a mapping from team IDs to names
team_id_map = {idx + 1: name for idx, name in enumerate(team_names)}

# Load the JSON data from the file
try:
    with open('C:\\Users\\takos\\OneDrive\\Desktop\\winmix.hu\\data\\formatted_results.json', 'r', encoding='utf-8') as file:
        matches = json.load(file)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading JSON data: {e}")
    matches = []

# Initialize data structures to store statistics
team_stats = defaultdict(lambda: {
    "OMSZ": 0,  # Total number of matches
    "MCSGM": 0,  # Matches where both teams scored
    "GMCMGY": 0,  # Wins in matches where both teams scored
    "GMCMDS": 0,  # Draws in matches where both teams scored
    "GMCMVS": 0,  # Losses in matches where both teams scored
    "GMCMRG": 0,  # Goals scored in matches where both teams scored
    "GMCMKG": 0,  # Goals conceded in matches where both teams scored
    "TotalWins": 0,  # Total wins in all matches
    "TotalLosses": 0,  # Total losses in all matches
    "ELO": 1500,  # Initial ELO Rating
    "SRS": 0,    # Simple Ranking System
    "PR": 0,     # Power Ranking
    "GR": 1500,  # Initial Glicko Rating
    "GPI": 0     # Goal-Based Performance Index
})

# Process each match to update team statistics
for match in matches:
    home_id = match["Hazai csapat ID"]
    away_id = match["Vendég Csapat ID"]
    home_goals = match["Hazai csapat gólszám"]
    away_goals = match["Vendég Csapat gólszám"]

    # Update total match count
    team_stats[home_id]["OMSZ"] += 1
    team_stats[away_id]["OMSZ"] += 1

    # Update total goals scored
    team_stats[home_id]["GMCMRG"] += home_goals
    team_stats[away_id]["GMCMRG"] += away_goals

    # Update total wins and losses
    if home_goals > away_goals:
        team_stats[home_id]["TotalWins"] += 1
        team_stats[away_id]["TotalLosses"] += 1
    elif home_goals < away_goals:
        team_stats[away_id]["TotalWins"] += 1
        team_stats[home_id]["TotalLosses"] += 1

    # Check if both teams scored
    if home_goals > 0 and away_goals > 0:
        team_stats[home_id]["MCSGM"] += 1
        team_stats[away_id]["MCSGM"] += 1

        # Update goals in matches where both teams scored
        team_stats[home_id]["GMCMRG"] += home_goals
        team_stats[home_id]["GMCMKG"] += away_goals
        team_stats[away_id]["GMCMRG"] += away_goals
        team_stats[away_id]["GMCMKG"] += home_goals

        # Update win/draw/loss in matches where both teams scored
        if home_goals > away_goals:
            team_stats[home_id]["GMCMGY"] += 1
            team_stats[away_id]["GMCMVS"] += 1
        elif home_goals < away_goals:
            team_stats[away_id]["GMCMGY"] += 1
            team_stats[home_id]["GMCMVS"] += 1
        else:
            team_stats[home_id]["GMCMDS"] += 1
            team_stats[away_id]["GMCMDS"] += 1

# Calculate additional statistics
for team_id, stats in team_stats.items():
    stats["GMCMGKE"] = stats["GMCMRG"] - stats["GMCMKG"]  # Goal difference in matches where both teams scored

    # Calculate SRS (Simple Ranking System)
    if stats["OMSZ"] > 0:
        stats["SRS"] = (stats["GMCMRG"] - stats["GMCMKG"]) / stats["OMSZ"]

    # Calculate PR (Power Ranking) - Placeholder for actual calculation
    stats["PR"] = stats["ELO"]  # This is a placeholder; implement actual PR logic

    # Calculate GR (Glicko Rating) - Placeholder for actual calculation
    stats["GR"] = stats["ELO"]  # This is a placeholder; implement actual GR logic

    # Calculate GPI (Goal-Based Performance Index)
    if stats["OMSZ"] > 0:
        stats["GPI"] = (stats["GMCMRG"] - stats["GMCMKG"]) / stats["OMSZ"]

# Sort teams by total wins and total losses
sorted_teams = sorted(
    team_stats.items(),
    key=lambda x: (x[1]["TotalWins"], -x[1]["TotalLosses"]),
    reverse=True
)

# Write the statistics to a CSV file
csv_file_path = 'C:\\Users\\takos\\OneDrive\\Desktop\\winmix.hu\\data\\team_statistics.csv'
try:
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            "Rank", "TID", "CN", "OMSZ", "MCSGM", "GMCMGY", "GMCMDS", "GMCMVS",
            "GMCMRG", "GMCMKG", "GMCMGKE", "TotalWins", "TotalLosses", "ELO", "SRS", "PR", "GR", "GPI"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for rank, (team_id, stats) in enumerate(sorted_teams, start=1):
            row = {
                "Rank": rank,
                "TID": team_id,
                "CN": team_id_map[team_id],
                **stats
            }
            writer.writerow(row)
    print(f"Team statistics have been saved to {csv_file_path}")
except IOError as e:
    print(f"Error writing CSV file: {e}")