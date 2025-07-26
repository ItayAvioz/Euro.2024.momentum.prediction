#!/usr/bin/env python3
"""
Normalized Tournament Statistics Analysis
Creates normalized (per 90 minutes) statistics for all tournament stages
Accounts for extra time and penalties in knockout rounds
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
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
    print("\nAnalyzing match durations...")
    
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
                # Regular time (90 + stoppage)
                actual_minutes = 90
            elif max_period <= 2 and max_minute > 95:
                # Regular time with extended stoppage
                actual_minutes = 90
            elif max_period >= 3:
                # Extra time
                actual_minutes = 120
            else:
                actual_minutes = 90  # Default
                
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

def analyze_tournament_by_stage(matches, events, duration_info):
    """Analyze tournament statistics by stage with normalization"""
    print("\nAnalyzing tournament statistics by stage...")
    
    stages = ['Group Stage', 'Round of 16', 'Quarter-finals', 'Semi-finals', 'Final']
    results = {}
    
    for stage in stages:
        print(f"  Processing {stage}...")
        
        stage_matches = matches[matches['stage'] == stage]
        stage_events = events[events['match_id'].isin(stage_matches['match_id'])]
        
        # Basic counts
        num_games = len(stage_matches)
        
        # Goals from match data (more reliable)
        total_goals = stage_matches['home_score'].sum() + stage_matches['away_score'].sum()
        
        # Extra time and penalties
        games_to_extra_time = 0
        games_to_penalties = 0
        total_actual_minutes = 0
        
        for _, match in stage_matches.iterrows():
            match_id = match['match_id']
            if match_id in duration_info:
                if duration_info[match_id]['actual_minutes'] > 90:
                    games_to_extra_time += 1
                total_actual_minutes += duration_info[match_id]['actual_minutes']
                
                # Check for penalties (0-0 after extra time or specific penalty events)
                if match['home_score'] == match['away_score'] and stage != 'Group Stage':
                    # Check for penalty events
                    match_events = events[events['match_id'] == match_id]
                    penalty_events = match_events[match_events['type'].astype(str).str.contains('Penalty', na=False)]
                    if len(penalty_events) > 0:
                        games_to_penalties += 1
            else:
                total_actual_minutes += 90  # Default to 90 minutes
        
        # Draws and wins
        draws = len(stage_matches[stage_matches['home_score'] == stage_matches['away_score']])
        wins = num_games - draws
        
        # Substitutions
        sub_events = stage_events[stage_events['type'].astype(str).str.contains('Substitution', na=False)]
        total_substitutions = len(sub_events)
        
        # Cards
        red_cards = 0
        yellow_cards = 0
        
        # Parse bad_behaviour column for cards
        card_events = stage_events[stage_events['bad_behaviour'].notna()]
        for _, event in card_events.iterrows():
            bad_behaviour_str = str(event['bad_behaviour'])
            if 'Red Card' in bad_behaviour_str:
                red_cards += 1
            elif 'Yellow Card' in bad_behaviour_str:
                yellow_cards += 1
        
        # Corners - count unique corner sequences
        corner_events = stage_events[
            (stage_events['type'].astype(str).str.contains('Pass', na=False)) &
            (stage_events['pass'].astype(str).str.contains('corner', na=False, case=False))
        ]
        
        # Group by match and count unique corner sequences
        total_corners = 0
        for match_id in stage_matches['match_id']:
            match_corners = corner_events[corner_events['match_id'] == match_id]
            if len(match_corners) > 0:
                # Count unique corner sequences (consecutive corners are one sequence)
                corner_sequences = 0
                prev_minute = -1
                for _, corner in match_corners.iterrows():
                    if corner['minute'] > prev_minute + 2:  # New sequence if >2 min gap
                        corner_sequences += 1
                    prev_minute = corner['minute']
                total_corners += corner_sequences
        
        # Calculate normalized (per 90 minutes) statistics
        total_90min_equivalent = total_actual_minutes / 90 if total_actual_minutes > 0 else num_games
        
        # Store results
        results[stage] = {
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
            'total_90min_equivalent': total_90min_equivalent
        }
    
    return results

def create_summary_table(results):
    """Create summary table matching the provided format"""
    print("\nCreating summary table...")
    
    # Prepare data for DataFrame
    table_data = []
    
    # Map stage names to match the image
    stage_mapping = {
        'Group Stage': 'Group Stage',
        'Round of 16': 'Round of 16', 
        'Quarter-finals': 'Quarter-finals',
        'Semi-finals': 'Semi-finals',
        'Final': 'Final'
    }
    
    statistics = [
        ('Number of Games', 'num_games'),
        ('Number of Goals', 'total_goals'),
        ('Average Goals per Game', 'avg_goals_per_game'),
        ('Average Goals per 90min', 'avg_goals_per_90min'),
        ('Games to Extra Time', 'games_to_extra_time'),
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
        for stage in ['Group Stage', 'Round of 16', 'Quarter-finals', 'Semi-finals', 'Final']:
            if stage in results:
                value = results[stage][stat_key]
                # Format values appropriately
                if 'Average' in stat_name and 'per' in stat_name:
                    row[stage] = f"{value:.2f}"
                else:
                    row[stage] = str(int(value)) if isinstance(value, (int, float)) else str(value)
            else:
                row[stage] = "0"
        table_data.append(row)
    
    # Create DataFrame
    summary_df = pd.DataFrame(table_data)
    
    return summary_df

def create_comparison_visualization(results):
    """Create visualization comparing regular vs normalized statistics"""
    print("\nCreating comparison visualizations...")
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Tournament Statistics: Regular vs Normalized (per 90 minutes)', fontsize=16, fontweight='bold')
    
    stages = ['Group Stage', 'Round of 16', 'Quarter-finals', 'Semi-finals', 'Final']
    
    # 1. Goals per game vs per 90min
    regular_goals = [results[stage]['avg_goals_per_game'] for stage in stages]
    normalized_goals = [results[stage]['avg_goals_per_90min'] for stage in stages]
    
    x = np.arange(len(stages))
    width = 0.35
    
    ax1.bar(x - width/2, regular_goals, width, label='Per Game', alpha=0.8, color='#FF6B6B')
    ax1.bar(x + width/2, normalized_goals, width, label='Per 90min', alpha=0.8, color='#4ECDC4')
    ax1.set_title('Average Goals: Per Game vs Per 90min', fontweight='bold')
    ax1.set_ylabel('Goals')
    ax1.set_xticks(x)
    ax1.set_xticklabels(stages, rotation=45)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Substitutions per game vs per 90min
    regular_subs = [results[stage]['avg_subs_per_game'] for stage in stages]
    normalized_subs = [results[stage]['avg_subs_per_90min'] for stage in stages]
    
    ax2.bar(x - width/2, regular_subs, width, label='Per Game', alpha=0.8, color='#FF6B6B')
    ax2.bar(x + width/2, normalized_subs, width, label='Per 90min', alpha=0.8, color='#4ECDC4')
    ax2.set_title('Average Substitutions: Per Game vs Per 90min', fontweight='bold')
    ax2.set_ylabel('Substitutions')
    ax2.set_xticks(x)
    ax2.set_xticklabels(stages, rotation=45)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Yellow cards per game vs per 90min
    regular_yellow = [results[stage]['avg_yellow_cards_per_game'] for stage in stages]
    normalized_yellow = [results[stage]['avg_yellow_cards_per_90min'] for stage in stages]
    
    ax3.bar(x - width/2, regular_yellow, width, label='Per Game', alpha=0.8, color='#FF6B6B')
    ax3.bar(x + width/2, normalized_yellow, width, label='Per 90min', alpha=0.8, color='#4ECDC4')
    ax3.set_title('Average Yellow Cards: Per Game vs Per 90min', fontweight='bold')
    ax3.set_ylabel('Yellow Cards')
    ax3.set_xticks(x)
    ax3.set_xticklabels(stages, rotation=45)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Corners per game vs per 90min
    regular_corners = [results[stage]['avg_corners_per_game'] for stage in stages]
    normalized_corners = [results[stage]['avg_corners_per_90min'] for stage in stages]
    
    ax4.bar(x - width/2, regular_corners, width, label='Per Game', alpha=0.8, color='#FF6B6B')
    ax4.bar(x + width/2, normalized_corners, width, label='Per 90min', alpha=0.8, color='#4ECDC4')
    ax4.set_title('Average Corners: Per Game vs Per 90min', fontweight='bold')
    ax4.set_ylabel('Corners')
    ax4.set_xticks(x)
    ax4.set_xticklabels(stages, rotation=45)
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('EDA/normalized_tournament_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

def print_detailed_results(results):
    """Print detailed analysis results"""
    print("\n" + "="*80)
    print("NORMALIZED TOURNAMENT STATISTICS ANALYSIS")
    print("="*80)
    
    for stage in ['Group Stage', 'Round of 16', 'Quarter-finals', 'Semi-finals', 'Final']:
        if stage in results:
            data = results[stage]
            print(f"\n{stage.upper()}")
            print("-" * len(stage))
            print(f"Games: {data['num_games']}")
            print(f"Total Actual Minutes: {data['total_actual_minutes']:.0f} ({data['total_90min_equivalent']:.1f} × 90min equivalent)")
            print(f"Games to Extra Time: {data['games_to_extra_time']}")
            print(f"Games to Penalties: {data['games_to_penalties']}")
            
            print(f"\nGoals:")
            print(f"  Per Game: {data['avg_goals_per_game']:.2f}")
            print(f"  Per 90min: {data['avg_goals_per_90min']:.2f}")
            print(f"  Difference: {((data['avg_goals_per_90min'] - data['avg_goals_per_game']) / data['avg_goals_per_game'] * 100):+.1f}%" if data['avg_goals_per_game'] > 0 else "  Difference: N/A")
            
            print(f"\nSubstitutions:")
            print(f"  Per Game: {data['avg_subs_per_game']:.2f}")
            print(f"  Per 90min: {data['avg_subs_per_90min']:.2f}")
            print(f"  Difference: {((data['avg_subs_per_90min'] - data['avg_subs_per_game']) / data['avg_subs_per_game'] * 100):+.1f}%" if data['avg_subs_per_game'] > 0 else "  Difference: N/A")

def save_results(summary_df, results):
    """Save results to CSV files"""
    print("\nSaving results...")
    
    # Save summary table
    summary_df.to_csv('EDA/normalized_tournament_statistics_table.csv', index=False)
    
    # Save detailed results
    detailed_data = []
    for stage, data in results.items():
        detailed_data.append({
            'Stage': stage,
            'Games': data['num_games'],
            'Total_Actual_Minutes': data['total_actual_minutes'],
            'Games_to_Extra_Time': data['games_to_extra_time'],
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
    detailed_df.to_csv('EDA/normalized_tournament_detailed.csv', index=False)
    
    print("Saved:")
    print("  - EDA/normalized_tournament_statistics_table.csv")
    print("  - EDA/normalized_tournament_detailed.csv")
    print("  - EDA/normalized_tournament_comparison.png")

def main():
    """Main analysis function"""
    print("NORMALIZED TOURNAMENT STATISTICS ANALYSIS")
    print("=" * 50)
    
    # Load data
    matches, events = load_data()
    
    # Get match duration information
    duration_info = get_match_duration_info(matches, events)
    
    # Analyze by stage
    results = analyze_tournament_by_stage(matches, events, duration_info)
    
    # Create summary table
    summary_df = create_summary_table(results)
    
    # Print results
    print_detailed_results(results)
    
    # Display summary table
    print("\n" + "="*80)
    print("TOURNAMENT STATISTICS SUMMARY TABLE")
    print("="*80)
    print(summary_df.to_string(index=False))
    
    # Create visualizations
    create_comparison_visualization(results)
    
    # Save results
    save_results(summary_df, results)
    
    print("\n" + "="*50)
    print("ANALYSIS COMPLETE!")
    print("Check EDA/ directory for files and visualizations")

if __name__ == "__main__":
    main() 