"""
Momentum Data Loader
====================
Loads momentum and prediction data from models/period_separated_momentum/outputs/

Data Sources:
- momentum_by_period.csv: Actual momentum values per minute
- arimax_predictions_by_period.csv: Predicted momentum changes (75+ min)

Author: Euro 2024 Momentum Project
Date: December 2024
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, List, Tuple


class MomentumDataLoader:
    """
    Load and query momentum data for commentary generation.
    
    Provides:
    - Per-minute momentum values for both teams
    - Momentum change (last 3 minutes)
    - Historical data for streak analysis
    - ARIMAX predictions for minutes 75+
    """
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        
        # Paths to momentum data
        self.base_path = Path(__file__).parent.parent.parent.parent.parent / "models" / "period_separated_momentum" / "outputs"
        self.momentum_file = self.base_path / "momentum_by_period.csv"
        self.predictions_file = self.base_path / "arimax_predictions_by_period.csv"
        
        # Data storage
        self.momentum_df = None
        self.predictions_df = None
        
        # Load data
        self._load_data()
    
    def _load_data(self):
        """Load both CSV files."""
        if self.momentum_file.exists():
            self.momentum_df = pd.read_csv(self.momentum_file)
            if self.verbose:
                print(f"[OK] Loaded momentum data: {len(self.momentum_df)} rows")
        else:
            raise FileNotFoundError(f"Momentum file not found: {self.momentum_file}")
        
        if self.predictions_file.exists():
            self.predictions_df = pd.read_csv(self.predictions_file)
            if self.verbose:
                print(f"[OK] Loaded predictions data: {len(self.predictions_df)} rows")
        else:
            if self.verbose:
                print(f"[WARN] Predictions file not found: {self.predictions_file}")
    
    def get_momentum_for_minute(
        self, 
        match_id: int, 
        minute: int, 
        period: int
    ) -> Optional[Dict]:
        """
        Get momentum data for a specific minute.
        
        Args:
            match_id: Match identifier
            minute: Game minute
            period: Game period (1, 2, 3, 4)
        
        Returns:
            {
                'home_team': str,
                'away_team': str,
                'home_momentum': float,
                'away_momentum': float,
                'home_change': float,        # Change in LAST 3 min
                'away_change': float,        # Change in LAST 3 min
                'momentum_diff': float,      # home - away
                'dominant_team': str,        # Team with higher momentum
                'events_count': int
            }
        """
        if self.momentum_df is None:
            return None
        
        # Filter by match, period, minute
        row = self.momentum_df[
            (self.momentum_df['match_id'] == match_id) &
            (self.momentum_df['period'] == period) &
            (self.momentum_df['minute'] == minute)
        ]
        
        if row.empty:
            return None
        
        row = row.iloc[0]
        
        home_mom = float(row['team_home_momentum']) if pd.notna(row['team_home_momentum']) else 0.0
        away_mom = float(row['team_away_momentum']) if pd.notna(row['team_away_momentum']) else 0.0
        home_change = float(row['team_home_momentum_change']) if pd.notna(row['team_home_momentum_change']) else 0.0
        away_change = float(row['team_away_momentum_change']) if pd.notna(row['team_away_momentum_change']) else 0.0
        
        diff = home_mom - away_mom
        
        # Determine dominant team (threshold 0.5)
        if abs(diff) < 0.5:
            dominant = "Even"
        elif diff > 0:
            dominant = row['team_home']
        else:
            dominant = row['team_away']
        
        return {
            'home_team': row['team_home'],
            'away_team': row['team_away'],
            'home_momentum': home_mom,
            'away_momentum': away_mom,
            'home_change': home_change,
            'away_change': away_change,
            'momentum_diff': diff,
            'dominant_team': dominant,
            'events_count': int(row['events_in_window']) if pd.notna(row['events_in_window']) else 0
        }
    
    def get_momentum_history(
        self,
        match_id: int,
        current_minute: int,
        period: int,
        lookback: int = 5
    ) -> List[Dict]:
        """
        Get momentum history for streak analysis.
        
        Args:
            match_id: Match identifier
            current_minute: Current game minute
            period: Game period
            lookback: How many previous minutes to look back
        
        Returns:
            List of momentum data for last N minutes (oldest first)
        """
        if self.momentum_df is None:
            return []
        
        # Get range of minutes
        start_minute = max(0, current_minute - lookback)
        
        history = []
        for minute in range(start_minute, current_minute + 1):
            data = self.get_momentum_for_minute(match_id, minute, period)
            if data:
                data['minute'] = minute
                history.append(data)
        
        return history
    
    def get_predictions_for_minute(
        self,
        match_id: int,
        minute: int
    ) -> Optional[Dict]:
        """
        Get ARIMAX predictions for minute 75+.
        
        Args:
            match_id: Match identifier
            minute: Game minute (must be >= 75)
        
        Returns:
            {
                'home_team': str,
                'away_team': str,
                'home_predicted_change': float,   # NEXT 3 min prediction
                'away_predicted_change': float,
                'home_accuracy': float,           # Model confidence
                'away_accuracy': float,
                'expected_dominant': str          # Who's expected to improve more
            }
        """
        if self.predictions_df is None or minute < 75:
            return None
        
        # Get predictions for both teams
        match_preds = self.predictions_df[
            (self.predictions_df['match_id'] == match_id) &
            (self.predictions_df['minute_start'] == minute)
        ]
        
        if match_preds.empty:
            return None
        
        home_pred = match_preds[match_preds['is_home'] == True]
        away_pred = match_preds[match_preds['is_home'] == False]
        
        if home_pred.empty or away_pred.empty:
            return None
        
        home_row = home_pred.iloc[0]
        away_row = away_pred.iloc[0]
        
        home_change = float(home_row['prediction_value']) if pd.notna(home_row['prediction_value']) else 0.0
        away_change = float(away_row['prediction_value']) if pd.notna(away_row['prediction_value']) else 0.0
        
        # Who's expected to improve more?
        if home_change > away_change + 0.3:
            expected = home_row['team']
        elif away_change > home_change + 0.3:
            expected = away_row['team']
        else:
            expected = "Neither/Both"
        
        return {
            'home_team': home_row['team'],
            'away_team': away_row['team'],
            'home_predicted_change': home_change,
            'away_predicted_change': away_change,
            'home_accuracy': float(home_row['directional_accuracy']) if pd.notna(home_row['directional_accuracy']) else 0.0,
            'away_accuracy': float(away_row['directional_accuracy']) if pd.notna(away_row['directional_accuracy']) else 0.0,
            'expected_dominant': expected
        }
    
    def get_all_predictions_from_minute(
        self,
        match_id: int,
        start_minute: int,
        max_minute: int = 90
    ) -> List[Dict]:
        """
        Get ALL remaining ARIMAX predictions from a given minute to end of half.
        
        At minute 76, the agent can see predictions for 76, 77, 78, ..., up to ~90.
        This gives the agent the FULL prediction window to analyze trends.
        
        Args:
            match_id: Match identifier
            start_minute: Starting minute (must be >= 75)
            max_minute: Maximum minute to include (default 90)
        
        Returns:
            List of prediction dicts for each minute, sorted by minute
        """
        if self.predictions_df is None or start_minute < 75:
            return []
        
        predictions = []
        
        for minute in range(start_minute, max_minute + 1):
            pred = self.get_predictions_for_minute(match_id, minute)
            if pred:
                pred['minute'] = minute
                predictions.append(pred)
        
        return predictions
    
    def get_full_context(
        self,
        match_id: int,
        minute: int,
        period: int,
        include_history: bool = True,
        lookback: int = 5,
        include_full_prediction_window: bool = True
    ) -> Dict:
        """
        Get complete momentum context: actual + history + predictions (if 75+).
        
        DATA TIMING EXPLANATION:
        ========================
        Momentum Value at minute X:
          - Calculated from events in 3-minute window: (X-1, X-2, X-3)
          - Example: Momentum(65) = events from minutes 64, 63, 62
          - Example: Momentum(72) = events from minutes 71, 70, 69
        
        Momentum Change at minute X (IMPORTANT - change is 3 minutes behind!):
          - At minute X, the AVAILABLE change is for minute (X-3)
          - Formula: Change(X-3) = Momentum(X) - Momentum(X-3)
          - Example at minute 65: Change(62) = Momentum(65) - Momentum(62)
            = events(64,63,62) - events(61,60,59)
          - Example at minute 75: Change(72) = Momentum(75) - Momentum(72)
            = events(74,73,72) - events(71,70,69)
        
        Predictions (minute 76 onwards):
          - ARIMAX predicts momentum CHANGE for the NEXT 3 minutes
          - At minute 76: we have predictions for 76, 77, 78, ..., to end of half (~87)
          - The agent sees the FULL remaining prediction window!
        
        Why predictions start at minute 76 (not 75)?
          - At minute 75: last actual change is Change(72)
          - First prediction available is for minute 76
        
        Args:
            match_id: Match identifier
            minute: Current game minute
            period: Game period
            include_history: Whether to include historical data for streaks
            lookback: How many minutes to look back for history
            include_full_prediction_window: Whether to include ALL predictions to end of half
        
        Returns:
            Complete momentum context dictionary
        """
        result = {
            'has_momentum': False,
            'has_prediction': False,
            'has_prediction_window': False,
            'has_history': False,
            'minute': minute,
            'period': period,
            'match_id': match_id
        }
        
        # Get actual momentum
        momentum = self.get_momentum_for_minute(match_id, minute, period)
        if momentum:
            result['has_momentum'] = True
            result.update(momentum)
        
        # Get historical data for streak analysis
        if include_history:
            history = self.get_momentum_history(match_id, minute, period, lookback)
            if len(history) > 1:
                result['has_history'] = True
                result['history'] = history
        
        # Get predictions (only for minute 76+)
        # At minute 75, we have actual momentum change, predictions start at 76
        if minute >= 76:
            # Current minute prediction
            predictions = self.get_predictions_for_minute(match_id, minute)
            if predictions:
                result['has_prediction'] = True
                result['predictions'] = predictions
            
            # FULL prediction window from current minute to end of half
            if include_full_prediction_window:
                # For second half, max is ~87 (can't predict beyond 87 as momentum uses 3 min window)
                max_prediction_minute = 87 if period == 2 else 117  # 117 for extra time
                all_predictions = self.get_all_predictions_from_minute(
                    match_id, minute, max_prediction_minute
                )
                if all_predictions:
                    result['has_prediction_window'] = True
                    result['prediction_window'] = all_predictions
        
        return result
    
    def get_match_max_differential(
        self,
        match_id: int,
        up_to_minute: int = None,
        period: int = None
    ) -> Dict:
        """
        Get the maximum momentum differential in the match so far.
        
        Returns:
            {
                'max_diff': float,
                'max_diff_minute': int,
                'max_diff_team': str,  # Team that had the advantage
                'current_vs_max': str  # 'at_peak', 'near_peak', 'below_peak'
            }
        """
        if self.momentum_df is None:
            return {}
        
        # Filter match data
        match_data = self.momentum_df[self.momentum_df['match_id'] == match_id].copy()
        
        if period:
            match_data = match_data[match_data['period'] == period]
        
        if up_to_minute:
            match_data = match_data[match_data['minute'] <= up_to_minute]
        
        if match_data.empty:
            return {}
        
        # Calculate absolute differential
        match_data['abs_diff'] = abs(match_data['team_home_momentum'] - match_data['team_away_momentum'])
        
        # Find max
        max_idx = match_data['abs_diff'].idxmax()
        max_row = match_data.loc[max_idx]
        
        home_mom = max_row['team_home_momentum']
        away_mom = max_row['team_away_momentum']
        max_diff = home_mom - away_mom
        
        # Determine which team had advantage
        if max_diff > 0:
            max_team = max_row['team_home']
        else:
            max_team = max_row['team_away']
        
        # Compare current to max
        current_diff = None
        if up_to_minute:
            current = self.get_momentum_for_minute(match_id, up_to_minute, period or 2)
            if current:
                current_diff = abs(current['momentum_diff'])
        
        current_vs_max = 'unknown'
        if current_diff is not None:
            if abs(current_diff - abs(max_diff)) < 0.3:
                current_vs_max = 'at_peak'
            elif current_diff > abs(max_diff) * 0.7:
                current_vs_max = 'near_peak'
            else:
                current_vs_max = 'below_peak'
        
        return {
            'max_diff': abs(max_diff),
            'max_diff_minute': int(max_row['minute']),
            'max_diff_team': max_team,
            'current_vs_max': current_vs_max
        }
    
    def get_match_running_totals(
        self,
        match_id: int,
        up_to_minute: int,
        period: int
    ) -> Dict:
        """
        Calculate running totals for a match up to the given minute.
        
        V6.2: These totals are for comparing against research thresholds.
        
        Returns:
            {
                'home_team': str,
                'away_team': str,
                'home_total_momentum': float,    # Sum of |momentum| from min 0 to current
                'away_total_momentum': float,
                'home_num_sequences': int,       # Count of positive change sequences
                'away_num_sequences': int,
                'home_longest_sequence': int,    # Longest consecutive positive changes
                'away_longest_sequence': int,
                'home_positive_changes': int,    # Count up to (minute - 3) inclusive
                'away_positive_changes': int,
                'home_predicted_positive': int,  # Sum of predicted positive changes (min 76+)
                'away_predicted_positive': int,
            }
        """
        if self.momentum_df is None:
            return {}
        
        # Get all match data up to current minute (period 1 and 2 only)
        match_data = self.momentum_df[
            (self.momentum_df['match_id'] == match_id) &
            (self.momentum_df['period'].isin([1, 2])) &
            (self.momentum_df['minute'] <= up_to_minute)
        ].sort_values(['period', 'minute'])
        
        if match_data.empty:
            return {}
        
        home_team = match_data.iloc[0]['team_home']
        away_team = match_data.iloc[0]['team_away']
        
        # 1. Total absolute momentum (sum of all momentum values)
        home_total = match_data['team_home_momentum'].abs().sum()
        away_total = match_data['team_away_momentum'].abs().sum()
        
        # 2 & 3. Sequences and longest sequence (from positive changes)
        home_changes = match_data['team_home_momentum_change'].dropna().tolist()
        away_changes = match_data['team_away_momentum_change'].dropna().tolist()
        
        home_seq, home_longest = self._count_positive_sequences(home_changes)
        away_seq, away_longest = self._count_positive_sequences(away_changes)
        
        # 4. Positive changes count (up to minute - 3 because change is 3 min behind)
        change_cutoff_minute = up_to_minute - 3
        change_data = match_data[match_data['minute'] <= change_cutoff_minute]
        
        home_pos_changes = (change_data['team_home_momentum_change'] > 0).sum()
        away_pos_changes = (change_data['team_away_momentum_change'] > 0).sum()
        
        # 5. Predicted positive changes (only for minute 76+ in period 2)
        home_pred_pos = 0
        away_pred_pos = 0
        
        if period == 2 and up_to_minute >= 76 and self.predictions_df is not None:
            # Get ALL predictions from minute 76 to end (calculated once at min 76)
            all_preds = self.get_all_predictions_from_minute(match_id, 76, 90)
            for pred in all_preds:
                if pred.get('home_predicted_change', 0) > 0:
                    home_pred_pos += 1
                if pred.get('away_predicted_change', 0) > 0:
                    away_pred_pos += 1
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'home_total_momentum': round(home_total, 1),
            'away_total_momentum': round(away_total, 1),
            'home_num_sequences': home_seq,
            'away_num_sequences': away_seq,
            'home_longest_sequence': home_longest,
            'away_longest_sequence': away_longest,
            'home_positive_changes': int(home_pos_changes),
            'away_positive_changes': int(away_pos_changes),
            'home_predicted_positive': home_pred_pos,
            'away_predicted_positive': away_pred_pos,
        }
    
    def _count_positive_sequences(self, changes: List[float]) -> Tuple[int, int]:
        """
        Count positive sequences and find longest one.
        
        Returns:
            (num_sequences, longest_sequence)
        """
        if not changes:
            return (0, 0)
        
        num_sequences = 0
        longest = 0
        current_streak = 0
        in_positive = False
        
        for change in changes:
            if change > 0:
                if not in_positive:
                    # Start new sequence
                    num_sequences += 1
                    in_positive = True
                    current_streak = 1
                else:
                    current_streak += 1
                longest = max(longest, current_streak)
            else:
                in_positive = False
                current_streak = 0
        
        return (num_sequences, longest)


# Test if run directly
if __name__ == "__main__":
    print("=" * 60)
    print("Testing Momentum Data Loader")
    print("=" * 60)
    
    loader = MomentumDataLoader(verbose=True)
    
    # Test with Germany vs Scotland (match_id: 3930158)
    test_match = 3930158
    test_minute = 25
    test_period = 1
    
    print(f"\n[TEST] Testing match {test_match}, minute {test_minute}, period {test_period}")
    
    # Get single minute
    momentum = loader.get_momentum_for_minute(test_match, test_minute, test_period)
    if momentum:
        print(f"\n[OK] Momentum data:")
        print(f"   {momentum['home_team']}: {momentum['home_momentum']:.2f} (change: {momentum['home_change']:+.2f})")
        print(f"   {momentum['away_team']}: {momentum['away_momentum']:.2f} (change: {momentum['away_change']:+.2f})")
        print(f"   Dominant: {momentum['dominant_team']} (diff: {momentum['momentum_diff']:+.2f})")
    
    # Get full context
    print(f"\n[TEST] Full context with history:")
    context = loader.get_full_context(test_match, test_minute, test_period)
    print(f"   Has momentum: {context['has_momentum']}")
    print(f"   Has history: {context['has_history']}")
    if context.get('history'):
        print(f"   History length: {len(context['history'])} minutes")
    
    # Test predictions (minute 75+)
    print(f"\n[TEST] Testing predictions for minute 80:")
    pred = loader.get_predictions_for_minute(test_match, 80)
    if pred:
        print(f"   {pred['home_team']} predicted change: {pred['home_predicted_change']:+.2f}")
        print(f"   {pred['away_team']} predicted change: {pred['away_predicted_change']:+.2f}")
        print(f"   Expected dominant: {pred['expected_dominant']}")
    
    # Test max differential
    print(f"\n[TEST] Max differential in match:")
    max_diff = loader.get_match_max_differential(test_match, up_to_minute=45, period=1)
    if max_diff:
        print(f"   Max diff: {max_diff['max_diff']:.2f} at minute {max_diff['max_diff_minute']}")
        print(f"   Team with advantage: {max_diff['max_diff_team']}")
    
    print("\n[OK] Tests completed!")

