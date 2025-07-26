#!/usr/bin/env python3
"""
Simplified Tournament Statistics Analysis
Creates 3-category analysis: Group Stage, Round of 16, Quarter-finals+Semi-finals+Final
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def load_data():
    """Load the required datasets"""
    print("Loading data...")
    
    matches = pd.read_csv('Data/matches_complete.csv')
    events = pd.read_csv('Data/events_complete.csv')
    
    print(f"Loaded {len(matches)} matches and {len(events)} events")
    return matches, events

def get_match_duration_info(matches, events):
    """Get actual match duration information for normalization"""
    print("Analyzing match durations...")
    
    duration_info = {}
    
    for _, match in matches.iterrows():
        match_id = match['match_id']
        stage = match['stage']
        
        # Get match events to determine actual duration
        match_events = events[events['match_id'] == match_id]
        
        if len(match_events) > 0:
            max_minute = match_events['minute'].max()
            max_period = match_events['period'].max()
            
            # Estimate actual playing time
            if max_period <= 2 and max_minute <= 95:
                actual_minutes = 90
            elif max_period <= 2 and max_minute > 95:
                actual_minutes = 90
            elif max_period >= 3:
                actual_minutes = 120
            else:
                actual_minutes = 90
                
            duration_info[match_id] = {
                'stage': stage,
                'actual_minutes': actual_minutes,
                'max_minute': max_minute,
                'max_period': max_period,
                'home_team': match['home_team_name'],
                'away_team': match['away_team_name'],
                'home_score': match['home_score'],
                'away_score': match['away_score']
            }
    
    return duration_info

def analyze_simplified_tournament(matches, events, duration_info):
    """Analyze tournament with simplified 3-category grouping"""
    print("Analyzing simplified tournament categories...")
    
    # Define the 3 categories
    categories = {
        'Group Stage': ['Group Stage'],
        'Round of 16': ['Round of 16'],
        'Quarter-finals + Semi-finals + Final': ['Quarter-finals', 'Semi-finals', 'Final']
    }
    
    results = {}
    
    for category_name, stage_list in categories.items():
        print(f"  Processing {category_name}...")
        
        # Get matches for this category
        category_matches = matches[matches['stage'].isin(stage_list)]
        category_events = events[events['match_id'].isin(category_matches['match_id'])]
        
        # Basic counts
        num_games = len(category_matches)
        
        # Goals from match data
        total_goals = category_matches['home_score'].sum() + category_matches['away_score'].sum()
        
        # Extra time and penalties
        games_to_extra_time = 0
        games_to_penalties = 0
        total_actual_minutes = 0
        
        for _, match in category_matches.iterrows():
            match_id = match['match_id']
            if match_id in duration_info:
                if duration_info[match_id]['actual_minutes'] > 90:
                    games_to_extra_time += 1
                total_actual_minutes += duration_info[match_id]['actual_minutes']
                
                # Check for penalties
                if match['home_score'] == match['away_score'] and match['stage'] != 'Group Stage':
                    match_events = events[events['match_id'] == match_id]
                    penalty_events = match_events[match_events['type'].astype(str).str.contains('Penalty', na=False)]
                    if len(penalty_events) > 0:
                        games_to_penalties += 1
            else:
                total_actual_minutes += 90
        
        # Draws and wins
        draws = len(category_matches[category_matches['home_score'] == category_matches['away_score']])
        wins = num_games - draws
        
        # Substitutions
        sub_events = category_events[category_events['type'].astype(str).str.contains('Substitution', na=False)]
        total_substitutions = len(sub_events)
        
        # Cards
        red_cards = 0
        yellow_cards = 0
        
        card_events = category_events[category_events['bad_behaviour'].notna()]
        for _, event in card_events.iterrows():
            bad_behaviour_str = str(event['bad_behaviour'])
            if 'Red Card' in bad_behaviour_str:
                red_cards += 1
            elif 'Yellow Card' in bad_behaviour_str:
                yellow_cards += 1
        
        # Corners
        corner_events = category_events[
            (category_events['type'].astype(str).str.contains('Pass', na=False)) &
            (category_events['pass'].astype(str).str.contains('corner', na=False, case=False))
        ]
        
        total_corners = 0
        for match_id in category_matches['match_id']:
            match_corners = corner_events[corner_events['match_id'] == match_id]
            if len(match_corners) > 0:
                corner_sequences = 0
                prev_minute = -1
                for _, corner in match_corners.iterrows():
                    if corner['minute'] > prev_minute + 2:
                        corner_sequences += 1
                    prev_minute = corner['minute']
                total_corners += corner_sequences
        
        # Calculate normalized statistics
        total_90min_equivalent = total_actual_minutes / 90 if total_actual_minutes > 0 else num_games
        
        # Store results
        results[category_name] = {
            'num_games': num_games,
            'total_goals': total_goals,
            'avg_goals_per_game': total_goals / num_games if num_games > 0 else 0,
            'avg_goals_per_90min': total_goals / total_90min_equivalent if total_90min_equivalent > 0 else 0,
            'games_to_extra_time': games_to_extra_time,
            'games_to_penalties': games_to_penalties,
            'total_draws': draws,
            'total_wins': wins,
            'total_substitutions': total_substitutions,
            'avg_subs_per_game': total_substitutions / num_games if num_games > 0 else 0,
            'avg_subs_per_90min': total_substitutions / total_90min_equivalent if total_90min_equivalent > 0 else 0,
            'total_red_cards': red_cards,
            'avg_red_cards_per_game': red_cards / num_games if num_games > 0 else 0,
            'avg_red_cards_per_90min': red_cards / total_90min_equivalent if total_90min_equivalent > 0 else 0,
            'total_yellow_cards': yellow_cards,
            'avg_yellow_cards_per_game': yellow_cards / num_games if num_games > 0 else 0,
            'avg_yellow_cards_per_90min': yellow_cards / total_90min_equivalent if total_90min_equivalent > 0 else 0,
            'total_corners': total_corners,
            'avg_corners_per_game': total_corners / num_games if num_games > 0 else 0,
            'avg_corners_per_90min': total_corners / total_90min_equivalent if total_90min_equivalent > 0 else 0,
            'total_actual_minutes': total_actual_minutes,
            'total_90min_equivalent': total_90min_equivalent,
            'extra_time_percentage': (games_to_extra_time / num_games * 100) if num_games > 0 else 0
        }
    
    return results

def create_simplified_summary_table(results):
    """Create simplified summary table"""
    print("Creating simplified summary table...")
    
    table_data = []
    
    statistics = [
        ('Number of Games', 'num_games'),
        ('Number of Goals', 'total_goals'),
        ('Average Goals per Game', 'avg_goals_per_game'),
        ('Average Goals per 90min', 'avg_goals_per_90min'),
        ('Games to Extra Time', 'games_to_extra_time'),
        ('Extra Time Percentage', 'extra_time_percentage'),
        ('Games to Penalties', 'games_to_penalties'),
        ('Total Draws', 'total_draws'),
        ('Total Wins', 'total_wins'),
        ('Total Substitutions', 'total_substitutions'),
        ('Average Substitutions per Game', 'avg_subs_per_game'),
        ('Average Substitutions per 90min', 'avg_subs_per_90min'),
        ('Total Red Cards', 'total_red_cards'),
        ('Average Red Cards per Game', 'avg_red_cards_per_game'),
        ('Average Red Cards per 90min', 'avg_red_cards_per_90min'),
        ('Total Yellow Cards', 'total_yellow_cards'),
        ('Average Yellow Cards per Game', 'avg_yellow_cards_per_game'),
        ('Average Yellow Cards per 90min', 'avg_yellow_cards_per_90min'),
        ('Total Corners', 'total_corners'),
        ('Average Corners per Game', 'avg_corners_per_game'),
        ('Average Corners per 90min', 'avg_corners_per_90min')
    ]
    
    # Create table data
    for stat_name, stat_key in statistics:
        row = {'Statistic': stat_name}
        for category in ['Group Stage', 'Round of 16', 'Quarter-finals + Semi-finals + Final']:
            if category in results:
                value = results[category][stat_key]
                # Format values appropriately
                if 'Average' in stat_name and 'per' in stat_name:
                    row[category] = f"{value:.2f}"
                elif 'Percentage' in stat_name:
                    row[category] = f"{value:.1f}%"
                else:
                    row[category] = str(int(value)) if isinstance(value, (int, float)) else str(value)
            else:
                row[category] = "0"
        table_data.append(row)
    
    summary_df = pd.DataFrame(table_data)
    return summary_df

def print_simplified_results(results):
    """Print simplified analysis results"""
    print("\n" + "="*80)
    print("SIMPLIFIED TOURNAMENT STATISTICS ANALYSIS")
    print("="*80)
    
    for category in ['Group Stage', 'Round of 16', 'Quarter-finals + Semi-finals + Final']:
        if category in results:
            data = results[category]
            print(f"\n{category.upper()}")
            print("-" * len(category))
            print(f"Games: {data['num_games']}")
            print(f"Total Actual Minutes: {data['total_actual_minutes']:.0f} ({data['total_90min_equivalent']:.1f} × 90min equivalent)")
            print(f"Games to Extra Time: {data['games_to_extra_time']} ({data['extra_time_percentage']:.1f}%)")
            print(f"Games to Penalties: {data['games_to_penalties']}")
            
            print(f"\nGoals:")
            print(f"  Per Game: {data['avg_goals_per_game']:.2f}")
            print(f"  Per 90min: {data['avg_goals_per_90min']:.2f}")
            if data['avg_goals_per_game'] > 0:
                diff = ((data['avg_goals_per_90min'] - data['avg_goals_per_game']) / data['avg_goals_per_game'] * 100)
                print(f"  Normalization Impact: {diff:+.1f}%")
            
            print(f"\nSubstitutions:")
            print(f"  Per Game: {data['avg_subs_per_game']:.2f}")
            print(f"  Per 90min: {data['avg_subs_per_90min']:.2f}")
            if data['avg_subs_per_game'] > 0:
                diff = ((data['avg_subs_per_90min'] - data['avg_subs_per_game']) / data['avg_subs_per_game'] * 100)
                print(f"  Normalization Impact: {diff:+.1f}%")

def save_simplified_results(summary_df, results):
    """Save simplified results to files"""
    print("\nSaving simplified results...")
    
    # Save summary table
    summary_df.to_csv('EDA/simplified_tournament_statistics_table.csv', index=False)
    
    # Save detailed results
    detailed_data = []
    for category, data in results.items():
        detailed_data.append({
            'Category': category,
            'Games': data['num_games'],
            'Total_Actual_Minutes': data['total_actual_minutes'],
            'Games_to_Extra_Time': data['games_to_extra_time'],
            'Extra_Time_Percentage': data['extra_time_percentage'],
            'Games_to_Penalties': data['games_to_penalties'],
            'Goals_Per_Game': data['avg_goals_per_game'],
            'Goals_Per_90min': data['avg_goals_per_90min'],
            'Subs_Per_Game': data['avg_subs_per_game'],
            'Subs_Per_90min': data['avg_subs_per_90min'],
            'Yellow_Cards_Per_Game': data['avg_yellow_cards_per_game'],
            'Yellow_Cards_Per_90min': data['avg_yellow_cards_per_90min'],
            'Corners_Per_Game': data['avg_corners_per_game'],
            'Corners_Per_90min': data['avg_corners_per_90min']
        })
    
    detailed_df = pd.DataFrame(detailed_data)
    detailed_df.to_csv('EDA/simplified_tournament_detailed.csv', index=False)
    
    print("Saved:")
    print("  - EDA/simplified_tournament_statistics_table.csv")
    print("  - EDA/simplified_tournament_detailed.csv")

def main():
    """Main analysis function"""
    print("SIMPLIFIED TOURNAMENT STATISTICS ANALYSIS")
    print("=" * 50)
    
    # Load data
    matches, events = load_data()
    
    # Get match duration information
    duration_info = get_match_duration_info(matches, events)
    
    # Analyze with simplified categories
    results = analyze_simplified_tournament(matches, events, duration_info)
    
    # Create summary table
    summary_df = create_simplified_summary_table(results)
    
    # Print results
    print_simplified_results(results)
    
    # Display summary table
    print("\n" + "="*80)
    print("SIMPLIFIED TOURNAMENT STATISTICS SUMMARY TABLE")
    print("="*80)
    print(summary_df.to_string(index=False))
    
    # Save results
    save_simplified_results(summary_df, results)
    
    print("\n" + "="*50)
    print("ANALYSIS COMPLETE!")
    print("Check EDA/ directory for simplified statistics files")

if __name__ == "__main__":
    main() 