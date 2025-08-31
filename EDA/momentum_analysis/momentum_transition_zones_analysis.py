#!/usr/bin/env python3
"""
Momentum Transition Zones Analysis - Idea 1
Find exact 3-minute windows where momentum flips direction for multiple features
Test K=3-10 clustering and assess predictability
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import warnings
warnings.filterwarnings('ignore')

class MomentumTransitionAnalyzer:
    """Detect and analyze momentum transition zones across Euro 2024"""
    
    def __init__(self, dataset_path='Data/euro_2024_complete_dataset.csv'):
        print("🔄 MOMENTUM TRANSITION ZONES ANALYSIS - IDEA 1")
        print("=" * 70)
        
        # Load dataset
        self.df = pd.read_csv(dataset_path, low_memory=False)
        print(f"📊 Dataset: {len(self.df):,} events")
        
        # Extract key fields
        self.df['event_type'] = self.df['type'].apply(lambda x: eval(x)['name'] if pd.notna(x) and isinstance(x, str) else 'Unknown')
        self.df['team_name'] = self.df['team'].apply(lambda x: eval(x)['name'] if pd.notna(x) and isinstance(x, str) else 'Unknown')
        self.df['possession_team_name'] = self.df['possession_team'].apply(lambda x: eval(x)['name'] if pd.notna(x) and isinstance(x, str) else 'Unknown')
        
        print(f"🎮 Matches: {self.df['match_id'].nunique()} matches")
        
    def extract_temporal_features(self):
        """Extract 5 core temporal momentum features by minute"""
        print("\n🔧 EXTRACTING TEMPORAL FEATURES FOR TRANSITION ANALYSIS")
        print("-" * 60)
        
        temporal_data = []
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
            
            # Extract minute-by-minute features
            for minute in range(0, 125):
                minute_events = match_df[match_df['minute'] == minute]
                
                if len(minute_events) == 0:
                    continue
                
                # Get 5-minute window for calculations
                window_5min = match_df[(match_df['minute'] >= max(0, minute - 4)) & (match_df['minute'] <= minute)]
                window_3min = match_df[(match_df['minute'] >= max(0, minute - 2)) & (match_df['minute'] <= minute)]
                
                features = self.calculate_momentum_features(window_5min, window_3min, team_a, team_b, match_id, minute)
                if features:
                    temporal_data.append(features)
        
        self.temporal_df = pd.DataFrame(temporal_data)
        print(f"✅ Extracted {len(self.temporal_df):,} temporal observations")
        return self.temporal_df
    
    def calculate_momentum_features(self, window_5min, window_3min, team_a, team_b, match_id, minute):
        """Calculate 5 core momentum features"""
        try:
            # FEATURE 1: POSSESSION BALANCE (5-min window)
            team_a_poss = len(window_5min[window_5min['possession_team_name'] == team_a])
            team_b_poss = len(window_5min[window_5min['possession_team_name'] == team_b])
            total_poss = team_a_poss + team_b_poss
            
            if total_poss > 0:
                possession_balance = (team_a_poss - team_b_poss) / total_poss * 100
            else:
                possession_balance = 0
            
            # FEATURE 2: INTENSITY BALANCE (3-min window)
            intensity_a = self.calculate_intensity(window_3min, team_a)
            intensity_b = self.calculate_intensity(window_3min, team_b)
            intensity_balance = intensity_a - intensity_b
            
            # FEATURE 3: PATTERN BALANCE (5-min window)
            pattern_a = self.calculate_patterns(window_5min, team_a)
            pattern_b = self.calculate_patterns(window_5min, team_b)
            pattern_balance = pattern_a - pattern_b
            
            # FEATURE 4: COMPLEXITY BALANCE (5-min window)
            complexity_a = self.calculate_complexity(window_5min, team_a)
            complexity_b = self.calculate_complexity(window_5min, team_b)
            complexity_balance = complexity_a - complexity_b
            
            # FEATURE 5: MOMENTUM BALANCE (combined)
            momentum_balance = (
                possession_balance * 0.20 +
                intensity_balance * 0.35 +
                pattern_balance * 0.25 +
                complexity_balance * 0.20
            )
            
            return {
                'match_id': match_id,
                'minute': minute,
                'team_a': team_a,
                'team_b': team_b,
                'possession_balance': possession_balance,
                'intensity_balance': intensity_balance,
                'pattern_balance': pattern_balance,
                'complexity_balance': complexity_balance,
                'momentum_balance': momentum_balance
            }
            
        except Exception as e:
            return None
    
    def calculate_intensity(self, events, team):
        """Calculate event intensity for team"""
        team_events = events[events['team_name'] == team]
        
        intensity_weights = {
            'Pass': 1.0, 'Pressure': 2.0, 'Carry': 1.5, 'Duel': 2.5,
            'Ball Recovery': 2.0, 'Shot': 3.0, 'Dribble': 2.0,
            'Clearance': 1.5, 'Interception': 2.0, 'Block': 2.5
        }
        
        total_intensity = 0
        for event_type, weight in intensity_weights.items():
            count = len(team_events[team_events['event_type'] == event_type])
            total_intensity += count * weight
            
        return total_intensity
    
    def calculate_patterns(self, events, team):
        """Calculate play pattern score"""
        team_events = events[events['team_name'] == team]
        
        if 'play_pattern' not in events.columns:
            return len(team_events) * 1.0  # Fallback
        
        pattern_weights = {
            'Regular Play': 1.0, 'From Free Kick': 1.8, 'From Corner': 2.2,
            'From Throw In': 1.2, 'From Kick Off': 1.5, 'From Goal Kick': 0.8
        }
        
        total_pattern = 0
        for _, event in team_events.iterrows():
            pattern_name = 'Regular Play'  # Default
            if pd.notna(event.get('play_pattern')):
                try:
                    pattern_data = eval(event['play_pattern'])
                    pattern_name = pattern_data.get('name', 'Regular Play')
                except:
                    pass
            
            weight = pattern_weights.get(pattern_name, 1.0)
            total_pattern += weight
            
        return total_pattern
    
    def calculate_complexity(self, events, team):
        """Calculate sequence complexity"""
        team_events = events[events['team_name'] == team]
        
        complexity_score = 0
        for _, event in team_events.iterrows():
            base_score = 1.0
            
            # Related events complexity
            if pd.notna(event.get('related_events')):
                try:
                    related_list = eval(event['related_events'])
                    related_count = len(related_list)
                    
                    if related_count == 0:
                        complexity_score += 0.5
                    elif related_count == 1:
                        complexity_score += 1.5
                    else:
                        complexity_score += 2.5
                except:
                    complexity_score += 0.5
            else:
                complexity_score += 0.5
                
        return complexity_score
    
    def detect_transitions(self):
        """Detect momentum transition zones"""
        print("\n🔄 DETECTING MOMENTUM TRANSITIONS")
        print("-" * 50)
        
        transitions = []
        
        # Group by match for transition detection
        for match_id in self.temporal_df['match_id'].unique():
            match_data = self.temporal_df[self.temporal_df['match_id'] == match_id].sort_values('minute')
            
            if len(match_data) < 6:  # Need at least 6 minutes for 3-minute slopes
                continue
            
            # Calculate 3-minute slopes for each feature
            features = ['possession_balance', 'intensity_balance', 'pattern_balance', 'complexity_balance', 'momentum_balance']
            
            for i in range(3, len(match_data) - 3):  # Start from minute 3, end 3 before last
                current_minute = match_data.iloc[i]['minute']
                
                # Get 3-minute windows (before and after current minute)
                before_window = match_data.iloc[i-3:i]
                after_window = match_data.iloc[i:i+3]
                
                if len(before_window) < 3 or len(after_window) < 3:
                    continue
                
                transition_data = {
                    'match_id': match_id,
                    'minute': current_minute,
                    'team_a': match_data.iloc[i]['team_a'],
                    'team_b': match_data.iloc[i]['team_b']
                }
                
                # Calculate slopes and direction changes
                direction_changes = 0
                total_magnitude = 0
                
                for feature in features:
                    # Before slope (3 minutes before)
                    before_values = before_window[feature].values
                    after_values = after_window[feature].values
                    
                    if len(before_values) >= 2 and len(after_values) >= 2:
                        before_slope = np.polyfit(range(len(before_values)), before_values, 1)[0]
                        after_slope = np.polyfit(range(len(after_values)), after_values, 1)[0]
                        
                        # Direction change detection
                        if (before_slope > 0 and after_slope < 0) or (before_slope < 0 and after_slope > 0):
                            direction_changes += 1
                            total_magnitude += abs(after_slope - before_slope)
                        
                        transition_data[f'{feature}_before_slope'] = before_slope
                        transition_data[f'{feature}_after_slope'] = after_slope
                        transition_data[f'{feature}_direction_change'] = 1 if (before_slope > 0 and after_slope < 0) or (before_slope < 0 and after_slope > 0) else 0
                
                # Transition metrics
                transition_data['transition_count'] = direction_changes
                transition_data['transition_magnitude'] = total_magnitude
                transition_data['is_major_transition'] = 1 if direction_changes >= 3 else 0
                
                # Add current values for context
                for feature in features:
                    transition_data[f'{feature}_current'] = match_data.iloc[i][feature]
                
                transitions.append(transition_data)
        
        self.transitions_df = pd.DataFrame(transitions)
        print(f"✅ Detected {len(self.transitions_df):,} potential transition points")
        print(f"   Major transitions (3+ features): {self.transitions_df['is_major_transition'].sum():,}")
        
        return self.transitions_df
    
    def engineer_transition_features(self):
        """Engineer additional features for transition analysis"""
        print("\n🔧 ENGINEERING TRANSITION FEATURES")
        print("-" * 40)
        
        # Core transition features already calculated
        base_features = ['transition_count', 'transition_magnitude', 'is_major_transition']
        
        # Add derived features
        self.transitions_df['transition_synchrony'] = self.transitions_df['transition_count'] / 5.0  # Proportion of features changing
        
        # Pre-transition stability (average of before slopes)
        slope_features = [col for col in self.transitions_df.columns if 'before_slope' in col]
        self.transitions_df['pre_transition_stability'] = self.transitions_df[slope_features].abs().mean(axis=1)
        
        # Post-transition volatility (average of after slopes)
        after_slope_features = [col for col in self.transitions_df.columns if 'after_slope' in col]
        self.transitions_df['post_transition_volatility'] = self.transitions_df[after_slope_features].abs().mean(axis=1)
        
        # Leading feature (which feature has largest direction change)
        direction_features = [col for col in self.transitions_df.columns if 'direction_change' in col]
        for idx, row in self.transitions_df.iterrows():
            max_change = 0
            leading_feature = 'none'
            
            for feature in ['possession_balance', 'intensity_balance', 'pattern_balance', 'complexity_balance', 'momentum_balance']:
                if row[f'{feature}_direction_change'] == 1:
                    magnitude = abs(row[f'{feature}_after_slope'] - row[f'{feature}_before_slope'])
                    if magnitude > max_change:
                        max_change = magnitude
                        leading_feature = feature
            
            self.transitions_df.at[idx, 'leading_feature_magnitude'] = max_change
        
        # Game phase context
        self.transitions_df['game_phase'] = self.transitions_df['minute'].apply(
            lambda x: 'early' if x <= 30 else 'mid' if x <= 60 else 'late'
        )
        
        # Timing features
        self.transitions_df['is_first_half'] = (self.transitions_df['minute'] <= 45).astype(int)
        self.transitions_df['is_second_half'] = (self.transitions_df['minute'] > 45).astype(int)
        
        print(f"✅ Engineered transition features")
        print(f"   Total features: {len(self.transitions_df.columns)}")
        
        return self.transitions_df
    
    def optimize_transition_clustering(self):
        """Test K=3-10 for optimal transition clustering"""
        print("\n📊 OPTIMIZING TRANSITION CLUSTERING (K=3-10)")
        print("-" * 55)
        
        # Select features for clustering
        clustering_features = [
            'transition_count', 'transition_magnitude', 'transition_synchrony',
            'pre_transition_stability', 'post_transition_volatility', 'leading_feature_magnitude',
            'is_first_half', 'minute'
        ]
        
        # Filter to major transitions for better clustering
        major_transitions = self.transitions_df[self.transitions_df['is_major_transition'] == 1].copy()
        
        if len(major_transitions) < 50:
            print("⚠️  Insufficient major transitions, using all transitions")
            major_transitions = self.transitions_df.copy()
        
        X = major_transitions[clustering_features].fillna(0)
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
            major_transitions[f'cluster_k{k}'] = clusters
            
            # Analyze cluster characteristics
            cluster_analysis = {}
            for cluster_id in range(k):
                cluster_data = major_transitions[major_transitions[f'cluster_k{k}'] == cluster_id]
                
                cluster_analysis[cluster_id] = {
                    'size': len(cluster_data),
                    'avg_transition_count': cluster_data['transition_count'].mean(),
                    'avg_magnitude': cluster_data['transition_magnitude'].mean(),
                    'avg_minute': cluster_data['minute'].mean(),
                    'major_transitions_pct': cluster_data['is_major_transition'].mean() * 100
                }
            
            results.append({
                'k': k,
                'silhouette_score': silhouette,
                'inertia': inertia,
                'cluster_analysis': cluster_analysis
            })
            
            print(f"     Silhouette: {silhouette:.3f}")
        
        self.clustering_results = results
        self.major_transitions_df = major_transitions
        
        # Find optimal K
        best_k = max(results, key=lambda x: x['silhouette_score'])
        print(f"\n🏆 OPTIMAL K: {best_k['k']} (Silhouette: {best_k['silhouette_score']:.3f})")
        
        return results, best_k
    
    def analyze_predictability(self):
        """Analyze transition predictability using 2-minute persistence"""
        print("\n🔮 ANALYZING TRANSITION PREDICTABILITY")
        print("-" * 45)
        
        # Get optimal clustering results
        best_k = max(self.clustering_results, key=lambda x: x['silhouette_score'])
        optimal_clusters = self.major_transitions_df[f'cluster_k{best_k["k"]}']
        
        predictions = []
        
        # For each major transition, check if it was predictable 2 minutes before
        for idx, transition in self.major_transitions_df.iterrows():
            match_id = transition['match_id']
            transition_minute = transition['minute']
            
            # Get data 2 minutes before
            prediction_minute = transition_minute - 2
            
            # Find corresponding temporal data
            temporal_data = self.temporal_df[
                (self.temporal_df['match_id'] == match_id) & 
                (self.temporal_df['minute'] == prediction_minute)
            ]
            
            if len(temporal_data) == 0:
                continue
            
            temporal_row = temporal_data.iloc[0]
            
            # Calculate prediction signals
            features = ['possession_balance', 'intensity_balance', 'pattern_balance', 'complexity_balance', 'momentum_balance']
            
            prediction_signals = 0
            signal_strength = 0
            
            for feature in features:
                current_value = temporal_row[feature]
                transition_value = transition[f'{feature}_current']
                
                # Check if current trend points toward transition
                if abs(current_value) > 5:  # Strong momentum in one direction
                    # Check if transition reverses this momentum
                    if transition[f'{feature}_direction_change'] == 1:
                        prediction_signals += 1
                        signal_strength += abs(current_value)
            
            # Predictability assessment
            predictability_score = prediction_signals / 5.0  # Proportion of features giving signals
            
            predictions.append({
                'match_id': match_id,
                'transition_minute': transition_minute,
                'prediction_minute': prediction_minute,
                'prediction_signals': prediction_signals,
                'predictability_score': predictability_score,
                'signal_strength': signal_strength,
                'transition_magnitude': transition['transition_magnitude'],
                'cluster': optimal_clusters.iloc[idx] if idx < len(optimal_clusters) else -1
            })
        
        self.predictions_df = pd.DataFrame(predictions)
        
        # Calculate overall predictability metrics
        if len(self.predictions_df) > 0:
            avg_predictability = self.predictions_df['predictability_score'].mean()
            high_predictability = (self.predictions_df['predictability_score'] >= 0.6).mean() * 100
            
            print(f"✅ Predictability Analysis Complete")
            print(f"   Average predictability score: {avg_predictability:.3f}")
            print(f"   High predictability (≥60%): {high_predictability:.1f}% of transitions")
            print(f"   Total predictions analyzed: {len(self.predictions_df):,}")
        
        return self.predictions_df
    
    def generate_summary(self):
        """Generate comprehensive summary of transition analysis"""
        print("\n📊 GENERATING COMPREHENSIVE SUMMARY")
        print("-" * 50)
        
        # Get optimal results
        best_k = max(self.clustering_results, key=lambda x: x['silhouette_score'])
        
        summary = {
            'dataset_size': len(self.temporal_df),
            'total_transitions': len(self.transitions_df),
            'major_transitions': self.transitions_df['is_major_transition'].sum(),
            'optimal_k': best_k['k'],
            'optimal_silhouette': best_k['silhouette_score'],
            'avg_predictability': self.predictions_df['predictability_score'].mean() if len(self.predictions_df) > 0 else 0,
            'high_predictability_pct': (self.predictions_df['predictability_score'] >= 0.6).mean() * 100 if len(self.predictions_df) > 0 else 0
        }
        
        # Cluster insights
        cluster_insights = []
        for cluster_id, cluster_data in best_k['cluster_analysis'].items():
            cluster_insights.append({
                'cluster_id': cluster_id,
                'size': cluster_data['size'],
                'avg_transition_count': cluster_data['avg_transition_count'],
                'avg_magnitude': cluster_data['avg_magnitude'],
                'avg_timing': cluster_data['avg_minute'],
                'interpretation': self.interpret_cluster(cluster_data)
            })
        
        summary['cluster_insights'] = cluster_insights
        
        # Save summary
        summary_df = pd.DataFrame([summary])
        summary_df.to_csv('EDA/momentum_transitions_summary.csv', index=False)
        
        print(f"✅ Summary saved: EDA/momentum_transitions_summary.csv")
        
        return summary

    def interpret_cluster(self, cluster_data):
        """Interpret cluster characteristics"""
        avg_count = cluster_data['avg_transition_count']
        avg_magnitude = cluster_data['avg_magnitude']
        avg_minute = cluster_data['avg_minute']
        
        if avg_count >= 4 and avg_magnitude > 10:
            cluster_type = "Major Momentum Shifts"
        elif avg_count >= 3 and avg_minute > 60:
            cluster_type = "Late Game Transitions"
        elif avg_count >= 3 and avg_minute < 30:
            cluster_type = "Early Game Adjustments"
        elif avg_magnitude > 5:
            cluster_type = "Moderate Transitions"
        else:
            cluster_type = "Minor Adjustments"
        
        return cluster_type


def main():
    """Run complete momentum transition zones analysis"""
    try:
        # Initialize analyzer
        analyzer = MomentumTransitionAnalyzer()
        
        # Extract temporal features
        temporal_df = analyzer.extract_temporal_features()
        
        # Detect transitions
        transitions_df = analyzer.detect_transitions()
        
        # Engineer features
        transitions_df = analyzer.engineer_transition_features()
        
        # Optimize clustering
        results, best_k = analyzer.optimize_transition_clustering()
        
        # Analyze predictability
        predictions_df = analyzer.analyze_predictability()
        
        # Generate summary
        summary = analyzer.generate_summary()
        
        print(f"\n🏆 MOMENTUM TRANSITION ZONES ANALYSIS COMPLETE!")
        print("=" * 60)
        print(f"✅ Temporal observations: {len(temporal_df):,}")
        print(f"✅ Transition points: {len(transitions_df):,}")
        print(f"✅ Major transitions: {transitions_df['is_major_transition'].sum():,}")
        print(f"✅ Optimal K: {best_k['k']} (Silhouette: {best_k['silhouette_score']:.3f})")
        print(f"✅ Predictability: {summary['avg_predictability']:.3f}")
        print("=" * 60)
        
        return analyzer, summary
        
    except Exception as e:
        print(f"❌ Error in transition analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    analyzer, summary = main() 