import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ast

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

print("=== EURO 2024 GOAL DIFFERENCE ANALYSIS ===")
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

# ===== ANALYZE MATCHES FOR GOAL DIFFERENCES =====
print("\n" + "="*80)
print("ANALYZING GOAL DIFFERENCES")
print("="*80)

goal_diff_analysis = []

for _, match in matches.iterrows():
    match_id = match['match_id']
    match_events = events[events['match_id'] == match_id].copy()
    
    if len(match_events) == 0:
        continue
    
    # Get team information
    home_team_id = match['home_team_id'] 
    away_team_id = match['away_team_id']
    
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
    ht_goal_diff = ht_home_goals - ht_away_goals
    ft_goal_diff = ft_home_goals - ft_away_goals
    
    # Check for extra time/penalties
    # Check if match has periods beyond 2 (extra time)
    max_period = match_events['period'].max()
    has_extra_time = max_period > 2
    
    # For penalties, we'd need to check if it's a knockout stage draw
    # Knockout stages in Euro 2024: Round of 16, Quarter-finals, Semi-finals, Final
    knockout_stages = ['Round of 16', 'Quarter-finals', 'Semi-finals', 'Final']
    is_knockout = match['stage'] in knockout_stages
    went_to_penalties = is_knockout and ft_goal_diff == 0 and has_extra_time
    
    goal_diff_analysis.append({
        'match_id': match_id,
        'home_team': match['home_team_name'],
        'away_team': match['away_team_name'],
        'stage': match['stage'],
        'ht_home': ht_home_goals,
        'ht_away': ht_away_goals,
        'ht_goal_diff': ht_goal_diff,
        'ht_abs_diff': abs(ht_goal_diff),
        'ft_home': ft_home_goals,
        'ft_away': ft_away_goals,
        'ft_goal_diff': ft_goal_diff,
        'ft_abs_diff': abs(ft_goal_diff),
        'has_extra_time': has_extra_time,
        'went_to_penalties': went_to_penalties,
        'is_knockout': is_knockout
    })

# Create DataFrame
diff_df = pd.DataFrame(goal_diff_analysis)

print(f"Successfully analyzed {len(diff_df)} matches")

# ===== HALFTIME GOAL DIFFERENCE ANALYSIS =====
print("\n" + "="*80)
print("HALFTIME GOAL DIFFERENCE DISTRIBUTION")
print("="*80)

ht_diff_counts = diff_df['ht_abs_diff'].value_counts().sort_index()

print("HALFTIME RESULTS BY GOAL DIFFERENCE:")
total_matches = len(diff_df)

for diff in sorted(ht_diff_counts.index):
    count = ht_diff_counts[diff]
    percentage = (count / total_matches) * 100
    
    if diff == 0:
        print(f"Draw (0 goal difference): {count} matches ({percentage:.1f}%)")
    else:
        print(f"{diff} goal difference: {count} matches ({percentage:.1f}%)")

# ===== FULL-TIME GOAL DIFFERENCE ANALYSIS =====
print("\n" + "="*80)
print("FULL-TIME GOAL DIFFERENCE DISTRIBUTION")
print("="*80)

ft_diff_counts = diff_df['ft_abs_diff'].value_counts().sort_index()

print("FULL-TIME RESULTS BY GOAL DIFFERENCE:")

for diff in sorted(ft_diff_counts.index):
    count = ft_diff_counts[diff]
    percentage = (count / total_matches) * 100
    
    if diff == 0:
        # Separate draws by extra time/penalties
        draws = diff_df[diff_df['ft_abs_diff'] == 0]
        regular_draws = len(draws[~draws['has_extra_time']])
        extra_time_draws = len(draws[draws['has_extra_time'] & ~draws['went_to_penalties']])
        penalty_wins = len(draws[draws['went_to_penalties']])
        
        print(f"Draw (0 goal difference): {count} matches ({percentage:.1f}%)")
        print(f"  - Regular time draws: {regular_draws} matches")
        if extra_time_draws > 0:
            print(f"  - Extra time draws: {extra_time_draws} matches")
        if penalty_wins > 0:
            print(f"  - Decided by penalties: {penalty_wins} matches")
    else:
        # Check if any went to extra time
        diff_matches = diff_df[diff_df['ft_abs_diff'] == diff]
        extra_time_wins = len(diff_matches[diff_matches['has_extra_time']])
        regular_wins = count - extra_time_wins
        
        print(f"{diff} goal difference: {count} matches ({percentage:.1f}%)")
        if extra_time_wins > 0:
            print(f"  - Regular time: {regular_wins} matches")
            print(f"  - After extra time: {extra_time_wins} matches")

# ===== SPECIAL CASES ANALYSIS =====
print("\n" + "="*80)
print("SPECIAL CASES ANALYSIS")
print("="*80)

# Extra time matches
extra_time_matches = diff_df[diff_df['has_extra_time']]
print(f"MATCHES THAT WENT TO EXTRA TIME: {len(extra_time_matches)}")
if len(extra_time_matches) > 0:
    for _, match in extra_time_matches.iterrows():
        print(f"  {match['home_team']} vs {match['away_team']} ({match['stage']}): "
              f"HT {match['ht_home']}-{match['ht_away']}, FT {match['ft_home']}-{match['ft_away']}")

# Penalty shootouts
penalty_matches = diff_df[diff_df['went_to_penalties']]
print(f"\nMATCHES DECIDED BY PENALTIES: {len(penalty_matches)}")
if len(penalty_matches) > 0:
    for _, match in penalty_matches.iterrows():
        print(f"  {match['home_team']} vs {match['away_team']} ({match['stage']}): "
              f"HT {match['ht_home']}-{match['ht_away']}, FT {match['ft_home']}-{match['ft_away']}")

# ===== COMPARISON ANALYSIS =====
print("\n" + "="*80)
print("HALFTIME vs FULL-TIME COMPARISON")
print("="*80)

# Create comparison table
comparison_data = []
max_diff = max(ht_diff_counts.index.max(), ft_diff_counts.index.max())

for diff in range(max_diff + 1):
    ht_count = ht_diff_counts.get(diff, 0)
    ft_count = ft_diff_counts.get(diff, 0)
    ht_pct = (ht_count / total_matches) * 100
    ft_pct = (ft_count / total_matches) * 100
    change = ft_count - ht_count
    
    comparison_data.append({
        'Goal_Difference': diff,
        'Halftime_Count': ht_count,
        'Halftime_Percent': ht_pct,
        'Fulltime_Count': ft_count,
        'Fulltime_Percent': ft_pct,
        'Change': change
    })

comparison_df = pd.DataFrame(comparison_data)

print("GOAL DIFFERENCE COMPARISON TABLE:")
print(comparison_df.to_string(index=False, float_format='%.1f'))

# ===== VISUALIZATION =====
print("\n" + "="*80)
print("CREATING VISUALIZATIONS")
print("="*80)

fig = plt.figure(figsize=(20, 15))

# 1. Halftime vs Full-time goal difference comparison
plt.subplot(2, 3, 1)
x = np.arange(len(comparison_df))
width = 0.35

bars1 = plt.bar(x - width/2, comparison_df['Halftime_Count'], width, 
                label='Halftime', alpha=0.8, color='skyblue')
bars2 = plt.bar(x + width/2, comparison_df['Fulltime_Count'], width, 
                label='Full-time', alpha=0.8, color='lightcoral')

plt.xlabel('Goal Difference')
plt.ylabel('Number of Matches')
plt.title('Goal Difference Distribution\nHalftime vs Full-time')
plt.xticks(x, comparison_df['Goal_Difference'])
plt.legend()
plt.grid(axis='y', alpha=0.3)

# Add value labels
for bar in bars1:
    height = bar.get_height()
    if height > 0:
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                 f'{int(height)}', ha='center', va='bottom', fontsize=10)
for bar in bars2:
    height = bar.get_height()
    if height > 0:
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                 f'{int(height)}', ha='center', va='bottom', fontsize=10)

# 2. Percentage comparison
plt.subplot(2, 3, 2)
bars1 = plt.bar(x - width/2, comparison_df['Halftime_Percent'], width, 
                label='Halftime', alpha=0.8, color='skyblue')
bars2 = plt.bar(x + width/2, comparison_df['Fulltime_Percent'], width, 
                label='Full-time', alpha=0.8, color='lightcoral')

plt.xlabel('Goal Difference')
plt.ylabel('Percentage of Matches (%)')
plt.title('Goal Difference Distribution (%)\nHalftime vs Full-time')
plt.xticks(x, comparison_df['Goal_Difference'])
plt.legend()
plt.grid(axis='y', alpha=0.3)

# 3. Change in distribution
plt.subplot(2, 3, 3)
colors = ['green' if change >= 0 else 'red' for change in comparison_df['Change']]
bars = plt.bar(x, comparison_df['Change'], color=colors, alpha=0.7)

plt.xlabel('Goal Difference')
plt.ylabel('Change in Number of Matches\n(Full-time - Halftime)')
plt.title('Change in Goal Difference Distribution')
plt.xticks(x, comparison_df['Goal_Difference'])
plt.axhline(y=0, color='black', linestyle='-', alpha=0.5)
plt.grid(axis='y', alpha=0.3)

# Add value labels
for i, bar in enumerate(bars):
    height = bar.get_height()
    if height != 0:
        plt.text(bar.get_x() + bar.get_width()/2., height + (0.2 if height > 0 else -0.5),
                 f'{int(height):+d}', ha='center', va='bottom' if height > 0 else 'top', fontsize=10)

# 4. Special cases breakdown
plt.subplot(2, 3, 4)
special_cases = ['Regular\nTime', 'Extra Time', 'Penalties']
special_counts = [
    len(diff_df[~diff_df['has_extra_time']]),
    len(diff_df[diff_df['has_extra_time'] & ~diff_df['went_to_penalties']]),
    len(diff_df[diff_df['went_to_penalties']])
]

bars = plt.bar(special_cases, special_counts, 
               color=['lightblue', 'orange', 'red'], alpha=0.8)
plt.ylabel('Number of Matches')
plt.title('Match Duration Categories')
plt.grid(axis='y', alpha=0.3)

# Add value labels
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
             f'{int(height)}', ha='center', va='bottom', fontweight='bold')

# 5. Knockout vs Group stage draws
plt.subplot(2, 3, 5)
group_draws = len(diff_df[(diff_df['ft_abs_diff'] == 0) & ~diff_df['is_knockout']])
knockout_regular_draws = len(diff_df[(diff_df['ft_abs_diff'] == 0) & diff_df['is_knockout'] & ~diff_df['has_extra_time']])
knockout_extra_draws = len(diff_df[(diff_df['ft_abs_diff'] == 0) & diff_df['is_knockout'] & diff_df['has_extra_time']])

draw_categories = ['Group Stage\nDraws', 'Knockout\nRegular Draws', 'Knockout\nExtra Time']
draw_counts = [group_draws, knockout_regular_draws, knockout_extra_draws]

bars = plt.bar(draw_categories, draw_counts, 
               color=['lightgreen', 'yellow', 'orange'], alpha=0.8)
plt.ylabel('Number of Matches')
plt.title('Draw Distribution by Stage')
plt.grid(axis='y', alpha=0.3)

# Add value labels
for bar in bars:
    height = bar.get_height()
    if height > 0:
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                 f'{int(height)}', ha='center', va='bottom', fontweight='bold')

# 6. Goal difference evolution
plt.subplot(2, 3, 6)
# Show how goal differences change from HT to FT
evolution_data = []
for ht_diff in range(max_diff + 1):
    for ft_diff in range(max_diff + 1):
        count = len(diff_df[(diff_df['ht_abs_diff'] == ht_diff) & (diff_df['ft_abs_diff'] == ft_diff)])
        if count > 0:
            evolution_data.append([ht_diff, ft_diff, count])

# Create a simple evolution chart
ht_values = [row[0] for row in evolution_data]
ft_values = [row[1] for row in evolution_data]
sizes = [row[2] * 20 for row in evolution_data]  # Scale for visibility

scatter = plt.scatter(ht_values, ft_values, s=sizes, alpha=0.6, c=sizes, cmap='viridis')
plt.xlabel('Halftime Goal Difference')
plt.ylabel('Full-time Goal Difference')
plt.title('Goal Difference Evolution\n(Size = Number of Matches)')
plt.plot([0, max_diff], [0, max_diff], 'r--', alpha=0.5, label='No change line')
plt.legend()
plt.grid(True, alpha=0.3)

# Add colorbar
plt.colorbar(scatter, label='Number of Matches')

plt.tight_layout()
plt.savefig('goal_difference_complete_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# ===== SAVE RESULTS =====
print("\n" + "="*80)
print("SAVING RESULTS")
print("="*80)

# Save detailed analysis
diff_df.to_csv('goal_difference_detailed_analysis.csv', index=False)

# Save comparison table
comparison_df.to_csv('goal_difference_comparison.csv', index=False)

# Save summary statistics
summary_stats = {
    'Category': ['Total Matches', 'HT Draws', 'FT Draws', 'FT Regular Draws', 'FT Extra Time', 'Penalties',
                'Most Common HT Diff', 'Most Common FT Diff', 'Biggest HT Diff', 'Biggest FT Diff'],
    'Count': [total_matches, ht_diff_counts[0], ft_diff_counts[0], 
             len(diff_df[(diff_df['ft_abs_diff'] == 0) & ~diff_df['has_extra_time']]),
             len(diff_df[diff_df['has_extra_time']]), len(diff_df[diff_df['went_to_penalties']]),
             ht_diff_counts.index[0], ft_diff_counts.index[0], 
             ht_diff_counts.index.max(), ft_diff_counts.index.max()]
}
summary_df = pd.DataFrame(summary_stats)
summary_df.to_csv('goal_difference_summary.csv', index=False)

print("Files saved:")
print("- goal_difference_complete_analysis.png")
print("- goal_difference_detailed_analysis.csv")
print("- goal_difference_comparison.csv")
print("- goal_difference_summary.csv")

print(f"\n=== ANALYSIS COMPLETE ===")
print(f"Key Findings:")
print(f"- Draws decrease from {ht_diff_counts[0]} at HT to {ft_diff_counts[0]} at FT")
print(f"- {len(diff_df[diff_df['has_extra_time']])} matches went to extra time")
print(f"- {len(diff_df[diff_df['went_to_penalties']])} matches decided by penalties")
print(f"- Most common margin: {ht_diff_counts.index[0]} goals at HT, {ft_diff_counts.index[0]} goals at FT") 