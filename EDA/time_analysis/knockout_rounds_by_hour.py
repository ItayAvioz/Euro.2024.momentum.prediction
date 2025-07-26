import pandas as pd
import numpy as np

print("=== EURO 2024 KNOCKOUT ROUNDS (1/8 + 1/4) BY KICKOFF HOUR ANALYSIS ===")

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

# Filter Round of 16 and Quarter-finals
knockout_stages = ['Round of 16', 'Quarter-finals']
knockout_matches = matches[matches['stage'].isin(knockout_stages)].copy()
knockout_matches = knockout_matches.dropna(subset=['kickoff_hour'])

print(f"Total Knockout matches (R16 + QF): {len(knockout_matches)}")

# Load events for extra time analysis
events = pd.read_csv('../Data/events_complete.csv')

# ===== BASIC ANALYSIS =====
print("\n" + "="*70)
print("KNOCKOUT ROUNDS KICKOFF DISTRIBUTION")
print("="*70)

# Create analysis dataset
ko_analysis = []

for _, match in knockout_matches.iterrows():
    match_id = match['match_id']
    kickoff_hour = match['kickoff_hour']
    stage = match['stage']
    
    # Check for extra time
    match_events = events[events['match_id'] == match_id]
    max_period = match_events['period'].max() if len(match_events) > 0 else 2
    has_extra_time = max_period > 2
    
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
        outcome = 'Draw (Extra Time)'
    
    ko_analysis.append({
        'match_id': match_id,
        'kickoff_hour': kickoff_hour,
        'stage': stage,
        'home_team': match['home_team_name'],
        'away_team': match['away_team_name'],
        'home_goals': ft_home_goals,
        'away_goals': ft_away_goals,
        'total_goals': total_goals,
        'goal_difference': goal_difference,
        'outcome': outcome,
        'has_extra_time': has_extra_time,
        'match_date': match['match_date']
    })

ko_df = pd.DataFrame(ko_analysis)

# Hour distribution
hour_distribution = ko_df['kickoff_hour'].value_counts().sort_index()

print("KNOCKOUT ROUNDS MATCHES BY HOUR:")
print("Hour" + " "*8 + "Matches" + " "*5 + "Percentage")
print("-" * 40)

total_ko_matches = len(ko_df)
for hour, count in hour_distribution.items():
    percentage = (count / total_ko_matches) * 100
    print(f"{hour:02d}:00 {count:>10} {percentage:>10.1f}%")

# ===== STAGE BREAKDOWN =====
print("\n" + "="*70)
print("STAGE DISTRIBUTION BY HOUR")
print("="*70)

stage_hour_cross = pd.crosstab(ko_df['stage'], ko_df['kickoff_hour'])
print("MATCHES BY STAGE AND HOUR:")
print(stage_hour_cross)

# ===== DETAILED ANALYSIS BY HOUR =====
print("\n" + "="*70)
print("DETAILED ANALYSIS BY KICKOFF HOUR")
print("="*70)

hour_stats = []

for hour in sorted(ko_df['kickoff_hour'].unique()):
    hour_matches = ko_df[ko_df['kickoff_hour'] == hour]
    
    # Basic stats
    num_matches = len(hour_matches)
    
    # Outcomes (knockout games can't end in draws in 90 minutes)
    extra_time_games = len(hour_matches[hour_matches['has_extra_time'] == True])
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
    extra_time_pct = (extra_time_games / num_matches) * 100
    home_win_pct = (home_wins / num_matches) * 100
    away_win_pct = (away_wins / num_matches) * 100
    
    # Goal categories
    zero_goals = len(hour_matches[hour_matches['total_goals'] == 0])
    low_scoring = len(hour_matches[hour_matches['total_goals'] <= 1])
    high_scoring = len(hour_matches[hour_matches['total_goals'] >= 4])
    
    # Stage distribution within hour
    r16_count = len(hour_matches[hour_matches['stage'] == 'Round of 16'])
    qf_count = len(hour_matches[hour_matches['stage'] == 'Quarter-finals'])
    
    hour_stats.append({
        'Hour': int(hour),
        'Matches': num_matches,
        'R16': r16_count,
        'QF': qf_count,
        'Extra_Time': extra_time_games,
        'Extra_Time_%': extra_time_pct,
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
    print("-" * 50)
    print(f"Stage Breakdown:")
    print(f"  Round of 16: {stats['R16']} matches")
    print(f"  Quarter-finals: {stats['QF']} matches")
    
    print(f"Match Duration:")
    print(f"  Extra Time: {stats['Extra_Time']} ({stats['Extra_Time_%']:.1f}%)")
    print(f"  90 Minutes: {stats['Matches'] - stats['Extra_Time']} ({100 - stats['Extra_Time_%']:.1f}%)")
    
    print(f"Outcomes:")
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

# ===== STAGE-SPECIFIC ANALYSIS =====
print("\n" + "="*70)
print("STAGE-SPECIFIC ANALYSIS BY HOUR")
print("="*70)

# Round of 16 by hour
print("ROUND OF 16 BY HOUR:")
r16_matches = ko_df[ko_df['stage'] == 'Round of 16']
r16_hour_stats = []

for hour in sorted(r16_matches['kickoff_hour'].unique()):
    hour_r16 = r16_matches[r16_matches['kickoff_hour'] == hour]
    
    avg_goals = hour_r16['total_goals'].mean()
    extra_time_pct = (hour_r16['has_extra_time'].sum() / len(hour_r16)) * 100
    home_win_pct = (len(hour_r16[hour_r16['outcome'] == 'Home Win']) / len(hour_r16)) * 100
    
    print(f"  {hour:02d}:00: {len(hour_r16)} matches - {avg_goals:.2f} goals/match, {extra_time_pct:.1f}% extra time, {home_win_pct:.1f}% home wins")
    
    r16_hour_stats.append({
        'hour': hour,
        'matches': len(hour_r16),
        'avg_goals': avg_goals,
        'extra_time_pct': extra_time_pct
    })

# Quarter-finals by hour
print("\nQUARTER-FINALS BY HOUR:")
qf_matches = ko_df[ko_df['stage'] == 'Quarter-finals']
qf_hour_stats = []

for hour in sorted(qf_matches['kickoff_hour'].unique()):
    hour_qf = qf_matches[qf_matches['kickoff_hour'] == hour]
    
    avg_goals = hour_qf['total_goals'].mean()
    extra_time_pct = (hour_qf['has_extra_time'].sum() / len(hour_qf)) * 100
    home_win_pct = (len(hour_qf[hour_qf['outcome'] == 'Home Win']) / len(hour_qf)) * 100
    
    print(f"  {hour:02d}:00: {len(hour_qf)} matches - {avg_goals:.2f} goals/match, {extra_time_pct:.1f}% extra time, {home_win_pct:.1f}% home wins")
    
    qf_hour_stats.append({
        'hour': hour,
        'matches': len(hour_qf),
        'avg_goals': avg_goals,
        'extra_time_pct': extra_time_pct
    })

# ===== COMPARATIVE ANALYSIS =====
print("\n" + "="*70)
print("COMPARATIVE ANALYSIS ACROSS HOURS")
print("="*70)

stats_df = pd.DataFrame(hour_stats)

# Find patterns
if len(stats_df) > 1:
    highest_scoring_hour = stats_df.loc[stats_df['Avg_Goals'].idxmax(), 'Hour']
    highest_scoring_avg = stats_df['Avg_Goals'].max()
    
    lowest_scoring_hour = stats_df.loc[stats_df['Avg_Goals'].idxmin(), 'Hour']
    lowest_scoring_avg = stats_df['Avg_Goals'].min()
    
    most_extra_time_hour = stats_df.loc[stats_df['Extra_Time_%'].idxmax(), 'Hour']
    most_extra_time_pct = stats_df['Extra_Time_%'].max()
    
    least_extra_time_hour = stats_df.loc[stats_df['Extra_Time_%'].idxmin(), 'Hour']
    least_extra_time_pct = stats_df['Extra_Time_%'].min()
    
    print("COMPARATIVE RANKINGS:")
    print(f"Highest scoring: {highest_scoring_hour:02d}:00 ({highest_scoring_avg:.2f} goals/match)")
    print(f"Lowest scoring: {lowest_scoring_hour:02d}:00 ({lowest_scoring_avg:.2f} goals/match)")
    print(f"Most extra time: {most_extra_time_hour:02d}:00 ({most_extra_time_pct:.1f}%)")
    print(f"Least extra time: {least_extra_time_hour:02d}:00 ({least_extra_time_pct:.1f}%)")
    
    # Variation analysis
    goals_range = highest_scoring_avg - lowest_scoring_avg
    extra_time_range = most_extra_time_pct - least_extra_time_pct
    
    print(f"\nVARIATION ANALYSIS:")
    print(f"Goals per match range: {goals_range:.2f} (difference between highest and lowest)")
    print(f"Extra time percentage range: {extra_time_range:.1f} percentage points")
    
    # Home advantage analysis
    print(f"\nHOME ADVANTAGE BY HOUR:")
    for _, stats in stats_df.iterrows():
        home_advantage = stats['Home_Win_%'] - stats['Away_Win_%']
        print(f"{stats['Hour']:02d}:00: Home {stats['Home_Win_%']:.1f}% vs Away {stats['Away_Win_%']:.1f}% (Advantage: {home_advantage:+.1f}%)")
else:
    print("Only one kickoff hour found - no comparison possible")

# ===== KNOCKOUT PRESSURE ANALYSIS =====
print("\n" + "="*70)
print("KNOCKOUT PRESSURE ANALYSIS")
print("="*70)

# Overall knockout stats
total_extra_time = ko_df['has_extra_time'].sum()
overall_extra_time_pct = (total_extra_time / total_ko_matches) * 100
overall_avg_goals = ko_df['total_goals'].mean()

print(f"OVERALL KNOCKOUT ROUNDS:")
print(f"Total matches: {total_ko_matches}")
print(f"Extra time matches: {total_extra_time} ({overall_extra_time_pct:.1f}%)")
print(f"Average goals: {overall_avg_goals:.2f}")

# Compare with Group Stage
group_stage = matches[matches['stage'] == 'Group Stage']
group_stage = group_stage.dropna(subset=['kickoff_hour'])

gs_avg_goals = ((group_stage['home_score'].fillna(0) + group_stage['away_score'].fillna(0)).sum() / len(group_stage))

print(f"\nCOMPARISON WITH GROUP STAGE:")
print(f"Group Stage avg goals: {gs_avg_goals:.2f}")
print(f"Knockout avg goals: {overall_avg_goals:.2f}")
print(f"Difference: {overall_avg_goals - gs_avg_goals:+.2f} goals per match")

# ===== SAVE RESULTS =====
print("\n" + "="*70)
print("SAVING RESULTS")
print("="*70)

# Save detailed analysis
ko_df.to_csv('knockout_rounds_by_hour_detailed.csv', index=False)
stats_df.to_csv('knockout_hour_statistics.csv', index=False)

print("Files saved:")
print("- knockout_rounds_by_hour_detailed.csv")
print("- knockout_hour_statistics.csv")

print(f"\n=== KNOCKOUT ROUNDS HOUR ANALYSIS COMPLETE ===")
if len(stats_df) > 1:
    print(f"Key Finding: {highest_scoring_hour:02d}:00 most attacking ({highest_scoring_avg:.2f} goals)")
    print(f"Pressure Impact: {extra_time_range:.1f}% difference in extra time rates")
    print(f"Elimination Effect: {overall_extra_time_pct:.1f}% of knockout games went to extra time")
else:
    print(f"Key Finding: Knockout rounds concentrated in single time slot")
    print(f"Elimination Effect: {overall_extra_time_pct:.1f}% of games went to extra time") 