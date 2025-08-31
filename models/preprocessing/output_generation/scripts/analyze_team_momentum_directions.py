"""
Team Momentum Direction Analysis

Analyzes momentum change directions between teams in the same game window:
- Positive-Positive: Both teams increase momentum
- Negative-Negative: Both teams decrease momentum  
- Positive-Negative: Team X increases, Team Y decreases
- Negative-Positive: Team X decreases, Team Y increases

Note: Order matters! No real home/away distinction.

Author: AI Assistant
Date: August 2024
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path

def analyze_team_momentum_directions():
    """Analyze momentum change direction patterns between teams in same game."""
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    logger.info("📊 Analyzing Team Momentum Directions...")
    
    # Load streamlined dataset
    input_file = "../momentum_targets_streamlined.csv"
    df = pd.read_csv(input_file)
    logger.info(f"Loaded {len(df)} windows")
    
    print("📊 TEAM MOMENTUM DIRECTION ANALYSIS")
    print("=" * 50)
    print(f"Total game windows: {len(df):,}")
    print("Note: Each window contains Team X and Team Y (not home/away)")
    
    # Classify momentum change directions
    def classify_direction(change):
        if change > 0:
            return "Positive"
        elif change < 0:
            return "Negative"
        else:
            return "Neutral"
    
    # Add direction classifications
    df['team_x_direction'] = df['team_home_momentum_change'].apply(classify_direction)
    df['team_y_direction'] = df['team_away_momentum_change'].apply(classify_direction)
    
    # Create combined direction patterns
    df['direction_pattern'] = df['team_x_direction'] + '-' + df['team_y_direction']
    
    # Count direction patterns
    pattern_counts = df['direction_pattern'].value_counts()
    
    print(f"\n📈 DIRECTION PATTERN ANALYSIS")
    print("-" * 40)
    print(f"{'Pattern':>20} {'Count':>8} {'Percentage':>12}")
    print("-" * 45)
    
    total_windows = len(df)
    for pattern, count in pattern_counts.items():
        percentage = (count / total_windows) * 100
        print(f"{pattern:>20} {count:>8} {percentage:>10.1f}%")
    
    # Specific analysis as requested
    print(f"\n🎯 REQUESTED ANALYSIS (Exact Order)")
    print("-" * 40)
    
    positive_positive = len(df[(df['team_x_direction'] == 'Positive') & (df['team_y_direction'] == 'Positive')])
    negative_negative = len(df[(df['team_x_direction'] == 'Negative') & (df['team_y_direction'] == 'Negative')])
    positive_negative = len(df[(df['team_x_direction'] == 'Positive') & (df['team_y_direction'] == 'Negative')])
    negative_positive = len(df[(df['team_x_direction'] == 'Negative') & (df['team_y_direction'] == 'Positive')])
    
    print(f"Positive-Positive: {positive_positive:>6} ({(positive_positive/total_windows)*100:>5.1f}%) - Both teams gain momentum")
    print(f"Negative-Negative: {negative_negative:>6} ({(negative_negative/total_windows)*100:>5.1f}%) - Both teams lose momentum")
    print(f"Positive-Negative: {positive_negative:>6} ({(positive_negative/total_windows)*100:>5.1f}%) - Team X gains, Team Y loses")
    print(f"Negative-Positive: {negative_positive:>6} ({(negative_positive/total_windows)*100:>5.1f}%) - Team X loses, Team Y gains")
    
    # Competitive vs Collaborative patterns
    competitive = positive_negative + negative_positive  # One gains, one loses
    collaborative = positive_positive + negative_negative  # Both move in same direction
    
    print(f"\n⚔️ COMPETITIVE vs COLLABORATIVE PATTERNS")
    print("-" * 45)
    print(f"Competitive (opposite directions): {competitive:>6} ({(competitive/total_windows)*100:>5.1f}%)")
    print(f"Collaborative (same direction):   {collaborative:>6} ({(collaborative/total_windows)*100:>5.1f}%)")
    
    # Detailed magnitude analysis for each pattern
    print(f"\n📏 MAGNITUDE ANALYSIS BY PATTERN")
    print("-" * 40)
    print(f"{'Pattern':>20} {'Avg X Change':>15} {'Avg Y Change':>15} {'X Std':>8} {'Y Std':>8}")
    print("-" * 75)
    
    patterns = ['Positive-Positive', 'Negative-Negative', 'Positive-Negative', 'Negative-Positive']
    for pattern in patterns:
        subset = df[df['direction_pattern'] == pattern]
        if len(subset) > 0:
            avg_x = subset['team_home_momentum_change'].mean()
            avg_y = subset['team_away_momentum_change'].mean()
            std_x = subset['team_home_momentum_change'].std()
            std_y = subset['team_away_momentum_change'].std()
            print(f"{pattern:>20} {avg_x:>15.3f} {avg_y:>15.3f} {std_x:>8.3f} {std_y:>8.3f}")
    
    # Extreme cases analysis
    print(f"\n🔥 EXTREME CASES ANALYSIS")
    print("-" * 30)
    
    # Find largest positive-positive cases
    pos_pos_subset = df[df['direction_pattern'] == 'Positive-Positive']
    if len(pos_pos_subset) > 0:
        pos_pos_subset['combined_gain'] = pos_pos_subset['team_home_momentum_change'] + pos_pos_subset['team_away_momentum_change']
        max_combined_gain = pos_pos_subset['combined_gain'].max()
        print(f"Largest combined momentum gain: {max_combined_gain:.3f}")
    
    # Find largest negative-negative cases
    neg_neg_subset = df[df['direction_pattern'] == 'Negative-Negative']
    if len(neg_neg_subset) > 0:
        neg_neg_subset['combined_loss'] = neg_neg_subset['team_home_momentum_change'] + neg_neg_subset['team_away_momentum_change']
        max_combined_loss = neg_neg_subset['combined_loss'].min()
        print(f"Largest combined momentum loss: {max_combined_loss:.3f}")
    
    # Find largest momentum swings (positive-negative)
    pos_neg_subset = df[df['direction_pattern'] == 'Positive-Negative']
    if len(pos_neg_subset) > 0:
        pos_neg_subset['momentum_swing'] = pos_neg_subset['team_home_momentum_change'] - pos_neg_subset['team_away_momentum_change']
        max_swing_pos_neg = pos_neg_subset['momentum_swing'].max()
        print(f"Largest Positive-Negative swing: {max_swing_pos_neg:.3f}")
    
    neg_pos_subset = df[df['direction_pattern'] == 'Negative-Positive']
    if len(neg_pos_subset) > 0:
        neg_pos_subset['momentum_swing'] = neg_pos_subset['team_away_momentum_change'] - neg_pos_subset['team_home_momentum_change']
        max_swing_neg_pos = neg_pos_subset['momentum_swing'].max()
        print(f"Largest Negative-Positive swing: {max_swing_neg_pos:.3f}")
    
    # Sample data for each pattern
    print(f"\n📋 SAMPLE DATA FOR EACH PATTERN")
    print("-" * 35)
    
    for pattern in patterns:
        subset = df[df['direction_pattern'] == pattern]
        if len(subset) > 0:
            print(f"\n{pattern} (Sample - first 3 cases):")
            sample = subset[['match_id', 'minute_range', 'team_home', 'team_away', 
                           'team_home_momentum_change', 'team_away_momentum_change']].head(3)
            for _, row in sample.iterrows():
                print(f"  {row['minute_range']:>6} | {row['team_home']:>10} vs {row['team_away']:<10} | "
                      f"X: {row['team_home_momentum_change']:>6.3f}, Y: {row['team_away_momentum_change']:>6.3f}")
    
    # Zero change cases
    neutral_cases = df[(df['team_x_direction'] == 'Neutral') | (df['team_y_direction'] == 'Neutral')]
    print(f"\n🎯 NEUTRAL CASES")
    print("-" * 20)
    print(f"Windows with at least one neutral change: {len(neutral_cases)}")
    if len(neutral_cases) > 0:
        neutral_patterns = neutral_cases['direction_pattern'].value_counts()
        for pattern, count in neutral_patterns.items():
            print(f"  {pattern}: {count}")
    
    logger.info("✅ Team momentum direction analysis completed!")
    
    return df

def main():
    """Main execution function."""
    print("📊 Team Momentum Direction Analyzer")
    print("=" * 40)
    
    # Analyze team momentum directions
    result_df = analyze_team_momentum_directions()
    
    print(f"\n✅ Analysis completed!")
    print(f"Analyzed {len(result_df):,} game windows")

if __name__ == "__main__":
    main()
