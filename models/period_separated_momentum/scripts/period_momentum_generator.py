#!/usr/bin/env python3
"""
Period-Separated Momentum Generator
====================================

Generates momentum data with proper period separation to avoid mixing
first half stoppage time with second half data.

Key changes from original:
- Filters events by period BEFORE calculating momentum
- Adds period column to output
- Period 1: First half (0-45+stoppage)
- Period 2: Second half (45-90+stoppage)

Author: Euro 2024 Momentum Prediction Project
Date: December 2024
"""

import sys
import pandas as pd
import numpy as np
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import warnings

warnings.filterwarnings('ignore')

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "preprocessing" / "input_generation" / "scripts"))
from momentum_3min_calculator import MomentumCalculator


class PeriodSeparatedMomentumGenerator:
    """
    Generate momentum data with proper period separation.
    """
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.calculator = MomentumCalculator(verbose=verbose)
        
        # Paths
        self.data_path = Path(__file__).parent.parent.parent.parent / "Data" / "euro_2024_complete_dataset.csv"
        self.output_path = Path(__file__).parent.parent / "outputs"
        self.output_path.mkdir(parents=True, exist_ok=True)
        
    def load_events_data(self) -> pd.DataFrame:
        """Load the complete events dataset"""
        print(f"📂 Loading events data from {self.data_path}")
        df = pd.read_csv(self.data_path, low_memory=False)
        print(f"   Loaded {len(df):,} events")
        return df
    
    def get_team_name(self, team_data) -> str:
        """Extract clean team name"""
        if pd.isna(team_data):
            return ''
        if isinstance(team_data, dict):
            return team_data.get('name', '')
        elif isinstance(team_data, str):
            try:
                import ast
                parsed = ast.literal_eval(team_data)
                if isinstance(parsed, dict):
                    return parsed.get('name', '')
            except:
                pass
            return team_data
        return ''
    
    def process_match_by_period(self, match_events: pd.DataFrame, match_id: int) -> List[Dict]:
        """
        Process a single match with period separation.
        
        Args:
            match_events: DataFrame with match events
            match_id: Match identifier
            
        Returns:
            List of momentum records with period information
        """
        results = []
        
        # Get team names
        home_team = self.get_team_name(match_events['home_team'].iloc[0] if 'home_team' in match_events.columns 
                                       else match_events['home_team_name'].iloc[0] if 'home_team_name' in match_events.columns else '')
        away_team = self.get_team_name(match_events['away_team'].iloc[0] if 'away_team' in match_events.columns
                                       else match_events['away_team_name'].iloc[0] if 'away_team_name' in match_events.columns else '')
        
        if not home_team or not away_team:
            # Try to extract from possession_team
            teams = match_events['possession_team'].dropna().unique()
            team_names = [self.get_team_name(t) for t in teams]
            team_names = [t for t in team_names if t]
            if len(team_names) >= 2:
                home_team = team_names[0]
                away_team = team_names[1]
        
        if not home_team or not away_team:
            print(f"   ⚠️ Could not identify teams for match {match_id}")
            return results
        
        # Process each period separately (1, 2 = regular time, 3, 4 = overtime)
        for period in [1, 2, 3, 4]:
            period_events = match_events[match_events['period'] == period].copy()
            
            if len(period_events) == 0:
                continue
            
            # DO NOT sort - preserve original event order to match original calculation
            # The momentum calculator uses order-dependent weighting
            
            min_minute = int(period_events['minute'].min())
            max_minute = int(period_events['minute'].max())
            
            if self.verbose:
                print(f"   Period {period}: minutes {min_minute}-{max_minute}, {len(period_events)} events")
            
            # Calculate momentum for 3-minute windows within this period
            # Window format: "0-2" means minutes 0, 1, 2 (inclusive)
            # Start from minute 0 for period 1, or min_minute for period 2
            if period == 1:
                first_window_start = 0
            else:
                first_window_start = min_minute
            
            for window_start in range(first_window_start, max_minute - 1):
                window_end = window_start + 2  # Inclusive end (3 minutes: start, start+1, start+2)
                
                # Get events in this window (for THIS PERIOD ONLY)
                # Include events at minute window_start, window_start+1, window_start+2
                window_events = period_events[
                    (period_events['minute'] >= window_start) & 
                    (period_events['minute'] <= window_end)
                ].to_dict('records')
                
                # DO NOT skip empty windows - include them with momentum=0 (matches original)
                if len(window_events) == 0:
                    home_momentum = 0.0
                    away_momentum = 0.0
                else:
                    # Use score_diff = 0 to match original data generation approach
                    home_context = {'score_diff': 0, 'minute': window_start}
                    away_context = {'score_diff': 0, 'minute': window_start}
                    
                    home_momentum = self.calculator.calculate_3min_team_momentum(window_events, home_team, home_context)
                    away_momentum = self.calculator.calculate_3min_team_momentum(window_events, away_team, away_context)
                
                results.append({
                    'match_id': match_id,
                    'period': period,
                    'minute_range': f"{window_start}-{window_end}",  # Format: "0-2" for minutes 0,1,2
                    'minute': window_start,  # For easier filtering
                    'team_home': home_team,
                    'team_away': away_team,
                    'team_home_momentum': round(home_momentum, 3),
                    'team_away_momentum': round(away_momentum, 3),
                    'events_in_window': len(window_events)
                })
        
        return results
    
    def calculate_momentum_change(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate momentum change: y(t) = momentum(t+3) - momentum(t)
        
        Matches ORIGINAL approach: find future window by MINUTE (start_minute + 3),
        not by index. This is critical when there are gaps in minutes.
        """
        df = df.sort_values(['match_id', 'period', 'minute']).reset_index(drop=True)
        
        # Initialize change columns with NaN
        df['team_home_momentum_change'] = np.nan
        df['team_away_momentum_change'] = np.nan
        
        # Calculate changes within each match-period group
        for (match_id, period), group in df.groupby(['match_id', 'period']):
            group_data = group.copy()
            
            for idx, row in group_data.iterrows():
                current_minute = row['minute']
                future_minute = current_minute + 3  # Look for minute t+3
                
                # Find the future window by MINUTE (not index)
                future_row = group_data[group_data['minute'] == future_minute]
                
                if len(future_row) > 0:
                    future_home = future_row.iloc[0]['team_home_momentum']
                    future_away = future_row.iloc[0]['team_away_momentum']
                    
                    # Momentum change = future(t+3) - current(t)
                    df.loc[idx, 'team_home_momentum_change'] = round(
                        future_home - row['team_home_momentum'], 3
                    )
                    df.loc[idx, 'team_away_momentum_change'] = round(
                        future_away - row['team_away_momentum'], 3
                    )
        
        return df
    
    def generate(self) -> pd.DataFrame:
        """
        Main generation function.
        
        Returns:
            DataFrame with period-separated momentum data
        """
        print("\n" + "="*60)
        print("🎯 PERIOD-SEPARATED MOMENTUM GENERATOR")
        print("="*60)
        
        # Load events
        events_df = self.load_events_data()
        
        # Get unique matches
        match_ids = events_df['match_id'].unique()
        print(f"\n📊 Processing {len(match_ids)} matches...")
        
        all_results = []
        
        for i, match_id in enumerate(match_ids):
            match_events = events_df[events_df['match_id'] == match_id].copy()
            
            if self.verbose or (i + 1) % 10 == 0:
                print(f"   [{i+1}/{len(match_ids)}] Processing match {match_id}")
            
            match_results = self.process_match_by_period(match_events, match_id)
            all_results.extend(match_results)
        
        # Create DataFrame
        df = pd.DataFrame(all_results)
        
        if len(df) == 0:
            print("❌ No results generated!")
            return df
        
        # Calculate momentum change
        print("\n📈 Calculating momentum changes...")
        df = self.calculate_momentum_change(df)
        
        # Save output
        output_file = self.output_path / "momentum_by_period.csv"
        df.to_csv(output_file, index=False)
        print(f"\n✅ Saved to {output_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("📊 SUMMARY")
        print("="*60)
        print(f"Total records: {len(df):,}")
        print(f"Unique matches: {df['match_id'].nunique()}")
        print(f"Period 1 records: {len(df[df['period'] == 1]):,}")
        print(f"Period 2 records: {len(df[df['period'] == 2]):,}")
        
        # Show sample
        print("\n📋 Sample data:")
        print(df[['match_id', 'period', 'minute_range', 'team_home', 'team_away', 
                  'team_home_momentum', 'team_away_momentum']].head(10).to_string())
        
        return df


if __name__ == "__main__":
    generator = PeriodSeparatedMomentumGenerator(verbose=False)
    df = generator.generate()

