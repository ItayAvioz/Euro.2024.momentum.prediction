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

# ===== EXTRACT HALFTIME SCORES =====
print("\n" + "="*80)
print("EXTRACTING HALFTIME AND FULL-TIME SCORES")
print("="*80)

# For each match, find the last event in period 1 to get halftime score
halftime_scores = []
fulltime_scores = []

for match_id in matches['match_id'].unique():
    match_events = events[events['match_id'] == match_id].copy()
    
    if len(match_events) == 0:
        continue
    
    # Get period 1 events (first half)
    p1_events = match_events[match_events['period'] == 1]
    # Get period 2 events (second half) 
    p2_events = match_events[match_events['period'] == 2]
    
    if len(p1_events) == 0 or len(p2_events) == 0:
        continue
    
    # Get halftime score (last event of period 1)
    last_p1_event = p1_events.iloc[-1]
    ht_home = last_p1_event['home_score'] if pd.notna(last_p1_event['home_score']) else 0
    ht_away = last_p1_event['away_score'] if pd.notna(last_p1_event['away_score']) else 0
    
    # Get full-time score (last event of period 2)
    last_p2_event = p2_events.iloc[-1]
    ft_home = last_p2_event['home_score'] if pd.notna(last_p2_event['home_score']) else 0
    ft_away = last_p2_event['away_score'] if pd.notna(last_p2_event['away_score']) else 0
    
    # Calculate results
    ht_result = 'Draw' if ht_home == ht_away else ('Home Win' if ht_home > ht_away else 'Away Win')
    ft_result = 'Draw' if ft_home == ft_away else ('Home Win' if ft_home > ft_away else 'Away Win')
    
    # Second half goals
    sh_home_goals = ft_home - ht_home
    sh_away_goals = ft_away - ht_away
    total_sh_goals = sh_home_goals + sh_away_goals
    
    halftime_scores.append({
        'match_id': match_id,
        'ht_home': int(ht_home),
        'ht_away': int(ht_away),
        'ht_total': int(ht_home + ht_away),
        'ht_result': ht_result,
        'ft_home': int(ft_home),
        'ft_away': int(ft_away),
        'ft_total': int(ft_home + ft_away),
        'ft_result': ft_result,
        'sh_home_goals': int(sh_home_goals),
        'sh_away_goals': int(sh_away_goals),
        'sh_total_goals': int(total_sh_goals),
        'result_changed': ht_result != ft_result
    })

# Create DataFrame
results_df = pd.DataFrame(halftime_scores)

print(f"Successfully analyzed {len(results_df)} matches")

# ===== ANALYSIS =====
print("\n" + "="*80)
print("HALFTIME vs FULL-TIME ANALYSIS")
print("="*80)

# Basic statistics
print("BASIC STATISTICS:")
print(f"Average goals at halftime: {results_df['ht_total'].mean():.2f}")
print(f"Average goals at full-time: {results_df['ft_total'].mean():.2f}")
print(f"Average second-half goals: {results_df['sh_total_goals'].mean():.2f}")

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

# Comeback analysis
comebacks = []
for _, row in results_df.iterrows():
    if row['ht_result'] == 'Home Win' and row['ft_result'] == 'Away Win':
        comebacks.append('Away Comeback')
    elif row['ht_result'] == 'Away Win' and row['ft_result'] == 'Home Win':
        comebacks.append('Home Comeback')
    elif row['ht_result'] in ['Home Win', 'Away Win'] and row['ft_result'] == 'Draw':
        comebacks.append('Equalizer')
    elif row['ht_result'] == 'Draw' and row['ft_result'] in ['Home Win', 'Away Win']:
        comebacks.append('Late Winner')
    else:
        comebacks.append('No Change')

results_df['momentum_type'] = comebacks

momentum_counts = results_df['momentum_type'].value_counts()
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
plt.scatter(results_df['ht_total'], results_df['ft_total'], alpha=0.7, s=60)
plt.plot([0, results_df['ht_total'].max()], [0, results_df['ht_total'].max()], 'r--', alpha=0.5, label='No change line')
plt.xlabel('Halftime Total Goals')
plt.ylabel('Full-time Total Goals')
plt.title('Halftime vs Full-time Goals')
plt.legend()
plt.grid(True, alpha=0.3)

# Add annotations for high-scoring games
for _, row in results_df.iterrows():
    if row['ft_total'] >= 4:  # High-scoring games
        plt.annotate(f"({row['ht_total']},{row['ft_total']})", 
                    (row['ht_total'], row['ft_total']), 
                    xytext=(5, 5), textcoords='offset points', fontsize=8)

# 2. Second half goals distribution
plt.subplot(2, 3, 2)
sh_goals_dist = results_df['sh_total_goals'].value_counts().sort_index()
plt.bar(sh_goals_dist.index, sh_goals_dist.values, alpha=0.7, color='lightcoral')
plt.xlabel('Second Half Goals')
plt.ylabel('Number of Matches')
plt.title('Second Half Goals Distribution')
plt.grid(axis='y', alpha=0.3)

# Add value labels
for i, v in enumerate(sh_goals_dist.values):
    plt.text(sh_goals_dist.index[i], v + 0.5, str(v), ha='center', va='bottom')

# 3. Result transition sankey-style visualization
plt.subplot(2, 3, 3)
transition_data = []
for ht_result in ['Home Win', 'Draw', 'Away Win']:
    for ft_result in ['Home Win', 'Draw', 'Away Win']:
        count = len(results_df[(results_df['ht_result'] == ht_result) & (results_df['ft_result'] == ft_result)])
        if count > 0:
            transition_data.append([ht_result, ft_result, count])

# Create a simplified transition chart
ht_positions = {'Home Win': 0, 'Draw': 1, 'Away Win': 2}
ft_positions = {'Home Win': 0, 'Draw': 1, 'Away Win': 2}

for ht_res, ft_res, count in transition_data:
    ht_pos = ht_positions[ht_res]
    ft_pos = ft_positions[ft_res]
    
    # Line thickness based on count
    linewidth = max(1, count / 3)
    
    # Color based on whether result changed
    color = 'green' if ht_res == ft_res else 'red'
    alpha = min(1.0, count / 10)
    
    plt.plot([0, 1], [ht_pos, ft_pos], color=color, linewidth=linewidth, alpha=alpha)

plt.xlim(-0.1, 1.1)
plt.ylim(-0.5, 2.5)
plt.xticks([0, 1], ['Halftime', 'Full-time'])
plt.yticks([0, 1, 2], ['Home Win', 'Draw', 'Away Win'])
plt.title('Result Transitions\n(Green=Same, Red=Changed)')
plt.grid(True, alpha=0.3)

# 4. Momentum patterns pie chart
plt.subplot(2, 3, 4)
momentum_counts_filtered = momentum_counts[momentum_counts > 0]
colors = ['lightblue', 'lightcoral', 'lightgreen', 'orange', 'purple'][:len(momentum_counts_filtered)]
plt.pie(momentum_counts_filtered.values, labels=momentum_counts_filtered.index, autopct='%1.1f%%', 
        colors=colors, startangle=90)
plt.title('Momentum Patterns Distribution')

# 5. Goals comparison by result type
plt.subplot(2, 3, 5)
result_goals = results_df.groupby('ht_result')[['ht_total', 'sh_total_goals', 'ft_total']].mean()

x = np.arange(len(result_goals.index))
width = 0.25

plt.bar(x - width, result_goals['ht_total'], width, label='Halftime Goals', alpha=0.8, color='skyblue')
plt.bar(x, result_goals['sh_total_goals'], width, label='Second Half Goals', alpha=0.8, color='lightcoral')
plt.bar(x + width, result_goals['ft_total'], width, label='Full-time Goals', alpha=0.8, color='lightgreen')

plt.xlabel('Halftime Result')
plt.ylabel('Average Goals')
plt.title('Average Goals by Halftime Result')
plt.xticks(x, result_goals.index, rotation=45)
plt.legend()
plt.grid(axis='y', alpha=0.3)

# 6. Result change analysis
plt.subplot(2, 3, 6)
change_data = results_df['result_changed'].value_counts()
labels = ['Result Stayed Same', 'Result Changed']
colors = ['lightgreen', 'lightcoral']
plt.pie(change_data.values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
plt.title(f'Result Changes\n{change_data[True]} of {len(results_df)} matches changed')

plt.tight_layout()
plt.savefig('halftime_vs_fulltime_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# ===== DETAILED EXAMPLES =====
print("\n" + "="*80)
print("NOTABLE EXAMPLES")
print("="*80)

print("BIGGEST COMEBACKS:")
comebacks_data = results_df[results_df['momentum_type'].isin(['Away Comeback', 'Home Comeback'])]
if len(comebacks_data) > 0:
    for _, row in comebacks_data.iterrows():
        print(f"Match {row['match_id']}: HT {row['ht_home']}-{row['ht_away']} → FT {row['ft_home']}-{row['ft_away']} ({row['momentum_type']})")

print(f"\nHIGHEST SCORING SECOND HALVES:")
high_sh = results_df.nlargest(5, 'sh_total_goals')
for _, row in high_sh.iterrows():
    print(f"Match {row['match_id']}: HT {row['ht_home']}-{row['ht_away']} → FT {row['ft_home']}-{row['ft_away']} ({row['sh_total_goals']} second-half goals)")

print(f"\nMOST DRAMATIC CHANGES:")
dramatic = results_df[results_df['result_changed'] == True].copy()
dramatic['goal_swing'] = abs(dramatic['sh_home_goals'] - dramatic['sh_away_goals'])
dramatic_sorted = dramatic.nlargest(5, 'goal_swing')
for _, row in dramatic_sorted.iterrows():
    print(f"Match {row['match_id']}: HT {row['ht_home']}-{row['ht_away']} ({row['ht_result']}) → FT {row['ft_home']}-{row['ft_away']} ({row['ft_result']})")

# ===== SAVE RESULTS =====
print("\n" + "="*80)
print("SAVING RESULTS")
print("="*80)

# Save detailed results
results_df.to_csv('halftime_vs_fulltime_detailed.csv', index=False)

# Save summary statistics
summary_stats = {
    'Metric': ['Average HT Goals', 'Average FT Goals', 'Average SH Goals', 'Result Changes', 'Result Changes %'],
    'Value': [results_df['ht_total'].mean(), results_df['ft_total'].mean(), results_df['sh_total_goals'].mean(), 
             result_changes, (result_changes/len(results_df)*100)]
}
summary_df = pd.DataFrame(summary_stats)
summary_df.to_csv('halftime_fulltime_summary.csv', index=False)

# Save transition matrix
transition_matrix.to_csv('result_transition_matrix.csv')

print("Files saved:")
print("- halftime_vs_fulltime_analysis.png")
print("- halftime_vs_fulltime_detailed.csv")
print("- halftime_fulltime_summary.csv")
print("- result_transition_matrix.csv")

print(f"\n=== ANALYSIS COMPLETE ===")
print(f"Key Finding: {result_changes} of {len(results_df)} matches ({(result_changes/len(results_df)*100):.1f}%) had result changes between halftime and full-time") 