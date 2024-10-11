import json
from collections import defaultdict

# Load the JSON data from the file with error handling
try:
    with open('C:\\Users\\takos\\OneDrive\\Desktop\\winmix.hu\\data\\prediction\\formatted_results.json', 'r', encoding='utf-8') as file:
        matches = json.load(file)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading JSON data: {e}")
    matches = []

# Initialize data structures to store statistics
both_teams_score_stats = defaultdict(lambda: defaultdict(lambda: {"matches": 0, "both_score": 0}))

# Process each match to update statistics
for match in matches:
    home_id = match.get("Hazai csapat ID")
    away_id = match.get("Vendég Csapat ID")
    both_teams_scored = match.get("Mindkét csapat szerzett gólt?") == "Igen"

    # Ensure valid team IDs are present
    if home_id is None or away_id is None:
        print(f"Invalid team data in match: {match}")
        continue

    # Update match count only once per match (home_id -> away_id)
    both_teams_score_stats[home_id][away_id]["matches"] += 1

    # Update both teams score count
    if both_teams_scored:
        both_teams_score_stats[home_id][away_id]["both_score"] += 1

# Write the results to a text file with error handling
text_file_path = 'C:\\Users\\takos\\OneDrive\\Desktop\\winmix.hu\\data\\both_teams_score_stats.txt'
try:
    with open(text_file_path, 'w', encoding='utf-8') as textfile:
        for team_id in sorted(both_teams_score_stats.keys()):
            if team_id < 1:
                continue
            textfile.write(f"Team ID {team_id}:\n")
            for opponent_id in sorted(both_teams_score_stats[team_id].keys()):
                matches = both_teams_score_stats[team_id][opponent_id]["matches"]
                both_score = both_teams_score_stats[team_id][opponent_id]["both_score"]
                percentage = (both_score / matches) * 100 if matches > 0 else 0
                textfile.write(f"  Opponent ID {opponent_id}: {both_score}/{matches} - {percentage:.2f}%\n")
    print(f"Both teams score statistics have been saved to {text_file_path}")
except IOError as e:
    print(f"Error writing to file: {e}")