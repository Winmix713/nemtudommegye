import json
from ast import literal_eval

# Define the team names and their corresponding IDs
team_ids = {
    "Aston Oroszlán": 1,
    "Brentford": 2,
    "Brighton": 3,
    "Chelsea": 4,
    "Crystal Palace": 5,
    "Everton": 6,
    "Fulham": 7,
    "London Ágyúk": 8,
    "Liverpool": 9,
    "Manchester Kék": 10,
    "Newcastle": 11,
    "Nottingham": 12,
    "Tottenham": 13,
    "Vörös Ördögök": 14,
    "West Ham": 15,
    "Wolverhampton": 16
}

# Read the match pairings from the text file with error handling
input_file_path = r'D:\2024.10.10-ASZTALMENTÉS!!!!\pyhton_gyakorlas\chatgpt\upcoming_round_matches.txt'
try:
    with open(input_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        # Use literal_eval for security instead of eval
        matches = literal_eval(content.split('=')[1].strip())
except FileNotFoundError:
    print(f"Error: The file '{input_file_path}' was not found.")
    matches = []
except (SyntaxError, ValueError) as e:
    print(f"Error: Failed to parse the file '{input_file_path}'. Reason: {e}")
    matches = []

# Load team data from JSON
team_data_path = r'D:\2024.10.10-ASZTALMENTÉS!!!!\pyhton_gyakorlas\chatgpt\vsport_teamdata.json'
try:
    with open(team_data_path, 'r', encoding='utf-8') as json_file:
        team_data = json.load(json_file)
except FileNotFoundError:
    print(f"Error: The file '{team_data_path}' was not found.")
    team_data = {"teams": []}

# Create a dictionary for quick access to team data
team_info = {team['team_name']: team for team in team_data.get('teams', [])}

# Process the matches and create a list of dictionaries
match_list = []
pluszpont_content = set()

for index, (home_team, away_team) in enumerate(matches, start=1):
    # Check if the teams are valid and exist in the team_ids dictionary
    if home_team not in team_ids:
        print(f"Error: Home team '{home_team}' not found in team list. Skipping match.")
        continue
    if away_team not in team_ids:
        print(f"Error: Away team '{away_team}' not found in team list. Skipping match.")
        continue

    # Create a dictionary for the match information
    match_info = {
        "match_number": index,
        "home_team": home_team,
        "away_team": away_team,
        "home_team_id": team_ids[home_team],
        "away_team_id": team_ids[away_team]
    }
    match_list.append(match_info)

    # Check for top opponents
    if home_team in team_info:
        top_opponents = [opponent['opponent_name'] for opponent in team_info[home_team].get('top_opponents', [])]
        if away_team in top_opponents:
            match_str = f"{home_team} - {away_team} : + 5 %"
            reverse_match_str = f"{away_team} - {home_team} : + 5 %"
            if reverse_match_str not in pluszpont_content:
                pluszpont_content.add(match_str)

    if away_team in team_info:
        top_opponents = [opponent['opponent_name'] for opponent in team_info[away_team].get('top_opponents', [])]
        if home_team in top_opponents:
            match_str = f"{away_team} - {home_team} : + 5 %"
            reverse_match_str = f"{home_team} - {away_team} : + 5 %"
            if reverse_match_str not in pluszpont_content:
                pluszpont_content.add(match_str)

# Save the list to a JSON file with error handling
output_file_path = r'D:\2024.10.10-ASZTALMENTÉS!!!!\pyhton_gyakorlas\chatgpt\upcoming_matches.json'
try:
    with open(output_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(match_list, json_file, ensure_ascii=False, indent=4)
    print(f"Match data has been saved to '{output_file_path}'")
except IOError as e:
    print(f"Error writing to JSON file: {e}")

# Save the pluszpont content to a text file
pluszpont_file_path = r'D:\2024.10.10-ASZTALMENTÉS!!!!\pyhton_gyakorlas\chatgpt\pluszpont.txt'
try:
    with open(pluszpont_file_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write("\n".join(pluszpont_content))
    print(f"Pluszpont data has been saved to '{pluszpont_file_path}'")
except IOError as e:
    print(f"Error writing to text file: {e}")