"""
Create Streamlined Target Dataset

Creates a minimal version of the target dataset with only essential columns for modeling.

Author: AI Assistant
Date: August 2024
"""

import pandas as pd
import logging
from pathlib import Path

def create_streamlined_targets():
    """Create streamlined target dataset with only essential columns."""
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    logger.info("🎯 Creating Streamlined Target Dataset...")
    
    # File paths
    input_file = "../data/targets/momentum_targets_enhanced.csv"
    output_file = "../data/targets/momentum_targets_streamlined.csv"
    
    try:
        # Load full dataset
        logger.info("Loading full target dataset...")
        df_full = pd.read_csv(input_file)
        logger.info(f"Loaded {len(df_full)} windows with {len(df_full.columns)} columns")
        
        # Select only essential columns
        essential_columns = [
            # Match identification
            'match_id',
            'minute_range',
            'team_home',
            'team_away',
            
            # Current momentum (features)
            'team_home_momentum',
            'team_away_momentum',
            
            # Target variables (what we want to predict)
            'team_home_momentum_change',
            'team_away_momentum_change',
            
            # Data quality indicators
            'has_future_window'
        ]
        
        # Create streamlined dataset
        df_streamlined = df_full[essential_columns].copy()
        
        # Filter to only windows with valid targets
        df_streamlined = df_streamlined[df_streamlined['has_future_window'] == True].copy()
        
        # Drop the has_future_window column since all remaining rows are True
        df_streamlined = df_streamlined.drop('has_future_window', axis=1)
        
        # Save streamlined dataset
        logger.info(f"Saving streamlined dataset to {output_file}...")
        df_streamlined.to_csv(output_file, index=False)
        
        # Report results
        logger.info("✅ Streamlined dataset created successfully!")
        logger.info(f"  Original: {df_full.shape[0]} windows × {df_full.shape[1]} columns")
        logger.info(f"  Streamlined: {df_streamlined.shape[0]} windows × {df_streamlined.shape[1]} columns")
        logger.info(f"  Size reduction: {(1 - df_streamlined.shape[1]/df_full.shape[1])*100:.1f}% fewer columns")
        logger.info(f"  Data reduction: {(1 - df_streamlined.shape[0]/df_full.shape[0])*100:.1f}% fewer rows (removed invalid targets)")
        
        # Show sample
        print("\n📊 Streamlined Dataset Sample:")
        print("=" * 60)
        print(f"Shape: {df_streamlined.shape}")
        print(f"Columns: {list(df_streamlined.columns)}")
        print("\nFirst 5 rows:")
        print(df_streamlined.head())
        
        print(f"\nTarget Statistics:")
        print(f"Home momentum change - Mean: {df_streamlined['team_home_momentum_change'].mean():.3f}, Std: {df_streamlined['team_home_momentum_change'].std():.3f}")
        print(f"Away momentum change - Mean: {df_streamlined['team_away_momentum_change'].mean():.3f}, Std: {df_streamlined['team_away_momentum_change'].std():.3f}")
        
        return df_streamlined
        
    except Exception as e:
        logger.error(f"❌ Error creating streamlined dataset: {e}")
        raise

def main():
    """Main execution function."""
    print("🎯 Streamlined Target Dataset Creator")
    print("=" * 50)
    
    # Create streamlined dataset
    df = create_streamlined_targets()
    
    print(f"\n✅ Streamlined dataset created successfully!")
    print(f"File: momentum_targets_streamlined.csv")
    print(f"Ready for modeling with {len(df)} windows!")

if __name__ == "__main__":
    main()
