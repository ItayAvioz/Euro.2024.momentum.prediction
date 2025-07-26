import pandas as pd
import numpy as np
import ast
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report, silhouette_score
import warnings
warnings.filterwarnings('ignore')

def safe_parse(x):
    """Safely parse JSON-like strings"""
    if pd.isna(x) or x == '' or x == 'nan':
        return {}
    try:
        return ast.literal_eval(x) if isinstance(x, str) else x
    except:
        return {}

def safe_parse_location(x):
    """Safely parse location coordinates"""
    if pd.isna(x) or x == '' or x == 'nan':
        return [None, None]
    try:
        parsed = ast.literal_eval(x) if isinstance(x, str) else x
        if isinstance(parsed, list) and len(parsed) >= 2:
            return [float(parsed[0]), float(parsed[1])]
        return [None, None]
    except:
        return [None, None]

def load_and_parse_data(file_path):
    """Load and parse the events data with enhanced location processing"""
    print("🔄 Loading Euro 2024 events data...")
    df = pd.read_csv(file_path, low_memory=False)
    
    # Filter for Pass and Carry events only
    df = df[df['event_type'].isin(['Pass', 'Carry'])].copy()
    
    print(f"✅ Loaded {len(df):,} Pass and Carry events")
    print(f"   - Pass events: {len(df[df['event_type'] == 'Pass']):,}")
    print(f"   - Carry events: {len(df[df['event_type'] == 'Carry']):,}")
    
    # Parse key columns
    print("   Parsing JSON columns...")
    
    # Parse type
    if 'type' in df.columns:
        type_data = df['type'].apply(safe_parse)
        df['type_id'] = type_data.apply(lambda x: x.get('id', None))
    
    # Parse play_pattern
    if 'play_pattern' in df.columns:
        play_pattern_data = df['play_pattern'].apply(safe_parse)
        df['play_pattern_id'] = play_pattern_data.apply(lambda x: x.get('id', None))
    
    # Parse player
    if 'player' in df.columns:
        player_data = df['player'].apply(safe_parse)
        df['player_id'] = player_data.apply(lambda x: x.get('id', None))
    
    # Parse position
    if 'position' in df.columns:
        position_data = df['position'].apply(safe_parse)
        df['position_id'] = position_data.apply(lambda x: x.get('id', None))
    
    # Parse location coordinates (ENHANCED)
    print("   Parsing location coordinates...")
    if 'location' in df.columns:
        location_parsed = df['location'].apply(safe_parse_location)
        df['start_x'] = location_parsed.apply(lambda x: x[0])
        df['start_y'] = location_parsed.apply(lambda x: x[1])
        
        # Create enhanced location features (using numeric values directly)
        df['field_zone_id'] = pd.cut(df['start_x'], bins=[0, 40, 80, 120], labels=[1, 2, 3]).astype(float)
        df['field_side_id'] = pd.cut(df['start_y'], bins=[0, 27, 53, 80], labels=[1, 2, 3]).astype(float)
        
        # Distance from goal (attacking direction)
        df['distance_to_goal'] = 120 - df['start_x']
        
        # Distance from center line
        df['distance_from_center'] = abs(df['start_y'] - 40)
        
        # Combined position risk (closer to goal + central = higher risk/reward)
        df['position_risk'] = (120 - df['start_x']) / 120 + (1 - abs(df['start_y'] - 40) / 40)
    
    # Parse pass details
    if 'pass' in df.columns:
        pass_data = df['pass'].apply(safe_parse)
        df['pass_length'] = pass_data.apply(lambda x: x.get('length', None))
        df['pass_angle'] = pass_data.apply(lambda x: x.get('angle', None))
        
        # Parse recipient
        recipient = pass_data.apply(lambda x: x.get('recipient', {}))
        df['recipient_id'] = recipient.apply(lambda x: x.get('id', None) if isinstance(x, dict) else None)
        
        # Parse height
        height = pass_data.apply(lambda x: x.get('height', {}))
        df['pass_height_id'] = height.apply(lambda x: x.get('id', None) if isinstance(x, dict) else None)
        
        # Parse body part
        body_part = pass_data.apply(lambda x: x.get('body_part', {}))
        df['body_part_id'] = body_part.apply(lambda x: x.get('id', None) if isinstance(x, dict) else None)
        
        # Parse outcome
        outcome = pass_data.apply(lambda x: x.get('outcome', {}))
        df['pass_outcome_id'] = outcome.apply(lambda x: x.get('id', None) if isinstance(x, dict) else None)
        
        # Parse end location
        end_location = pass_data.apply(lambda x: x.get('end_location', []))
        df['pass_end_x'] = end_location.apply(lambda x: x[0] if isinstance(x, list) and len(x) >= 2 else None)
        df['pass_end_y'] = end_location.apply(lambda x: x[1] if isinstance(x, list) and len(x) >= 2 else None)
    
    # Parse carry details
    if 'carry' in df.columns:
        carry_data = df['carry'].apply(safe_parse)
        end_location = carry_data.apply(lambda x: x.get('end_location', []))
        df['carry_end_x'] = end_location.apply(lambda x: x[0] if isinstance(x, list) and len(x) >= 2 else None)
        df['carry_end_y'] = end_location.apply(lambda x: x[1] if isinstance(x, list) and len(x) >= 2 else None)
    
    # Parse related events count
    if 'related_events' in df.columns:
        df['related_events_count'] = df['related_events'].apply(
            lambda x: len(ast.literal_eval(x)) if pd.notna(x) and x != '' and x != 'nan' else 0
        )
    
    print(f"   Location parsing complete. Valid coordinates: {df['start_x'].notna().sum():,}")
    
    return df

def create_enhanced_pass_features(df):
    """Create enhanced features for Pass events including location"""
    print("🔧 Creating Enhanced Pass features with location...")
    
    pass_df = df[df['event_type'] == 'Pass'].copy()
    
    # Basic features
    features = pass_df[['play_pattern_id', 'period', 'minute', 'player_id', 'position_id',
                       'recipient_id', 'pass_height_id', 'body_part_id', 'pass_outcome_id',
                       'pass_length', 'pass_angle', 'start_x', 'start_y', 'pass_end_x', 'pass_end_y',
                       'field_zone_id', 'field_side_id', 'distance_to_goal', 'distance_from_center', 'position_risk',
                       'related_events_count']].copy()
    
    # Derived spatial features
    features['forward_progress'] = features['pass_end_x'] - features['start_x']
    features['lateral_movement'] = abs(features['pass_end_y'] - features['start_y'])
    features['diagonal_distance'] = np.sqrt(features['forward_progress']**2 + features['lateral_movement']**2)
    
    # Zone progression (fixed to use numeric values)
    features['field_zone_end'] = pd.cut(features['pass_end_x'], bins=[0, 40, 80, 120], labels=[1, 2, 3]).astype(float)
    features['zone_progression'] = features['field_zone_end'] - features['field_zone_id']
    
    # Advanced location features
    features['attacking_third_start'] = (features['start_x'] > 80).astype(int)
    features['attacking_third_end'] = (features['pass_end_x'] > 80).astype(int)
    features['crosses_center_line'] = ((features['start_x'] < 60) & (features['pass_end_x'] > 60)).astype(int)
    features['goal_approach'] = (features['pass_end_x'] > 100).astype(int)
    
    # Central corridor vs. wide areas
    features['central_start'] = ((features['start_y'] > 25) & (features['start_y'] < 55)).astype(int)
    features['wide_to_central'] = ((features['start_y'] <= 25) | (features['start_y'] >= 55)) & ((features['pass_end_y'] > 25) & (features['pass_end_y'] < 55))
    features['wide_to_central'] = features['wide_to_central'].astype(int)
    
    # Pass success (no outcome = success)
    features['pass_success'] = features['pass_outcome_id'].isna().astype(int)
    
    # Under pressure flag
    features['under_pressure'] = pass_df['under_pressure'].fillna(0).astype(int) if 'under_pressure' in pass_df.columns else 0
    
    # Game phase
    features['game_phase'] = pd.cut(features['minute'], bins=[0, 15, 30, 45, 60, 75, 120], labels=[1, 2, 3, 4, 5, 6]).astype(float)
    
    # Fill missing values
    numeric_cols = ['play_pattern_id', 'pass_height_id', 'body_part_id', 'pass_length', 'pass_angle', 'related_events_count']
    for col in numeric_cols:
        if col in features.columns:
            features[col] = features[col].fillna(features[col].median())
    
    features = features.fillna(0)
    
    print(f"✅ Created {len(features)} Pass events with {len(features.columns)} enhanced features")
    
    return features

def create_enhanced_carry_features(df):
    """Create enhanced features for Carry events including location"""
    print("🔧 Creating Enhanced Carry features with location...")
    
    carry_df = df[df['event_type'] == 'Carry'].copy()
    
    # Basic features
    features = carry_df[['play_pattern_id', 'period', 'minute', 'player_id', 'position_id',
                        'start_x', 'start_y', 'carry_end_x', 'carry_end_y', 'duration',
                        'field_zone_id', 'field_side_id', 'distance_to_goal', 'distance_from_center', 'position_risk',
                        'related_events_count']].copy()
    
    # Derived spatial features
    features['carry_distance'] = np.sqrt((features['carry_end_x'] - features['start_x'])**2 + 
                                        (features['carry_end_y'] - features['start_y'])**2)
    features['forward_progress'] = features['carry_end_x'] - features['start_x']
    features['lateral_movement'] = abs(features['carry_end_y'] - features['start_y'])
    
    # Carry speed and direction
    features['carry_speed'] = features['carry_distance'] / (features['duration'] + 0.1)
    features['carry_direction'] = np.arctan2(features['carry_end_y'] - features['start_y'],
                                           features['carry_end_x'] - features['start_x'])
    
    # Zone progression
    features['field_zone_end'] = pd.cut(features['carry_end_x'], bins=[0, 40, 80, 120], labels=[1, 2, 3]).astype(float)
    features['zone_progression'] = features['field_zone_end'] - features['field_zone_id']
    
    # Advanced location features
    features['attacking_third_start'] = (features['start_x'] > 80).astype(int)
    features['attacking_third_end'] = (features['carry_end_x'] > 80).astype(int)
    features['crosses_center_line'] = ((features['start_x'] < 60) & (features['carry_end_x'] > 60)).astype(int)
    features['goal_approach'] = (features['carry_end_x'] > 100).astype(int)
    features['dribble_into_box'] = ((features['start_x'] < 102) & (features['carry_end_x'] > 102)).astype(int)
    
    # Central vs. wide carries
    features['central_start'] = ((features['start_y'] > 25) & (features['start_y'] < 55)).astype(int)
    features['wing_to_center'] = ((features['start_y'] <= 25) | (features['start_y'] >= 55)) & ((features['carry_end_y'] > 25) & (features['carry_end_y'] < 55))
    features['wing_to_center'] = features['wing_to_center'].astype(int)
    
    # Under pressure flag
    features['under_pressure'] = carry_df['under_pressure'].fillna(0).astype(int) if 'under_pressure' in carry_df.columns else 0
    
    # Game phase
    features['game_phase'] = pd.cut(features['minute'], bins=[0, 15, 30, 45, 60, 75, 120], labels=[1, 2, 3, 4, 5, 6]).astype(float)
    
    # Decision speed categories
    features['decision_speed'] = pd.cut(features['duration'], bins=[0, 1, 3, 6, 100], labels=[1, 2, 3, 4]).astype(float)
    
    # Fill missing values
    numeric_cols = ['play_pattern_id', 'duration', 'related_events_count']
    for col in numeric_cols:
        if col in features.columns:
            features[col] = features[col].fillna(features[col].median())
    
    features = features.fillna(0)
    
    print(f"✅ Created {len(features)} Carry events with {len(features.columns)} enhanced features")
    
    return features

def enhanced_clustering(features_df, event_type):
    """Run enhanced clustering analysis"""
    print(f"🔍 Enhanced Clustering - {event_type}")
    
    # Select numeric features for clustering
    numeric_features = features_df.select_dtypes(include=[np.number]).columns.tolist()
    X = features_df[numeric_features].copy()
    
    # Clean data
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.median())
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Try different clustering methods
    best_silhouette = -1
    best_clusters = None
    best_method = None
    
    methods = {
        'KMeans_6': KMeans(n_clusters=6, random_state=42, n_init=10),
        'KMeans_8': KMeans(n_clusters=8, random_state=42, n_init=10),
        'KMeans_10': KMeans(n_clusters=10, random_state=42, n_init=10),
    }
    
    for method_name, method in methods.items():
        try:
            clusters = method.fit_predict(X_scaled)
            silhouette = silhouette_score(X_scaled, clusters)
            
            print(f"   {method_name}: Silhouette Score = {silhouette:.3f}")
            
            if silhouette > best_silhouette:
                best_silhouette = silhouette
                best_clusters = clusters
                best_method = method_name
                
        except Exception as e:
            print(f"   {method_name}: Error - {str(e)}")
    
    print(f"\n🏆 Best Method: {best_method} (Silhouette: {best_silhouette:.3f})")
    
    # Analyze clusters
    analyze_enhanced_clusters(features_df, best_clusters, event_type)
    
    return best_clusters, best_silhouette

def analyze_enhanced_clusters(features_df, clusters, event_type):
    """Analyze enhanced cluster characteristics"""
    print(f"\n📊 Enhanced Cluster Analysis - {event_type}")
    print("-" * 50)
    
    df_with_clusters = features_df.copy()
    df_with_clusters['cluster'] = clusters
    
    cluster_summary = []
    
    for cluster_id in sorted(df_with_clusters['cluster'].unique()):
        cluster_data = df_with_clusters[df_with_clusters['cluster'] == cluster_id]
        size = len(cluster_data)
        pct = (size / len(df_with_clusters)) * 100
        
        summary = {
            'Cluster': cluster_id,
            'Size': size,
            'Percentage': f"{pct:.1f}%",
            'Avg_Forward_Progress': f"{cluster_data['forward_progress'].mean():.2f}",
            'Distance_to_Goal': f"{cluster_data['distance_to_goal'].mean():.1f}",
            'Position_Risk': f"{cluster_data['position_risk'].mean():.2f}",
            'Attacking_Third': f"{cluster_data['attacking_third_start'].mean():.2f}",
            'Zone_Progression': f"{cluster_data['zone_progression'].mean():.2f}",
        }
        
        if event_type == "Pass":
            summary['Pass_Success'] = f"{cluster_data['pass_success'].mean():.2f}"
            summary['Goal_Approach'] = f"{cluster_data.get('goal_approach', pd.Series([0])).mean():.2f}"
        else:  # Carry
            summary['Carry_Speed'] = f"{cluster_data['carry_speed'].mean():.2f}"
            summary['Box_Entry'] = f"{cluster_data.get('dribble_into_box', pd.Series([0])).mean():.2f}"
        
        cluster_summary.append(summary)
        
        print(f"\n🎯 Cluster {cluster_id} ({size:,} events, {pct:.1f}%):")
        print(f"   Forward Progress: {cluster_data['forward_progress'].mean():.2f}m")
        print(f"   Distance to Goal: {cluster_data['distance_to_goal'].mean():.1f}m")
        print(f"   Position Risk: {cluster_data['position_risk'].mean():.2f}")
        print(f"   Zone Progression: {cluster_data['zone_progression'].mean():.2f}")
        
        if event_type == "Pass":
            print(f"   Pass Success: {cluster_data['pass_success'].mean():.2f}")
        else:
            print(f"   Carry Speed: {cluster_data['carry_speed'].mean():.2f}")
    
    # Save cluster summary
    cluster_df = pd.DataFrame(cluster_summary)
    cluster_df.to_csv(f'enhanced_{event_type.lower()}_clusters.csv', index=False)
    print(f"\n💾 Saved to enhanced_{event_type.lower()}_clusters.csv")
    
    return cluster_summary

def enhanced_supervised(features_df, event_type):
    """Run enhanced supervised analysis"""
    print(f"🎯 Enhanced Supervised Analysis - {event_type}")
    
    # Create enhanced momentum labels
    labels = create_enhanced_momentum_labels(features_df, event_type)
    
    print(f"Enhanced Momentum Distribution:")
    unique, counts = np.unique(labels, return_counts=True)
    for label, count in zip(unique, counts):
        label_names = {-2: "Strong Negative", -1: "Negative", 0: "Neutral", 1: "Positive", 2: "Strong Positive"}
        name = label_names.get(label, f"Label_{label}")
        print(f"  {name}: {count:,} ({count/len(labels)*100:.1f}%)")
    
    # Select features for modeling
    location_features = ['distance_to_goal', 'position_risk', 'attacking_third_start', 'zone_progression']
    core_features = ['forward_progress', 'related_events_count']
    
    if event_type == "Pass":
        event_features = ['pass_success', 'pass_length', 'goal_approach', 'crosses_center_line']
    else:
        event_features = ['carry_speed', 'carry_distance', 'duration', 'dribble_into_box']
    
    feature_cols = core_features + location_features + event_features
    feature_cols = [col for col in feature_cols if col in features_df.columns]
    
    X = features_df[feature_cols].fillna(0)
    y = labels
    
    # Train models
    models = {
        'RandomForest': RandomForestClassifier(n_estimators=150, random_state=42),
        'GradientBoosting': GradientBoostingClassifier(random_state=42)
    }
    
    best_score = 0
    best_model_name = None
    best_model = None
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    for model_name, model in models.items():
        cv_scores = cross_val_score(model, X, y, cv=cv, scoring='accuracy')
        mean_score = cv_scores.mean()
        
        print(f"   {model_name}: {mean_score:.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        if mean_score > best_score:
            best_score = mean_score
            best_model_name = model_name
            best_model = model
    
    # Get feature importance
    best_model.fit(X, y)
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\n🏆 Best: {best_model_name} ({best_score:.3f})")
    print("📊 Top Features:")
    print(feature_importance.head(8).to_string(index=False))
    
    # Save results
    feature_importance.to_csv(f'enhanced_{event_type.lower()}_importance.csv', index=False)
    
    return best_score, best_model_name, feature_importance

def create_enhanced_momentum_labels(features_df, event_type="Pass"):
    """Create enhanced momentum labels with location factors"""
    momentum_score = np.zeros(len(features_df))
    
    # 1. Forward progress (primary factor)
    forward_progress = features_df['forward_progress'].fillna(0)
    momentum_score += np.where(forward_progress > 20, 4,
                     np.where(forward_progress > 10, 3,
                     np.where(forward_progress > 5, 2,
                     np.where(forward_progress > 0, 1,
                     np.where(forward_progress > -5, -1, -3)))))
    
    # 2. Zone progression
    zone_prog = features_df['zone_progression'].fillna(0)
    momentum_score += zone_prog * 3
    
    # 3. Location-based momentum
    if 'attacking_third_start' in features_df.columns:
        momentum_score += features_df['attacking_third_start'] * 2
    if 'goal_approach' in features_df.columns:
        momentum_score += features_df['goal_approach'] * 3
    if 'crosses_center_line' in features_df.columns:
        momentum_score += features_df['crosses_center_line'] * 2
    
    # 4. Position risk
    position_risk = features_df['position_risk'].fillna(0)
    momentum_score += np.where(position_risk > 1.5, 2, np.where(position_risk > 1.0, 1, 0))
    
    # 5. Event-specific factors
    if event_type == "Pass" and 'pass_success' in features_df.columns:
        momentum_score += np.where(features_df['pass_success'] == 1, 3, -4)
    elif event_type == "Carry":
        if 'carry_speed' in features_df.columns:
            carry_speed = features_df['carry_speed'].fillna(features_df['carry_speed'].median())
            momentum_score += np.where(carry_speed > 5.0, 3,
                             np.where(carry_speed > 3.0, 2,
                             np.where(carry_speed > 1.5, 1, 0)))
        if 'dribble_into_box' in features_df.columns:
            momentum_score += features_df['dribble_into_box'] * 4
    
    # Convert to labels
    labels = np.where(momentum_score >= 8, 2,
            np.where(momentum_score >= 4, 1,
            np.where(momentum_score <= -8, -2,
            np.where(momentum_score <= -4, -1, 0))))
    
    return labels

def main():
    """Main analysis function"""
    print("🚀 ENHANCED PASS & CARRY MOMENTUM ANALYSIS WITH LOCATION")
    print("=" * 80)
    
    # Load data
    df = load_and_parse_data('../Data/events_complete.csv')
    
    # Create features
    pass_features = create_enhanced_pass_features(df)
    carry_features = create_enhanced_carry_features(df)
    
    print(f"\n📊 Enhanced Features Summary:")
    print(f"   Pass: {len(pass_features.columns)} features")
    print(f"   Carry: {len(carry_features.columns)} features")
    
    # Run analyses
    print("\n" + "="*60)
    pass_clusters, pass_sil = enhanced_clustering(pass_features, "Pass")
    
    print("\n" + "="*60)
    pass_score, pass_model, pass_imp = enhanced_supervised(pass_features, "Pass")
    
    print("\n" + "="*60)
    carry_clusters, carry_sil = enhanced_clustering(carry_features, "Carry")
    
    print("\n" + "="*60)
    carry_score, carry_model, carry_imp = enhanced_supervised(carry_features, "Carry")
    
    # Final summary
    print("\n" + "="*80)
    print("📋 ENHANCED ANALYSIS RESULTS")
    print("=" * 80)
    print(f"📊 Dataset: {len(df):,} events with location data")
    print(f"🔍 Clustering: Pass({pass_sil:.3f}), Carry({carry_sil:.3f})")
    print(f"🎯 Classification: Pass({pass_score:.3f}), Carry({carry_score:.3f})")
    print("💾 Files: enhanced_pass/carry_clusters.csv, enhanced_pass/carry_importance.csv")
    print("✅ Enhanced Analysis Complete!")
    
    return {
        'pass_silhouette': pass_sil,
        'carry_silhouette': carry_sil,
        'pass_accuracy': pass_score,
        'carry_accuracy': carry_score
    }

if __name__ == "__main__":
    results = main() 