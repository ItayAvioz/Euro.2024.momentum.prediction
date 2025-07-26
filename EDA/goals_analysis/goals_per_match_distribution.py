import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ast

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

print("=== EURO 2024 GOALS PER MATCH DISTRIBUTION ANALYSIS ===")
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

# ===== ANALYZE GOALS PER MATCH =====
print("\n" + "="*80)
print("ANALYZING GOALS PER MATCH DISTRIBUTION")
print("="*80)

match_analysis = []

for _, match in matches.iterrows():
    match_id = match['match_id']
    match_events = events[events['match_id'] == match_id].copy()
    
    if len(match_events) == 0:
        continue
    
    # Get team information
    home_team_id = match['home_team_id'] 
    away_team_id = match['away_team_id']
    stage = match['stage']
    
    # Get final scores
    ft_home_goals = int(match['home_score']) if pd.notna(match['home_score']) else 0
    ft_away_goals = int(match['away_score']) if pd.notna(match['away_score']) else 0
    
    # Calculate totals
    total_goals = ft_home_goals + ft_away_goals
    goal_difference = abs(ft_home_goals - ft_away_goals)
    
    # Determine match outcome
    if ft_home_goals > ft_away_goals:
        outcome = 'Home Win'
        winner = 'Home'
    elif ft_away_goals > ft_home_goals:
        outcome = 'Away Win'
        winner = 'Away'
    else:
        outcome = 'Draw'
        winner = 'Draw'
    
    # Check for extra time
    max_period = match_events['period'].max()
    has_extra_time = max_period > 2
    
    match_analysis.append({
        'match_id': match_id,
        'stage': stage,
        'home_team': match['home_team_name'],
        'away_team': match['away_team_name'],
        'home_goals': ft_home_goals,
        'away_goals': ft_away_goals,
        'total_goals': total_goals,
        'goal_difference': goal_difference,
        'outcome': outcome,
        'winner': winner,
        'has_extra_time': has_extra_time
    })

# Create DataFrame
goals_df = pd.DataFrame(match_analysis)

print(f"Successfully analyzed {len(goals_df)} matches")

# ===== GOALS PER MATCH DISTRIBUTION =====
print("\n" + "="*80)
print("TOTAL GOALS PER MATCH DISTRIBUTION")
print("="*80)

# Count matches by total goals
goals_distribution = goals_df['total_goals'].value_counts().sort_index()

print("GOALS PER MATCH BREAKDOWN:")
print("Goals" + " "*5 + "Matches" + " "*5 + "Percentage")
print("-" * 40)

total_matches = len(goals_df)
for goals, count in goals_distribution.items():
    percentage = (count / total_matches) * 100
    print(f"{goals:>5} {count:>10} {percentage:>10.1f}%")

print(f"\nTOTAL MATCHES: {total_matches}")

# Basic statistics
avg_goals = goals_df['total_goals'].mean()
median_goals = goals_df['total_goals'].median()
mode_goals = goals_df['total_goals'].mode().iloc[0]
max_goals = goals_df['total_goals'].max()
min_goals = goals_df['total_goals'].min()

print(f"\nGOALS PER MATCH STATISTICS:")
print(f"Average: {avg_goals:.2f}")
print(f"Median: {median_goals:.1f}")
print(f"Mode: {mode_goals}")
print(f"Range: {min_goals} - {max_goals}")

# ===== OUTCOME DISTRIBUTION BY GOALS =====
print("\n" + "="*80)
print("MATCH OUTCOME DISTRIBUTION BY TOTAL GOALS")
print("="*80)

outcome_by_goals = []

for goals in sorted(goals_df['total_goals'].unique()):
    goal_matches = goals_df[goals_df['total_goals'] == goals]
    
    draws = len(goal_matches[goal_matches['outcome'] == 'Draw'])
    home_wins = len(goal_matches[goal_matches['outcome'] == 'Home Win'])
    away_wins = len(goal_matches[goal_matches['outcome'] == 'Away Win'])
    total_matches_with_goals = len(goal_matches)
    
    # Calculate percentages
    draw_pct = (draws / total_matches_with_goals) * 100
    home_win_pct = (home_wins / total_matches_with_goals) * 100
    away_win_pct = (away_wins / total_matches_with_goals) * 100
    
    outcome_by_goals.append({
        'Total_Goals': goals,
        'Matches': total_matches_with_goals,
        'Draws': draws,
        'Draw_%': draw_pct,
        'Home_Wins': home_wins,
        'Home_Win_%': home_win_pct,
        'Away_Wins': away_wins,
        'Away_Win_%': away_win_pct,
        'Total_Wins': home_wins + away_wins,
        'Win_%': home_win_pct + away_win_pct
    })

# Create summary DataFrame
outcome_summary = pd.DataFrame(outcome_by_goals)

print("OUTCOME DISTRIBUTION BY TOTAL GOALS:")
print("Goals" + " "*3 + "Matches" + " "*3 + "Draws" + " "*5 + "Wins" + " "*6 + "Draw%" + " "*4 + "Win%")
print("-" * 70)

for _, row in outcome_summary.iterrows():
    print(f"{row['Total_Goals']:>5} {row['Matches']:>8} {row['Draws']:>8} {row['Total_Wins']:>8} {row['Draw_%']:>8.1f}% {row['Win_%']:>8.1f}%")

# ===== DRAW PROBABILITY ANALYSIS =====
print("\n" + "="*80)
print("DRAW PROBABILITY BY GOALS SCORED")
print("="*80)

print("DETAILED DRAW ANALYSIS:")
for _, row in outcome_summary.iterrows():
    goals = int(row['Total_Goals'])
    draws = int(row['Draws'])
    matches = int(row['Matches'])
    draw_pct = row['Draw_%']
    
    print(f"\n{goals} GOAL{'S' if goals != 1 else ''} ({matches} matches):")
    print(f"  Draws: {draws} ({draw_pct:.1f}%)")
    print(f"  Decisive: {matches - draws} ({100 - draw_pct:.1f}%)")

# Find patterns
zero_goal_draws = outcome_summary[outcome_summary['Total_Goals'] == 0]['Draw_%'].iloc[0] if 0 in outcome_summary['Total_Goals'].values else 0
high_goal_draws = outcome_summary[outcome_summary['Total_Goals'] >= 4]['Draw_%'].mean() if len(outcome_summary[outcome_summary['Total_Goals'] >= 4]) > 0 else 0

print(f"\nKEY PATTERNS:")
print(f"0-goal matches draw rate: {zero_goal_draws:.1f}%")
print(f"4+ goal matches draw rate: {high_goal_draws:.1f}%")

# Most common scorelines
print(f"\nMOST COMMON TOTAL GOALS:")
top_3_goals = goals_distribution.head(3)
for goals, count in top_3_goals.items():
    pct = (count / total_matches) * 100
    print(f"{goals} goals: {count} matches ({pct:.1f}%)")

# ===== STAGE-SPECIFIC ANALYSIS =====
print("\n" + "="*80)
print("GOALS PER MATCH BY TOURNAMENT STAGE")
print("="*80)

stage_goals = []
stages = ['Group Stage', 'Round of 16', 'Quarter-finals', 'Semi-finals', 'Final']

for stage in stages:
    stage_matches = goals_df[goals_df['stage'] == stage]
    
    if len(stage_matches) == 0:
        continue
    
    avg_goals_stage = stage_matches['total_goals'].mean()
    median_goals_stage = stage_matches['total_goals'].median()
    draw_rate_stage = (len(stage_matches[stage_matches['outcome'] == 'Draw']) / len(stage_matches)) * 100
    
    # Goals distribution for this stage
    stage_goal_dist = stage_matches['total_goals'].value_counts().sort_index()
    
    stage_goals.append({
        'Stage': stage,
        'Matches': len(stage_matches),
        'Avg_Goals': avg_goals_stage,
        'Median_Goals': median_goals_stage,
        'Draw_Rate_%': draw_rate_stage,
        'Goals_Distribution': dict(stage_goal_dist)
    })

print("STAGE-SPECIFIC GOALS ANALYSIS:")
print("Stage" + " "*15 + "Matches" + " "*3 + "Avg Goals" + " "*3 + "Draw Rate")
print("-" * 65)

for item in stage_goals:
    print(f"{item['Stage']:<20} {item['Matches']:>7} {item['Avg_Goals']:>10.2f} {item['Draw_Rate_%']:>10.1f}%")

# ===== VISUALIZATION =====
print("\n" + "="*80)
print("CREATING VISUALIZATIONS")
print("="*80)

fig = plt.figure(figsize=(20, 15))

# 1. Goals per match distribution
plt.subplot(2, 3, 1)
bars = plt.bar(goals_distribution.index, goals_distribution.values, alpha=0.8, color='lightblue')
plt.xlabel('Total Goals per Match')
plt.ylabel('Number of Matches')
plt.title('Distribution of Total Goals per Match')
plt.grid(axis='y', alpha=0.3)

# Add value labels
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.2,
             f'{int(height)}', ha='center', va='bottom', fontsize=10)

# 2. Draw percentage by total goals
plt.subplot(2, 3, 2)
plt.plot(outcome_summary['Total_Goals'], outcome_summary['Draw_%'], 
         marker='o', linewidth=3, markersize=8, color='red')
plt.xlabel('Total Goals in Match')
plt.ylabel('Draw Percentage (%)')
plt.title('Draw Probability by Total Goals')
plt.grid(alpha=0.3)

# Add value labels
for _, row in outcome_summary.iterrows():
    plt.annotate(f"{row['Draw_%']:.1f}%", 
                (row['Total_Goals'], row['Draw_%']), 
                textcoords="offset points", xytext=(0,10), ha='center')

# 3. Outcome distribution stacked bar
plt.subplot(2, 3, 3)
x = outcome_summary['Total_Goals']
draws = outcome_summary['Draw_%']
wins = outcome_summary['Win_%']

bars1 = plt.bar(x, draws, label='Draws', alpha=0.8, color='orange')
bars2 = plt.bar(x, wins, bottom=draws, label='Decisive', alpha=0.8, color='green')

plt.xlabel('Total Goals in Match')
plt.ylabel('Percentage of Matches (%)')
plt.title('Match Outcomes by Total Goals')
plt.legend()
plt.grid(axis='y', alpha=0.3)

# 4. Goals by stage
plt.subplot(2, 3, 4)
stage_names = [item['Stage'][:8] + '..' if len(item['Stage']) > 8 else item['Stage'] for item in stage_goals]
stage_avg_goals = [item['Avg_Goals'] for item in stage_goals]

bars = plt.bar(stage_names, stage_avg_goals, alpha=0.8, color='lightgreen')
plt.xlabel('Tournament Stage')
plt.ylabel('Average Goals per Match')
plt.title('Average Goals by Tournament Stage')
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', alpha=0.3)

# Add value labels
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.05,
             f'{height:.2f}', ha='center', va='bottom', fontsize=10)

# 5. Detailed goals distribution heatmap
plt.subplot(2, 3, 5)
# Create matrix for heatmap
max_goals = goals_df['total_goals'].max()
heatmap_data = np.zeros((len(stages), max_goals + 1))

for i, stage in enumerate(stages):
    stage_matches = goals_df[goals_df['stage'] == stage]
    if len(stage_matches) > 0:
        stage_dist = stage_matches['total_goals'].value_counts()
        total_stage_matches = len(stage_matches)
        for goals in range(max_goals + 1):
            if goals in stage_dist.index:
                heatmap_data[i, goals] = (stage_dist[goals] / total_stage_matches) * 100

# Create heatmap
sns.heatmap(heatmap_data, 
            xticklabels=list(range(max_goals + 1)),
            yticklabels=[stage[:8] + '..' if len(stage) > 8 else stage for stage in stages],
            annot=True, fmt='.1f', cmap='Blues',
            cbar_kws={'label': 'Percentage of Matches (%)'})
plt.title('Goals Distribution by Stage (%)')
plt.xlabel('Total Goals per Match')
plt.ylabel('Tournament Stage')

# 6. Cumulative goals distribution
plt.subplot(2, 3, 6)
cumulative_pct = (goals_distribution.cumsum() / total_matches) * 100
plt.plot(goals_distribution.index, cumulative_pct, 
         marker='s', linewidth=3, markersize=8, color='purple')
plt.xlabel('Total Goals per Match')
plt.ylabel('Cumulative Percentage (%)')
plt.title('Cumulative Goals Distribution')
plt.grid(alpha=0.3)

# Add specific percentages
for goals, cum_pct in cumulative_pct.items():
    plt.annotate(f"{cum_pct:.1f}%", 
                (goals, cum_pct), 
                textcoords="offset points", xytext=(0,10), ha='center')

plt.tight_layout()
plt.savefig('goals_per_match_distribution_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# ===== STATISTICAL INSIGHTS =====
print("\n" + "="*80)
print("STATISTICAL INSIGHTS")
print("="*80)

# Find key patterns
most_common_goals = goals_distribution.idxmax()
most_common_count = goals_distribution.max()
most_common_pct = (most_common_count / total_matches) * 100

highest_draw_goals = outcome_summary.loc[outcome_summary['Draw_%'].idxmax(), 'Total_Goals']
highest_draw_rate = outcome_summary['Draw_%'].max()

lowest_draw_goals = outcome_summary.loc[outcome_summary['Draw_%'].idxmin(), 'Total_Goals']
lowest_draw_rate = outcome_summary['Draw_%'].min()

print(f"GOAL SCORING PATTERNS:")
print(f"Most common: {most_common_goals} goals ({most_common_count} matches, {most_common_pct:.1f}%)")
print(f"Tournament average: {avg_goals:.2f} goals per match")

print(f"\nDRAW PATTERNS:")
print(f"Highest draw rate: {highest_draw_goals} goals ({highest_draw_rate:.1f}%)")
print(f"Lowest draw rate: {lowest_draw_goals} goals ({lowest_draw_rate:.1f}%)")

# Calculate low/high scoring games
low_scoring = len(goals_df[goals_df['total_goals'] <= 1])
high_scoring = len(goals_df[goals_df['total_goals'] >= 4])
low_scoring_pct = (low_scoring / total_matches) * 100
high_scoring_pct = (high_scoring / total_matches) * 100

print(f"\nSCORING CATEGORIES:")
print(f"Low-scoring (0-1 goals): {low_scoring} matches ({low_scoring_pct:.1f}%)")
print(f"High-scoring (4+ goals): {high_scoring} matches ({high_scoring_pct:.1f}%)")

# ===== SAVE RESULTS =====
print("\n" + "="*80)
print("SAVING RESULTS")
print("="*80)

# Save detailed analysis
goals_df.to_csv('goals_per_match_detailed.csv', index=False)

# Save outcome summary
outcome_summary.to_csv('goals_outcome_distribution.csv', index=False)

print("Files saved:")
print("- goals_per_match_distribution_analysis.png")
print("- goals_per_match_detailed.csv")
print("- goals_outcome_distribution.csv")

print(f"\n=== GOALS ANALYSIS COMPLETE ===")
print(f"Most common: {most_common_goals} goals per match ({most_common_pct:.1f}%)")
print(f"Draw sweet spot: {highest_draw_goals} goals ({highest_draw_rate:.1f}% draws)")
print(f"Tournament character: {low_scoring_pct:.1f}% low-scoring, {high_scoring_pct:.1f}% high-scoring") 