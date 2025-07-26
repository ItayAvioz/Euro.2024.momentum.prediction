#!/usr/bin/env python3
"""
Euro 2024 Tournament Statistics Analysis
Comprehensive analysis of tournament-wide statistics
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def load_euro_2024_data():
    """Load the main Euro 2024 dataset"""
    data_path = Path("Data/euro_2024_complete_dataset.csv")
    matches_path = Path("Data/matches_complete.csv")
    
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found at {data_path}")
    
    print("Loading Euro 2024 datasets...")
    df_events = pd.read_csv(data_path)
    
    # Load matches data if available
    if matches_path.exists():
        df_matches = pd.read_csv(matches_path)
        print(f"Events dataset: {df_events.shape[0]:,} rows × {df_events.shape[1]} columns")
        print(f"Matches dataset: {df_matches.shape[0]:,} rows × {df_matches.shape[1]} columns")
        return df_events, df_matches
    else:
        print(f"Events dataset: {df_events.shape[0]:,} rows × {df_events.shape[1]} columns")
        print("Matches dataset not found - will derive match info from events")
        return df_events, None

def analyze_matches_and_goals(df_events, df_matches=None):
    """Analyze match counts and goal statistics"""
    print("\nAnalyzing matches and goals...")
    
    # Number of games
    num_games = df_events['match_id'].nunique()
    
    # Goals analysis - look for goal events
    goal_events = df_events[df_events['event_type'].str.contains('Goal', case=False, na=False)]
    if goal_events.empty:
        # Try alternative approach - look for shot events that resulted in goals
        shot_events = df_events[df_events['event_type'].str.contains('Shot', case=False, na=False)]
        # Check if shot has outcome indicating goal
        goal_events = shot_events[shot_events['shot'].str.contains('Goal', case=False, na=False)]
    
    total_goals = len(goal_events)
    avg_goals_per_game = total_goals / num_games if num_games > 0 else 0
    
    # Extra time and penalties analysis
    # Look for events in extra time periods or penalty shootouts
    extra_time_games = 0
    penalty_games = 0
    
    # Check periods - regular time is periods 1-2, extra time is 3-4, penalties is 5
    if 'period' in df_events.columns:
        extra_time_matches = df_events[df_events['period'] > 2]['match_id'].nunique()
        penalty_matches = df_events[df_events['period'] == 5]['match_id'].nunique()
        extra_time_games = extra_time_matches - penalty_matches  # Extra time only (not including penalties)
        penalty_games = penalty_matches
    
    # Match outcomes analysis
    match_results = {}
    if df_matches is not None and 'home_score' in df_matches.columns and 'away_score' in df_matches.columns:
        draws = len(df_matches[df_matches['home_score'] == df_matches['away_score']])
        wins = len(df_matches) - draws  # Total games minus draws
        match_results = {'draws': draws, 'wins': wins}
    else:
        # Try to derive from events data
        match_scores = []
        for match_id in df_events['match_id'].unique():
            match_events = df_events[df_events['match_id'] == match_id]
            if 'home_score' in match_events.columns and 'away_score' in match_events.columns:
                # Get final scores
                final_home = match_events['home_score'].iloc[-1] if not match_events['home_score'].isna().all() else 0
                final_away = match_events['away_score'].iloc[-1] if not match_events['away_score'].isna().all() else 0
                match_scores.append((final_home, final_away))
        
        if match_scores:
            draws = sum(1 for home, away in match_scores if home == away)
            wins = len(match_scores) - draws
            match_results = {'draws': draws, 'wins': wins}
        else:
            match_results = {'draws': 'Unknown', 'wins': 'Unknown'}
    
    return {
        'num_games': num_games,
        'total_goals': total_goals,
        'avg_goals_per_game': avg_goals_per_game,
        'extra_time_games': extra_time_games,
        'penalty_games': penalty_games,
        'draws': match_results.get('draws', 'Unknown'),
        'wins': match_results.get('wins', 'Unknown'),
        'goal_events_found': len(goal_events)
    }

def analyze_substitutions(df_events):
    """Analyze substitution statistics"""
    print("Analyzing substitutions...")
    
    # Look for substitution events
    substitution_events = df_events[df_events['event_type'].str.contains('Substitution', case=False, na=False)]
    
    if substitution_events.empty:
        # Try alternative approaches
        if 'substitution' in df_events.columns:
            substitution_events = df_events[df_events['substitution'].notna()]
        elif 'player_off' in df_events.columns:
            # Player off events might indicate substitutions
            substitution_events = df_events[df_events['player_off'].notna()]
    
    total_substitutions = len(substitution_events)
    num_games = df_events['match_id'].nunique()
    avg_substitutions_per_game = total_substitutions / num_games if num_games > 0 else 0
    
    return {
        'total_substitutions': total_substitutions,
        'avg_substitutions_per_game': avg_substitutions_per_game,
        'method_used': 'event_type' if not substitution_events.empty else 'alternative_columns'
    }

def analyze_cards(df_events):
    """Analyze red and yellow card statistics"""
    print("Analyzing cards (red and yellow)...")
    
    # Method 1: Look for card events in event_type
    red_card_events = df_events[df_events['event_type'].str.contains('Red Card|Sending Off', case=False, na=False)]
    yellow_card_events = df_events[df_events['event_type'].str.contains('Yellow Card|Booking', case=False, na=False)]
    
    # Method 2: Look in bad_behaviour column for card information
    card_events_alt = df_events[df_events['bad_behaviour'].notna()]
    red_cards_alt = 0
    yellow_cards_alt = 0
    
    if not card_events_alt.empty:
        for idx, row in card_events_alt.iterrows():
            try:
                bad_behaviour = str(row['bad_behaviour'])
                if 'red' in bad_behaviour.lower() or 'sending' in bad_behaviour.lower():
                    red_cards_alt += 1
                elif 'yellow' in bad_behaviour.lower() or 'booking' in bad_behaviour.lower():
                    yellow_cards_alt += 1
            except:
                continue
    
    # Use the method that finds more cards
    red_cards_method1 = len(red_card_events)
    yellow_cards_method1 = len(yellow_card_events)
    
    if red_cards_alt > red_cards_method1 or yellow_cards_alt > yellow_cards_method1:
        total_red_cards = red_cards_alt
        total_yellow_cards = yellow_cards_alt
        method_used = "bad_behaviour column analysis"
    else:
        total_red_cards = red_cards_method1
        total_yellow_cards = yellow_cards_method1
        method_used = "event_type pattern matching"
    
    num_games = df_events['match_id'].nunique()
    avg_red_cards_per_game = total_red_cards / num_games if num_games > 0 else 0
    avg_yellow_cards_per_game = total_yellow_cards / num_games if num_games > 0 else 0
    
    return {
        'total_red_cards': total_red_cards,
        'avg_red_cards_per_game': avg_red_cards_per_game,
        'total_yellow_cards': total_yellow_cards,
        'avg_yellow_cards_per_game': avg_yellow_cards_per_game,
        'method_used': method_used,
        'method1_results': f"Red: {red_cards_method1}, Yellow: {yellow_cards_method1}",
        'method2_results': f"Red: {red_cards_alt}, Yellow: {yellow_cards_alt}"
    }

def analyze_corners(df_events):
    """Analyze corner kick statistics"""
    print("Analyzing corners...")
    
    # Method 1: Look for corner events in event_type
    corner_events = df_events[df_events['event_type'].str.contains('Corner', case=False, na=False)]
    
    # Method 2: Look in play_pattern for corners (corners start from corner kicks)
    corner_play_pattern = df_events[df_events['play_pattern'].str.contains('Corner', case=False, na=False)]
    
    # Method 3: Check if there's a specific corner column or in other event details
    corner_events_alt = 0
    if 'corner' in df_events.columns:
        corner_events_alt = df_events[df_events['corner'].notna()]
        corner_events_alt = len(corner_events_alt)
    
    # Use the method that finds the most corners
    corners_method1 = len(corner_events)
    corners_method2 = len(corner_play_pattern)
    corners_method3 = corner_events_alt
    
    if corners_method2 > corners_method1 and corners_method2 > corners_method3:
        total_corners = corners_method2
        method_used = "play_pattern analysis (events starting from corners)"
    elif corners_method3 > corners_method1 and corners_method3 > corners_method2:
        total_corners = corners_method3
        method_used = "corner column analysis"
    else:
        total_corners = corners_method1
        method_used = "event_type pattern matching"
    
    num_games = df_events['match_id'].nunique()
    avg_corners_per_game = total_corners / num_games if num_games > 0 else 0
    
    return {
        'total_corners': total_corners,
        'avg_corners_per_game': avg_corners_per_game,
        'method_used': method_used,
        'method1_results': f"Event type: {corners_method1}",
        'method2_results': f"Play pattern: {corners_method2}",
        'method3_results': f"Corner column: {corners_method3}"
    }

def create_tournament_statistics_table(stats):
    """Create a formatted statistics table"""
    
    # Create the main statistics table
    table_data = [
        ['Number of Games', stats['matches']['num_games'], ''],
        ['Number of Goals', stats['matches']['total_goals'], ''],
        ['Average Goals per Game', f"{stats['matches']['avg_goals_per_game']:.2f}", ''],
        ['Games to Extra Time', stats['matches']['extra_time_games'], ''],
        ['Games to Penalties', stats['matches']['penalty_games'], ''],
        ['Total Draws', stats['matches']['draws'], ''],
        ['Total Wins', stats['matches']['wins'], ''],
        ['Total Substitutions', stats['substitutions']['total_substitutions'], ''],
        ['Average Substitutions per Game', f"{stats['substitutions']['avg_substitutions_per_game']:.2f}", ''],
        ['Total Red Cards', stats['cards']['total_red_cards'], ''],
        ['Average Red Cards per Game', f"{stats['cards']['avg_red_cards_per_game']:.2f}", ''],
        ['Total Yellow Cards', stats['cards']['total_yellow_cards'], ''],
        ['Average Yellow Cards per Game', f"{stats['cards']['avg_yellow_cards_per_game']:.2f}", ''],
        ['Total Corners', stats['corners']['total_corners'], ''],
        ['Average Corners per Game', f"{stats['corners']['avg_corners_per_game']:.2f}", '']
    ]
    
    return table_data

def print_tournament_statistics(stats):
    """Print formatted tournament statistics"""
    
    print("\n" + "="*80)
    print("EURO 2024 TOURNAMENT STATISTICS")
    print("="*80)
    
    table_data = create_tournament_statistics_table(stats)
    
    # Print main table
    print(f"{'Statistic':<35} {'Value':<15} {'Notes':<20}")
    print("-" * 80)
    
    for stat, value, notes in table_data:
        print(f"{stat:<35} {value:<15} {notes:<20}")
    
    print("-" * 80)
    
    # Print methodology explanations
    print("\n" + "="*80)
    print("METHODOLOGY EXPLANATIONS")
    print("="*80)
    
    print("\n🟡 YELLOW CARDS:")
    print(f"   Method Used: {stats['cards']['method_used']}")
    print(f"   Method 1 (Event Type): {stats['cards']['method1_results']}")
    print(f"   Method 2 (Bad Behaviour): {stats['cards']['method2_results']}")
    print("   Explanation: Searched for card events in 'event_type' column using pattern")
    print("   matching (Yellow Card, Booking) and cross-validated with 'bad_behaviour'")
    print("   column to ensure accuracy. Used the method that found more card events.")
    
    print("\n🔴 RED CARDS:")
    print(f"   Method Used: {stats['cards']['method_used']}")
    print("   Explanation: Similar to yellow cards, searched for red card events using")
    print("   pattern matching (Red Card, Sending Off) in both 'event_type' and")
    print("   'bad_behaviour' columns. Selected the method with higher detection rate.")
    
    print("\n⚪ CORNERS:")
    print(f"   Method Used: {stats['corners']['method_used']}")
    print(f"   Method 1: {stats['corners']['method1_results']}")
    print(f"   Method 2: {stats['corners']['method2_results']}")
    print(f"   Method 3: {stats['corners']['method3_results']}")
    print("   Explanation: Analyzed corner kicks using three approaches:")
    print("   1. Direct 'Corner' events in event_type column")
    print("   2. Events with play_pattern starting 'From Corner'")
    print("   3. Dedicated corner column if available")
    print("   Selected the method that identified the most corner events.")
    
    print(f"\n{'='*80}")
    print("📊 Data Quality Notes:")
    print(f"   • Total events analyzed: {stats.get('total_events', 'Unknown'):,}")
    print(f"   • Matches in dataset: {stats['matches']['num_games']}")
    print(f"   • Goal events found: {stats['matches'].get('goal_events_found', 'Unknown')}")
    print("   • Statistics derived from complete Euro 2024 event-level data")
    print(f"{'='*80}")

def save_tournament_statistics(stats, output_dir):
    """Save tournament statistics to CSV"""
    
    table_data = create_tournament_statistics_table(stats)
    
    # Create DataFrame
    df_stats = pd.DataFrame(table_data, columns=['Statistic', 'Value', 'Notes'])
    
    # Add methodology information
    methodology_data = [
        ['Cards Analysis Method', stats['cards']['method_used'], 'Yellow and Red Cards'],
        ['Corners Analysis Method', stats['corners']['method_used'], 'Corner Kicks'],
        ['Substitutions Analysis Method', stats['substitutions']['method_used'], 'Player Substitutions']
    ]
    
    df_methodology = pd.DataFrame(methodology_data, columns=['Analysis_Type', 'Method_Used', 'Description'])
    
    # Save files
    stats_path = output_dir / 'euro_2024_tournament_statistics.csv'
    methodology_path = output_dir / 'analysis_methodology.csv'
    
    df_stats.to_csv(stats_path, index=False)
    df_methodology.to_csv(methodology_path, index=False)
    
    print(f"\n📊 Tournament statistics saved to: {stats_path}")
    print(f"📋 Methodology details saved to: {methodology_path}")

def main():
    """Main analysis function"""
    print("EURO 2024 TOURNAMENT STATISTICS ANALYSIS")
    print("="*60)
    
    # Create output directory
    output_dir = Path("EDA/analysis/tournament_statistics")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Load data
        df_events, df_matches = load_euro_2024_data()
        
        # Analyze different aspects
        matches_stats = analyze_matches_and_goals(df_events, df_matches)
        substitutions_stats = analyze_substitutions(df_events)
        cards_stats = analyze_cards(df_events)
        corners_stats = analyze_corners(df_events)
        
        # Combine all statistics
        tournament_stats = {
            'matches': matches_stats,
            'substitutions': substitutions_stats,
            'cards': cards_stats,
            'corners': corners_stats,
            'total_events': len(df_events)
        }
        
        # Print and save results
        print_tournament_statistics(tournament_stats)
        save_tournament_statistics(tournament_stats, output_dir)
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        raise

if __name__ == "__main__":
    main() 