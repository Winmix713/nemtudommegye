import json
import csv
import os
from collections import defaultdict

# Load both teams score stats from text file
def load_both_teams_score_stats(file_path):
    both_teams_score_stats = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 6:
                    home_id = int(parts[2])
                    away_id = int(parts[4])
                    both_score = int(parts[5].split('/')[0])
                    total_matches = int(parts[5].split('/')[1])
                    both_teams_score_stats[(home_id, away_id)] = {
                        "both_score": both_score,
                        "total_matches": total_matches
                    }
            print(f"Successfully loaded both teams score statistics for {len(both_teams_score_stats)} matches.")
        return both_teams_score_stats
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return {}

# Load upcoming matches from JSON file
def load_upcoming_matches(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            matches = json.load(f)
            print(f"Successfully loaded {len(matches)} upcoming matches.")
            return matches
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from {file_path}.")
        return []

# Load team statistics from CSV file
def load_team_statistics(file_path):
    team_stats = defaultdict(lambda: {
        "OMSZ": 0,  # Total number of matches
        "MCSGM": 0  # Matches where both teams scored
    })
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                team_id = int(row['TID'])
                team_stats[team_id]["wins"] = int(row['TotalWins'])
                team_stats[team_id]["losses"] = int(row['TotalLosses'])
                team_stats[team_id]["elo"] = float(row['ELO'])
            print(f"Successfully loaded statistics for {len(team_stats)} teams.")
        return team_stats
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return {}
    except csv.Error as e:
        print(f"Error: Failed to read CSV from {file_path}: {e}")
        return {}

# Process past matches to update team statistics
def process_past_matches(past_matches, team_stats):
    for match in past_matches:
        home_id = match["Hazai csapat ID"]
        away_id = match["Vendég Csapat ID"]
        home_goals = match["Hazai csapat gólszám"]
        away_goals = match["Vendég Csapat gólszám"]
        # Update total match count
        team_stats[home_id]["OMSZ"] += 1
        team_stats[away_id]["OMSZ"] += 1
        # Check if both teams scored
        if home_goals > 0 and away_goals > 0:
            team_stats[home_id]["MCSGM"] += 1
            team_stats[away_id]["MCSGM"] += 1
    # Calculate Esély for each team
    for team_id, stats in team_stats.items():
        if stats["OMSZ"] > 0:
            stats["Esély"] = (stats["MCSGM"] / stats["OMSZ"]) * 100
        else:
            stats["Esély"] = 0

# Function to calculate predictions based on combined stats
def calculate_predictions(matches, team_stats, both_teams_score_stats):
    predictions = []
    for match in matches:
        home_team_id = match["home_team_id"]
        away_team_id = match["away_team_id"]
        # Calculate combined Esély (probability)
        home_esély = team_stats[home_team_id]["Esély"]
        away_esély = team_stats[away_team_id]["Esély"]
        combined_esély = (home_esély + away_esély) / 2
        # Get both teams score stats
        both_teams_to_score = 0.0
        if (home_team_id, away_team_id) in both_teams_score_stats:
            stats = both_teams_score_stats[(home_team_id, away_team_id)]
            both_teams_to_score = stats["both_score"] / stats["total_matches"] * 100
        # Final combined probability
        final_probability = (combined_esély + both_teams_to_score) / 2
        predictions.append({
            "match": f"{match['home_team']} vs {match['away_team']}",
            "percentage": final_probability
        })
    print(f"Calculated predictions for {len(predictions)} matches.")
    return predictions

# Save predictions to a text file
def save_predictions(predictions, file_path):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            for i, prediction in enumerate(predictions):
                if i < 3:
                    f.write(f"Top {i+1}: {prediction['match']} - {prediction['percentage']:.2f}%\n")
                else:
                    f.write(f"{prediction['match']} - {prediction['percentage']:.2f}%\n")
        print(f"Predictions saved to {file_path}")
    except IOError as e:
        print(f"Error: Could not save predictions to {file_path}. Reason: {e}")

# Main function
def main():
    # Define file paths
    upcoming_matches_path = "D:\\2024.10.10-ASZTALMENTÉS!!!!\\pyhton_gyakorlas\\upcoming_matches.json"
    team_statistics_path = "D:\\2024.10.10-ASZTALMENTÉS!!!!\\pyhton_gyakorlas\\team_statistics.csv"
    both_teams_score_stats_path = "D:\\2024.10.10-ASZTALMENTÉS!!!!\\pyhton_gyakorlas\\both_teams_score_stats.txt"
    formatted_results_path = "D:\\2024.10.10-ASZTALMENTÉS!!!!\\pyhton_gyakorlas\\formatted_results.json"
    predictions_output_base_path = "D:\\2024.10.10-ASZTALMENTÉS!!!!\\pyhton_gyakorlas\\"
    predictions_output_file = "prediction1.txt"

    # Load data
    upcoming_matches = load_upcoming_matches(upcoming_matches_path)
    if not upcoming_matches:
        print("No upcoming matches found. Exiting.")
        return

    team_stats = load_team_statistics(team_statistics_path)
    if not team_stats:
        print("No team statistics found. Exiting.")
        return

    both_teams_score_stats = load_both_teams_score_stats(both_teams_score_stats_path)
    if not both_teams_score_stats:
        print("No both teams score stats found. Exiting.")
        return

    # Load past match data
    try:
        with open(formatted_results_path, 'r', encoding='utf-8') as f:
            past_matches = json.load(f)
            print(f"Successfully loaded {len(past_matches)} past matches.")
    except FileNotFoundError:
        print(f"Error: {formatted_results_path} not found.")
        return

    # Process past matches to update team statistics
    process_past_matches(past_matches, team_stats)

    # Calculate predictions
    predictions = calculate_predictions(upcoming_matches, team_stats, both_teams_score_stats)

    # Save predictions to file
    output_file = os.path.join(predictions_output_base_path, predictions_output_file)
    save_predictions(predictions, output_file)

if __name__ == "__main__":
    main()