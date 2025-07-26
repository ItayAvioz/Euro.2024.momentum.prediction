#!/usr/bin/env python3
import pandas as pd
import ast

# Load data
print("Loading data...")
events = pd.read_csv('Data/events_complete.csv', low_memory=False)
matches = pd.read_csv('Data/matches_complete.csv')

# Get Quarter-finals matches only
qf_matches = matches[matches['stage'] == 'Quarter-finals']
print(f"Quarter-finals: {len(qf_matches)} games")

# Get shot events for Quarter-finals
shot_events = events[events['type'].astype(str).str.contains('Shot', na=False)]
qf_shots = shot_events[shot_events['match_id'].isin(qf_matches['match_id'])]
print(f"Total shots in Quarter-finals: {len(qf_shots)}")

# Analyze shot outcomes
on_target = 0
goals = 0

for idx, shot in qf_shots.iterrows():
    try:
        shot_dict = ast.literal_eval(str(shot['shot']))
        outcome = shot_dict.get('outcome', {})
        outcome_id = outcome.get('id', 0)
        outcome_name = str(outcome.get('name', '')).lower()
        
        # Check if on target (Goal, Saved, Post/Bar)
        if (outcome_id in [97, 100, 101] or 
            'goal' in outcome_name or 
            'saved' in outcome_name or 
            'post' in outcome_name or 
            'bar' in outcome_name):
            on_target += 1
            
        # Check if goal
        if outcome_id == 97 or 'goal' in outcome_name:
            goals += 1
            
    except:
        pass

print(f"Shots on target in Quarter-finals: {on_target}")
print(f"Goals in Quarter-finals: {goals}")

# Calculate actual playing time (3 out of 4 games went to extra time)
regular_games = 1  # 1 game in regular time
extra_time_games = 3  # 3 games to extra time

total_minutes = (regular_games * 90) + (extra_time_games * 120)
print(f"Total actual minutes: {total_minutes}")

# Calculate 90-minute equivalent
minutes_90_equivalent = total_minutes / 90
print(f"90-minute equivalent: {minutes_90_equivalent:.1f}")

# Calculate normalized statistics
shots_per_90min = len(qf_shots) / minutes_90_equivalent
shots_on_target_per_90min = on_target / minutes_90_equivalent
goals_per_90min = goals / minutes_90_equivalent

print(f"\nQUARTER-FINALS SHOT STATISTICS (NORMALIZED TO 90 MINUTES):")
print(f"========================================================")
print(f"Total Shots: {len(qf_shots)}")
print(f"Shots on Target: {on_target}")
print(f"Goals: {goals}")
print(f"Shot Accuracy: {(on_target/len(qf_shots)*100):.1f}%")
print(f"Conversion Rate: {(goals/len(qf_shots)*100):.1f}%")
print(f"")
print(f"NORMALIZED PER 90 MINUTES:")
print(f"Shots per 90min: {shots_per_90min:.2f}")
print(f"Shots on Target per 90min: {shots_on_target_per_90min:.2f}")
print(f"Goals per 90min: {goals_per_90min:.2f}") 