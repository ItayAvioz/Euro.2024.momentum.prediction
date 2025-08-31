"""
Team Superiority Analysis by Game

For each game and each team, count:
1. How many times momentum was higher than opponent
2. How many times momentum change was higher than opponent  
3. How many times relative change (momentum_change/momentum) was higher than opponent

Author: AI Assistant
Date: August 2024
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path

def analyze_team_superiority_by_game():
    """Analyze team superiority metrics for each game and team."""
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    logger.info("📊 Analyzing Team Superiority by Game...")
    
    # Load streamlined dataset
    input_file = "../momentum_targets_streamlined.csv"
    df = pd.read_csv(input_file)
    logger.info(f"Loaded {len(df)} windows")
    
    print("📊 TEAM SUPERIORITY ANALYSIS BY GAME")
    print("=" * 55)
    print(f"Total game windows: {len(df):,}")
    
    # Calculate relative change (momentum_change / momentum)
    # Handle division by zero by setting to 0 when momentum is 0
    df['team_home_relative_change'] = np.where(
        df['team_home_momentum'] != 0,
        df['team_home_momentum_change'] / df['team_home_momentum'],
        0
    )
    df['team_away_relative_change'] = np.where(
        df['team_away_momentum'] != 0,
        df['team_away_momentum_change'] / df['team_away_momentum'],
        0
    )
    
    # Create comparison flags
    df['home_momentum_higher'] = df['team_home_momentum'] > df['team_away_momentum']
    df['home_change_higher'] = df['team_home_momentum_change'] > df['team_away_momentum_change']
    df['home_relative_higher'] = df['team_home_relative_change'] > df['team_away_relative_change']
    
    # Group by match to analyze each game
    results = []
    
    print(f"\n📈 SUPERIORITY COUNTS BY GAME AND TEAM")
    print("-" * 60)
    print(f"{'Match ID':>10} {'Team':>15} {'Windows':>8} {'Mom>Opp':>8} {'ΔMom>Opp':>10} {'RelΔ>Opp':>10}")
    print("-" * 70)
    
    for match_id in df['match_id'].unique():
        match_data = df[df['match_id'] == match_id]
        total_windows = len(match_data)
        
        # Get team names
        home_team = match_data['team_home'].iloc[0]
        away_team = match_data['team_away'].iloc[0]
        
        # Home team superiority counts
        home_momentum_wins = match_data['home_momentum_higher'].sum()
        home_change_wins = match_data['home_change_higher'].sum()
        home_relative_wins = match_data['home_relative_higher'].sum()
        
        # Away team superiority counts
        away_momentum_wins = total_windows - home_momentum_wins
        away_change_wins = total_windows - home_change_wins
        away_relative_wins = total_windows - home_relative_wins
        
        # Store results
        results.append({
            'match_id': match_id,
            'team': home_team,
            'team_type': 'home',
            'total_windows': total_windows,
            'momentum_wins': home_momentum_wins,
            'change_wins': home_change_wins,
            'relative_wins': home_relative_wins,
            'momentum_win_rate': home_momentum_wins / total_windows,
            'change_win_rate': home_change_wins / total_windows,
            'relative_win_rate': home_relative_wins / total_windows
        })
        
        results.append({
            'match_id': match_id,
            'team': away_team,
            'team_type': 'away',
            'total_windows': total_windows,
            'momentum_wins': away_momentum_wins,
            'change_wins': away_change_wins,
            'relative_wins': away_relative_wins,
            'momentum_win_rate': away_momentum_wins / total_windows,
            'change_win_rate': away_change_wins / total_windows,
            'relative_win_rate': away_relative_wins / total_windows
        })
        
        # Print results for this match
        print(f"{match_id:>10} {home_team:>15} {total_windows:>8} {home_momentum_wins:>8} {home_change_wins:>10} {home_relative_wins:>10}")
        print(f"{match_id:>10} {away_team:>15} {total_windows:>8} {away_momentum_wins:>8} {away_change_wins:>10} {away_relative_wins:>10}")
        print("-" * 70)
    
    # Convert to DataFrame for analysis
    results_df = pd.DataFrame(results)
    
    # Overall statistics
    print(f"\n📊 OVERALL STATISTICS")
    print("-" * 30)
    print(f"Total matches analyzed: {len(df['match_id'].unique())}")
    print(f"Total teams: {len(results_df)}")
    print(f"Average windows per match: {df.groupby('match_id').size().mean():.1f}")
    
    # Win rate distributions
    print(f"\n📈 WIN RATE DISTRIBUTIONS")
    print("-" * 35)
    print(f"{'Metric':>20} {'Min':>8} {'Max':>8} {'Mean':>8} {'Std':>8}")
    print("-" * 55)
    
    metrics = [
        ('Momentum Superiority', 'momentum_win_rate'),
        ('Change Superiority', 'change_win_rate'),
        ('Relative Superiority', 'relative_win_rate')
    ]
    
    for name, col in metrics:
        min_val = results_df[col].min()
        max_val = results_df[col].max()
        mean_val = results_df[col].mean()
        std_val = results_df[col].std()
        print(f"{name:>20} {min_val:>8.3f} {max_val:>8.3f} {mean_val:>8.3f} {std_val:>8.3f}")
    
    # Dominant teams analysis
    print(f"\n🏆 MOST DOMINANT TEAMS")
    print("-" * 30)
    
    # Sort by momentum win rate
    top_momentum = results_df.nlargest(5, 'momentum_win_rate')
    print(f"\nTop 5 - Momentum Superiority:")
    for _, row in top_momentum.iterrows():
        print(f"  {row['team']:>15} ({row['match_id']}) - {row['momentum_wins']:>2}/{row['total_windows']:>2} windows ({row['momentum_win_rate']*100:>5.1f}%)")
    
    # Sort by change win rate
    top_change = results_df.nlargest(5, 'change_win_rate')
    print(f"\nTop 5 - Change Superiority:")
    for _, row in top_change.iterrows():
        print(f"  {row['team']:>15} ({row['match_id']}) - {row['change_wins']:>2}/{row['total_windows']:>2} windows ({row['change_win_rate']*100:>5.1f}%)")
    
    # Sort by relative win rate
    top_relative = results_df.nlargest(5, 'relative_win_rate')
    print(f"\nTop 5 - Relative Change Superiority:")
    for _, row in top_relative.iterrows():
        print(f"  {row['team']:>15} ({row['match_id']}) - {row['relative_wins']:>2}/{row['total_windows']:>2} windows ({row['relative_win_rate']*100:>5.1f}%)")
    
    # Consistency analysis
    print(f"\n🎯 CONSISTENCY ANALYSIS")
    print("-" * 25)
    
    # Teams that dominated in all three metrics
    high_performers = results_df[
        (results_df['momentum_win_rate'] > 0.6) &
        (results_df['change_win_rate'] > 0.6) &
        (results_df['relative_win_rate'] > 0.6)
    ]
    
    print(f"Teams dominant in all 3 metrics (>60% win rate): {len(high_performers)}")
    if len(high_performers) > 0:
        for _, row in high_performers.iterrows():
            print(f"  {row['team']:>15} ({row['match_id']}) - Mom: {row['momentum_win_rate']*100:>5.1f}%, "
                  f"Chg: {row['change_win_rate']*100:>5.1f}%, Rel: {row['relative_win_rate']*100:>5.1f}%")
    
    # Correlation analysis
    print(f"\n🔗 CORRELATION ANALYSIS")
    print("-" * 25)
    
    corr_mom_change = results_df['momentum_win_rate'].corr(results_df['change_win_rate'])
    corr_mom_relative = results_df['momentum_win_rate'].corr(results_df['relative_win_rate'])
    corr_change_relative = results_df['change_win_rate'].corr(results_df['relative_win_rate'])
    
    print(f"Momentum vs Change superiority:    {corr_mom_change:>6.3f}")
    print(f"Momentum vs Relative superiority:  {corr_mom_relative:>6.3f}")
    print(f"Change vs Relative superiority:    {corr_change_relative:>6.3f}")
    
    # Balanced games analysis
    print(f"\n⚖️ BALANCED GAMES ANALYSIS")
    print("-" * 30)
    
    # Find games where teams were very close in performance
    balanced_threshold = 0.1  # Within 10% win rate
    
    match_balance = []
    for match_id in df['match_id'].unique():
        match_teams = results_df[results_df['match_id'] == match_id]
        if len(match_teams) == 2:
            diff_momentum = abs(match_teams['momentum_win_rate'].iloc[0] - match_teams['momentum_win_rate'].iloc[1])
            diff_change = abs(match_teams['change_win_rate'].iloc[0] - match_teams['change_win_rate'].iloc[1])
            diff_relative = abs(match_teams['relative_win_rate'].iloc[0] - match_teams['relative_win_rate'].iloc[1])
            
            match_balance.append({
                'match_id': match_id,
                'team1': match_teams['team'].iloc[0],
                'team2': match_teams['team'].iloc[1],
                'momentum_balance': diff_momentum < balanced_threshold,
                'change_balance': diff_change < balanced_threshold,
                'relative_balance': diff_relative < balanced_threshold,
                'all_balanced': (diff_momentum < balanced_threshold) and 
                               (diff_change < balanced_threshold) and 
                               (diff_relative < balanced_threshold)
            })
    
    balance_df = pd.DataFrame(match_balance)
    balanced_games = balance_df['all_balanced'].sum()
    
    print(f"Highly balanced games (all metrics within 10%): {balanced_games}/{len(balance_df)} ({balanced_games/len(balance_df)*100:.1f}%)")
    
    if balanced_games > 0:
        print("Most balanced games:")
        balanced_matches = balance_df[balance_df['all_balanced']]
        for _, row in balanced_matches.head(5).iterrows():
            print(f"  {row['team1']} vs {row['team2']} ({row['match_id']})")
    
    logger.info("✅ Team superiority analysis completed!")
    
    return results_df

def main():
    """Main execution function."""
    print("📊 Team Superiority by Game Analyzer")
    print("=" * 45)
    
    # Analyze team superiority
    result_df = analyze_team_superiority_by_game()
    
    print(f"\n✅ Analysis completed!")
    print(f"Analyzed {len(result_df)} team performances across games")

if __name__ == "__main__":
    main()
