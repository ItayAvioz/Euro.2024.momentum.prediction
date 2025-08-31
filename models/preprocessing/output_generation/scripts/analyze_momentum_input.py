"""
Momentum Input Analysis

Analyzes momentum input data with:
1. Statistics (min, max, avg, mean, std)
2. Distribution count with specific rounding rules
3. Momentum range analysis by time intervals (5, 10, 15 minutes)
4. Double observations (team x and team y)

Author: AI Assistant
Date: August 2024
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path

def analyze_momentum_input():
    """Analyze momentum input data following exact specifications."""
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    logger.info("📊 Analyzing Momentum Input Data...")
    
    # Load streamlined dataset
    input_file = "../momentum_targets_streamlined.csv"
    df = pd.read_csv(input_file)
    logger.info(f"Loaded {len(df)} windows")
    
    # Create double observations (team x and team y)
    logger.info("Creating double observations...")
    
    # Team X observations (home team perspective)
    team_x = df.copy()
    team_x['team_name'] = team_x['team_home']
    team_x['opponent'] = team_x['team_away']
    team_x['momentum'] = team_x['team_home_momentum']
    team_x['momentum_change'] = team_x['team_home_momentum_change']
    team_x['perspective'] = 'home'
    
    # Team Y observations (away team perspective)
    team_y = df.copy()
    team_y['team_name'] = team_y['team_away']
    team_y['opponent'] = team_y['team_home']
    team_y['momentum'] = team_y['team_away_momentum']
    team_y['momentum_change'] = team_y['team_away_momentum_change']
    team_y['perspective'] = 'away'
    
    # Combine for double observations
    double_obs = pd.concat([team_x, team_y], ignore_index=True)
    
    # Extract minute from minute_range for time analysis
    double_obs['start_minute'] = double_obs['minute_range'].str.split('-').str[0].astype(int)
    
    logger.info(f"Created {len(double_obs)} double observations from {len(df)} windows")
    
    print("📊 MOMENTUM INPUT ANALYSIS")
    print("=" * 60)
    print(f"Total observations: {len(double_obs):,} (double counting team x and team y)")
    print(f"Original windows: {len(df):,}")
    
    # 1. BASIC STATISTICS
    print("\n📈 BASIC STATISTICS")
    print("-" * 30)
    momentum_stats = {
        'min': double_obs['momentum'].min(),
        'max': double_obs['momentum'].max(),
        'avg': double_obs['momentum'].mean(),
        'mean': double_obs['momentum'].mean(),  # avg and mean are same
        'std': double_obs['momentum'].std()
    }
    
    for stat, value in momentum_stats.items():
        print(f"{stat.upper():>4}: {value:8.3f}")
    
    # 2. DISTRIBUTION COUNT WITH ROUNDING RULES
    print("\n📊 DISTRIBUTION COUNT (Rounding Rules)")
    print("-" * 40)
    print("Rules: <0.25 round down, >=0.25 round up to 0.5 or 1")
    
    def custom_round(value):
        """Apply custom rounding rules: <0.25 round down, >=0.25 round up to 0.5 or 1"""
        fractional_part = value - int(value)
        
        if fractional_part < 0.25:
            return int(value)  # Round down
        elif fractional_part < 0.75:
            return int(value) + 0.5  # Round to 0.5
        else:
            return int(value) + 1  # Round up to next integer
    
    # Apply custom rounding
    double_obs['momentum_rounded'] = double_obs['momentum'].apply(custom_round)
    
    # Count distribution
    dist_counts = double_obs['momentum_rounded'].value_counts().sort_index()
    
    print(f"{'Value':>8} {'Count':>8} {'Percentage':>12}")
    print("-" * 30)
    for value, count in dist_counts.items():
        percentage = (count / len(double_obs)) * 100
        print(f"{value:>8} {count:>8} {percentage:>10.1f}%")
    
    # 3. MOMENTUM RANGE BY TIME INTERVALS
    print("\n⏰ MOMENTUM RANGE BY TIME INTERVALS")
    print("-" * 45)
    
    # Define time intervals
    time_intervals = [
        (0, 4, "0-5min"),
        (5, 9, "5-10min"), 
        (10, 14, "10-15min"),
        (15, 19, "15-20min"),
        (20, 24, "20-25min"),
        (25, 29, "25-30min"),
        (30, 34, "30-35min"),
        (35, 39, "35-40min"),
        (40, 44, "40-45min"),
        (45, 49, "45-50min"),
        (50, 54, "50-55min"),
        (55, 59, "55-60min"),
        (60, 64, "60-65min"),
        (65, 69, "65-70min"),
        (70, 74, "70-75min"),
        (75, 79, "75-80min"),
        (80, 84, "80-85min"),
        (85, 89, "85-90min"),
        (90, 120, "90+min")
    ]
    
    # Also create the specific 5, 10, 15 minute analysis
    specific_intervals = [
        (0, 4, "5min"),
        (0, 9, "10min"),
        (0, 14, "15min")
    ]
    
    print("📋 ALL GAME TIME ANALYSIS:")
    print(f"{'Interval':>12} {'Count':>8} {'Min':>8} {'Max':>8} {'Avg':>8} {'Std':>8}")
    print("-" * 60)
    
    for start, end, label in time_intervals:
        interval_data = double_obs[
            (double_obs['start_minute'] >= start) & 
            (double_obs['start_minute'] <= end)
        ]
        
        if len(interval_data) > 0:
            print(f"{label:>12} {len(interval_data):>8} {interval_data['momentum'].min():>8.3f} "
                  f"{interval_data['momentum'].max():>8.3f} {interval_data['momentum'].mean():>8.3f} "
                  f"{interval_data['momentum'].std():>8.3f}")
        else:
            print(f"{label:>12} {0:>8} {'N/A':>8} {'N/A':>8} {'N/A':>8} {'N/A':>8}")
    
    print(f"\n📋 SPECIFIC INTERVALS (5, 10, 15 minutes):")
    print(f"{'Interval':>12} {'Count':>8} {'Min':>8} {'Max':>8} {'Avg':>8} {'Std':>8}")
    print("-" * 60)
    
    for start, end, label in specific_intervals:
        interval_data = double_obs[
            (double_obs['start_minute'] >= start) & 
            (double_obs['start_minute'] <= end)
        ]
        
        if len(interval_data) > 0:
            print(f"{label:>12} {len(interval_data):>8} {interval_data['momentum'].min():>8.3f} "
                  f"{interval_data['momentum'].max():>8.3f} {interval_data['momentum'].mean():>8.3f} "
                  f"{interval_data['momentum'].std():>8.3f}")
    
    # 4. TEAM PERSPECTIVE ANALYSIS
    print(f"\n👥 TEAM PERSPECTIVE BREAKDOWN:")
    print("-" * 35)
    
    home_obs = double_obs[double_obs['perspective'] == 'home']
    away_obs = double_obs[double_obs['perspective'] == 'away']
    
    print(f"{'Perspective':>12} {'Count':>8} {'Min':>8} {'Max':>8} {'Avg':>8} {'Std':>8}")
    print("-" * 60)
    print(f"{'Home':>12} {len(home_obs):>8} {home_obs['momentum'].min():>8.3f} "
          f"{home_obs['momentum'].max():>8.3f} {home_obs['momentum'].mean():>8.3f} "
          f"{home_obs['momentum'].std():>8.3f}")
    print(f"{'Away':>12} {len(away_obs):>8} {away_obs['momentum'].min():>8.3f} "
          f"{away_obs['momentum'].max():>8.3f} {away_obs['momentum'].mean():>8.3f} "
          f"{away_obs['momentum'].std():>8.3f}")
    
    # 5. ADDITIONAL INSIGHTS
    print(f"\n🔍 ADDITIONAL INSIGHTS:")
    print("-" * 25)
    print(f"Unique teams: {double_obs['team_name'].nunique()}")
    print(f"Unique matches: {double_obs['match_id'].nunique()}")
    print(f"Minutes covered: {double_obs['start_minute'].min()}-{double_obs['start_minute'].max()}")
    print(f"Zero momentum observations: {(double_obs['momentum'] == 0).sum()}")
    print(f"Negative momentum observations: {(double_obs['momentum'] < 0).sum()}")
    
    logger.info("✅ Momentum input analysis completed!")
    
    return double_obs

def main():
    """Main execution function."""
    print("📊 Momentum Input Analyzer")
    print("=" * 40)
    
    # Analyze momentum input
    result_df = analyze_momentum_input()
    
    print(f"\n✅ Analysis completed!")
    print(f"Analyzed {len(result_df):,} observations")

if __name__ == "__main__":
    main()
