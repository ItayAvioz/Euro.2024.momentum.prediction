"""
Target Variable Generator - Momentum Change Calculator

Creates y-target variables for momentum prediction by calculating momentum change
over 3-minute windows: y(t) = momentum(t+3) - momentum(t)

Author: AI Assistant
Date: August 2024
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Tuple, Dict, Any

class MomentumTargetGenerator:
    """
    Generates target variables for momentum prediction modeling.
    
    Calculates momentum change between current and future 3-minute windows:
    y(t) = momentum(t+3) - momentum(t)
    """
    
    def __init__(self, input_file: str = None, output_file: str = None):
        """
        Initialize the target generator.
        
        Args:
            input_file: Path to input momentum windows CSV
            output_file: Path to save output targets CSV
        """
        # Set up logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Default file paths
        if input_file is None:
            input_file = "../input_generation/momentum_windows_enhanced_v2.csv"
        if output_file is None:
            output_file = "../momentum_targets_enhanced.csv"
            
        self.input_file = input_file
        self.output_file = output_file
        
        # Configuration
        self.lag_minutes = 3  # Standard 3-minute prediction horizon
        
        self.logger.info(f"Target Generator initialized:")
        self.logger.info(f"  Input: {self.input_file}")
        self.logger.info(f"  Output: {self.output_file}")
        self.logger.info(f"  Lag: {self.lag_minutes} minutes")
    
    def load_input_data(self) -> pd.DataFrame:
        """
        Load the input momentum windows dataset.
        
        Returns:
            DataFrame with momentum windows data
        """
        self.logger.info("Loading input momentum data...")
        
        try:
            df = pd.read_csv(self.input_file)
            self.logger.info(f"Loaded {len(df)} momentum windows")
            self.logger.info(f"Columns: {list(df.columns)}")
            
            # Validate required columns
            required_cols = ['match_id', 'minute_range', 'team_home_momentum', 'team_away_momentum']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            # Parse minute range for easier processing
            df['start_minute'] = df['minute_range'].str.split('-').str[0].astype(int)
            df['end_minute'] = df['minute_range'].str.split('-').str[1].astype(int)
            
            self.logger.info("Input data loaded successfully")
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading input data: {e}")
            raise
    
    def find_future_windows(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Find future windows (t+3) for each current window (t).
        
        Args:
            df: Input dataframe with momentum windows
            
        Returns:
            DataFrame with future window information added
        """
        self.logger.info("Finding future windows for target calculation...")
        
        # Initialize new columns
        df['future_window_start'] = df['start_minute'] + self.lag_minutes
        df['future_window_end'] = df['end_minute'] + self.lag_minutes
        df['future_window_minutes'] = df['future_window_start'].astype(str) + '-' + df['future_window_end'].astype(str)
        df['has_future_window'] = False
        df['future_home_momentum'] = np.nan
        df['future_away_momentum'] = np.nan
        
        # Process each match separately
        matches_processed = 0
        total_windows = len(df)
        windows_with_future = 0
        
        for match_id in df['match_id'].unique():
            match_data = df[df['match_id'] == match_id].copy()
            
            # For each window in this match, find its future window
            for idx, row in match_data.iterrows():
                future_start = row['future_window_start']
                future_end = row['future_window_end']
                
                # Look for matching future window in same match
                future_window = match_data[
                    (match_data['start_minute'] == future_start) & 
                    (match_data['end_minute'] == future_end)
                ]
                
                if len(future_window) > 0:
                    # Found future window - extract momentum values
                    future_row = future_window.iloc[0]
                    df.at[idx, 'has_future_window'] = True
                    df.at[idx, 'future_home_momentum'] = future_row['team_home_momentum']
                    df.at[idx, 'future_away_momentum'] = future_row['team_away_momentum']
                    windows_with_future += 1
            
            matches_processed += 1
            if matches_processed % 10 == 0:
                self.logger.info(f"  Processed {matches_processed} matches...")
        
        self.logger.info(f"Future window matching completed:")
        self.logger.info(f"  Total windows: {total_windows}")
        self.logger.info(f"  Windows with future: {windows_with_future}")
        self.logger.info(f"  Windows without future: {total_windows - windows_with_future}")
        self.logger.info(f"  Coverage: {windows_with_future/total_windows*100:.1f}%")
        
        return df
    
    def calculate_momentum_targets(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate momentum change targets: y(t) = momentum(t+3) - momentum(t)
        
        Args:
            df: DataFrame with current and future momentum values
            
        Returns:
            DataFrame with target variables added
        """
        self.logger.info("Calculating momentum change targets...")
        
        # Calculate momentum changes for windows with future data
        mask = df['has_future_window'] == True
        
        df['team_home_momentum_change'] = np.nan
        df['team_away_momentum_change'] = np.nan
        
        # Calculate changes: future - current
        df.loc[mask, 'team_home_momentum_change'] = (
            df.loc[mask, 'future_home_momentum'] - df.loc[mask, 'team_home_momentum']
        )
        df.loc[mask, 'team_away_momentum_change'] = (
            df.loc[mask, 'future_away_momentum'] - df.loc[mask, 'team_away_momentum']
        )
        
        # Add processing notes
        df['target_calculation_notes'] = 'No future window available'
        df.loc[mask, 'target_calculation_notes'] = 'Target calculated successfully'
        
        # Calculate statistics
        valid_targets = df[mask]
        n_valid = len(valid_targets)
        
        if n_valid > 0:
            home_stats = valid_targets['team_home_momentum_change'].describe()
            away_stats = valid_targets['team_away_momentum_change'].describe()
            
            self.logger.info(f"Target calculation completed:")
            self.logger.info(f"  Valid targets: {n_valid}")
            self.logger.info(f"  Home momentum change - Mean: {home_stats['mean']:.3f}, Std: {home_stats['std']:.3f}")
            self.logger.info(f"  Away momentum change - Mean: {away_stats['mean']:.3f}, Std: {away_stats['std']:.3f}")
            self.logger.info(f"  Home range: [{home_stats['min']:.3f}, {home_stats['max']:.3f}]")
            self.logger.info(f"  Away range: [{away_stats['min']:.3f}, {away_stats['max']:.3f}]")
        
        return df
    
    def validate_targets(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate the generated target variables.
        
        Args:
            df: DataFrame with target variables
            
        Returns:
            Dictionary with validation results
        """
        self.logger.info("Validating target variables...")
        
        validation_results = {
            'total_windows': len(df),
            'windows_with_targets': len(df[df['has_future_window'] == True]),
            'windows_without_targets': len(df[df['has_future_window'] == False]),
            'target_coverage': len(df[df['has_future_window'] == True]) / len(df) * 100,
            'unique_matches': df['match_id'].nunique(),
            'home_target_stats': {},
            'away_target_stats': {},
            'issues': []
        }
        
        # Calculate target statistics
        valid_df = df[df['has_future_window'] == True]
        
        if len(valid_df) > 0:
            validation_results['home_target_stats'] = {
                'mean': valid_df['team_home_momentum_change'].mean(),
                'std': valid_df['team_home_momentum_change'].std(),
                'min': valid_df['team_home_momentum_change'].min(),
                'max': valid_df['team_home_momentum_change'].max(),
                'null_count': valid_df['team_home_momentum_change'].isnull().sum()
            }
            
            validation_results['away_target_stats'] = {
                'mean': valid_df['team_away_momentum_change'].mean(),
                'std': valid_df['team_away_momentum_change'].std(),
                'min': valid_df['team_away_momentum_change'].min(),
                'max': valid_df['team_away_momentum_change'].max(),
                'null_count': valid_df['team_away_momentum_change'].isnull().sum()
            }
        
        # Check for issues
        if validation_results['target_coverage'] < 70:
            validation_results['issues'].append(f"Low target coverage: {validation_results['target_coverage']:.1f}%")
        
        if len(valid_df) > 0:
            if valid_df['team_home_momentum_change'].isnull().sum() > 0:
                validation_results['issues'].append("Null values in home momentum change targets")
            
            if valid_df['team_away_momentum_change'].isnull().sum() > 0:
                validation_results['issues'].append("Null values in away momentum change targets")
        
        # Log validation results
        self.logger.info("Validation Results:")
        self.logger.info(f"  Target Coverage: {validation_results['target_coverage']:.1f}%")
        self.logger.info(f"  Windows with targets: {validation_results['windows_with_targets']}")
        self.logger.info(f"  Windows without targets: {validation_results['windows_without_targets']}")
        
        if validation_results['issues']:
            self.logger.warning("Issues found:")
            for issue in validation_results['issues']:
                self.logger.warning(f"  - {issue}")
        else:
            self.logger.info("✅ All validation checks passed!")
        
        return validation_results
    
    def save_output(self, df: pd.DataFrame) -> None:
        """
        Save the final dataset with target variables.
        
        Args:
            df: DataFrame with target variables to save
        """
        self.logger.info(f"Saving output to {self.output_file}...")
        
        try:
            # Create output directory if it doesn't exist
            output_path = Path(self.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to CSV
            df.to_csv(self.output_file, index=False)
            
            self.logger.info(f"✅ Output saved successfully!")
            self.logger.info(f"  File: {self.output_file}")
            self.logger.info(f"  Shape: {df.shape}")
            self.logger.info(f"  Columns: {len(df.columns)}")
            
        except Exception as e:
            self.logger.error(f"Error saving output: {e}")
            raise
    
    def generate_targets(self) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Main method to generate target variables from input momentum data.
        
        Returns:
            Tuple of (final_dataframe, validation_results)
        """
        self.logger.info("🎯 Starting Target Variable Generation...")
        
        try:
            # Step 1: Load input data
            df = self.load_input_data()
            
            # Step 2: Find future windows
            df = self.find_future_windows(df)
            
            # Step 3: Calculate momentum change targets  
            df = self.calculate_momentum_targets(df)
            
            # Step 4: Validate results
            validation_results = self.validate_targets(df)
            
            # Step 5: Save output
            self.save_output(df)
            
            self.logger.info("🎉 Target Variable Generation completed successfully!")
            
            return df, validation_results
            
        except Exception as e:
            self.logger.error(f"❌ Target generation failed: {e}")
            raise

def main():
    """Main execution function."""
    print("🎯 Momentum Target Variable Generator")
    print("=" * 50)
    
    # Initialize generator
    generator = MomentumTargetGenerator()
    
    # Generate targets
    df, validation = generator.generate_targets()
    
    # Display summary
    print("\n📊 Generation Summary:")
    print(f"Total Windows: {validation['total_windows']}")
    print(f"Windows with Targets: {validation['windows_with_targets']}")
    print(f"Target Coverage: {validation['target_coverage']:.1f}%")
    print(f"Unique Matches: {validation['unique_matches']}")
    
    if validation['windows_with_targets'] > 0:
        print(f"\nHome Momentum Change:")
        print(f"  Mean: {validation['home_target_stats']['mean']:.3f}")
        print(f"  Std: {validation['home_target_stats']['std']:.3f}")
        print(f"  Range: [{validation['home_target_stats']['min']:.3f}, {validation['home_target_stats']['max']:.3f}]")
        
        print(f"\nAway Momentum Change:")
        print(f"  Mean: {validation['away_target_stats']['mean']:.3f}")
        print(f"  Std: {validation['away_target_stats']['std']:.3f}")
        print(f"  Range: [{validation['away_target_stats']['min']:.3f}, {validation['away_target_stats']['max']:.3f}]")
    
    print("\n✅ Target generation completed!")

if __name__ == "__main__":
    main()
