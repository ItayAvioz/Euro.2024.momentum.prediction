"""
Comprehensive summary of all 3 Sports Mole commentary datasets
"""

import pandas as pd

# Load all 3 matches
final = pd.read_csv('../data/sports_mole_final_commentary_COMPLETE.csv')
nl_eng = pd.read_csv('../data/sports_mole_netherlands_england_commentary.csv')
sp_fr = pd.read_csv('../data/sports_mole_spain_france_commentary.csv')

print("\n" + "="*70)
print("🏆 SPORTS MOLE COMMENTARY - ALL 3 MATCHES COMPLETE")
print("="*70)

# Overall statistics
print(f"\n📊 OVERALL STATISTICS")
print(f"   Total Matches: 3")
print(f"   Total Entries: {len(final) + len(nl_eng) + len(sp_fr)}")
print(f"   Average per Match: {(len(final) + len(nl_eng) + len(sp_fr)) / 3:.0f}")

print(f"\n{'='*70}")
print("MATCH-BY-MATCH BREAKDOWN")
print('='*70)

matches = [
    ('🏆 FINAL: Spain vs England', final, 'Spain 2-1 England'),
    ('🥈 SEMI: Netherlands vs England', nl_eng, 'Netherlands 1-2 England'),
    ('🥈 SEMI: Spain vs France', sp_fr, 'Spain 2-1 France')
]

for title, df, result in matches:
    print(f"\n{title}")
    print(f"   Result: {result}")
    print(f"   Entries: {len(df)}")
    print(f"   Minutes: {df['minute'].min()}-{df['minute'].max()}")
    
    red_count = len(df[df['line_type'] == 'key_event'])
    black_count = len(df[df['line_type'] == 'general'])
    red_pct = (red_count / len(df)) * 100
    
    print(f"   🔴 Red Lines: {red_count} ({red_pct:.1f}%)")
    print(f"   ⚫ Black Lines: {black_count} ({100-red_pct:.1f}%)")
    
    # Top 3 event types
    top_events = df['event_type'].value_counts().head(3)
    print(f"   Top Events: {', '.join([f'{evt} ({cnt})' for evt, cnt in top_events.items()])}")

print(f"\n{'='*70}")
print("EVENT TYPE COMPARISON ACROSS ALL MATCHES")
print('='*70)

# Combine all dataframes
all_df = pd.concat([final, nl_eng, sp_fr])

print(f"\n🔴 KEY EVENTS (Red Lines):")
key_events = all_df[all_df['line_type'] == 'key_event']['event_type'].value_counts()
for event, count in key_events.items():
    print(f"   • {event:.<25} {count:>3}")

print(f"\n⚫ GENERAL COMMENTARY (Black Lines):")
general = all_df[all_df['line_type'] == 'general']['event_type'].value_counts().head(5)
for event, count in general.items():
    print(f"   • {event:.<25} {count:>3}")

print(f"\n{'='*70}")
print("TEAM STATISTICS")
print('='*70)

# Count mentions by team
team_counts = all_df['team_focus'].value_counts()
print(f"\n📈 Commentary Focus:")
for team, count in team_counts.items():
    pct = (count / len(all_df)) * 100
    print(f"   {team:.<20} {count:>3} ({pct:>5.1f}%)")

print(f"\n{'='*70}")
print("GOALS TIMELINE ACROSS ALL MATCHES")
print('='*70)

goals = all_df[all_df['event_type'] == 'Goal'].sort_values(['match_id', 'minute'])

match_names = {
    'final': '🏆 FINAL',
    'netherlands_england': '🥈 NL-ENG',
    'spain_france': '🥈 ESP-FRA'
}

for match_id in ['spain_france', 'netherlands_england', 'final']:
    match_goals = goals[goals['match_id'] == match_id]
    if len(match_goals) > 0:
        print(f"\n{match_names[match_id]}:")
        for _, goal in match_goals.iterrows():
            text = goal['commentary_text'][:70] + '...' if len(goal['commentary_text']) > 70 else goal['commentary_text']
            print(f"   ⚽ {goal['minute']:>2}' - {text}")

print(f"\n{'='*70}")
print("COMMENTARY CHARACTERISTICS")
print('='*70)

print(f"\nLength Statistics:")
print(f"   Average: {all_df['commentary_length'].mean():.0f} characters")
print(f"   Median: {all_df['commentary_length'].median():.0f} characters")
print(f"   Min: {all_df['commentary_length'].min()} characters")
print(f"   Max: {all_df['commentary_length'].max()} characters")

print(f"\nRed vs Black Line Lengths:")
red_lines = all_df[all_df['line_type'] == 'key_event']
black_lines = all_df[all_df['line_type'] == 'general']
print(f"   🔴 Red Lines Average: {red_lines['commentary_length'].mean():.0f} characters")
print(f"   ⚫ Black Lines Average: {black_lines['commentary_length'].mean():.0f} characters")

print(f"\n{'='*70}")
print("📁 OUTPUT FILES")
print('='*70)
print(f"   ✓ sports_mole_final_commentary_COMPLETE.csv ({len(final)} entries)")
print(f"   ✓ sports_mole_netherlands_england_commentary.csv ({len(nl_eng)} entries)")
print(f"   ✓ sports_mole_spain_france_commentary.csv ({len(sp_fr)} entries)")
print(f"\n   Total: {len(all_df)} commentary entries across 3 matches")

print(f"\n{'='*70}")
print("🎯 READY FOR NLP ANALYSIS")
print('='*70)
print(f"   → Minute-level aggregation")
print(f"   → Cosine Similarity comparison")
print(f"   → Entity Overlap analysis")
print(f"   → Semantic Similarity metrics")
print('='*70 + "\n")

