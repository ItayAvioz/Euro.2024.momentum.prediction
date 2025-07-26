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

def load_and_parse_data(file_path):
    """Load and parse the events data"""
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
        df['type_name'] = type_data.apply(lambda x: x.get('name', None))
    
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
    
    # Parse location (start coordinates)
    if 'location' in df.columns:
        try:
            location_parsed = df['location'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else [None, None])
            df['start_x'] = location_parsed.apply(lambda x: x[0] if len(x) >= 2 else None)
            df['start_y'] = location_parsed.apply(lambda x: x[1] if len(x) >= 2 else None)
        except:
            df['start_x'] = None
            df['start_y'] = None
    
    # Parse related events count
    if 'related_events' in df.columns:
        df['related_events_count'] = df['related_events'].apply(
            lambda x: len(ast.literal_eval(x)) if pd.notna(x) and x != '' and x != 'nan' else 0
        )
    
    return df

def create_pass_features(df):
    """Create features for Pass events"""
    print("🔧 Creating Pass features...")
    
    pass_df = df[df['event_type'] == 'Pass'].copy()
    
    # Select and clean features
    features = pass_df[['play_pattern_id', 'period', 'minute', 'player_id', 'position_id',
                       'recipient_id', 'pass_height_id', 'body_part_id', 'pass_outcome_id',
                       'pass_length', 'pass_angle', 'start_x', 'start_y', 'pass_end_x', 'pass_end_y',
                       'related_events_count']].copy()
    
    # Derived features
    features['forward_progress'] = features['pass_end_x'] - features['start_x']
    features['lateral_movement'] = abs(features['pass_end_y'] - features['start_y'])
    
    # Field zones (1=defensive, 2=middle, 3=attacking)
    features['field_zone_start'] = pd.cut(features['start_x'], bins=[0, 40, 80, 120], labels=[1, 2, 3]).astype(float)
    features['field_zone_end'] = pd.cut(features['pass_end_x'], bins=[0, 40, 80, 120], labels=[1, 2, 3]).astype(float)
    features['zone_progression'] = features['field_zone_end'] - features['field_zone_start']
    
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
    
    print(f"✅ Created {len(features)} Pass events with {len(features.columns)} features")
    return features

def create_carry_features(df):
    """Create features for Carry events"""
    print("🔧 Creating Carry features...")
    
    carry_df = df[df['event_type'] == 'Carry'].copy()
    
    # Select and clean features
    features = carry_df[['play_pattern_id', 'period', 'minute', 'player_id', 'position_id',
                        'start_x', 'start_y', 'carry_end_x', 'carry_end_y', 'duration',
                        'related_events_count']].copy()
    
    # Derived features
    features['carry_distance'] = np.sqrt(
        (features['carry_end_x'] - features['start_x'])**2 + 
        (features['carry_end_y'] - features['start_y'])**2
    )
    features['forward_progress'] = features['carry_end_x'] - features['start_x']
    features['lateral_movement'] = abs(features['carry_end_y'] - features['start_y'])
    
    # Carry speed
    features['carry_speed'] = features['carry_distance'] / (features['duration'] + 0.1)
    
    # Field zones
    features['field_zone_start'] = pd.cut(features['start_x'], bins=[0, 40, 80, 120], labels=[1, 2, 3]).astype(float)
    features['field_zone_end'] = pd.cut(features['carry_end_x'], bins=[0, 40, 80, 120], labels=[1, 2, 3]).astype(float)
    features['zone_progression'] = features['field_zone_end'] - features['field_zone_start']
    
    # Under pressure flag
    features['under_pressure'] = carry_df['under_pressure'].fillna(0).astype(int) if 'under_pressure' in carry_df.columns else 0
    
    # Game phase
    features['game_phase'] = pd.cut(features['minute'], bins=[0, 15, 30, 45, 60, 75, 120], labels=[1, 2, 3, 4, 5, 6]).astype(float)
    
    # Fill missing values
    numeric_cols = ['play_pattern_id', 'duration', 'related_events_count']
    for col in numeric_cols:
        if col in features.columns:
            features[col] = features[col].fillna(features[col].median())
    
    features = features.fillna(0)
    
    print(f"✅ Created {len(features)} Carry events with {len(features.columns)} features")
    return features

def unsupervised_analysis(features_df, event_type="Pass"):
    """Run unsupervised clustering analysis"""
    print(f"\n🔍 UNSUPERVISED PATTERN DISCOVERY - {event_type}")
    print("=" * 60)
    
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
        'KMeans_5': KMeans(n_clusters=5, random_state=42, n_init=10),
        'KMeans_7': KMeans(n_clusters=7, random_state=42, n_init=10),
        'KMeans_10': KMeans(n_clusters=10, random_state=42, n_init=10),
    }
    
    for method_name, method in methods.items():
        try:
            clusters = method.fit_predict(X_scaled)
            silhouette = silhouette_score(X_scaled, clusters)
            
            print(f"{method_name}: Silhouette Score = {silhouette:.3f}")
            
            if silhouette > best_silhouette:
                best_silhouette = silhouette
                best_clusters = clusters
                best_method = method_name
                
        except Exception as e:
            print(f"{method_name}: Error - {str(e)}")
    
    print(f"\n🏆 Best Method: {best_method} (Silhouette: {best_silhouette:.3f})")
    
    # Analyze best clusters
    analyze_clusters(features_df, best_clusters, event_type, best_method)
    
    return best_clusters, best_silhouette, best_method

def analyze_clusters(features_df, clusters, event_type, method_name):
    """Analyze cluster characteristics"""
    print(f"\n📊 CLUSTER ANALYSIS - {event_type} ({method_name})")
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
            'Avg_Minute': f"{cluster_data['minute'].mean():.1f}",
            'Play_Pattern_Mode': cluster_data['play_pattern_id'].mode().iloc[0] if len(cluster_data) > 0 else 'N/A',
        }
        
        if event_type == "Pass":
            summary['Pass_Success_Rate'] = f"{cluster_data['pass_success'].mean():.2f}"
            if 'pass_length' in cluster_data.columns:
                summary['Avg_Pass_Length'] = f"{cluster_data['pass_length'].mean():.1f}"
        else:  # Carry
            if 'duration' in cluster_data.columns:
                summary['Avg_Duration'] = f"{cluster_data['duration'].mean():.2f}s"
            if 'carry_speed' in cluster_data.columns:
                summary['Avg_Speed'] = f"{cluster_data['carry_speed'].mean():.2f}"
        
        cluster_summary.append(summary)
        
        print(f"\n🎯 Cluster {cluster_id} ({size:,} events, {pct:.1f}%):")
        print(f"   Forward Progress: {cluster_data['forward_progress'].mean():.2f}")
        print(f"   Game Minute: {cluster_data['minute'].mean():.1f}")
        print(f"   Zone Progression: {cluster_data['zone_progression'].mean():.2f}")
        
        if event_type == "Pass" and 'pass_success' in cluster_data.columns:
            print(f"   Pass Success: {cluster_data['pass_success'].mean():.2f}")
        elif event_type == "Carry" and 'carry_speed' in cluster_data.columns:
            print(f"   Carry Speed: {cluster_data['carry_speed'].mean():.2f}")
    
    # Save cluster summary
    cluster_df = pd.DataFrame(cluster_summary)
    cluster_df.to_csv(f'{event_type.lower()}_cluster_analysis.csv', index=False)
    print(f"\n💾 Cluster analysis saved to {event_type.lower()}_cluster_analysis.csv")
    
    return cluster_summary

def create_momentum_labels(features_df, event_type="Pass"):
    """Create momentum labels"""
    momentum_score = np.zeros(len(features_df))
    
    # Forward progress scoring
    forward_progress = features_df['forward_progress'].fillna(0)
    momentum_score += np.where(forward_progress > 15, 3,
                     np.where(forward_progress > 8, 2,
                     np.where(forward_progress > 0, 1,
                     np.where(forward_progress > -5, -1, -3))))
    
    # Zone progression
    if 'zone_progression' in features_df.columns:
        zone_prog = features_df['zone_progression'].fillna(0)
        momentum_score += zone_prog * 2
    
    # Sequence context
    if 'related_events_count' in features_df.columns:
        momentum_score += np.where(features_df['related_events_count'] >= 3, 1, 0)
    
    # Event-specific factors
    if event_type == "Pass" and 'pass_success' in features_df.columns:
        momentum_score += np.where(features_df['pass_success'] == 1, 2, -2)
    elif event_type == "Carry" and 'carry_speed' in features_df.columns:
        carry_speed = features_df['carry_speed'].fillna(features_df['carry_speed'].median())
        momentum_score += np.where(carry_speed > 4.0, 2,
                         np.where(carry_speed > 2.0, 1,
                         np.where(carry_speed < 0.8, -2, 0)))
    
    # Convert to categorical labels
    labels = np.where(momentum_score >= 4, 2,
            np.where(momentum_score >= 2, 1,
            np.where(momentum_score <= -4, -2,
            np.where(momentum_score <= -2, -1, 0))))
    
    return labels

def supervised_analysis(features_df, event_type="Pass"):
    """Run supervised classification analysis"""
    print(f"\n🎯 SUPERVISED MOMENTUM CLASSIFICATION - {event_type}")
    print("=" * 60)
    
    # Create momentum labels
    labels = create_momentum_labels(features_df, event_type)
    
    print(f"Momentum Label Distribution:")
    unique, counts = np.unique(labels, return_counts=True)
    for label, count in zip(unique, counts):
        label_names = {-2: "Strong Negative", -1: "Negative", 0: "Neutral", 1: "Positive", 2: "Strong Positive"}
        label_name = label_names.get(label, f"Label_{label}")
        print(f"  {label_name}: {count:,} ({count/len(labels)*100:.1f}%)")
    
    # Select features for modeling
    feature_cols = ['play_pattern_id', 'period', 'minute', 'forward_progress', 'zone_progression']
    
    if event_type == "Pass":
        pass_specific = ['pass_height_id', 'body_part_id', 'pass_success', 'pass_length']
        feature_cols.extend([col for col in pass_specific if col in features_df.columns])
    else:
        carry_specific = ['duration', 'carry_speed', 'carry_distance']
        feature_cols.extend([col for col in carry_specific if col in features_df.columns])
    
    # Add common features if available
    common_features = ['under_pressure', 'related_events_count']
    feature_cols.extend([col for col in common_features if col in features_df.columns])
    
    X = features_df[feature_cols].fillna(0)
    y = labels
    
    # Train models
    models = {
        'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
        'GradientBoosting': GradientBoostingClassifier(random_state=42)
    }
    
    best_score = 0
    best_model_name = None
    best_model = None
    best_importance = None
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    for model_name, model in models.items():
        cv_scores = cross_val_score(model, X, y, cv=cv, scoring='accuracy')
        mean_score = cv_scores.mean()
        
        print(f"{model_name}: CV Accuracy = {mean_score:.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        if mean_score > best_score:
            best_score = mean_score
            best_model_name = model_name
            best_model = model
    
    # Train best model and get feature importance
    best_model.fit(X, y)
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\n🏆 Best Model: {best_model_name} (CV Score: {best_score:.3f})")
    print("\n📊 Top 10 Feature Importances:")
    print(feature_importance.head(10).to_string(index=False))
    
    # Save results
    feature_importance.to_csv(f'{event_type.lower()}_feature_importance.csv', index=False)
    
    return best_score, best_model_name, feature_importance

def main():
    """Run complete analysis"""
    print("🚀 STARTING PASS & CARRY MOMENTUM ANALYSIS")
    print("=" * 80)
    
    # Load and preprocess data
    df = load_and_parse_data('../Data/events_complete.csv')
    
    # Create features
    pass_features = create_pass_features(df)
    carry_features = create_carry_features(df)
    
    # Run analyses
    print("\n" + "="*80)
    pass_clusters, pass_silhouette, pass_method = unsupervised_analysis(pass_features, "Pass")
    
    print("\n" + "="*80)
    pass_score, pass_model, pass_importance = supervised_analysis(pass_features, "Pass")
    
    print("\n" + "="*80)
    carry_clusters, carry_silhouette, carry_method = unsupervised_analysis(carry_features, "Carry")
    
    print("\n" + "="*80)
    carry_score, carry_model, carry_importance = supervised_analysis(carry_features, "Carry")
    
    # Generate summary
    print("\n" + "="*80)
    print("📋 FINAL SUMMARY")
    print("=" * 80)
    print(f"📊 Dataset: {len(df):,} total events")
    print(f"   - Pass: {len(pass_features):,} events")
    print(f"   - Carry: {len(carry_features):,} events")
    print(f"\n🔍 Unsupervised Results:")
    print(f"   - Pass: {pass_method} (Silhouette: {pass_silhouette:.3f})")
    print(f"   - Carry: {carry_method} (Silhouette: {carry_silhouette:.3f})")
    print(f"\n🎯 Supervised Results:")
    print(f"   - Pass: {pass_model} (Accuracy: {pass_score:.3f})")
    print(f"   - Carry: {carry_model} (Accuracy: {carry_score:.3f})")
    print(f"\n💾 Files Generated:")
    print(f"   - pass_cluster_analysis.csv")
    print(f"   - carry_cluster_analysis.csv")
    print(f"   - pass_feature_importance.csv")
    print(f"   - carry_feature_importance.csv")
    print("\n✅ Analysis Complete!")

if __name__ == "__main__":
    main() 