#!/usr/bin/env python3
"""
Euro 2024 Group Stage Analysis by Matchday
Detailed breakdown of Group Stage statistics by Game 1, Game 2, Game 3
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

def identify_group_stage_matches(df_matches):
    """Identify Group Stage matches and their matchdays"""
    print("\nIdentifying Group Stage matches by matchday...")
    
    # Filter for Group Stage matches
    group_matches = df_matches[df_matches['stage'] == 'Group Stage'].copy()
    
    print(f"Found {len(group_matches)} Group Stage matches")
    
    # Determine matchday based on match_week
    # Euro 2024 Group Stage typically runs across 3 weeks
    matchday_mapping = {}
    
    if 'match_week' in group_matches.columns:
        # Sort by match_week to understand the progression
        group_matches = group_matches.sort_values(['match_week', 'match_date'])
        
        # Map match weeks to matchdays
        unique_weeks = sorted(group_matches['match_week'].unique())
        print(f"Group Stage match weeks: {unique_weeks}")
        
        for idx, row in group_matches.iterrows():
            match_id = row['match_id']
            match_week = row['match_week']
            
            # Map weeks to matchdays (assuming first 3 weeks are group stage)
            if match_week == unique_weeks[0]:
                matchday = "Matchday 1"
            elif match_week == unique_weeks[1]:
                matchday = "Matchday 2"
            elif match_week == unique_weeks[2]:
                matchday = "Matchday 3"
            else:
                matchday = "Unknown"
            
            matchday_mapping[match_id] = matchday
    
    # Print matchday distribution
    matchday_counts = {}
    for matchday in matchday_mapping.values():
        matchday_counts[matchday] = matchday_counts.get(matchday, 0) + 1
    
    print("Matchday distribution:")
    for matchday, count in sorted(matchday_counts.items()):
        print(f"  {matchday}: {count} matches")
    
    return matchday_mapping, group_matches

def analyze_goals_by_matchday(df_matches, matchday_mapping):
    """Analyze goals by matchday using match scores"""
    print("\nAnalyzing goals by matchday...")
    
    matchday_goals = {}
    
    for matchday in ['Matchday 1', 'Matchday 2', 'Matchday 3']:
        matchday_matches = [match_id for match_id, md in matchday_mapping.items() if md == matchday]
        matchday_match_data = df_matches[df_matches['match_id'].isin(matchday_matches)]
        
        if matchday_match_data.empty:
            matchday_goals[matchday] = 0
            continue
        
        # Calculate total goals from home_score and away_score
        total_goals = matchday_match_data['home_score'].sum() + matchday_match_data['away_score'].sum()
        matchday_goals[matchday] = int(total_goals)
        
        print(f"  {matchday}: {total_goals} goals in {len(matchday_matches)} matches")
    
    return matchday_goals

def analyze_comprehensive_matchday_statistics(df_events, df_matches, matchday_mapping):
    """Analyze comprehensive statistics by matchday"""
    print("\nAnalyzing comprehensive statistics by matchday...")
    
    matchdays = ['Matchday 1', 'Matchday 2', 'Matchday 3']
    matchday_stats = {}
    
    # Get goals using match scores
    matchday_goals = analyze_goals_by_matchday(df_matches, matchday_mapping)
    
    for matchday in matchdays:
        matchday_matches = [match_id for match_id, md in matchday_mapping.items() if md == matchday]
        
        if not matchday_matches:
            continue
        
        # Filter data for this matchday
        matchday_events = df_events[df_events['match_id'].isin(matchday_matches)]
        matchday_match_data = df_matches[df_matches['match_id'].isin(matchday_matches)]
        
        num_games = len(matchday_matches)
        goals = matchday_goals.get(matchday, 0)
        
        print(f"\n{matchday}: {num_games} matches")
        
        # Match results
        if not matchday_match_data.empty:
            draws = len(matchday_match_data[matchday_match_data['home_score'] == matchday_match_data['away_score']])
            wins = num_games - draws
        else:
            draws = wins = 0
        
        # Extra time and penalties (should be 0 for group stage)
        extra_time_matches = set()
        penalty_matches = set()
        
        if 'period' in matchday_events.columns:
            for match_id in matchday_matches:
                match_events = matchday_events[matchday_events['match_id'] == match_id]
                if not match_events.empty:
                    max_period = match_events['period'].max()
                    if max_period >= 3:
                        extra_time_matches.add(match_id)
                    if max_period >= 5:
                        penalty_matches.add(match_id)
        
        extra_time_only = len(extra_time_matches) - len(penalty_matches)
        
        # Substitutions
        sub_events = matchday_events[matchday_events['event_type'] == 'Substitution']
        if sub_events.empty and 'substitution' in matchday_events.columns:
            sub_events = matchday_events[matchday_events['substitution'].notna()]
        substitutions = len(sub_events)
        
        # Cards
        card_events = matchday_events[matchday_events['bad_behaviour'].notna()]
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
        
        # Corners
        corner_events = matchday_events[matchday_events['play_pattern'].str.contains('Corner', case=False, na=False)]
        
        # Count corners per match more accurately
        corners = 0
        for match_id in matchday_matches:
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
        matchday_stats[matchday] = {
            'num_games': num_games,
            'goals': goals,
            'avg_goals_per_game': goals / num_games if num_games > 0 else 0,
            'extra_time_games': extra_time_only,
            'penalty_games': len(penalty_matches),
            'draws': draws,
            'wins': wins,
            'draw_percentage': (draws / num_games * 100) if num_games > 0 else 0,
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
        print(f"  Draws: {draws} ({draws/num_games*100:.1f}%), Wins: {wins}")
        print(f"  Cards: {yellow_cards} yellow, {red_cards} red")
        print(f"  Corners: {corners} ({corners/num_games:.2f}/game)")
    
    return matchday_stats

def create_matchday_statistics_table(matchday_stats):
    """Create the matchday statistics table"""
    
    matchday_order = ['Matchday 1', 'Matchday 2', 'Matchday 3']
    
    # Create table data
    table_data = []
    
    stats_to_include = [
        ('Number of Games', 'num_games'),
        ('Number of Goals', 'goals'),
        ('Average Goals per Game', 'avg_goals_per_game'),
        ('Games to Extra Time', 'extra_time_games'),
        ('Games to Penalties', 'penalty_games'),
        ('Total Draws', 'draws'),
        ('Draw Percentage', 'draw_percentage'),
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
        for matchday in matchday_order:
            if matchday in matchday_stats:
                value = matchday_stats[matchday].get(stat_key, 0)
                if isinstance(value, float):
                    if 'percentage' in stat_key.lower():
                        row.append(f"{value:.1f}%")
                    else:
                        row.append(f"{value:.2f}")
                else:
                    row.append(str(value))
            else:
                row.append('-')
        table_data.append(row)
    
    headers = ['Statistic'] + [matchday for matchday in matchday_order if matchday in matchday_stats]
    
    return headers, table_data

def print_matchday_statistics(matchday_stats):
    """Print the formatted matchday statistics table"""
    
    headers, table_data = create_matchday_statistics_table(matchday_stats)
    
    print("\n" + "="*100)
    print("EURO 2024 GROUP STAGE STATISTICS BY MATCHDAY")
    print("="*100)
    
    # Print table
    col_width = 35
    matchday_width = 15
    
    # Headers
    header_line = f"{'Statistic':<{col_width}}"
    for header in headers[1:]:
        header_line += f"{header:<{matchday_width}}"
    print(header_line)
    print("-" * 100)
    
    # Data rows
    for row in table_data:
        line = f"{row[0]:<{col_width}}"
        for value in row[1:]:
            line += f"{value:<{matchday_width}}"
        print(line)
    
    print("-" * 100)

def analyze_matchday_trends(matchday_stats):
    """Analyze trends across matchdays"""
    
    print("\n" + "="*80)
    print("GROUP STAGE MATCHDAY TREND ANALYSIS")
    print("="*80)
    
    matchday_order = ['Matchday 1', 'Matchday 2', 'Matchday 3']
    
    print("\n🥅 GOALS PROGRESSION:")
    for matchday in matchday_order:
        if matchday in matchday_stats:
            goals = matchday_stats[matchday]['goals']
            avg_goals = matchday_stats[matchday]['avg_goals_per_game']
            games = matchday_stats[matchday]['num_games']
            print(f"   {matchday}: {goals} total ({avg_goals:.2f}/game, {games} games)")
    
    print("\n🎯 COMPETITIVENESS EVOLUTION:")
    for matchday in matchday_order:
        if matchday in matchday_stats:
            draws = matchday_stats[matchday]['draws']
            draw_pct = matchday_stats[matchday]['draw_percentage']
            games = matchday_stats[matchday]['num_games']
            print(f"   {matchday}: {draws}/{games} draws ({draw_pct:.1f}%)")
    
    print("\n🟨 DISCIPLINARY PROGRESSION:")
    for matchday in matchday_order:
        if matchday in matchday_stats:
            yellow = matchday_stats[matchday]['yellow_cards']
            red = matchday_stats[matchday]['red_cards']
            games = matchday_stats[matchday]['num_games']
            yellow_avg = yellow / games if games > 0 else 0
            red_avg = red / games if games > 0 else 0
            print(f"   {matchday}: {yellow_avg:.2f} yellow/game, {red_avg:.2f} red/game")
    
    print("\n⚽ TACTICAL TRENDS:")
    for matchday in matchday_order:
        if matchday in matchday_stats:
            corners = matchday_stats[matchday]['avg_corners_per_game']
            subs = matchday_stats[matchday]['avg_substitutions_per_game']
            print(f"   {matchday}: {corners:.2f} corners/game, {subs:.2f} subs/game")
    
    # Calculate trends
    print("\n📈 KEY TRENDS:")
    
    # Goals trend
    goals_trend = []
    for matchday in matchday_order:
        if matchday in matchday_stats:
            goals_trend.append(matchday_stats[matchday]['avg_goals_per_game'])
    
    if len(goals_trend) >= 3:
        if goals_trend[2] > goals_trend[0]:
            print(f"   🔥 Goals increased from Matchday 1 to 3: {goals_trend[0]:.2f} → {goals_trend[2]:.2f} (+{((goals_trend[2]/goals_trend[0]-1)*100):.1f}%)")
        else:
            print(f"   📉 Goals decreased from Matchday 1 to 3: {goals_trend[0]:.2f} → {goals_trend[2]:.2f} ({((goals_trend[2]/goals_trend[0]-1)*100):.1f}%)")
    
    # Draw trend
    draw_trend = []
    for matchday in matchday_order:
        if matchday in matchday_stats:
            draw_trend.append(matchday_stats[matchday]['draw_percentage'])
    
    if len(draw_trend) >= 3:
        if draw_trend[2] < draw_trend[0]:
            print(f"   ⚡ Competitiveness increased: Draws decreased from {draw_trend[0]:.1f}% to {draw_trend[2]:.1f}%")
        else:
            print(f"   🤝 Balanced competition: Draws increased from {draw_trend[0]:.1f}% to {draw_trend[2]:.1f}%")

def save_matchday_statistics(matchday_stats, output_dir):
    """Save matchday statistics"""
    
    headers, table_data = create_matchday_statistics_table(matchday_stats)
    
    # Create DataFrame and save
    df_stats = pd.DataFrame(table_data, columns=headers)
    stats_path = output_dir / 'euro_2024_group_stage_matchday_statistics.csv'
    df_stats.to_csv(stats_path, index=False)
    
    print(f"\n📊 Group Stage matchday statistics saved to: {stats_path}")

def main():
    """Main analysis function"""
    print("EURO 2024 GROUP STAGE ANALYSIS BY MATCHDAY")
    print("="*60)
    
    # Create output directory
    output_dir = Path("EDA/analysis/tournament_statistics")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Load data
        df_events, df_matches = load_euro_2024_data()
        
        if df_matches is None:
            print("ERROR: Matches dataset required for accurate analysis")
            return
        
        # Identify Group Stage matches by matchday
        matchday_mapping, group_matches = identify_group_stage_matches(df_matches)
        
        # Analyze statistics by matchday
        matchday_stats = analyze_comprehensive_matchday_statistics(df_events, df_matches, matchday_mapping)
        
        # Print and save results
        print_matchday_statistics(matchday_stats)
        analyze_matchday_trends(matchday_stats)
        save_matchday_statistics(matchday_stats, output_dir)
        
        print(f"\n{'='*80}")
        print("✅ GROUP STAGE MATCHDAY ANALYSIS COMPLETE")
        print(f"{'='*80}")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        raise

if __name__ == "__main__":
    main() 