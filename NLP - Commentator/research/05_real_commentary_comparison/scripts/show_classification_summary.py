"""
Display summary of Sports Mole commentary with red/black line classification
"""

import pandas as pd

df = pd.read_csv('../data/sports_mole_final_commentary_COMPLETE.csv')

print("\n" + "="*70)
print("SPORTS MOLE FINAL COMMENTARY - COMPLETE CLASSIFICATION")
print("="*70)

print(f"\n📊 OVERALL STATISTICS")
print(f"   Total Entries: {len(df)}")
print(f"   Minute Range: {df['minute'].min()}-{df['minute'].max()}")
print(f"   Average Commentary Length: {int(df['commentary_length'].mean())} characters")

print(f"\n{'='*70}")
print("🔴 RED LINES (Key Events) vs ⚫ BLACK LINES (General Commentary)")
print('='*70)

for line_type, count in df['line_type'].value_counts().items():
    pct = (count / len(df)) * 100
    emoji = "🔴" if line_type == "key_event" else "⚫"
    bar = "█" * int(pct / 2)
    print(f"{emoji} {line_type.upper():.<20} {count:>3} ({pct:>5.1f}%) {bar}")

print(f"\n{'='*70}")
print("EVENT TYPE BREAKDOWN")
print('='*70)

print("\n🔴 KEY EVENTS:")
key_events = df[df['line_type'] == 'key_event']['event_type'].value_counts()
for event, count in key_events.items():
    print(f"   • {event:.<25} {count:>2}")

print("\n⚫ GENERAL COMMENTARY:")
general = df[df['line_type'] == 'general']['event_type'].value_counts().head(5)
for event, count in general.items():
    print(f"   • {event:.<25} {count:>2}")

print(f"\n{'='*70}")
print("TEAM FOCUS DISTRIBUTION")
print('='*70)
for team, count in df['team_focus'].value_counts().items():
    pct = (count / len(df)) * 100
    print(f"   {team:.<15} {count:>3} ({pct:>5.1f}%)")

print(f"\n{'='*70}")
print("MOST MENTIONED PLAYERS")
print('='*70)

# Count all player mentions
all_players = []
for players_str in df['players_mentioned']:
    if pd.notna(players_str) and players_str:
        all_players.extend([p.strip() for p in players_str.split(',')])

from collections import Counter
player_counts = Counter(all_players)

print("\n🏴󠁧󠁢󠁥󠁮󠁧󠁿 England:")
england_players = ['Pickford', 'Walker', 'Stones', 'Guehi', 'Shaw', 'Rice', 
                   'Bellingham', 'Foden', 'Saka', 'Kane', 'Palmer', 'Watkins']
for player in england_players:
    if player in player_counts and player_counts[player] > 0:
        print(f"   {player:.<20} {player_counts[player]:>2} mentions")

print("\n🇪🇸 Spain:")
spain_players = ['Simon', 'Carvajal', 'Laporte', 'Le Normand', 'Cucurella',
                 'Rodri', 'Ruiz', 'Olmo', 'Yamal', 'Williams', 'Morata', 'Oyarzabal']
for player in spain_players:
    if player in player_counts and player_counts[player] > 0:
        print(f"   {player:.<20} {player_counts[player]:>2} mentions")

print(f"\n{'='*70}")
print("SAMPLE ENTRIES BY LINE TYPE")
print('='*70)

print("\n🔴 RED LINE EXAMPLES (Key Events):")
red_samples = df[df['line_type'] == 'key_event'].head(5)
for _, row in red_samples.iterrows():
    text = row['commentary_text'][:80] + '...' if len(row['commentary_text']) > 80 else row['commentary_text']
    print(f"   {row['minute_display']:>6} [{row['event_type']}]: {text}")

print("\n⚫ BLACK LINE EXAMPLES (General Commentary):")
black_samples = df[df['line_type'] == 'general'].head(5)
for _, row in black_samples.iterrows():
    text = row['commentary_text'][:80] + '...' if len(row['commentary_text']) > 80 else row['commentary_text']
    print(f"   {row['minute_display']:>6} [{row['event_type']}]: {text}")

print(f"\n{'='*70}")
print("TIMELINE OF KEY EVENTS (Red Lines)")
print('='*70)

key_timeline = df[df['line_type'] == 'key_event'][['minute_display', 'event_type', 'commentary_text']]
for _, row in key_timeline.iterrows():
    text = row['commentary_text'][:60] + '...' if len(row['commentary_text']) > 60 else row['commentary_text']
    print(f"🔴 {row['minute_display']:>6} [{row['event_type']:<15}] {text}")

print(f"\n{'='*70}")
print(f"✅ CSV FILE: data/sports_mole_final_commentary_COMPLETE.csv")
print(f"   Columns: match_id, minute, plus_time, minute_display,")
print(f"            commentary_text, line_type, event_type,")
print(f"            players_mentioned, team_focus, commentary_length")
print('='*70 + "\n")

