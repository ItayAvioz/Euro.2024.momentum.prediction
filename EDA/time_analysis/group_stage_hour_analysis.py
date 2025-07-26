import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

print("=== EURO 2024 GROUP STAGE BY KICKOFF HOUR ANALYSIS ===")

# Load the data
matches = pd.read_csv('../Data/matches_complete.csv')

# Parse kickoff times
def extract_kickoff_hour(kick_off_str):
    try:
        if pd.isna(kick_off_str):
            return None
        hour_part = str(kick_off_str).split(':')[0]
        return int(hour_part)
    except:
        return None

matches['kickoff_hour'] = matches['kick_off'].apply(extract_kickoff_hour)

# Filter only Group Stage matches
group_stage_matches = matches[matches['stage'] == 'Group Stage'].copy()
group_stage_matches = group_stage_matches.dropna(subset=['kickoff_hour'])

print(f"Total Group Stage matches: {len(group_stage_matches)}")

# ===== BASIC ANALYSIS =====
print("\n" + "="*70)
print("GROUP STAGE KICKOFF DISTRIBUTION")
print("="*70)

# Create analysis dataset
gs_analysis = []

for _, match in group_stage_matches.iterrows():
    kickoff_hour = match['kickoff_hour']
    match_week = match['match_week']
    
    # Get final scores
    ft_home_goals = int(match['home_score']) if pd.notna(match['home_score']) else 0
    ft_away_goals = int(match['away_score']) if pd.notna(match['away_score']) else 0
    
    total_goals = ft_home_goals + ft_away_goals
    goal_difference = abs(ft_home_goals - ft_away_goals)
    
    if ft_home_goals > ft_away_goals:
        outcome = 'Home Win'
    elif ft_away_goals > ft_home_goals:
        outcome = 'Away Win'
    else:
        outcome = 'Draw'
    
    gs_analysis.append({
        'match_id': match['match_id'],
        'kickoff_hour': kickoff_hour,
        'match_week': match_week,
        'home_team': match['home_team_name'],
        'away_team': match['away_team_name'],
        'home_goals': ft_home_goals,
        'away_goals': ft_away_goals,
        'total_goals': total_goals,
        'goal_difference': goal_difference,
        'outcome': outcome,
        'match_date': match['match_date']
    })

gs_df = pd.DataFrame(gs_analysis)

# Hour distribution
hour_distribution = gs_df['kickoff_hour'].value_counts().sort_index()

print("GROUP STAGE MATCHES BY HOUR:")
print("Hour" + " "*8 + "Matches" + " "*5 + "Percentage")
print("-" * 40)

total_gs_matches = len(gs_df)
for hour, count in hour_distribution.items():
    percentage = (count / total_gs_matches) * 100
    print(f"{hour:02d}:00 {count:>10} {percentage:>10.1f}%")

# ===== DETAILED ANALYSIS BY HOUR =====
print("\n" + "="*70)
print("DETAILED ANALYSIS BY KICKOFF HOUR")
print("="*70)

hour_stats = []

for hour in sorted(gs_df['kickoff_hour'].unique()):
    hour_matches = gs_df[gs_df['kickoff_hour'] == hour]
    
    # Basic stats
    num_matches = len(hour_matches)
    
    # Outcomes
    draws = len(hour_matches[hour_matches['outcome'] == 'Draw'])
    home_wins = len(hour_matches[hour_matches['outcome'] == 'Home Win'])
    away_wins = len(hour_matches[hour_matches['outcome'] == 'Away Win'])
    
    # Goals
    total_goals = hour_matches['total_goals'].sum()
    avg_goals = hour_matches['total_goals'].mean()
    min_goals = hour_matches['total_goals'].min()
    max_goals = hour_matches['total_goals'].max()
    
    # Goal differences
    avg_goal_diff = hour_matches['goal_difference'].mean()
    
    # Percentages
    draw_pct = (draws / num_matches) * 100
    home_win_pct = (home_wins / num_matches) * 100
    away_win_pct = (away_wins / num_matches) * 100
    
    # Goal categories
    zero_goals = len(hour_matches[hour_matches['total_goals'] == 0])
    low_scoring = len(hour_matches[hour_matches['total_goals'] <= 1])
    high_scoring = len(hour_matches[hour_matches['total_goals'] >= 4])
    
    hour_stats.append({
        'Hour': hour,
        'Matches': num_matches,
        'Draws': draws,
        'Draw_%': draw_pct,
        'Home_Wins': home_wins,
        'Home_Win_%': home_win_pct,
        'Away_Wins': away_wins,
        'Away_Win_%': away_win_pct,
        'Total_Goals': total_goals,
        'Avg_Goals': avg_goals,
        'Min_Goals': min_goals,
        'Max_Goals': max_goals,
        'Avg_Goal_Diff': avg_goal_diff,
        'Zero_Goals': zero_goals,
        'Low_Scoring': low_scoring,
        'High_Scoring': high_scoring,
        'Zero_Goals_%': (zero_goals / num_matches) * 100,
        'Low_Scoring_%': (low_scoring / num_matches) * 100,
        'High_Scoring_%': (high_scoring / num_matches) * 100
    })

# Display detailed stats
for stats in hour_stats:
    print(f"\n{stats['Hour']:02d}:00 - {stats['Matches']} MATCHES")
    print("-" * 40)
    print(f"Outcomes:")
    print(f"  Draws: {stats['Draws']} ({stats['Draw_%']:.1f}%)")
    print(f"  Home Wins: {stats['Home_Wins']} ({stats['Home_Win_%']:.1f}%)")
    print(f"  Away Wins: {stats['Away_Wins']} ({stats['Away_Win_%']:.1f}%)")
    
    print(f"Goals:")
    print(f"  Total: {stats['Total_Goals']} goals")
    print(f"  Average: {stats['Avg_Goals']:.2f} per match")
    print(f"  Range: {stats['Min_Goals']}-{stats['Max_Goals']} goals")
    print(f"  Avg Goal Difference: {stats['Avg_Goal_Diff']:.2f}")
    
    print(f"Scoring Categories:")
    print(f"  Zero goals: {stats['Zero_Goals']} ({stats['Zero_Goals_%']:.1f}%)")
    print(f"  Low-scoring (0-1): {stats['Low_Scoring']} ({stats['Low_Scoring_%']:.1f}%)")
    print(f"  High-scoring (4+): {stats['High_Scoring']} ({stats['High_Scoring_%']:.1f}%)")

# ===== MATCHDAY BREAKDOWN BY HOUR =====
print("\n" + "="*70)
print("MATCHDAY DISTRIBUTION BY HOUR")
print("="*70)

matchday_hour_cross = pd.crosstab(gs_df['match_week'], gs_df['kickoff_hour'])
print("MATCHES BY MATCHDAY AND HOUR:")
print(matchday_hour_cross)

# Analyze each matchday by hour
print(f"\nMATCHDAY BREAKDOWN:")
for matchday in sorted(gs_df['match_week'].unique()):
    md_matches = gs_df[gs_df['match_week'] == matchday]
    hour_dist = md_matches['kickoff_hour'].value_counts().sort_index()
    
    print(f"\nMatchday {matchday} ({len(md_matches)} matches):")
    for hour, count in hour_dist.items():
        pct = (count / len(md_matches)) * 100
        md_hour_matches = md_matches[md_matches['kickoff_hour'] == hour]
        avg_goals_md_hour = md_hour_matches['total_goals'].mean()
        draws_md_hour = len(md_hour_matches[md_hour_matches['outcome'] == 'Draw'])
        draw_pct_md_hour = (draws_md_hour / count) * 100
        
        print(f"  {hour:02d}:00: {count} matches ({pct:.1f}%) - {avg_goals_md_hour:.2f} goals/match, {draw_pct_md_hour:.1f}% draws")

# ===== COMPARATIVE ANALYSIS =====
print("\n" + "="*70)
print("COMPARATIVE ANALYSIS ACROSS HOURS")
print("="*70)

stats_df = pd.DataFrame(hour_stats)

# Find patterns
highest_scoring_hour = stats_df.loc[stats_df['Avg_Goals'].idxmax(), 'Hour']
highest_scoring_avg = stats_df['Avg_Goals'].max()

lowest_scoring_hour = stats_df.loc[stats_df['Avg_Goals'].idxmin(), 'Hour']
lowest_scoring_avg = stats_df['Avg_Goals'].min()

most_draws_hour = stats_df.loc[stats_df['Draw_%'].idxmax(), 'Hour']
most_draws_pct = stats_df['Draw_%'].max()

least_draws_hour = stats_df.loc[stats_df['Draw_%'].idxmin(), 'Hour']
least_draws_pct = stats_df['Draw_%'].min()

print("COMPARATIVE RANKINGS:")
print(f"Highest scoring: {highest_scoring_hour:02d}:00 ({highest_scoring_avg:.2f} goals/match)")
print(f"Lowest scoring: {lowest_scoring_hour:02d}:00 ({lowest_scoring_avg:.2f} goals/match)")
print(f"Most draws: {most_draws_hour:02d}:00 ({most_draws_pct:.1f}%)")
print(f"Least draws: {least_draws_hour:02d}:00 ({least_draws_pct:.1f}%)")

# Goals difference analysis
goals_range = highest_scoring_avg - lowest_scoring_avg
draws_range = most_draws_pct - least_draws_pct

print(f"\nVARIATION ANALYSIS:")
print(f"Goals per match range: {goals_range:.2f} (difference between highest and lowest)")
print(f"Draw percentage range: {draws_range:.1f} percentage points")

# Home advantage analysis
print(f"\nHOME ADVANTAGE BY HOUR:")
for _, stats in stats_df.iterrows():
    home_advantage = stats['Home_Win_%'] - stats['Away_Win_%']
    print(f"{stats['Hour']:02d}:00: Home {stats['Home_Win_%']:.1f}% vs Away {stats['Away_Win_%']:.1f}% (Advantage: {home_advantage:+.1f}%)")

# ===== SAVE RESULTS =====
print("\n" + "="*70)
print("SAVING RESULTS")
print("="*70)

# Save detailed analysis
gs_df.to_csv('group_stage_by_hour_detailed.csv', index=False)
stats_df.to_csv('group_stage_hour_statistics.csv', index=False)

print("Files saved:")
print("- group_stage_by_hour_detailed.csv")
print("- group_stage_hour_statistics.csv")

print(f"\n=== GROUP STAGE HOUR ANALYSIS COMPLETE ===")
print(f"Key Finding: {highest_scoring_hour:02d}:00 is most attacking ({highest_scoring_avg:.2f} goals)")
print(f"Strategy Impact: {goals_range:.2f} goal difference between time slots")
print(f"Draw Variation: {draws_range:.1f}% difference in competitive balance") 