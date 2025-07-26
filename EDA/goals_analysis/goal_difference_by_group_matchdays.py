import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ast

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

print("=== EURO 2024 GROUP STAGE GOAL DIFFERENCE BY MATCHDAYS ANALYSIS ===")
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

# Filter only Group Stage matches
group_matches = matches[matches['stage'] == 'Group Stage'].copy()

print(f"Group Stage matches: {len(group_matches)}")

# ===== ANALYZE BY GROUP STAGE MATCHDAYS =====
print("\n" + "="*80)
print("ANALYZING GOAL DIFFERENCES BY GROUP STAGE MATCHDAYS")
print("="*80)

matchday_analysis = []

for _, match in group_matches.iterrows():
    match_id = match['match_id']
    match_events = events[events['match_id'] == match_id].copy()
    
    if len(match_events) == 0:
        continue
    
    # Get team information
    home_team_id = match['home_team_id'] 
    away_team_id = match['away_team_id']
    matchday = match['match_week']
    
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
    
    # Check for extra time (shouldn't be any in group stage, but let's check)
    max_period = match_events['period'].max()
    has_extra_time = max_period > 2
    
    matchday_analysis.append({
        'match_id': match_id,
        'matchday': matchday,
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
matchday_df = pd.DataFrame(matchday_analysis)

print(f"Successfully analyzed {len(matchday_df)} group stage matches across {matchday_df['matchday'].nunique()} matchdays")

# ===== MATCHDAY-BY-MATCHDAY ANALYSIS =====
print("\n" + "="*80)
print("GOAL DIFFERENCE ANALYSIS BY GROUP STAGE MATCHDAY")
print("="*80)

# Group by matchday
matchdays = [1, 2, 3]
matchday_stats = []

for matchday in matchdays:
    md_matches = matchday_df[matchday_df['matchday'] == matchday]
    
    if len(md_matches) == 0:
        continue
    
    # Basic statistics
    num_matches = len(md_matches)
    
    # Halftime statistics
    ht_draws = len(md_matches[md_matches['ht_goal_diff'] == 0])
    ht_1_goal = len(md_matches[md_matches['ht_goal_diff'] == 1])
    ht_2_goal = len(md_matches[md_matches['ht_goal_diff'] == 2])
    ht_3plus_goal = len(md_matches[md_matches['ht_goal_diff'] >= 3])
    
    # Full-time statistics
    ft_draws = len(md_matches[md_matches['ft_goal_diff'] == 0])
    ft_1_goal = len(md_matches[md_matches['ft_goal_diff'] == 1])
    ft_2_goal = len(md_matches[md_matches['ft_goal_diff'] == 2])
    ft_3plus_goal = len(md_matches[md_matches['ft_goal_diff'] >= 3])
    
    # Averages
    avg_ht_diff = md_matches['ht_goal_diff'].mean()
    avg_ft_diff = md_matches['ft_goal_diff'].mean()
    avg_total_goals = md_matches['total_goals'].mean()
    
    # Extra time (should be 0 for group stage)
    extra_time_matches = md_matches['has_extra_time'].sum()
    
    matchday_stats.append({
        'Matchday': f'Matchday {matchday}',
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
        'Extra_Time_%': (extra_time_matches/num_matches)*100 if num_matches > 0 else 0
    })

# Create summary DataFrame
matchday_summary = pd.DataFrame(matchday_stats)

print("GOAL DIFFERENCE DISTRIBUTION BY GROUP STAGE MATCHDAY:")
print("="*70)

for _, row in matchday_summary.iterrows():
    print(f"\n{row['Matchday'].upper()} ({row['Matches']} matches):")
    print(f"  Halftime Draws: {row['HT_Draws']} ({row['HT_Draws_%']:.1f}%)")
    print(f"  Full-time Draws: {row['FT_Draws']} ({row['FT_Draws_%']:.1f}%)")
    print(f"  1-Goal Games (FT): {row['FT_1Goal']} ({row['FT_1Goal_%']:.1f}%)")
    print(f"  2+ Goal Margins (FT): {row['FT_2+Goal']} ({row['FT_2+Goal_%']:.1f}%)")
    print(f"  Avg Goal Difference: HT {row['Avg_HT_Diff']:.2f} -> FT {row['Avg_FT_Diff']:.2f}")
    print(f"  Avg Total Goals: {row['Avg_Goals']:.2f}")
    if row['Extra_Time'] > 0:
        print(f"  Extra Time: {row['Extra_Time']} matches ({row['Extra_Time_%']:.1f}%)")

# ===== PROGRESSION ANALYSIS =====
print("\n" + "="*80)
print("GROUP STAGE PROGRESSION TRENDS")
print("="*80)

print("DRAW PERCENTAGE EVOLUTION ACROSS MATCHDAYS:")
print("Matchday" + " "*10 + "HT Draws" + " "*5 + "FT Draws" + " "*5 + "Change")
print("-" * 60)
for _, row in matchday_summary.iterrows():
    change = row['FT_Draws_%'] - row['HT_Draws_%']
    print(f"{row['Matchday']:<15} {row['HT_Draws_%']:>6.1f}%   {row['FT_Draws_%']:>6.1f}%   {change:>+6.1f}%")

print(f"\nCLOSE GAMES (0-1 Goal Difference at FT) BY MATCHDAY:")
for _, row in matchday_summary.iterrows():
    close_games = row['FT_Draws_%'] + row['FT_1Goal_%']
    print(f"{row['Matchday']:<15} {close_games:>6.1f}%")

print(f"\nDECISIVE GAMES (2+ Goal Difference at FT) BY MATCHDAY:")
for _, row in matchday_summary.iterrows():
    print(f"{row['Matchday']:<15} {row['FT_2+Goal_%']:>6.1f}%")

print(f"\nGOALS PER MATCH PROGRESSION:")
for _, row in matchday_summary.iterrows():
    print(f"{row['Matchday']:<15} {row['Avg_Goals']:>6.2f} goals/match")

# ===== TACTICAL EVOLUTION =====
print("\n" + "="*80)
print("TACTICAL EVOLUTION ACROSS GROUP STAGE")
print("="*80)

# Calculate competitiveness metrics
competitiveness_trend = []
for _, row in matchday_summary.iterrows():
    close_games_pct = row['FT_Draws_%'] + row['FT_1Goal_%']
    decisive_games_pct = row['FT_2+Goal_%']
    avg_separation = row['Avg_FT_Diff']
    
    competitiveness_trend.append({
        'Matchday': row['Matchday'],
        'Close_Games_%': close_games_pct,
        'Decisive_Games_%': decisive_games_pct,
        'Avg_Separation': avg_separation,
        'Goals_Per_Match': row['Avg_Goals']
    })

print("COMPETITIVENESS EVOLUTION:")
print("Matchday" + " "*8 + "Close Games" + " "*3 + "Decisive" + " "*5 + "Avg Sep" + " "*3 + "Goals/Match")
print("-" * 75)
for item in competitiveness_trend:
    print(f"{item['Matchday']:<15} {item['Close_Games_%']:>8.1f}%   {item['Decisive_Games_%']:>8.1f}%   {item['Avg_Separation']:>6.2f}   {item['Goals_Per_Match']:>8.2f}")

# ===== VISUALIZATION =====
print("\n" + "="*80)
print("CREATING VISUALIZATIONS")
print("="*80)

fig = plt.figure(figsize=(20, 15))

# 1. Goal difference evolution by matchday
plt.subplot(2, 3, 1)
x = np.arange(len(matchday_summary))
width = 0.35

bars1 = plt.bar(x - width/2, matchday_summary['Avg_HT_Diff'], width, 
                label='Halftime', alpha=0.8, color='skyblue')
bars2 = plt.bar(x + width/2, matchday_summary['Avg_FT_Diff'], width, 
                label='Full-time', alpha=0.8, color='lightcoral')

plt.xlabel('Group Stage Matchday')
plt.ylabel('Average Goal Difference')
plt.title('Average Goal Difference by Matchday')
plt.xticks(x, matchday_summary['Matchday'], rotation=0)
plt.legend()
plt.grid(axis='y', alpha=0.3)

# Add value labels
for bar in bars1:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
             f'{height:.2f}', ha='center', va='bottom', fontsize=10)
for bar in bars2:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
             f'{height:.2f}', ha='center', va='bottom', fontsize=10)

# 2. Draw percentage by matchday
plt.subplot(2, 3, 2)
bars1 = plt.bar(x - width/2, matchday_summary['HT_Draws_%'], width, 
                label='Halftime', alpha=0.8, color='skyblue')
bars2 = plt.bar(x + width/2, matchday_summary['FT_Draws_%'], width, 
                label='Full-time', alpha=0.8, color='lightcoral')

plt.xlabel('Group Stage Matchday')
plt.ylabel('Draw Percentage (%)')
plt.title('Draw Percentage by Matchday')
plt.xticks(x, matchday_summary['Matchday'], rotation=0)
plt.legend()
plt.grid(axis='y', alpha=0.3)

# 3. Close vs Decisive games evolution
plt.subplot(2, 3, 3)
close_games = matchday_summary['FT_Draws_%'] + matchday_summary['FT_1Goal_%']
decisive_games = matchday_summary['FT_2+Goal_%']

plt.plot(x, close_games, marker='o', linewidth=3, markersize=8, label='Close Games (0-1 goal)', color='orange')
plt.plot(x, decisive_games, marker='s', linewidth=3, markersize=8, label='Decisive Games (2+ goals)', color='red')

plt.xlabel('Group Stage Matchday')
plt.ylabel('Percentage of Matches (%)')
plt.title('Competitiveness Evolution Across Matchdays')
plt.xticks(x, matchday_summary['Matchday'], rotation=0)
plt.legend()
plt.grid(alpha=0.3)

# 4. Goals per match progression
plt.subplot(2, 3, 4)
bars = plt.bar(x, matchday_summary['Avg_Goals'], alpha=0.8, color='lightgreen')
plt.xlabel('Group Stage Matchday')
plt.ylabel('Average Goals per Match')
plt.title('Goal Scoring Evolution by Matchday')
plt.xticks(x, matchday_summary['Matchday'], rotation=0)
plt.grid(axis='y', alpha=0.3)

# Add value labels
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.05,
             f'{height:.2f}', ha='center', va='bottom', fontsize=10)

# 5. Detailed matchday comparison heatmap
plt.subplot(2, 3, 5)
heatmap_data = matchday_summary[['HT_Draws_%', 'FT_Draws_%', 'FT_1Goal_%', 'FT_2+Goal_%', 'Avg_Goals']].T
heatmap_data.columns = matchday_summary['Matchday']

sns.heatmap(heatmap_data, annot=True, fmt='.1f', cmap='RdYlBu_r', 
            cbar_kws={'label': 'Percentage (%) / Goals'})
plt.title('Match Characteristics by Matchday')
plt.ylabel('Match Metric')

# 6. Stacked distribution by matchday
plt.subplot(2, 3, 6)
draws = matchday_summary['FT_Draws_%']
one_goal = matchday_summary['FT_1Goal_%'] 
two_plus = matchday_summary['FT_2+Goal_%']

bars1 = plt.bar(x, draws, label='Draws (0)', alpha=0.8, color='lightblue')
bars2 = plt.bar(x, one_goal, bottom=draws, label='1 Goal', alpha=0.8, color='orange')
bars3 = plt.bar(x, two_plus, bottom=draws+one_goal, label='2+ Goals', alpha=0.8, color='red')

plt.xlabel('Group Stage Matchday')
plt.ylabel('Percentage of Matches (%)')
plt.title('Goal Difference Distribution by Matchday')
plt.xticks(x, matchday_summary['Matchday'], rotation=0)
plt.legend()
plt.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('goal_difference_group_matchdays_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# ===== STATISTICAL INSIGHTS =====
print("\n" + "="*80)
print("STATISTICAL INSIGHTS")
print("="*80)

# Most competitive matchday
most_draws_md = matchday_summary.loc[matchday_summary['FT_Draws_%'].idxmax(), 'Matchday']
most_close_md_idx = (matchday_summary['FT_Draws_%'] + matchday_summary['FT_1Goal_%']).idxmax()
most_close_md = matchday_summary.loc[most_close_md_idx, 'Matchday']
most_decisive_md = matchday_summary.loc[matchday_summary['FT_2+Goal_%'].idxmax(), 'Matchday']
highest_scoring_md = matchday_summary.loc[matchday_summary['Avg_Goals'].idxmax(), 'Matchday']

print(f"GROUP STAGE COMPETITIVENESS RANKINGS:")
print(f"Most draws: {most_draws_md} ({matchday_summary.loc[matchday_summary['FT_Draws_%'].idxmax(), 'FT_Draws_%']:.1f}%)")
print(f"Most close games (0-1 goal): {most_close_md} ({(matchday_summary['FT_Draws_%'] + matchday_summary['FT_1Goal_%']).max():.1f}%)")
print(f"Most decisive games (2+ goals): {most_decisive_md} ({matchday_summary.loc[matchday_summary['FT_2+Goal_%'].idxmax(), 'FT_2+Goal_%']:.1f}%)")
print(f"Highest scoring: {highest_scoring_md} ({matchday_summary.loc[matchday_summary['Avg_Goals'].idxmax(), 'Avg_Goals']:.2f} goals/match)")

# Progression trends
md1_draws = matchday_summary[matchday_summary['Matchday'] == 'Matchday 1']['FT_Draws_%'].iloc[0]
md3_draws = matchday_summary[matchday_summary['Matchday'] == 'Matchday 3']['FT_Draws_%'].iloc[0]
md1_goals = matchday_summary[matchday_summary['Matchday'] == 'Matchday 1']['Avg_Goals'].iloc[0]
md3_goals = matchday_summary[matchday_summary['Matchday'] == 'Matchday 3']['Avg_Goals'].iloc[0]

print(f"\nGROUP STAGE PROGRESSION:")
print(f"Draw percentage: Matchday 1 {md1_draws:.1f}% -> Matchday 3 {md3_draws:.1f}% ({md3_draws-md1_draws:+.1f}%)")
print(f"Goals per match: Matchday 1 {md1_goals:.2f} -> Matchday 3 {md3_goals:.2f} ({md3_goals-md1_goals:+.2f})")

# Calculate trend direction
draw_trend = "increasing" if md3_draws > md1_draws else "decreasing"
goal_trend = "increasing" if md3_goals > md1_goals else "decreasing"
print(f"Trend: Draws are {draw_trend}, goals are {goal_trend} across group stage")

# ===== SAVE RESULTS =====
print("\n" + "="*80)
print("SAVING RESULTS")
print("="*80)

# Save detailed matchday analysis
matchday_df.to_csv('goal_difference_group_matchdays_detailed.csv', index=False)

# Save matchday summary
matchday_summary.to_csv('goal_difference_group_matchdays_summary.csv', index=False)

print("Files saved:")
print("- goal_difference_group_matchdays_analysis.png")
print("- goal_difference_group_matchdays_detailed.csv")
print("- goal_difference_group_matchdays_summary.csv")

print(f"\n=== GROUP STAGE ANALYSIS COMPLETE ===")
print(f"Most competitive: {most_close_md}")
print(f"Most decisive: {most_decisive_md}")
print(f"Highest scoring: {highest_scoring_md}")
print(f"Overall trend: Group stage becomes {draw_trend.upper()} in draws, {goal_trend.upper()} in goals") 