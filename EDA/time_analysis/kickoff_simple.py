import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ast

print("=== EURO 2024 KICKOFF TIME ANALYSIS ===")

# Load the data
events = pd.read_csv('../Data/events_complete.csv')
matches = pd.read_csv('../Data/matches_complete.csv')

print(f"Total matches: {len(matches):,}")

# Parse kickoff times - format is "HH:MM:SS.mmm"
def extract_kickoff_hour(kick_off_str):
    try:
        if pd.isna(kick_off_str):
            return None
        hour_part = str(kick_off_str).split(':')[0]
        return int(hour_part)
    except:
        return None

matches['kickoff_hour'] = matches['kick_off'].apply(extract_kickoff_hour)
matches_with_time = matches.dropna(subset=['kickoff_hour']).copy()

print(f"Matches with kickoff times: {len(matches_with_time)}")

# ===== BASIC KICKOFF ANALYSIS =====
print("\n" + "="*60)
print("KICKOFF TIME DISTRIBUTION")
print("="*60)

kickoff_analysis = []

for _, match in matches_with_time.iterrows():
    match_id = match['match_id']
    kickoff_hour = match['kickoff_hour']
    stage = match['stage']
    
    # Get final scores
    ft_home_goals = int(match['home_score']) if pd.notna(match['home_score']) else 0
    ft_away_goals = int(match['away_score']) if pd.notna(match['away_score']) else 0
    
    total_goals = ft_home_goals + ft_away_goals
    
    if ft_home_goals > ft_away_goals:
        outcome = 'Home Win'
    elif ft_away_goals > ft_home_goals:
        outcome = 'Away Win'
    else:
        outcome = 'Draw'
    
    kickoff_analysis.append({
        'match_id': match_id,
        'kickoff_hour': kickoff_hour,
        'stage': stage,
        'home_team': match['home_team_name'],
        'away_team': match['away_team_name'],
        'total_goals': total_goals,
        'outcome': outcome,
        'match_date': match['match_date']
    })

kickoff_df = pd.DataFrame(kickoff_analysis)

# Overall distribution by hour
hour_distribution = kickoff_df['kickoff_hour'].value_counts().sort_index()

print("MATCHES BY KICKOFF HOUR:")
print("Hour" + " "*8 + "Matches" + " "*5 + "Percentage")
print("-" * 40)

total_matches = len(kickoff_df)
for hour, count in hour_distribution.items():
    percentage = (count / total_matches) * 100
    print(f"{hour:02d}:00 {count:>10} {percentage:>10.1f}%")

# ===== SIMULTANEOUS GAMES =====
print("\n" + "="*60)
print("SIMULTANEOUS GAMES")
print("="*60)

kickoff_df['date_hour'] = kickoff_df['match_date'] + '_' + kickoff_df['kickoff_hour'].astype(str)
simultaneous_groups = kickoff_df.groupby('date_hour').size().reset_index(name='num_matches')

print("SIMULTANEOUS GAMES DISTRIBUTION:")
for num_matches, count in simultaneous_groups['num_matches'].value_counts().sort_index().items():
    total_in_slots = num_matches * count
    print(f"{num_matches} simultaneous: {count} time slots ({total_in_slots} total matches)")

# Show simultaneous examples
multi_match_slots = simultaneous_groups[simultaneous_groups['num_matches'] > 1]
print(f"\nSIMULTANEOUS GAMES EXAMPLES:")
for _, slot in multi_match_slots.head(5).iterrows():
    date_hour = slot['date_hour']
    num_matches = slot['num_matches']
    slot_matches = kickoff_df[kickoff_df['date_hour'] == date_hour]
    
    date_part = date_hour.split('_')[0]
    hour_part = date_hour.split('_')[1]
    
    print(f"\n{date_part} at {hour_part}:00 ({num_matches} matches):")
    for _, match in slot_matches.iterrows():
        print(f"  {match['home_team']} vs {match['away_team']} - {match['total_goals']} goals, {match['outcome']}")

# ===== OUTCOMES BY TIME =====
print("\n" + "="*60)
print("OUTCOMES BY KICKOFF TIME")
print("="*60)

print("Hour" + " "*4 + "Matches" + " "*3 + "Draws" + " "*3 + "Draw%" + " "*4 + "Avg Goals")
print("-" * 55)

for hour in sorted(kickoff_df['kickoff_hour'].unique()):
    hour_matches = kickoff_df[kickoff_df['kickoff_hour'] == hour]
    
    draws = len(hour_matches[hour_matches['outcome'] == 'Draw'])
    total_hour_matches = len(hour_matches)
    avg_goals = hour_matches['total_goals'].mean()
    draw_pct = (draws / total_hour_matches) * 100
    
    print(f"{hour:02d}:00 {total_hour_matches:>9} {draws:>7} {draw_pct:>6.1f}% {avg_goals:>10.2f}")

# ===== STAGE PREFERENCES =====
print("\n" + "="*60)
print("STAGE TIME PREFERENCES")
print("="*60)

stage_time_cross = pd.crosstab(kickoff_df['stage'], kickoff_df['kickoff_hour'])
print("MATCHES BY STAGE AND HOUR:")
print(stage_time_cross)

print(f"\nMOST COMMON KICKOFF BY STAGE:")
for stage in kickoff_df['stage'].unique():
    stage_matches = kickoff_df[kickoff_df['stage'] == stage]
    most_common_hour = stage_matches['kickoff_hour'].mode().iloc[0] if len(stage_matches) > 0 else None
    stage_count = len(stage_matches)
    print(f"{stage}: {most_common_hour:02d}:00 (from {stage_count} matches)")

# ===== KEY INSIGHTS =====
print("\n" + "="*60)
print("KEY INSIGHTS")
print("="*60)

peak_hour = hour_distribution.idxmax()
peak_matches = hour_distribution.max()

# Goals by hour
goals_by_hour = kickoff_df.groupby('kickoff_hour')['total_goals'].agg(['mean', 'count']).reset_index()
highest_goals_hour = goals_by_hour.loc[goals_by_hour['mean'].idxmax(), 'kickoff_hour']
highest_goals_avg = goals_by_hour['mean'].max()

# Draws by hour
draws_by_hour = kickoff_df.groupby('kickoff_hour').apply(
    lambda x: (x['outcome'] == 'Draw').sum() / len(x) * 100
).reset_index(name='draw_pct')
highest_draw_hour = draws_by_hour.loc[draws_by_hour['draw_pct'].idxmax(), 'kickoff_hour']
highest_draw_rate = draws_by_hour['draw_pct'].max()

most_simultaneous = simultaneous_groups['num_matches'].max()
simultaneous_slots = len(simultaneous_groups[simultaneous_groups['num_matches'] > 1])

print(f"Peak scheduling: {peak_hour:02d}:00 with {peak_matches} matches ({(peak_matches/total_matches)*100:.1f}%)")
print(f"Highest scoring: {highest_goals_hour:02d}:00 with {highest_goals_avg:.2f} goals/match")
print(f"Most draw-prone: {highest_draw_hour:02d}:00 with {highest_draw_rate:.1f}% draws")
print(f"Max simultaneous: {most_simultaneous} matches in same time slot")
print(f"Simultaneous slots: {simultaneous_slots} time slots had multiple games")

# Stage insights
group_stage_matches = kickoff_df[kickoff_df['stage'] == 'Group Stage']
group_peak = group_stage_matches['kickoff_hour'].mode().iloc[0]
knockout_matches = kickoff_df[kickoff_df['stage'] != 'Group Stage']
knockout_peak = knockout_matches['kickoff_hour'].mode().iloc[0] if len(knockout_matches) > 0 else None

print(f"\nGroup Stage favorite: {group_peak:02d}:00")
if knockout_peak:
    print(f"Knockout favorite: {knockout_peak:02d}:00")

# Save results
kickoff_df.to_csv('kickoff_time_analysis_results.csv', index=False)
print(f"\nResults saved to: kickoff_time_analysis_results.csv")

print(f"\n=== ANALYSIS COMPLETE ===")
print(f"Tournament spread across {len(hour_distribution)} different kickoff hours")
print(f"Prime time dominance: {peak_hour:02d}:00 hosts {(peak_matches/total_matches)*100:.1f}% of matches") 