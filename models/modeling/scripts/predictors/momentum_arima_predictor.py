"""
Main ARIMA Prediction Pipeline

Runs pure ARIMA models on momentum data across all games:
1. momentum → momentum predictions  
2. momentum_change → momentum_change predictions

Author: AI Assistant
Date: August 2024
"""

import pandas as pd
import numpy as np
import yaml
import logging
from pathlib import Path
from typing import List, Dict, Tuple
import sys

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from models.arima_model import MomentumARIMAPredictor

class MainARIMAPipeline:
    """Main pipeline for running ARIMA models on all games."""
    
    def __init__(self, config_path: str = "../configs/arima_config.yaml"):
        """Initialize the ARIMA prediction pipeline."""
        # Set up logging first
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        self.config = self._load_config(config_path)
        self.results = []
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            else:
                self.logger.warning(f"Config file {config_path} not found. Using defaults.")
                return self._get_default_config()
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default configuration."""
        return {
            'arima_params': {
                'max_p': 2, 'max_d': 1, 'max_q': 2,
                'seasonal': False, 'auto_select': True,
                'information_criterion': 'aic'
            },
            'data_split': {
                'train_end_minute': 75,
                'test_start_minute': 75,
                'test_end_minute': 90
            },
            'evaluation': {'primary_metric': 'mse'},
            'output': {'results_file': '../outputs/arima_predictions.csv'},
            'validation': {'min_train_observations': 10, 'max_missing_ratio': 0.2}
        }
    
    def load_data(self, data_path: str) -> pd.DataFrame:
        """Load momentum data from CSV."""
        try:
            df = pd.read_csv(data_path)
            self.logger.info(f"Loaded data: {len(df)} rows, {len(df['match_id'].unique())} unique matches")
            
            # Extract minute from minute_range for proper ordering
            df['minute'] = df['minute_range'].str.split('-').str[0].astype(int)
            
            return df
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            raise
    
    def prepare_game_data(self, df: pd.DataFrame, match_id: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Prepare training and testing data for a specific game.
        
        Args:
            df: Full dataset
            match_id: Match ID to process
            
        Returns:
            Tuple of (train_data, test_data) - both chronologically ordered
        """
        # Filter and sort data for this match
        match_data = df[df['match_id'] == match_id].copy()
        match_data = match_data.sort_values('minute').reset_index(drop=True)
        
        # Split based on minute thresholds  
        train_end = self.config['data_split']['train_end_minute']
        test_start = self.config['data_split']['test_start_minute']
        test_end = self.config['data_split']['test_end_minute']
        
        train_data = match_data[match_data['minute'] < train_end]
        test_data = match_data[
            (match_data['minute'] >= test_start) & 
            (match_data['minute'] < test_end)
        ]
        
        return train_data, test_data
    
    def run_arima_for_team(
        self,
        train_data: pd.DataFrame,
        test_data: pd.DataFrame,
        team_type: str,  # 'home' or 'away'
        match_id: int,
        team_name: str
    ) -> List[Dict]:
        """
        Run ARIMA models for a specific team.
        
        Args:
            train_data: Training dataset (chronologically ordered)
            test_data: Testing dataset (chronologically ordered)
            team_type: 'home' or 'away'
            match_id: Match identifier
            team_name: Team name
            
        Returns:
            List of prediction results
        """
        results = []
        
        try:
            # Prepare data series for this team
            momentum_col = f'team_{team_type}_momentum'
            change_col = f'team_{team_type}_momentum_change'
            
            # Create time series (chronologically ordered)
            momentum_train = pd.Series(
                train_data[momentum_col].values,
                index=range(len(train_data))
            )
            change_train = pd.Series(
                train_data[change_col].values,
                index=range(len(train_data))
            )
            
            # Initialize ARIMA predictor
            predictor = MomentumARIMAPredictor(self.config)
            
            # Train models
            trained_models = predictor.train_models(momentum_train, change_train)
            
            if not trained_models:
                self.logger.warning(f"No models trained for {team_name}")
                return results
            
            # Generate predictions
            n_predictions = len(test_data)
            predictions = predictor.predict_all(n_predictions)
            
            # Get actual values
            actual_momentum = test_data[momentum_col].values
            actual_change = test_data[change_col].values
            
            # Process results for each model type
            model_mappings = [
                ('momentum', predictions.get('momentum'), actual_momentum, 'momentum_to_momentum'),
                ('change', predictions.get('change'), actual_change, 'change_to_change')
            ]
            
            for model_key, pred_values, actual_values, model_type in model_mappings:
                if pred_values is not None and model_key in trained_models:
                    # Evaluate model
                    metrics = trained_models[model_key].evaluate(actual_values, pred_values)
                    model_info = trained_models[model_key].get_model_info()
                    
                    # Store individual predictions
                    for i, (_, row) in enumerate(test_data.iterrows()):
                        if i < len(pred_values) and i < len(actual_values):
                            result = {
                                'game_id': match_id,
                                'team': team_name,
                                'model_type': model_type,
                                'minutes_prediction': row['minute_range'],
                                'minute_start': row['minute'],
                                'prediction_value': float(pred_values[i]),
                                'actual_value': float(actual_values[i]),
                                'mse': float(metrics['mse']),
                                'adjusted_r2': float(metrics['adjusted_r2']),
                                'directional_accuracy': float(metrics['directional_accuracy']),
                                'arima_order': str(model_info['arima_order']),
                                'n_train_observations': int(model_info['training_size'])
                            }
                            results.append(result)
            
            self.logger.info(f"✅ Processed {team_name}: {len(results)} predictions generated")
            
        except Exception as e:
            import traceback
            self.logger.error(f"❌ Error processing {team_name}: {e}")
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
        
        return results
    
    def run_all_predictions(self, data_path: str) -> pd.DataFrame:
        """
        Run ARIMA predictions for all games and teams.
        
        Args:
            data_path: Path to momentum data CSV
            
        Returns:
            DataFrame with all prediction results
        """
        self.logger.info("🚀 Starting ARIMA prediction pipeline...")
        
        # Load data
        df = self.load_data(data_path)
        
        # Get unique matches
        unique_matches = sorted(df['match_id'].unique())
        self.logger.info(f"Processing {len(unique_matches)} matches")
        
        all_results = []
        
        for i, match_id in enumerate(unique_matches):
            self.logger.info(f"Processing match {match_id} ({i+1}/{len(unique_matches)})")
            
            # Prepare game data
            train_data, test_data = self.prepare_game_data(df, match_id)
            
            if len(train_data) < self.config['validation']['min_train_observations']:
                self.logger.warning(f"Insufficient training data for match {match_id}: {len(train_data)}")
                continue
                
            if len(test_data) == 0:
                self.logger.warning(f"No test data for match {match_id}")
                continue
            
            # Get team names
            home_team = train_data['team_home'].iloc[0]
            away_team = train_data['team_away'].iloc[0]
            
            # Run ARIMA for both teams
            for team_type, team_name in [('home', home_team), ('away', away_team)]:
                team_results = self.run_arima_for_team(
                    train_data, test_data, team_type, match_id, team_name
                )
                all_results.extend(team_results)
        
        # Convert to DataFrame and save
        if all_results:
            results_df = pd.DataFrame(all_results)
            
            # Save results
            output_path = Path(self.config['output']['results_file'])
            output_path.parent.mkdir(parents=True, exist_ok=True)
            results_df.to_csv(output_path, index=False)
            
            self.logger.info(f"✅ Saved {len(results_df)} predictions to {output_path}")
            
            # Display summary
            self._display_summary(results_df)
            
            return results_df
        else:
            self.logger.error("❌ No predictions generated!")
            return pd.DataFrame()
    
    def _display_summary(self, results_df: pd.DataFrame):
        """Display summary statistics of results."""
        print(f"\n📊 ARIMA PREDICTION SUMMARY")
        print("=" * 50)
        print(f"Total predictions: {len(results_df):,}")
        print(f"Unique games: {results_df['game_id'].nunique()}")
        print(f"Teams analyzed: {results_df['team'].nunique()}")
        print(f"Model types: {results_df['model_type'].unique()}")
        
        print(f"\n📈 Performance by Model Type:")
        for model_type in results_df['model_type'].unique():
            subset = results_df[results_df['model_type'] == model_type]
            avg_mse = subset['mse'].mean()
            avg_r2 = subset['adjusted_r2'].mean()
            avg_dir = subset['directional_accuracy'].mean()
            print(f"  {model_type}:")
            print(f"    Average MSE: {avg_mse:.4f}")
            print(f"    Average Adjusted R²: {avg_r2:.4f}")
            print(f"    Average Directional Accuracy: {avg_dir:.4f}")
        
        print(f"\n📋 Sample Results:")
        print(results_df[['game_id', 'team', 'model_type', 'minutes_prediction', 
                         'prediction_value', 'actual_value', 'mse']].head(10))

def main():
    """Main execution function."""
    print("🚀 Pure ARIMA Momentum Prediction Pipeline")
    print("=" * 60)
    
    # Initialize pipeline
    pipeline = MainARIMAPipeline()
    
    # Run predictions
    data_path = "../../../preprocessing/data/targets/momentum_targets_streamlined.csv"
    results = pipeline.run_all_predictions(data_path)
    
    print(f"\n✅ Pipeline completed!")
    if len(results) > 0:
        print(f"Results saved to: ../outputs/predictions/arima_predictions.csv")
    else:
        print("❌ No results generated - check logs for errors")

if __name__ == "__main__":
    main()
