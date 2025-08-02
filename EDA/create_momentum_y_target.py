#!/usr/bin/env python3
"""
Create Y Momentum Target Feature - Euro 2024
Generate momentum scores for all data rows using current momentum function
Based on Research/experiments/models/feature_engineering/momentum_weight_functions.py
"""

import pandas as pd
import numpy as np
import ast
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class MomentumYTargetCreator:
    """Create Y momentum target for all Euro 2024 events"""
    
    def __init__(self):
        """Initialize momentum calculation system"""
        print("🎯 CREATING Y MOMENTUM TARGET - EURO 2024")
        print("=" * 60)
        
        # Load momentum weight system (current baseline)
        self.load_momentum_weights()
        
        # Load data
        self.load_euro_2024_data()
        
    def load_momentum_weights(self):
        """Load current momentum weight system as baseline"""
        print("\n⚖️ LOADING CURRENT MOMENTUM WEIGHT SYSTEM")
        print("-" * 50)
        
        # Current momentum component weights
        self.component_weights = {
            'goal_threat_level': {
                'weight': 0.40,
                'description': 'Direct scoring opportunities',
            },
            'attacking_momentum': {
                'weight': 0.25,
                'description': 'Attacking intent and frequency',
            },
            'recent_attacking': {
                'weight': 0.20,
                'description': 'Attacking actions in last 60 seconds',
            },
            'performance_index': {
                'weight': 0.15,
                'description': 'Combined execution × attacking',
            },
            'pressure_resistance': {
                'weight': 0.10,
                'description': 'Actions maintained under pressure',
            },
            'tempo_control': {
                'weight': 0.08,
                'description': 'Ball progression vs possession',
            },
            'under_pressure': {
                'weight': -0.05,
                'description': 'Opponent pressure (negative)',
            },
            'possession_dominance': {
                'weight': 0.015,
                'description': 'Possession advantage over 50/50',
            },
            'execution_quality': {
                'weight': 2.0,
                'description': 'Success rate multiplier',
            }
        }
        
        # Time period modifiers
        self.time_modifiers = {
            'early_game': {'range': (0, 15), 'modifier': 0.85},
            'first_phase': {'range': (15, 30), 'modifier': 1.0},
            'late_first_half': {'range': (30, 45), 'modifier': 1.1},
            'second_half_start': {'range': (45, 60), 'modifier': 1.05},
            'crucial_phase': {'range': (60, 75), 'modifier': 1.15},
            'final_push': {'range': (75, 90), 'modifier': 1.25},
            'injury_time': {'range': (90, 120), 'modifier': 1.35}
        }
        
        # Situational modifiers  
        self.situation_modifiers = {
            'score_differential': {
                'losing_by_2_plus': 1.25,
                'losing_by_1': 1.15,
                'tied_game': 1.0,
                'winning_by_1': 0.95,
                'winning_by_2_plus': 0.85
            },
            'competition_stage': {
                'group_stage': 0.9,
                'knockout_stage': 1.1,
                'final': 1.2
            }
        }
        
        print(f"   ✅ Loaded {len(self.component_weights)} momentum components")
        print(f"   ✅ Loaded {len(self.time_modifiers)} time period modifiers")
        print(f"   ✅ Loaded situational modifiers for score and stage")
        
    def load_euro_2024_data(self):
        """Load Euro 2024 complete dataset"""
        print(f"\n📊 LOADING EURO 2024 COMPLETE DATASET")
        print("-" * 50)
        
        try:
            # Load main dataset
            self.events_df = pd.read_csv('../Data/events_complete.csv', low_memory=False)
            print(f"   ✅ Events loaded: {len(self.events_df):,} rows")
            
            # Load matches for context
            try:
                self.matches_df = pd.read_csv('../Data/matches_complete.csv', low_memory=False)
                print(f"   ✅ Matches loaded: {len(self.matches_df):,} rows")
            except:
                print(f"   ⚠️ Matches file not found, using event data only")
                self.matches_df = None
            
            # Extract key fields
            print(f"\n🔧 EXTRACTING KEY FIELDS...")
            self.extract_key_fields()
            
        except Exception as e:
            print(f"   ❌ Error loading data: {e}")
            raise
    
    def extract_key_fields(self):
        """Extract and parse key fields from raw data"""
        
        # Safe parsing function for JSON-like strings
        def safe_parse(value, field_name='name'):
            """Safely parse JSON-like string values"""
            if pd.isna(value) or value == '':
                return None
            try:
                if isinstance(value, str):
                    parsed = ast.literal_eval(value)
                    if isinstance(parsed, dict) and field_name in parsed:
                        return parsed[field_name]
                    elif isinstance(parsed, dict) and 'name' in parsed:
                        return parsed['name']
                    else:
                        return str(parsed)
                return str(value) if pd.notna(value) else None
            except:
                return str(value) if pd.notna(value) else None
        
        # Extract event type
        if 'type' in self.events_df.columns:
            self.events_df['event_type'] = self.events_df['type'].apply(safe_parse)
        else:
            self.events_df['event_type'] = 'Unknown'
        
        # Extract team information
        if 'team' in self.events_df.columns:
            self.events_df['team_name'] = self.events_df['team'].apply(safe_parse)
        else:
            self.events_df['team_name'] = self.events_df.get('team_name', 'Unknown')
        
        # Extract possession team
        if 'possession_team' in self.events_df.columns:
            self.events_df['possession_team_name'] = self.events_df['possession_team'].apply(safe_parse)
        else:
            self.events_df['possession_team_name'] = self.events_df['team_name']
        
        # Create match identifiers
        if 'match_id' not in self.events_df.columns:
            self.events_df['match_id'] = pd.factorize(
                self.events_df['home_team'].astype(str) + '_vs_' + 
                self.events_df['away_team'].astype(str)
            )[0]
        
        # Ensure minute is numeric
        self.events_df['minute'] = pd.to_numeric(self.events_df['minute'], errors='coerce').fillna(0)
        
        print(f"   ✅ Event types: {self.events_df['event_type'].nunique()} unique")
        print(f"   ✅ Teams: {self.events_df['team_name'].nunique()} unique")
        print(f"   ✅ Matches: {self.events_df['match_id'].nunique()} unique")
        
    def calculate_momentum_features(self, events_window, team_name, minute):
        """Calculate momentum features for a specific time window"""
        
        # Filter events for the team
        team_events = events_window[events_window['team_name'] == team_name]
        total_events = len(team_events)
        
        if total_events == 0:
            return self.get_zero_features()
        
        # === GOAL THREAT LEVEL ===
        shots = len(team_events[team_events['event_type'].str.contains('Shot', na=False, case=False)])
        goals = len(team_events[team_events['event_type'].str.contains('Goal', na=False, case=False)])
        
        # Calculate goal threat (simplified)
        goal_threat_level = min(10, shots * 1.5 + goals * 3.0)
        
        # === ATTACKING MOMENTUM ===
        attacking_events = ['Shot', 'Pass', 'Carry', 'Dribble']
        attacking_count = 0
        for event in attacking_events:
            attacking_count += len(team_events[team_events['event_type'].str.contains(event, na=False, case=False)])
        attacking_momentum = min(10, attacking_count * 0.3)
        
        # === RECENT ATTACKING (simplified as window is already recent) ===
        recent_attacking = attacking_momentum * 0.8  # Simplified correlation
        
        # === PERFORMANCE INDEX ===
        pass_events = team_events[team_events['event_type'].str.contains('Pass', na=False, case=False)]
        pass_success_rate = 0.85  # Default good rate (could be calculated from outcomes)
        performance_index = min(10, attacking_momentum * pass_success_rate)
        
        # === PRESSURE RESISTANCE ===
        if 'under_pressure' in team_events.columns:
            pressure_events = team_events[team_events['under_pressure'].notna()]
        else:
            pressure_events = []
        pressure_resistance = min(10, max(1, (total_events - len(pressure_events)) / max(1, total_events) * 10))
        
        # === TEMPO CONTROL ===
        carry_events = len(team_events[team_events['event_type'].str.contains('Carry', na=False, case=False)])
        tempo_control = min(10, carry_events * 0.8 + attacking_momentum * 0.2)
        
        # === UNDER PRESSURE ===
        under_pressure = len(pressure_events) / max(1, total_events) * 10
        
        # === POSSESSION DOMINANCE ===
        possession_events = events_window[events_window['possession_team_name'] == team_name]
        possession_rate = len(possession_events) / max(1, len(events_window)) * 100
        possession_dominance = max(-50, min(50, possession_rate - 50))
        
        # === EXECUTION QUALITY ===
        execution_quality = min(1.0, pass_success_rate * 1.1)  # Normalized multiplier
        
        return {
            'goal_threat_level': goal_threat_level,
            'attacking_momentum': attacking_momentum,
            'recent_attacking': recent_attacking,
            'performance_index': performance_index,
            'pressure_resistance': pressure_resistance,
            'tempo_control': tempo_control,
            'under_pressure': under_pressure,
            'possession_dominance': possession_dominance,
            'execution_quality': execution_quality
        }
    
    def get_zero_features(self):
        """Return zero/default features when no events available"""
        return {
            'goal_threat_level': 0.0,
            'attacking_momentum': 0.0,
            'recent_attacking': 0.0,
            'performance_index': 0.0,
            'pressure_resistance': 5.0,  # Neutral value
            'tempo_control': 0.0,
            'under_pressure': 0.0,
            'possession_dominance': 0.0,
            'execution_quality': 0.8  # Default good execution
        }
    
    def get_time_modifier(self, minute):
        """Get time-based modifier for given minute"""
        for period_name, period_info in self.time_modifiers.items():
            time_min, time_max = period_info['range']
            if time_min <= minute <= time_max:
                return period_info['modifier']
        return self.time_modifiers['injury_time']['modifier']  # Default to injury time
    
    def get_score_modifier(self, score_diff):
        """Get score differential modifier"""
        if score_diff == 0:
            return self.situation_modifiers['score_differential']['tied_game']
        elif score_diff == -1:
            return self.situation_modifiers['score_differential']['losing_by_1']
        elif score_diff <= -2:
            return self.situation_modifiers['score_differential']['losing_by_2_plus']
        elif score_diff == 1:
            return self.situation_modifiers['score_differential']['winning_by_1']
        else:  # score_diff >= 2
            return self.situation_modifiers['score_differential']['winning_by_2_plus']
    
    def calculate_momentum_score(self, features, minute, score_diff=0, stage='group_stage'):
        """Calculate final momentum score using current weight function"""
        
        # Base momentum calculation
        base_momentum = 0
        for component, info in self.component_weights.items():
            if component in features and component != 'execution_quality':
                base_momentum += features[component] * info['weight']
        
        # Apply execution quality multiplier
        base_momentum *= features.get('execution_quality', 0.8)
        
        # Apply time modifier
        time_modifier = self.get_time_modifier(minute)
        
        # Apply score modifier
        score_modifier = self.get_score_modifier(score_diff)
        
        # Apply stage modifier
        stage_modifier = self.situation_modifiers['competition_stage'].get(stage, 1.0)
        
        # Final momentum calculation
        final_momentum = base_momentum * time_modifier * score_modifier * stage_modifier
        
        # Normalize to 0-10 range
        return max(0, min(10, final_momentum))
    
    def create_momentum_targets(self, window_minutes=3):
        """Create momentum Y targets for all events using 3-minute windows"""
        print(f"\n🎯 CREATING MOMENTUM Y TARGETS")
        print(f"   Window size: {window_minutes} minutes")
        print("-" * 50)
        
        # Initialize momentum column
        self.events_df['momentum_y'] = 5.0  # Default neutral momentum
        
        processed_count = 0
        match_count = 0
        
        # Group by match for processing
        for match_id in self.events_df['match_id'].unique():
            match_events = self.events_df[self.events_df['match_id'] == match_id].copy()
            match_events = match_events.sort_values('minute')
            match_count += 1
            
            if len(match_events) == 0:
                continue
            
            stage = 'group_stage'  # Default (could be enhanced with actual stage detection)
            
            # Process each unique minute in the match
            for minute in match_events['minute'].unique():
                if pd.isna(minute):
                    continue
                    
                minute = int(minute)
                
                # Define 3-minute window
                window_start = max(0, minute - window_minutes)
                window_end = minute
                
                # Get events in window
                window_events = match_events[
                    (match_events['minute'] >= window_start) & 
                    (match_events['minute'] <= window_end)
                ]
                
                if len(window_events) == 0:
                    continue
                
                # Get teams for this minute
                minute_events = match_events[match_events['minute'] == minute]
                teams = minute_events['team_name'].dropna().unique()
                
                for team in teams:
                    if pd.isna(team) or team == 'Unknown':
                        continue
                        
                    # Calculate momentum features
                    features = self.calculate_momentum_features(window_events, team, minute)
                    
                    # Calculate momentum score
                    momentum_score = self.calculate_momentum_score(
                        features, minute, score_diff=0, stage=stage
                    )
                    
                    # Assign to all events for this team in this minute
                    team_minute_mask = (
                        (self.events_df['match_id'] == match_id) & 
                        (self.events_df['minute'] == minute) & 
                        (self.events_df['team_name'] == team)
                    )
                    
                    self.events_df.loc[team_minute_mask, 'momentum_y'] = momentum_score
                    processed_count += len(self.events_df[team_minute_mask])
                
                if processed_count % 5000 == 0:
                    print(f"   📊 Processed {processed_count:,} events from {match_count} matches...")
        
        print(f"   ✅ Processed {processed_count:,} events from {match_count} matches")
        
        return self.events_df
    
    def validate_momentum_data(self):
        """Validate momentum Y target data completeness and quality"""
        print(f"\n✅ VALIDATING MOMENTUM Y TARGET DATA")
        print("-" * 50)
        
        # Check for missing values
        missing_count = self.events_df['momentum_y'].isna().sum()
        print(f"   Missing values: {missing_count:,} ({missing_count/len(self.events_df)*100:.2f}%)")
        
        # Check value distribution
        momentum_stats = self.events_df['momentum_y'].describe()
        print(f"\n📊 MOMENTUM SCORE DISTRIBUTION:")
        print(f"   Count:   {momentum_stats['count']:,.0f}")
        print(f"   Mean:    {momentum_stats['mean']:.2f}")
        print(f"   Std:     {momentum_stats['std']:.2f}")
        print(f"   Min:     {momentum_stats['min']:.2f}")
        print(f"   25%:     {momentum_stats['25%']:.2f}")
        print(f"   Median:  {momentum_stats['50%']:.2f}")
        print(f"   75%:     {momentum_stats['75%']:.2f}")
        print(f"   Max:     {momentum_stats['max']:.2f}")
        
        # Check value ranges
        valid_range = ((self.events_df['momentum_y'] >= 0) & 
                      (self.events_df['momentum_y'] <= 10)).sum()
        print(f"\n   Values in range [0-10]: {valid_range:,} ({valid_range/len(self.events_df)*100:.1f}%)")
        
        # Distribution by score ranges
        print(f"\n📈 MOMENTUM LEVEL DISTRIBUTION:")
        score_ranges = [
            ('Very Low (0-2)', (self.events_df['momentum_y'] < 2).sum()),
            ('Low (2-4)', ((self.events_df['momentum_y'] >= 2) & (self.events_df['momentum_y'] < 4)).sum()),
            ('Medium (4-6)', ((self.events_df['momentum_y'] >= 4) & (self.events_df['momentum_y'] < 6)).sum()),
            ('High (6-8)', ((self.events_df['momentum_y'] >= 6) & (self.events_df['momentum_y'] < 8)).sum()),
            ('Very High (8-10)', (self.events_df['momentum_y'] >= 8).sum())
        ]
        
        for range_name, count in score_ranges:
            percentage = count / len(self.events_df) * 100
            print(f"   {range_name:20}: {count:6,} ({percentage:5.1f}%)")
        
        # Check by event type
        print(f"\n🎯 MOMENTUM BY EVENT TYPE (Top 10):")
        event_momentum = self.events_df.groupby('event_type')['momentum_y'].agg(['count', 'mean']).sort_values('count', ascending=False)
        for event_type, row in event_momentum.head(10).iterrows():
            print(f"   {event_type:20}: {row['count']:6,} events, avg momentum {row['mean']:4.1f}")
        
        return missing_count == 0
    
    def get_real_examples(self, num_examples=20):
        """Get real examples for validation"""
        print(f"\n📋 REAL EXAMPLES FOR VALIDATION (Sample of {num_examples})")
        print("=" * 80)
        
        # Get diverse examples across momentum ranges and event types
        examples = []
        
        # Very High momentum examples
        high_momentum = self.events_df[self.events_df['momentum_y'] >= 8.0].sample(n=min(4, len(self.events_df[self.events_df['momentum_y'] >= 8.0])), random_state=42)
        examples.append(("Very High (8-10)", high_momentum))
        
        # High momentum examples  
        med_high_momentum = self.events_df[(self.events_df['momentum_y'] >= 6.0) & (self.events_df['momentum_y'] < 8.0)].sample(n=min(4, len(self.events_df[(self.events_df['momentum_y'] >= 6.0) & (self.events_df['momentum_y'] < 8.0)])), random_state=42)
        examples.append(("High (6-8)", med_high_momentum))
        
        # Medium momentum examples
        medium_momentum = self.events_df[(self.events_df['momentum_y'] >= 4.0) & (self.events_df['momentum_y'] < 6.0)].sample(n=min(4, len(self.events_df[(self.events_df['momentum_y'] >= 4.0) & (self.events_df['momentum_y'] < 6.0)])), random_state=42)
        examples.append(("Medium (4-6)", medium_momentum))
        
        # Low momentum examples
        low_momentum = self.events_df[(self.events_df['momentum_y'] >= 2.0) & (self.events_df['momentum_y'] < 4.0)].sample(n=min(4, len(self.events_df[(self.events_df['momentum_y'] >= 2.0) & (self.events_df['momentum_y'] < 4.0)])), random_state=42)
        examples.append(("Low (2-4)", low_momentum))
        
        # Very Low momentum examples
        very_low_momentum = self.events_df[self.events_df['momentum_y'] < 2.0].sample(n=min(4, len(self.events_df[self.events_df['momentum_y'] < 2.0])), random_state=42)
        examples.append(("Very Low (0-2)", very_low_momentum))
        
        example_count = 1
        for range_name, sample_df in examples:
            print(f"\n🎯 {range_name} MOMENTUM EXAMPLES:")
            print("-" * 60)
            
            for idx, row in sample_df.iterrows():
                print(f"\n📋 EXAMPLE {example_count}:")
                print(f"   Team: {row['team_name']}")
                print(f"   Event: {row['event_type']}")
                print(f"   Minute: {row['minute']}")
                print(f"   Match: {row['home_team']} vs {row['away_team']}")
                print(f"   MOMENTUM SCORE: {row['momentum_y']:.2f}/10")
                
                # Context information
                if pd.notna(row.get('possession_team_name')):
                    possession_status = "✅ In Possession" if row['team_name'] == row['possession_team_name'] else "❌ Out of Possession"
                    print(f"   Possession: {possession_status}")
                
                if pd.notna(row.get('under_pressure')):
                    print(f"   Under Pressure: ✅ Yes")
                else:
                    print(f"   Under Pressure: ❌ No")
                
                example_count += 1
                
                if example_count > num_examples:
                    break
            
            if example_count > num_examples:
                break
        
        return examples
    
    def save_results(self):
        """Save the enhanced dataset with momentum Y targets"""
        print(f"\n💾 SAVING ENHANCED DATASET")
        print("-" * 50)
        
        # Save enhanced events with momentum scores
        output_file = 'euro_2024_events_with_momentum_y.csv'
        self.events_df.to_csv(output_file, index=False)
        print(f"   ✅ Saved enhanced dataset: {output_file}")
        print(f"   📊 Total rows: {len(self.events_df):,}")
        print(f"   📋 Total columns: {len(self.events_df.columns)}")
        
        # Save momentum statistics summary
        summary_stats = {
            'total_events': len(self.events_df),
            'momentum_mean': self.events_df['momentum_y'].mean(),
            'momentum_std': self.events_df['momentum_y'].std(),
            'momentum_min': self.events_df['momentum_y'].min(),
            'momentum_max': self.events_df['momentum_y'].max(),
            'missing_values': self.events_df['momentum_y'].isna().sum(),
            'unique_matches': self.events_df['match_id'].nunique(),
            'unique_teams': self.events_df['team_name'].nunique()
        }
        
        summary_df = pd.DataFrame([summary_stats])
        summary_file = 'momentum_y_summary_stats.csv'
        summary_df.to_csv(summary_file, index=False)
        print(f"   ✅ Saved summary statistics: {summary_file}")
        
        return output_file

def main():
    """Main execution function"""
    print("🚀 STARTING MOMENTUM Y TARGET CREATION")
    print("=" * 80)
    
    try:
        # Initialize creator
        creator = MomentumYTargetCreator()
        
        # Create momentum targets
        enhanced_df = creator.create_momentum_targets(window_minutes=3)
        
        # Validate results
        is_complete = creator.validate_momentum_data()
        
        # Get real examples
        examples = creator.get_real_examples(num_examples=20)
        
        # Save results
        output_file = creator.save_results()
        
        print(f"\n🎉 MOMENTUM Y TARGET CREATION COMPLETE!")
        print(f"✅ Data completeness: {'PASS' if is_complete else 'NEEDS REVIEW'}")
        print(f"📁 Output file: {output_file}")
        print(f"📊 Ready for model training with momentum Y targets!")
        
        return creator
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()