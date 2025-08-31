"""
Test suite for window generation functionality.

Tests window boundary validation, momentum calculation accuracy,
edge case handling, and performance benchmarks.

Author: Euro 2024 Momentum Analysis Team
Date: February 2024
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path

# Add scripts to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from window_generator import WindowGenerator
from momentum_pipeline import MomentumPipeline

class TestWindowGeneration(unittest.TestCase):
    """Test cases for window generation functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before running tests."""
        # Create sample test data
        cls.create_sample_data()
        
    @classmethod
    def create_sample_data(cls):
        """Create sample Euro 2024 data for testing."""
        # Sample events for testing
        sample_events = []
        
        # Match 1: 90-minute match
        for minute in range(0, 90):
            # Add a few events per minute
            for i in range(2):
                sample_events.append({
                    'match_id': 12345,
                    'minute': minute + (i * 0.5),
                    'team': "{'id': 944, 'name': 'Team A'}",
                    'possession_team': "{'id': 944, 'name': 'Team A'}",
                    'type': "{'id': 1, 'name': 'Pass'}",
                    'location': '[50.0, 40.0]'
                })
                
                sample_events.append({
                    'match_id': 12345,
                    'minute': minute + (i * 0.5),
                    'team': "{'id': 945, 'name': 'Team B'}",
                    'possession_team': "{'id': 945, 'name': 'Team B'}",
                    'type': "{'id': 1, 'name': 'Pass'}",
                    'location': '[30.0, 60.0]'
                })
        
        # Match 2: 120-minute match (with extra time)
        for minute in range(0, 120):
            sample_events.append({
                'match_id': 67890,
                'minute': minute,
                'team': "{'id': 946, 'name': 'Team C'}",
                'possession_team': "{'id': 946, 'name': 'Team C'}",
                'type': "{'id': 1, 'name': 'Pass'}",
                'location': '[40.0, 50.0]'
            })
        
        # Save to temporary CSV
        cls.sample_df = pd.DataFrame(sample_events)
        cls.temp_file = Path(__file__).parent / 'test_data.csv'
        cls.sample_df.to_csv(cls.temp_file, index=False)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test fixtures after running tests."""
        # Remove temporary file
        if cls.temp_file.exists():
            cls.temp_file.unlink()
    
    def setUp(self):
        """Set up each test."""
        self.generator = WindowGenerator(data_path=str(self.temp_file))
        self.generator.load_data()
    
    def test_data_loading(self):
        """Test data loading functionality."""
        self.assertIsNotNone(self.generator.data)
        self.assertGreater(len(self.generator.data), 0)
        
        # Check required columns exist
        required_columns = ['match_id', 'minute', 'team', 'type']
        for col in required_columns:
            self.assertIn(col, self.generator.data.columns)
    
    def test_match_list_extraction(self):
        """Test extraction of unique match IDs."""
        match_list = self.generator.get_match_list()
        self.assertEqual(len(match_list), 2)  # Two test matches
        self.assertIn(12345, match_list)
        self.assertIn(67890, match_list)
    
    def test_match_duration_calculation(self):
        """Test calculation of match duration."""
        duration_1 = self.generator.get_match_duration(12345)
        duration_2 = self.generator.get_match_duration(67890)
        
        self.assertGreaterEqual(duration_1, 89)  # At least 89 minutes
        self.assertGreaterEqual(duration_2, 119)  # At least 119 minutes
    
    def test_window_list_generation(self):
        """Test generation of 3-minute window lists."""
        windows_1 = self.generator.generate_window_list(12345)
        windows_2 = self.generator.generate_window_list(67890)
        
        # Check window format
        self.assertIsInstance(windows_1, list)
        self.assertGreater(len(windows_1), 0)
        
        # Check first few windows
        expected_starts = [0, 1, 2, 3, 4]
        actual_starts = [w[0] for w in windows_1[:5]]
        self.assertEqual(actual_starts, expected_starts)
        
        # Check window size
        for start, end in windows_1:
            self.assertEqual(end - start, 2)  # 3-minute window (0-2 inclusive)
    
    def test_window_event_extraction(self):
        """Test extraction of events for specific windows."""
        # Test window 0-2 for match 12345
        window_events = self.generator.extract_window_events(12345, 0, 2)
        
        self.assertIsInstance(window_events, pd.DataFrame)
        self.assertGreater(len(window_events), 0)
        
        # Check all events are within window
        self.assertTrue(all(window_events['minute'] >= 0))
        self.assertTrue(all(window_events['minute'] <= 2))
    
    def test_team_name_extraction(self):
        """Test extraction of team names from match data."""
        home_team, away_team = self.generator.get_team_names(12345)
        
        self.assertIsNotNone(home_team)
        self.assertIsNotNone(away_team)
        self.assertNotEqual(home_team, away_team)
        self.assertIn('Team', home_team)  # Should contain 'Team A' or 'Team B'
    
    def test_momentum_calculation(self):
        """Test momentum calculation for a window."""
        result = self.generator.calculate_window_momentum(12345, 0, 2)
        
        # Check result structure
        required_keys = [
            'match_id', 'minute_window', 'team_home', 'team_away',
            'team_home_momentum', 'team_away_momentum', 'total_events',
            'home_events', 'away_events'
        ]
        
        for key in required_keys:
            self.assertIn(key, result)
        
        # Check data types and ranges
        self.assertEqual(result['match_id'], 12345)
        self.assertEqual(result['minute_window'], 0)
        self.assertIsInstance(result['team_home_momentum'], (int, float))
        self.assertIsInstance(result['team_away_momentum'], (int, float))
        self.assertGreaterEqual(result['team_home_momentum'], 0)
        self.assertGreaterEqual(result['team_away_momentum'], 0)
        self.assertGreaterEqual(result['total_events'], 0)
    
    def test_single_match_processing(self):
        """Test processing of a single match."""
        results = self.generator.process_single_match(12345)
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        # Check first result
        first_result = results[0]
        self.assertEqual(first_result['match_id'], 12345)
        self.assertEqual(first_result['minute_window'], 0)
    
    def test_empty_window_handling(self):
        """Test handling of windows with no events."""
        # Create data with gaps
        gap_data = pd.DataFrame([
            {
                'match_id': 99999,
                'minute': 0,
                'team': "{'id': 944, 'name': 'Team A'}",
                'type': "{'id': 1, 'name': 'Pass'}",
                'location': '[50.0, 40.0]'
            },
            {
                'match_id': 99999,
                'minute': 10,  # 10-minute gap
                'team': "{'id': 945, 'name': 'Team B'}",
                'type': "{'id': 1, 'name': 'Pass'}",
                'location': '[30.0, 60.0]'
            }
        ])
        
        temp_gap_file = Path(__file__).parent / 'test_gap_data.csv'
        gap_data.to_csv(temp_gap_file, index=False)
        
        try:
            gap_generator = WindowGenerator(data_path=str(temp_gap_file))
            gap_generator.load_data()
            
            # Test window with no events (minutes 3-5)
            result = gap_generator.calculate_window_momentum(99999, 3, 5)
            
            self.assertEqual(result['total_events'], 0)
            self.assertEqual(result['team_home_momentum'], 0.0)
            self.assertEqual(result['team_away_momentum'], 0.0)
            
        finally:
            if temp_gap_file.exists():
                temp_gap_file.unlink()
    
    def test_summary_statistics(self):
        """Test generation of summary statistics."""
        # Process a match first
        self.generator.process_single_match(12345)
        
        stats = self.generator.get_summary_statistics()
        
        # Check statistics structure
        expected_keys = [
            'total_windows', 'total_matches', 'avg_windows_per_match',
            'avg_home_momentum', 'avg_away_momentum', 'max_home_momentum',
            'max_away_momentum', 'total_events_processed', 'avg_events_per_window'
        ]
        
        for key in expected_keys:
            self.assertIn(key, stats)
            self.assertIsInstance(stats[key], (int, float))


class TestMomentumPipeline(unittest.TestCase):
    """Test cases for momentum pipeline functionality."""
    
    def setUp(self):
        """Set up each test."""
        # Use the same test data as WindowGenerator tests
        TestWindowGeneration.create_sample_data()
        temp_file = Path(__file__).parent / 'test_data.csv'
        
        self.pipeline = MomentumPipeline(data_path=str(temp_file))
    
    def tearDown(self):
        """Clean up after each test."""
        temp_file = Path(__file__).parent / 'test_data.csv'
        if temp_file.exists():
            temp_file.unlink()
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        self.assertIsNotNone(self.pipeline.config)
        self.assertIn('window_settings', self.pipeline.config)
        self.assertIn('momentum_settings', self.pipeline.config)
    
    def test_component_initialization(self):
        """Test initialization of pipeline components."""
        self.pipeline.initialize_components()
        
        self.assertIsNotNone(self.pipeline.window_generator)
        self.assertIsNotNone(self.pipeline.window_generator.data)
    
    def test_data_validation(self):
        """Test data validation functionality."""
        self.pipeline.initialize_components()
        
        is_valid = self.pipeline.validate_data()
        self.assertTrue(is_valid)
    
    def test_quality_report_generation(self):
        """Test quality report generation."""
        self.pipeline.initialize_components()
        
        # Generate some results first
        results = self.pipeline.generate_momentum_windows()
        self.assertIsNotNone(results)
        self.assertGreater(len(results), 0)
        
        # Generate quality report
        report = self.pipeline.generate_quality_report()
        
        self.assertIn('data_quality', report)
        self.assertIn('momentum_statistics', report)
        self.assertIn('event_statistics', report)


class TestPerformance(unittest.TestCase):
    """Performance and benchmark tests."""
    
    def test_window_generation_performance(self):
        """Test performance of window generation."""
        import time
        
        # Create larger test dataset
        large_data = []
        for match_id in range(10):  # 10 matches
            for minute in range(90):  # 90 minutes each
                for i in range(5):  # 5 events per minute
                    large_data.append({
                        'match_id': match_id,
                        'minute': minute,
                        'team': f"{{'id': {match_id*2}, 'name': 'Team A'}}",
                        'type': "{'id': 1, 'name': 'Pass'}",
                        'location': '[50.0, 40.0]'
                    })
        
        large_df = pd.DataFrame(large_data)
        temp_large_file = Path(__file__).parent / 'test_large_data.csv'
        large_df.to_csv(temp_large_file, index=False)
        
        try:
            start_time = time.time()
            
            generator = WindowGenerator(data_path=str(temp_large_file))
            results = generator.process_all_matches()
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Performance assertions
            self.assertLess(processing_time, 60)  # Should complete within 60 seconds
            self.assertGreater(len(results), 0)
            
            # Calculate performance metrics
            events_per_second = len(large_data) / processing_time
            windows_per_second = len(results) / processing_time
            
            print(f"Performance metrics:")
            print(f"  Processing time: {processing_time:.2f} seconds")
            print(f"  Events per second: {events_per_second:.0f}")
            print(f"  Windows per second: {windows_per_second:.0f}")
            
        finally:
            if temp_large_file.exists():
                temp_large_file.unlink()


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
