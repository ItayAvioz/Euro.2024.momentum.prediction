#!/usr/bin/env python3
"""
Debug script to understand team name formats in the data
"""

import pandas as pd
import json
from momentum_3min_calculator import MomentumCalculator

def debug_team_formats():
    """Debug the team name formats in the dataset."""
    print("🔍 DEBUGGING TEAM NAME FORMATS")
    print("=" * 50)
    
    # Load a small sample of data
    df = pd.read_csv("../Data/euro_2024_complete_dataset.csv", nrows=1000)
    
    print(f"📊 Sample size: {len(df)} events")
    
    # Check team column format
    print(f"\n🏠 HOME TEAM FORMAT:")
    sample_home = df['home_team_name'].iloc[0]
    print(f"   Type: {type(sample_home)}")
    print(f"   Value: {sample_home}")
    
    print(f"\n🛫 AWAY TEAM FORMAT:")
    sample_away = df['away_team_name'].iloc[0]
    print(f"   Type: {type(sample_away)}")
    print(f"   Value: {sample_away}")
    
    print(f"\n👥 TEAM COLUMN FORMAT:")
    sample_team = df['team'].iloc[0]
    print(f"   Type: {type(sample_team)}")
    print(f"   Value: {sample_team}")
    
    print(f"\n⚽ POSSESSION TEAM FORMAT:")
    sample_poss = df['possession_team'].iloc[0]
    print(f"   Type: {type(sample_poss)}")
    print(f"   Value: {sample_poss}")
    
    # Test our team extraction
    calculator = MomentumCalculator()
    
    print(f"\n🧮 TEAM EXTRACTION TEST:")
    for i in range(5):
        event = df.iloc[i].to_dict()
        primary_team = calculator.get_primary_team(event)
        poss_team = calculator.get_possession_team_name(event)
        
        print(f"   Event {i+1}:")
        print(f"     Primary team: '{primary_team}'")
        print(f"     Possession team: '{poss_team}'")
        print(f"     Raw team: {event.get('team', 'N/A')}")
        print(f"     Raw possession: {event.get('possession_team', 'N/A')}")
        print()

if __name__ == "__main__":
    debug_team_formats()
