import pandas as pd
import numpy as np

print("="*70)
print("SUBSTITUTION & CARD EFFECT ON MOMENTUM CHANGE")
print("="*70)

# Load data
momentum_df = pd.read_csv('../outputs/momentum_by_period.csv')
events_df = pd.read_csv('../../../Data/events_complete.csv', low_memory=False)

# Get team names per match
match_teams = momentum_df.groupby('match_id').first()[['team_home', 'team_away']].to_dict('index')

def get_momentum_change_at_minute(match_id, period, minute, team_col):
    """Get momentum change at specific minute"""
    row = momentum_df[
        (momentum_df['match_id'] == match_id) & 
        (momentum_df['period'] == period) & 
        (momentum_df['minute'] == minute)
    ]
    if len(row) > 0:
        return row[team_col].values[0]
    return None

def analyze_event_effect(event_type_filter, event_name):
    """Analyze effect of an event on momentum change"""
    print(f"\n{'='*70}")
    print(f"ANALYZING {event_name.upper()} EFFECT")
    print(f"{'='*70}")
    
    # Find all events of this type
    if event_type_filter == 'Substitution':
        events = events_df[events_df['event_type'] == 'Substitution'].copy()
    elif event_type_filter == 'Yellow Card':
        # Cards are in "Bad Behaviour" event type
        bb = events_df[events_df['event_type'] == 'Bad Behaviour'].copy()
        events = bb[bb['bad_behaviour'].str.contains('Yellow', na=False)]
    elif event_type_filter == 'Red Card':
        bb = events_df[events_df['event_type'] == 'Bad Behaviour'].copy()
        events = bb[bb['bad_behaviour'].str.contains('Red Card', na=False)]
    else:
        events = events_df[events_df['event_type'] == event_type_filter].copy()
    
    print(f"Total {event_name} events found: {len(events)}")
    
    results = []
    for idx, event in events.iterrows():
        match_id = event['match_id']
        minute = int(event['minute'])
        period = int(event['period']) if pd.notna(event.get('period')) else 1
        team = event['team_name']
        
        if match_id not in match_teams:
            continue
        
        home = match_teams[match_id]['team_home']
        away = match_teams[match_id]['team_away']
        
        # Determine team column
        is_home = (team == home)
        team_col = 'team_home_momentum_change' if is_home else 'team_away_momentum_change'
        opp_col = 'team_away_momentum_change' if is_home else 'team_home_momentum_change'
        
        # Get momentum change BEFORE event (at minute - 1)
        team_before = get_momentum_change_at_minute(match_id, period, minute - 1, team_col)
        opp_before = get_momentum_change_at_minute(match_id, period, minute - 1, opp_col)
        
        # Get momentum change AFTER event (at minute)
        team_after = get_momentum_change_at_minute(match_id, period, minute, team_col)
        opp_after = get_momentum_change_at_minute(match_id, period, minute, opp_col)
        
        # Get momentum change 1 minute after (at minute + 1)
        team_after_1 = get_momentum_change_at_minute(match_id, period, minute + 1, team_col)
        opp_after_1 = get_momentum_change_at_minute(match_id, period, minute + 1, opp_col)
        
        if team_before is not None and team_after is not None:
            results.append({
                'match_id': match_id,
                'minute': minute,
                'period': period,
                'team': team,
                'team_before': team_before,
                'team_after': team_after,
                'team_after_1': team_after_1,
                'opp_before': opp_before,
                'opp_after': opp_after,
                'opp_after_1': opp_after_1,
                'team_improved': team_after > team_before,
                'opp_worsened': opp_after < opp_before if opp_after is not None and opp_before is not None else None
            })
    
    if not results:
        print("No valid results found")
        return None
    
    df = pd.DataFrame(results)
    
    # Analysis
    print(f"\nAnalyzed {len(df)} {event_name} events with valid momentum data")
    
    # Team improvement
    team_improved = df['team_improved'].sum()
    team_worsened = (~df['team_improved']).sum()
    print(f"\n--- TEAM THAT HAD {event_name.upper()} ---")
    print(f"Momentum IMPROVED after: {team_improved} ({team_improved/len(df)*100:.1f}%)")
    print(f"Momentum WORSENED after: {team_worsened} ({team_worsened/len(df)*100:.1f}%)")
    
    # Opponent effect
    opp_valid = df.dropna(subset=['opp_worsened'])
    if len(opp_valid) > 0:
        opp_worsened = opp_valid['opp_worsened'].sum()
        opp_improved = (~opp_valid['opp_worsened']).sum()
        print(f"\n--- OPPONENT TEAM ---")
        print(f"Momentum WORSENED after: {opp_worsened} ({opp_worsened/len(opp_valid)*100:.1f}%)")
        print(f"Momentum IMPROVED after: {opp_improved} ({opp_improved/len(opp_valid)*100:.1f}%)")
    
    # Average change
    print(f"\n--- AVERAGE MOMENTUM CHANGE ---")
    print(f"Team before avg: {df['team_before'].mean():.3f}")
    print(f"Team after avg:  {df['team_after'].mean():.3f}")
    print(f"Team change:     {df['team_after'].mean() - df['team_before'].mean():.3f}")
    
    if 'opp_before' in df.columns:
        print(f"\nOpp before avg:  {df['opp_before'].mean():.3f}")
        print(f"Opp after avg:   {df['opp_after'].mean():.3f}")
        print(f"Opp change:      {df['opp_after'].mean() - df['opp_before'].mean():.3f}")
    
    # Continuation effect (2 minutes after)
    df_cont = df.dropna(subset=['team_after_1'])
    if len(df_cont) > 0:
        continued_positive = (df_cont['team_after'] > df_cont['team_before']) & (df_cont['team_after_1'] > df_cont['team_before'])
        print(f"\n--- CONTINUATION (still better 1 min after) ---")
        print(f"Effect continued: {continued_positive.sum()} ({continued_positive.sum()/len(df_cont)*100:.1f}%)")
    
    return df

# Analyze Substitutions
sub_df = analyze_event_effect('Substitution', 'Substitution')

# Analyze Yellow Cards
yellow_df = analyze_event_effect('Yellow Card', 'Yellow Card')

# Analyze Red Cards (if any)
red_df = analyze_event_effect('Red Card', 'Red Card')

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("""
Expected patterns:
- SUBSTITUTION: Team improves (fresh legs), opponent may suffer
- YELLOW CARD: Team worsens (aggressive play penalized), opponent benefits
- RED CARD: Team worsens significantly (down a player), opponent benefits strongly
""")

