#!/usr/bin/env python3
"""
Momentum Flow Corridors Analysis - Idea 3B
Track momentum flow across pitch like rivers - highways, channels, tunnels
Test K=3-10 clustering and assess flow predictability
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

class MomentumFlowCorridorsAnalyzer:
    """Analyze momentum flow corridors across Euro 2024"""
    
    def __init__(self, dataset_path='Data/euro_2024_complete_dataset.csv'):
        print("🌊 MOMENTUM FLOW CORRIDORS ANALYSIS - IDEA 3B")
        print("=" * 70)
        
        # Load dataset
        self.df = pd.read_csv(dataset_path, low_memory=False)
        print(f"📊 Dataset: {len(self.df):,} events")
        
        # Grid parameters for flow analysis
        self.grid_width = 20
        self.grid_length = 15
        
        # Extract key fields
        self.df['event_type'] = self.df['type'].apply(lambda x: eval(x)['name'] if pd.notna(x) and isinstance(x, str) else 'Unknown')
        self.df['team_name'] = self.df['team'].apply(lambda x: eval(x)['name'] if pd.notna(x) and isinstance(x, str) else 'Unknown')
        
        # Extract location coordinates
        self.extract_coordinates()
        
        print(f"🎮 Matches: {self.df['match_id'].nunique()} matches")
        print(f"📍 Events with location: {self.df['x_coord'].notna().sum():,}")
        
    def extract_coordinates(self):
        """Extract x,y coordinates from location field"""
        print("\n🗺️ EXTRACTING COORDINATES FOR FLOW ANALYSIS")
        print("-" * 45)
        
        coords_extracted = 0
        
        for idx, row in self.df.iterrows():
            if pd.notna(row.get('location')):
                try:
                    location = eval(row['location'])
                    if isinstance(location, list) and len(location) >= 2:
                        self.df.at[idx, 'x_coord'] = float(location[0])
                        self.df.at[idx, 'y_coord'] = float(location[1])
                        coords_extracted += 1
                except:
                    self.df.at[idx, 'x_coord'] = np.nan
                    self.df.at[idx, 'y_coord'] = np.nan
            else:
                self.df.at[idx, 'x_coord'] = np.nan
                self.df.at[idx, 'y_coord'] = np.nan
        
        print(f"✅ Extracted coordinates for {coords_extracted:,} events")
        
        # Filter to events with valid coordinates
        self.df = self.df[self.df['x_coord'].notna() & self.df['y_coord'].notna()].copy()
        
        # Normalize coordinates to standard pitch (120x80)
        if len(self.df) > 0:
            x_max = self.df['x_coord'].max()
            y_max = self.df['y_coord'].max()
            
            if x_max > 0 and y_max > 0:
                self.df['x_norm'] = (self.df['x_coord'] / x_max) * 120
                self.df['y_norm'] = (self.df['y_coord'] / y_max) * 80
            else:
                self.df['x_norm'] = self.df['x_coord']
                self.df['y_norm'] = self.df['y_coord']
        
        # Assign zones for flow analysis
        self.assign_flow_zones()
        
    def assign_flow_zones(self):
        """Assign zones for flow analysis"""
        zone_width = 120 / self.grid_width
        zone_length = 80 / self.grid_length
        
        for idx, row in self.df.iterrows():
            x_norm = row['x_norm']
            y_norm = row['y_norm']
            
            zone_x = int(min(x_norm // zone_width, self.grid_width - 1))
            zone_y = int(min(y_norm // zone_length, self.grid_length - 1))
            zone_id = zone_x + zone_y * self.grid_width
            
            self.df.at[idx, 'zone_id'] = zone_id
            self.df.at[idx, 'zone_x'] = zone_x
            self.df.at[idx, 'zone_y'] = zone_y
        
        print(f"✅ Assigned zones for flow analysis ({self.grid_width}x{self.grid_length} grid)")
    
    def detect_flow_sequences(self):
        """Detect momentum flow sequences between zones"""
        print("\n🌊 DETECTING MOMENTUM FLOW SEQUENCES")
        print("-" * 40)
        
        flow_sequences = []
        sequences_detected = 0
        
        # Process each match
        for match_id in self.df['match_id'].unique():
            match_df = self.df[self.df['match_id'] == match_id].sort_values(['minute', 'second'])
            teams = match_df['team_name'].unique()
            
            if len(teams) < 2:
                continue
            
            # Process each team's sequences
            for team in teams:
                team_events = match_df[match_df['team_name'] == team].copy()
                
                # Detect flow sequences (consecutive events forming pathways)
                for i in range(len(team_events) - 1):
                    current_event = team_events.iloc[i]
                    next_event = team_events.iloc[i + 1]
                    
                    # Time proximity check (within 30 seconds)
                    time_diff = (next_event['minute'] - current_event['minute']) * 60 + (next_event.get('second', 0) - current_event.get('second', 0))
                    
                    if time_diff <= 30 and time_diff >= 0:  # Valid flow sequence
                        flow_data = self.calculate_flow_features(current_event, next_event, team, match_id)
                        if flow_data:
                            flow_sequences.append(flow_data)
                            sequences_detected += 1
        
        self.flow_df = pd.DataFrame(flow_sequences)
        print(f"✅ Detected {sequences_detected:,} flow sequences")
        return self.flow_df
    
    def calculate_flow_features(self, from_event, to_event, team, match_id):
        """Calculate flow features between two events"""
        try:
            from_zone = from_event['zone_id']
            to_zone = to_event['zone_id']
            
            # Skip same-zone flows
            if from_zone == to_zone:
                return None
            
            from_x, from_y = from_event['zone_x'], from_event['zone_y']
            to_x, to_y = to_event['zone_x'], to_event['zone_y']
            
            # Flow vector calculation
            flow_distance = np.sqrt((to_x - from_x)**2 + (to_y - from_y)**2)
            flow_direction_x = to_x - from_x
            flow_direction_y = to_y - from_y
            
            # Flow direction classification
            if abs(flow_direction_x) > abs(flow_direction_y):
                primary_direction = 'horizontal'
                flow_orientation = 'attacking' if flow_direction_x > 0 else 'defending'
            else:
                primary_direction = 'vertical'
                flow_orientation = 'wide' if flow_direction_y > 0 else 'central'
            
            # Event importance weighting
            event_weights = {
                'Pass': 1.0, 'Carry': 2.0, 'Dribble': 2.5, 'Shot': 3.0,
                'Cross': 2.2, 'Through Ball': 2.8, 'Corner': 2.0
            }
            
            from_weight = event_weights.get(from_event.get('event_type', 'Unknown'), 1.0)
            to_weight = event_weights.get(to_event.get('event_type', 'Unknown'), 1.0)
            flow_intensity = (from_weight + to_weight) / 2
            
            # Flow efficiency (goal distance improvement)
            from_goal_dist = np.sqrt((120 - from_event['x_norm'])**2 + (40 - from_event['y_norm'])**2)
            to_goal_dist = np.sqrt((120 - to_event['x_norm'])**2 + (40 - to_event['y_norm'])**2)
            goal_approach = from_goal_dist - to_goal_dist  # Positive = closer to goal
            
            # Time features
            time_diff = (to_event['minute'] - from_event['minute']) * 60 + (to_event.get('second', 0) - from_event.get('second', 0))
            flow_speed = flow_distance / (time_diff + 1)  # zones per second
            
            # Corridor identification
            corridor_type = self.classify_corridor_type(from_x, from_y, to_x, to_y, flow_intensity)
            
            return {
                'match_id': match_id,
                'team': team,
                'from_zone': from_zone,
                'to_zone': to_zone,
                'from_x': from_x,
                'from_y': from_y,
                'to_x': to_x,
                'to_y': to_y,
                'flow_distance': flow_distance,
                'flow_direction_x': flow_direction_x,
                'flow_direction_y': flow_direction_y,
                'primary_direction': primary_direction,
                'flow_orientation': flow_orientation,
                'flow_intensity': flow_intensity,
                'goal_approach': goal_approach,
                'flow_speed': flow_speed,
                'time_diff': time_diff,
                'corridor_type': corridor_type,
                'minute': from_event['minute'],
                'game_phase': 'early' if from_event['minute'] <= 30 else 'mid' if from_event['minute'] <= 60 else 'late',
                'attacking_flow': 1 if goal_approach > 0 else 0,
                'long_flow': 1 if flow_distance > 3 else 0,
                'fast_flow': 1 if flow_speed > 0.5 else 0
            }
            
        except Exception as e:
            return None
    
    def classify_corridor_type(self, from_x, from_y, to_x, to_y, intensity):
        """Classify flow corridor type"""
        # Calculate corridor characteristics
        x_diff = abs(to_x - from_x)
        y_diff = abs(to_y - from_y)
        
        # Central vs wide
        avg_y = (from_y + to_y) / 2
        is_central = 5 <= avg_y <= 10  # Central third of pitch width
        
        # Attacking vs defensive
        avg_x = (from_x + to_x) / 2
        is_attacking = avg_x >= 13  # Attacking third
        is_defensive = avg_x <= 7   # Defensive third
        
        # Corridor classification
        if intensity >= 2.5 and x_diff >= 3:
            if is_attacking:
                return 'Attack Highway'
            elif is_defensive:
                return 'Defense Highway'
            else:
                return 'Transition Highway'
        elif is_central and x_diff >= 2:
            return 'Central Channel'
        elif not is_central and y_diff <= 2:
            return 'Wing Alley'
        elif intensity >= 2.0:
            return 'Pressure Tunnel'
        elif x_diff <= 1 and y_diff <= 1:
            return 'Local Flow'
        else:
            return 'General Flow'
    
    def engineer_corridor_features(self):
        """Engineer additional corridor features"""
        print("\n🔧 ENGINEERING CORRIDOR FEATURES")
        print("-" * 35)
        
        # Corridor aggregation features
        corridor_features = []
        
        # Process corridors by type and characteristics
        for match_id in self.flow_df['match_id'].unique():
            match_flows = self.flow_df[self.flow_df['match_id'] == match_id]
            
            for team in match_flows['team'].unique():
                team_flows = match_flows[match_flows['team'] == team]
                
                for corridor_type in team_flows['corridor_type'].unique():
                    corridor_flows = team_flows[team_flows['corridor_type'] == corridor_type]
                    
                    # Aggregate corridor characteristics
                    features = {
                        'match_id': match_id,
                        'team': team,
                        'corridor_type': corridor_type,
                        'corridor_usage_count': len(corridor_flows),
                        'avg_flow_intensity': corridor_flows['flow_intensity'].mean(),
                        'avg_flow_speed': corridor_flows['flow_speed'].mean(),
                        'avg_goal_approach': corridor_flows['goal_approach'].mean(),
                        'total_distance': corridor_flows['flow_distance'].sum(),
                        'attacking_flows_pct': corridor_flows['attacking_flow'].mean() * 100,
                        'long_flows_pct': corridor_flows['long_flow'].mean() * 100,
                        'fast_flows_pct': corridor_flows['fast_flow'].mean() * 100,
                        'corridor_efficiency': corridor_flows['goal_approach'].sum() / len(corridor_flows),
                        'early_usage': len(corridor_flows[corridor_flows['game_phase'] == 'early']),
                        'mid_usage': len(corridor_flows[corridor_flows['game_phase'] == 'mid']),
                        'late_usage': len(corridor_flows[corridor_flows['game_phase'] == 'late']),
                        'primary_direction_horizontal': (corridor_flows['primary_direction'] == 'horizontal').mean(),
                        'flow_consistency': 1 / (corridor_flows['flow_intensity'].std() + 1),
                        'corridor_dominance': len(corridor_flows) / len(team_flows),
                        'avg_time_between_flows': corridor_flows['time_diff'].mean()
                    }
                    
                    corridor_features.append(features)
        
        self.corridor_features_df = pd.DataFrame(corridor_features)
        
        # Additional derived features
        self.corridor_features_df['usage_intensity'] = self.corridor_features_df['corridor_usage_count'] / (self.corridor_features_df['avg_time_between_flows'] + 1)
        self.corridor_features_df['tactical_importance'] = self.corridor_features_df['corridor_efficiency'] * self.corridor_features_df['corridor_dominance']
        self.corridor_features_df['tempo_factor'] = self.corridor_features_df['avg_flow_speed'] * self.corridor_features_df['fast_flows_pct'] / 100
        
        print(f"✅ Engineered corridor features")
        print(f"   Corridor observations: {len(self.corridor_features_df)}")
        print(f"   Total features: {len(self.corridor_features_df.columns)}")
        
        return self.corridor_features_df
    
    def optimize_corridor_clustering(self):
        """Test K=3-10 for optimal corridor clustering"""
        print("\n📊 OPTIMIZING CORRIDOR CLUSTERING (K=3-10)")
        print("-" * 50)
        
        # Select features for clustering
        clustering_features = [
            'corridor_usage_count', 'avg_flow_intensity', 'avg_flow_speed', 'avg_goal_approach',
            'attacking_flows_pct', 'long_flows_pct', 'fast_flows_pct', 'corridor_efficiency',
            'primary_direction_horizontal', 'flow_consistency', 'corridor_dominance',
            'usage_intensity', 'tactical_importance', 'tempo_factor'
        ]
        
        # Filter to significant corridors
        significant_corridors = self.corridor_features_df[self.corridor_features_df['corridor_usage_count'] >= 3].copy()
        
        if len(significant_corridors) < 30:
            print("⚠️  Insufficient significant corridors, using all corridors")
            significant_corridors = self.corridor_features_df.copy()
        
        X = significant_corridors[clustering_features].fillna(0)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        results = []
        
        for k in range(3, 11):
            print(f"   Testing K={k}...")
            
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=20)
            clusters = kmeans.fit_predict(X_scaled)
            
            # Calculate metrics
            silhouette = silhouette_score(X_scaled, clusters)
            inertia = kmeans.inertia_
            
            # Add cluster labels
            significant_corridors[f'cluster_k{k}'] = clusters
            
            # Analyze cluster characteristics
            cluster_analysis = {}
            for cluster_id in range(k):
                cluster_data = significant_corridors[significant_corridors[f'cluster_k{k}'] == cluster_id]
                
                cluster_analysis[cluster_id] = {
                    'size': len(cluster_data),
                    'avg_usage': cluster_data['corridor_usage_count'].mean(),
                    'avg_intensity': cluster_data['avg_flow_intensity'].mean(),
                    'avg_efficiency': cluster_data['corridor_efficiency'].mean(),
                    'dominant_corridor_types': cluster_data['corridor_type'].value_counts().head(3).to_dict()
                }
            
            results.append({
                'k': k,
                'silhouette_score': silhouette,
                'inertia': inertia,
                'cluster_analysis': cluster_analysis
            })
            
            print(f"     Silhouette: {silhouette:.3f}")
        
        self.clustering_results = results
        self.significant_corridors_df = significant_corridors
        
        # Find optimal K
        best_k = max(results, key=lambda x: x['silhouette_score'])
        print(f"\n🏆 OPTIMAL K: {best_k['k']} (Silhouette: {best_k['silhouette_score']:.3f})")
        
        return results, best_k
    
    def analyze_flow_predictability(self):
        """Analyze flow corridor predictability"""
        print("\n🔮 ANALYZING FLOW CORRIDOR PREDICTABILITY")
        print("-" * 45)
        
        predictions = []
        
        # For each team and corridor type combination, predict future usage
        for team in self.corridor_features_df['team'].unique():
            team_corridors = self.corridor_features_df[self.corridor_features_df['team'] == team]
            
            for corridor_type in team_corridors['corridor_type'].unique():
                corridor_data = team_corridors[team_corridors['corridor_type'] == corridor_type]
                
                if len(corridor_data) < 3:
                    continue
                
                # Calculate predictability metrics
                usage_consistency = 1 / (corridor_data['corridor_usage_count'].std() + 1)
                efficiency_consistency = 1 / (corridor_data['corridor_efficiency'].std() + 1)
                intensity_consistency = corridor_data['flow_consistency'].mean()
                
                # Overall predictability
                predictability = (usage_consistency * 0.4 + efficiency_consistency * 0.3 + intensity_consistency * 0.3)
                
                # Usage frequency
                avg_usage = corridor_data['corridor_usage_count'].mean()
                usage_reliability = min(avg_usage / 10, 1.0)  # Normalize to 0-1
                
                # Temporal predictability
                early_usage = corridor_data['early_usage'].mean()
                mid_usage = corridor_data['mid_usage'].mean()
                late_usage = corridor_data['late_usage'].mean()
                
                temporal_consistency = 1 - np.std([early_usage, mid_usage, late_usage]) / (np.mean([early_usage, mid_usage, late_usage]) + 1)
                
                # Combined predictability score
                combined_predictability = (predictability * 0.5 + usage_reliability * 0.3 + temporal_consistency * 0.2)
                
                predictions.append({
                    'team': team,
                    'corridor_type': corridor_type,
                    'usage_consistency': usage_consistency,
                    'efficiency_consistency': efficiency_consistency,
                    'intensity_consistency': intensity_consistency,
                    'usage_reliability': usage_reliability,
                    'temporal_consistency': temporal_consistency,
                    'combined_predictability': combined_predictability,
                    'avg_usage': avg_usage,
                    'avg_efficiency': corridor_data['corridor_efficiency'].mean(),
                    'matches_analyzed': len(corridor_data)
                })
        
        self.predictions_df = pd.DataFrame(predictions)
        
        if len(self.predictions_df) > 0:
            avg_predictability = self.predictions_df['combined_predictability'].mean()
            high_predictability = (self.predictions_df['combined_predictability'] >= 0.6).mean() * 100
            
            print(f"✅ Flow predictability analyzed")
            print(f"   Team-corridor combinations: {len(self.predictions_df)}")
            print(f"   Average predictability: {avg_predictability:.3f}")
            print(f"   High predictability (≥60%): {high_predictability:.1f}% of corridors")
        else:
            print("⚠️  No predictions generated")
        
        return self.predictions_df
    
    def generate_summary(self):
        """Generate comprehensive summary"""
        print("\n📊 GENERATING COMPREHENSIVE SUMMARY")
        print("-" * 40)
        
        # Get optimal results
        best_k = max(self.clustering_results, key=lambda x: x['silhouette_score'])
        
        summary = {
            'total_flow_sequences': len(self.flow_df),
            'total_corridors': len(self.corridor_features_df),
            'significant_corridors': len(self.significant_corridors_df),
            'optimal_k': best_k['k'],
            'optimal_silhouette': best_k['silhouette_score'],
            'corridor_types': len(self.corridor_features_df['corridor_type'].unique())
        }
        
        if len(self.predictions_df) > 0:
            summary.update({
                'avg_flow_predictability': self.predictions_df['combined_predictability'].mean(),
                'high_predictability_pct': (self.predictions_df['combined_predictability'] >= 0.6).mean() * 100,
                'team_corridor_combinations': len(self.predictions_df)
            })
        else:
            summary.update({
                'avg_flow_predictability': 0,
                'high_predictability_pct': 0,
                'team_corridor_combinations': 0
            })
        
        # Save summary
        summary_df = pd.DataFrame([summary])
        summary_df.to_csv('EDA/flow_corridors_summary.csv', index=False)
        
        print(f"✅ Summary saved: EDA/flow_corridors_summary.csv")
        
        return summary


def main():
    """Run complete momentum flow corridors analysis"""
    try:
        # Initialize analyzer
        analyzer = MomentumFlowCorridorsAnalyzer()
        
        # Detect flow sequences
        flow_df = analyzer.detect_flow_sequences()
        
        # Engineer corridor features
        corridor_features = analyzer.engineer_corridor_features()
        
        # Optimize clustering
        results, best_k = analyzer.optimize_corridor_clustering()
        
        # Analyze predictability
        predictions_df = analyzer.analyze_flow_predictability()
        
        # Generate summary
        summary = analyzer.generate_summary()
        
        print(f"\n🏆 MOMENTUM FLOW CORRIDORS ANALYSIS COMPLETE!")
        print("=" * 60)
        print(f"✅ Flow sequences: {len(flow_df):,}")
        print(f"✅ Corridor features: {len(corridor_features)}")
        print(f"✅ Optimal K: {best_k['k']} (Silhouette: {best_k['silhouette_score']:.3f})")
        if summary['team_corridor_combinations'] > 0:
            print(f"✅ Flow predictability: {summary['avg_flow_predictability']:.3f}")
        print("=" * 60)
        
        return analyzer, summary
        
    except Exception as e:
        print(f"❌ Error in flow corridors analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    analyzer, summary = main() 