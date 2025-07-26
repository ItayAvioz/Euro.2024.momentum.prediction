#!/usr/bin/env python3
"""
Quick fix for team substitution analysis
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def analyze_team_substitutions():
    """Analyze team-level substitution patterns"""
    
    # Load data
    matches = pd.read_csv('Data/matches_complete.csv')
    events = pd.read_csv('Data/events_complete.csv')
    
    # Get Group Stage matches
    group_matches = matches[matches['stage'] == 'Group Stage'].copy()
    group_matches['match_date'] = pd.to_datetime(group_matches['match_date'])
    group_matches = group_matches.sort_values('match_date')
    
    # Map matchdays
    unique_dates = sorted(group_matches['match_date'].dt.date.unique())
    matchday_mapping = {}
    for date in unique_dates:
        if date.day <= 18:
            matchday_mapping[date] = 1
        elif date.day <= 23:
            matchday_mapping[date] = 2
        else:
            matchday_mapping[date] = 3
    
    group_matches['matchday'] = group_matches['match_date'].dt.date.map(matchday_mapping)
    
    # Get substitution events
    sub_events = events[events['type'].astype(str).str.contains('Substitution', na=False)].copy()
    
    # Parse team names from dictionary format
    sub_events['team_name'] = sub_events['team'].astype(str).str.extract(r"'name': '([^']+)'")
    
    # Merge with match info
    sub_events = sub_events.merge(
        group_matches[['match_id', 'matchday', 'home_team_name', 'away_team_name']],
        on='match_id',
        how='inner'
    )
    
    print("TEAM SUBSTITUTION ANALYSIS BY MATCHDAY")
    print("=" * 50)
    
    # Analyze by matchday
    for matchday in [1, 2, 3]:
        md_subs = sub_events[sub_events['matchday'] == matchday]
        md_matches = group_matches[group_matches['matchday'] == matchday]
        
        print(f"\nMATCHDAY {matchday}")
        print("-" * 20)
        
        # Calculate team stats per match
        team_stats = []
        for _, match in md_matches.iterrows():
            match_subs = md_subs[md_subs['match_id'] == match['match_id']]
            home_subs = len(match_subs[match_subs['team_name'] == match['home_team_name']])
            away_subs = len(match_subs[match_subs['team_name'] == match['away_team_name']])
            
            team_stats.append({
                'match_id': match['match_id'],
                'home_team': match['home_team_name'],
                'away_team': match['away_team_name'],
                'home_subs': home_subs,
                'away_subs': away_subs,
                'total_subs': home_subs + away_subs
            })
        
        if team_stats:
            team_df = pd.DataFrame(team_stats)
            
            print(f"Average Home Team Subs per Match: {team_df['home_subs'].mean():.2f}")
            print(f"Average Away Team Subs per Match: {team_df['away_subs'].mean():.2f}")
            print(f"Max Team Subs in Single Match: {max(team_df['home_subs'].max(), team_df['away_subs'].max())}")
            print(f"Min Team Subs in Single Match: {min(team_df['home_subs'].min(), team_df['away_subs'].min())}")
            
            # Home vs Away advantage
            total_home = team_df['home_subs'].sum()
            total_away = team_df['away_subs'].sum()
            print(f"Total Home Team Subs: {total_home}")
            print(f"Total Away Team Subs: {total_away}")
            print(f"Home vs Away Ratio: {total_home/total_away:.3f}" if total_away > 0 else "Home vs Away Ratio: N/A")
            
            # Distribution analysis
            print(f"Matches with 0 team subs: {len(team_df[(team_df['home_subs']==0) | (team_df['away_subs']==0)])}")
            print(f"Matches with 5+ team subs: {len(team_df[(team_df['home_subs']>=5) | (team_df['away_subs']>=5)])}")

if __name__ == "__main__":
    analyze_team_substitutions() 