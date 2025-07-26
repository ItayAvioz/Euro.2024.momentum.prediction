import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ast
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

def parse_shot_outcome(shot_detail_str):
    """Parse shot outcome to identify goals"""
    try:
        if isinstance(shot_detail_str, str):
            shot_dict = ast.literal_eval(shot_detail_str)
        else:
            shot_dict = shot_detail_str
            
        outcome = shot_dict.get('outcome', {})
        if isinstance(outcome, dict):
            outcome_name = outcome.get('name', '').lower()
            outcome_id = outcome.get('id', 0)
            
            if outcome_id == 97 or 'goal' in outcome_name:
                return True
    except:
        pass
    return False

def parse_team_info(team_str):
    """Parse team information from string"""
    try:
        if isinstance(team_str, str):
            team_dict = ast.literal_eval(team_str)
            return team_dict.get('name', 'Unknown')
    except:
        pass
    return str(team_str)

# Load data
print("Loading Euro 2024 data...")
events_df = pd.read_csv('../Data/events_complete.csv', low_memory=False)
matches_df = pd.read_csv('../Data/matches_complete.csv')

print("Processing goal data...")

# Get all goals from shots (periods 1-2 only)
shots_df = events_df[events_df['shot'].notna()].copy()
shots_df['is_goal'] = shots_df['shot'].apply(parse_shot_outcome)
shot_goals = shots_df[shots_df['is_goal'] == True]

# Filter for periods 1 and 2 only
regulation_goals = shot_goals[shot_goals['period'].isin([1, 2])].copy()

# Get own goals (periods 1-2 only)
own_goals = events_df[
    (events_df['type'].str.contains('Own Goal Against', na=False)) & 
    (events_df['period'].isin([1, 2]))
].copy()

# Combine all regulation goals
all_regulation_goals = []

# Add shot goals
for _, goal in regulation_goals.iterrows():
    team_name = parse_team_info(goal['team'])
    all_regulation_goals.append({
        'match_id': goal['match_id'],
        'period': goal['period'],
        'team': team_name,
        'minute': goal['minute'],
        'type': 'Shot Goal'
    })

# Add own goals
for _, goal in own_goals.iterrows():
    team_name = parse_team_info(goal['team'])
    all_regulation_goals.append({
        'match_id': goal['match_id'],
        'period': goal['period'],
        'team': team_name,
        'minute': goal['minute'],
        'type': 'Own Goal'
    })

goals_df = pd.DataFrame(all_regulation_goals)

print(f"Total regulation goals found: {len(goals_df)}")
print(f"Period 1 goals: {len(goals_df[goals_df['period'] == 1])}")
print(f"Period 2 goals: {len(goals_df[goals_df['period'] == 2])}")

# Create match-level goal counts
match_goals = defaultdict(lambda: {'period_1': 0, 'period_2': 0, 'total': 0})

for _, goal in goals_df.iterrows():
    match_id = goal['match_id']
    period = goal['period']
    
    if period == 1:
        match_goals[match_id]['period_1'] += 1
    elif period == 2:
        match_goals[match_id]['period_2'] += 1
    
    match_goals[match_id]['total'] += 1

# Convert to DataFrame
match_summary = []
for match_id, goals in match_goals.items():
    match_summary.append({
        'match_id': match_id,
        'period_1_goals': goals['period_1'],
        'period_2_goals': goals['period_2'],
        'total_goals': goals['total']
    })

match_summary_df = pd.DataFrame(match_summary)

# Get all 51 matches (including those with 0 goals)
all_matches = matches_df['match_id'].unique()
complete_match_summary = []

for match_id in all_matches:
    if match_id in match_goals:
        goals = match_goals[match_id]
        complete_match_summary.append({
            'match_id': match_id,
            'period_1_goals': goals['period_1'],
            'period_2_goals': goals['period_2'],
            'total_goals': goals['total']
        })
    else:
        complete_match_summary.append({
            'match_id': match_id,
            'period_1_goals': 0,
            'period_2_goals': 0,
            'total_goals': 0
        })

complete_df = pd.DataFrame(complete_match_summary)

print("\n" + "="*80)
print("EURO 2024 GOALS PER GAME ANALYSIS - PERIODS 1 & 2")
print("="*80)

# Summary Statistics
print("\nSUMMARY STATISTICS")
print("-" * 40)
print(f"Total matches: {len(complete_df)}")
print(f"Total goals: {complete_df['total_goals'].sum()}")
print(f"Period 1 goals: {complete_df['period_1_goals'].sum()}")
print(f"Period 2 goals: {complete_df['period_2_goals'].sum()}")
print(f"Average goals per match: {complete_df['total_goals'].mean():.2f}")
print(f"Average P1 goals per match: {complete_df['period_1_goals'].mean():.2f}")
print(f"Average P2 goals per match: {complete_df['period_2_goals'].mean():.2f}")

# Distribution Tables
print("\nPERIOD 1 GOALS DISTRIBUTION")
print("-" * 40)
p1_dist = complete_df['period_1_goals'].value_counts().sort_index()
p1_pct = (p1_dist / len(complete_df) * 100).round(1)

p1_table = pd.DataFrame({
    'Goals': p1_dist.index,
    'Matches': p1_dist.values,
    'Percentage': p1_pct.values
})
print(p1_table.to_string(index=False))

print("\nPERIOD 2 GOALS DISTRIBUTION")
print("-" * 40)
p2_dist = complete_df['period_2_goals'].value_counts().sort_index()
p2_pct = (p2_dist / len(complete_df) * 100).round(1)

p2_table = pd.DataFrame({
    'Goals': p2_dist.index,
    'Matches': p2_dist.values,
    'Percentage': p2_pct.values
})
print(p2_table.to_string(index=False))

print("\nTOTAL GOALS DISTRIBUTION (BOTH PERIODS)")
print("-" * 40)
total_dist = complete_df['total_goals'].value_counts().sort_index()
total_pct = (total_dist / len(complete_df) * 100).round(1)

total_table = pd.DataFrame({
    'Goals': total_dist.index,
    'Matches': total_dist.values,
    'Percentage': total_pct.values
})
print(total_table.to_string(index=False))

# Period Comparison
print("\nPERIOD COMPARISON")
print("-" * 40)
comparison_stats = pd.DataFrame({
    'Metric': [
        'Total Goals', 
        'Average per Match', 
        'Max Goals in Match',
        'Matches with 0 Goals',
        'Matches with 1+ Goals',
        'Matches with 2+ Goals',
        'Matches with 3+ Goals'
    ],
    'Period 1': [
        complete_df['period_1_goals'].sum(),
        f"{complete_df['period_1_goals'].mean():.2f}",
        complete_df['period_1_goals'].max(),
        len(complete_df[complete_df['period_1_goals'] == 0]),
        len(complete_df[complete_df['period_1_goals'] >= 1]),
        len(complete_df[complete_df['period_1_goals'] >= 2]),
        len(complete_df[complete_df['period_1_goals'] >= 3])
    ],
    'Period 2': [
        complete_df['period_2_goals'].sum(),
        f"{complete_df['period_2_goals'].mean():.2f}",
        complete_df['period_2_goals'].max(),
        len(complete_df[complete_df['period_2_goals'] == 0]),
        len(complete_df[complete_df['period_2_goals'] >= 1]),
        len(complete_df[complete_df['period_2_goals'] >= 2]),
        len(complete_df[complete_df['period_2_goals'] >= 3])
    ]
})
print(comparison_stats.to_string(index=False))

# Create visualizations
fig, axes = plt.subplots(2, 2, figsize=(15, 12))
fig.suptitle('Euro 2024 Goals Distribution Analysis\n(Regulation Time: Periods 1 & 2)', 
             fontsize=16, fontweight='bold', y=0.98)

# Period 1 Distribution
ax1 = axes[0, 0]
p1_dist.plot(kind='bar', ax=ax1, color='skyblue', alpha=0.7)
ax1.set_title('Period 1 Goals Distribution', fontweight='bold')
ax1.set_xlabel('Goals per Match')
ax1.set_ylabel('Number of Matches')
ax1.tick_params(axis='x', rotation=0)

# Add percentage labels on bars
for i, (goals, matches) in enumerate(p1_dist.items()):
    pct = (matches / len(complete_df) * 100)
    ax1.text(i, matches + 0.5, f'{pct:.1f}%', ha='center', fontweight='bold')

# Period 2 Distribution
ax2 = axes[0, 1]
p2_dist.plot(kind='bar', ax=ax2, color='lightcoral', alpha=0.7)
ax2.set_title('Period 2 Goals Distribution', fontweight='bold')
ax2.set_xlabel('Goals per Match')
ax2.set_ylabel('Number of Matches')
ax2.tick_params(axis='x', rotation=0)

# Add percentage labels on bars
for i, (goals, matches) in enumerate(p2_dist.items()):
    pct = (matches / len(complete_df) * 100)
    ax2.text(i, matches + 0.5, f'{pct:.1f}%', ha='center', fontweight='bold')

# Period Comparison Bar Chart
ax3 = axes[1, 0]

# Get all unique goal counts from both periods
all_goals = sorted(set(p1_dist.index) | set(p2_dist.index))
x = np.arange(len(all_goals))
width = 0.35

# Align both distributions to same goal counts
p1_aligned = [p1_dist.get(goal, 0) for goal in all_goals]
p2_aligned = [p2_dist.get(goal, 0) for goal in all_goals]

bars1 = ax3.bar(x - width/2, p1_aligned, width, label='Period 1', 
                color='skyblue', alpha=0.7)
bars2 = ax3.bar(x + width/2, p2_aligned, width, label='Period 2', 
                color='lightcoral', alpha=0.7)

ax3.set_title('Period 1 vs Period 2 Comparison', fontweight='bold')
ax3.set_xlabel('Goals per Match')
ax3.set_ylabel('Number of Matches')
ax3.set_xticks(x)
ax3.set_xticklabels(all_goals)
ax3.legend()

# Total Distribution
ax4 = axes[1, 1]
total_dist.plot(kind='bar', ax=ax4, color='lightgreen', alpha=0.7)
ax4.set_title('Total Goals Distribution\n(Both Periods Combined)', fontweight='bold')
ax4.set_xlabel('Total Goals per Match')
ax4.set_ylabel('Number of Matches')
ax4.tick_params(axis='x', rotation=0)

# Add percentage labels on bars
for i, (goals, matches) in enumerate(total_dist.items()):
    pct = (matches / len(complete_df) * 100)
    ax4.text(i, matches + 0.5, f'{pct:.1f}%', ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig('goals_per_game_period_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# Additional insights
print("\nKEY INSIGHTS")
print("-" * 40)
print(f"• Second half produces {complete_df['period_2_goals'].sum() - complete_df['period_1_goals'].sum():+d} more goals than first half")
print(f"• {len(complete_df[complete_df['period_2_goals'] > complete_df['period_1_goals']])} matches had more goals in 2nd half")
print(f"• {len(complete_df[complete_df['period_1_goals'] > complete_df['period_2_goals']])} matches had more goals in 1st half")
print(f"• {len(complete_df[complete_df['period_1_goals'] == complete_df['period_2_goals']])} matches had equal goals in both halves")
print(f"• Most common total: {total_dist.index[0]} goals ({total_dist.iloc[0]} matches, {total_pct.iloc[0]:.1f}%)")
print(f"• Goalless matches: {len(complete_df[complete_df['total_goals'] == 0])} ({len(complete_df[complete_df['total_goals'] == 0])/len(complete_df)*100:.1f}%)")

# Save summary tables to CSV
p1_table.to_csv('period_1_goals_distribution.csv', index=False)
p2_table.to_csv('period_2_goals_distribution.csv', index=False)
total_table.to_csv('total_goals_distribution.csv', index=False)
comparison_stats.to_csv('period_comparison_stats.csv', index=False)
complete_df.to_csv('match_goals_summary.csv', index=False)

print(f"\nFiles saved:")
print("• goals_per_game_period_analysis.png")
print("• period_1_goals_distribution.csv")
print("• period_2_goals_distribution.csv") 
print("• total_goals_distribution.csv")
print("• period_comparison_stats.csv")
print("• match_goals_summary.csv") 