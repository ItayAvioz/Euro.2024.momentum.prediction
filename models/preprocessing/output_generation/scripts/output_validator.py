"""
Output Validator - Target Variable Quality Assurance

Validates the generated momentum change targets for quality and completeness.

Author: AI Assistant  
Date: August 2024
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
from typing import Dict, List, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

class TargetValidator:
    """
    Validates momentum change target variables for quality assurance.
    """
    
    def __init__(self, target_file: str = None):
        """
        Initialize the validator.
        
        Args:
            target_file: Path to the target variables CSV file
        """
        # Set up logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        if target_file is None:
            target_file = "../momentum_targets_enhanced.csv"
            
        self.target_file = target_file
        self.logger.info(f"Target Validator initialized for: {target_file}")
    
    def load_data(self) -> pd.DataFrame:
        """Load the target dataset."""
        self.logger.info("Loading target dataset...")
        
        try:
            df = pd.read_csv(self.target_file)
            self.logger.info(f"Loaded {len(df)} windows from {df['match_id'].nunique()} matches")
            return df
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            raise
    
    def validate_data_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate the basic data structure."""
        self.logger.info("Validating data structure...")
        
        results = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'unique_matches': df['match_id'].nunique(),
            'required_columns_present': True,
            'missing_columns': [],
            'data_types_correct': True,
            'type_issues': []
        }
        
        # Check required columns
        required_columns = [
            'match_id', 'minute_range', 'team_home_momentum', 'team_away_momentum',
            'team_home_momentum_change', 'team_away_momentum_change', 
            'has_future_window', 'future_window_minutes'
        ]
        
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            results['required_columns_present'] = False
            results['missing_columns'] = missing
            self.logger.error(f"Missing required columns: {missing}")
        
        # Check data types
        expected_types = {
            'match_id': ['int64', 'int32'],
            'team_home_momentum': ['float64'],
            'team_away_momentum': ['float64'],
            'team_home_momentum_change': ['float64'],
            'team_away_momentum_change': ['float64'],
            'has_future_window': ['bool', 'boolean']
        }
        
        for col, expected in expected_types.items():
            if col in df.columns:
                actual_type = str(df[col].dtype)
                if actual_type not in expected:
                    results['data_types_correct'] = False
                    results['type_issues'].append(f"{col}: expected {expected}, got {actual_type}")
        
        if results['data_types_correct']:
            self.logger.info("✅ Data structure validation passed")
        else:
            self.logger.warning(f"⚠️ Data type issues: {results['type_issues']}")
        
        return results
    
    def validate_target_coverage(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate target variable coverage."""
        self.logger.info("Validating target coverage...")
        
        total_windows = len(df)
        windows_with_targets = len(df[df['has_future_window'] == True])
        coverage_percentage = (windows_with_targets / total_windows) * 100
        
        results = {
            'total_windows': total_windows,
            'windows_with_targets': windows_with_targets,
            'windows_without_targets': total_windows - windows_with_targets,
            'coverage_percentage': coverage_percentage,
            'adequate_coverage': coverage_percentage >= 70.0,
            'coverage_by_match': {}
        }
        
        # Check coverage by match
        for match_id in df['match_id'].unique():
            match_data = df[df['match_id'] == match_id]
            match_total = len(match_data)
            match_with_targets = len(match_data[match_data['has_future_window'] == True])
            match_coverage = (match_with_targets / match_total) * 100 if match_total > 0 else 0
            
            results['coverage_by_match'][match_id] = {
                'total': match_total,
                'with_targets': match_with_targets,
                'coverage': match_coverage
            }
        
        # Log results
        self.logger.info(f"Target Coverage Analysis:")
        self.logger.info(f"  Overall Coverage: {coverage_percentage:.1f}%")
        self.logger.info(f"  Windows with targets: {windows_with_targets}")
        self.logger.info(f"  Windows without targets: {total_windows - windows_with_targets}")
        
        if results['adequate_coverage']:
            self.logger.info("✅ Target coverage is adequate")
        else:
            self.logger.warning(f"⚠️ Low target coverage: {coverage_percentage:.1f}% (minimum 70%)")
        
        return results
    
    def validate_target_distributions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate target variable distributions."""
        self.logger.info("Validating target distributions...")
        
        valid_df = df[df['has_future_window'] == True]
        
        if len(valid_df) == 0:
            self.logger.error("No valid targets to analyze")
            return {'error': 'No valid targets available'}
        
        results = {
            'home_target_stats': valid_df['team_home_momentum_change'].describe().to_dict(),
            'away_target_stats': valid_df['team_away_momentum_change'].describe().to_dict(),
            'home_null_count': valid_df['team_home_momentum_change'].isnull().sum(),
            'away_null_count': valid_df['team_away_momentum_change'].isnull().sum(),
            'extreme_outliers': {},
            'distribution_issues': []
        }
        
        # Check for outliers (beyond 3 standard deviations)
        for team_type in ['home', 'away']:
            col = f'team_{team_type}_momentum_change'
            values = valid_df[col].dropna()
            
            if len(values) > 0:
                mean_val = values.mean()
                std_val = values.std()
                
                outliers = values[np.abs(values - mean_val) > 3 * std_val]
                results['extreme_outliers'][team_type] = {
                    'count': len(outliers),
                    'percentage': (len(outliers) / len(values)) * 100,
                    'values': outliers.tolist() if len(outliers) <= 10 else outliers.head(10).tolist()
                }
                
                # Check for distribution issues
                if std_val == 0:
                    results['distribution_issues'].append(f"{team_type} targets have zero variance")
                elif len(outliers) / len(values) > 0.05:  # More than 5% outliers
                    results['distribution_issues'].append(f"{team_type} targets have {len(outliers)/len(values)*100:.1f}% extreme outliers")
        
        # Log results
        self.logger.info("Target Distribution Analysis:")
        self.logger.info(f"  Home targets - Mean: {results['home_target_stats']['mean']:.3f}, Std: {results['home_target_stats']['std']:.3f}")
        self.logger.info(f"  Away targets - Mean: {results['away_target_stats']['mean']:.3f}, Std: {results['away_target_stats']['std']:.3f}")
        
        if results['distribution_issues']:
            for issue in results['distribution_issues']:
                self.logger.warning(f"⚠️ {issue}")
        else:
            self.logger.info("✅ Target distributions look healthy")
        
        return results
    
    def validate_temporal_consistency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate temporal consistency of targets."""
        self.logger.info("Validating temporal consistency...")
        
        results = {
            'temporal_gaps': [],
            'match_continuity_issues': [],
            'time_ordering_correct': True,
            'future_window_logic_correct': True
        }
        
        # Check each match separately
        for match_id in df['match_id'].unique():
            match_data = df[df['match_id'] == match_id].copy()
            match_data = match_data.sort_values('start_minute')
            
            # Check time ordering
            start_minutes = match_data['start_minute'].tolist()
            if start_minutes != sorted(start_minutes):
                results['time_ordering_correct'] = False
                results['match_continuity_issues'].append(f"Match {match_id}: Time ordering issues")
            
            # Check future window logic
            for idx, row in match_data.iterrows():
                if row['has_future_window']:
                    expected_future_start = row['start_minute'] + 3
                    expected_future_end = row['end_minute'] + 3
                    expected_future_range = f"{expected_future_start}-{expected_future_end}"
                    
                    if row['future_window_minutes'] != expected_future_range:
                        results['future_window_logic_correct'] = False
                        results['match_continuity_issues'].append(
                            f"Match {match_id}: Future window logic error at minute {row['start_minute']}"
                        )
        
        # Log results
        if results['time_ordering_correct'] and results['future_window_logic_correct']:
            self.logger.info("✅ Temporal consistency validation passed")
        else:
            self.logger.warning("⚠️ Temporal consistency issues found")
            for issue in results['match_continuity_issues']:
                self.logger.warning(f"  {issue}")
        
        return results
    
    def generate_validation_report(self, all_results: Dict[str, Any]) -> str:
        """Generate a comprehensive validation report."""
        self.logger.info("Generating validation report...")
        
        report = []
        report.append("# Target Variables Validation Report")
        report.append("=" * 50)
        report.append("")
        
        # Data Structure
        struct = all_results['structure']
        report.append("## Data Structure")
        report.append(f"- Total Windows: {struct['total_rows']:,}")
        report.append(f"- Total Columns: {struct['total_columns']}")
        report.append(f"- Unique Matches: {struct['unique_matches']}")
        report.append(f"- Required Columns Present: {'✅' if struct['required_columns_present'] else '❌'}")
        if struct['missing_columns']:
            report.append(f"- Missing Columns: {struct['missing_columns']}")
        report.append("")
        
        # Coverage
        coverage = all_results['coverage']
        report.append("## Target Coverage")
        report.append(f"- Windows with Targets: {coverage['windows_with_targets']:,}")
        report.append(f"- Coverage Percentage: {coverage['coverage_percentage']:.1f}%")
        report.append(f"- Adequate Coverage: {'✅' if coverage['adequate_coverage'] else '❌'}")
        report.append("")
        
        # Distributions
        if 'distributions' in all_results and 'error' not in all_results['distributions']:
            dist = all_results['distributions']
            report.append("## Target Distributions")
            report.append("### Home Team Momentum Change")
            report.append(f"- Mean: {dist['home_target_stats']['mean']:.3f}")
            report.append(f"- Std: {dist['home_target_stats']['std']:.3f}")
            report.append(f"- Range: [{dist['home_target_stats']['min']:.3f}, {dist['home_target_stats']['max']:.3f}]")
            report.append("")
            report.append("### Away Team Momentum Change")
            report.append(f"- Mean: {dist['away_target_stats']['mean']:.3f}")
            report.append(f"- Std: {dist['away_target_stats']['std']:.3f}")
            report.append(f"- Range: [{dist['away_target_stats']['min']:.3f}, {dist['away_target_stats']['max']:.3f}]")
            report.append("")
        
        # Temporal Consistency
        temporal = all_results['temporal']
        report.append("## Temporal Consistency")
        report.append(f"- Time Ordering Correct: {'✅' if temporal['time_ordering_correct'] else '❌'}")
        report.append(f"- Future Window Logic Correct: {'✅' if temporal['future_window_logic_correct'] else '❌'}")
        if temporal['match_continuity_issues']:
            report.append("- Issues Found:")
            for issue in temporal['match_continuity_issues']:
                report.append(f"  - {issue}")
        report.append("")
        
        # Overall Status
        all_good = (
            struct['required_columns_present'] and
            coverage['adequate_coverage'] and
            temporal['time_ordering_correct'] and
            temporal['future_window_logic_correct']
        )
        
        report.append("## Overall Status")
        if all_good:
            report.append("✅ **ALL VALIDATIONS PASSED** - Data is ready for modeling!")
        else:
            report.append("⚠️ **ISSUES FOUND** - Please review and fix before modeling")
        
        report_text = "\n".join(report)
        
        # Save report to file
        report_file = Path(self.target_file).parent / "validation_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        self.logger.info(f"Validation report saved to: {report_file}")
        
        return report_text
    
    def validate_all(self) -> Dict[str, Any]:
        """Run all validation checks."""
        self.logger.info("🔍 Starting comprehensive target validation...")
        
        try:
            # Load data
            df = self.load_data()
            
            # Run all validations
            results = {
                'structure': self.validate_data_structure(df),
                'coverage': self.validate_target_coverage(df),
                'distributions': self.validate_target_distributions(df),
                'temporal': self.validate_temporal_consistency(df)
            }
            
            # Generate report
            report = self.generate_validation_report(results)
            
            self.logger.info("🎉 Validation completed successfully!")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Validation failed: {e}")
            raise

def main():
    """Main execution function."""
    print("🔍 Target Variables Validator")
    print("=" * 50)
    
    # Initialize validator
    validator = TargetValidator()
    
    # Run validation
    results = validator.validate_all()
    
    # Display summary
    print("\n📊 Validation Summary:")
    print(f"Total Windows: {results['structure']['total_rows']:,}")
    print(f"Target Coverage: {results['coverage']['coverage_percentage']:.1f}%")
    print(f"Structure Valid: {'✅' if results['structure']['required_columns_present'] else '❌'}")
    print(f"Coverage Adequate: {'✅' if results['coverage']['adequate_coverage'] else '❌'}")
    print(f"Temporal Consistent: {'✅' if results['temporal']['time_ordering_correct'] else '❌'}")
    
    print("\n✅ Validation completed! Check validation_report.md for details.")

if __name__ == "__main__":
    main()
