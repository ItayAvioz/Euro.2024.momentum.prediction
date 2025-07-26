import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ast

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

print("=== EURO 2024 GOAL DIFFERENCE BY STAGES ANALYSIS ===")
print("Loading and processing data...")

# Load the data
events = pd.read_csv('../Data/events_complete.csv')
matches = pd.read_csv('../Data/matches_complete.csv')

print(f"Total events: {len(events):,}")
print(f"Total matches: {len(matches):,}")

# Parse event types
def extract_type_name(type_str):
    try:
        if pd.isna(type_str):
            return None
        type_dict = ast.literal_eval(str(type_str))
        return type_dict.get('name', None)
    except:
        return str(type_str)

events['type_name'] = events['type'].apply(extract_type_name)

# Parse shot outcomes to identify goals
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

events['shot_outcome_id'] = events['shot'].apply(extract_shot_outcome)

# ===== ANALYZE BY TOURNAMENT STAGES =====
print("\n" + "="*80)
print("ANALYZING GOAL DIFFERENCES BY TOURNAMENT STAGE")
print("="*80)

stage_analysis = []

for _, match in matches.iterrows():
    match_id = match['match_id']
    match_events = events[events['match_id'] == match_id].copy()
    
    if len(match_events) == 0:
        continue
    
    # Get team information
    home_team_id = match['home_team_id'] 
    away_team_id = match['away_team_id']
    stage = match['stage']
    
    # Count goals by period using shot outcome ID 97 (Goal)
    goal_events = match_events[(match_events['type_name'] == 'Shot') & 
                              (match_events['shot_outcome_id'] == 97)]
    
    # First half goals
    p1_goals = goal_events[goal_events['period'] == 1]
    ht_home_goals = len(p1_goals[p1_goals['team_id'] == home_team_id])
    ht_away_goals = len(p1_goals[p1_goals['team_id'] == away_team_id])
    
    # Full-time goals
    ft_home_goals = int(match['home_score']) if pd.notna(match['home_score']) else 0
    ft_away_goals = int(match['away_score']) if pd.notna(match['away_score']) else 0
    
    # Calculate goal differences
    ht_goal_diff = abs(ht_home_goals - ht_away_goals)
    ft_goal_diff = abs(ft_home_goals - ft_away_goals)
    
    # Check for extra time
    max_period = match_events['period'].max()
    has_extra_time = max_period > 2
    
    stage_analysis.append({
        'match_id': match_id,
        'stage': stage,
        'home_team': match['home_team_name'],
        'away_team': match['away_team_name'],
        'ht_home': ht_home_goals,
        'ht_away': ht_away_goals,
        'ht_goal_diff': ht_goal_diff,
        'ft_home': ft_home_goals,
        'ft_away': ft_away_goals,
        'ft_goal_diff': ft_goal_diff,
        'total_goals': ft_home_goals + ft_away_goals,
        'has_extra_time': has_extra_time
    })

# Create DataFrame
stage_df = pd.DataFrame(stage_analysis)

print(f"Successfully analyzed {len(stage_df)} matches across {stage_df['stage'].nunique()} stages")

# ===== STAGE-BY-STAGE ANALYSIS =====
print("\n" + "="*80)
print("GOAL DIFFERENCE ANALYSIS BY STAGE")
print("="*80)

# Group by stage
stages = ['Group Stage', 'Round of 16', 'Quarter-finals', 'Semi-finals', 'Final']
stage_stats = []

for stage in stages:
    stage_matches = stage_df[stage_df['stage'] == stage]
    
    if len(stage_matches) == 0:
        continue
    
    # Basic statistics
    num_matches = len(stage_matches)
    
    # Halftime statistics
    ht_draws = len(stage_matches[stage_matches['ht_goal_diff'] == 0])
    ht_1_goal = len(stage_matches[stage_matches['ht_goal_diff'] == 1])
    ht_2_goal = len(stage_matches[stage_matches['ht_goal_diff'] == 2])
    ht_3plus_goal = len(stage_matches[stage_matches['ht_goal_diff'] >= 3])
    
    # Full-time statistics
    ft_draws = len(stage_matches[stage_matches['ft_goal_diff'] == 0])
    ft_1_goal = len(stage_matches[stage_matches['ft_goal_diff'] == 1])
    ft_2_goal = len(stage_matches[stage_matches['ft_goal_diff'] == 2])
    ft_3plus_goal = len(stage_matches[stage_matches['ft_goal_diff'] >= 3])
    
    # Averages
    avg_ht_diff = stage_matches['ht_goal_diff'].mean()
    avg_ft_diff = stage_matches['ft_goal_diff'].mean()
    avg_total_goals = stage_matches['total_goals'].mean()
    
    # Extra time
    extra_time_matches = stage_matches['has_extra_time'].sum()
    
    stage_stats.append({
        'Stage': stage,
        'Matches': num_matches,
        'HT_Draws': ht_draws,
        'HT_Draws_%': (ht_draws/num_matches)*100,
        'HT_1Goal': ht_1_goal,
        'HT_1Goal_%': (ht_1_goal/num_matches)*100,
        'HT_2+Goal': ht_2_goal + ht_3plus_goal,
        'HT_2+Goal_%': ((ht_2_goal + ht_3plus_goal)/num_matches)*100,
        'FT_Draws': ft_draws,
        'FT_Draws_%': (ft_draws/num_matches)*100,
        'FT_1Goal': ft_1_goal,
        'FT_1Goal_%': (ft_1_goal/num_matches)*100,
        'FT_2+Goal': ft_2_goal + ft_3plus_goal,
        'FT_2+Goal_%': ((ft_2_goal + ft_3plus_goal)/num_matches)*100,
        'Avg_HT_Diff': avg_ht_diff,
        'Avg_FT_Diff': avg_ft_diff,
        'Avg_Goals': avg_total_goals,
        'Extra_Time': extra_time_matches,
        'Extra_Time_%': (extra_time_matches/num_matches)*100
    })

# Create summary DataFrame
stage_summary = pd.DataFrame(stage_stats)

print("GOAL DIFFERENCE DISTRIBUTION BY STAGE:")
print("="*60)

for _, row in stage_summary.iterrows():
    print(f"\n{row['Stage'].upper()} ({row['Matches']} matches):")
    print(f"  Halftime Draws: {row['HT_Draws']} ({row['HT_Draws_%']:.1f}%)")
    print(f"  Full-time Draws: {row['FT_Draws']} ({row['FT_Draws_%']:.1f}%)")
    print(f"  1-Goal Games (FT): {row['FT_1Goal']} ({row['FT_1Goal_%']:.1f}%)")
    print(f"  2+ Goal Margins (FT): {row['FT_2+Goal']} ({row['FT_2+Goal_%']:.1f}%)")
    print(f"  Avg Goal Difference: HT {row['Avg_HT_Diff']:.2f} -> FT {row['Avg_FT_Diff']:.2f}")
    print(f"  Avg Total Goals: {row['Avg_Goals']:.2f}")
    if row['Extra_Time'] > 0:
        print(f"  Extra Time: {row['Extra_Time']} matches ({row['Extra_Time_%']:.1f}%)")

# ===== COMPETITIVENESS ANALYSIS =====
print("\n" + "="*80)
print("COMPETITIVENESS TRENDS ACROSS STAGES")
print("="*80)

print("DRAW PERCENTAGE EVOLUTION:")
print("Stage" + " "*15 + "HT Draws" + " "*5 + "FT Draws" + " "*5 + "Change")
print("-" * 60)
for _, row in stage_summary.iterrows():
    change = row['FT_Draws_%'] - row['HT_Draws_%']
    print(f"{row['Stage']:<20} {row['HT_Draws_%']:>6.1f}%   {row['FT_Draws_%']:>6.1f}%   {change:>+6.1f}%")

print(f"\nCLOSE GAMES (0-1 Goal Difference at FT):")
for _, row in stage_summary.iterrows():
    close_games = row['FT_Draws_%'] + row['FT_1Goal_%']
    print(f"{row['Stage']:<20} {close_games:>6.1f}%")

print(f"\nDECISIVE GAMES (2+ Goal Difference at FT):")
for _, row in stage_summary.iterrows():
    print(f"{row['Stage']:<20} {row['FT_2+Goal_%']:>6.1f}%")

# ===== VISUALIZATION =====
print("\n" + "="*80)
print("CREATING VISUALIZATIONS")
print("="*80)

fig = plt.figure(figsize=(20, 15))

# 1. Goal difference evolution by stage
plt.subplot(2, 3, 1)
x = np.arange(len(stage_summary))
width = 0.35

bars1 = plt.bar(x - width/2, stage_summary['Avg_HT_Diff'], width, 
                label='Halftime', alpha=0.8, color='skyblue')
bars2 = plt.bar(x + width/2, stage_summary['Avg_FT_Diff'], width, 
                label='Full-time', alpha=0.8, color='lightcoral')

plt.xlabel('Tournament Stage')
plt.ylabel('Average Goal Difference')
plt.title('Average Goal Difference by Stage')
plt.xticks(x, stage_summary['Stage'], rotation=45, ha='right')
plt.legend()
plt.grid(axis='y', alpha=0.3)

# Add value labels
for bar in bars1:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
             f'{height:.2f}', ha='center', va='bottom', fontsize=9)
for bar in bars2:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
             f'{height:.2f}', ha='center', va='bottom', fontsize=9)

# 2. Draw percentage by stage
plt.subplot(2, 3, 2)
bars1 = plt.bar(x - width/2, stage_summary['HT_Draws_%'], width, 
                label='Halftime', alpha=0.8, color='skyblue')
bars2 = plt.bar(x + width/2, stage_summary['FT_Draws_%'], width, 
                label='Full-time', alpha=0.8, color='lightcoral')

plt.xlabel('Tournament Stage')
plt.ylabel('Draw Percentage (%)')
plt.title('Draw Percentage by Stage')
plt.xticks(x, stage_summary['Stage'], rotation=45, ha='right')
plt.legend()
plt.grid(axis='y', alpha=0.3)

# 3. Close vs Decisive games
plt.subplot(2, 3, 3)
close_games = stage_summary['FT_Draws_%'] + stage_summary['FT_1Goal_%']
decisive_games = stage_summary['FT_2+Goal_%']

bars1 = plt.bar(x, close_games, label='Close Games (0-1 goal)', alpha=0.8, color='orange')
bars2 = plt.bar(x, decisive_games, bottom=close_games, label='Decisive Games (2+ goals)', alpha=0.8, color='red')

plt.xlabel('Tournament Stage')
plt.ylabel('Percentage of Matches (%)')
plt.title('Game Competitiveness by Stage')
plt.xticks(x, stage_summary['Stage'], rotation=45, ha='right')
plt.legend()
plt.grid(axis='y', alpha=0.3)

# 4. Goals and extra time by stage
plt.subplot(2, 3, 4)
ax1 = plt.gca()
bars1 = ax1.bar(x, stage_summary['Avg_Goals'], alpha=0.7, color='lightgreen')
ax1.set_xlabel('Tournament Stage')
ax1.set_ylabel('Average Goals per Match', color='green')
ax1.tick_params(axis='y', labelcolor='green')
plt.xticks(x, stage_summary['Stage'], rotation=45, ha='right')

ax2 = ax1.twinx()
line = ax2.plot(x, stage_summary['Extra_Time_%'], color='red', marker='o', linewidth=2, markersize=8, label='Extra Time %')
ax2.set_ylabel('Extra Time Percentage (%)', color='red')
ax2.tick_params(axis='y', labelcolor='red')

plt.title('Goals per Match & Extra Time by Stage')
plt.grid(axis='y', alpha=0.3)

# 5. Detailed stage comparison heatmap
plt.subplot(2, 3, 5)
heatmap_data = stage_summary[['HT_Draws_%', 'FT_Draws_%', 'FT_1Goal_%', 'FT_2+Goal_%', 'Extra_Time_%']].T
heatmap_data.columns = [stage[:8] + '..' if len(stage) > 8 else stage for stage in stage_summary['Stage']]

sns.heatmap(heatmap_data, annot=True, fmt='.1f', cmap='RdYlBu_r', 
            cbar_kws={'label': 'Percentage (%)'})
plt.title('Match Characteristics by Stage (%)')
plt.ylabel('Match Type')

# 6. Individual stage distributions
plt.subplot(2, 3, 6)
# Create stacked bar chart for goal difference distributions
stages_short = [stage[:8] + '..' if len(stage) > 8 else stage for stage in stage_summary['Stage']]

draws = stage_summary['FT_Draws_%']
one_goal = stage_summary['FT_1Goal_%'] 
two_plus = stage_summary['FT_2+Goal_%']

bars1 = plt.bar(stages_short, draws, label='Draws (0)', alpha=0.8, color='lightblue')
bars2 = plt.bar(stages_short, one_goal, bottom=draws, label='1 Goal', alpha=0.8, color='orange')
bars3 = plt.bar(stages_short, two_plus, bottom=draws+one_goal, label='2+ Goals', alpha=0.8, color='red')

plt.xlabel('Tournament Stage')
plt.ylabel('Percentage of Matches (%)')
plt.title('Goal Difference Distribution by Stage')
plt.xticks(rotation=45, ha='right')
plt.legend()
plt.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('goal_difference_by_stages_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# ===== STATISTICAL INSIGHTS =====
print("\n" + "="*80)
print("STATISTICAL INSIGHTS")
print("="*80)

# Most competitive stage
most_draws_stage = stage_summary.loc[stage_summary['FT_Draws_%'].idxmax(), 'Stage']
most_close_stage_idx = (stage_summary['FT_Draws_%'] + stage_summary['FT_1Goal_%']).idxmax()
most_close_stage = stage_summary.loc[most_close_stage_idx, 'Stage']
most_decisive_stage = stage_summary.loc[stage_summary['FT_2+Goal_%'].idxmax(), 'Stage']

print(f"COMPETITIVENESS RANKINGS:")
print(f"Most draws: {most_draws_stage} ({stage_summary.loc[stage_summary['FT_Draws_%'].idxmax(), 'FT_Draws_%']:.1f}%)")
print(f"Most close games (0-1 goal): {most_close_stage} ({(stage_summary['FT_Draws_%'] + stage_summary['FT_1Goal_%']).max():.1f}%)")
print(f"Most decisive games (2+ goals): {most_decisive_stage} ({stage_summary.loc[stage_summary['FT_2+Goal_%'].idxmax(), 'FT_2+Goal_%']:.1f}%)")

# Progression analysis
print(f"\nPROGRESSION ANALYSIS:")
group_stage_draws = stage_summary[stage_summary['Stage'] == 'Group Stage']['FT_Draws_%'].iloc[0]
final_draws = stage_summary[stage_summary['Stage'] == 'Final']['FT_Draws_%'].iloc[0]
print(f"Draw percentage: Group Stage {group_stage_draws:.1f}% -> Final {final_draws:.1f}%")

group_stage_decisive = stage_summary[stage_summary['Stage'] == 'Group Stage']['FT_2+Goal_%'].iloc[0]
final_decisive = stage_summary[stage_summary['Stage'] == 'Final']['FT_2+Goal_%'].iloc[0]
print(f"Decisive games: Group Stage {group_stage_decisive:.1f}% -> Final {final_decisive:.1f}%")

# ===== SAVE RESULTS =====
print("\n" + "="*80)
print("SAVING RESULTS")
print("="*80)

# Save detailed stage analysis
stage_df.to_csv('goal_difference_stages_detailed.csv', index=False)

# Save stage summary
stage_summary.to_csv('goal_difference_stages_summary.csv', index=False)

print("Files saved:")
print("- goal_difference_by_stages_analysis.png")
print("- goal_difference_stages_detailed.csv")
print("- goal_difference_stages_summary.csv")

print(f"\n=== ANALYSIS COMPLETE ===")
print(f"Key Finding: {most_close_stage} had the most competitive matches")
print(f"Draws evolution: {group_stage_draws:.1f}% (Group) → {final_draws:.1f}% (Final)")
print(f"Tournament becomes {'more' if final_decisive > group_stage_decisive else 'less'} decisive in later stages") 