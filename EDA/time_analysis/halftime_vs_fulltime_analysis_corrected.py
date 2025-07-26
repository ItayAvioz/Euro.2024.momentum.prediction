import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ast

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

print("=== EURO 2024 HALFTIME vs FULL-TIME ANALYSIS ===")
print("Loading and processing data...")

# Load the events and matches data
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

# ===== EXTRACT HALFTIME AND FULL-TIME RESULTS =====
print("\n" + "="*80)
print("EXTRACTING HALFTIME AND FULL-TIME RESULTS")
print("="*80)

results_analysis = []

for _, match in matches.iterrows():
    match_id = match['match_id']
    match_events = events[events['match_id'] == match_id].copy()
    
    if len(match_events) == 0:
        continue
    
    # Get home and away team IDs
    home_team_id = match['home_team_id'] 
    away_team_id = match['away_team_id']
    
    # Count goals by period and team using shot outcome ID 97 (Goal)
    goal_events = match_events[(match_events['type_name'] == 'Shot') & 
                              (match_events['shot_outcome_id'] == 97)]
    
    # First half goals
    p1_goals = goal_events[goal_events['period'] == 1]
    ht_home_goals = len(p1_goals[p1_goals['team_id'] == home_team_id])
    ht_away_goals = len(p1_goals[p1_goals['team_id'] == away_team_id])
    
    # Full-time goals (from matches data)
    ft_home_goals = int(match['home_score']) if pd.notna(match['home_score']) else 0
    ft_away_goals = int(match['away_score']) if pd.notna(match['away_score']) else 0
    
    # Second half goals (calculated)
    sh_home_goals = ft_home_goals - ht_home_goals
    sh_away_goals = ft_away_goals - ht_away_goals
    
    # Determine results
    ht_result = 'Draw' if ht_home_goals == ht_away_goals else ('Home Win' if ht_home_goals > ht_away_goals else 'Away Win')
    ft_result = 'Draw' if ft_home_goals == ft_away_goals else ('Home Win' if ft_home_goals > ft_away_goals else 'Away Win')
    
    # Additional metrics
    ht_total = ht_home_goals + ht_away_goals
    ft_total = ft_home_goals + ft_away_goals
    sh_total = sh_home_goals + sh_away_goals
    
    results_analysis.append({
        'match_id': match_id,
        'home_team': match['home_team_name'],
        'away_team': match['away_team_name'],
        'stage': match['stage'],
        'ht_home': ht_home_goals,
        'ht_away': ht_away_goals,
        'ht_total': ht_total,
        'ht_result': ht_result,
        'ft_home': ft_home_goals,
        'ft_away': ft_away_goals,
        'ft_total': ft_total,
        'ft_result': ft_result,
        'sh_home': sh_home_goals,
        'sh_away': sh_away_goals,
        'sh_total': sh_total,
        'result_changed': ht_result != ft_result
    })

# Create DataFrame
results_df = pd.DataFrame(results_analysis)

print(f"Successfully analyzed {len(results_df)} matches")

# ===== ANALYSIS =====
print("\n" + "="*80)
print("HALFTIME vs FULL-TIME ANALYSIS")
print("="*80)

# Basic statistics
print("BASIC STATISTICS:")
print(f"Average goals at halftime: {results_df['ht_total'].mean():.2f}")
print(f"Average goals at full-time: {results_df['ft_total'].mean():.2f}")
print(f"Average second-half goals: {results_df['sh_total'].mean():.2f}")

# Result distribution
print(f"\nHALFTIME RESULTS:")
ht_results = results_df['ht_result'].value_counts()
for result, count in ht_results.items():
    percentage = (count / len(results_df)) * 100
    print(f"{result}: {count} ({percentage:.1f}%)")

print(f"\nFULL-TIME RESULTS:")
ft_results = results_df['ft_result'].value_counts()
for result, count in ft_results.items():
    percentage = (count / len(results_df)) * 100
    print(f"{result}: {count} ({percentage:.1f}%)")

# Result changes
result_changes = results_df['result_changed'].sum()
print(f"\nRESULT CHANGES:")
print(f"Matches where result changed: {result_changes} ({(result_changes/len(results_df)*100):.1f}%)")
print(f"Matches where result stayed same: {len(results_df) - result_changes} ({((len(results_df) - result_changes)/len(results_df)*100):.1f}%)")

# Detailed result transition matrix
print(f"\nRESULT TRANSITION MATRIX:")
transition_matrix = pd.crosstab(results_df['ht_result'], results_df['ft_result'], margins=True)
print(transition_matrix)

# ===== MOMENTUM ANALYSIS =====
print("\n" + "="*80)
print("MOMENTUM ANALYSIS")
print("="*80)

# Momentum patterns
momentum_patterns = []
for _, row in results_df.iterrows():
    if row['ht_result'] == 'Home Win' and row['ft_result'] == 'Away Win':
        momentum_patterns.append('Away Comeback')
    elif row['ht_result'] == 'Away Win' and row['ft_result'] == 'Home Win':
        momentum_patterns.append('Home Comeback')
    elif row['ht_result'] in ['Home Win', 'Away Win'] and row['ft_result'] == 'Draw':
        momentum_patterns.append('Equalizer')
    elif row['ht_result'] == 'Draw' and row['ft_result'] in ['Home Win', 'Away Win']:
        momentum_patterns.append('Late Winner')
    else:
        momentum_patterns.append('Result Maintained')

results_df['momentum_pattern'] = momentum_patterns

momentum_counts = results_df['momentum_pattern'].value_counts()
print("MOMENTUM PATTERNS:")
for pattern, count in momentum_counts.items():
    percentage = (count / len(results_df)) * 100
    print(f"{pattern}: {count} ({percentage:.1f}%)")

# ===== VISUALIZATION =====
print("\n" + "="*80)
print("CREATING VISUALIZATIONS")
print("="*80)

fig = plt.figure(figsize=(20, 15))

# 1. Halftime vs Full-time goals scatter plot
plt.subplot(2, 3, 1)
plt.scatter(results_df['ht_total'], results_df['ft_total'], alpha=0.7, s=80, c='skyblue', edgecolors='navy')
max_goals = max(results_df['ft_total'].max(), results_df['ht_total'].max())
plt.plot([0, max_goals], [0, max_goals], 'r--', alpha=0.7, linewidth=2, label='No change line')
plt.xlabel('Halftime Total Goals')
plt.ylabel('Full-time Total Goals')
plt.title('Halftime vs Full-time Goals')
plt.legend()
plt.grid(True, alpha=0.3)

# Annotate interesting matches
for _, row in results_df.iterrows():
    if row['ft_total'] >= 4 or row['result_changed']:
        plt.annotate(f"{row['home_team'][:3]}-{row['away_team'][:3]}", 
                    (row['ht_total'], row['ft_total']), 
                    xytext=(5, 5), textcoords='offset points', fontsize=8)

# 2. Second half goals distribution
plt.subplot(2, 3, 2)
sh_goals_dist = results_df['sh_total'].value_counts().sort_index()
bars = plt.bar(sh_goals_dist.index, sh_goals_dist.values, alpha=0.8, color='lightcoral', edgecolor='darkred')
plt.xlabel('Second Half Goals')
plt.ylabel('Number of Matches')
plt.title('Second Half Goals Distribution')
plt.grid(axis='y', alpha=0.3)

# Add value labels
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.3,
             f'{int(height)}', ha='center', va='bottom', fontweight='bold')

# 3. Result transition visualization
plt.subplot(2, 3, 3)
transition_data = pd.crosstab(results_df['ht_result'], results_df['ft_result'])
sns.heatmap(transition_data, annot=True, fmt='d', cmap='Blues', cbar_kws={'label': 'Number of Matches'})
plt.title('Result Transitions\n(Halftime → Full-time)')
plt.ylabel('Halftime Result')
plt.xlabel('Full-time Result')

# 4. Momentum patterns pie chart
plt.subplot(2, 3, 4)
colors = ['lightgreen', 'lightcoral', 'orange', 'lightblue', 'pink']
momentum_counts_filtered = momentum_counts[momentum_counts > 0]
plt.pie(momentum_counts_filtered.values, labels=momentum_counts_filtered.index, 
        autopct='%1.1f%%', colors=colors[:len(momentum_counts_filtered)], startangle=90)
plt.title(f'Momentum Patterns\n({len(results_df)} matches analyzed)')

# 5. Goals by stage
plt.subplot(2, 3, 5)
stage_goals = results_df.groupby('stage')[['ht_total', 'sh_total', 'ft_total']].mean()

x = np.arange(len(stage_goals.index))
width = 0.25

plt.bar(x - width, stage_goals['ht_total'], width, label='Halftime Goals', alpha=0.8, color='skyblue')
plt.bar(x, stage_goals['sh_total'], width, label='Second Half Goals', alpha=0.8, color='lightcoral')
plt.bar(x + width, stage_goals['ft_total'], width, label='Full-time Goals', alpha=0.8, color='lightgreen')

plt.xlabel('Tournament Stage')
plt.ylabel('Average Goals')
plt.title('Average Goals by Tournament Stage')
plt.xticks(x, stage_goals.index, rotation=45, ha='right')
plt.legend()
plt.grid(axis='y', alpha=0.3)

# 6. Result stability analysis
plt.subplot(2, 3, 6)
stability_data = results_df['result_changed'].value_counts()
labels = ['Result Maintained', 'Result Changed']
colors = ['lightgreen', 'lightcoral']
explode = (0.05, 0.05)

plt.pie(stability_data.values, labels=labels, autopct='%1.1f%%', colors=colors, 
        explode=explode, startangle=90, shadow=True)
plt.title(f'Result Stability\n{stability_data[False]} maintained vs {stability_data[True]} changed')

plt.tight_layout()
plt.savefig('halftime_vs_fulltime_complete_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# ===== DETAILED EXAMPLES =====
print("\n" + "="*80)
print("NOTABLE EXAMPLES")
print("="*80)

print("DRAMATIC COMEBACKS:")
comebacks = results_df[results_df['momentum_pattern'].isin(['Away Comeback', 'Home Comeback'])]
if len(comebacks) > 0:
    for _, row in comebacks.iterrows():
        print(f"{row['home_team']} vs {row['away_team']} ({row['stage']}): "
              f"HT {row['ht_home']}-{row['ht_away']} → FT {row['ft_home']}-{row['ft_away']} ({row['momentum_pattern']})")
else:
    print("No complete comebacks found in this tournament")

print(f"\nHIGHEST SCORING SECOND HALVES:")
high_sh = results_df.nlargest(5, 'sh_total')
for _, row in high_sh.iterrows():
    print(f"{row['home_team']} vs {row['away_team']} ({row['stage']}): "
          f"HT {row['ht_home']}-{row['ht_away']} → FT {row['ft_home']}-{row['ft_away']} "
          f"({row['sh_total']} second-half goals)")

print(f"\nLATE WINNERS:")
late_winners = results_df[results_df['momentum_pattern'] == 'Late Winner']
for _, row in late_winners.iterrows():
    print(f"{row['home_team']} vs {row['away_team']} ({row['stage']}): "
          f"HT {row['ht_home']}-{row['ht_away']} → FT {row['ft_home']}-{row['ft_away']}")

# ===== SAVE RESULTS =====
print("\n" + "="*80)
print("SAVING RESULTS")
print("="*80)

# Save detailed results
results_df.to_csv('halftime_vs_fulltime_complete_analysis.csv', index=False)

# Save summary statistics
summary_stats = {
    'Metric': ['Total Matches', 'Avg HT Goals', 'Avg FT Goals', 'Avg SH Goals', 
               'Result Changes', 'Result Changes %', 'Most Common HT Result', 'Most Common FT Result'],
    'Value': [len(results_df), results_df['ht_total'].mean(), results_df['ft_total'].mean(), 
             results_df['sh_total'].mean(), result_changes, (result_changes/len(results_df)*100),
             ht_results.index[0], ft_results.index[0]]
}
summary_df = pd.DataFrame(summary_stats)
summary_df.to_csv('halftime_fulltime_summary_stats.csv', index=False)

# Save transition matrix
transition_matrix.to_csv('halftime_fulltime_transition_matrix.csv')

print("Files saved:")
print("- halftime_vs_fulltime_complete_analysis.png")
print("- halftime_vs_fulltime_complete_analysis.csv")
print("- halftime_fulltime_summary_stats.csv")
print("- halftime_fulltime_transition_matrix.csv")

print(f"\n=== ANALYSIS COMPLETE ===")
print(f"Key Finding: {result_changes} of {len(results_df)} matches ({(result_changes/len(results_df)*100):.1f}%) "
      f"had result changes between halftime and full-time")
print(f"Average goals increased from {results_df['ht_total'].mean():.2f} at HT to {results_df['ft_total'].mean():.2f} at FT")
print(f"Most common momentum pattern: {momentum_counts.index[0]} ({momentum_counts.iloc[0]} matches)")

# Clean up temporary file
import os
if os.path.exists('check_data_structure.py'):
    os.remove('check_data_structure.py') 