"""
Analyze Key Features for EDA Insights
====================================

This script analyzes:
1. Player involvement percentage
2. Duration missing values and outliers  
3. Away score outliers

For updating eda_insights.csv
"""

import pandas as pd
import numpy as np

def main():
    print("🔍 Analyzing key features for EDA insights...")
    
    # Load dataset
    df = pd.read_csv('../Data/euro_2024_complete_dataset.csv', low_memory=False)
    print(f"Dataset shape: {df.shape}")
    
    # 1. Player involvement analysis
    print("\n" + "="*50)
    print("PLAYER INVOLVEMENT ANALYSIS")
    print("="*50)
    
    events_with_player = df['player'].notna().sum()
    events_without_player = df['player'].isna().sum()
    total_events = len(df)
    
    player_involvement_pct = (events_with_player / total_events) * 100
    
    print(f"Events with player: {events_with_player:,} ({player_involvement_pct:.2f}%)")
    print(f"Events without player: {events_without_player:,} ({100-player_involvement_pct:.2f}%)")
    
    # 2. Duration analysis
    print("\n" + "="*50)
    print("DURATION ANALYSIS")
    print("="*50)
    
    duration_missing = df['duration'].isna().sum()
    duration_missing_pct = (duration_missing / total_events) * 100
    
    print(f"Duration missing: {duration_missing:,} ({duration_missing_pct:.2f}%)")
    
    if duration_missing < total_events:
        duration_stats = df['duration'].describe()
        print(f"Duration statistics:")
        print(duration_stats)
        
        # Check for outliers (using IQR method)
        Q1 = df['duration'].quantile(0.25)
        Q3 = df['duration'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = df[(df['duration'] < lower_bound) | (df['duration'] > upper_bound)]['duration']
        print(f"Duration outliers: {len(outliers):,} events")
        if len(outliers) > 0:
            print(f"Outlier range: {outliers.min():.2f} to {outliers.max():.2f}")
    
    # 3. Away score analysis
    print("\n" + "="*50)
    print("AWAY SCORE ANALYSIS")
    print("="*50)
    
    away_score_stats = df['away_score'].describe()
    print(f"Away score statistics:")
    print(away_score_stats)
    
    # Check for outliers
    Q1_away = df['away_score'].quantile(0.25)
    Q3_away = df['away_score'].quantile(0.75)
    IQR_away = Q3_away - Q1_away
    lower_bound_away = Q1_away - 1.5 * IQR_away
    upper_bound_away = Q3_away + 1.5 * IQR_away
    
    away_outliers = df[(df['away_score'] < lower_bound_away) | (df['away_score'] > upper_bound_away)]['away_score']
    print(f"Away score outliers: {len(away_outliers):,} events")
    if len(away_outliers) > 0:
        print(f"Away score outlier values: {sorted(away_outliers.unique())}")
    
    # Summary for insights
    print("\n" + "="*60)
    print("SUMMARY FOR EDA INSIGHTS")
    print("="*60)
    print(f"Player involvement: {player_involvement_pct:.2f}% events have player involvement")
    print(f"Duration missing: {duration_missing_pct:.2f}% missing + {len(outliers):,} outliers to check")
    print(f"Away score outliers: {len(away_outliers):,} outlier events to check")

if __name__ == "__main__":
    main() 