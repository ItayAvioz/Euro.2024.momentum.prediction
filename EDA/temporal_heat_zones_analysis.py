#!/usr/bin/env python3
"""
Temporal Heat Zones Evolution Analysis - Idea 3A
Map pitch into zones and track momentum evolution by location and time
Test K=3-10 clustering and assess location-temporal predictability
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import warnings
warnings.filterwarnings('ignore')

class TemporalHeatZonesAnalyzer:
    """Analyze temporal heat zones evolution across Euro 2024"""
    
    def __init__(self, dataset_path='Data/euro_2024_complete_dataset.csv'):
        print("🔥 TEMPORAL HEAT ZONES EVOLUTION ANALYSIS - IDEA 3A")
        print("=" * 70)
        
        # Load dataset
        self.df = pd.read_csv(dataset_path, low_memory=False)
        print(f"📊 Dataset: {len(self.df):,} events")
        
        # Extract key fields
        self.df['event_type'] = self.df['type'].apply(lambda x: eval(x)['name'] if pd.notna(x) and isinstance(x, str) else 'Unknown')
        self.df['team_name'] = self.df['team'].apply(lambda x: eval(x)['name'] if pd.notna(x) and isinstance(x, str) else 'Unknown')
        
        # Extract location coordinates
        self.extract_coordinates()
        
        print(f"🎮 Matches: {self.df['match_id'].nunique()} matches")
        print(f"📍 Events with location: {self.df['x_coord'].notna().sum():,}")
        
    def extract_coordinates(self):
        """Extract x,y coordinates from location field"""
        print("\n🗺️ EXTRACTING PITCH COORDINATES")
        print("-" * 35)
        
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
        
        print(f"✅ Normalized coordinates to 120x80 pitch")
        
    def create_pitch_grid(self):
        """Create 20x15 pitch grid (300 zones)"""
        print("\n🏟️ CREATING PITCH GRID (20x15 = 300 zones)")
        print("-" * 45)
        
        # Define grid parameters
        self.grid_width = 20  # zones across width
        self.grid_length = 15  # zones across length
        self.zone_width = 120 / self.grid_width  # 6 meters per zone
        self.zone_length = 80 / self.grid_length  # 5.33 meters per zone
        
        # Assign zone IDs to each event
        zones_assigned = 0
        
        for idx, row in self.df.iterrows():
            x_norm = row['x_norm']
            y_norm = row['y_norm']
            
            # Calculate zone indices
            zone_x = int(min(x_norm // self.zone_width, self.grid_width - 1))
            zone_y = int(min(y_norm // self.zone_length, self.grid_length - 1))
            
            # Zone ID: zone_x + zone_y * grid_width
            zone_id = zone_x + zone_y * self.grid_width
            
            self.df.at[idx, 'zone_id'] = zone_id
            self.df.at[idx, 'zone_x'] = zone_x
            self.df.at[idx, 'zone_y'] = zone_y
            
            # Zone characteristics
            self.df.at[idx, 'goal_distance'] = self.calculate_goal_distance(x_norm, y_norm)
            self.df.at[idx, 'zone_type'] = self.classify_zone_type(x_norm, y_norm)
            
            zones_assigned += 1
        
        print(f"✅ Assigned {zones_assigned:,} events to {self.grid_width}x{self.grid_length} grid")
        print(f"   Zone size: {self.zone_width:.1f}m x {self.zone_length:.1f}m")
        print(f"   Total zones: {self.grid_width * self.grid_length}")
        
    def calculate_goal_distance(self, x, y):
        """Calculate distance to goal"""
        # Assuming goal is at x=120, y=40 (center of goal line)
        goal_x, goal_y = 120, 40
        distance = np.sqrt((x - goal_x)**2 + (y - goal_y)**2)
        return distance
    
    def classify_zone_type(self, x, y):
        """Classify zone type based on location"""
        if x <= 40:
            return 'Defensive Third'
        elif x <= 80:
            return 'Middle Third'
        else:
            return 'Attacking Third'
    
    def extract_temporal_zone_features(self):
        """Extract temporal momentum features by zone and time"""
        print("\n⏱️ EXTRACTING TEMPORAL ZONE FEATURES")
        print("-" * 40)
        
        zone_temporal_data = []
        matches_processed = 0
        
        for match_id in self.df['match_id'].unique():
            matches_processed += 1
            if matches_processed % 10 == 0:
                print(f"   Processing match {matches_processed}/{self.df['match_id'].nunique()}...")
            
            match_df = self.df[self.df['match_id'] == match_id]
            teams = match_df['team_name'].unique()
            
            if len(teams) < 2:
                continue
                
            team_a, team_b = teams[0], teams[1]
            
            # Process each 5-minute time window
            for time_window_start in range(0, 125, 5):  # 5-minute windows
                time_window_end = time_window_start + 5
                
                window_events = match_df[
                    (match_df['minute'] >= time_window_start) & 
                    (match_df['minute'] < time_window_end)
                ]
                
                if len(window_events) == 0:
                    continue
                
                # Process each zone
                for zone_id in range(self.grid_width * self.grid_length):
                    zone_features = self.calculate_zone_temporal_features(
                        window_events, zone_id, team_a, team_b, match_id, 
                        time_window_start, time_window_end
                    )
                    
                    if zone_features:
                        zone_temporal_data.append(zone_features)
        
        self.zone_temporal_df = pd.DataFrame(zone_temporal_data)
        print(f"✅ Extracted {len(self.zone_temporal_df):,} zone-time observations")
        
        return self.zone_temporal_df
    
    def calculate_zone_temporal_features(self, window_events, zone_id, team_a, team_b, match_id, time_start, time_end):
        """Calculate momentum features for specific zone in time window"""
        try:
            zone_events = window_events[window_events['zone_id'] == zone_id]
            
            if len(zone_events) == 0:
                return None  # Skip empty zones
            
            # Team-specific zone events
            team_a_events = zone_events[zone_events['team_name'] == team_a]
            team_b_events = zone_events[zone_events['team_name'] == team_b]
            
            # Zone momentum metrics
            zone_activity = len(zone_events)
            team_a_activity = len(team_a_events)
            team_b_activity = len(team_b_events)
            
            # Zone momentum balance
            activity_balance = team_a_activity - team_b_activity
            
            # Zone intensity (weighted by event importance)
            intensity_weights = {
                'Pass': 1.0, 'Pressure': 2.0, 'Carry': 1.5, 'Duel': 2.5,
                'Ball Recovery': 2.0, 'Shot': 3.0, 'Dribble': 2.0,
                'Clearance': 1.5, 'Interception': 2.0, 'Block': 2.5
            }
            
            zone_intensity = 0
            for _, event in zone_events.iterrows():
                event_type = event.get('event_type', 'Unknown')
                weight = intensity_weights.get(event_type, 1.0)
                zone_intensity += weight
            
            # Zone characteristics from first event (representative)
            sample_event = zone_events.iloc[0]
            zone_x = sample_event.get('zone_x', 0)
            zone_y = sample_event.get('zone_y', 0)
            goal_distance = sample_event.get('goal_distance', 0)
            zone_type = sample_event.get('zone_type', 'Unknown')
            
            return {
                'match_id': match_id,
                'zone_id': zone_id,
                'zone_x': zone_x,
                'zone_y': zone_y,
                'time_window_start': time_start,
                'time_window_end': time_end,
                'time_window_mid': (time_start + time_end) / 2,
                'team_a': team_a,
                'team_b': team_b,
                'zone_activity': zone_activity,
                'team_a_activity': team_a_activity,
                'team_b_activity': team_b_activity,
                'activity_balance': activity_balance,
                'zone_intensity': zone_intensity,
                'goal_distance': goal_distance,
                'zone_type': zone_type,
                'game_phase': 'early' if time_start <= 30 else 'mid' if time_start <= 60 else 'late',
                'first_half': 1 if time_end <= 45 else 0,
                'second_half': 1 if time_start > 45 else 0
            }
            
        except Exception as e:
            return None
    
    def engineer_heat_evolution_features(self):
        """Engineer features for heat evolution analysis"""
        print("\n🔧 ENGINEERING HEAT EVOLUTION FEATURES")
        print("-" * 45)
        
        # Add derived features
        self.zone_temporal_df['heat_density'] = self.zone_temporal_df['zone_intensity'] / (self.zone_temporal_df['zone_activity'] + 1)
        self.zone_temporal_df['dominance_strength'] = self.zone_temporal_df['activity_balance'].abs()
        self.zone_temporal_df['zone_importance'] = 100 / (self.zone_temporal_df['goal_distance'] + 1)  # Closer to goal = more important
        
        # Temporal features
        self.zone_temporal_df['time_factor'] = self.zone_temporal_df['time_window_mid'] / 90  # Normalized time (0-1+)
        
        # Zone position features
        self.zone_temporal_df['central_position'] = 1 - (abs(self.zone_temporal_df['zone_y'] - 7.5) / 7.5)  # Central = 1, wide = 0
        self.zone_temporal_df['attacking_position'] = self.zone_temporal_df['zone_x'] / (self.grid_width - 1)  # Defensive = 0, attacking = 1
        
        # Heat evolution tracking
        heat_evolution_features = []
        
        for zone_id in self.zone_temporal_df['zone_id'].unique():
            zone_data = self.zone_temporal_df[self.zone_temporal_df['zone_id'] == zone_id].sort_values('time_window_mid')
            
            if len(zone_data) < 3:  # Need at least 3 time points
                continue
            
            # Calculate heat trends over time
            intensity_values = zone_data['zone_intensity'].values
            time_values = zone_data['time_window_mid'].values
            
            if len(intensity_values) > 1:
                # Heat trend (slope)
                heat_trend = np.polyfit(time_values, intensity_values, 1)[0]
                
                # Heat volatility (standard deviation)
                heat_volatility = np.std(intensity_values)
                
                # Peak timing
                peak_time = time_values[np.argmax(intensity_values)]
                
                # Heat persistence (autocorrelation)
                heat_series = pd.Series(intensity_values)
                heat_persistence = heat_series.autocorr(lag=1) if len(heat_series) > 1 else 0
                heat_persistence = heat_persistence if not np.isnan(heat_persistence) else 0
                
                for idx in zone_data.index:
                    self.zone_temporal_df.at[idx, 'heat_trend'] = heat_trend
                    self.zone_temporal_df.at[idx, 'heat_volatility'] = heat_volatility
                    self.zone_temporal_df.at[idx, 'heat_peak_time'] = peak_time
                    self.zone_temporal_df.at[idx, 'heat_persistence'] = heat_persistence
        
        # Fill missing evolution features
        evolution_features = ['heat_trend', 'heat_volatility', 'heat_peak_time', 'heat_persistence']
        for feature in evolution_features:
            if feature not in self.zone_temporal_df.columns:
                self.zone_temporal_df[feature] = 0
            else:
                self.zone_temporal_df[feature] = self.zone_temporal_df[feature].fillna(0)
        
        print(f"✅ Engineered heat evolution features")
        print(f"   Total features: {len(self.zone_temporal_df.columns)}")
        
        return self.zone_temporal_df
    
    def optimize_heat_clustering(self):
        """Test K=3-10 for optimal heat zone clustering"""
        print("\n📊 OPTIMIZING HEAT ZONE CLUSTERING (K=3-10)")
        print("-" * 50)
        
        # Select features for clustering
        clustering_features = [
            'zone_intensity', 'activity_balance', 'heat_density', 'dominance_strength',
            'zone_importance', 'time_factor', 'central_position', 'attacking_position',
            'heat_trend', 'heat_volatility', 'heat_persistence'
        ]
        
        # Filter to active zones (with significant activity)
        active_zones = self.zone_temporal_df[self.zone_temporal_df['zone_activity'] >= 2].copy()
        
        if len(active_zones) < 50:
            print("⚠️  Insufficient active zones, using all zones")
            active_zones = self.zone_temporal_df.copy()
        
        X = active_zones[clustering_features].fillna(0)
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
            active_zones[f'cluster_k{k}'] = clusters
            
            # Analyze cluster characteristics
            cluster_analysis = {}
            for cluster_id in range(k):
                cluster_data = active_zones[active_zones[f'cluster_k{k}'] == cluster_id]
                
                cluster_analysis[cluster_id] = {
                    'size': len(cluster_data),
                    'avg_intensity': cluster_data['zone_intensity'].mean(),
                    'avg_balance': cluster_data['activity_balance'].mean(),
                    'avg_time': cluster_data['time_window_mid'].mean(),
                    'avg_goal_distance': cluster_data['goal_distance'].mean(),
                    'zone_type_distribution': cluster_data['zone_type'].value_counts().to_dict()
                }
            
            results.append({
                'k': k,
                'silhouette_score': silhouette,
                'inertia': inertia,
                'cluster_analysis': cluster_analysis
            })
            
            print(f"     Silhouette: {silhouette:.3f}")
        
        self.clustering_results = results
        self.active_zones_df = active_zones
        
        # Find optimal K
        best_k = max(results, key=lambda x: x['silhouette_score'])
        print(f"\n🏆 OPTIMAL K: {best_k['k']} (Silhouette: {best_k['silhouette_score']:.3f})")
        
        return results, best_k
    
    def analyze_heat_predictability(self):
        """Analyze heat zone predictability"""
        print("\n🔮 ANALYZING HEAT ZONE PREDICTABILITY")
        print("-" * 40)
        
        predictions = []
        
        # For each zone, predict future heat based on current patterns
        for zone_id in self.zone_temporal_df['zone_id'].unique():
            zone_data = self.zone_temporal_df[self.zone_temporal_df['zone_id'] == zone_id].sort_values('time_window_mid')
            
            if len(zone_data) < 4:  # Need at least 4 time windows
                continue
            
            # Use first 75% of data to predict last 25%
            split_point = int(len(zone_data) * 0.75)
            train_data = zone_data.iloc[:split_point]
            test_data = zone_data.iloc[split_point:]
            
            if len(train_data) < 2 or len(test_data) < 1:
                continue
            
            # Calculate prediction metrics
            train_intensity = train_data['zone_intensity'].values
            test_intensity = test_data['zone_intensity'].values
            
            # Trend-based prediction
            if len(train_intensity) > 1:
                trend = np.polyfit(range(len(train_intensity)), train_intensity, 1)[0]
                last_value = train_intensity[-1]
                
                # Predict next values
                predictions_list = []
                for i in range(len(test_intensity)):
                    predicted_value = last_value + trend * (i + 1)
                    predictions_list.append(predicted_value)
                
                # Calculate prediction accuracy
                if len(predictions_list) > 0 and len(test_intensity) > 0:
                    predictions_array = np.array(predictions_list)
                    
                    # Mean Absolute Error
                    mae = np.mean(np.abs(predictions_array - test_intensity))
                    
                    # Relative accuracy
                    mean_actual = np.mean(test_intensity)
                    relative_accuracy = 1 - (mae / (mean_actual + 1))  # +1 to avoid division by zero
                    relative_accuracy = max(0, relative_accuracy)  # Ensure non-negative
                    
                    predictions.append({
                        'zone_id': zone_id,
                        'zone_x': zone_data.iloc[0]['zone_x'],
                        'zone_y': zone_data.iloc[0]['zone_y'],
                        'goal_distance': zone_data.iloc[0]['goal_distance'],
                        'zone_type': zone_data.iloc[0]['zone_type'],
                        'heat_trend': train_data['heat_trend'].iloc[0] if 'heat_trend' in train_data.columns else trend,
                        'heat_persistence': train_data['heat_persistence'].iloc[0] if 'heat_persistence' in train_data.columns else 0,
                        'prediction_accuracy': relative_accuracy,
                        'mae': mae,
                        'observations': len(zone_data)
                    })
        
        self.predictions_df = pd.DataFrame(predictions)
        
        if len(self.predictions_df) > 0:
            avg_accuracy = self.predictions_df['prediction_accuracy'].mean()
            high_accuracy = (self.predictions_df['prediction_accuracy'] >= 0.6).mean() * 100
            
            print(f"✅ Heat predictability analyzed")
            print(f"   Zones analyzed: {len(self.predictions_df)}")
            print(f"   Average accuracy: {avg_accuracy:.3f}")
            print(f"   High accuracy (≥60%): {high_accuracy:.1f}% of zones")
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
            'total_events': len(self.df),
            'total_zones': self.grid_width * self.grid_length,
            'active_zones': len(self.zone_temporal_df['zone_id'].unique()),
            'zone_time_observations': len(self.zone_temporal_df),
            'optimal_k': best_k['k'],
            'optimal_silhouette': best_k['silhouette_score']
        }
        
        if len(self.predictions_df) > 0:
            summary.update({
                'avg_heat_predictability': self.predictions_df['prediction_accuracy'].mean(),
                'high_predictability_pct': (self.predictions_df['prediction_accuracy'] >= 0.6).mean() * 100,
                'zones_analyzed': len(self.predictions_df)
            })
        else:
            summary.update({
                'avg_heat_predictability': 0,
                'high_predictability_pct': 0,
                'zones_analyzed': 0
            })
        
        # Save summary
        summary_df = pd.DataFrame([summary])
        summary_df.to_csv('EDA/heat_zones_summary.csv', index=False)
        
        print(f"✅ Summary saved: EDA/heat_zones_summary.csv")
        
        return summary


def main():
    """Run complete temporal heat zones analysis"""
    try:
        # Initialize analyzer
        analyzer = TemporalHeatZonesAnalyzer()
        
        # Create pitch grid
        analyzer.create_pitch_grid()
        
        # Extract temporal zone features
        zone_temporal_df = analyzer.extract_temporal_zone_features()
        
        # Engineer heat evolution features
        zone_temporal_df = analyzer.engineer_heat_evolution_features()
        
        # Optimize clustering
        results, best_k = analyzer.optimize_heat_clustering()
        
        # Analyze predictability
        predictions_df = analyzer.analyze_heat_predictability()
        
        # Generate summary
        summary = analyzer.generate_summary()
        
        print(f"\n🏆 TEMPORAL HEAT ZONES ANALYSIS COMPLETE!")
        print("=" * 60)
        print(f"✅ Events analyzed: {len(analyzer.df):,}")
        print(f"✅ Zone-time observations: {len(zone_temporal_df):,}")
        print(f"✅ Active zones: {summary['active_zones']}")
        print(f"✅ Optimal K: {best_k['k']} (Silhouette: {best_k['silhouette_score']:.3f})")
        if summary['zones_analyzed'] > 0:
            print(f"✅ Heat predictability: {summary['avg_heat_predictability']:.3f}")
        print("=" * 60)
        
        return analyzer, summary
        
    except Exception as e:
        print(f"❌ Error in heat zones analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    analyzer, summary = main() 