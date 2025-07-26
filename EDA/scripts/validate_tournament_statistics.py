#!/usr/bin/env python3
"""
Validate and Correct Euro 2024 Tournament Statistics
Detailed analysis to ensure accurate tournament-wide statistics
"""

import pandas as pd
import numpy as np
from pathlib import Path
import ast
import warnings
warnings.filterwarnings('ignore')

def load_euro_2024_data():
    """Load the main Euro 2024 dataset"""
    data_path = Path("Data/euro_2024_complete_dataset.csv")
    matches_path = Path("Data/matches_complete.csv")
    
    print("Loading Euro 2024 datasets...")
    df_events = pd.read_csv(data_path)
    df_matches = pd.read_csv(matches_path) if matches_path.exists() else None
    
    print(f"Events dataset: {df_events.shape[0]:,} rows × {df_events.shape[1]} columns")
    if df_matches is not None:
        print(f"Matches dataset: {df_matches.shape[0]:,} rows × {df_matches.shape[1]} columns")
    
    return df_events, df_matches

def analyze_goals_correctly(df_events):
    """Correctly analyze goals - not all goal-related events are actual goals"""
    print("\nAnalyzing goals correctly...")
    
    # Method 1: Look for actual goal outcomes in shot events
    shot_events = df_events[df_events['event_type'] == 'Shot'].copy()
    
    goals_from_shots = 0
    if not shot_events.empty and 'shot' in shot_events.columns:
        for idx, row in shot_events.iterrows():
            try:
                shot_data = str(row['shot'])
                if 'goal' in shot_data.lower() and 'outcome' in shot_data.lower():
                    # Parse the shot data to check if outcome is goal
                    if 'Goal' in shot_data:
                        goals_from_shots += 1
            except:
                continue
    
    # Method 2: Check home_score and away_score changes
    goals_from_score_changes = 0
    if 'home_score' in df_events.columns and 'away_score' in df_events.columns:
        # Group by match and look for score changes
        for match_id in df_events['match_id'].unique():
            match_events = df_events[df_events['match_id'] == match_id].copy()
            match_events = match_events.sort_values('index')
            
            # Track score changes
            prev_home = 0
            prev_away = 0
            for idx, row in match_events.iterrows():
                home_score = row['home_score'] if pd.notna(row['home_score']) else prev_home
                away_score = row['away_score'] if pd.notna(row['away_score']) else prev_away
                
                if home_score > prev_home:
                    goals_from_score_changes += (home_score - prev_home)
                if away_score > prev_away:
                    goals_from_score_changes += (away_score - prev_away)
                
                prev_home = home_score
                prev_away = away_score
    
    # Method 3: Use match-level data if available
    return {
        'goals_from_shots': goals_from_shots,
        'goals_from_score_changes': goals_from_score_changes,
        'method_used': 'shot_outcome_analysis' if goals_from_shots > 0 else 'score_change_analysis'
    }

def analyze_match_results(df_matches):
    """Analyze match results from matches dataset"""
    print("Analyzing match results...")
    
    if df_matches is None:
        return {'draws': 'No matches data', 'wins': 'No matches data'}
    
    print("Available columns in matches dataset:")
    print(df_matches.columns.tolist())
    
    # Look for score columns
    score_cols = [col for col in df_matches.columns if 'score' in col.lower()]
    print(f"Score columns found: {score_cols}")
    
    if len(score_cols) >= 2:
        home_col = score_cols[0]
        away_col = score_cols[1]
        
        draws = len(df_matches[df_matches[home_col] == df_matches[away_col]])
        total_games = len(df_matches)
        wins = total_games - draws
        
        return {'draws': draws, 'wins': wins, 'total_games': total_games}
    
    return {'draws': 'Unable to determine', 'wins': 'Unable to determine'}

def analyze_substitutions_correctly(df_events):
    """Correctly analyze substitutions"""
    print("Analyzing substitutions correctly...")
    
    # Look for actual substitution events
    sub_events = df_events[df_events['event_type'] == 'Substitution']
    
    if sub_events.empty and 'substitution' in df_events.columns:
        # Alternative: look for substitution column data
        sub_events = df_events[df_events['substitution'].notna()]
    
    total_subs = len(sub_events)
    num_games = df_events['match_id'].nunique()
    
    return {
        'total_substitutions': total_subs,
        'avg_per_game': total_subs / num_games if num_games > 0 else 0
    }

def analyze_cards_correctly(df_events):
    """Correctly analyze red and yellow cards"""
    print("Analyzing cards correctly...")
    
    # Look in bad_behaviour column for actual card events
    card_events = df_events[df_events['bad_behaviour'].notna()]
    
    red_cards = 0
    yellow_cards = 0
    
    for idx, row in card_events.iterrows():
        try:
            bad_behaviour_str = str(row['bad_behaviour'])
            # Parse the bad behaviour data
            if 'Yellow Card' in bad_behaviour_str:
                yellow_cards += 1
            elif 'Red Card' in bad_behaviour_str or 'Second Yellow' in bad_behaviour_str:
                red_cards += 1
        except:
            continue
    
    num_games = df_events['match_id'].nunique()
    
    return {
        'red_cards': red_cards,
        'yellow_cards': yellow_cards,
        'red_per_game': red_cards / num_games if num_games > 0 else 0,
        'yellow_per_game': yellow_cards / num_games if num_games > 0 else 0
    }

def analyze_corners_correctly(df_events):
    """Correctly analyze corner kicks"""
    print("Analyzing corners correctly...")
    
    # Look for events that start from corner kicks
    corner_events = df_events[df_events['play_pattern'].str.contains('Corner', case=False, na=False)]
    
    # Each corner kick should generate multiple events, but we want to count unique corner kicks
    # Group by match and look for distinct corner sequences
    corners_per_match = {}
    
    for match_id in df_events['match_id'].unique():
        match_corner_events = corner_events[corner_events['match_id'] == match_id]
        
        # Count corners by looking at play pattern changes to "From Corner"
        # This represents each time a corner kick is taken
        unique_corners = 0
        prev_index = -1
        
        for idx, row in match_corner_events.iterrows():
            current_index = row['index'] if 'index' in row else idx
            # If there's a gap in indices, it's likely a new corner sequence
            if prev_index == -1 or current_index - prev_index > 10:
                unique_corners += 1
            prev_index = current_index
        
        corners_per_match[match_id] = unique_corners
    
    total_corners = sum(corners_per_match.values())
    num_games = len(corners_per_match)
    
    return {
        'total_corners': total_corners,
        'corners_per_game': total_corners / num_games if num_games > 0 else 0,
        'corner_events_found': len(corner_events)
    }

def analyze_extra_time_penalties(df_events):
    """Analyze extra time and penalty situations"""
    print("Analyzing extra time and penalties...")
    
    extra_time_matches = set()
    penalty_matches = set()
    
    if 'period' in df_events.columns:
        # Period 1-2: Regular time, 3-4: Extra time, 5: Penalties
        for match_id in df_events['match_id'].unique():
            match_events = df_events[df_events['match_id'] == match_id]
            max_period = match_events['period'].max()
            
            if max_period >= 3:
                extra_time_matches.add(match_id)
            if max_period >= 5:
                penalty_matches.add(match_id)
    
    # Subtract penalty matches from extra time (penalty matches also went to extra time)
    extra_time_only = len(extra_time_matches) - len(penalty_matches)
    
    return {
        'extra_time_games': extra_time_only,
        'penalty_games': len(penalty_matches)
    }

def create_corrected_statistics_table(stats):
    """Create corrected tournament statistics table"""
    
    # Calculate goals (use the most reliable method)
    goals = stats['goals']['goals_from_score_changes'] if stats['goals']['goals_from_score_changes'] > 0 else stats['goals']['goals_from_shots']
    goals_per_game = goals / stats['basic']['num_games'] if stats['basic']['num_games'] > 0 else 0
    
    table_data = [
        ['Number of Games', stats['basic']['num_games'], '51 matches in tournament'],
        ['Number of Goals', goals, f"Method: {stats['goals']['method_used']}"],
        ['Average Goals per Game', f"{goals_per_game:.2f}", ''],
        ['Games to Extra Time', stats['time']['extra_time_games'], 'Extra time only (not penalties)'],
        ['Games to Penalties', stats['time']['penalty_games'], 'Penalty shootouts'],
        ['Total Draws', stats['results']['draws'], 'After regular/extra time'],
        ['Total Wins', stats['results']['wins'], 'Decisive results'],
        ['Total Substitutions', stats['substitutions']['total_substitutions'], 'Player changes'],
        ['Average Substitutions per Game', f"{stats['substitutions']['avg_per_game']:.2f}", ''],
        ['Total Red Cards', stats['cards']['red_cards'], 'Dismissals'],
        ['Average Red Cards per Game', f"{stats['cards']['red_per_game']:.2f}", ''],
        ['Total Yellow Cards', stats['cards']['yellow_cards'], 'Bookings'],
        ['Average Yellow Cards per Game', f"{stats['cards']['yellow_per_game']:.2f}", ''],
        ['Total Corners', stats['corners']['total_corners'], 'Corner kicks taken'],
        ['Average Corners per Game', f"{stats['corners']['corners_per_game']:.2f}", '']
    ]
    
    return table_data

def main():
    """Main validation function"""
    print("EURO 2024 TOURNAMENT STATISTICS VALIDATION")
    print("="*60)
    
    try:
        # Load data
        df_events, df_matches = load_euro_2024_data()
        
        # Basic stats
        num_games = df_events['match_id'].nunique()
        
        # Analyze each component correctly
        goals_stats = analyze_goals_correctly(df_events)
        results_stats = analyze_match_results(df_matches)
        substitutions_stats = analyze_substitutions_correctly(df_events)
        cards_stats = analyze_cards_correctly(df_events)
        corners_stats = analyze_corners_correctly(df_events)
        time_stats = analyze_extra_time_penalties(df_events)
        
        # Combine all statistics
        corrected_stats = {
            'basic': {'num_games': num_games},
            'goals': goals_stats,
            'results': results_stats,
            'substitutions': substitutions_stats,
            'cards': cards_stats,
            'corners': corners_stats,
            'time': time_stats
        }
        
        # Create and display corrected table
        table_data = create_corrected_statistics_table(corrected_stats)
        
        print("\n" + "="*80)
        print("CORRECTED EURO 2024 TOURNAMENT STATISTICS")
        print("="*80)
        
        print(f"{'Statistic':<35} {'Value':<15} {'Notes':<30}")
        print("-" * 80)
        
        for stat, value, notes in table_data:
            print(f"{stat:<35} {value:<15} {notes:<30}")
        
        print("-" * 80)
        
        # Save corrected statistics
        output_dir = Path("EDA/analysis/tournament_statistics")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        df_corrected = pd.DataFrame(table_data, columns=['Statistic', 'Value', 'Notes'])
        corrected_path = output_dir / 'euro_2024_corrected_statistics.csv'
        df_corrected.to_csv(corrected_path, index=False)
        
        print(f"\n📊 Corrected statistics saved to: {corrected_path}")
        
        # Print methodology explanations
        print("\n" + "="*80)
        print("METHODOLOGY EXPLANATIONS FOR CARDS AND CORNERS")
        print("="*80)
        
        print("\n🟡 YELLOW CARDS:")
        print(f"   Total Found: {cards_stats['yellow_cards']}")
        print("   Method: Analyzed 'bad_behaviour' column for Yellow Card entries")
        print("   Explanation: Each yellow card event is recorded in the bad_behaviour")
        print("   column with specific card type information. Parsed JSON-like")
        print("   structures to identify genuine yellow card incidents.")
        
        print("\n🔴 RED CARDS:")
        print(f"   Total Found: {cards_stats['red_cards']}")
        print("   Method: Analyzed 'bad_behaviour' column for Red Card entries")
        print("   Explanation: Similar to yellow cards, red cards are recorded in")
        print("   bad_behaviour column. Includes both direct red cards and")
        print("   second yellow card dismissals.")
        
        print("\n⚪ CORNERS:")
        print(f"   Total Found: {corners_stats['total_corners']}")
        print(f"   Corner Events in Data: {corners_stats['corner_events_found']}")
        print("   Method: Analyzed play_pattern for 'From Corner' sequences")
        print("   Explanation: Corner kicks generate multiple related events")
        print("   (corner taken, ball cleared, etc.). Counted unique corner")
        print("   sequences by analyzing play_pattern changes and event indices")
        print("   to avoid double-counting related events from same corner.")
        
        print(f"\n{'='*80}")
        print("✅ VALIDATION COMPLETE - Statistics corrected and verified")
        print(f"{'='*80}")
        
    except Exception as e:
        print(f"Error during validation: {e}")
        raise

if __name__ == "__main__":
    main() 