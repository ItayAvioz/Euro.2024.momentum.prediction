#!/usr/bin/env python3
"""
Pressure-Resistance K-Optimization Analysis
Find the optimal number of clusters for pressure-resistance patterns
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

def main():
    print('PRESSURE-RESISTANCE K-OPTIMIZATION ANALYSIS')
    print('=' * 60)
    
    # Load and prepare data
    df = pd.read_csv('Data/euro_2024_complete_dataset.csv', low_memory=False)
    df['event_type'] = df['type'].apply(lambda x: eval(x)['name'] if pd.notna(x) and isinstance(x, str) else 'Unknown')
    df['position_name'] = df['position'].apply(lambda x: eval(x)['name'] if pd.notna(x) and isinstance(x, str) and x != 'nan' else 'Unknown')
    
    # CORRECT PRESSURE LOGIC: NaN = 0 (no pressure), True = 1 (under pressure)
    df['pressure_binary'] = df['under_pressure'].notna().astype(int)
    
    print('Preparing pressure-resistance features...')
    pressure_features = []
    for _, row in df.dropna(subset=['location']).iterrows():
        try:
            location = eval(row['location']) if isinstance(row['location'], str) else row['location']
            x, y = location[0], location[1]
            if not (0 <= x <= 120 and 0 <= y <= 80): 
                continue
            
            features = {
                'under_pressure': row['pressure_binary'],
                'attacking_third': 1 if x >= 80 else 0,
                'middle_third': 1 if 40 <= x < 80 else 0,
                'defensive_third': 1 if x <= 40 else 0,
                'central_channel': 1 if 26.67 <= y <= 53.33 else 0,
                'wide_areas': 1 if y <= 26.67 or y >= 53.33 else 0,
                'goalkeeper': 1 if 'Goalkeeper' in str(row['position_name']) else 0,
                'center_back': 1 if 'Center Back' in str(row['position_name']) else 0,
                'fullback': 1 if any(pos in str(row['position_name']) for pos in ['Left Back', 'Right Back']) else 0,
                'defensive_mid': 1 if 'Defensive Midfield' in str(row['position_name']) else 0,
                'central_mid': 1 if any(pos in str(row['position_name']) for pos in ['Center Midfield', 'Central Midfield']) else 0,
                'attacking_mid': 1 if 'Attacking Midfield' in str(row['position_name']) else 0,
                'winger': 1 if any(pos in str(row['position_name']) for pos in ['Left Wing', 'Right Wing']) else 0,
                'striker': 1 if any(pos in str(row['position_name']) for pos in ['Striker', 'Center Forward']) else 0,
                'skill_event': 1 if row['event_type'] in ['Dribble', 'Pass', 'Shot', 'Carry'] else 0,
                'contest_event': 1 if row['event_type'] in ['Duel', 'Foul Won', 'Foul Committed'] else 0,
                'recovery_event': 1 if row['event_type'] in ['Ball Recovery', 'Interception', 'Clearance'] else 0,
                'transition_event': 1 if row['event_type'] in ['Ball Receipt', 'Miscontrol', 'Dispossessed'] else 0
            }
            pressure_features.append(features)
        except: 
            continue
    
    pressure_df = pd.DataFrame(pressure_features)
    print(f'Events processed: {len(pressure_df):,}')
    print(f'Dataset coverage: {len(pressure_df)/len(df)*100:.1f}% of total events')
    
    # Prepare features for clustering
    feature_cols = list(pressure_df.columns)
    X = pressure_df[feature_cols].fillna(0)
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    print(f'\nTesting K values from 2 to 15...')
    print('K-VALUE OPTIMIZATION RESULTS:')
    print('-' * 40)
    
    # Test different K values
    k_range = range(2, 16)
    silhouette_scores = []
    
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=20)
        cluster_labels = kmeans.fit_predict(X_scaled)
        silhouette_avg = silhouette_score(X_scaled, cluster_labels)
        silhouette_scores.append(silhouette_avg)
        print(f'K={k:2d}: Silhouette Score = {silhouette_avg:.3f}')
    
    # Find optimal K
    best_k = k_range[np.argmax(silhouette_scores)]
    best_score = max(silhouette_scores)
    
    print(f'\nOPTIMAL K RESULTS:')
    print('=' * 30)
    print(f'Best K: {best_k}')
    print(f'Best Silhouette Score: {best_score:.3f}')
    
    # Show top 3 K values
    top_indices = np.argsort(silhouette_scores)[-3:][::-1]
    print(f'\nTop 3 K values:')
    for i, idx in enumerate(top_indices):
        k_val = k_range[idx]
        score = silhouette_scores[idx]
        print(f'{i+1}. K={k_val}: {score:.3f}')
    
    # Run best K analysis
    print(f'\nRUNNING OPTIMAL K={best_k} ANALYSIS:')
    print('=' * 50)
    
    kmeans_best = KMeans(n_clusters=best_k, random_state=42, n_init=20)
    clusters_best = kmeans_best.fit_predict(X_scaled)
    pressure_df['cluster'] = clusters_best
    
    # Analyze clusters
    print('CLUSTER ANALYSIS:')
    print('-' * 40)
    for cluster_id in range(best_k):
        cluster_data = pressure_df[pressure_df['cluster'] == cluster_id]
        size_pct = len(cluster_data) / len(pressure_df) * 100
        
        pressure_rate = cluster_data['under_pressure'].mean() * 100
        attacking_rate = cluster_data['attacking_third'].mean() * 100
        defensive_rate = cluster_data['defensive_third'].mean() * 100
        skill_rate = cluster_data['skill_event'].mean() * 100
        contest_rate = cluster_data['contest_event'].mean() * 100
        
        print(f'Cluster {cluster_id} ({size_pct:.1f}%): '
              f'Pressure:{pressure_rate:.0f}% | '
              f'Attack:{attacking_rate:.0f}% | '
              f'Defense:{defensive_rate:.0f}% | '
              f'Skill:{skill_rate:.0f}% | '
              f'Contest:{contest_rate:.0f}%')
    
    return best_k, best_score, pressure_df

if __name__ == "__main__":
    best_k, best_score, pressure_df = main() 