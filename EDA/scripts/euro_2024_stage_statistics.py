#!/usr/bin/env python3
"""
Euro 2024 Tournament Statistics by Stage
Comprehensive analysis of tournament statistics broken down by stage
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

def identify_stages(df_events, df_matches):
    """Identify tournament stages for each match"""
    print("\nIdentifying tournament stages...")
    
    # First, try to get stage information from the stage column
    stage_mapping = {}
    
    if 'stage' in df_events.columns:
        # Get stage information from events data
        for match_id in df_events['match_id'].unique():
            match_events = df_events[df_events['match_id'] == match_id]
            stage = match_events['stage'].iloc[0] if not match_events['stage'].isna().all() else 'Unknown'
            stage_mapping[match_id] = stage
    
    # Also check matches data if available
    if df_matches is not None and 'stage' in df_matches.columns:
        for idx, row in df_matches.iterrows():
            match_id = row['match_id']
            stage = row['stage'] if pd.notna(row['stage']) else 'Unknown'
            stage_mapping[match_id] = stage
    
    # If we still don't have stage info, try to infer from match_week or competition_stage
    if not stage_mapping or all(v == 'Unknown' for v in stage_mapping.values()):
        print("Stage column not found, attempting to infer from other columns...")
        
        if 'competition_stage' in df_events.columns:
            for match_id in df_events['match_id'].unique():
                match_events = df_events[df_events['match_id'] == match_id]
                comp_stage = match_events['competition_stage'].iloc[0] if not match_events['competition_stage'].isna().all() else 'Unknown'
                stage_mapping[match_id] = comp_stage
        elif 'match_week' in df_events.columns:
            # Infer stages from match week (typical Euro format)
            for match_id in df_events['match_id'].unique():
                match_events = df_events[df_events['match_id'] == match_id]
                match_week = match_events['match_week'].iloc[0] if not match_events['match_week'].isna().all() else 0
                
                if match_week <= 3:
                    stage = "Group Stage"
                elif match_week == 4:
                    stage = "Round of 16"
                elif match_week == 5:
                    stage = "Quarter-finals"
                elif match_week == 6:
                    stage = "Semi-finals"
                elif match_week == 7:
                    stage = "Final"
                else:
                    stage = "Unknown"
                
                stage_mapping[match_id] = stage
    
    print(f"Found {len(stage_mapping)} matches with stage information")
    
    # Print stage distribution
    stage_counts = {}
    for stage in stage_mapping.values():
        stage_counts[stage] = stage_counts.get(stage, 0) + 1
    
    print("Stage distribution:")
    for stage, count in sorted(stage_counts.items()):
        print(f"  {stage}: {count} matches")
    
    return stage_mapping

def analyze_stage_statistics(df_events, df_matches, stage_mapping):
    """Analyze statistics for each tournament stage"""
    print("\nAnalyzing statistics by stage...")
    
    stages = ['Group Stage', 'Round of 16', 'Quarter-finals', 'Semi-finals', 'Final']
    stage_stats = {}
    
    for stage in stages:
        # Get matches for this stage
        stage_matches = [match_id for match_id, match_stage in stage_mapping.items() if match_stage == stage]
        
        if not stage_matches:
            print(f"No matches found for {stage}")
            continue
        
        # Filter events for this stage
        stage_events = df_events[df_events['match_id'].isin(stage_matches)]
        stage_matches_data = df_matches[df_matches['match_id'].isin(stage_matches)] if df_matches is not None else None
        
        print(f"\nAnalyzing {stage}: {len(stage_matches)} matches, {len(stage_events):,} events")
        
        # Basic statistics
        num_games = len(stage_matches)
        
        # Goals analysis
        goals = analyze_goals_for_stage(stage_events)
        
        # Match results
        results = analyze_match_results_for_stage(stage_matches_data) if stage_matches_data is not None else {'draws': 0, 'wins': 0}
        
        # Extra time and penalties
        time_stats = analyze_extra_time_for_stage(stage_events)
        
        # Substitutions
        substitutions = analyze_substitutions_for_stage(stage_events)
        
        # Cards
        cards = analyze_cards_for_stage(stage_events)
        
        # Corners
        corners = analyze_corners_for_stage(stage_events)
        
        # Compile stage statistics
        stage_stats[stage] = {
            'num_games': num_games,
            'goals': goals,
            'avg_goals_per_game': goals / num_games if num_games > 0 else 0,
            'extra_time_games': time_stats['extra_time'],
            'penalty_games': time_stats['penalties'],
            'draws': results['draws'],
            'wins': results['wins'],
            'substitutions': substitutions,
            'avg_substitutions_per_game': substitutions / num_games if num_games > 0 else 0,
            'red_cards': cards['red'],
            'avg_red_cards_per_game': cards['red'] / num_games if num_games > 0 else 0,
            'yellow_cards': cards['yellow'],
            'avg_yellow_cards_per_game': cards['yellow'] / num_games if num_games > 0 else 0,
            'corners': corners,
            'avg_corners_per_game': corners / num_games if num_games > 0 else 0
        }
    
    return stage_stats

def analyze_goals_for_stage(stage_events):
    """Analyze goals for a specific stage"""
    # Look for actual goal outcomes in shot events
    shot_events = stage_events[stage_events['event_type'] == 'Shot'].copy()
    
    goals = 0
    if not shot_events.empty and 'shot' in shot_events.columns:
        for idx, row in shot_events.iterrows():
            try:
                shot_data = str(row['shot'])
                if 'goal' in shot_data.lower() and 'outcome' in shot_data.lower():
                    if 'Goal' in shot_data:
                        goals += 1
            except:
                continue
    
    return goals

def analyze_match_results_for_stage(stage_matches_data):
    """Analyze match results for a specific stage"""
    if stage_matches_data is None or stage_matches_data.empty:
        return {'draws': 0, 'wins': 0}
    
    if 'home_score' in stage_matches_data.columns and 'away_score' in stage_matches_data.columns:
        draws = len(stage_matches_data[stage_matches_data['home_score'] == stage_matches_data['away_score']])
        wins = len(stage_matches_data) - draws
        return {'draws': draws, 'wins': wins}
    
    return {'draws': 0, 'wins': 0}

def analyze_extra_time_for_stage(stage_events):
    """Analyze extra time and penalties for a specific stage"""
    extra_time_matches = set()
    penalty_matches = set()
    
    if 'period' in stage_events.columns:
        for match_id in stage_events['match_id'].unique():
            match_events = stage_events[stage_events['match_id'] == match_id]
            max_period = match_events['period'].max()
            
            if max_period >= 3:
                extra_time_matches.add(match_id)
            if max_period >= 5:
                penalty_matches.add(match_id)
    
    extra_time_only = len(extra_time_matches) - len(penalty_matches)
    
    return {
        'extra_time': extra_time_only,
        'penalties': len(penalty_matches)
    }

def analyze_substitutions_for_stage(stage_events):
    """Analyze substitutions for a specific stage"""
    sub_events = stage_events[stage_events['event_type'] == 'Substitution']
    
    if sub_events.empty and 'substitution' in stage_events.columns:
        sub_events = stage_events[stage_events['substitution'].notna()]
    
    return len(sub_events)

def analyze_cards_for_stage(stage_events):
    """Analyze cards for a specific stage"""
    card_events = stage_events[stage_events['bad_behaviour'].notna()]
    
    red_cards = 0
    yellow_cards = 0
    
    for idx, row in card_events.iterrows():
        try:
            bad_behaviour_str = str(row['bad_behaviour'])
            if 'Yellow Card' in bad_behaviour_str:
                yellow_cards += 1
            elif 'Red Card' in bad_behaviour_str or 'Second Yellow' in bad_behaviour_str:
                red_cards += 1
        except:
            continue
    
    return {'red': red_cards, 'yellow': yellow_cards}

def analyze_corners_for_stage(stage_events):
    """Analyze corners for a specific stage"""
    corner_events = stage_events[stage_events['play_pattern'].str.contains('Corner', case=False, na=False)]
    
    corners_per_match = {}
    
    for match_id in stage_events['match_id'].unique():
        match_corner_events = corner_events[corner_events['match_id'] == match_id]
        
        unique_corners = 0
        prev_index = -1
        
        for idx, row in match_corner_events.iterrows():
            current_index = row['index'] if 'index' in row else idx
            if prev_index == -1 or current_index - prev_index > 10:
                unique_corners += 1
            prev_index = current_index
        
        corners_per_match[match_id] = unique_corners
    
    return sum(corners_per_match.values())

def create_stage_statistics_table(stage_stats):
    """Create comprehensive stage statistics table"""
    
    # Define the order of stages
    stage_order = ['Group Stage', 'Round of 16', 'Quarter-finals', 'Semi-finals', 'Final']
    
    table_data = []
    
    # Header row
    headers = ['Statistic'] + [stage for stage in stage_order if stage in stage_stats]
    
    # Statistics rows
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
    
    return headers, table_data

def print_stage_statistics(stage_stats):
    """Print formatted stage statistics"""
    
    headers, table_data = create_stage_statistics_table(stage_stats)
    
    print("\n" + "="*120)
    print("EURO 2024 TOURNAMENT STATISTICS BY STAGE")
    print("="*120)
    
    # Calculate column widths
    col_width = 25
    stage_width = 15
    
    # Print headers
    header_line = f"{'Statistic':<{col_width}}"
    for header in headers[1:]:
        header_line += f"{header:<{stage_width}}"
    print(header_line)
    print("-" * 120)
    
    # Print data rows
    for row in table_data:
        line = f"{row[0]:<{col_width}}"
        for value in row[1:]:
            line += f"{value:<{stage_width}}"
        print(line)
    
    print("-" * 120)

def save_stage_statistics(stage_stats, output_dir):
    """Save stage statistics to CSV"""
    
    headers, table_data = create_stage_statistics_table(stage_stats)
    
    # Create DataFrame
    df_stats = pd.DataFrame(table_data, columns=headers)
    
    # Save file
    stats_path = output_dir / 'euro_2024_stage_statistics.csv'
    df_stats.to_csv(stats_path, index=False)
    
    print(f"\n📊 Stage statistics saved to: {stats_path}")
    
    # Also save detailed stage data
    detailed_data = []
    for stage, stats in stage_stats.items():
        for stat_key, value in stats.items():
            detailed_data.append({
                'Stage': stage,
                'Statistic': stat_key,
                'Value': value
            })
    
    df_detailed = pd.DataFrame(detailed_data)
    detailed_path = output_dir / 'euro_2024_detailed_stage_statistics.csv'
    df_detailed.to_csv(detailed_path, index=False)
    
    print(f"📋 Detailed stage data saved to: {detailed_path}")

def analyze_stage_trends(stage_stats):
    """Analyze trends across tournament stages"""
    
    print("\n" + "="*80)
    print("STAGE TREND ANALYSIS")
    print("="*80)
    
    stage_order = ['Group Stage', 'Round of 16', 'Quarter-finals', 'Semi-finals', 'Final']
    
    print("\n🥅 GOALS TREND:")
    for stage in stage_order:
        if stage in stage_stats:
            avg_goals = stage_stats[stage]['avg_goals_per_game']
            print(f"   {stage:<15}: {avg_goals:.2f} goals/game")
    
    print("\n🟨 CARDS TREND:")
    for stage in stage_order:
        if stage in stage_stats:
            avg_yellow = stage_stats[stage]['avg_yellow_cards_per_game']
            avg_red = stage_stats[stage]['avg_red_cards_per_game']
            print(f"   {stage:<15}: {avg_yellow:.2f} yellow, {avg_red:.2f} red per game")
    
    print("\n⚽ CORNERS TREND:")
    for stage in stage_order:
        if stage in stage_stats:
            avg_corners = stage_stats[stage]['avg_corners_per_game']
            print(f"   {stage:<15}: {avg_corners:.2f} corners/game")
    
    print("\n🔄 SUBSTITUTIONS TREND:")
    for stage in stage_order:
        if stage in stage_stats:
            avg_subs = stage_stats[stage]['avg_substitutions_per_game']
            print(f"   {stage:<15}: {avg_subs:.2f} substitutions/game")
    
    print("\n⏱️ EXTRA TIME/PENALTIES:")
    for stage in stage_order:
        if stage in stage_stats:
            extra_time = stage_stats[stage]['extra_time_games']
            penalties = stage_stats[stage]['penalty_games']
            total_games = stage_stats[stage]['num_games']
            print(f"   {stage:<15}: {extra_time} extra time, {penalties} penalties ({total_games} total games)")

def main():
    """Main analysis function"""
    print("EURO 2024 TOURNAMENT STATISTICS BY STAGE")
    print("="*60)
    
    # Create output directory
    output_dir = Path("EDA/analysis/tournament_statistics")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Load data
        df_events, df_matches = load_euro_2024_data()
        
        # Identify stages
        stage_mapping = identify_stages(df_events, df_matches)
        
        # Analyze statistics by stage
        stage_stats = analyze_stage_statistics(df_events, df_matches, stage_mapping)
        
        # Print and save results
        print_stage_statistics(stage_stats)
        analyze_stage_trends(stage_stats)
        save_stage_statistics(stage_stats, output_dir)
        
        print(f"\n{'='*80}")
        print("✅ STAGE ANALYSIS COMPLETE")
        print(f"{'='*80}")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        raise

if __name__ == "__main__":
    main() 