#!/usr/bin/env python3
"""
Corrected Euro 2024 Tournament Statistics by Stage
Using match-level data for accurate goal counting and stage analysis
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
    
    print("Loading Euro 2024 datasets...")
    df_events = pd.read_csv(data_path)
    df_matches = pd.read_csv(matches_path) if matches_path.exists() else None
    
    print(f"Events dataset: {df_events.shape[0]:,} rows × {df_events.shape[1]} columns")
    if df_matches is not None:
        print(f"Matches dataset: {df_matches.shape[0]:,} rows × {df_matches.shape[1]} columns")
    
    return df_events, df_matches

def get_stage_mapping(df_matches):
    """Get stage mapping from matches dataset"""
    print("\nGetting stage information from matches dataset...")
    
    stage_mapping = {}
    
    if df_matches is not None and 'stage' in df_matches.columns:
        for idx, row in df_matches.iterrows():
            match_id = row['match_id']
            stage = row['stage']
            stage_mapping[match_id] = stage
    
    # Print stage distribution
    stage_counts = {}
    for stage in stage_mapping.values():
        stage_counts[stage] = stage_counts.get(stage, 0) + 1
    
    print("Stage distribution:")
    for stage, count in sorted(stage_counts.items()):
        print(f"  {stage}: {count} matches")
    
    return stage_mapping

def analyze_goals_correctly_by_stage(df_matches, stage_mapping):
    """Analyze goals correctly using match scores"""
    print("\nAnalyzing goals by stage using match scores...")
    
    stage_goals = {}
    
    for stage in ['Group Stage', 'Round of 16', 'Quarter-finals', 'Semi-finals', 'Final']:
        stage_matches = [match_id for match_id, match_stage in stage_mapping.items() if match_stage == stage]
        stage_match_data = df_matches[df_matches['match_id'].isin(stage_matches)]
        
        if stage_match_data.empty:
            stage_goals[stage] = 0
            continue
        
        # Calculate total goals from home_score and away_score
        total_goals = stage_match_data['home_score'].sum() + stage_match_data['away_score'].sum()
        stage_goals[stage] = int(total_goals)
        
        print(f"  {stage}: {total_goals} goals in {len(stage_matches)} matches")
    
    return stage_goals

def analyze_comprehensive_stage_statistics(df_events, df_matches, stage_mapping):
    """Analyze comprehensive statistics by stage"""
    print("\nAnalyzing comprehensive statistics by stage...")
    
    stages = ['Group Stage', 'Round of 16', 'Quarter-finals', 'Semi-finals', 'Final']
    stage_stats = {}
    
    # Get goals using match scores
    stage_goals = analyze_goals_correctly_by_stage(df_matches, stage_mapping)
    
    for stage in stages:
        stage_matches = [match_id for match_id, match_stage in stage_mapping.items() if match_stage == stage]
        
        if not stage_matches:
            continue
        
        # Filter data for this stage
        stage_events = df_events[df_events['match_id'].isin(stage_matches)]
        stage_match_data = df_matches[df_matches['match_id'].isin(stage_matches)]
        
        num_games = len(stage_matches)
        goals = stage_goals.get(stage, 0)
        
        print(f"\n{stage}: {num_games} matches")
        
        # Match results
        if not stage_match_data.empty:
            draws = len(stage_match_data[stage_match_data['home_score'] == stage_match_data['away_score']])
            wins = num_games - draws
        else:
            draws = wins = 0
        
        # Extra time and penalties
        extra_time_matches = set()
        penalty_matches = set()
        
        if 'period' in stage_events.columns:
            for match_id in stage_matches:
                match_events = stage_events[stage_events['match_id'] == match_id]
                if not match_events.empty:
                    max_period = match_events['period'].max()
                    if max_period >= 3:
                        extra_time_matches.add(match_id)
                    if max_period >= 5:
                        penalty_matches.add(match_id)
        
        extra_time_only = len(extra_time_matches) - len(penalty_matches)
        
        # Substitutions
        sub_events = stage_events[stage_events['event_type'] == 'Substitution']
        if sub_events.empty and 'substitution' in stage_events.columns:
            sub_events = stage_events[stage_events['substitution'].notna()]
        substitutions = len(sub_events)
        
        # Cards
        card_events = stage_events[stage_events['bad_behaviour'].notna()]
        red_cards = yellow_cards = 0
        
        for idx, row in card_events.iterrows():
            try:
                bad_behaviour_str = str(row['bad_behaviour'])
                if 'Yellow Card' in bad_behaviour_str:
                    yellow_cards += 1
                elif 'Red Card' in bad_behaviour_str or 'Second Yellow' in bad_behaviour_str:
                    red_cards += 1
            except:
                continue
        
        # Corners (simplified counting)
        corner_events = stage_events[stage_events['play_pattern'].str.contains('Corner', case=False, na=False)]
        
        # Count corners per match more accurately
        corners = 0
        for match_id in stage_matches:
            match_corner_events = corner_events[corner_events['match_id'] == match_id]
            # Count unique corner sequences
            unique_corners = 0
            prev_index = -1
            
            for idx, row in match_corner_events.iterrows():
                current_index = row['index'] if 'index' in row else idx
                if prev_index == -1 or current_index - prev_index > 10:
                    unique_corners += 1
                prev_index = current_index
            
            corners += unique_corners
        
        # Compile statistics
        stage_stats[stage] = {
            'num_games': num_games,
            'goals': goals,
            'avg_goals_per_game': goals / num_games if num_games > 0 else 0,
            'extra_time_games': extra_time_only,
            'penalty_games': len(penalty_matches),
            'draws': draws,
            'wins': wins,
            'substitutions': substitutions,
            'avg_substitutions_per_game': substitutions / num_games if num_games > 0 else 0,
            'red_cards': red_cards,
            'avg_red_cards_per_game': red_cards / num_games if num_games > 0 else 0,
            'yellow_cards': yellow_cards,
            'avg_yellow_cards_per_game': yellow_cards / num_games if num_games > 0 else 0,
            'corners': corners,
            'avg_corners_per_game': corners / num_games if num_games > 0 else 0
        }
        
        print(f"  Goals: {goals} ({goals/num_games:.2f}/game)")
        print(f"  Draws: {draws}, Wins: {wins}")
        print(f"  Extra time: {extra_time_only}, Penalties: {len(penalty_matches)}")
        print(f"  Cards: {yellow_cards} yellow, {red_cards} red")
        print(f"  Corners: {corners} ({corners/num_games:.2f}/game)")
    
    return stage_stats

def create_stage_statistics_table(stage_stats):
    """Create the corrected stage statistics table"""
    
    stage_order = ['Group Stage', 'Round of 16', 'Quarter-finals', 'Semi-finals', 'Final']
    
    # Create table data
    table_data = []
    
    stats_to_include = [
        ('Number of Games', 'num_games'),
        ('Number of Goals', 'goals'),
        ('Average Goals per Game', 'avg_goals_per_game'),
        ('Games to Extra Time', 'extra_time_games'),
        ('Games to Penalties', 'penalty_games'),
        ('Total Draws', 'draws'),
        ('Total Wins', 'wins'),
        ('Total Substitutions', 'substitutions'),
        ('Average Substitutions per Game', 'avg_substitutions_per_game'),
        ('Total Red Cards', 'red_cards'),
        ('Average Red Cards per Game', 'avg_red_cards_per_game'),
        ('Total Yellow Cards', 'yellow_cards'),
        ('Average Yellow Cards per Game', 'avg_yellow_cards_per_game'),
        ('Total Corners', 'corners'),
        ('Average Corners per Game', 'avg_corners_per_game')
    ]
    
    for stat_name, stat_key in stats_to_include:
        row = [stat_name]
        for stage in stage_order:
            if stage in stage_stats:
                value = stage_stats[stage].get(stat_key, 0)
                if isinstance(value, float):
                    row.append(f"{value:.2f}")
                else:
                    row.append(str(value))
            else:
                row.append('-')
        table_data.append(row)
    
    headers = ['Statistic'] + [stage for stage in stage_order if stage in stage_stats]
    
    return headers, table_data

def print_corrected_stage_statistics(stage_stats):
    """Print the corrected stage statistics table"""
    
    headers, table_data = create_stage_statistics_table(stage_stats)
    
    print("\n" + "="*130)
    print("EURO 2024 TOURNAMENT STATISTICS BY STAGE (CORRECTED)")
    print("="*130)
    
    # Print table
    col_width = 30
    stage_width = 15
    
    # Headers
    header_line = f"{'Statistic':<{col_width}}"
    for header in headers[1:]:
        header_line += f"{header:<{stage_width}}"
    print(header_line)
    print("-" * 130)
    
    # Data rows
    for row in table_data:
        line = f"{row[0]:<{col_width}}"
        for value in row[1:]:
            line += f"{value:<{stage_width}}"
        print(line)
    
    print("-" * 130)

def analyze_stage_trends_corrected(stage_stats):
    """Analyze trends with corrected data"""
    
    print("\n" + "="*80)
    print("CORRECTED STAGE TREND ANALYSIS")
    print("="*80)
    
    stage_order = ['Group Stage', 'Round of 16', 'Quarter-finals', 'Semi-finals', 'Final']
    
    print("\n🥅 GOALS TREND (Corrected):")
    for stage in stage_order:
        if stage in stage_stats:
            goals = stage_stats[stage]['goals']
            avg_goals = stage_stats[stage]['avg_goals_per_game']
            games = stage_stats[stage]['num_games']
            print(f"   {stage:<15}: {goals} total ({avg_goals:.2f}/game, {games} games)")
    
    print("\n🎯 KNOCKOUT STAGE INTENSITY:")
    knockout_stages = ['Round of 16', 'Quarter-finals', 'Semi-finals', 'Final']
    for stage in knockout_stages:
        if stage in stage_stats:
            extra = stage_stats[stage]['extra_time_games']
            penalties = stage_stats[stage]['penalty_games']
            games = stage_stats[stage]['num_games']
            intensity = (extra + penalties) / games * 100 if games > 0 else 0
            print(f"   {stage:<15}: {intensity:.1f}% went beyond 90 minutes ({extra} ET, {penalties} penalties)")
    
    print("\n🟨 DISCIPLINARY TREND:")
    for stage in stage_order:
        if stage in stage_stats:
            yellow = stage_stats[stage]['yellow_cards']
            red = stage_stats[stage]['red_cards']
            games = stage_stats[stage]['num_games']
            yellow_avg = yellow / games if games > 0 else 0
            red_avg = red / games if games > 0 else 0
            print(f"   {stage:<15}: {yellow_avg:.2f} yellow/game, {red_avg:.2f} red/game")

def save_corrected_stage_statistics(stage_stats, output_dir):
    """Save corrected stage statistics"""
    
    headers, table_data = create_stage_statistics_table(stage_stats)
    
    # Create DataFrame and save
    df_stats = pd.DataFrame(table_data, columns=headers)
    stats_path = output_dir / 'euro_2024_corrected_stage_statistics.csv'
    df_stats.to_csv(stats_path, index=False)
    
    print(f"\n📊 Corrected stage statistics saved to: {stats_path}")

def main():
    """Main analysis function"""
    print("EURO 2024 CORRECTED TOURNAMENT STATISTICS BY STAGE")
    print("="*60)
    
    # Create output directory
    output_dir = Path("EDA/analysis/tournament_statistics")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Load data
        df_events, df_matches = load_euro_2024_data()
        
        if df_matches is None:
            print("ERROR: Matches dataset required for accurate goal counting")
            return
        
        # Get stage mapping
        stage_mapping = get_stage_mapping(df_matches)
        
        # Analyze statistics by stage
        stage_stats = analyze_comprehensive_stage_statistics(df_events, df_matches, stage_mapping)
        
        # Print and save results
        print_corrected_stage_statistics(stage_stats)
        analyze_stage_trends_corrected(stage_stats)
        save_corrected_stage_statistics(stage_stats, output_dir)
        
        print(f"\n{'='*80}")
        print("✅ CORRECTED STAGE ANALYSIS COMPLETE")
        print(f"{'='*80}")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        raise

if __name__ == "__main__":
    main() 