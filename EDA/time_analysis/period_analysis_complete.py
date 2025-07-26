import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ast

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

print("=== EURO 2024 PERIOD ANALYSIS: FIRST HALF vs SECOND HALF ===")
print("Loading and processing data...")

# Load the events data
events = pd.read_csv('../Data/events_complete.csv')

# Parse the type column to extract the name
def extract_type_name(type_str):
    try:
        if pd.isna(type_str):
            return None
        type_dict = ast.literal_eval(str(type_str))
        return type_dict.get('name', None)
    except:
        return str(type_str)

# Extract event type names
events['type_name'] = events['type'].apply(extract_type_name)

# Filter for periods 1 and 2 only
period_events = events[events['period'].isin([1, 2])].copy()

# ===== PERIOD STATISTICS ANALYSIS =====
print("\n" + "="*80)
print("PERIOD STATISTICS ANALYSIS")
print("="*80)

p1_events = period_events[period_events['period'] == 1]
p2_events = period_events[period_events['period'] == 2]

# Basic event counts
p1_total = len(p1_events)
p2_total = len(p2_events)

print(f'Period 1 (First Half): {p1_total:,} events')
print(f'Period 2 (Second Half): {p2_total:,} events')
print(f'Difference: {p1_total - p2_total:,} (+{((p1_total/p2_total - 1) * 100):.1f}% more in first half)')

# Goals analysis
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

period_events['shot_outcome_id'] = period_events['shot'].apply(extract_shot_outcome)

# Goals (outcome ID 97)
goals_p1 = len(period_events[(period_events['period'] == 1) & (period_events['shot_outcome_id'] == 97)])
goals_p2 = len(period_events[(period_events['period'] == 2) & (period_events['shot_outcome_id'] == 97)])

# Shots (all shots)
shots_p1 = len(period_events[(period_events['period'] == 1) & (period_events['shot_outcome_id'].notna())])
shots_p2 = len(period_events[(period_events['period'] == 2) & (period_events['shot_outcome_id'].notna())])

# Yellow cards
def extract_card_type(bad_behaviour_str):
    try:
        if pd.isna(bad_behaviour_str):
            return None
        bad_dict = ast.literal_eval(str(bad_behaviour_str))
        card = bad_dict.get('card', {})
        if isinstance(card, dict):
            return card.get('name', None)
        return None
    except:
        return None

period_events['card_type'] = period_events['bad_behaviour'].apply(extract_card_type)
yellow_p1 = len(period_events[(period_events['period'] == 1) & (period_events['card_type'] == 'Yellow Card')])
yellow_p2 = len(period_events[(period_events['period'] == 2) & (period_events['card_type'] == 'Yellow Card')])

# Substitutions
subs_p1 = len(period_events[(period_events['period'] == 1) & (period_events['type_name'] == 'Substitution')])
subs_p2 = len(period_events[(period_events['period'] == 2) & (period_events['type_name'] == 'Substitution')])

# Create summary statistics table
summary_stats = [
    ['Total Events', p1_total, p2_total, p1_total - p2_total, f'{((p1_total/p2_total - 1) * 100):+.1f}%'],
    ['Goals', goals_p1, goals_p2, goals_p1 - goals_p2, f'{((goals_p1/goals_p2 - 1) * 100) if goals_p2 > 0 else 0:+.1f}%'],
    ['Shots', shots_p1, shots_p2, shots_p1 - shots_p2, f'{((shots_p1/shots_p2 - 1) * 100) if shots_p2 > 0 else 0:+.1f}%'],
    ['Yellow Cards', yellow_p1, yellow_p2, yellow_p1 - yellow_p2, f'{((yellow_p1/yellow_p2 - 1) * 100) if yellow_p2 > 0 else 0:+.1f}%'],
    ['Substitutions', subs_p1, subs_p2, subs_p1 - subs_p2, f'{((subs_p1/subs_p2 - 1) * 100) if subs_p2 > 0 else 0:+.1f}%']
]

summary_df = pd.DataFrame(summary_stats, columns=['Metric', 'Period 1', 'Period 2', 'Difference', 'Change %'])

print('\nSUMMARY STATISTICS TABLE:')
print(summary_df.to_string(index=False))

# Goal-to-shot conversion rates
p1_conversion = (goals_p1 / shots_p1) * 100 if shots_p1 > 0 else 0
p2_conversion = (goals_p2 / shots_p2) * 100 if shots_p2 > 0 else 0
conversion_improvement = ((p2_conversion / p1_conversion) - 1) * 100 if p1_conversion > 0 else 0

print(f'\nCONVERSION EFFICIENCY:')
print(f'Period 1 Goal-to-Shot Ratio: {p1_conversion:.1f}% ({goals_p1}/{shots_p1})')
print(f'Period 2 Goal-to-Shot Ratio: {p2_conversion:.1f}% ({goals_p2}/{shots_p2})')
print(f'Second Half Efficiency Improvement: {conversion_improvement:+.1f}%')

# ===== EVENT DISTRIBUTION VISUALIZATION =====
print("\n" + "="*80)
print("CREATING EVENT DISTRIBUTION VISUALIZATION")
print("="*80)

# Get top 10 event types
all_event_counts = period_events['type_name'].value_counts()
top_10_events = all_event_counts.head(10).index.tolist()

# Create comparison data for visualization
comparison_data = []
for event_type in top_10_events:
    p1_count = len(p1_events[p1_events['type_name'] == event_type])
    p2_count = len(p2_events[p2_events['type_name'] == event_type])
    
    p1_percentage = (p1_count / len(p1_events)) * 100
    p2_percentage = (p2_count / len(p2_events)) * 100
    
    comparison_data.append({
        'Event Type': event_type,
        'Period 1 Count': p1_count,
        'Period 2 Count': p2_count,
        'Period 1 %': p1_percentage,
        'Period 2 %': p2_percentage,
        'Difference': p1_count - p2_count,
        'Percentage Diff': p1_percentage - p2_percentage
    })

comparison_df = pd.DataFrame(comparison_data)

# Create comprehensive visualization
fig = plt.figure(figsize=(20, 15))

# 1. Side-by-side bar chart - Event Counts
plt.subplot(2, 3, 1)
x = np.arange(len(top_10_events))
width = 0.35

bars1 = plt.bar(x - width/2, comparison_df['Period 1 Count'], width, 
                label='First Half', alpha=0.8, color='skyblue')
bars2 = plt.bar(x + width/2, comparison_df['Period 2 Count'], width, 
                label='Second Half', alpha=0.8, color='lightcoral')

plt.xlabel('Event Types')
plt.ylabel('Event Count')
plt.title('Event Counts: First Half vs Second Half')
plt.xticks(x, [event[:10] + '...' if len(event) > 10 else event for event in top_10_events], rotation=45, ha='right')
plt.legend()
plt.grid(axis='y', alpha=0.3)

# Add value labels on bars
for bar in bars1:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 100,
             f'{int(height):,}', ha='center', va='bottom', fontsize=8)
for bar in bars2:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 100,
             f'{int(height):,}', ha='center', va='bottom', fontsize=8)

# 2. Percentage comparison
plt.subplot(2, 3, 2)
bars1 = plt.bar(x - width/2, comparison_df['Period 1 %'], width, 
                label='First Half', alpha=0.8, color='skyblue')
bars2 = plt.bar(x + width/2, comparison_df['Period 2 %'], width, 
                label='Second Half', alpha=0.8, color='lightcoral')

plt.xlabel('Event Types')
plt.ylabel('Percentage of Total Events (%)')
plt.title('Event Percentages: First Half vs Second Half')
plt.xticks(x, [event[:10] + '...' if len(event) > 10 else event for event in top_10_events], rotation=45, ha='right')
plt.legend()
plt.grid(axis='y', alpha=0.3)

# 3. Difference chart
plt.subplot(2, 3, 3)
colors = ['green' if diff > 0 else 'red' for diff in comparison_df['Difference']]
bars = plt.bar(x, comparison_df['Difference'], color=colors, alpha=0.7)

plt.xlabel('Event Types')
plt.ylabel('Event Count Difference (P1 - P2)')
plt.title('Event Count Differences\n(Positive = More in First Half)')
plt.xticks(x, [event[:10] + '...' if len(event) > 10 else event for event in top_10_events], rotation=45, ha='right')
plt.axhline(y=0, color='black', linestyle='-', alpha=0.5)
plt.grid(axis='y', alpha=0.3)

# Add value labels
for i, bar in enumerate(bars):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + (50 if height > 0 else -150),
             f'{int(height):,}', ha='center', va='bottom' if height > 0 else 'top', fontsize=8)

# 4. Summary statistics visualization
plt.subplot(2, 3, 4)
metrics = summary_df['Metric']
p1_values = summary_df['Period 1']
p2_values = summary_df['Period 2']

x_pos = np.arange(len(metrics))
bars1 = plt.bar(x_pos - 0.35, p1_values, 0.3, label='First Half', alpha=0.8, color='skyblue')
bars2 = plt.bar(x_pos, p2_values, 0.3, label='Second Half', alpha=0.8, color='lightcoral')

plt.xlabel('Metrics')
plt.ylabel('Count')
plt.title('Key Statistics Comparison')
plt.xticks(x_pos - 0.175, metrics, rotation=45, ha='right')
plt.legend()
plt.yscale('log')  # Log scale due to large differences
plt.grid(axis='y', alpha=0.3)

# 5. Pie chart - First Half distribution
plt.subplot(2, 3, 5)
p1_counts = comparison_df['Period 1 Count']
p1_others = len(p1_events) - p1_counts.sum()
pie_data_p1 = list(p1_counts) + [p1_others]
pie_labels_p1 = [event[:10] + '...' if len(event) > 10 else event for event in top_10_events] + ['Others']

plt.pie(pie_data_p1, labels=pie_labels_p1, autopct='%1.1f%%', startangle=90)
plt.title(f'First Half Event Distribution\nTotal: {len(p1_events):,} events')

# 6. Pie chart - Second Half distribution
plt.subplot(2, 3, 6)
p2_counts = comparison_df['Period 2 Count']
p2_others = len(p2_events) - p2_counts.sum()
pie_data_p2 = list(p2_counts) + [p2_others]
pie_labels_p2 = [event[:10] + '...' if len(event) > 10 else event for event in top_10_events] + ['Others']

plt.pie(pie_data_p2, labels=pie_labels_p2, autopct='%1.1f%%', startangle=90)
plt.title(f'Second Half Event Distribution\nTotal: {len(p2_events):,} events')

plt.tight_layout()
plt.savefig('period_analysis_complete_visualization.png', dpi=300, bbox_inches='tight')
plt.show()

# ===== SAVE RESULTS =====
print("\n" + "="*80)
print("SAVING RESULTS")
print("="*80)

# Save summary statistics
summary_df.to_csv('period_summary_statistics.csv', index=False)

# Save detailed event comparison
event_comparison_df = comparison_df[['Event Type', 'Period 1 Count', 'Period 1 %', 
                                   'Period 2 Count', 'Period 2 %', 'Difference']].copy()
event_comparison_df['Period 1 %'] = event_comparison_df['Period 1 %'].round(1)
event_comparison_df['Period 2 %'] = event_comparison_df['Period 2 %'].round(1)
event_comparison_df.to_csv('period_event_distribution_detailed.csv', index=False)

print("Files saved:")
print("- period_analysis_complete_visualization.png")
print("- period_summary_statistics.csv")
print("- period_event_distribution_detailed.csv")

print(f"\n=== ANALYSIS COMPLETE ===")
print(f"Key Finding: Second half is {conversion_improvement:+.1f}% more efficient at converting shots to goals")
print(f"({p2_conversion:.1f}% vs {p1_conversion:.1f}% conversion rate)") 