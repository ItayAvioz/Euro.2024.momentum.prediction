import pandas as pd
import ast
import re

# --- Configuration ---
DATA_PATH = '../Data/euro_2024_complete_dataset.csv'
OUTPUT_CSV_PATH = 'euro_2024_cards_analysis.csv'

# --- Helper Functions ---
def _safe_read_csv(path):
    """Attempts to read a CSV with multiple encodings."""
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    for encoding in encodings:
        try:
            # Try reading a sample first to quickly check encoding
            df_sample = pd.read_csv(path, encoding=encoding, nrows=100, low_memory=False)
            # If sample reads, read the full file
            return pd.read_csv(path, encoding=encoding, low_memory=False)
        except Exception as e:
            # print(f"Failed to read with {encoding}: {e}")
            continue
    raise ValueError(f"Could not read CSV with any of the attempted encodings: {encodings}")

def parse_event_details(df, column_name):
    """Safely parses dictionary strings in a DataFrame column."""
    if column_name not in df.columns:
        return pd.Series([None] * len(df), index=df.index)
    
    def parse_literal(x):
        try:
            return ast.literal_eval(x) if pd.notna(x) and isinstance(x, str) else {}
        except (ValueError, SyntaxError):
            return {}
    return df[column_name].apply(parse_literal)

def extract_card_info(foul_details, bad_behaviour_details):
    """Extracts card information from foul committed and bad behaviour details."""
    cards = []
    
    # Check foul committed details
    if foul_details and isinstance(foul_details, dict):
        if 'card' in foul_details:
            card_info = foul_details['card']
            if isinstance(card_info, dict) and 'name' in card_info:
                cards.append(card_info['name'])
    
    # Check bad behaviour details
    if bad_behaviour_details and isinstance(bad_behaviour_details, dict):
        if 'card' in bad_behaviour_details:
            card_info = bad_behaviour_details['card']
            if isinstance(card_info, dict) and 'name' in card_info:
                cards.append(card_info['name'])
    
    return cards

def get_period_name(period):
    """Convert period number to readable name."""
    period_map = {
        1: "Period 1",
        2: "Period 2", 
        3: "Period 3 (Extra Time 1st Half)",
        4: "Period 4 (Extra Time 2nd Half)",
        5: "Period 5 (Penalty Shootout)"
    }
    return period_map.get(period, f"Period {period}")

# --- Main Analysis ---
if __name__ == "__main__":
    print("🔍 ANALYZING EURO 2024 CARDS DATA...")
    print("==================================================")

    # Load data
    try:
        df = _safe_read_csv(DATA_PATH)
        print(f"✅ Dataset loaded: {len(df):,} total events")
    except ValueError as e:
        print(f"❌ Error loading dataset: {e}")
        exit()

    # Filter for card-related events (Foul Committed and Bad Behaviour)
    card_events = df[
        (df['type'].astype(str).str.contains('Foul Committed', na=False)) |
        (df['type'].astype(str).str.contains('Bad Behaviour', na=False))
    ].copy()

    print(f"📊 Found {len(card_events)} potential card events")

    # Parse event details
    card_events['foul_details'] = parse_event_details(card_events, 'foul_committed')
    card_events['bad_behaviour_details'] = parse_event_details(card_events, 'bad_behaviour')

    # Extract card information
    card_events['cards'] = card_events.apply(
        lambda row: extract_card_info(row['foul_details'], row['bad_behaviour_details']), 
        axis=1
    )

    # Filter events that actually have cards
    events_with_cards = card_events[card_events['cards'].apply(len) > 0].copy()
    
    print(f"📊 Found {len(events_with_cards)} events with actual cards")

    # Expand cards (some events might have multiple cards)
    card_records = []
    for _, row in events_with_cards.iterrows():
        for card in row['cards']:
            card_records.append({
                'match_id': row['match_id'],
                'home_team': row.get('home_team_name', 'Unknown'),
                'away_team': row.get('away_team_name', 'Unknown'),
                'match_date': row.get('match_date', 'Unknown'),
                'stage': row.get('stage', 'Unknown'),
                'period': row['period'],
                'period_name': get_period_name(row['period']),
                'minute': row['minute'],
                'second': row.get('second', 0),
                'team': row['team'],
                'player': row.get('player', 'Unknown'),
                'card_type': card,
                'event_type': row['type'],
                'event_uuid': row.get('event_uuid', 'Unknown')
            })

    # Create DataFrame from card records
    cards_df = pd.DataFrame(card_records)
    
    if len(cards_df) == 0:
        print("❌ No cards found in the dataset")
        exit()

    print(f"📊 Total card records: {len(cards_df)}")

    # Save detailed card data
    cards_df.to_csv(OUTPUT_CSV_PATH, index=False)
    print(f"\n💾 SAVED: {OUTPUT_CSV_PATH}")
    print(f"📄 Contains {len(cards_df)} card records with detailed information")

    # --- Analysis Summary ---
    print("\n🎯 CARDS ANALYSIS SUMMARY:")
    print("=" * 50)

    # Total cards by type
    card_counts = cards_df['card_type'].value_counts()
    print("\n📊 TOTAL CARDS BY TYPE:")
    for card_type, count in card_counts.items():
        print(f"  {card_type}: {count} cards")

    # Cards by period
    print("\n📊 CARDS BY PERIOD:")
    period_counts = cards_df.groupby(['period', 'period_name', 'card_type']).size().unstack(fill_value=0)
    print(period_counts)

    # Period 1 vs Period 2 breakdown
    p1_cards = cards_df[cards_df['period'] == 1]
    p2_cards = cards_df[cards_df['period'] == 2]
    
    print(f"\n📊 PERIOD 1 vs PERIOD 2 BREAKDOWN:")
    print(f"Period 1 (First Half):")
    if len(p1_cards) > 0:
        p1_counts = p1_cards['card_type'].value_counts()
        for card_type, count in p1_counts.items():
            print(f"  {card_type}: {count} cards")
        print(f"  TOTAL: {len(p1_cards)} cards")
    else:
        print("  No cards found")

    print(f"\nPeriod 2 (Second Half):")
    if len(p2_cards) > 0:
        p2_counts = p2_cards['card_type'].value_counts()
        for card_type, count in p2_counts.items():
            print(f"  {card_type}: {count} cards")
        print(f"  TOTAL: {len(p2_cards)} cards")
    else:
        print("  No cards found")

    # Check for second yellow cards (which become red cards)
    print(f"\n🔍 CHECKING FOR SECOND YELLOW CARDS:")
    
    # Group by player and match to find multiple yellows
    player_match_cards = cards_df.groupby(['match_id', 'player', 'team'])['card_type'].apply(list).reset_index()
    
    second_yellows = []
    for _, row in player_match_cards.iterrows():
        card_list = row['card_type']
        yellow_count = card_list.count('Yellow Card')
        if yellow_count >= 2:
            second_yellows.append({
                'match_id': row['match_id'],
                'player': row['player'],
                'team': row['team'],
                'yellow_cards': yellow_count,
                'all_cards': card_list
            })

    if second_yellows:
        print(f"  Found {len(second_yellows)} players with multiple yellow cards:")
        for sy in second_yellows:
            print(f"    {sy['player']} ({sy['team']}): {sy['all_cards']}")
    else:
        print("  No players found with multiple yellow cards in same match")

    # Dashboard update data
    print(f"\n🎯 DASHBOARD UPDATE DATA:")
    print("=" * 30)
    
    total_yellows = card_counts.get('Yellow Card', 0)
    total_reds = card_counts.get('Red Card', 0) + card_counts.get('Second Yellow', 0)
    
    p1_yellows = p1_cards['card_type'].value_counts().get('Yellow Card', 0) if len(p1_cards) > 0 else 0
    p1_reds = (p1_cards['card_type'].value_counts().get('Red Card', 0) + 
               p1_cards['card_type'].value_counts().get('Second Yellow', 0)) if len(p1_cards) > 0 else 0
    
    p2_yellows = p2_cards['card_type'].value_counts().get('Yellow Card', 0) if len(p2_cards) > 0 else 0
    p2_reds = (p2_cards['card_type'].value_counts().get('Red Card', 0) + 
               p2_cards['card_type'].value_counts().get('Second Yellow', 0)) if len(p2_cards) > 0 else 0

    print(f"YELLOW CARDS: {total_yellows} total")
    print(f"  Period 1: {p1_yellows} cards")
    print(f"  Period 2: {p2_yellows} cards")
    print(f"  Per match: {total_yellows/51:.2f}")
    
    print(f"\nRED CARDS: {total_reds} total")
    print(f"  Period 1: {p1_reds} cards") 
    print(f"  Period 2: {p2_reds} cards")
    print(f"  Per match: {total_reds/51:.2f}")

    # Check all periods for completeness
    print(f"\n📊 ALL PERIODS BREAKDOWN:")
    all_periods = cards_df.groupby('period')['card_type'].value_counts().unstack(fill_value=0)
    print(all_periods)
    
    total_all_periods = len(cards_df)
    print(f"\nTOTAL CARDS (ALL PERIODS): {total_all_periods}")
