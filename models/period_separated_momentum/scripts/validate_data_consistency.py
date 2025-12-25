#!/usr/bin/env python3
"""
Data Consistency Validator
==========================

Validates that the period-separated momentum data is consistent with
the original data for non-overlapping minutes (0-44).

Key validations:
1. For minutes 0-44 (no period overlap), values should be similar
2. Check that period separation is correct
3. Verify data completeness

Author: Euro 2024 Momentum Prediction Project
Date: December 2024
"""

import pandas as pd
import numpy as np
from pathlib import Path


class DataConsistencyValidator:
    """Validate period-separated data against original"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent.parent
        
        # File paths
        self.original_path = self.base_path / "preprocessing" / "data" / "targets" / "momentum_targets_streamlined.csv"
        self.new_path = self.base_path / "period_separated_momentum" / "outputs" / "momentum_by_period.csv"
        self.output_path = self.base_path / "period_separated_momentum" / "outputs"
        
    def load_data(self):
        """Load both datasets"""
        print("📂 Loading datasets...")
        
        self.original_df = pd.read_csv(self.original_path)
        self.new_df = pd.read_csv(self.new_path)
        
        # Extract minute from minute_range
        self.original_df['minute'] = self.original_df['minute_range'].apply(lambda x: int(x.split('-')[0]))
        
        print(f"   Original: {len(self.original_df):,} records")
        print(f"   New (period-separated): {len(self.new_df):,} records")
        
    def validate_non_overlapping_minutes(self) -> dict:
        """
        Compare data for non-overlapping minutes (0-44).
        
        These should be identical because period 1 events at minute 0-44
        don't overlap with period 2.
        """
        print("\n" + "="*60)
        print("🔍 VALIDATION 1: Non-overlapping minutes (0-44)")
        print("="*60)
        
        results = {
            'matches_compared': 0,
            'records_compared': 0,
            'exact_matches': 0,
            'close_matches': 0,  # Within 0.1 tolerance
            'mismatches': 0,
            'mismatch_details': []
        }
        
        # Filter to minutes 0-44 (no overlap)
        original_filtered = self.original_df[self.original_df['minute'] <= 44].copy()
        new_filtered = self.new_df[(self.new_df['minute'] <= 44) & (self.new_df['period'] == 1)].copy()
        
        print(f"\nOriginal records (minute 0-44): {len(original_filtered):,}")
        print(f"New records (period 1, minute 0-44): {len(new_filtered):,}")
        
        # Compare by match_id and minute_range
        for match_id in original_filtered['match_id'].unique():
            orig_match = original_filtered[original_filtered['match_id'] == match_id]
            new_match = new_filtered[new_filtered['match_id'] == match_id]
            
            results['matches_compared'] += 1
            
            for _, orig_row in orig_match.iterrows():
                minute_range = orig_row['minute_range']
                new_row = new_match[new_match['minute_range'] == minute_range]
                
                if len(new_row) == 0:
                    continue
                    
                new_row = new_row.iloc[0]
                results['records_compared'] += 1
                
                # Compare home momentum
                orig_home = orig_row['team_home_momentum']
                new_home = new_row['team_home_momentum']
                
                orig_away = orig_row['team_away_momentum']
                new_away = new_row['team_away_momentum']
                
                home_diff = abs(orig_home - new_home)
                away_diff = abs(orig_away - new_away)
                
                if home_diff < 0.001 and away_diff < 0.001:
                    results['exact_matches'] += 1
                elif home_diff < 0.1 and away_diff < 0.1:
                    results['close_matches'] += 1
                else:
                    results['mismatches'] += 1
                    results['mismatch_details'].append({
                        'match_id': match_id,
                        'minute_range': minute_range,
                        'orig_home': orig_home,
                        'new_home': new_home,
                        'home_diff': home_diff,
                        'orig_away': orig_away,
                        'new_away': new_away,
                        'away_diff': away_diff
                    })
        
        # Print results
        print(f"\n📊 Results:")
        print(f"   Matches compared: {results['matches_compared']}")
        print(f"   Records compared: {results['records_compared']}")
        print(f"   Exact matches: {results['exact_matches']} ({100*results['exact_matches']/max(1,results['records_compared']):.1f}%)")
        print(f"   Close matches (±0.1): {results['close_matches']} ({100*results['close_matches']/max(1,results['records_compared']):.1f}%)")
        print(f"   Mismatches: {results['mismatches']} ({100*results['mismatches']/max(1,results['records_compared']):.1f}%)")
        
        if results['mismatches'] > 0 and len(results['mismatch_details']) <= 10:
            print(f"\n⚠️ Sample mismatches:")
            for m in results['mismatch_details'][:5]:
                print(f"   Match {m['match_id']}, {m['minute_range']}: "
                      f"home diff={m['home_diff']:.3f}, away diff={m['away_diff']:.3f}")
        
        return results
    
    def validate_period_separation(self) -> dict:
        """
        Validate that period separation is correct.
        """
        print("\n" + "="*60)
        print("🔍 VALIDATION 2: Period Separation")
        print("="*60)
        
        results = {
            'period_1_count': len(self.new_df[self.new_df['period'] == 1]),
            'period_2_count': len(self.new_df[self.new_df['period'] == 2]),
            'period_1_min_minute': self.new_df[self.new_df['period'] == 1]['minute'].min(),
            'period_1_max_minute': self.new_df[self.new_df['period'] == 1]['minute'].max(),
            'period_2_min_minute': self.new_df[self.new_df['period'] == 2]['minute'].min(),
            'period_2_max_minute': self.new_df[self.new_df['period'] == 2]['minute'].max(),
        }
        
        print(f"\n📊 Period 1 (First Half):")
        print(f"   Records: {results['period_1_count']:,}")
        print(f"   Minute range: {results['period_1_min_minute']} - {results['period_1_max_minute']}")
        
        print(f"\n📊 Period 2 (Second Half):")
        print(f"   Records: {results['period_2_count']:,}")
        print(f"   Minute range: {results['period_2_min_minute']} - {results['period_2_max_minute']}")
        
        # Check for overlapping minutes between periods
        period_1_minutes = set(self.new_df[self.new_df['period'] == 1]['minute'].unique())
        period_2_minutes = set(self.new_df[self.new_df['period'] == 2]['minute'].unique())
        overlap = period_1_minutes.intersection(period_2_minutes)
        
        print(f"\n📊 Minute Overlap Analysis:")
        print(f"   Period 1 unique minutes: {len(period_1_minutes)}")
        print(f"   Period 2 unique minutes: {len(period_2_minutes)}")
        print(f"   Overlapping minutes: {len(overlap)}")
        if overlap:
            print(f"   Overlap range: {min(overlap)} - {max(overlap)}")
        
        results['overlapping_minutes'] = len(overlap)
        results['overlap_range'] = (min(overlap), max(overlap)) if overlap else None
        
        return results
    
    def validate_data_completeness(self) -> dict:
        """
        Validate that all matches and expected windows are present.
        """
        print("\n" + "="*60)
        print("🔍 VALIDATION 3: Data Completeness")
        print("="*60)
        
        results = {
            'original_matches': self.original_df['match_id'].nunique(),
            'new_matches': self.new_df['match_id'].nunique(),
            'missing_matches': [],
            'extra_matches': []
        }
        
        orig_matches = set(self.original_df['match_id'].unique())
        new_matches = set(self.new_df['match_id'].unique())
        
        results['missing_matches'] = list(orig_matches - new_matches)
        results['extra_matches'] = list(new_matches - orig_matches)
        
        print(f"\n📊 Match Completeness:")
        print(f"   Original matches: {results['original_matches']}")
        print(f"   New matches: {results['new_matches']}")
        print(f"   Missing: {len(results['missing_matches'])}")
        print(f"   Extra: {len(results['extra_matches'])}")
        
        # Average records per match
        orig_avg = len(self.original_df) / results['original_matches']
        new_avg = len(self.new_df) / results['new_matches']
        
        print(f"\n📊 Records per Match:")
        print(f"   Original avg: {orig_avg:.1f}")
        print(f"   New avg: {new_avg:.1f}")
        
        return results
    
    def generate_report(self) -> pd.DataFrame:
        """Generate validation report"""
        print("\n" + "="*60)
        print("📋 GENERATING VALIDATION REPORT")
        print("="*60)
        
        # Run all validations
        self.load_data()
        
        v1 = self.validate_non_overlapping_minutes()
        v2 = self.validate_period_separation()
        v3 = self.validate_data_completeness()
        
        # Create summary report
        report = {
            'Validation': [
                'Non-overlapping minutes (0-44)',
                'Non-overlapping minutes (0-44)',
                'Non-overlapping minutes (0-44)',
                'Period Separation',
                'Period Separation',
                'Period Separation',
                'Data Completeness',
                'Data Completeness'
            ],
            'Metric': [
                'Records Compared',
                'Match Rate (%)',
                'Mismatch Count',
                'Period 1 Records',
                'Period 2 Records',
                'Overlapping Minutes',
                'Original Matches',
                'New Matches'
            ],
            'Value': [
                v1['records_compared'],
                f"{100*(v1['exact_matches']+v1['close_matches'])/max(1,v1['records_compared']):.1f}%",
                v1['mismatches'],
                v2['period_1_count'],
                v2['period_2_count'],
                v2['overlapping_minutes'],
                v3['original_matches'],
                v3['new_matches']
            ]
        }
        
        report_df = pd.DataFrame(report)
        
        # Save report
        report_path = self.output_path / "validation_report.csv"
        report_df.to_csv(report_path, index=False)
        print(f"\n✅ Report saved to {report_path}")
        
        # Print summary
        print("\n" + "="*60)
        print("✅ VALIDATION SUMMARY")
        print("="*60)
        
        match_rate = 100*(v1['exact_matches']+v1['close_matches'])/max(1,v1['records_compared'])
        
        if match_rate >= 95:
            print(f"🟢 Data consistency: EXCELLENT ({match_rate:.1f}% match)")
        elif match_rate >= 80:
            print(f"🟡 Data consistency: GOOD ({match_rate:.1f}% match)")
        else:
            print(f"🔴 Data consistency: NEEDS REVIEW ({match_rate:.1f}% match)")
        
        if v2['overlapping_minutes'] > 0:
            print(f"🟢 Period separation: WORKING (overlap at minutes {v2['overlap_range'][0]}-{v2['overlap_range'][1]})")
        else:
            print(f"⚠️ Period separation: No overlap detected (unusual)")
        
        if v3['new_matches'] == v3['original_matches']:
            print(f"🟢 Data completeness: COMPLETE ({v3['new_matches']} matches)")
        else:
            print(f"🟡 Data completeness: {v3['new_matches']}/{v3['original_matches']} matches")
        
        return report_df


if __name__ == "__main__":
    validator = DataConsistencyValidator()
    report = validator.generate_report()

