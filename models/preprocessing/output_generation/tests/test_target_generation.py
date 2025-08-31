"""
Unit Tests for Target Generation

Tests the momentum change target calculation functionality.

Author: AI Assistant
Date: August 2024
"""

import unittest
import pandas as pd
import numpy as np
import tempfile
import os
from pathlib import Path
import sys

# Add scripts directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / 'scripts'))

from target_generator import MomentumTargetGenerator

class TestTargetGeneration(unittest.TestCase):
    """Test cases for momentum target generation."""
    
    def setUp(self):
        """Set up test data and temporary files."""
        # Create sample input data
        self.sample_data = pd.DataFrame({
            'match_id': [1, 1, 1, 1, 1, 2, 2, 2],
            'minute_range': ['0-2', '1-3', '2-4', '3-5', '4-6', '0-2', '1-3', '2-4'],
            'team_home': ['TeamA', 'TeamA', 'TeamA', 'TeamA', 'TeamA', 'TeamB', 'TeamB', 'TeamB'],
            'team_away': ['TeamX', 'TeamX', 'TeamX', 'TeamX', 'TeamX', 'TeamY', 'TeamY', 'TeamY'],
            'team_home_momentum': [5.0, 6.0, 7.0, 8.0, 9.0, 4.0, 5.0, 6.0],
            'team_away_momentum': [3.0, 4.0, 5.0, 6.0, 7.0, 2.0, 3.0, 4.0],
        })
        
        # Create temporary files
        self.temp_input = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.temp_output = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        
        # Save sample data
        self.sample_data.to_csv(self.temp_input.name, index=False)
        
        # Close files so they can be read
        self.temp_input.close()
        self.temp_output.close()
    
    def tearDown(self):
        """Clean up temporary files."""
        os.unlink(self.temp_input.name)
        if os.path.exists(self.temp_output.name):
            os.unlink(self.temp_output.name)
    
    def test_initialization(self):
        """Test generator initialization."""
        generator = MomentumTargetGenerator(
            input_file=self.temp_input.name,
            output_file=self.temp_output.name
        )
        
        self.assertEqual(generator.input_file, self.temp_input.name)
        self.assertEqual(generator.output_file, self.temp_output.name)
        self.assertEqual(generator.lag_minutes, 3)
    
    def test_load_input_data(self):
        """Test input data loading."""
        generator = MomentumTargetGenerator(
            input_file=self.temp_input.name,
            output_file=self.temp_output.name
        )
        
        df = generator.load_input_data()
        
        # Check data loaded correctly
        self.assertEqual(len(df), 8)
        self.assertIn('start_minute', df.columns)
        self.assertIn('end_minute', df.columns)
        
        # Check minute parsing
        self.assertEqual(df.iloc[0]['start_minute'], 0)
        self.assertEqual(df.iloc[0]['end_minute'], 2)
        self.assertEqual(df.iloc[1]['start_minute'], 1)
        self.assertEqual(df.iloc[1]['end_minute'], 3)
    
    def test_find_future_windows(self):
        """Test future window matching."""
        generator = MomentumTargetGenerator(
            input_file=self.temp_input.name,
            output_file=self.temp_output.name
        )
        
        df = generator.load_input_data()
        df = generator.find_future_windows(df)
        
        # Check future window columns added
        self.assertIn('has_future_window', df.columns)
        self.assertIn('future_home_momentum', df.columns)
        self.assertIn('future_away_momentum', df.columns)
        
        # Check specific cases
        # Window 0-2 should have future window 3-5
        first_row = df.iloc[0]
        self.assertEqual(first_row['future_window_start'], 3)
        self.assertEqual(first_row['future_window_end'], 5)
        self.assertTrue(first_row['has_future_window'])
        self.assertEqual(first_row['future_home_momentum'], 8.0)  # From 3-5 window
        
        # Last window should not have future
        last_row = df.iloc[-1]  # 2-4 window for match 2
        self.assertFalse(last_row['has_future_window'])
    
    def test_calculate_momentum_targets(self):
        """Test momentum change calculation."""
        generator = MomentumTargetGenerator(
            input_file=self.temp_input.name,
            output_file=self.temp_output.name
        )
        
        df = generator.load_input_data()
        df = generator.find_future_windows(df)
        df = generator.calculate_momentum_targets(df)
        
        # Check target columns added
        self.assertIn('team_home_momentum_change', df.columns)
        self.assertIn('team_away_momentum_change', df.columns)
        
        # Check specific calculation
        # Window 0-2: home=5.0, future window 3-5: home=8.0
        # Expected change: 8.0 - 5.0 = 3.0
        first_row = df.iloc[0]
        if first_row['has_future_window']:
            expected_home_change = 8.0 - 5.0  # 3.0
            expected_away_change = 6.0 - 3.0  # 3.0
            
            self.assertAlmostEqual(first_row['team_home_momentum_change'], expected_home_change, places=3)
            self.assertAlmostEqual(first_row['team_away_momentum_change'], expected_away_change, places=3)
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Test with missing columns
        bad_data = pd.DataFrame({'wrong_column': [1, 2, 3]})
        bad_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        bad_data.to_csv(bad_file.name, index=False)
        bad_file.close()
        
        generator = MomentumTargetGenerator(
            input_file=bad_file.name,
            output_file=self.temp_output.name
        )
        
        with self.assertRaises(ValueError):
            generator.load_input_data()
        
        os.unlink(bad_file.name)
    
    def test_validation_results(self):
        """Test validation functionality."""
        generator = MomentumTargetGenerator(
            input_file=self.temp_input.name,
            output_file=self.temp_output.name
        )
        
        df = generator.load_input_data()
        df = generator.find_future_windows(df)
        df = generator.calculate_momentum_targets(df)
        
        validation_results = generator.validate_targets(df)
        
        # Check validation structure
        self.assertIn('total_windows', validation_results)
        self.assertIn('windows_with_targets', validation_results)
        self.assertIn('target_coverage', validation_results)
        self.assertIn('home_target_stats', validation_results)
        self.assertIn('away_target_stats', validation_results)
        
        # Check basic counts
        self.assertEqual(validation_results['total_windows'], 8)
        self.assertGreater(validation_results['windows_with_targets'], 0)
        self.assertGreater(validation_results['target_coverage'], 0)
    
    def test_full_pipeline(self):
        """Test the complete generation pipeline."""
        generator = MomentumTargetGenerator(
            input_file=self.temp_input.name,
            output_file=self.temp_output.name
        )
        
        # Run full pipeline
        df, validation = generator.generate_targets()
        
        # Check output file was created
        self.assertTrue(os.path.exists(self.temp_output.name))
        
        # Load and check output file
        output_df = pd.read_csv(self.temp_output.name)
        
        # Check structure
        self.assertEqual(len(output_df), 8)
        self.assertIn('team_home_momentum_change', output_df.columns)
        self.assertIn('team_away_momentum_change', output_df.columns)
        self.assertIn('has_future_window', output_df.columns)
        
        # Check that some windows have targets
        windows_with_targets = len(output_df[output_df['has_future_window'] == True])
        self.assertGreater(windows_with_targets, 0)
        
        # Check validation results
        self.assertIn('total_windows', validation)
        self.assertIn('windows_with_targets', validation)
        self.assertEqual(validation['total_windows'], 8)

class TestSpecificScenarios(unittest.TestCase):
    """Test specific momentum calculation scenarios."""
    
    def test_momentum_increase_scenario(self):
        """Test scenario where momentum increases."""
        data = pd.DataFrame({
            'match_id': [1, 1],
            'minute_range': ['0-2', '3-5'],
            'team_home': ['TeamA', 'TeamA'],
            'team_away': ['TeamB', 'TeamB'],
            'team_home_momentum': [5.0, 8.0],  # Increases by 3.0
            'team_away_momentum': [3.0, 2.0],  # Decreases by 1.0
        })
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        data.to_csv(temp_file.name, index=False)
        temp_file.close()
        
        temp_output = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        temp_output.close()
        
        generator = MomentumTargetGenerator(temp_file.name, temp_output.name)
        df, _ = generator.generate_targets()
        
        # Check the target calculation
        first_window = df.iloc[0]
        self.assertTrue(first_window['has_future_window'])
        self.assertAlmostEqual(first_window['team_home_momentum_change'], 3.0, places=3)
        self.assertAlmostEqual(first_window['team_away_momentum_change'], -1.0, places=3)
        
        # Cleanup
        os.unlink(temp_file.name)
        os.unlink(temp_output.name)
    
    def test_no_future_window_scenario(self):
        """Test scenario where no future window exists."""
        data = pd.DataFrame({
            'match_id': [1],
            'minute_range': ['85-87'],  # Near end of match
            'team_home': ['TeamA'],
            'team_away': ['TeamB'],
            'team_home_momentum': [6.0],
            'team_away_momentum': [4.0],
        })
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        data.to_csv(temp_file.name, index=False)
        temp_file.close()
        
        temp_output = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        temp_output.close()
        
        generator = MomentumTargetGenerator(temp_file.name, temp_output.name)
        df, validation = generator.generate_targets()
        
        # Check that no future window was found
        first_window = df.iloc[0]
        self.assertFalse(first_window['has_future_window'])
        self.assertTrue(pd.isna(first_window['team_home_momentum_change']))
        self.assertTrue(pd.isna(first_window['team_away_momentum_change']))
        
        # Check validation reflects this
        self.assertEqual(validation['windows_with_targets'], 0)
        self.assertEqual(validation['target_coverage'], 0.0)
        
        # Cleanup
        os.unlink(temp_file.name)
        os.unlink(temp_output.name)

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
