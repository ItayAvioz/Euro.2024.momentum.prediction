import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ast
from datetime import datetime

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

print("=== EURO 2024 KICKOFF TIME ANALYSIS ===")
print("Loading and processing data...")

# Load the data
events = pd.read_csv('../Data/events_complete.csv')
matches = pd.read_csv('../Data/matches_complete.csv')

print(f"Total events: {len(events):,}")
print(f"Total matches: {len(matches):,}")

# Parse event types and shot outcomes
def extract_type_name(type_str):
    try:
        if pd.isna(type_str):
            return None
        type_dict = ast.literal_eval(str(type_str))
        return type_dict.get('name', None)
    except:
        return str(type_str)

def extract_shot_outcome(shot_str):
    try:
        if pd.isna(shot_str):
            return None
        shot_dict = ast.literal_eval(str(shot_str))
        outcome = shot_dict.get('outcome', {})
        if isinstance(outcome, dict):
            return outcome.get('id', None)
        return None
    except:
        return None

events['type_name'] = events['type'].apply(extract_type_name)
events['shot_outcome_id'] = events['shot'].apply(extract_shot_outcome)

# ===== PROCESS KICKOFF TIMES =====
print("\n" + "="*80)
print("PROCESSING KICKOFF TIMES")
print("="*80)

# Parse kickoff times
def extract_kickoff_hour(kick_off_str):
    try:
        if pd.isna(kick_off_str):
            return None
        # Extract hour from format like "22:00:00.000"
        hour_part = kick_off_str.split(':')[0]
        return int(hour_part)
    except:
        return None

matches['kickoff_hour'] = matches['kick_off'].apply(extract_kickoff_hour)

print("Sample kickoff times:")
print(matches[['kick_off', 'kickoff_hour']].head(10))

# Remove matches without kickoff time
matches_with_time = matches.dropna(subset=['kickoff_hour']).copy()
print(f"\nMatches with kickoff times: {len(matches_with_time)}")

# ===== ANALYZE MATCHES BY KICKOFF TIME =====
print("\n" + "="*80)
print("ANALYZING MATCHES BY KICKOFF TIME")
print("="*80)

kickoff_analysis = []

for _, match in matches_with_time.iterrows():
    match_id = match['match_id']
    match_events = events[events['match_id'] == match_id].copy()
    
    if len(match_events) == 0:
        continue
    
    # Get match details
    kickoff_hour = match['kickoff_hour']
    stage = match['stage']
    home_team_id = match['home_team_id'] 
    away_team_id = match['away_team_id']
    
    # Get final scores
    ft_home_goals = int(match['home_score']) if pd.notna(match['home_score']) else 0
    ft_away_goals = int(match['away_score']) if pd.notna(match['away_score']) else 0
    
    # Calculate totals and outcome
    total_goals = ft_home_goals + ft_away_goals
    goal_difference = abs(ft_home_goals - ft_away_goals)
    
    if ft_home_goals > ft_away_goals:
        outcome = 'Home Win'
    elif ft_away_goals > ft_home_goals:
        outcome = 'Away Win'
    else:
        outcome = 'Draw'
    
    # Check for extra time
    max_period = match_events['period'].max()
    has_extra_time = max_period > 2
    
    kickoff_analysis.append({
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

# Create DataFrame
kickoff_df = pd.DataFrame(kickoff_analysis)

print(f"Successfully analyzed {len(kickoff_df)} matches with kickoff times")

# ===== KICKOFF TIME DISTRIBUTION =====
print("\n" + "="*80)
print("KICKOFF TIME DISTRIBUTION")
print("="*80)

# Overall distribution by hour
hour_distribution = kickoff_df['kickoff_hour'].value_counts().sort_index()

print("MATCHES BY KICKOFF HOUR:")
print("Hour" + " "*8 + "Matches" + " "*5 + "Percentage")
print("-" * 40)

total_matches = len(kickoff_df)
for hour, count in hour_distribution.items():
    percentage = (count / total_matches) * 100
    print(f"{hour:02d}:00 {count:>10} {percentage:>10.1f}%")

# ===== SIMULTANEOUS GAMES ANALYSIS =====
print("\n" + "="*80)
print("SIMULTANEOUS GAMES ANALYSIS")
print("="*80)

# Group by date and hour to find simultaneous games
kickoff_df['date_hour'] = kickoff_df['match_date'] + '_' + kickoff_df['kickoff_hour'].astype(str)
simultaneous_groups = kickoff_df.groupby('date_hour').size().reset_index(name='num_matches')

print("SIMULTANEOUS GAMES DISTRIBUTION:")
print("Simultaneous Matches" + " "*5 + "Occurrences" + " "*5 + "Total Matches")
print("-" * 60)

for num_matches, count in simultaneous_groups['num_matches'].value_counts().sort_index().items():
    total_in_slots = num_matches * count
    print(f"{num_matches:>17} {count:>15} {total_in_slots:>15}")

# Detailed simultaneous games
print(f"\nDETAILED SIMULTANEOUS GAMES:")
multi_match_slots = simultaneous_groups[simultaneous_groups['num_matches'] > 1].sort_values('num_matches', ascending=False)

for _, slot in multi_match_slots.head(10).iterrows():
    date_hour = slot['date_hour']
    num_matches = slot['num_matches']
    slot_matches = kickoff_df[kickoff_df['date_hour'] == date_hour]
    
    date_part = date_hour.split('_')[0]
    hour_part = date_hour.split('_')[1]
    
    print(f"\n{date_part} at {hour_part}:00 - {num_matches} matches:")
    for _, match in slot_matches.iterrows():
        print(f"  {match['home_team']} vs {match['away_team']} ({match['stage']}) - {match['total_goals']} goals")

# ===== OUTCOMES BY KICKOFF TIME =====
print("\n" + "="*80)
print("MATCH OUTCOMES BY KICKOFF TIME")
print("="*80)

# Analyze outcomes by hour
hour_outcomes = []

for hour in sorted(kickoff_df['kickoff_hour'].unique()):
    hour_matches = kickoff_df[kickoff_df['kickoff_hour'] == hour]
    
    draws = len(hour_matches[hour_matches['outcome'] == 'Draw'])
    home_wins = len(hour_matches[hour_matches['outcome'] == 'Home Win'])
    away_wins = len(hour_matches[hour_matches['outcome'] == 'Away Win'])
    total_hour_matches = len(hour_matches)
    
    avg_goals = hour_matches['total_goals'].mean()
    avg_goal_diff = hour_matches['goal_difference'].mean()
    
    draw_pct = (draws / total_hour_matches) * 100
    home_win_pct = (home_wins / total_hour_matches) * 100
    away_win_pct = (away_wins / total_hour_matches) * 100
    
    hour_outcomes.append({
        'Hour': f"{hour:02d}:00",
        'Matches': total_hour_matches,
        'Draws': draws,
        'Draw_%': draw_pct,
        'Home_Wins': home_wins,
        'Home_Win_%': home_win_pct,
        'Away_Wins': away_wins,
        'Away_Win_%': away_win_pct,
        'Avg_Goals': avg_goals,
        'Avg_Goal_Diff': avg_goal_diff
    })

hour_summary = pd.DataFrame(hour_outcomes)

print("OUTCOMES BY KICKOFF HOUR:")
print("Hour" + " "*4 + "Matches" + " "*3 + "Draws%" + " "*4 + "Goals" + " "*4 + "Goal Diff")
print("-" * 60)

for _, row in hour_summary.iterrows():
    print(f"{row['Hour']:<8} {row['Matches']:>7} {row['Draw_%']:>8.1f}% {row['Avg_Goals']:>8.2f} {row['Avg_Goal_Diff']:>8.2f}")

# ===== STAGE-TIME DISTRIBUTION =====
print("\n" + "="*80)
print("STAGE DISTRIBUTION BY KICKOFF TIME")
print("="*80)

# Analyze stages by hour
stage_time_cross = pd.crosstab(kickoff_df['kickoff_hour'], kickoff_df['stage'])

print("MATCHES BY STAGE AND HOUR:")
print(stage_time_cross)

# Stage preferences by time
print(f"\nSTAGE TIME PREFERENCES:")
for stage in kickoff_df['stage'].unique():
    stage_matches = kickoff_df[kickoff_df['stage'] == stage]
    most_common_hour = stage_matches['kickoff_hour'].mode().iloc[0] if len(stage_matches) > 0 else None
    hour_distribution_stage = stage_matches['kickoff_hour'].value_counts().sort_index()
    
    print(f"\n{stage}:")
    print(f"  Most common hour: {most_common_hour:02d}:00")
    print(f"  Time distribution: {dict(hour_distribution_stage)}")

# ===== GOALS BY TIME ANALYSIS =====
print("\n" + "="*80)
print("GOAL SCORING BY TIME OF DAY")
print("="*80)

# Goals by hour analysis
goals_by_hour = []

for hour in sorted(kickoff_df['kickoff_hour'].unique()):
    hour_matches = kickoff_df[kickoff_df['kickoff_hour'] == hour]
    
    avg_goals = hour_matches['total_goals'].mean()
    total_goals = hour_matches['total_goals'].sum()
    num_matches = len(hour_matches)
    
    # Goal distribution
    zero_goals = len(hour_matches[hour_matches['total_goals'] == 0])
    low_goals = len(hour_matches[hour_matches['total_goals'] <= 1])
    high_goals = len(hour_matches[hour_matches['total_goals'] >= 4])
    
    goals_by_hour.append({
        'Hour': hour,
        'Matches': num_matches,
        'Total_Goals': total_goals,
        'Avg_Goals': avg_goals,
        'Zero_Goals': zero_goals,
        'Low_Scoring_%': (low_goals / num_matches) * 100,
        'High_Scoring_%': (high_goals / num_matches) * 100
    })

goals_summary = pd.DataFrame(goals_by_hour)

print("GOAL SCORING BY HOUR:")
print("Hour" + " "*4 + "Matches" + " "*3 + "Avg Goals" + " "*3 + "Low%" + " "*5 + "High%")
print("-" * 65)

for _, row in goals_summary.iterrows():
    print(f"{row['Hour']:02d}:00 {row['Matches']:>9} {row['Avg_Goals']:>10.2f} {row['Low_Scoring_%']:>8.1f}% {row['High_Scoring_%']:>8.1f}%")

# ===== VISUALIZATION =====
print("\n" + "="*80)
print("CREATING VISUALIZATIONS")
print("="*80)

fig = plt.figure(figsize=(20, 15))

# 1. Matches by kickoff hour
plt.subplot(2, 3, 1)
bars = plt.bar(hour_distribution.index, hour_distribution.values, alpha=0.8, color='lightblue')
plt.xlabel('Kickoff Hour')
plt.ylabel('Number of Matches')
plt.title('Match Distribution by Kickoff Hour')
plt.xticks(hour_distribution.index, [f"{h:02d}:00" for h in hour_distribution.index], rotation=45)
plt.grid(axis='y', alpha=0.3)

# Add value labels
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.2,
             f'{int(height)}', ha='center', va='bottom', fontsize=10)

# 2. Draw percentage by hour
plt.subplot(2, 3, 2)
plt.plot(hour_summary['Hour'].str[:2].astype(int), hour_summary['Draw_%'], 
         marker='o', linewidth=3, markersize=8, color='red')
plt.xlabel('Kickoff Hour')
plt.ylabel('Draw Percentage (%)')
plt.title('Draw Rate by Kickoff Time')
plt.xticks(hour_summary['Hour'].str[:2].astype(int), hour_summary['Hour'], rotation=45)
plt.grid(alpha=0.3)

# 3. Goals by hour
plt.subplot(2, 3, 3)
plt.bar(goals_summary['Hour'], goals_summary['Avg_Goals'], alpha=0.8, color='lightgreen')
plt.xlabel('Kickoff Hour')
plt.ylabel('Average Goals per Match')
plt.title('Goal Scoring by Kickoff Time')
plt.xticks(goals_summary['Hour'], [f"{h:02d}:00" for h in goals_summary['Hour']], rotation=45)
plt.grid(axis='y', alpha=0.3)

# 4. Stage-time heatmap
plt.subplot(2, 3, 4)
stage_time_pct = stage_time_cross.div(stage_time_cross.sum(axis=1), axis=0) * 100
sns.heatmap(stage_time_pct.T, annot=True, fmt='.1f', cmap='Blues',
            cbar_kws={'label': 'Percentage of Stage Matches (%)'})
plt.title('Stage Distribution by Kickoff Hour (%)')
plt.xlabel('Kickoff Hour')
plt.ylabel('Tournament Stage')

# 5. Simultaneous games
plt.subplot(2, 3, 5)
simul_counts = simultaneous_groups['num_matches'].value_counts().sort_index()
bars = plt.bar(simul_counts.index, simul_counts.values, alpha=0.8, color='orange')
plt.xlabel('Number of Simultaneous Matches')
plt.ylabel('Number of Time Slots')
plt.title('Simultaneous Games Distribution')
plt.grid(axis='y', alpha=0.3)

# Add value labels
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
             f'{int(height)}', ha='center', va='bottom', fontsize=10)

# 6. Outcome distribution by time
plt.subplot(2, 3, 6)
hours = hour_summary['Hour'].str[:2].astype(int)
draws = hour_summary['Draw_%']
home_wins = hour_summary['Home_Win_%']
away_wins = hour_summary['Away_Win_%']

width = 0.25
x = np.arange(len(hours))

bars1 = plt.bar(x - width, draws, width, label='Draws', alpha=0.8, color='yellow')
bars2 = plt.bar(x, home_wins, width, label='Home Wins', alpha=0.8, color='blue')
bars3 = plt.bar(x + width, away_wins, width, label='Away Wins', alpha=0.8, color='red')

plt.xlabel('Kickoff Hour')
plt.ylabel('Percentage of Matches (%)')
plt.title('Match Outcomes by Kickoff Time')
plt.xticks(x, [f"{h:02d}:00" for h in hours], rotation=45)
plt.legend()
plt.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('kickoff_time_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# ===== STATISTICAL INSIGHTS =====
print("\n" + "="*80)
print("STATISTICAL INSIGHTS")
print("="*80)

# Find patterns
peak_hour = hour_distribution.idxmax()
peak_matches = hour_distribution.max()

highest_goals_hour = goals_summary.loc[goals_summary['Avg_Goals'].idxmax(), 'Hour']
highest_goals_avg = goals_summary['Avg_Goals'].max()

highest_draw_hour = hour_summary.loc[hour_summary['Draw_%'].idxmax(), 'Hour']
highest_draw_rate = hour_summary['Draw_%'].max()

most_simultaneous = simultaneous_groups['num_matches'].max()
simultaneous_slots = len(simultaneous_groups[simultaneous_groups['num_matches'] > 1])

print(f"KICKOFF TIME PATTERNS:")
print(f"Peak scheduling hour: {peak_hour:02d}:00 ({peak_matches} matches)")
print(f"Highest scoring hour: {highest_goals_hour} ({highest_goals_avg:.2f} goals/match)")
print(f"Most draw-prone hour: {highest_draw_hour} ({highest_draw_rate:.1f}%)")

print(f"\nSCHEDULING INSIGHTS:")
print(f"Maximum simultaneous games: {most_simultaneous}")
print(f"Time slots with multiple games: {simultaneous_slots}")
print(f"Total unique kickoff hours: {len(hour_distribution)}")

# Time preferences by stage
group_stage_peak = kickoff_df[kickoff_df['stage'] == 'Group Stage']['kickoff_hour'].mode().iloc[0]
knockout_matches = kickoff_df[kickoff_df['stage'] != 'Group Stage']
knockout_peak = knockout_matches['kickoff_hour'].mode().iloc[0] if len(knockout_matches) > 0 else None

print(f"\nSTAGE TIME PREFERENCES:")
print(f"Group Stage peak: {group_stage_peak:02d}:00")
if knockout_peak:
    print(f"Knockout peak: {knockout_peak:02d}:00")

# ===== SAVE RESULTS =====
print("\n" + "="*80)
print("SAVING RESULTS")
print("="*80)

# Save detailed analysis
kickoff_df.to_csv('kickoff_time_detailed.csv', index=False)

# Save hour summary
hour_summary.to_csv('kickoff_hour_outcomes.csv', index=False)

# Save simultaneous games
simultaneous_groups.to_csv('simultaneous_games.csv', index=False)

print("Files saved:")
print("- kickoff_time_analysis.png")
print("- kickoff_time_detailed.csv")
print("- kickoff_hour_outcomes.csv")
print("- simultaneous_games.csv")

print(f"\n=== KICKOFF TIME ANALYSIS COMPLETE ===")
print(f"Peak hour: {peak_hour:02d}:00 with {peak_matches} matches")
print(f"Best scoring time: {highest_goals_hour} ({highest_goals_avg:.2f} goals)")
print(f"Most competitive time: {highest_draw_hour} ({highest_draw_rate:.1f}% draws)") 