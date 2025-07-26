import pandas as pd
import numpy as np
import ast
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold, GridSearchCV
from sklearn.metrics import classification_report, silhouette_score
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

class PassCarryMomentumAnalyzer:
    def __init__(self, data_path):
        self.data_path = data_path
        self.df = None
        self.pass_features = None
        self.carry_features = None
        self.results = {}
        
    def load_and_preprocess_data(self):
        """Load and preprocess the Euro 2024 events data"""
        print("🔄 Loading Euro 2024 events data...")
        self.df = pd.read_csv(self.data_path, low_memory=False)
        
        # Parse JSON-like columns
        self.df = self._parse_json_columns()
        
        # Filter for Pass and Carry events only
        self.df = self.df[self.df['event_type'].isin(['Pass', 'Carry'])].copy()
        
        print(f"✅ Loaded {len(self.df):,} Pass and Carry events")
        print(f"   - Pass events: {len(self.df[self.df['event_type'] == 'Pass']):,}")
        print(f"   - Carry events: {len(self.df[self.df['event_type'] == 'Carry']):,}")
        
        return self
    
    def _parse_json_columns(self):
        """Parse JSON-like string columns into structured data"""
        
        def safe_parse(x):
            if pd.isna(x) or x == '' or x == 'nan':
                return {}
            try:
                return ast.literal_eval(x) if isinstance(x, str) else x
            except:
                return {}
        
        # Parse key columns
        json_columns = ['type', 'possession_team', 'play_pattern', 'team', 'player', 'position', 'pass', 'carry']
        
        for col in json_columns:
            if col in self.df.columns:
                print(f"   Parsing {col}...")
                parsed_data = self.df[col].apply(safe_parse)
                
                # Extract ID and name if available
                if col == 'type':
                    self.df['type_id'] = parsed_data.apply(lambda x: x.get('id', None))
                    self.df['type_name'] = parsed_data.apply(lambda x: x.get('name', None))
                elif col == 'play_pattern':
                    self.df['play_pattern_id'] = parsed_data.apply(lambda x: x.get('id', None))
                    self.df['play_pattern_name'] = parsed_data.apply(lambda x: x.get('name', None))
                elif col == 'player':
                    self.df['player_id'] = parsed_data.apply(lambda x: x.get('id', None))
                    self.df['player_name'] = parsed_data.apply(lambda x: x.get('name', None))
                elif col == 'position':
                    self.df['position_id'] = parsed_data.apply(lambda x: x.get('id', None))
                    self.df['position_name'] = parsed_data.apply(lambda x: x.get('name', None))
                elif col == 'pass':
                    # Extract pass details
                    self.df['pass_length'] = parsed_data.apply(lambda x: x.get('length', None))
                    self.df['pass_angle'] = parsed_data.apply(lambda x: x.get('angle', None))
                    
                    # Parse recipient
                    recipient = parsed_data.apply(lambda x: x.get('recipient', {}))
                    self.df['recipient_id'] = recipient.apply(lambda x: x.get('id', None) if isinstance(x, dict) else None)
                    
                    # Parse height
                    height = parsed_data.apply(lambda x: x.get('height', {}))
                    self.df['pass_height_id'] = height.apply(lambda x: x.get('id', None) if isinstance(x, dict) else None)
                    
                    # Parse body part
                    body_part = parsed_data.apply(lambda x: x.get('body_part', {}))
                    self.df['body_part_id'] = body_part.apply(lambda x: x.get('id', None) if isinstance(x, dict) else None)
                    
                    # Parse outcome
                    outcome = parsed_data.apply(lambda x: x.get('outcome', {}))
                    self.df['pass_outcome_id'] = outcome.apply(lambda x: x.get('id', None) if isinstance(x, dict) else None)
                    
                    # Parse end location
                    end_location = parsed_data.apply(lambda x: x.get('end_location', []))
                    self.df['pass_end_x'] = end_location.apply(lambda x: x[0] if isinstance(x, list) and len(x) >= 2 else None)
                    self.df['pass_end_y'] = end_location.apply(lambda x: x[1] if isinstance(x, list) and len(x) >= 2 else None)
                    
                elif col == 'carry':
                    # Parse carry end location
                    end_location = parsed_data.apply(lambda x: x.get('end_location', []))
                    self.df['carry_end_x'] = end_location.apply(lambda x: x[0] if isinstance(x, list) and len(x) >= 2 else None)
                    self.df['carry_end_y'] = end_location.apply(lambda x: x[1] if isinstance(x, list) and len(x) >= 2 else None)
        
        # Parse location coordinates
        if 'location' in self.df.columns:
            location_data = self.df['location'].apply(safe_parse)
            # Assuming location is a list [x, y]
            self.df['start_x'] = self.df['location'].apply(lambda x: eval(x)[0] if isinstance(x, str) and x.startswith('[') else None)
            self.df['start_y'] = self.df['location'].apply(lambda x: eval(x)[1] if isinstance(x, str) and x.startswith('[') else None)
        
        # Parse related events count
        if 'related_events' in self.df.columns:
            self.df['related_events_count'] = self.df['related_events'].apply(
                lambda x: len(ast.literal_eval(x)) if pd.notna(x) and x != '' and x != 'nan' else 0
            )
        
        return self.df
    
    def create_pass_features(self):
        """Create comprehensive features for Pass events"""
        print("🔧 Creating Pass features...")
        
        pass_df = self.df[self.df['event_type'] == 'Pass'].copy()
        
        # Core features
        features = pass_df[[
            'play_pattern_id', 'period', 'minute', 'player_id', 'position_id',
            'recipient_id', 'pass_height_id', 'body_part_id', 'pass_outcome_id',
            'pass_length', 'pass_angle', 'start_x', 'start_y', 'pass_end_x', 'pass_end_y',
            'related_events_count'
        ]].copy()
        
        # Derived features
        features['forward_progress'] = features['pass_end_x'] - features['start_x']
        features['lateral_movement'] = abs(features['pass_end_y'] - features['start_y'])
        
        # Field zones (1=defensive, 2=middle, 3=attacking)
        features['field_zone_start'] = pd.cut(features['start_x'], bins=[0, 40, 80, 120], labels=[1, 2, 3])
        features['field_zone_end'] = pd.cut(features['pass_end_x'], bins=[0, 40, 80, 120], labels=[1, 2, 3])
        features['zone_progression'] = features['field_zone_end'].astype(float) - features['field_zone_start'].astype(float)
        
        # Pass success (no outcome = success, outcome = failure)
        features['pass_success'] = features['pass_outcome_id'].isna().astype(int)
        
        # Under pressure flag
        features['under_pressure'] = pass_df['under_pressure'].fillna(0).astype(int)
        
        # Game phase
        features['game_phase'] = pd.cut(features['minute'], 
                                      bins=[0, 15, 30, 45, 60, 75, 120], 
                                      labels=[1, 2, 3, 4, 5, 6])
        
        # Fill missing values
        numeric_cols = ['play_pattern_id', 'pass_height_id', 'body_part_id', 'pass_length', 'pass_angle', 'related_events_count']
        for col in numeric_cols:
            features[col] = features[col].fillna(features[col].median())
        
        features = features.fillna(0)
        
        self.pass_features = features
        print(f"✅ Created {len(features)} Pass events with {len(features.columns)} features")
        
        return features
    
    def create_carry_features(self):
        """Create comprehensive features for Carry events"""
        print("🔧 Creating Carry features...")
        
        carry_df = self.df[self.df['event_type'] == 'Carry'].copy()
        
        # Core features
        features = carry_df[[
            'play_pattern_id', 'period', 'minute', 'player_id', 'position_id',
            'start_x', 'start_y', 'carry_end_x', 'carry_end_y', 'duration',
            'related_events_count'
        ]].copy()
        
        # Derived features
        features['carry_distance'] = np.sqrt(
            (features['carry_end_x'] - features['start_x'])**2 + 
            (features['carry_end_y'] - features['start_y'])**2
        )
        features['forward_progress'] = features['carry_end_x'] - features['start_x']
        features['lateral_movement'] = abs(features['carry_end_y'] - features['start_y'])
        
        # Carry speed (distance per second)
        features['carry_speed'] = features['carry_distance'] / (features['duration'] + 0.1)  # Avoid division by zero
        
        # Field zones
        features['field_zone_start'] = pd.cut(features['start_x'], bins=[0, 40, 80, 120], labels=[1, 2, 3])
        features['field_zone_end'] = pd.cut(features['carry_end_x'], bins=[0, 40, 80, 120], labels=[1, 2, 3])
        features['zone_progression'] = features['field_zone_end'].astype(float) - features['field_zone_start'].astype(float)
        
        # Under pressure flag
        features['under_pressure'] = carry_df['under_pressure'].fillna(0).astype(int)
        
        # Game phase
        features['game_phase'] = pd.cut(features['minute'], 
                                      bins=[0, 15, 30, 45, 60, 75, 120], 
                                      labels=[1, 2, 3, 4, 5, 6])
        
        # Decision speed categories
        features['decision_speed'] = pd.cut(features['duration'], 
                                          bins=[0, 1, 3, 6, 100], 
                                          labels=['instant', 'quick', 'normal', 'slow'])
        
        # Fill missing values
        numeric_cols = ['play_pattern_id', 'duration', 'related_events_count']
        for col in numeric_cols:
            features[col] = features[col].fillna(features[col].median())
        
        features = features.fillna(0)
        
        self.carry_features = features
        print(f"✅ Created {len(features)} Carry events with {len(features.columns)} features")
        
        return features
    
    def unsupervised_analysis(self, event_type="Pass", n_iterations=3):
        """Run unsupervised pattern discovery"""
        print(f"\n🔍 UNSUPERVISED PATTERN DISCOVERY - {event_type}")
        print("=" * 60)
        
        features_df = self.pass_features if event_type == "Pass" else self.carry_features
        
        # Select numeric features for clustering
        numeric_features = features_df.select_dtypes(include=[np.number]).columns.tolist()
        X = features_df[numeric_features].copy()
        
        # Remove any infinite or extremely large values
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(X.median())
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        best_results = {}
        
        # Try different clustering methods
        clustering_methods = {
            'KMeans_5': KMeans(n_clusters=5, random_state=42, n_init=10),
            'KMeans_7': KMeans(n_clusters=7, random_state=42, n_init=10),
            'KMeans_10': KMeans(n_clusters=10, random_state=42, n_init=10),
        }
        
        for iteration in range(n_iterations):
            print(f"\n--- Iteration {iteration + 1} ---")
            
            for method_name, method in clustering_methods.items():
                try:
                    clusters = method.fit_predict(X_scaled)
                    silhouette = silhouette_score(X_scaled, clusters)
                    
                    if method_name not in best_results or silhouette > best_results[method_name]['silhouette']:
                        best_results[method_name] = {
                            'clusters': clusters,
                            'silhouette': silhouette,
                            'method': method,
                            'features': numeric_features,
                            'scaler': scaler
                        }
                    
                    print(f"{method_name}: Silhouette Score = {silhouette:.3f}")
                
                except Exception as e:
                    print(f"{method_name}: Error - {str(e)}")
        
        # Analyze best results
        best_method = max(best_results.keys(), key=lambda k: best_results[k]['silhouette'])
        print(f"\n🏆 Best Method: {best_method} (Silhouette: {best_results[best_method]['silhouette']:.3f})")
        
        # Analyze clusters
        self._analyze_clusters(features_df, best_results[best_method]['clusters'], event_type, best_method)
        
        self.results[f'{event_type}_unsupervised'] = best_results[best_method]
        
        return best_results[best_method]
    
    def _analyze_clusters(self, features_df, clusters, event_type, method_name):
        """Analyze cluster characteristics"""
        print(f"\n📊 CLUSTER ANALYSIS - {event_type} ({method_name})")
        print("-" * 50)
        
        df_with_clusters = features_df.copy()
        df_with_clusters['cluster'] = clusters
        
        cluster_summary = []
        
        for cluster_id in sorted(df_with_clusters['cluster'].unique()):
            if cluster_id == -1:  # DBSCAN noise
                continue
            
            cluster_data = df_with_clusters[df_with_clusters['cluster'] == cluster_id]
            size = len(cluster_data)
            pct = (size / len(df_with_clusters)) * 100
            
            summary = {
                'Cluster': cluster_id,
                'Size': size,
                'Percentage': f"{pct:.1f}%",
                'Avg_Forward_Progress': f"{cluster_data['forward_progress'].mean():.2f}",
                'Avg_Minute': f"{cluster_data['minute'].mean():.1f}",
                'Play_Pattern_Mode': cluster_data['play_pattern_id'].mode().iloc[0] if len(cluster_data['play_pattern_id'].mode()) > 0 else 'N/A',
            }
            
            if event_type == "Pass":
                summary['Pass_Success_Rate'] = f"{cluster_data['pass_success'].mean():.2f}"
                summary['Avg_Pass_Length'] = f"{cluster_data['pass_length'].mean():.1f}"
            else:  # Carry
                summary['Avg_Duration'] = f"{cluster_data['duration'].mean():.2f}s"
                summary['Avg_Speed'] = f"{cluster_data['carry_speed'].mean():.2f}"
            
            cluster_summary.append(summary)
            
            print(f"\n🎯 Cluster {cluster_id} ({size:,} events, {pct:.1f}%):")
            print(f"   Forward Progress: {cluster_data['forward_progress'].mean():.2f}")
            print(f"   Game Minute: {cluster_data['minute'].mean():.1f}")
            print(f"   Under Pressure: {cluster_data['under_pressure'].mean():.2f}")
            
            if event_type == "Pass":
                print(f"   Pass Success: {cluster_data['pass_success'].mean():.2f}")
                print(f"   Pass Length: {cluster_data['pass_length'].mean():.1f}")
            else:
                print(f"   Duration: {cluster_data['duration'].mean():.2f}s")
                print(f"   Speed: {cluster_data['carry_speed'].mean():.2f}")
        
        # Save cluster summary
        cluster_df = pd.DataFrame(cluster_summary)
        cluster_df.to_csv(f'EDA/{event_type.lower()}_cluster_analysis.csv', index=False)
        print(f"\n💾 Cluster analysis saved to {event_type.lower()}_cluster_analysis.csv")
    
    def create_momentum_labels(self, features_df, event_type="Pass"):
        """Create sophisticated momentum labels"""
        
        momentum_score = np.zeros(len(features_df))
        
        # 1. Forward progress (+/- 3 points)
        forward_progress = features_df['forward_progress'].fillna(0)
        momentum_score += np.where(forward_progress > 15, 3,
                         np.where(forward_progress > 8, 2,
                         np.where(forward_progress > 0, 1,
                         np.where(forward_progress > -5, -1, -3))))
        
        # 2. Zone progression (+/- 2 points)
        zone_prog = features_df['zone_progression'].fillna(0)
        momentum_score += zone_prog * 2
        
        # 3. Sequence context (+1 point)
        momentum_score += np.where(features_df['related_events_count'] >= 3, 1, 0)
        
        # 4. Pressure context (-1 point)
        momentum_score -= features_df['under_pressure'].fillna(0)
        
        # 5. Game phase context
        late_game = features_df['minute'] > 75
        momentum_score += np.where(late_game, 1, 0)
        
        if event_type == "Pass":
            # Pass-specific factors
            momentum_score += np.where(features_df['pass_success'] == 1, 2, -2)
            # Long passes are riskier
            momentum_score += np.where(features_df['pass_length'] > 30, 1, 0)
            
        else:  # Carry
            # Carry-specific factors
            carry_speed = features_df['carry_speed'].fillna(features_df['carry_speed'].median())
            momentum_score += np.where(carry_speed > 4.0, 2,
                             np.where(carry_speed > 2.0, 1,
                             np.where(carry_speed < 0.8, -2, 0)))
            
            # Duration penalty (hesitation)
            momentum_score -= np.where(features_df['duration'] > 4.0, 1, 0)
        
        # Convert to categorical labels
        labels = np.where(momentum_score >= 4, 2,      # Strong Positive
                np.where(momentum_score >= 2, 1,      # Positive  
                np.where(momentum_score <= -4, -2,    # Strong Negative
                np.where(momentum_score <= -2, -1, 0))))  # Negative, Neutral
        
        return labels, momentum_score
    
    def supervised_analysis(self, event_type="Pass", n_iterations=3):
        """Run supervised momentum classification"""
        print(f"\n🎯 SUPERVISED MOMENTUM CLASSIFICATION - {event_type}")
        print("=" * 60)
        
        features_df = self.pass_features if event_type == "Pass" else self.carry_features
        
        # Create momentum labels
        labels, momentum_scores = self.create_momentum_labels(features_df, event_type)
        
        print(f"Momentum Label Distribution:")
        unique, counts = np.unique(labels, return_counts=True)
        for label, count in zip(unique, counts):
            label_name = {-2: "Strong Negative", -1: "Negative", 0: "Neutral", 1: "Positive", 2: "Strong Positive"}[label]
            print(f"  {label_name}: {count:,} ({count/len(labels)*100:.1f}%)")
        
        # Select features for modeling
        feature_cols = ['play_pattern_id', 'period', 'minute', 'forward_progress', 
                       'zone_progression', 'under_pressure', 'related_events_count']
        
        if event_type == "Pass":
            feature_cols.extend(['pass_height_id', 'body_part_id', 'pass_success', 'pass_length'])
        else:
            feature_cols.extend(['duration', 'carry_speed', 'carry_distance'])
        
        X = features_df[feature_cols].fillna(0)
        y = labels
        
        # Model configurations for grid search
        models = {
            'XGBoost': {
                'model': xgb.XGBClassifier(random_state=42),
                'params': {
                    'n_estimators': [100, 200],
                    'max_depth': [3, 5, 7],
                    'learning_rate': [0.1, 0.2]
                }
            },
            'RandomForest': {
                'model': RandomForestClassifier(random_state=42),
                'params': {
                    'n_estimators': [100, 200],
                    'max_depth': [5, 10, None],
                    'min_samples_split': [2, 5]
                }
            }
        }
        
        best_results = {}
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        
        for model_name, config in models.items():
            print(f"\n🔍 Optimizing {model_name}...")
            
            # Grid search
            grid_search = GridSearchCV(
                config['model'], 
                config['params'], 
                cv=cv, 
                scoring='accuracy',
                n_jobs=-1
            )
            
            grid_search.fit(X, y)
            
            best_results[model_name] = {
                'best_score': grid_search.best_score_,
                'best_params': grid_search.best_params_,
                'best_model': grid_search.best_estimator_,
                'feature_importance': pd.DataFrame({
                    'feature': feature_cols,
                    'importance': grid_search.best_estimator_.feature_importances_
                }).sort_values('importance', ascending=False)
            }
            
            print(f"   Best CV Score: {grid_search.best_score_:.3f}")
            print(f"   Best Params: {grid_search.best_params_}")
        
        # Select best model
        best_model_name = max(best_results.keys(), key=lambda k: best_results[k]['best_score'])
        best_result = best_results[best_model_name]
        
        print(f"\n🏆 Best Model: {best_model_name} (CV Score: {best_result['best_score']:.3f})")
        print("\n📊 Top 10 Feature Importances:")
        print(best_result['feature_importance'].head(10).to_string(index=False))
        
        # Save results
        best_result['feature_importance'].to_csv(f'EDA/{event_type.lower()}_feature_importance.csv', index=False)
        
        self.results[f'{event_type}_supervised'] = best_result
        
        return best_result
    
    def run_complete_analysis(self):
        """Run complete analysis pipeline"""
        print("🚀 STARTING COMPLETE PASS & CARRY MOMENTUM ANALYSIS")
        print("=" * 80)
        
        # Load and preprocess data
        self.load_and_preprocess_data()
        
        # Create features
        self.create_pass_features()
        self.create_carry_features()
        
        # Run analyses
        print("\n" + "="*80)
        pass_unsupervised = self.unsupervised_analysis("Pass", n_iterations=3)
        
        print("\n" + "="*80)
        pass_supervised = self.supervised_analysis("Pass", n_iterations=3)
        
        print("\n" + "="*80)
        carry_unsupervised = self.unsupervised_analysis("Carry", n_iterations=3)
        
        print("\n" + "="*80)
        carry_supervised = self.supervised_analysis("Carry", n_iterations=3)
        
        # Generate summary report
        self.generate_summary_report()
        
        return self.results
    
    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        print("\n" + "="*80)
        print("📋 COMPREHENSIVE ANALYSIS SUMMARY")
        print("=" * 80)
        
        print(f"\n📊 DATASET SUMMARY:")
        print(f"   Total Events Analyzed: {len(self.df):,}")
        print(f"   Pass Events: {len(self.pass_features):,}")
        print(f"   Carry Events: {len(self.carry_features):,}")
        
        print(f"\n🔍 UNSUPERVISED RESULTS:")
        if 'Pass_unsupervised' in self.results:
            print(f"   Pass Clustering - Best Silhouette Score: {self.results['Pass_unsupervised']['silhouette']:.3f}")
        if 'Carry_unsupervised' in self.results:
            print(f"   Carry Clustering - Best Silhouette Score: {self.results['Carry_unsupervised']['silhouette']:.3f}")
        
        print(f"\n🎯 SUPERVISED RESULTS:")
        if 'Pass_supervised' in self.results:
            print(f"   Pass Classification - Best CV Score: {self.results['Pass_supervised']['best_score']:.3f}")
            print(f"   Pass Best Model: {self.results['Pass_supervised']['best_params']}")
        if 'Carry_supervised' in self.results:
            print(f"   Carry Classification - Best CV Score: {self.results['Carry_supervised']['best_score']:.3f}")
            print(f"   Carry Best Model: {self.results['Carry_supervised']['best_params']}")
        
        print(f"\n💾 OUTPUT FILES GENERATED:")
        print(f"   - pass_cluster_analysis.csv")
        print(f"   - carry_cluster_analysis.csv") 
        print(f"   - pass_feature_importance.csv")
        print(f"   - carry_feature_importance.csv")
        
        print("\n✅ ANALYSIS COMPLETE!")

# Run the analysis
if __name__ == "__main__":
    analyzer = PassCarryMomentumAnalyzer('../Data/events_complete.csv')
    results = analyzer.run_complete_analysis() 