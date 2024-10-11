import json
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
past_matches = load_file('D:\\2024.10.10-ASZTALMENTÉS!!!!\\pyhton_gyakorlas\\chatgpt\\formatted_results.json', [])

# Define the team names and their corresponding IDs
team_names = {
    1: "Aston Oroszlán",
    2: "Brentford",
    3: "Brighton",
    4: "Chelsea",
    5: "Crystal Palace",
    6: "Everton",
    7: "Fulham",
    8: "London Ágyúk",
    9: "Liverpool",
    10: "Manchester Kék",
    11: "Newcastle",
    12: "Nottingham",
    13: "Tottenham",
    14: "Vörös Ördögök",
    15: "West Ham",
    16: "Wolverhampton"
}

# Initialize team statistics
team_stats = defaultdict(lambda: {
    "OMSZ": 0,  # Total number of matches
    "MCSGM": 0,  # Matches where both teams scored
    "Esély": 0,   # Probability
    "Ellenfelek": defaultdict(int)  # Opponents match count
})

# Process each past match to update statistics
for match in past_matches:
    try:
        home_id = int(match["Hazai csapat ID"])
        away_id = int(match["Vendég Csapat ID"])
        home_goals = int(match["Hazai csapat gólszám"])
        away_goals = int(match["Vendég Csapat gólszám"])
        
        # Update match statistics
        team_stats[home_id]["OMSZ"] += 1
        team_stats[away_id]["OMSZ"] += 1
        
        team_stats[home_id]["Ellenfelek"][away_id] += 1
        team_stats[away_id]["Ellenfelek"][home_id] += 1
        
        if home_goals > 0 and away_goals > 0:
            team_stats[home_id]["MCSGM"] += 1
            team_stats[away_id]["MCSGM"] += 1
    except (KeyError, ValueError) as e:
        print(f"Warning: Invalid match data {match}. Reason: {e}")

# Calculate Esély for each team
for team_id, stats in team_stats.items():
    stats["Esély"] = (stats["MCSGM"] / stats["OMSZ"]) * 100 if stats["OMSZ"] > 0 else 0

# Sort opponents for each team by match count
for team_id, stats in team_stats.items():
    sorted_ellenfelek = sorted(stats["Ellenfelek"].items(), key=lambda x: x[1], reverse=True)
    team_stats[team_id]["Top 3 Ellenfelek"] = sorted_ellenfelek[:3]

# Write the results to individual files for each team
output_folder = Path('D:/2024.10.10-ASZTALMENTÉS!!!!/pyhton_gyakorlas/chatgpt/')
output_folder.mkdir(parents=True, exist_ok=True)

for team_id, stats in team_stats.items():
    try:
        file_name = output_folder / f'atlag_mindket_{team_id}.txt'
        
        with open(file_name, 'w', encoding='utf-8') as file:
            # Writing the probability
            file.write(f"{team_names[team_id]} - Esély: {stats['Esély']:.2f}%\n")
            
            # Writing the top 3 opponents
            file.write("Top 3 opponents for exciting matches:\n")
            for opp_id, matches in stats["Top 3 Ellenfelek"]:
                file.write(f"{team_names[opp_id]} - {matches} mérkőzés\n")
        
        print(f"Results saved to {file_name}")
    except IOError as e:
        print(f"Error: Could not save file for team {team_id}. Reason: {e}")