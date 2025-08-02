#!/usr/bin/env python3
"""
Temporal Momentum Clustering Analysis
Discover hidden patterns in time-based momentum using Euro 2024 data
Following the same approach as pass/carry analysis
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class TemporalMomentumAnalyzer:
    """Analyze temporal patterns in Euro 2024 momentum"""
    
    def __init__(self, dataset_path='Data/euro_2024_complete_dataset.csv'):
        """Initialize with dataset"""
        print("🕒 TEMPORAL MOMENTUM CLUSTERING ANALYSIS")
        print("=" * 60)
        
        # Load dataset
        print("📊 Loading Euro 2024 dataset...")
        self.df = pd.read_csv(dataset_path)
        print(f"   Total events: {len(self.df):,}")
        print(f"   Unique matches: {self.df['match_id'].nunique()}")
        print(f"   Date range: {self.df['match_date'].min()} to {self.df['match_date'].max()}")
        
        # Prepare temporal features
        self.prepare_temporal_features()
        
    def prepare_temporal_features(self):
        """Prepare temporal features for clustering"""
        print("\n🔧 PREPARING TEMPORAL FEATURES")
        print("-" * 40)
        
        # Convert kick_off times to minutes from midnight for analysis
        def time_to_minutes(time_str):
            """Convert HH:MM:SS.mmm to minutes from midnight"""
            try:
                time_parts = time_str.split(':')
                hours = int(time_parts[0])
                minutes = int(time_parts[1])
                return hours * 60 + minutes
            except:
                return np.nan
                
        # Create comprehensive temporal features
        temporal_features = []
        
        for _, row in self.df.iterrows():
            features = {
                # Basic time features
                'minute': row['minute'],
                'second': row['second'],
                'period': row['period'],
                
                # Game phase (derived from minute and period)
                'game_phase': self._calculate_game_phase(row['minute'], row['period']),
                
                # Time in match (total minutes played)
                'total_minutes': self._calculate_total_minutes(row['minute'], row['period']),
                
                # Kickoff time context
                'kickoff_minutes': time_to_minutes(row.get('kick_off', '19:00:00.000')),
                
                # Tournament context
                'stage_numeric': self._encode_stage(row['stage']),
                'match_week': row.get('match_week', 1),
                
                # Temporal momentum indicators
                'is_opening_phase': 1 if row['minute'] <= 15 else 0,
                'is_closing_phase': 1 if row['minute'] >= 75 else 0,
                'is_halftime_response': 1 if (row['period'] == 2 and row['minute'] <= 60) else 0,
                'is_extra_time': 1 if row['period'] > 2 else 0,
                
                # Event density context (events per minute in current period)
                'period_intensity': self._calculate_period_intensity(row),
                
                # Original event info for analysis
                'event_type': row['event_type'],
                'team_name': row.get('team_name', 'Unknown'),
                'match_id': row['match_id']
            }
            temporal_features.append(features)
        
        self.temporal_df = pd.DataFrame(temporal_features)
        
        print(f"✅ Created temporal dataset: {len(self.temporal_df):,} events")
        print(f"   Features: {[col for col in self.temporal_df.columns if col not in ['event_type', 'team_name', 'match_id']]}")
        
    def _calculate_game_phase(self, minute, period):
        """Calculate game phase from minute and period"""
        if period == 1:
            if minute <= 15: return 1  # Opening
            elif minute <= 30: return 2  # Early Development
            else: return 3  # Late First Half
        elif period == 2:
            if minute <= 60: return 4  # Halftime Response
            elif minute <= 75: return 5  # Second Half Development
            else: return 6  # Closing Phase
        else:
            return 7  # Extra Time
    
    def _calculate_total_minutes(self, minute, period):
        """Calculate total minutes played"""
        if period == 1:
            return minute
        elif period == 2:
            return 45 + minute
        elif period == 3:
            return 90 + minute
        elif period == 4:
            return 105 + minute
        else:
            return 120 + minute
    
    def _encode_stage(self, stage):
        """Encode tournament stage numerically"""
        stage_map = {
            'Group Stage': 1,
            'Round of 16': 2,
            'Quarter-finals': 3,
            'Semi-finals': 4,
            'Final': 5
        }
        return stage_map.get(stage, 1)
    
    def _calculate_period_intensity(self, row):
        """Calculate event intensity for current period"""
        try:
            period_events = self.df[
                (self.df['match_id'] == row['match_id']) & 
                (self.df['period'] == row['period'])
            ]
            if len(period_events) > 0:
                max_minute = max(period_events['minute'].max(), 1)
                return len(period_events) / max_minute
            return 0
        except:
            return 0
    
    def analyze_temporal_patterns(self):
        """Analyze temporal patterns comprehensively"""
        print("\n📈 TEMPORAL PATTERN ANALYSIS")
        print("-" * 40)
        
        # Feature columns for clustering
        feature_cols = [
            'minute', 'second', 'period', 'game_phase', 'total_minutes',
            'kickoff_minutes', 'stage_numeric', 'match_week',
            'is_opening_phase', 'is_closing_phase', 'is_halftime_response',
            'is_extra_time', 'period_intensity'
        ]
        
        # Prepare clustering data
        X = self.temporal_df[feature_cols].fillna(0)
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Test different cluster numbers
        silhouette_scores = []
        k_range = range(2, 11)
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(X_scaled)
            score = silhouette_score(X_scaled, cluster_labels)
            silhouette_scores.append(score)
            print(f"   K={k}: Silhouette Score = {score:.3f}")
        
        # Find optimal clusters
        best_k = k_range[np.argmax(silhouette_scores)]
        best_score = max(silhouette_scores)
        
        print(f"\n🎯 OPTIMAL CLUSTERING")
        print(f"   Best K: {best_k}")
        print(f"   Best Silhouette Score: {best_score:.3f}")
        
        # Final clustering
        kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
        self.temporal_df['temporal_cluster'] = kmeans.fit_predict(X_scaled)
        
        # Analyze clusters
        self.analyze_clusters(feature_cols)
        
        return best_k, best_score
    
    def analyze_clusters(self, feature_cols):
        """Analyze discovered temporal clusters"""
        print("\n🔍 CLUSTER ANALYSIS")
        print("-" * 40)
        
        cluster_analysis = []
        
        for cluster_id in sorted(self.temporal_df['temporal_cluster'].unique()):
            cluster_data = self.temporal_df[self.temporal_df['temporal_cluster'] == cluster_id]
            
            # Calculate cluster characteristics
            characteristics = {
                'cluster': cluster_id,
                'size': len(cluster_data),
                'percentage': len(cluster_data) / len(self.temporal_df) * 100,
                
                # Temporal characteristics
                'avg_minute': cluster_data['minute'].mean(),
                'avg_period': cluster_data['period'].mean(),
                'avg_game_phase': cluster_data['game_phase'].mean(),
                'avg_total_minutes': cluster_data['total_minutes'].mean(),
                
                # Context characteristics
                'avg_kickoff_minutes': cluster_data['kickoff_minutes'].mean(),
                'avg_stage': cluster_data['stage_numeric'].mean(),
                'avg_intensity': cluster_data['period_intensity'].mean(),
                
                # Phase flags
                'opening_rate': cluster_data['is_opening_phase'].mean() * 100,
                'closing_rate': cluster_data['is_closing_phase'].mean() * 100,
                'halftime_response_rate': cluster_data['is_halftime_response'].mean() * 100,
                'extra_time_rate': cluster_data['is_extra_time'].mean() * 100,
                
                # Top event types
                'top_event_types': cluster_data['event_type'].value_counts().head(3).to_dict(),
                
                # Stage distribution
                'stage_distribution': cluster_data.groupby('stage_numeric')['stage_numeric'].count().to_dict()
            }
            
            cluster_analysis.append(characteristics)
            
            # Print cluster summary
            print(f"\n🏷️  CLUSTER {cluster_id} ({characteristics['percentage']:.1f}% of events)")
            print(f"   Size: {characteristics['size']:,} events")
            print(f"   Average Minute: {characteristics['avg_minute']:.1f}")
            print(f"   Average Period: {characteristics['avg_period']:.1f}")
            print(f"   Game Phase: {characteristics['avg_game_phase']:.1f}")
            print(f"   Total Minutes: {characteristics['avg_total_minutes']:.1f}")
            print(f"   Kickoff Context: {characteristics['avg_kickoff_minutes']:.0f} minutes from midnight")
            print(f"   Tournament Stage: {characteristics['avg_stage']:.1f}")
            print(f"   Period Intensity: {characteristics['avg_intensity']:.2f} events/min")
            print(f"   Opening Phase: {characteristics['opening_rate']:.1f}%")
            print(f"   Closing Phase: {characteristics['closing_rate']:.1f}%")
            print(f"   Halftime Response: {characteristics['halftime_response_rate']:.1f}%")
            print(f"   Extra Time: {characteristics['extra_time_rate']:.1f}%")
            print(f"   Top Events: {list(characteristics['top_event_types'].keys())}")
        
        self.cluster_analysis = cluster_analysis
        
        # Create cluster interpretation
        self.interpret_temporal_clusters()
    
    def interpret_temporal_clusters(self):
        """Interpret the meaning of discovered clusters"""
        print("\n🎭 CLUSTER INTERPRETATION")
        print("-" * 40)
        
        interpretations = []
        
        for analysis in self.cluster_analysis:
            cluster_id = analysis['cluster']
            
            # Determine cluster type based on characteristics
            if analysis['opening_rate'] > 50:
                cluster_type = "Opening Blitz"
                description = "Early game aggressive momentum"
            elif analysis['closing_rate'] > 50:
                cluster_type = "Decisive Moments"
                description = "Late game momentum swings"
            elif analysis['halftime_response_rate'] > 30:
                cluster_type = "Halftime Response"
                description = "Second half tactical adjustment"
            elif analysis['extra_time_rate'] > 10:
                cluster_type = "Pressure Cooker"
                description = "Extra time high-stakes moments"
            elif analysis['avg_intensity'] > 2.0:
                cluster_type = "High Intensity"
                description = "Fast-paced tactical execution"
            elif analysis['avg_stage'] > 3:
                cluster_type = "Tournament Climax"
                description = "Late stage strategic play"
            else:
                cluster_type = "Control Phase"
                description = "Measured possession and development"
            
            interpretation = {
                'cluster_id': cluster_id,
                'type': cluster_type,
                'description': description,
                'size_percentage': analysis['percentage'],
                'key_characteristics': [
                    f"Avg Minute: {analysis['avg_minute']:.1f}",
                    f"Period: {analysis['avg_period']:.1f}",
                    f"Intensity: {analysis['avg_intensity']:.2f} events/min"
                ]
            }
            
            interpretations.append(interpretation)
            
            print(f"\n🎯 CLUSTER {cluster_id}: {cluster_type}")
            print(f"   Description: {description}")
            print(f"   Size: {analysis['percentage']:.1f}% of all events")
            print(f"   Key Characteristics: {', '.join(interpretation['key_characteristics'])}")
        
        self.interpretations = interpretations
    
    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        print("\n📋 TEMPORAL MOMENTUM SUMMARY REPORT")
        print("=" * 60)
        
        # Overall statistics
        print(f"📊 DATASET OVERVIEW")
        print(f"   Total Events Analyzed: {len(self.temporal_df):,}")
        print(f"   Unique Matches: {self.temporal_df['match_id'].nunique()}")
        print(f"   Tournament Stages: {self.temporal_df['stage_numeric'].nunique()}")
        print(f"   Time Range: 0-{self.temporal_df['total_minutes'].max():.0f} minutes")
        
        # Clustering results
        print(f"\n🎯 CLUSTERING RESULTS")
        print(f"   Number of Clusters: {len(self.cluster_analysis)}")
        print(f"   Best Silhouette Score: {getattr(self, 'best_silhouette_score', 'N/A')}")
        
        # Cluster summary
        print(f"\n🏷️  DISCOVERED PATTERNS")
        for interp in self.interpretations:
            print(f"   {interp['type']} ({interp['size_percentage']:.1f}%): {interp['description']}")
        
        # Key insights
        print(f"\n🔍 KEY INSIGHTS")
        
        # Time-based insights
        opening_clusters = [c for c in self.cluster_analysis if c['opening_rate'] > 30]
        closing_clusters = [c for c in self.cluster_analysis if c['closing_rate'] > 30]
        intensity_clusters = [c for c in self.cluster_analysis if c['avg_intensity'] > 2.0]
        
        print(f"   📈 Opening Phase Patterns: {len(opening_clusters)} clusters focus on early game (0-15 min)")
        print(f"   📉 Closing Phase Patterns: {len(closing_clusters)} clusters focus on late game (75+ min)")
        print(f"   ⚡ High Intensity Patterns: {len(intensity_clusters)} clusters with >2.0 events/min")
        
        # Tournament progression insights
        late_stage_events = len(self.temporal_df[self.temporal_df['stage_numeric'] >= 3])
        print(f"   🏆 Tournament Pressure: {late_stage_events:,} events in knockout stages")
        
        # Period distribution insights
        period_dist = self.temporal_df['period'].value_counts().sort_index()
        print(f"   ⏱️  Period Distribution: {dict(period_dist)}")
        
        return {
            'total_events': len(self.temporal_df),
            'num_clusters': len(self.cluster_analysis),
            'cluster_interpretations': self.interpretations,
            'key_insights': {
                'opening_patterns': len(opening_clusters),
                'closing_patterns': len(closing_clusters),
                'high_intensity_patterns': len(intensity_clusters),
                'knockout_events': late_stage_events
            }
        }

def main():
    """Run temporal momentum clustering analysis"""
    try:
        # Initialize analyzer
        analyzer = TemporalMomentumAnalyzer()
        
        # Run clustering analysis
        best_k, best_score = analyzer.analyze_temporal_patterns()
        analyzer.best_silhouette_score = best_score
        
        # Generate summary report
        summary = analyzer.generate_summary_report()
        
        print(f"\n✅ TEMPORAL MOMENTUM ANALYSIS COMPLETE")
        print(f"   Discovered {best_k} temporal momentum patterns")
        print(f"   Silhouette Score: {best_score:.3f}")
        print(f"   Analysis complete with {summary['total_events']:,} events")
        
        return analyzer, summary
        
    except Exception as e:
        print(f"❌ Error in temporal analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    analyzer, summary = main() 