"""
Momentum Change Output Analysis

Analyzes momentum change (target) data with:
1. Statistics (min, max, avg, mean, std)
2. Statistics of sequences: Upward momentum, Downward momentum
3. Double observations (team x and team y)

Author: AI Assistant
Date: August 2024
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path

def analyze_momentum_change_output():
    """Analyze momentum change output data following exact specifications."""
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    logger.info("📊 Analyzing Momentum Change Output Data...")
    
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
    
    # Extract minute from minute_range for sequence analysis
    double_obs['start_minute'] = double_obs['minute_range'].str.split('-').str[0].astype(int)
    
    logger.info(f"Created {len(double_obs)} double observations from {len(df)} windows")
    
    print("📊 MOMENTUM CHANGE OUTPUT ANALYSIS")
    print("=" * 65)
    print(f"Total observations: {len(double_obs):,} (double counting team x and team y)")
    print(f"Original windows: {len(df):,}")
    
    # 1. BASIC STATISTICS
    print("\n📈 BASIC STATISTICS")
    print("-" * 30)
    change_stats = {
        'min': double_obs['momentum_change'].min(),
        'max': double_obs['momentum_change'].max(),
        'avg': double_obs['momentum_change'].mean(),
        'mean': double_obs['momentum_change'].mean(),  # avg and mean are same
        'std': double_obs['momentum_change'].std()
    }
    
    for stat, value in change_stats.items():
        print(f"{stat.upper():>4}: {value:8.3f}")
    
    # 2. UPWARD vs DOWNWARD MOMENTUM STATISTICS
    print("\n📊 MOMENTUM DIRECTION ANALYSIS")
    print("-" * 40)
    
    # Classify momentum changes
    upward = double_obs[double_obs['momentum_change'] > 0]
    downward = double_obs[double_obs['momentum_change'] < 0]
    neutral = double_obs[double_obs['momentum_change'] == 0]
    
    print(f"{'Direction':>12} {'Count':>8} {'Percentage':>12} {'Min':>8} {'Max':>8} {'Avg':>8} {'Std':>8}")
    print("-" * 80)
    
    # Upward momentum stats
    if len(upward) > 0:
        print(f"{'Upward':>12} {len(upward):>8} {(len(upward)/len(double_obs)*100):>10.1f}% "
              f"{upward['momentum_change'].min():>8.3f} {upward['momentum_change'].max():>8.3f} "
              f"{upward['momentum_change'].mean():>8.3f} {upward['momentum_change'].std():>8.3f}")
    
    # Downward momentum stats
    if len(downward) > 0:
        print(f"{'Downward':>12} {len(downward):>8} {(len(downward)/len(double_obs)*100):>10.1f}% "
              f"{downward['momentum_change'].min():>8.3f} {downward['momentum_change'].max():>8.3f} "
              f"{downward['momentum_change'].mean():>8.3f} {downward['momentum_change'].std():>8.3f}")
    
    # Neutral momentum stats
    if len(neutral) > 0:
        print(f"{'Neutral':>12} {len(neutral):>8} {(len(neutral)/len(double_obs)*100):>10.1f}% "
              f"{neutral['momentum_change'].min():>8.3f} {neutral['momentum_change'].max():>8.3f} "
              f"{neutral['momentum_change'].mean():>8.3f} {neutral['momentum_change'].std():>8.3f}")
    
    # 3. SEQUENCE ANALYSIS (Consecutive upward/downward movements)
    print(f"\n🔄 SEQUENCE ANALYSIS")
    print("-" * 25)
    
    # Sort by match and minute for sequence analysis
    double_obs_sorted = double_obs.sort_values(['match_id', 'team_name', 'start_minute'])
    
    # Calculate sequences
    upward_sequences = []
    downward_sequences = []
    current_upward_length = 0
    current_downward_length = 0
    
    for idx, row in double_obs_sorted.iterrows():
        change = row['momentum_change']
        
        if change > 0:  # Upward
            current_upward_length += 1
            if current_downward_length > 0:
                downward_sequences.append(current_downward_length)
                current_downward_length = 0
        elif change < 0:  # Downward
            current_downward_length += 1
            if current_upward_length > 0:
                upward_sequences.append(current_upward_length)
                current_upward_length = 0
        else:  # Neutral
            if current_upward_length > 0:
                upward_sequences.append(current_upward_length)
                current_upward_length = 0
            if current_downward_length > 0:
                downward_sequences.append(current_downward_length)
                current_downward_length = 0
    
    # Add final sequences
    if current_upward_length > 0:
        upward_sequences.append(current_upward_length)
    if current_downward_length > 0:
        downward_sequences.append(current_downward_length)
    
    print(f"{'Sequence Type':>15} {'Count':>8} {'Min':>6} {'Max':>6} {'Avg':>8} {'Total Windows':>15}")
    print("-" * 70)
    
    if upward_sequences:
        print(f"{'Upward':>15} {len(upward_sequences):>8} {min(upward_sequences):>6} "
              f"{max(upward_sequences):>6} {np.mean(upward_sequences):>8.1f} {sum(upward_sequences):>15}")
    else:
        print(f"{'Upward':>15} {0:>8} {'N/A':>6} {'N/A':>6} {'N/A':>8} {0:>15}")
    
    if downward_sequences:
        print(f"{'Downward':>15} {len(downward_sequences):>8} {min(downward_sequences):>6} "
              f"{max(downward_sequences):>6} {np.mean(downward_sequences):>8.1f} {sum(downward_sequences):>15}")
    else:
        print(f"{'Downward':>15} {0:>8} {'N/A':>6} {'N/A':>6} {'N/A':>8} {0:>15}")
    
    # 4. MAGNITUDE ANALYSIS
    print(f"\n📏 MAGNITUDE ANALYSIS")
    print("-" * 25)
    
    # Absolute changes
    double_obs['abs_change'] = double_obs['momentum_change'].abs()
    
    magnitude_ranges = [
        (0.0, 0.1, "Very Small (0.0-0.1)"),
        (0.1, 0.3, "Small (0.1-0.3)"),
        (0.3, 0.5, "Medium (0.3-0.5)"),
        (0.5, 1.0, "Large (0.5-1.0)"),
        (1.0, 2.0, "Very Large (1.0-2.0)"),
        (2.0, 100.0, "Extreme (2.0+)")
    ]
    
    print(f"{'Magnitude Range':>20} {'Count':>8} {'Percentage':>12}")
    print("-" * 45)
    
    for min_val, max_val, label in magnitude_ranges:
        count = len(double_obs[(double_obs['abs_change'] >= min_val) & (double_obs['abs_change'] < max_val)])
        percentage = (count / len(double_obs)) * 100
        print(f"{label:>20} {count:>8} {percentage:>10.1f}%")
    
    # 5. TEAM PERSPECTIVE ANALYSIS
    print(f"\n👥 TEAM PERSPECTIVE BREAKDOWN:")
    print("-" * 35)
    
    home_obs = double_obs[double_obs['perspective'] == 'home']
    away_obs = double_obs[double_obs['perspective'] == 'away']
    
    print(f"{'Perspective':>12} {'Count':>8} {'Min':>8} {'Max':>8} {'Avg':>8} {'Std':>8}")
    print("-" * 70)
    print(f"{'Home':>12} {len(home_obs):>8} {home_obs['momentum_change'].min():>8.3f} "
          f"{home_obs['momentum_change'].max():>8.3f} {home_obs['momentum_change'].mean():>8.3f} "
          f"{home_obs['momentum_change'].std():>8.3f}")
    print(f"{'Away':>12} {len(away_obs):>8} {away_obs['momentum_change'].min():>8.3f} "
          f"{away_obs['momentum_change'].max():>8.3f} {away_obs['momentum_change'].mean():>8.3f} "
          f"{away_obs['momentum_change'].std():>8.3f}")
    
    # 6. DISTRIBUTION BY QUARTILES
    print(f"\n📊 QUARTILE DISTRIBUTION:")
    print("-" * 30)
    
    quartiles = double_obs['momentum_change'].quantile([0.25, 0.5, 0.75])
    print(f"Q1 (25th percentile): {quartiles[0.25]:>8.3f}")
    print(f"Q2 (50th percentile): {quartiles[0.5]:>8.3f}")
    print(f"Q3 (75th percentile): {quartiles[0.75]:>8.3f}")
    print(f"IQR (Q3 - Q1):        {quartiles[0.75] - quartiles[0.25]:>8.3f}")
    
    # 7. ADDITIONAL INSIGHTS
    print(f"\n🔍 ADDITIONAL INSIGHTS:")
    print("-" * 25)
    print(f"Zero change observations: {(double_obs['momentum_change'] == 0).sum()}")
    print(f"Positive changes: {(double_obs['momentum_change'] > 0).sum()} ({(double_obs['momentum_change'] > 0).sum()/len(double_obs)*100:.1f}%)")
    print(f"Negative changes: {(double_obs['momentum_change'] < 0).sum()} ({(double_obs['momentum_change'] < 0).sum()/len(double_obs)*100:.1f}%)")
    print(f"Largest positive change: {double_obs['momentum_change'].max():.3f}")
    print(f"Largest negative change: {double_obs['momentum_change'].min():.3f}")
    print(f"Most common change value: {double_obs['momentum_change'].mode().iloc[0]:.3f}")
    
    logger.info("✅ Momentum change output analysis completed!")
    
    return double_obs

def main():
    """Main execution function."""
    print("📊 Momentum Change Output Analyzer")
    print("=" * 45)
    
    # Analyze momentum change output
    result_df = analyze_momentum_change_output()
    
    print(f"\n✅ Analysis completed!")
    print(f"Analyzed {len(result_df):,} observations")

if __name__ == "__main__":
    main()
