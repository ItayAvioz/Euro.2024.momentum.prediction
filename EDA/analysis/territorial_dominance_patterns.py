#!/usr/bin/env python3
"""
Territorial Dominance DNA Patterns Analysis
Discover hidden tactical territorial signatures in Euro 2024 data
Variables: location, team, possession_team, type (event_type)
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

class TerritorialDominanceAnalyzer:
    """Analyze territorial dominance patterns in Euro 2024"""
    
    def __init__(self, dataset_path='Data/euro_2024_complete_dataset.csv'):
        """Initialize with dataset"""
        print("🏟️ TERRITORIAL DOMINANCE DNA PATTERNS ANALYSIS")
        print("=" * 70)
        
        # Load dataset
        print("📊 Loading Euro 2024 dataset...")
        self.df = pd.read_csv(dataset_path, low_memory=False)
        print(f"   Total events: {len(self.df):,}")
        print(f"   Unique teams: {self.df['team'].nunique()}")
        print(f"   Unique locations: {self.df['location'].nunique()}")
        
        # Extract event type from type column
        self.df['event_type'] = self.df['type'].apply(lambda x: eval(x)['name'] if pd.notna(x) and isinstance(x, str) else 'Unknown')
        print(f"   Event types: {self.df['event_type'].nunique()}")
        
        # Prepare territorial features
        self.prepare_territorial_features()
        
    def prepare_territorial_features(self):
        """Prepare territorial dominance features for clustering"""
        print("\n🔧 PREPARING TERRITORIAL FEATURES")
        print("-" * 50)
        
        # Filter out events without location data
        df_with_location = self.df.dropna(subset=['location']).copy()
        print(f"   Events with location data: {len(df_with_location):,}")
        
        territorial_features = []
        
        for _, row in df_with_location.iterrows():
            try:
                # Parse location coordinates [x, y]
                location = eval(row['location']) if isinstance(row['location'], str) else row['location']
                x, y = location[0], location[1]
                
                # Extract team info properly
                team_info = eval(row['team']) if isinstance(row['team'], str) else row['team']
                team_name = team_info.get('name', 'Unknown') if isinstance(team_info, dict) else str(team_info)
                
                possession_info = eval(row['possession_team']) if isinstance(row['possession_team'], str) else row['possession_team']
                possession_team = possession_info.get('name', 'Unknown') if isinstance(possession_info, dict) else str(possession_info)
                
                # Calculate territorial features
                features = {
                    # Raw coordinates (0-120, 0-80 pitch)
                    'x_coordinate': x,
                    'y_coordinate': y,
                    
                    # Territorial zones
                    'attacking_third': 1 if x >= 80 else 0,
                    'middle_third': 1 if 40 <= x < 80 else 0,
                    'defensive_third': 1 if x < 40 else 0,
                    
                    # Pitch width zones
                    'left_wing': 1 if y <= 26.67 else 0,
                    'center_channel': 1 if 26.67 < y < 53.33 else 0,
                    'right_wing': 1 if y >= 53.33 else 0,
                    
                    # Distance-based features
                    'distance_to_goal': np.sqrt((120 - x)**2 + (40 - y)**2),
                    'distance_to_own_goal': np.sqrt(x**2 + (40 - y)**2),
                    'distance_to_center': np.sqrt((60 - x)**2 + (40 - y)**2),
                    
                    # Team possession context
                    'own_possession': 1 if team_name == possession_team else 0,
                    'opponent_possession': 1 if team_name != possession_team else 0,
                    
                    # Event type encoding
                    'is_attacking_event': 1 if row['event_type'] in ['Shot', 'Goal', 'Pass', 'Carry'] else 0,
                    'is_defensive_event': 1 if row['event_type'] in ['Ball Recovery', 'Clearance', 'Block', 'Interception'] else 0,
                    'is_contested_event': 1 if row['event_type'] in ['Duel', 'Pressure', 'Foul Committed', 'Foul Won'] else 0,
                    
                    # Advanced territorial metrics
                    'field_tilt': (x / 120) * 100,  # 0-100% field position
                    'width_utilization': abs(y - 40) / 40,  # How wide from center
                    'danger_zone': 1 if (x >= 102 and 20 <= y <= 60) else 0,  # Penalty area proximity
                    
                    # Team and event metadata
                    'team_name': team_name,
                    'event_type': row['event_type'],
                    'match_id': row.get('match_id', 'Unknown')
                }
                
                territorial_features.append(features)
                
            except Exception as e:
                continue  # Skip invalid location data
        
        self.territorial_df = pd.DataFrame(territorial_features)
        
        print(f"✅ Created territorial dataset: {len(self.territorial_df):,} events")
        print(f"   Features: {len([col for col in self.territorial_df.columns if col not in ['team_name', 'event_type', 'match_id']])}")
        print(f"   Teams analyzed: {self.territorial_df['team_name'].nunique()}")
        print(f"   Event types: {self.territorial_df['event_type'].nunique()}")
        
    def analyze_territorial_patterns(self):
        """Analyze territorial dominance patterns comprehensively"""
        print("\n📈 TERRITORIAL PATTERN ANALYSIS")
        print("-" * 50)
        
        # Feature columns for clustering
        feature_cols = [
            'x_coordinate', 'y_coordinate', 'attacking_third', 'middle_third', 'defensive_third',
            'left_wing', 'center_channel', 'right_wing', 'distance_to_goal', 'distance_to_own_goal',
            'distance_to_center', 'own_possession', 'opponent_possession', 'is_attacking_event',
            'is_defensive_event', 'is_contested_event', 'field_tilt', 'width_utilization', 'danger_zone'
        ]
        
        # Prepare clustering data
        X = self.territorial_df[feature_cols].fillna(0)
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Test different cluster numbers
        silhouette_scores = []
        k_range = range(2, 11)
        
        print("🔍 Testing cluster numbers...")
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
        self.territorial_df['territorial_cluster'] = kmeans.fit_predict(X_scaled)
        
        # Store clustering info
        self.best_k = best_k
        self.best_score = best_score
        self.feature_cols = feature_cols
        self.scaler = scaler
        self.kmeans = kmeans
        
        # Analyze clusters
        self.analyze_clusters()
        
        return best_k, best_score
    
    def analyze_clusters(self):
        """Analyze discovered territorial clusters"""
        print("\n🔍 TERRITORIAL CLUSTER ANALYSIS")
        print("-" * 50)
        
        cluster_analysis = []
        
        for cluster_id in sorted(self.territorial_df['territorial_cluster'].unique()):
            cluster_data = self.territorial_df[self.territorial_df['territorial_cluster'] == cluster_id]
            
            # Calculate cluster characteristics
            characteristics = {
                'cluster': cluster_id,
                'size': len(cluster_data),
                'percentage': len(cluster_data) / len(self.territorial_df) * 100,
                
                # Spatial characteristics
                'avg_x': cluster_data['x_coordinate'].mean(),
                'avg_y': cluster_data['y_coordinate'].mean(),
                'avg_field_tilt': cluster_data['field_tilt'].mean(),
                'avg_width_use': cluster_data['width_utilization'].mean(),
                
                # Zone preferences
                'attacking_third_rate': cluster_data['attacking_third'].mean() * 100,
                'middle_third_rate': cluster_data['middle_third'].mean() * 100,
                'defensive_third_rate': cluster_data['defensive_third'].mean() * 100,
                
                # Width preferences
                'left_wing_rate': cluster_data['left_wing'].mean() * 100,
                'center_rate': cluster_data['center_channel'].mean() * 100,
                'right_wing_rate': cluster_data['right_wing'].mean() * 100,
                
                # Possession context
                'own_possession_rate': cluster_data['own_possession'].mean() * 100,
                'opponent_possession_rate': cluster_data['opponent_possession'].mean() * 100,
                
                # Event style
                'attacking_event_rate': cluster_data['is_attacking_event'].mean() * 100,
                'defensive_event_rate': cluster_data['is_defensive_event'].mean() * 100,
                'contested_event_rate': cluster_data['is_contested_event'].mean() * 100,
                
                # Danger metrics
                'avg_distance_to_goal': cluster_data['distance_to_goal'].mean(),
                'danger_zone_rate': cluster_data['danger_zone'].mean() * 100,
                
                # Top event types and teams
                'top_event_types': cluster_data['event_type'].value_counts().head(3).to_dict(),
                'top_teams': cluster_data['team_name'].value_counts().head(3).to_dict()
            }
            
            cluster_analysis.append(characteristics)
            
            # Print cluster summary
            print(f"\n🏷️  CLUSTER {cluster_id} ({characteristics['percentage']:.1f}% of events)")
            print(f"   Size: {characteristics['size']:,} events")
            print(f"   Average Position: ({characteristics['avg_x']:.1f}, {characteristics['avg_y']:.1f})")
            print(f"   Field Tilt: {characteristics['avg_field_tilt']:.1f}% (0=own goal, 100=opponent goal)")
            print(f"   Width Utilization: {characteristics['avg_width_use']:.2f} (0=center, 1=sideline)")
            
            print(f"   📍 Zone Distribution:")
            print(f"      Attacking Third: {characteristics['attacking_third_rate']:.1f}%")
            print(f"      Middle Third: {characteristics['middle_third_rate']:.1f}%")
            print(f"      Defensive Third: {characteristics['defensive_third_rate']:.1f}%")
            
            print(f"   📐 Width Distribution:")
            print(f"      Left Wing: {characteristics['left_wing_rate']:.1f}%")
            print(f"      Center: {characteristics['center_rate']:.1f}%")
            print(f"      Right Wing: {characteristics['right_wing_rate']:.1f}%")
            
            print(f"   ⚽ Event Characteristics:")
            print(f"      Attacking Events: {characteristics['attacking_event_rate']:.1f}%")
            print(f"      Defensive Events: {characteristics['defensive_event_rate']:.1f}%")
            print(f"      Contested Events: {characteristics['contested_event_rate']:.1f}%")
            
            print(f"   🎯 Danger Metrics:")
            print(f"      Distance to Goal: {characteristics['avg_distance_to_goal']:.1f}m")
            print(f"      Danger Zone Rate: {characteristics['danger_zone_rate']:.1f}%")
            
            print(f"   📊 Top Events: {list(characteristics['top_event_types'].keys())}")
        
        self.cluster_analysis = cluster_analysis
        
        # Create cluster interpretation
        self.interpret_territorial_clusters()
    
    def interpret_territorial_clusters(self):
        """Interpret the meaning of discovered territorial clusters"""
        print("\n🎭 TERRITORIAL CLUSTER INTERPRETATION")
        print("-" * 50)
        
        interpretations = []
        
        for analysis in self.cluster_analysis:
            cluster_id = analysis['cluster']
            
            # Determine cluster type based on characteristics
            if analysis['attacking_third_rate'] > 60:
                if analysis['danger_zone_rate'] > 20:
                    cluster_type = "Goal Threat Zone"
                    description = "High attacking third, frequent danger zone activity"
                else:
                    cluster_type = "Final Third Controllers"
                    description = "Attacking third dominance, wide build-up"
            elif analysis['defensive_third_rate'] > 60:
                if analysis['defensive_event_rate'] > 50:
                    cluster_type = "Defensive Fortress"
                    description = "Own third defensive actions, clearances and blocks"
                else:
                    cluster_type = "Build-Up Initiators" 
                    description = "Own third possession, patient build-up start"
            elif analysis['center_rate'] > 60:
                cluster_type = "Central Corridor"
                description = "Middle channel control, through-the-center play"
            elif analysis['left_wing_rate'] > 50 or analysis['right_wing_rate'] > 50:
                cluster_type = "Wide Play Specialists"
                description = "Flank-based territorial control"
            else:
                cluster_type = "Transitional Zones"
                description = "Mixed territorial approach, adaptable positioning"
            
            interpretation = {
                'cluster_id': cluster_id,
                'type': cluster_type,
                'description': description,
                'size_percentage': analysis['percentage'],
                'key_characteristics': [
                    f"Field Position: {analysis['avg_field_tilt']:.1f}%",
                    f"Width Usage: {analysis['avg_width_use']:.2f}",
                    f"Goal Distance: {analysis['avg_distance_to_goal']:.1f}m"
                ]
            }
            
            interpretations.append(interpretation)
            
            print(f"\n🎯 CLUSTER {cluster_id}: {cluster_type}")
            print(f"   Description: {description}")
            print(f"   Size: {analysis['percentage']:.1f}% of territorial events")
            print(f"   Key Characteristics: {', '.join(interpretation['key_characteristics'])}")
        
        self.interpretations = interpretations
    
    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        print("\n📋 TERRITORIAL DOMINANCE SUMMARY REPORT")
        print("=" * 70)
        
        # Overall statistics
        print(f"📊 DATASET OVERVIEW")
        print(f"   Total Events Analyzed: {len(self.territorial_df):,}")
        print(f"   Unique Teams: {self.territorial_df['team_name'].nunique()}")
        print(f"   Unique Positions: {len(self.territorial_df[['x_coordinate', 'y_coordinate']].drop_duplicates())}")
        print(f"   Event Types: {self.territorial_df['event_type'].nunique()}")
        
        # Clustering results
        print(f"\n🎯 CLUSTERING RESULTS")
        print(f"   Number of Clusters: {len(self.cluster_analysis)}")
        print(f"   Best Silhouette Score: {self.best_score:.3f}")
        print(f"   Features Used: {len(self.feature_cols)}")
        
        # Cluster summary
        print(f"\n🏷️  DISCOVERED TERRITORIAL PATTERNS")
        for interp in self.interpretations:
            print(f"   {interp['type']} ({interp['size_percentage']:.1f}%): {interp['description']}")
        
        # Key insights
        print(f"\n🔍 KEY TERRITORIAL INSIGHTS")
        
        # Zone distribution insights
        attacking_clusters = [c for c in self.cluster_analysis if c['attacking_third_rate'] > 50]
        defensive_clusters = [c for c in self.cluster_analysis if c['defensive_third_rate'] > 50]
        central_clusters = [c for c in self.cluster_analysis if c['center_rate'] > 40]
        
        print(f"   🎯 Attacking Zone Clusters: {len(attacking_clusters)} focus on final third")
        print(f"   🛡️  Defensive Zone Clusters: {len(defensive_clusters)} focus on own third")
        print(f"   🎭 Central Play Clusters: {len(central_clusters)} prefer middle channel")
        
        # Danger zone insights
        danger_events = sum(c['size'] * c['danger_zone_rate'] / 100 for c in self.cluster_analysis)
        print(f"   ⚡ High Danger Events: {danger_events:,.0f} in penalty area proximity")
        
        return {
            'total_events': len(self.territorial_df),
            'num_clusters': len(self.cluster_analysis),
            'best_silhouette_score': self.best_score,
            'cluster_interpretations': self.interpretations,
            'key_insights': {
                'attacking_clusters': len(attacking_clusters),
                'defensive_clusters': len(defensive_clusters),
                'central_clusters': len(central_clusters),
                'danger_events': danger_events
            }
        }
    
    def get_sample_examples(self, n=5):
        """Get sample input/output examples"""
        print(f"\n📝 SAMPLE INPUT/OUTPUT EXAMPLES")
        print("-" * 50)
        
        examples = []
        
        # Get diverse examples from different clusters
        for cluster_id in sorted(self.territorial_df['territorial_cluster'].unique())[:n]:
            cluster_data = self.territorial_df[self.territorial_df['territorial_cluster'] == cluster_id]
            sample = cluster_data.sample(1, random_state=42).iloc[0]
            
            example = {
                'input': {
                    'x_coordinate': sample['x_coordinate'],
                    'y_coordinate': sample['y_coordinate'],
                    'event_type': sample['event_type'],
                    'team_name': sample['team_name'],
                    'attacking_third': sample['attacking_third'],
                    'center_channel': sample['center_channel'],
                    'distance_to_goal': sample['distance_to_goal'],
                    'field_tilt': sample['field_tilt']
                },
                'output': {
                    'territorial_cluster': int(sample['territorial_cluster']),
                    'cluster_type': self.interpretations[cluster_id]['type'],
                    'description': self.interpretations[cluster_id]['description']
                }
            }
            
            examples.append(example)
            
            print(f"\n📋 EXAMPLE {cluster_id + 1}:")
            print(f"   📥 INPUT:")
            print(f"      Position: ({example['input']['x_coordinate']:.1f}, {example['input']['y_coordinate']:.1f})")
            print(f"      Event Type: {example['input']['event_type']}")
            print(f"      Team: {example['input']['team_name']}")
            print(f"      Field Tilt: {example['input']['field_tilt']:.1f}% towards goal")
            print(f"      Distance to Goal: {example['input']['distance_to_goal']:.1f}m")
            print(f"      Zone: {'Attacking' if example['input']['attacking_third'] else 'Non-attacking'} Third")
            
            print(f"   📤 OUTPUT:")
            print(f"      Cluster: {example['output']['territorial_cluster']}")
            print(f"      Type: {example['output']['cluster_type']}")
            print(f"      Pattern: {example['output']['description']}")
        
        return examples

def main():
    """Run territorial dominance pattern analysis"""
    try:
        # Initialize analyzer
        analyzer = TerritorialDominanceAnalyzer()
        
        # Run clustering analysis
        best_k, best_score = analyzer.analyze_territorial_patterns()
        
        # Generate summary report
        summary = analyzer.generate_summary_report()
        
        # Show examples
        examples = analyzer.get_sample_examples()
        
        print(f"\n✅ TERRITORIAL DOMINANCE ANALYSIS COMPLETE")
        print(f"   Discovered {best_k} territorial dominance patterns")
        print(f"   Silhouette Score: {best_score:.3f}")
        print(f"   Analysis complete with {summary['total_events']:,} events")
        
        return analyzer, summary, examples
        
    except Exception as e:
        print(f"❌ Error in territorial analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None, None

if __name__ == "__main__":
    analyzer, summary, examples = main() 