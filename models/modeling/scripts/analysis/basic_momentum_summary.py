#!/usr/bin/env python3
"""
Basic Momentum Analysis Summary
Creates summary statistics from ARIMA and ARIMAX predictions with corrected team assignments

Author: AI Assistant
Date: September 2024
"""

import pandas as pd
import numpy as np
from pathlib import Path

def load_predictions():
    """Load both ARIMA and ARIMAX predictions"""
    arima_path = Path("../outputs/predictions/arima_predictions.csv")
    arimax_path = Path("../outputs/predictions/arimax_predictions.csv")
    
    arima_df = pd.read_csv(arima_path) if arima_path.exists() else pd.DataFrame()
    arimax_df = pd.read_csv(arimax_path) if arimax_path.exists() else pd.DataFrame()
    
    # Combine both datasets
    all_predictions = pd.concat([arima_df, arimax_df], ignore_index=True)
    
    print(f"📊 LOADED PREDICTIONS")
    print(f"ARIMA predictions: {len(arima_df):,}")
    print(f"ARIMAX predictions: {len(arimax_df):,}")
    print(f"Total predictions: {len(all_predictions):,}")
    print(f"Unique games: {all_predictions['game_id'].nunique()}")
    print(f"Teams analyzed: {all_predictions['team'].nunique()}")
    print(f"Model types: {all_predictions['model_type'].unique().tolist()}")
    
    return all_predictions

def analyze_performance(df):
    """Analyze prediction performance by model type"""
    print(f"\n📈 PERFORMANCE ANALYSIS")
    print("=" * 50)
    
    performance_stats = []
    
    for model_type in df['model_type'].unique():
        subset = df[df['model_type'] == model_type]
        
        # Calculate metrics
        mse = subset['mse'].mean()
        rmse = np.sqrt(mse)
        mae = np.abs(subset['prediction_value'] - subset['actual_value']).mean()
        
        # Calculate directional accuracy (if prediction and actual have same sign)
        pred_signs = np.sign(subset['prediction_value'])
        actual_signs = np.sign(subset['actual_value'])
        directional_accuracy = (pred_signs == actual_signs).mean()
        
        stats = {
            'model_type': model_type,
            'predictions': len(subset),
            'games': subset['game_id'].nunique(),
            'teams': subset['team'].nunique(),
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'directional_accuracy': directional_accuracy
        }
        
        performance_stats.append(stats)
        
        print(f"\n{model_type}:")
        print(f"  Predictions: {len(subset):,}")
        print(f"  Games: {subset['game_id'].nunique()}")
        print(f"  Teams: {subset['team'].nunique()}")
        print(f"  MSE: {mse:.4f}")
        print(f"  RMSE: {rmse:.4f}")
        print(f"  MAE: {mae:.4f}")
        print(f"  Directional Accuracy: {directional_accuracy:.4f}")
    
    return pd.DataFrame(performance_stats)

def analyze_team_performance(df):
    """Analyze performance by team"""
    print(f"\n👥 TEAM PERFORMANCE ANALYSIS")
    print("=" * 50)
    
    team_stats = []
    
    for team in df['team'].unique():
        subset = df[df['team'] == team]
        
        stats = {
            'team': team,
            'predictions': len(subset),
            'games': subset['game_id'].nunique(),
            'avg_mse': subset['mse'].mean(),
            'avg_prediction': subset['prediction_value'].mean(),
            'avg_actual': subset['actual_value'].mean()
        }
        
        team_stats.append(stats)
    
    team_df = pd.DataFrame(team_stats).sort_values('avg_mse')
    
    print("Top 10 teams by lowest MSE:")
    print(team_df.head(10)[['team', 'predictions', 'games', 'avg_mse']].to_string(index=False))
    
    return team_df

def save_summaries(performance_df, team_df, all_predictions):
    """Save summary files"""
    output_dir = Path("../outputs/summaries")
    output_dir.mkdir(exist_ok=True)
    
    # Save performance summary
    performance_df.to_csv(output_dir / "model_performance_summary.csv", index=False)
    
    # Save team performance summary
    team_df.to_csv(output_dir / "team_performance_summary.csv", index=False)
    
    # Save overall statistics
    overall_stats = {
        'total_predictions': len(all_predictions),
        'unique_games': all_predictions['game_id'].nunique(),
        'unique_teams': all_predictions['team'].nunique(),
        'model_types': len(all_predictions['model_type'].unique()),
        'overall_mse': all_predictions['mse'].mean(),
        'overall_rmse': np.sqrt(all_predictions['mse'].mean()),
        'overall_mae': np.abs(all_predictions['prediction_value'] - all_predictions['actual_value']).mean()
    }
    
    overall_df = pd.DataFrame([overall_stats])
    overall_df.to_csv(output_dir / "overall_summary.csv", index=False)
    
    print(f"\n💾 SUMMARIES SAVED")
    print(f"Model performance: {output_dir}/model_performance_summary.csv")
    print(f"Team performance: {output_dir}/team_performance_summary.csv") 
    print(f"Overall summary: {output_dir}/overall_summary.csv")

def main():
    """Main analysis function"""
    print("🎯 BASIC MOMENTUM ANALYSIS SUMMARY")
    print("=" * 70)
    
    # Load predictions
    all_predictions = load_predictions()
    
    if len(all_predictions) == 0:
        print("❌ No predictions found!")
        return
    
    # Analyze performance
    performance_df = analyze_performance(all_predictions)
    
    # Analyze team performance
    team_df = analyze_team_performance(all_predictions)
    
    # Save summaries
    save_summaries(performance_df, team_df, all_predictions)
    
    print(f"\n✅ ANALYSIS COMPLETE!")

if __name__ == "__main__":
    main()
