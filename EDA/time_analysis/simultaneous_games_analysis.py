import pandas as pd
import numpy as np

print("=== EURO 2024 SIMULTANEOUS GAMES DETAILED ANALYSIS ===")

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
matches_with_time = matches.dropna(subset=['kickoff_hour']).copy()

print(f"Total matches: {len(matches_with_time)}")

# Create analysis dataset
kickoff_analysis = []

for _, match in matches_with_time.iterrows():
    match_id = match['match_id']
    kickoff_hour = match['kickoff_hour']
    stage = match['stage']
    
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
    
    # Get match week for group stage
    match_week = match.get('match_week', None)
    
    kickoff_analysis.append({
        'match_id': match_id,
        'kickoff_hour': kickoff_hour,
        'stage': stage,
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

kickoff_df = pd.DataFrame(kickoff_analysis)

# ===== FIND SIMULTANEOUS GAMES =====
print("\n" + "="*80)
print("IDENTIFYING SIMULTANEOUS GAMES")
print("="*80)

# Group by date and hour to find simultaneous games
kickoff_df['date_hour'] = kickoff_df['match_date'] + '_' + kickoff_df['kickoff_hour'].astype(str)
simultaneous_groups = kickoff_df.groupby('date_hour').size().reset_index(name='num_matches')

# Get only the simultaneous slots (2 matches)
simultaneous_slots = simultaneous_groups[simultaneous_groups['num_matches'] == 2]

print(f"Found {len(simultaneous_slots)} time slots with 2 simultaneous matches")
print(f"Total matches in simultaneous slots: {len(simultaneous_slots) * 2}")

# ===== DETAILED ANALYSIS OF EACH SIMULTANEOUS SLOT =====
print("\n" + "="*80)
print("DETAILED ANALYSIS OF SIMULTANEOUS GAMES")
print("="*80)

simultaneous_details = []

for i, (_, slot) in enumerate(simultaneous_slots.iterrows(), 1):
    date_hour = slot['date_hour']
    date_part = date_hour.split('_')[0]
    hour_part = date_hour.split('_')[1]
    
    # Get the 2 matches in this slot
    slot_matches = kickoff_df[kickoff_df['date_hour'] == date_hour].copy()
    
    print(f"\n{i}. {date_part} at {hour_part}:00")
    print("-" * 50)
    
    # Analyze the pair
    match1 = slot_matches.iloc[0]
    match2 = slot_matches.iloc[1]
    
    # Stage analysis
    stages = slot_matches['stage'].unique()
    stage = stages[0] if len(stages) == 1 else "Mixed"
    
    # Match week for group stage
    match_weeks = slot_matches['match_week'].dropna().unique()
    match_week = match_weeks[0] if len(match_weeks) == 1 else None
    
    # Goals analysis
    total_goals_slot = slot_matches['total_goals'].sum()
    avg_goals_slot = slot_matches['total_goals'].mean()
    
    # Outcomes analysis
    draws = len(slot_matches[slot_matches['outcome'] == 'Draw'])
    decisive = len(slot_matches[slot_matches['outcome'] != 'Draw'])
    
    print(f"Stage: {stage}")
    if match_week and stage == 'Group Stage':
        print(f"Group Stage Matchday: {match_week}")
    
    print(f"Matches:")
    for _, match in slot_matches.iterrows():
        score_str = f"{match['home_goals']}-{match['away_goals']}"
        print(f"  {match['home_team']} vs {match['away_team']}: {score_str} ({match['outcome']}) - {match['total_goals']} goals")
    
    print(f"Slot Statistics:")
    print(f"  Total Goals: {total_goals_slot}")
    print(f"  Average Goals: {avg_goals_slot:.1f}")
    print(f"  Draws: {draws}/2 ({(draws/2)*100:.0f}%)")
    print(f"  Decisive: {decisive}/2 ({(decisive/2)*100:.0f}%)")
    
    # Store for summary
    simultaneous_details.append({
        'slot_id': i,
        'date': date_part,
        'hour': int(hour_part),
        'stage': stage,
        'match_week': match_week,
        'total_goals': total_goals_slot,
        'avg_goals': avg_goals_slot,
        'draws': draws,
        'decisive': decisive,
        'match1_home': match1['home_team'],
        'match1_away': match1['away_team'],
        'match1_score': f"{match1['home_goals']}-{match1['away_goals']}",
        'match1_outcome': match1['outcome'],
        'match2_home': match2['home_team'],
        'match2_away': match2['away_team'],
        'match2_score': f"{match2['home_goals']}-{match2['away_goals']}",
        'match2_outcome': match2['outcome']
    })

# ===== SUMMARY STATISTICS =====
print("\n" + "="*80)
print("SIMULTANEOUS GAMES SUMMARY STATISTICS")
print("="*80)

simultaneous_df = pd.DataFrame(simultaneous_details)

# Stage breakdown
stage_counts = simultaneous_df['stage'].value_counts()
print("STAGE DISTRIBUTION:")
for stage, count in stage_counts.items():
    pct = (count / len(simultaneous_df)) * 100
    print(f"{stage}: {count} slots ({pct:.1f}%)")

# Match week breakdown for Group Stage
group_stage_slots = simultaneous_df[simultaneous_df['stage'] == 'Group Stage']
if len(group_stage_slots) > 0:
    print(f"\nGROUP STAGE MATCHDAY DISTRIBUTION:")
    matchday_counts = group_stage_slots['match_week'].value_counts().sort_index()
    for matchday, count in matchday_counts.items():
        pct = (count / len(group_stage_slots)) * 100
        print(f"Matchday {matchday}: {count} slots ({pct:.1f}%)")

# Hour distribution
hour_counts = simultaneous_df['hour'].value_counts().sort_index()
print(f"\nKICKOFF HOUR DISTRIBUTION:")
for hour, count in hour_counts.items():
    pct = (count / len(simultaneous_df)) * 100
    print(f"{hour:02d}:00: {count} slots ({pct:.1f}%)")

# Goals statistics
total_goals_all = simultaneous_df['total_goals'].sum()
avg_goals_per_slot = simultaneous_df['avg_goals'].mean()
avg_goals_per_match = total_goals_all / (len(simultaneous_df) * 2)

print(f"\nGOALS STATISTICS:")
print(f"Total goals across all slots: {total_goals_all}")
print(f"Average goals per slot (2 matches): {avg_goals_per_slot:.2f}")
print(f"Average goals per individual match: {avg_goals_per_match:.2f}")

# Outcomes statistics
total_draws = simultaneous_df['draws'].sum()
total_decisive = simultaneous_df['decisive'].sum()
total_matches_simul = len(simultaneous_df) * 2

print(f"\nOUTCOME STATISTICS:")
print(f"Total draws: {total_draws}/{total_matches_simul} ({(total_draws/total_matches_simul)*100:.1f}%)")
print(f"Total decisive: {total_decisive}/{total_matches_simul} ({(total_decisive/total_matches_simul)*100:.1f}%)")

# Slot-level patterns
both_draws = len(simultaneous_df[simultaneous_df['draws'] == 2])
both_decisive = len(simultaneous_df[simultaneous_df['decisive'] == 2])
mixed = len(simultaneous_df[simultaneous_df['draws'] == 1])

print(f"\nSLOT PATTERNS:")
print(f"Both matches draws: {both_draws} slots ({(both_draws/len(simultaneous_df))*100:.1f}%)")
print(f"Both matches decisive: {both_decisive} slots ({(both_decisive/len(simultaneous_df))*100:.1f}%)")
print(f"Mixed (1 draw, 1 decisive): {mixed} slots ({(mixed/len(simultaneous_df))*100:.1f}%)")

# ===== COMPARISON WITH NON-SIMULTANEOUS GAMES =====
print("\n" + "="*80)
print("COMPARISON: SIMULTANEOUS vs INDIVIDUAL GAMES")
print("="*80)

# Get non-simultaneous games
non_simultaneous_dates = simultaneous_groups[simultaneous_groups['num_matches'] == 1]['date_hour'].tolist()
non_simultaneous_matches = kickoff_df[kickoff_df['date_hour'].isin(non_simultaneous_dates)]

# Statistics for non-simultaneous
non_simul_draws = len(non_simultaneous_matches[non_simultaneous_matches['outcome'] == 'Draw'])
non_simul_total = len(non_simultaneous_matches)
non_simul_draw_pct = (non_simul_draws / non_simul_total) * 100
non_simul_avg_goals = non_simultaneous_matches['total_goals'].mean()

print("COMPARATIVE STATISTICS:")
print(f"Simultaneous matches:")
print(f"  Total matches: {total_matches_simul}")
print(f"  Draw rate: {(total_draws/total_matches_simul)*100:.1f}%")
print(f"  Average goals: {avg_goals_per_match:.2f}")

print(f"Individual matches:")
print(f"  Total matches: {non_simul_total}")
print(f"  Draw rate: {non_simul_draw_pct:.1f}%")
print(f"  Average goals: {non_simul_avg_goals:.2f}")

print(f"\nDIFFERENCES:")
draw_diff = (total_draws/total_matches_simul)*100 - non_simul_draw_pct
goals_diff = avg_goals_per_match - non_simul_avg_goals
print(f"Draw rate difference: {draw_diff:+.1f} percentage points")
print(f"Goals difference: {goals_diff:+.2f} goals per match")

# ===== SAVE RESULTS =====
print("\n" + "="*80)
print("SAVING RESULTS")
print("="*80)

simultaneous_df.to_csv('simultaneous_games_detailed.csv', index=False)
print("Detailed results saved to: simultaneous_games_detailed.csv")

print(f"\n=== SIMULTANEOUS GAMES ANALYSIS COMPLETE ===")
print(f"Key Finding: {len(group_stage_slots)} of 6 slots were Group Stage Matchday {group_stage_slots['match_week'].mode().iloc[0] if len(group_stage_slots) > 0 else 'N/A'}")
print(f"Most common pattern: {max(both_draws, both_decisive, mixed)} slots with {'both draws' if both_draws == max(both_draws, both_decisive, mixed) else 'both decisive' if both_decisive == max(both_draws, both_decisive, mixed) else 'mixed outcomes'}")
print(f"Scheduling strategy: {(len(group_stage_slots)/len(simultaneous_df))*100:.0f}% of simultaneous slots used for Group Stage coordination") 