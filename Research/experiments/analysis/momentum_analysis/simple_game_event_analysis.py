#!/usr/bin/env python3
"""
Simple Game Event Impact Analysis
Focus on key events that predict momentum changes
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

def main():
    """Analyze game events that predict momentum changes"""
    print("🎯 SIMPLE GAME EVENT MOMENTUM ANALYSIS")
    print("=" * 60)
    
    # Load data
    print("📊 Loading Euro 2024 Dataset...")
    try:
        events_df = pd.read_csv("../Data/events_complete.csv", low_memory=False)
        print(f"✅ Events loaded: {len(events_df):,}")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return
    
    # Analyze available events
    print(f"\n🔍 ANALYZING AVAILABLE GAME EVENTS")
    print("=" * 40)
    
    # Check event types
    event_types = events_df['type'].value_counts()
    print(f"📊 Event Types (Top 15):")
    for event_type, count in event_types.head(15).items():
        print(f"   {event_type:<20}: {count:>8,}")
    
    # Check for specific high-impact events
    high_impact_events = [
        'Substitution', 'Yellow Card', 'Red Card', 'Goal', 'Penalty',
        'Corner', 'Free Kick', 'Foul', 'Offside'
    ]
    
    print(f"\n🎯 HIGH-IMPACT EVENTS:")
    for event in high_impact_events:
        count = len(events_df[events_df['type'].str.contains(event, na=False, case=False)])
        if count > 0:
            print(f"   {event:<20}: {count:>6,} events")
    
    # Check match phases
    print(f"\n⏱️  MATCH PHASES:")
    print(f"   First 15 minutes: {len(events_df[events_df['minute'] <= 15]):,}")
    print(f"   Last 15 minutes (75+): {len(events_df[events_df['minute'] >= 75]):,}")
    print(f"   Stoppage time (90+): {len(events_df[events_df['minute'] >= 90]):,}")
    print(f"   Extra time (105+): {len(events_df[events_df['minute'] >= 105]):,}")
    
    # Check for tactical data
    print(f"\n🎪 TACTICAL DATA:")
    if 'tactics' in events_df.columns:
        tactics_count = events_df['tactics'].notna().sum()
        print(f"   Tactics entries: {tactics_count:,}")
    else:
        print("   No tactics column found")
    
    if 'substitution' in events_df.columns:
        sub_count = events_df['substitution'].notna().sum()
        print(f"   Substitution data: {sub_count:,}")
    else:
        print("   No substitution column found")
    
    # Check for formation data
    if 'formation' in events_df.columns:
        formation_count = events_df['formation'].notna().sum()
        print(f"   Formation data: {formation_count:,}")
    else:
        print("   No formation column found")
    
    # Sample analysis of key events
    print(f"\n📈 SAMPLE EVENT ANALYSIS:")
    
    # Goals by minute
    goals = events_df[events_df['type'].str.contains('Goal', na=False, case=False)]
    if len(goals) > 0:
        print(f"   Goals by phase:")
        print(f"     First 15 min: {len(goals[goals['minute'] <= 15])}")
        print(f"     Mid-game (16-75): {len(goals[(goals['minute'] > 15) & (goals['minute'] <= 75)])}")
        print(f"     Last 15 min (76+): {len(goals[goals['minute'] > 75])}")
    
    # Cards by minute
    cards = events_df[events_df['type'].str.contains('Card', na=False, case=False)]
    if len(cards) > 0:
        print(f"   Cards by phase:")
        print(f"     First 15 min: {len(cards[cards['minute'] <= 15])}")
        print(f"     Mid-game (16-75): {len(cards[(cards['minute'] > 15) & (cards['minute'] <= 75)])}")
        print(f"     Last 15 min (76+): {len(cards[cards['minute'] > 75])}")
    
    # Substitutions by minute
    subs = events_df[events_df['type'].str.contains('Substitution', na=False, case=False)]
    if len(subs) > 0:
        print(f"   Substitutions by phase:")
        print(f"     First 15 min: {len(subs[subs['minute'] <= 15])}")
        print(f"     Mid-game (16-75): {len(subs[(subs['minute'] > 15) & (subs['minute'] <= 75)])}")
        print(f"     Last 15 min (76+): {len(subs[subs['minute'] > 75])}")
    
    # Additional columns check
    print(f"\n🔍 ADDITIONAL COLUMNS:")
    interesting_cols = ['under_pressure', 'off_camera', 'out', 'counterpress', 
                       'duration', 'related_events', 'player']
    for col in interesting_cols:
        if col in events_df.columns:
            non_null_count = events_df[col].notna().sum()
            print(f"   {col:<20}: {non_null_count:>8,} non-null values")
    
    # Check all columns
    print(f"\n📋 ALL COLUMNS ({len(events_df.columns)}):")
    for i, col in enumerate(events_df.columns):
        print(f"   {i+1:2d}. {col}")
    
    print(f"\n✅ SIMPLE ANALYSIS COMPLETE")

if __name__ == "__main__":
    main() 