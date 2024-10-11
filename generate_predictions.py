import json
import re
import os
from collections import defaultdict
from pathlib import Path

# Error-handled file loading
def load_file(file_path, default_value):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read() if file_path.endswith('.txt') else json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error: Unable to load {file_path}. Reason: {e}")
        return default_value

# Load files with error handling
both_teams_score_stats = load_file('D:\\2024.10.10-ASZTALMENTÉS!!!!\\pyhton_gyakorlas\\chatgpt\\both_teams_score_stats.txt', "")
upcoming_matches = load_file('D:\\2024.10.10-ASZTALMENTÉS!!!!\\pyhton_gyakorlas\\chatgpt\\upcoming_matches.json', [])
past_matches = load_file('D:\\2024.10.10-ASZTALMENTÉS!!!!\\pyhton_gyakorlas\\chatgpt\\formatted_results.json', [])

# Initialize team statistics
team_stats = defaultdict(lambda: {
    "OMSZ": 0,  # Total number of matches
    "MCSGM": 0,  # Matches where both teams scored
    "Esély": 0   # Probability
})

# Process each past match to update statistics
for match in past_matches:
    try:
        home_id = int(match["Hazai csapat ID"])
        away_id = int(match["Vendég Csapat ID"])
        home_goals = int(match["Hazai csapat gólszám"])
        away_goals = int(match["Vendég Csapat gólszám"])
        team_stats[home_id]["OMSZ"] += 1
        team_stats[away_id]["OMSZ"] += 1
        if home_goals > 0 and away_goals > 0:
            team_stats[home_id]["MCSGM"] += 1
            team_stats[away_id]["MCSGM"] += 1
    except (KeyError, ValueError) as e:
        print(f"Warning: Invalid match data {match}. Reason: {e}")

# Calculate Esély for each team
for team_id, stats in team_stats.items():
    stats["Esély"] = (stats["MCSGM"] / stats["OMSZ"]) * 100 if stats["OMSZ"] > 0 else 0

# Extract percentage from both teams score stats
def extract_percentage_from_stats(home_team_id, away_team_id):
    try:
        pattern = rf"Team ID {home_team_id}:\n.*?Opponent ID {away_team_id}: (\d+)/(\d+) - (\d+\.\d+)%"
        match = re.search(pattern, both_teams_score_stats, re.DOTALL)
        if match:
            both_score = int(match.group(1))
            total_matches = int(match.group(2))
            return both_score / total_matches * 100
    except (ValueError, AttributeError) as e:
        print(f"Error extracting stats for {home_team_id} vs {away_team_id}. Reason: {e}")
    return 0

# Calculate predictions
predictions = []
for match in upcoming_matches:
    try:
        home_team_id = int(match["home_team_id"])
        away_team_id = int(match["away_team_id"])
        combined_esély = (team_stats[home_team_id]["Esély"] + team_stats[away_team_id]["Esély"]) / 2
        both_teams_to_score = extract_percentage_from_stats(home_team_id, away_team_id)
        final_probability = (combined_esély + both_teams_to_score) / 2
        predictions.append({
            "match": f"{match['home_team']} vs {match['away_team']}",
            "percentage": final_probability,
            "home_team_id": home_team_id,
            "away_team_id": away_team_id
        })
    except KeyError as e:
        print(f"Warning: Missing data for match {match}. Reason: {e}")

# Apply penalty deductions for specific teams
penalty_teams = {9: 5, 10: 9, 14: 4}  # team_id: penalty_percentage
penalty_applied = []

for prediction in predictions:
    penalty_applied_flag = False
    if prediction["home_team_id"] in penalty_teams:
        penalty = penalty_teams[prediction["home_team_id"]]
        prediction["percentage"] -= penalty
        penalty_applied.append((prediction["match"], penalty))
        penalty_applied_flag = True
    if prediction["away_team_id"] in penalty_teams:
        penalty = penalty_teams[prediction["away_team_id"]]
        prediction["percentage"] -= penalty
        penalty_applied.append((prediction["match"], penalty))
        penalty_applied_flag = True
    if penalty_applied_flag:
        prediction["penalty_applied"] = True

# Sort predictions again after applying penalties
predictions.sort(key=lambda x: x["percentage"], reverse=True)

# Write predictions to file
base_path = Path('D:/2024.10.10-ASZTALMENTÉS!!!!/pyhton_gyakorlas/chatgpt/')
output_file = base_path / 'prediction1.txt'
file_index = 1
while output_file.exists():
    file_index += 1
    output_file = base_path / f'prediction{file_index}.txt'

try:
    with open(output_file, 'w', encoding='utf-8') as file:
        for i, prediction in enumerate(predictions):
            penalty_marker = '*' if prediction.get("penalty_applied") else ''
            if i < 3:
                file.write(f"Top {i+1}: {prediction['match']} - {prediction['percentage']:.2f}%{penalty_marker}\n")
            else:
                file.write(f"{prediction['match']} - {prediction['percentage']:.2f}%{penalty_marker}\n")
        
        if penalty_applied:
            file.write("\n*Büntetésből levont érték:\n")
            for match, penalty in penalty_applied:
                file.write(f"{match} - {penalty} %\n")
                
    print(f"Predictions have been saved to {output_file}")
except IOError as e:
    print(f"Error: Could not save predictions to {output_file}. Reason: {e}")