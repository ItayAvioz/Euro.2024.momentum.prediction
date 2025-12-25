#!/usr/bin/env python3
"""
Period-Separated ARIMAX Predictor
=================================

Generates ARIMAX predictions using period-separated momentum data.
Trains and predicts separately for each period (1st half, 2nd half).

Key features:
- Uses period-separated momentum data
- Trains ARIMAX model per team per period
- Predicts momentum change using momentum as exogenous variable
- Outputs predictions with period information

Author: Euro 2024 Momentum Prediction Project
Date: December 2024
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')

try:
    from statsmodels.tsa.arima.model import ARIMA
    ARIMA_AVAILABLE = True
except ImportError:
    ARIMA_AVAILABLE = False
    print("Warning: ARIMA not available. Install with: pip install statsmodels")


class PeriodARIMAXPredictor:
    """
    ARIMAX predictor for period-separated momentum data.
    """
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        
        # Paths
        self.base_path = Path(__file__).parent.parent
        self.momentum_path = self.base_path / "outputs" / "momentum_by_period.csv"
        self.output_path = self.base_path / "outputs"
        
        # Configuration
        self.train_ratio = 0.75  # 75% train, 25% test
        self.arima_orders = [(1, 1, 1), (0, 1, 1), (1, 0, 1), (0, 1, 0)]
        
    def load_momentum_data(self) -> pd.DataFrame:
        """Load period-separated momentum data"""
        print(f"📂 Loading momentum data from {self.momentum_path}")
        df = pd.read_csv(self.momentum_path)
        print(f"   Loaded {len(df):,} records")
        return df
    
    def prepare_team_series(self, match_data: pd.DataFrame, team: str, 
                           is_home: bool) -> Tuple[pd.Series, pd.Series]:
        """
        Prepare momentum and change series for a team.
        
        Args:
            match_data: Match data for one period
            team: Team name
            is_home: Whether this is the home team
            
        Returns:
            Tuple of (momentum_series, change_series)
        """
        if is_home:
            momentum = match_data['team_home_momentum'].values
            change = match_data['team_home_momentum_change'].values
        else:
            momentum = match_data['team_away_momentum'].values
            change = match_data['team_away_momentum_change'].values
        
        # Create series with proper index
        momentum_series = pd.Series(momentum, index=range(len(momentum)))
        change_series = pd.Series(change, index=range(len(change)))
        
        return momentum_series, change_series
    
    def fit_arimax(self, train_change: pd.Series, train_momentum: pd.Series) -> Tuple[any, tuple]:
        """
        Fit ARIMAX model with momentum as exogenous variable.
        
        Args:
            train_change: Training change series (target)
            train_momentum: Training momentum series (exogenous)
            
        Returns:
            Tuple of (fitted_model, order)
        """
        # Clean data
        train_change = train_change.replace([np.inf, -np.inf], np.nan).dropna()
        train_momentum = train_momentum.replace([np.inf, -np.inf], np.nan).dropna()
        
        # Ensure same length
        min_len = min(len(train_change), len(train_momentum))
        train_change = train_change.iloc[:min_len]
        train_momentum = train_momentum.iloc[:min_len]
        
        if len(train_change) < 5:
            return None, (0, 0, 0)
        
        exog = train_momentum.values.reshape(-1, 1)
        
        # Try different orders
        for order in self.arima_orders:
            try:
                model = ARIMA(train_change, order=order, exog=exog).fit()
                return model, order
            except:
                continue
        
        # Fallback to mean
        return train_change.mean(), (0, 0, 0)
    
    def predict_arimax(self, model, order: tuple, steps: int, 
                      exog_future: np.ndarray) -> np.ndarray:
        """
        Generate ARIMAX predictions.
        
        Args:
            model: Fitted model or mean value
            order: ARIMA order tuple
            steps: Number of steps to predict
            exog_future: Future exogenous values
            
        Returns:
            Array of predictions
        """
        try:
            if hasattr(model, 'forecast'):
                forecast = model.forecast(steps=steps, exog=exog_future.reshape(-1, 1))
                if hasattr(forecast, 'values'):
                    return np.array(forecast.values, dtype=float)
                return np.array(forecast, dtype=float)
            else:
                # Mean fallback
                return np.full(steps, float(model))
        except Exception as e:
            if self.verbose:
                print(f"   Prediction error: {e}")
            return np.full(steps, 0.0)
    
    def process_match_period(self, match_data: pd.DataFrame, match_id: int,
                            period: int, team: str, is_home: bool) -> List[Dict]:
        """
        Process one team in one match period.
        
        Args:
            match_data: Match-period data
            match_id: Match identifier
            period: Period number (1 or 2)
            team: Team name
            is_home: Whether home team
            
        Returns:
            List of prediction records
        """
        results = []
        
        # Get series
        momentum_series, change_series = self.prepare_team_series(match_data, team, is_home)
        
        if len(momentum_series) < 10:
            return results
        
        # Train/test split
        n_train = int(len(momentum_series) * self.train_ratio)
        if n_train < 5:
            return results
        
        train_momentum = momentum_series.iloc[:n_train]
        train_change = change_series.iloc[:n_train]
        test_momentum = momentum_series.iloc[n_train:]
        test_change = change_series.iloc[n_train:]
        
        if len(test_change) == 0:
            return results
        
        # Fit ARIMAX
        model, order = self.fit_arimax(train_change, train_momentum)
        
        if model is None:
            return results
        
        # Predict
        n_test = len(test_change)
        predictions = self.predict_arimax(model, order, n_test, test_momentum.values)
        
        # Calculate metrics
        actuals = test_change.values
        mse = np.mean((predictions - actuals) ** 2)
        
        # Directional accuracy (sign agreement)
        sign_matches = np.sum(np.sign(predictions) == np.sign(actuals))
        directional_acc = sign_matches / len(actuals) if len(actuals) > 0 else 0
        
        # Get minute ranges for test period
        test_indices = match_data.index[n_train:n_train + n_test]
        minute_ranges = match_data.loc[test_indices, 'minute_range'].values
        minutes = match_data.loc[test_indices, 'minute'].values
        
        # Store predictions
        for i in range(n_test):
            results.append({
                'match_id': match_id,
                'period': period,
                'team': team,
                'is_home': is_home,
                'model_type': 'momentum_to_change_arimax',
                'minute_range': minute_ranges[i] if i < len(minute_ranges) else '',
                'minute': minutes[i] if i < len(minutes) else 0,
                'prediction_value': round(predictions[i], 6),
                'actual_value': round(actuals[i], 6),
                'mse': round(mse, 6),
                'directional_accuracy': round(directional_acc, 4),
                'arima_order': str(order),
                'n_train': n_train,
                'has_exog': True
            })
        
        return results
    
    def process_minute_based(self, train_data: pd.DataFrame, test_data: pd.DataFrame,
                              match_id: int, team: str, is_home: bool) -> List[Dict]:
        """
        Train on minutes 0-74, predict minutes 75-90 (matching original approach).
        
        Args:
            train_data: Training data (minutes 0-74)
            test_data: Test data (minutes 75-90)
            match_id: Match identifier
            team: Team name
            is_home: Whether home team
            
        Returns:
            List of prediction records
        """
        results = []
        
        # Sort data by minute
        train_data = train_data.sort_values('minute').reset_index(drop=True)
        test_data = test_data.sort_values('minute').reset_index(drop=True)
        
        # Get training series
        train_momentum, train_change = self.prepare_team_series(train_data, team, is_home)
        
        # Get test series
        test_momentum, test_change = self.prepare_team_series(test_data, team, is_home)
        
        if len(train_momentum) < 10 or len(test_change) < 3:
            return results
        
        # Fit ARIMAX on training data
        model, order = self.fit_arimax(train_change, train_momentum)
        
        if model is None:
            return results
        
        # Predict test data
        n_test = len(test_change)
        predictions = self.predict_arimax(model, order, n_test, test_momentum.values)
        
        # Calculate metrics
        actuals = test_change.values
        mse = np.mean((predictions - actuals) ** 2)
        
        # Directional accuracy
        if len(predictions) > 1:
            pred_dirs = np.sign(np.diff(predictions))
            actual_dirs = np.sign(np.diff(actuals))
            directional_acc = np.mean(pred_dirs == actual_dirs) if len(pred_dirs) > 0 else 0.0
        else:
            directional_acc = 0.0
        
        # Get minute info from test data
        minute_ranges = test_data['minute_range'].values
        minutes = test_data['minute'].values
        
        # Create result records
        for i in range(len(predictions)):
            mr = minute_ranges[i] if i < len(minute_ranges) else f"test_{i}"
            minute = minutes[i] if i < len(minutes) else 75 + i
            results.append({
                'match_id': match_id,
                'period': 2,  # Test data is in Period 2
                'team': team,
                'is_home': is_home,
                'minute_range': mr,
                'minute_start': int(minute),
                'prediction_value': round(float(predictions[i]), 6),
                'actual_value': round(float(actuals[i]), 6),
                'mse': round(mse, 6),
                'directional_accuracy': round(directional_acc, 4),
                'arima_order': str(order),
                'n_train': len(train_momentum),
                'has_exog': True
            })
        
        return results
    
    def generate_predictions(self) -> pd.DataFrame:
        """
        Generate predictions matching original approach:
        - Train on minutes 0-74 (75 minutes: all P1 + first ~30 min of P2)
        - Predict minutes 75-90 (rest of P2)
        
        Returns:
            DataFrame with all predictions
        """
        print("\n" + "="*60)
        print("🎯 PERIOD-SEPARATED ARIMAX PREDICTOR")
        print("="*60)
        print("📋 Strategy: Train on 75 min (P1+P2), Predict min 75-90")
        
        if not ARIMA_AVAILABLE:
            print("❌ ARIMA not available!")
            return pd.DataFrame()
        
        # Load data
        df = self.load_momentum_data()
        
        all_results = []
        match_ids = df['match_id'].unique()
        
        print(f"\n📊 Processing {len(match_ids)} matches...")
        
        # Training/test split parameters (matching original)
        TRAIN_END = 75  # Train on minutes 0-74
        TEST_START = 75  # Test from minute 75
        TEST_END = 90    # Test until minute 90
        
        for i, match_id in enumerate(match_ids):
            match_data = df[df['match_id'] == match_id].copy()
            
            if self.verbose or (i + 1) % 10 == 0:
                print(f"   [{i+1}/{len(match_ids)}] Match {match_id}")
            
            # Combine periods WITHOUT duplicates
            # Use Period 1 for minutes < 45, Period 2 for minutes >= 45
            p1_data = match_data[(match_data['period'] == 1) & (match_data['minute'] < 45)]
            p2_data = match_data[(match_data['period'] == 2) & (match_data['minute'] >= 45)]
            combined = pd.concat([p1_data, p2_data]).sort_values('minute').reset_index(drop=True)
            
            # Filter by minute for train/test split
            train_data = combined[combined['minute'] < TRAIN_END].copy()
            test_data = combined[
                (combined['minute'] >= TEST_START) & 
                (combined['minute'] < TEST_END)
            ].copy()
            
            if len(train_data) < 10 or len(test_data) < 3:
                continue
            
            home_team = train_data['team_home'].iloc[0]
            away_team = train_data['team_away'].iloc[0]
            
            # Process home team
            home_results = self.process_minute_based(
                train_data, test_data, match_id, home_team, is_home=True
            )
            all_results.extend(home_results)
            
            # Process away team
            away_results = self.process_minute_based(
                train_data, test_data, match_id, away_team, is_home=False
            )
            all_results.extend(away_results)
        
        # Create DataFrame
        results_df = pd.DataFrame(all_results)
        
        if len(results_df) == 0:
            print("❌ No predictions generated!")
            return results_df
        
        # Save output
        output_file = self.output_path / "arimax_predictions_by_period.csv"
        results_df.to_csv(output_file, index=False)
        print(f"\n✅ Saved {len(results_df):,} predictions to {output_file}")
        
        # Print summary
        self.print_summary(results_df)
        
        return results_df
    
    def print_summary(self, df: pd.DataFrame):
        """Print prediction summary"""
        print("\n" + "="*60)
        print("📊 PREDICTION SUMMARY")
        print("="*60)
        
        print(f"\nTotal predictions: {len(df):,}")
        print(f"Unique matches: {df['match_id'].nunique()}")
        print(f"Period 1 predictions: {len(df[df['period'] == 1]):,}")
        print(f"Period 2 predictions: {len(df[df['period'] == 2]):,}")
        
        # Overall metrics
        avg_mse = df['mse'].mean()
        avg_dir_acc = df['directional_accuracy'].mean()
        
        print(f"\n📈 Overall Metrics:")
        print(f"   Average MSE: {avg_mse:.4f}")
        print(f"   Average Directional Accuracy: {avg_dir_acc:.2%}")
        
        # By period
        print(f"\n📈 By Period:")
        for period in [1, 2]:
            period_df = df[df['period'] == period]
            if len(period_df) > 0:
                print(f"   Period {period}: MSE={period_df['mse'].mean():.4f}, "
                      f"Dir.Acc={period_df['directional_accuracy'].mean():.2%}")
        
        # Sign accuracy (differential)
        correct_sign = (np.sign(df['prediction_value']) == np.sign(df['actual_value'])).sum()
        sign_accuracy = correct_sign / len(df) if len(df) > 0 else 0
        
        print(f"\n📈 Sign Accuracy:")
        print(f"   Overall: {sign_accuracy:.2%} ({correct_sign:,}/{len(df):,})")
        
        # Sample predictions
        print(f"\n📋 Sample predictions:")
        sample = df[['match_id', 'period', 'team', 'minute_range', 
                     'prediction_value', 'actual_value']].head(10)
        print(sample.to_string())


if __name__ == "__main__":
    predictor = PeriodARIMAXPredictor(verbose=False)
    results = predictor.generate_predictions()

