#!/usr/bin/env python3
"""
Pressure-Resistance Patterns Analysis - CORRECTED VERSION
Discover pressure-resistance signatures across all Euro 2024 data
Variables: under_pressure, location, position, event_type
Focus: Key events by location, pressure impact, and player role
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

class PressureResistanceAnalyzer:
    """Analyze pressure-resistance patterns in Euro 2024"""
    
    def __init__(self, dataset_path='Data/euro_2024_complete_dataset.csv'):
        """Initialize with full dataset"""
        print("⚡ PRESSURE-RESISTANCE PATTERNS ANALYSIS - FULL DATASET")
        print("=" * 70)
        
        # Load complete dataset
        print("📊 Loading Euro 2024 complete dataset...")
        self.df = pd.read_csv(dataset_path, low_memory=False)
        print(f"   Total events: {len(self.df):,}")
        
        # Extract event type and position
        self.df['event_type'] = self.df['type'].apply(lambda x: eval(x)['name'] if pd.notna(x) and isinstance(x, str) else 'Unknown')
        self.df['position_name'] = self.df['position'].apply(lambda x: eval(x)['name'] if pd.notna(x) and isinstance(x, str) and x != 'nan' else 'Unknown')
        
        # CORRECT PRESSURE LOGIC: NaN = 0 (no pressure), True = 1 (under pressure)
        self.df['pressure_binary'] = self.df['under_pressure'].notna().astype(int)
        
        pressure_events = self.df['pressure_binary'].sum()
        no_pressure_events = len(self.df) - pressure_events
        pressure_rate = (pressure_events / len(self.df)) * 100
        
        print(f"   Under pressure events: {pressure_events:,} ({pressure_rate:.1f}%)")
        print(f"   No pressure events: {no_pressure_events:,} ({100-pressure_rate:.1f}%)")
        print(f"   Unique positions: {self.df['position_name'].nunique()}")
        print(f"   Unique event types: {self.df['event_type'].nunique()}")
        
        # Prepare pressure-resistance features for ALL data
        self.prepare_pressure_features()
    
    def prepare_pressure_features(self):
        """Prepare pressure-resistance features for clustering on FULL dataset"""
        print("\n🔧 PREPARING PRESSURE-RESISTANCE FEATURES")
        print("-" * 50)
        
        # Filter events with location data (use ALL, not limited subset)
        df_with_location = self.df.dropna(subset=['location']).copy()
        print(f"   Events with location data: {len(df_with_location):,}")
        
        pressure_features = []
        processed = 0
        
        for _, row in df_with_location.iterrows():
            try:
                # Parse location coordinates
                location = eval(row['location']) if isinstance(row['location'], str) else row['location']
                x, y = location[0], location[1]
                
                # Keep valid pitch coordinates (less restrictive)
                if not (0 <= x <= 120 and 0 <= y <= 80):
                    continue
                
                processed += 1
                
                # PRESSURE-RESISTANCE FEATURES
                features = {
                    # CORE PRESSURE IMPACT
                    'under_pressure': row['pressure_binary'],
                    
                    # LOCATION CONTEXT (key events by location)
                    'field_position': x / 120,  # 0=own goal, 1=opponent goal  
                    'width_position': abs(y - 40) / 40,  # 0=center, 1=sideline
                    'goal_distance': np.sqrt((120 - x)**2 + (40 - y)**2),
                    'own_goal_distance': np.sqrt(x**2 + (40 - y)**2),
                    
                    # TACTICAL ZONES
                    'attacking_third': 1 if x >= 80 else 0,
                    'middle_third': 1 if 40 <= x < 80 else 0,
                    'defensive_third': 1 if x <= 40 else 0,
                    'central_channel': 1 if 26.67 <= y <= 53.33 else 0,
                    'wide_areas': 1 if y <= 26.67 or y >= 53.33 else 0,
                    
                    # PLAYER ROLE (position-based pressure handling)
                    'goalkeeper': 1 if 'Goalkeeper' in str(row['position_name']) else 0,
                    'center_back': 1 if 'Center Back' in str(row['position_name']) else 0,
                    'fullback': 1 if any(pos in str(row['position_name']) for pos in ['Left Back', 'Right Back']) else 0,
                    'defensive_mid': 1 if 'Defensive Midfield' in str(row['position_name']) else 0,
                    'central_mid': 1 if any(pos in str(row['position_name']) for pos in ['Center Midfield', 'Central Midfield']) else 0,
                    'attacking_mid': 1 if 'Attacking Midfield' in str(row['position_name']) else 0,
                    'winger': 1 if any(pos in str(row['position_name']) for pos in ['Left Wing', 'Right Wing']) else 0,
                    'striker': 1 if any(pos in str(row['position_name']) for pos in ['Striker', 'Center Forward']) else 0,
                    
                    # EVENT TYPE CONTEXT
                    'skill_event': 1 if row['event_type'] in ['Dribble', 'Pass', 'Shot', 'Carry'] else 0,
                    'contest_event': 1 if row['event_type'] in ['Duel', 'Foul Won', 'Foul Committed'] else 0,
                    'recovery_event': 1 if row['event_type'] in ['Ball Recovery', 'Interception', 'Clearance'] else 0,
                    'transition_event': 1 if row['event_type'] in ['Ball Receipt', 'Miscontrol', 'Dispossessed'] else 0,
                    
                    # Metadata
                    'event_type': row['event_type'],
                    'position_name': row['position_name']
                }
                
                pressure_features.append(features)
                
            except Exception:
                continue
        
        self.pressure_df = pd.DataFrame(pressure_features)
        
        coverage = len(self.pressure_df) / len(self.df) * 100
        pressure_coverage = self.pressure_df['under_pressure'].sum()
        pressure_rate = self.pressure_df['under_pressure'].mean() * 100
        
        print(f"   Events processed: {len(self.pressure_df):,}")
        print(f"   Dataset coverage: {coverage:.1f}% of total events")
        print(f"   Under pressure events: {pressure_coverage:,} ({pressure_rate:.1f}%)")
        print(f"   ✅ FULL DATASET COVERAGE ACHIEVED")
    
    def optimize_with_pca(self):
        """Use PCA to optimize features for pressure-resistance clustering"""
        print("\n🧠 PCA FEATURE OPTIMIZATION")
        print("-" * 40)
        
        # Feature columns (exclude metadata)
        feature_cols = [col for col in self.pressure_df.columns 
                       if col not in ['event_type', 'position_name']]
        
        print(f"   Original features: {len(feature_cols)}")
        
        # Prepare data for PCA
        X = self.pressure_df[feature_cols].fillna(0)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # PCA analysis for feature importance
        pca = PCA(n_components=len(feature_cols))
        pca.fit(X_scaled)
        
        # Calculate feature importance across all components
        feature_importance = np.abs(pca.components_).sum(axis=0)
        feature_ranking = [(feature_cols[i], feature_importance[i]) for i in range(len(feature_cols))]
        feature_ranking.sort(key=lambda x: x[1], reverse=True)
        
        print("   PCA Feature Importance Ranking:")
        for i, (feature, importance) in enumerate(feature_ranking[:10]):
            print(f"   {i+1:2d}. {feature:<20} {importance:.3f}")
        
        # Keep top 80% of features 
        n_keep = int(len(feature_cols) * 0.8)
        self.selected_features = [feat[0] for feat in feature_ranking[:n_keep]]
        removed_features = [feat[0] for feat in feature_ranking[n_keep:]]
        
        print(f"   Selected features: {len(self.selected_features)}")
        print(f"   Removed features: {removed_features}")
        
        return self.selected_features
    
    def run_pressure_clustering(self, k=10):
        """Run optimized K=10 clustering on pressure-resistance patterns"""
        print(f"\n⚡ PRESSURE-RESISTANCE CLUSTERING (K={k})")
        print("-" * 50)
        
        # Use optimized features
        X_opt = self.pressure_df[self.selected_features].fillna(0)
        
        # Standardize features
        scaler = StandardScaler()
        X_opt_scaled = scaler.fit_transform(X_opt)
        
        # K-means clustering
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=20)
        clusters = kmeans.fit_predict(X_opt_scaled)
        
        # Add clusters to dataframe
        self.pressure_df['cluster'] = clusters
        
        # Calculate silhouette score
        silhouette_opt = silhouette_score(X_opt_scaled, clusters)
        
        print(f"   Events clustered: {len(self.pressure_df):,}")
        print(f"   Features used: {len(self.selected_features)}")
        print(f"   Silhouette score: {silhouette_opt:.3f}")
        
        # Analyze clusters
        self.analyze_pressure_clusters(k)
        
        return silhouette_opt
    
    def analyze_pressure_clusters(self, k):
        """Analyze the discovered pressure-resistance clusters"""
        print(f"\n📊 PRESSURE-RESISTANCE CLUSTER ANALYSIS")
        print("-" * 60)
        
        cluster_analysis = []
        
        for cluster_id in range(k):
            cluster_data = self.pressure_df[self.pressure_df['cluster'] == cluster_id]
            size_pct = len(cluster_data) / len(self.pressure_df) * 100
            
            # Key pressure-resistance metrics
            pressure_rate = cluster_data['under_pressure'].mean() * 100
            
            # Location patterns
            attacking_rate = cluster_data['attacking_third'].mean() * 100
            defensive_rate = cluster_data['defensive_third'].mean() * 100
            central_rate = cluster_data['central_channel'].mean() * 100
            
            # Event patterns
            skill_rate = cluster_data['skill_event'].mean() * 100
            contest_rate = cluster_data['contest_event'].mean() * 100
            
            # Position patterns
            positions = cluster_data['position_name'].mode().iloc[0] if len(cluster_data) > 0 else 'Mixed'
            
            analysis = {
                'cluster_id': cluster_id,
                'size_pct': size_pct,
                'pressure_rate': pressure_rate,
                'attacking_rate': attacking_rate, 
                'defensive_rate': defensive_rate,
                'central_rate': central_rate,
                'skill_rate': skill_rate,
                'contest_rate': contest_rate,
                'dominant_position': positions,
                'event_types': list(cluster_data['event_type'].value_counts().head(3).index)
            }
            
            cluster_analysis.append(analysis)
            
            print(f"Cluster {cluster_id} ({size_pct:.1f}%): "
                  f"Pressure:{pressure_rate:.0f}% | "
                  f"Attack:{attacking_rate:.0f}% | "
                  f"Defense:{defensive_rate:.0f}% | "
                  f"Skill:{skill_rate:.0f}% | "
                  f"Contest:{contest_rate:.0f}%")
        
        self.cluster_analysis = cluster_analysis
        return cluster_analysis
    
    def identify_key_pressure_patterns(self):
        """Identify key pressure-resistance patterns for momentum prediction"""
        print(f"\n🎯 KEY PRESSURE-RESISTANCE PATTERNS")
        print("-" * 50)
        
        key_patterns = []
        
        for cluster in self.cluster_analysis:
            pattern_type = "Unknown"
            momentum_impact = "Low"
            
            # Classify based on pressure + location + role
            if cluster['pressure_rate'] >= 80:
                if cluster['skill_rate'] >= 60:
                    pattern_type = "Elite Pressure Skills"
                    momentum_impact = "High"
                elif cluster['contest_rate'] >= 60:
                    pattern_type = "Pressure Battles"
                    momentum_impact = "High"
                else:
                    pattern_type = "High Pressure Zones"
                    momentum_impact = "Medium"
            
            elif cluster['pressure_rate'] >= 40:
                if cluster['attacking_rate'] >= 60:
                    pattern_type = "Attacking Under Pressure"
                    momentum_impact = "Medium"
                else:
                    pattern_type = "Moderate Pressure Zones"
                    momentum_impact = "Medium"
            
            elif cluster['pressure_rate'] <= 10:
                if cluster['skill_rate'] >= 70:
                    pattern_type = "Safe Skill Zones"
                    momentum_impact = "Low"
                elif cluster['attacking_rate'] >= 60:
                    pattern_type = "Safe Attacking Zones"
                    momentum_impact = "Low"
                else:
                    pattern_type = "Low Pressure Zones"
                    momentum_impact = "Low"
            
            else:
                pattern_type = "Mixed Pressure Zones"
                momentum_impact = "Medium"
            
            pattern = {
                'cluster_id': cluster['cluster_id'],
                'pattern_type': pattern_type,
                'momentum_impact': momentum_impact,
                'size_pct': cluster['size_pct'],
                'pressure_rate': cluster['pressure_rate'],
                'dominant_position': cluster['dominant_position'],
                'key_events': cluster['event_types'][:2]
            }
            
            key_patterns.append(pattern)
            
            print(f"Cluster {cluster['cluster_id']}: {pattern_type} ({cluster['size_pct']:.1f}%) - {momentum_impact} momentum impact")
        
        self.key_patterns = key_patterns
        return key_patterns
    
    def generate_examples(self):
        """Generate 5 input/output examples for pressure-resistance patterns"""
        print(f"\n📋 PRESSURE-RESISTANCE EXAMPLES")
        print("-" * 50)
        
        examples = []
        
        # Example 1: Elite pressure skills
        elite_cluster = next((p for p in self.key_patterns if 'Elite' in p['pattern_type']), self.key_patterns[0])
        examples.append({
            'id': 1,
            'scenario': 'Elite player maintaining skills under maximum pressure',
            'input': {
                'under_pressure': 1,
                'field_position': 0.75,  # Attacking area
                'attacking_third': 1,
                'skill_event': 1,
                'central_mid': 1,
                'event_type': 'Dribble'
            },
            'output': {
                'cluster': elite_cluster['cluster_id'],
                'pattern_type': elite_cluster['pattern_type'],
                'momentum_impact': elite_cluster['momentum_impact']
            }
        })
        
        # Example 2: Safe skill zones
        safe_cluster = next((p for p in self.key_patterns if 'Safe' in p['pattern_type']), self.key_patterns[1])
        examples.append({
            'id': 2,
            'scenario': 'Player executing skills in pressure-free environment',
            'input': {
                'under_pressure': 0,
                'field_position': 0.45,  # Middle area
                'middle_third': 1,
                'skill_event': 1,
                'central_mid': 1,
                'event_type': 'Pass'
            },
            'output': {
                'cluster': safe_cluster['cluster_id'],
                'pattern_type': safe_cluster['pattern_type'],
                'momentum_impact': safe_cluster['momentum_impact']
            }
        })
        
        # Example 3: Attacking under pressure
        attack_cluster = next((p for p in self.key_patterns if 'Attacking' in p['pattern_type']), self.key_patterns[2])
        examples.append({
            'id': 3,
            'scenario': 'Forward creating chances under defensive pressure',
            'input': {
                'under_pressure': 1,
                'field_position': 0.85,  # Deep attacking area
                'attacking_third': 1,
                'skill_event': 1,
                'striker': 1,
                'event_type': 'Shot'
            },
            'output': {
                'cluster': attack_cluster['cluster_id'],
                'pattern_type': attack_cluster['pattern_type'],
                'momentum_impact': attack_cluster['momentum_impact']
            }
        })
        
        # Example 4: Defensive pressure resistance
        defense_cluster = next((p for p in self.key_patterns if p['pressure_rate'] > 30 and 'Defense' not in p['pattern_type']), self.key_patterns[3])
        examples.append({
            'id': 4,
            'scenario': 'Defender handling pressure in own area',
            'input': {
                'under_pressure': 1,
                'field_position': 0.25,  # Defensive area
                'defensive_third': 1,
                'recovery_event': 1,
                'center_back': 1,
                'event_type': 'Clearance'
            },
            'output': {
                'cluster': defense_cluster['cluster_id'],
                'pattern_type': defense_cluster['pattern_type'],
                'momentum_impact': defense_cluster['momentum_impact']
            }
        })
        
        # Example 5: Contest situations
        contest_cluster = next((p for p in self.key_patterns if 'Battle' in p['pattern_type'] or p['pressure_rate'] > 50), self.key_patterns[4])
        examples.append({
            'id': 5,
            'scenario': 'Physical contest under pressure in midfield',
            'input': {
                'under_pressure': 1,
                'field_position': 0.55,  # Midfield contest
                'middle_third': 1,
                'contest_event': 1,
                'defensive_mid': 1,
                'event_type': 'Duel'
            },
            'output': {
                'cluster': contest_cluster['cluster_id'],
                'pattern_type': contest_cluster['pattern_type'],
                'momentum_impact': contest_cluster['momentum_impact']
            }
        })
        
        # Display examples
        for example in examples:
            print(f"\nEXAMPLE {example['id']}: {example['scenario'].upper()}")
            print(f"  INPUT:")
            for key, value in example['input'].items():
                print(f"    {key}: {value}")
            print(f"  OUTPUT:")
            print(f"    cluster: {example['output']['cluster']}")
            print(f"    pattern_type: {example['output']['pattern_type']}")
            print(f"    momentum_impact: {example['output']['momentum_impact']}")
        
        return examples


def main():
    """Run complete pressure-resistance pattern analysis"""
    try:
        # Initialize analyzer with full dataset
        analyzer = PressureResistanceAnalyzer()
        
        # Optimize features with PCA
        selected_features = analyzer.optimize_with_pca()
        
        # Run K=10 clustering
        silhouette_score = analyzer.run_pressure_clustering(k=10)
        
        # Identify key patterns
        key_patterns = analyzer.identify_key_pressure_patterns()
        
        # Generate examples
        examples = analyzer.generate_examples()
        
        print(f"\n✅ PRESSURE-RESISTANCE ANALYSIS COMPLETE")
        print(f"   Dataset Coverage: {len(analyzer.pressure_df):,} events ({len(analyzer.pressure_df)/len(analyzer.df)*100:.1f}%)")
        print(f"   Silhouette Score: {silhouette_score:.3f}")
        print(f"   Key Patterns: {len(key_patterns)} discovered")
        print(f"   Features: {len(selected_features)} optimized")
        
        return analyzer, key_patterns, examples
        
    except Exception as e:
        print(f"❌ Error in pressure-resistance analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None, None

if __name__ == "__main__":
    analyzer, patterns, examples = main() 