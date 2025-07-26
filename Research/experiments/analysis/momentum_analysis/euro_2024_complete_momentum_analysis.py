#!/usr/bin/env python3
"""
Euro 2024 Complete Momentum Analysis
Comprehensive analysis of momentum patterns using the complete Euro 2024 dataset
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class Euro2024MomentumAnalyzer:
    """Complete momentum analysis for Euro 2024"""
    
    def __init__(self):
        self.data = None
        self.momentum_data = None
        self.team_stats = {}
        self.match_stats = {}
        
    def load_data(self, file_path='euro_2024_complete/connected_complete.csv'):
        """Load and validate the Euro 2024 complete dataset"""
        print("📊 Loading Euro 2024 Complete Dataset...")
        
        try:
            # Load data in chunks to handle large file
            chunk_size = 10000
            chunks = []
            
            chunk_count = 0
            for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                chunks.append(chunk)
                chunk_count += 1
                if chunk_count % 10 == 0:
                    print(f"   Loaded {chunk_count * chunk_size:,} rows...")
            
            self.data = pd.concat(chunks, ignore_index=True)
            print(f"✅ Successfully loaded {len(self.data):,} events")
            
            return self.validate_data()
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def validate_data(self):
        """Validate data quality and completeness"""
        print("\n🔍 VALIDATING DATA QUALITY")
        print("=" * 50)
        
        # Basic data info
        print(f"📊 Dataset Shape: {self.data.shape}")
        print(f"📅 Columns: {len(self.data.columns)}")
        
        # Check essential columns
        essential_columns = ['match_id', 'team_name', 'minute', 'second', 'event_type', 'player_name']
        missing_columns = [col for col in essential_columns if col not in self.data.columns]
        
        if missing_columns:
            print(f"❌ Missing essential columns: {missing_columns}")
            return False
        
        print("✅ All essential columns present")
        
        # Display column info
        print(f"\n📋 Available columns ({len(self.data.columns)}):")
        for i, col in enumerate(self.data.columns, 1):
            print(f"   {i:2d}. {col}")
        
        # Check data coverage
        print(f"\n📈 DATA COVERAGE:")
        print(f"   🆔 Unique matches: {self.data['match_id'].nunique()}")
        print(f"   🏟️ Unique teams: {self.data['team_name'].nunique()}")
        print(f"   ⚽ Event types: {self.data['event_type'].nunique()}")
        print(f"   👥 Unique players: {self.data['player_name'].nunique()}")
        
        # Check for missing values
        print(f"\n🔍 MISSING VALUES:")
        missing_stats = self.data.isnull().sum()
        for col in essential_columns:
            missing_count = missing_stats[col]
            missing_pct = (missing_count / len(self.data)) * 100
            print(f"   {col}: {missing_count:,} ({missing_pct:.1f}%)")
        
        # Display unique teams
        print(f"\n🏟️ TEAMS IN DATASET:")
        teams = self.data['team_name'].dropna().unique()
        for i, team in enumerate(sorted(teams), 1):
            print(f"   {i:2d}. {team}")
        
        # Display event types
        print(f"\n⚽ EVENT TYPES:")
        event_types = self.data['event_type'].value_counts()
        for i, (event_type, count) in enumerate(event_types.head(10).items(), 1):
            print(f"   {i:2d}. {event_type}: {count:,}")
        
        return True
    
    def calculate_momentum_metrics(self):
        """Calculate comprehensive momentum metrics"""
        print("\n🔮 CALCULATING MOMENTUM METRICS")
        print("=" * 50)
        
        # Add timestamp
        self.data['timestamp_seconds'] = self.data['minute'] * 60 + self.data['second']
        
        momentum_records = []
        
        # Process each match
        matches = self.data['match_id'].unique()
        print(f"📊 Processing {len(matches)} matches...")
        
        for match_idx, match_id in enumerate(matches, 1):
            if match_idx % 5 == 0:
                print(f"   Processing match {match_idx}/{len(matches)}")
            
            match_data = self.data[self.data['match_id'] == match_id].copy()
            teams = match_data['team_name'].dropna().unique()
            
            # Calculate momentum every 30 seconds
            max_time = int(match_data['timestamp_seconds'].max())
            time_points = range(180, max_time + 1, 30)  # Start after 3 minutes
            
            for time_point in time_points:
                for team in teams:
                    momentum_score = self.calculate_momentum_at_time(match_data, time_point, team)
                    
                    momentum_records.append({
                        'match_id': match_id,
                        'team_name': team,
                        'time_seconds': time_point,
                        'minute': time_point // 60,
                        'momentum_score': momentum_score['score'],
                        'attacking_actions': momentum_score['attacking_actions'],
                        'possession_events': momentum_score['possession_events'],
                        'defensive_actions': momentum_score['defensive_actions'],
                        'total_events': momentum_score['total_events'],
                        'events_per_minute': momentum_score['events_per_minute'],
                        'possession_percentage': momentum_score['possession_percentage']
                    })
        
        self.momentum_data = pd.DataFrame(momentum_records)
        print(f"✅ Generated {len(self.momentum_data):,} momentum data points")
        
        return self.momentum_data
    
    def calculate_momentum_at_time(self, match_data, current_time, team_name):
        """Calculate momentum score at specific time"""
        # Get events from last 3 minutes (180 seconds)
        start_time = max(0, current_time - 180)
        recent_events = match_data[
            (match_data['timestamp_seconds'] >= start_time) &
            (match_data['timestamp_seconds'] <= current_time)
        ]
        
        team_events = recent_events[recent_events['team_name'] == team_name]
        total_events = len(recent_events)
        
        # Calculate features
        attacking_events = ['Shot', 'Dribble', 'Carry', 'Pass']
        defensive_events = ['Pressure', 'Tackle', 'Block', 'Interception']
        
        attacking_actions = len(team_events[team_events['event_type'].isin(attacking_events)])
        defensive_actions = len(team_events[team_events['event_type'].isin(defensive_events)])
        possession_events = len(team_events)
        
        # Calculate momentum score (0-10 scale)
        possession_pct = (possession_events / total_events * 100) if total_events > 0 else 50
        events_per_minute = possession_events / 3 if possession_events > 0 else 0
        
        momentum_score = min(10, max(0,
            attacking_actions * 1.2 +
            possession_pct * 0.04 +
            events_per_minute * 0.3 -
            defensive_actions * 0.3
        ))
        
        return {
            'score': momentum_score,
            'attacking_actions': attacking_actions,
            'possession_events': possession_events,
            'defensive_actions': defensive_actions,
            'total_events': possession_events,
            'events_per_minute': events_per_minute,
            'possession_percentage': possession_pct
        }
    
    def analyze_momentum_patterns(self):
        """Analyze momentum patterns and statistics"""
        print("\n📊 MOMENTUM PATTERN ANALYSIS")
        print("=" * 50)
        
        if self.momentum_data is None:
            print("❌ No momentum data available")
            return
        
        # 1. Average time to build momentum
        self.analyze_momentum_building_time()
        
        # 2. Average momentum per game
        self.analyze_average_momentum_per_game()
        
        # 3. Momentum change patterns
        self.analyze_momentum_changes()
        
        # 4. Team momentum profiles
        self.analyze_team_momentum_profiles()
        
        # 5. Match momentum dynamics
        self.analyze_match_momentum_dynamics()
        
        # 6. Critical momentum moments
        self.analyze_critical_momentum_moments()
    
    def analyze_momentum_building_time(self):
        """Analyze how long it takes to build momentum"""
        print("\n⏰ MOMENTUM BUILDING TIME ANALYSIS")
        print("-" * 40)
        
        # Define momentum thresholds
        low_momentum = 3
        medium_momentum = 6
        high_momentum = 8
        
        building_times = []
        
        for match_id in self.momentum_data['match_id'].unique():
            match_momentum = self.momentum_data[self.momentum_data['match_id'] == match_id]
            
            for team in match_momentum['team_name'].unique():
                team_momentum = match_momentum[match_momentum['team_name'] == team].sort_values('time_seconds')
                
                # Find momentum building sequences
                current_building = False
                build_start = None
                
                for _, row in team_momentum.iterrows():
                    if not current_building and row['momentum_score'] > medium_momentum:
                        current_building = True
                        build_start = row['time_seconds']
                    elif current_building and row['momentum_score'] >= high_momentum:
                        if build_start is not None:
                            build_time = row['time_seconds'] - build_start
                            building_times.append(build_time)
                        current_building = False
                        build_start = None
                    elif current_building and row['momentum_score'] < low_momentum:
                        current_building = False
                        build_start = None
        
        if building_times:
            avg_build_time = np.mean(building_times)
            median_build_time = np.median(building_times)
            
            print(f"📈 Average time to build high momentum: {avg_build_time:.1f} seconds ({avg_build_time/60:.1f} minutes)")
            print(f"📊 Median time to build high momentum: {median_build_time:.1f} seconds ({median_build_time/60:.1f} minutes)")
            print(f"🔄 Total momentum building sequences: {len(building_times)}")
            print(f"⚡ Fastest momentum build: {min(building_times):.1f} seconds")
            print(f"🐌 Slowest momentum build: {max(building_times):.1f} seconds")
        else:
            print("❌ No momentum building sequences found")
    
    def analyze_average_momentum_per_game(self):
        """Analyze average momentum per game"""
        print("\n⚽ AVERAGE MOMENTUM PER GAME")
        print("-" * 40)
        
        game_stats = []
        
        for match_id in self.momentum_data['match_id'].unique():
            match_momentum = self.momentum_data[self.momentum_data['match_id'] == match_id]
            
            for team in match_momentum['team_name'].unique():
                team_momentum = match_momentum[match_momentum['team_name'] == team]
                
                avg_momentum = team_momentum['momentum_score'].mean()
                max_momentum = team_momentum['momentum_score'].max()
                min_momentum = team_momentum['momentum_score'].min()
                momentum_variance = team_momentum['momentum_score'].var()
                
                game_stats.append({
                    'match_id': match_id,
                    'team': team,
                    'avg_momentum': avg_momentum,
                    'max_momentum': max_momentum,
                    'min_momentum': min_momentum,
                    'momentum_variance': momentum_variance
                })
        
        game_stats_df = pd.DataFrame(game_stats)
        
        print(f"📊 Overall average momentum: {game_stats_df['avg_momentum'].mean():.2f}")
        print(f"📈 Highest team average: {game_stats_df['avg_momentum'].max():.2f}")
        print(f"📉 Lowest team average: {game_stats_df['avg_momentum'].min():.2f}")
        print(f"📋 Standard deviation: {game_stats_df['avg_momentum'].std():.2f}")
        
        # Team rankings
        team_avg_momentum = game_stats_df.groupby('team')['avg_momentum'].mean().sort_values(ascending=False)
        print(f"\n🏆 TOP 5 TEAMS BY AVERAGE MOMENTUM:")
        for i, (team, avg_momentum) in enumerate(team_avg_momentum.head().items(), 1):
            print(f"   {i}. {team}: {avg_momentum:.2f}")
        
        print(f"\n📉 BOTTOM 5 TEAMS BY AVERAGE MOMENTUM:")
        for i, (team, avg_momentum) in enumerate(team_avg_momentum.tail().items(), 1):
            print(f"   {i}. {team}: {avg_momentum:.2f}")
    
    def analyze_momentum_changes(self):
        """Analyze momentum change patterns"""
        print("\n🔄 MOMENTUM CHANGE ANALYSIS")
        print("-" * 40)
        
        momentum_changes = []
        
        for match_id in self.momentum_data['match_id'].unique():
            match_momentum = self.momentum_data[self.momentum_data['match_id'] == match_id]
            
            for team in match_momentum['team_name'].unique():
                team_momentum = match_momentum[match_momentum['team_name'] == team].sort_values('time_seconds')
                
                # Calculate momentum changes
                team_momentum['momentum_change'] = team_momentum['momentum_score'].diff()
                
                # Store significant changes
                significant_changes = team_momentum[abs(team_momentum['momentum_change']) > 2]
                
                for _, row in significant_changes.iterrows():
                    momentum_changes.append({
                        'match_id': match_id,
                        'team': team,
                        'time_seconds': row['time_seconds'],
                        'momentum_change': row['momentum_change'],
                        'new_momentum': row['momentum_score']
                    })
        
        if momentum_changes:
            changes_df = pd.DataFrame(momentum_changes)
            
            avg_change = changes_df['momentum_change'].mean()
            avg_positive_change = changes_df[changes_df['momentum_change'] > 0]['momentum_change'].mean()
            avg_negative_change = changes_df[changes_df['momentum_change'] < 0]['momentum_change'].mean()
            
            print(f"📊 Average momentum change: {avg_change:.2f}")
            print(f"📈 Average positive change: {avg_positive_change:.2f}")
            print(f"📉 Average negative change: {avg_negative_change:.2f}")
            print(f"🔄 Total significant changes: {len(changes_df)}")
            print(f"⚡ Largest positive swing: {changes_df['momentum_change'].max():.2f}")
            print(f"💥 Largest negative swing: {changes_df['momentum_change'].min():.2f}")
            
            # Timing analysis
            changes_by_time = changes_df.groupby(changes_df['time_seconds'] // 600)['momentum_change'].count()  # 10-minute intervals
            peak_period = changes_by_time.idxmax() * 10
            
            print(f"🕐 Most momentum changes in minutes: {peak_period}-{peak_period+10}")
    
    def analyze_team_momentum_profiles(self):
        """Analyze momentum profiles for each team"""
        print("\n🏟️ TEAM MOMENTUM PROFILES")
        print("-" * 40)
        
        team_profiles = {}
        
        for team in self.momentum_data['team_name'].unique():
            team_data = self.momentum_data[self.momentum_data['team_name'] == team]
            
            profile = {
                'team': team,
                'avg_momentum': team_data['momentum_score'].mean(),
                'max_momentum': team_data['momentum_score'].max(),
                'min_momentum': team_data['momentum_score'].min(),
                'momentum_consistency': 1 / (team_data['momentum_score'].std() + 0.1),  # Higher = more consistent
                'high_momentum_percentage': (team_data['momentum_score'] >= 7).mean() * 100,
                'low_momentum_percentage': (team_data['momentum_score'] <= 3).mean() * 100,
                'attacking_focus': team_data['attacking_actions'].mean(),
                'defensive_focus': team_data['defensive_actions'].mean()
            }
            
            team_profiles[team] = profile
        
        # Display top teams in different categories
        profiles_df = pd.DataFrame(list(team_profiles.values()))
        
        print(f"🔥 HIGHEST AVERAGE MOMENTUM:")
        top_momentum = profiles_df.nlargest(3, 'avg_momentum')
        for _, row in top_momentum.iterrows():
            print(f"   {row['team']}: {row['avg_momentum']:.2f}")
        
        print(f"\n⚖️ MOST CONSISTENT MOMENTUM:")
        most_consistent = profiles_df.nlargest(3, 'momentum_consistency')
        for _, row in most_consistent.iterrows():
            print(f"   {row['team']}: {row['momentum_consistency']:.2f}")
        
        print(f"\n⚡ MOST HIGH MOMENTUM PERIODS:")
        high_momentum_teams = profiles_df.nlargest(3, 'high_momentum_percentage')
        for _, row in high_momentum_teams.iterrows():
            print(f"   {row['team']}: {row['high_momentum_percentage']:.1f}%")
        
        print(f"\n⚔️ MOST ATTACKING TEAMS:")
        attacking_teams = profiles_df.nlargest(3, 'attacking_focus')
        for _, row in attacking_teams.iterrows():
            print(f"   {row['team']}: {row['attacking_focus']:.1f} attacks/period")
    
    def analyze_match_momentum_dynamics(self):
        """Analyze momentum dynamics within matches"""
        print("\n⚖️ MATCH MOMENTUM DYNAMICS")
        print("-" * 40)
        
        match_dynamics = []
        
        for match_id in self.momentum_data['match_id'].unique():
            match_momentum = self.momentum_data[self.momentum_data['match_id'] == match_id]
            teams = match_momentum['team_name'].unique()
            
            if len(teams) == 2:
                team1_data = match_momentum[match_momentum['team_name'] == teams[0]].sort_values('time_seconds')
                team2_data = match_momentum[match_momentum['team_name'] == teams[1]].sort_values('time_seconds')
                
                # Align time points
                common_times = set(team1_data['time_seconds']).intersection(set(team2_data['time_seconds']))
                
                momentum_differences = []
                for time_point in common_times:
                    team1_momentum = team1_data[team1_data['time_seconds'] == time_point]['momentum_score'].iloc[0]
                    team2_momentum = team2_data[team2_data['time_seconds'] == time_point]['momentum_score'].iloc[0]
                    
                    momentum_differences.append(abs(team1_momentum - team2_momentum))
                
                if momentum_differences:
                    match_dynamics.append({
                        'match_id': match_id,
                        'team1': teams[0],
                        'team2': teams[1],
                        'avg_momentum_difference': np.mean(momentum_differences),
                        'max_momentum_difference': np.max(momentum_differences),
                        'momentum_swings': len([d for d in momentum_differences if d > 4])
                    })
        
        if match_dynamics:
            dynamics_df = pd.DataFrame(match_dynamics)
            
            print(f"📊 Average momentum difference between teams: {dynamics_df['avg_momentum_difference'].mean():.2f}")
            print(f"⚡ Largest momentum difference: {dynamics_df['max_momentum_difference'].max():.2f}")
            print(f"🔄 Average momentum swings per match: {dynamics_df['momentum_swings'].mean():.1f}")
            
            # Most competitive matches
            most_competitive = dynamics_df.nsmallest(3, 'avg_momentum_difference')
            print(f"\n🏆 MOST COMPETITIVE MATCHES (smallest momentum differences):")
            for _, row in most_competitive.iterrows():
                print(f"   {row['team1']} vs {row['team2']}: {row['avg_momentum_difference']:.2f}")
    
    def analyze_critical_momentum_moments(self):
        """Analyze critical momentum moments"""
        print("\n🎯 CRITICAL MOMENTUM MOMENTS")
        print("-" * 40)
        
        critical_moments = []
        
        # Find moments where momentum > 8 or < 2
        high_momentum = self.momentum_data[self.momentum_data['momentum_score'] >= 8]
        low_momentum = self.momentum_data[self.momentum_data['momentum_score'] <= 2]
        
        print(f"🔥 High momentum moments (≥8): {len(high_momentum)}")
        print(f"❄️ Low momentum moments (≤2): {len(low_momentum)}")
        
        # Analyze timing of critical moments
        if len(high_momentum) > 0:
            high_momentum_timing = high_momentum.groupby('minute')['momentum_score'].count()
            peak_high_minute = high_momentum_timing.idxmax()
            print(f"⏰ Most high momentum in minute: {peak_high_minute}")
        
        if len(low_momentum) > 0:
            low_momentum_timing = low_momentum.groupby('minute')['momentum_score'].count()
            peak_low_minute = low_momentum_timing.idxmax()
            print(f"⏰ Most low momentum in minute: {peak_low_minute}")
        
        # Find teams with most critical moments
        team_high_moments = high_momentum.groupby('team_name').size().sort_values(ascending=False)
        team_low_moments = low_momentum.groupby('team_name').size().sort_values(ascending=False)
        
        print(f"\n🔥 TEAMS WITH MOST HIGH MOMENTUM MOMENTS:")
        for team, count in team_high_moments.head(5).items():
            print(f"   {team}: {count}")
        
        print(f"\n❄️ TEAMS WITH MOST LOW MOMENTUM MOMENTS:")
        for team, count in team_low_moments.head(5).items():
            print(f"   {team}: {count}")
    
    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        print("\n" + "="*80)
        print("📋 EURO 2024 MOMENTUM ANALYSIS SUMMARY REPORT")
        print("="*80)
        
        if self.momentum_data is None:
            print("❌ No momentum data available for summary")
            return
        
        total_data_points = len(self.momentum_data)
        total_matches = self.momentum_data['match_id'].nunique()
        total_teams = self.momentum_data['team_name'].nunique()
        
        print(f"📊 DATASET OVERVIEW:")
        print(f"   🎯 Total momentum data points: {total_data_points:,}")
        print(f"   ⚽ Total matches analyzed: {total_matches}")
        print(f"   🏟️ Total teams analyzed: {total_teams}")
        
        avg_momentum = self.momentum_data['momentum_score'].mean()
        momentum_std = self.momentum_data['momentum_score'].std()
        
        print(f"\n📈 OVERALL MOMENTUM STATISTICS:")
        print(f"   📊 Average momentum across all games: {avg_momentum:.2f}")
        print(f"   📏 Standard deviation: {momentum_std:.2f}")
        print(f"   🔥 Maximum momentum recorded: {self.momentum_data['momentum_score'].max():.2f}")
        print(f"   ❄️ Minimum momentum recorded: {self.momentum_data['momentum_score'].min():.2f}")
        
        # Time distribution
        time_distribution = self.momentum_data.groupby('minute')['momentum_score'].mean()
        peak_minute = time_distribution.idxmax()
        lowest_minute = time_distribution.idxmin()
        
        print(f"\n⏰ TEMPORAL PATTERNS:")
        print(f"   🔝 Peak momentum minute: {peak_minute} ({time_distribution[peak_minute]:.2f})")
        print(f"   📉 Lowest momentum minute: {lowest_minute} ({time_distribution[lowest_minute]:.2f})")
        
        print(f"\n✅ ANALYSIS COMPLETE - Full momentum profile generated!")

def main():
    """Main analysis function"""
    print("🏆 EURO 2024 COMPLETE MOMENTUM ANALYSIS")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = Euro2024MomentumAnalyzer()
    
    # Load and validate data
    if not analyzer.load_data():
        print("❌ Failed to load data. Analysis cannot proceed.")
        return
    
    # Calculate momentum metrics
    if analyzer.calculate_momentum_metrics() is not None:
        # Perform comprehensive analysis
        analyzer.analyze_momentum_patterns()
        
        # Generate summary report
        analyzer.generate_summary_report()
        
        print("\n🎯 MOMENTUM ANALYSIS COMPLETE!")
        print("📊 All momentum metrics calculated and analyzed successfully!")
    else:
        print("❌ Failed to calculate momentum metrics")

if __name__ == "__main__":
    main() 