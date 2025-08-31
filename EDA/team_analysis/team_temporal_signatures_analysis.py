#!/usr/bin/env python3
"""
Team-Specific Temporal Signatures Analysis - Idea 2
Create unique momentum DNA profiles for each team
Test K=3-10 clustering and assess team signature distinctiveness
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')

class TeamTemporalSignatureAnalyzer:
    """Analyze team-specific temporal momentum signatures across Euro 2024"""
    
    def __init__(self, dataset_path='Data/euro_2024_complete_dataset.csv'):
        print("🏆 TEAM-SPECIFIC TEMPORAL SIGNATURES ANALYSIS - IDEA 2")
        print("=" * 70)
        
        # Load dataset
        self.df = pd.read_csv(dataset_path, low_memory=False)
        print(f"📊 Dataset: {len(self.df):,} events")
        
        # Extract key fields
        self.df['event_type'] = self.df['type'].apply(lambda x: eval(x)['name'] if pd.notna(x) and isinstance(x, str) else 'Unknown')
        self.df['team_name'] = self.df['team'].apply(lambda x: eval(x)['name'] if pd.notna(x) and isinstance(x, str) else 'Unknown')
        self.df['possession_team_name'] = self.df['possession_team'].apply(lambda x: eval(x)['name'] if pd.notna(x) and isinstance(x, str) else 'Unknown')
        
        print(f"🎮 Matches: {self.df['match_id'].nunique()} matches")
        print(f"⚽ Teams: {self.df['team_name'].nunique()} teams")
        
    def extract_team_temporal_data(self):
        """Extract temporal features for each team across all their matches"""
        print("\n🔧 EXTRACTING TEAM TEMPORAL DATA")
        print("-" * 40)
        
        team_temporal_data = []
        teams_processed = 0
        
        for team in self.df['team_name'].unique():
            teams_processed += 1
            print(f"   Processing team {teams_processed}/{self.df['team_name'].nunique()}: {team}")
            
            team_matches = self.df[self.df['team_name'] == team]['match_id'].unique()
            team_observations = []
            
            # Process each match for this team
            for match_id in team_matches:
                match_df = self.df[self.df['match_id'] == match_id]
                team_match_df = match_df[match_df['team_name'] == team]
                
                # Get opponent
                opponent = match_df[match_df['team_name'] != team]['team_name'].iloc[0] if len(match_df[match_df['team_name'] != team]) > 0 else 'Unknown'
                
                # Extract minute-by-minute features for this team
                for minute in range(0, 125):
                    minute_events = match_df[match_df['minute'] == minute]
                    
                    if len(minute_events) == 0:
                        continue
                    
                    # Get windows for calculations
                    window_5min = match_df[(match_df['minute'] >= max(0, minute - 4)) & (match_df['minute'] <= minute)]
                    window_3min = match_df[(match_df['minute'] >= max(0, minute - 2)) & (match_df['minute'] <= minute)]
                    
                    features = self.calculate_team_minute_features(window_5min, window_3min, team, opponent, match_id, minute)
                    if features:
                        team_observations.append(features)
            
            # Aggregate team temporal signature
            if team_observations:
                team_signature = self.calculate_team_signature(team, team_observations)
                team_temporal_data.append(team_signature)
        
        self.team_signatures_df = pd.DataFrame(team_temporal_data)
        print(f"✅ Extracted signatures for {len(self.team_signatures_df)} teams")
        return self.team_signatures_df
    
    def calculate_team_minute_features(self, window_5min, window_3min, team, opponent, match_id, minute):
        """Calculate momentum features for specific team at specific minute"""
        try:
            team_events_5min = window_5min[window_5min['team_name'] == team]
            opponent_events_5min = window_5min[window_5min['team_name'] == opponent]
            team_events_3min = window_3min[window_3min['team_name'] == team]
            
            # POSSESSION METRICS
            team_possession = len(window_5min[window_5min['possession_team_name'] == team])
            opponent_possession = len(window_5min[window_5min['possession_team_name'] == opponent])
            total_possession = team_possession + opponent_possession
            
            possession_pct = (team_possession / total_possession * 100) if total_possession > 0 else 50
            
            # INTENSITY METRICS
            intensity_score = self.calculate_intensity(team_events_3min)
            
            # PATTERN METRICS
            pattern_score = self.calculate_patterns(team_events_5min)
            
            # COMPLEXITY METRICS
            complexity_score = self.calculate_complexity(team_events_5min)
            
            # MOMENTUM METRICS
            momentum_score = (
                possession_pct * 0.20 +
                intensity_score * 0.35 +
                pattern_score * 0.25 +
                complexity_score * 0.20
            )
            
            return {
                'team': team,
                'opponent': opponent,
                'match_id': match_id,
                'minute': minute,
                'possession_pct': possession_pct,
                'intensity_score': intensity_score,
                'pattern_score': pattern_score,
                'complexity_score': complexity_score,
                'momentum_score': momentum_score,
                'game_phase': 'early' if minute <= 30 else 'mid' if minute <= 60 else 'late',
                'first_half': 1 if minute <= 45 else 0,
                'second_half': 1 if minute > 45 else 0
            }
            
        except Exception as e:
            return None
    
    def calculate_intensity(self, events):
        """Calculate event intensity"""
        intensity_weights = {
            'Pass': 1.0, 'Pressure': 2.0, 'Carry': 1.5, 'Duel': 2.5,
            'Ball Recovery': 2.0, 'Shot': 3.0, 'Dribble': 2.0,
            'Clearance': 1.5, 'Interception': 2.0, 'Block': 2.5
        }
        
        total_intensity = 0
        for event_type, weight in intensity_weights.items():
            count = len(events[events['event_type'] == event_type])
            total_intensity += count * weight
            
        return total_intensity
    
    def calculate_patterns(self, events):
        """Calculate play pattern score"""
        pattern_weights = {
            'Regular Play': 1.0, 'From Free Kick': 1.8, 'From Corner': 2.2,
            'From Throw In': 1.2, 'From Kick Off': 1.5, 'From Goal Kick': 0.8
        }
        
        total_pattern = 0
        for _, event in events.iterrows():
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
    
    def calculate_complexity(self, events):
        """Calculate sequence complexity"""
        complexity_score = 0
        for _, event in events.iterrows():
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
    
    def calculate_team_signature(self, team, observations):
        """Calculate comprehensive team temporal signature"""
        obs_df = pd.DataFrame(observations)
        
        # Basic statistics
        signature = {
            'team': team,
            'total_observations': len(obs_df),
            'matches_played': obs_df['match_id'].nunique()
        }
        
        # Overall averages
        for metric in ['possession_pct', 'intensity_score', 'pattern_score', 'complexity_score', 'momentum_score']:
            signature[f'avg_{metric}'] = obs_df[metric].mean()
            signature[f'std_{metric}'] = obs_df[metric].std()
        
        # Game phase signatures
        for phase in ['early', 'mid', 'late']:
            phase_data = obs_df[obs_df['game_phase'] == phase]
            if len(phase_data) > 0:
                for metric in ['possession_pct', 'intensity_score', 'pattern_score', 'complexity_score', 'momentum_score']:
                    signature[f'{phase}_{metric}'] = phase_data[metric].mean()
            else:
                for metric in ['possession_pct', 'intensity_score', 'pattern_score', 'complexity_score', 'momentum_score']:
                    signature[f'{phase}_{metric}'] = 0
        
        # Half-specific signatures
        first_half = obs_df[obs_df['first_half'] == 1]
        second_half = obs_df[obs_df['second_half'] == 1]
        
        for metric in ['possession_pct', 'intensity_score', 'pattern_score', 'complexity_score', 'momentum_score']:
            signature[f'first_half_{metric}'] = first_half[metric].mean() if len(first_half) > 0 else 0
            signature[f'second_half_{metric}'] = second_half[metric].mean() if len(second_half) > 0 else 0
            signature[f'half_difference_{metric}'] = signature[f'second_half_{metric}'] - signature[f'first_half_{metric}']
        
        # Signature characteristics
        signature['momentum_buildup_rate'] = self.calculate_buildup_rate(obs_df)
        signature['momentum_persistence'] = self.calculate_persistence(obs_df)
        signature['peak_timing_preference'] = self.calculate_peak_timing(obs_df)
        signature['consistency_score'] = self.calculate_consistency(obs_df)
        signature['volatility_index'] = self.calculate_volatility(obs_df)
        
        return signature
    
    def calculate_buildup_rate(self, obs_df):
        """Calculate how fast team builds momentum"""
        if len(obs_df) < 10:
            return 0
        
        # Calculate momentum slope over time
        momentum_values = obs_df.sort_values('minute')['momentum_score'].values
        time_points = range(len(momentum_values))
        
        if len(momentum_values) > 1:
            slope = np.polyfit(time_points, momentum_values, 1)[0]
            return slope
        return 0
    
    def calculate_persistence(self, obs_df):
        """Calculate momentum persistence (autocorrelation)"""
        if len(obs_df) < 5:
            return 0
        
        momentum_series = obs_df.sort_values('minute')['momentum_score']
        
        try:
            # Calculate 2-minute autocorrelation
            autocorr = momentum_series.autocorr(lag=2)
            return autocorr if not np.isnan(autocorr) else 0
        except:
            return 0
    
    def calculate_peak_timing(self, obs_df):
        """Calculate when team typically peaks"""
        if len(obs_df) == 0:
            return 45
        
        # Find minute with highest momentum
        peak_minute = obs_df.loc[obs_df['momentum_score'].idxmax(), 'minute']
        return peak_minute
    
    def calculate_consistency(self, obs_df):
        """Calculate how consistent team's patterns are"""
        if len(obs_df) == 0:
            return 0
        
        # Coefficient of variation for momentum
        momentum_std = obs_df['momentum_score'].std()
        momentum_mean = obs_df['momentum_score'].mean()
        
        if momentum_mean > 0:
            consistency = 1 / (1 + momentum_std / momentum_mean)  # Higher = more consistent
            return consistency
        return 0
    
    def calculate_volatility(self, obs_df):
        """Calculate momentum volatility"""
        if len(obs_df) < 2:
            return 0
        
        # Standard deviation of momentum changes
        momentum_series = obs_df.sort_values('minute')['momentum_score']
        momentum_changes = momentum_series.diff().abs()
        
        return momentum_changes.mean()
    
    def engineer_signature_features(self):
        """Engineer additional signature features"""
        print("\n🔧 ENGINEERING SIGNATURE FEATURES")
        print("-" * 35)
        
        # Signature strength features
        signature_features = []
        
        for idx, team_row in self.team_signatures_df.iterrows():
            features = {}
            
            # Team identification
            features['team'] = team_row['team']
            
            # Core temporal signature (15 features)
            core_metrics = ['possession_pct', 'intensity_score', 'pattern_score', 'complexity_score', 'momentum_score']
            
            for metric in core_metrics:
                features[f'avg_{metric}'] = team_row[f'avg_{metric}']
                features[f'early_{metric}'] = team_row[f'early_{metric}']
                features[f'late_{metric}'] = team_row[f'late_{metric}']
            
            # Progression patterns (5 features)
            for metric in core_metrics:
                features[f'progression_{metric}'] = team_row[f'late_{metric}'] - team_row[f'early_{metric}']
            
            # Signature characteristics (5 features)
            features['buildup_rate'] = team_row['momentum_buildup_rate']
            features['persistence'] = team_row['momentum_persistence']
            features['peak_timing'] = team_row['peak_timing_preference']
            features['consistency'] = team_row['consistency_score']
            features['volatility'] = team_row['volatility_index']
            
            # Half effects (5 features)
            for metric in core_metrics:
                features[f'half_effect_{metric}'] = team_row[f'half_difference_{metric}']
            
            signature_features.append(features)
        
        self.signature_features_df = pd.DataFrame(signature_features)
        print(f"✅ Engineered {len(self.signature_features_df.columns)-1} signature features")
        
        return self.signature_features_df
    
    def optimize_team_clustering(self):
        """Test K=3-10 for optimal team signature clustering"""
        print("\n📊 OPTIMIZING TEAM SIGNATURE CLUSTERING (K=3-10)")
        print("-" * 55)
        
        # Select features for clustering (exclude team name)
        clustering_features = [col for col in self.signature_features_df.columns if col != 'team']
        
        X = self.signature_features_df[clustering_features].fillna(0)
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
            self.signature_features_df[f'cluster_k{k}'] = clusters
            
            # Analyze cluster characteristics
            cluster_analysis = {}
            for cluster_id in range(k):
                cluster_teams = self.signature_features_df[self.signature_features_df[f'cluster_k{k}'] == cluster_id]
                
                cluster_analysis[cluster_id] = {
                    'size': len(cluster_teams),
                    'teams': cluster_teams['team'].tolist(),
                    'avg_buildup_rate': cluster_teams['buildup_rate'].mean(),
                    'avg_persistence': cluster_teams['persistence'].mean(),
                    'avg_peak_timing': cluster_teams['peak_timing'].mean(),
                    'avg_momentum': cluster_teams['avg_momentum_score'].mean()
                }
            
            results.append({
                'k': k,
                'silhouette_score': silhouette,
                'inertia': inertia,
                'cluster_analysis': cluster_analysis
            })
            
            print(f"     Silhouette: {silhouette:.3f}")
        
        self.clustering_results = results
        
        # Find optimal K
        best_k = max(results, key=lambda x: x['silhouette_score'])
        print(f"\n🏆 OPTIMAL K: {best_k['k']} (Silhouette: {best_k['silhouette_score']:.3f})")
        
        return results, best_k
    
    def calculate_team_similarities(self):
        """Calculate similarity matrix between all teams"""
        print("\n🔗 CALCULATING TEAM SIMILARITY MATRIX")
        print("-" * 40)
        
        # Use signature features for similarity calculation
        clustering_features = [col for col in self.signature_features_df.columns if col != 'team']
        X = self.signature_features_df[clustering_features].fillna(0)
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Calculate cosine similarity
        similarity_matrix = cosine_similarity(X_scaled)
        
        # Create similarity dataframe
        teams = self.signature_features_df['team'].tolist()
        similarity_df = pd.DataFrame(similarity_matrix, index=teams, columns=teams)
        
        self.similarity_matrix = similarity_df
        
        # Find most and least similar teams
        similarities = []
        for i, team1 in enumerate(teams):
            for j, team2 in enumerate(teams):
                if i < j:  # Avoid duplicates
                    similarity = similarity_matrix[i][j]
                    similarities.append({
                        'team1': team1,
                        'team2': team2,
                        'similarity': similarity
                    })
        
        similarities_df = pd.DataFrame(similarities)
        
        # Most similar teams
        most_similar = similarities_df.nlargest(5, 'similarity')
        least_similar = similarities_df.nsmallest(5, 'similarity')
        
        print(f"✅ Team similarity matrix calculated")
        print(f"   Most similar teams:")
        for _, row in most_similar.iterrows():
            print(f"     {row['team1']} ↔ {row['team2']}: {row['similarity']:.3f}")
        
        return similarity_df, most_similar, least_similar
    
    def analyze_signature_predictability(self):
        """Analyze how well signatures predict team behavior"""
        print("\n🔮 ANALYZING SIGNATURE PREDICTABILITY")
        print("-" * 40)
        
        predictability_scores = []
        
        for _, team_row in self.signature_features_df.iterrows():
            team = team_row['team']
            
            # Calculate signature distinctiveness
            other_teams = self.signature_features_df[self.signature_features_df['team'] != team]
            
            # Feature consistency (how stable team's patterns are)
            consistency = team_row['consistency']
            
            # Signature uniqueness (how different from other teams)
            team_similarity_scores = []
            if len(other_teams) > 0:
                for _, other_team in other_teams.iterrows():
                    # Calculate feature distance
                    feature_cols = [col for col in self.signature_features_df.columns if col != 'team' and 'cluster' not in col]
                    
                    team_features = team_row[feature_cols].fillna(0).values
                    other_features = other_team[feature_cols].fillna(0).values
                    
                    # Cosine similarity
                    similarity = np.dot(team_features, other_features) / (np.linalg.norm(team_features) * np.linalg.norm(other_features) + 1e-10)
                    team_similarity_scores.append(similarity)
                
                uniqueness = 1 - np.mean(team_similarity_scores)  # Lower similarity = higher uniqueness
            else:
                uniqueness = 1.0
            
            # Signature strength (combination of consistency and uniqueness)
            signature_strength = (consistency * 0.6 + uniqueness * 0.4)
            
            # Peak timing predictability
            peak_timing = team_row['peak_timing']
            timing_predictability = 1.0 if 60 <= peak_timing <= 80 else 0.8 if 30 <= peak_timing <= 90 else 0.6
            
            # Overall predictability
            predictability = (signature_strength * 0.7 + timing_predictability * 0.3)
            
            predictability_scores.append({
                'team': team,
                'consistency': consistency,
                'uniqueness': uniqueness,
                'signature_strength': signature_strength,
                'timing_predictability': timing_predictability,
                'overall_predictability': predictability
            })
        
        self.predictability_df = pd.DataFrame(predictability_scores)
        
        avg_predictability = self.predictability_df['overall_predictability'].mean()
        high_predictability = (self.predictability_df['overall_predictability'] >= 0.7).mean() * 100
        
        print(f"✅ Signature predictability analyzed")
        print(f"   Average predictability: {avg_predictability:.3f}")
        print(f"   High predictability (≥70%): {high_predictability:.1f}% of teams")
        
        return self.predictability_df
    
    def generate_summary(self):
        """Generate comprehensive summary"""
        print("\n📊 GENERATING COMPREHENSIVE SUMMARY")
        print("-" * 40)
        
        # Get optimal results
        best_k = max(self.clustering_results, key=lambda x: x['silhouette_score'])
        
        summary = {
            'total_teams': len(self.team_signatures_df),
            'total_observations': self.team_signatures_df['total_observations'].sum(),
            'optimal_k': best_k['k'],
            'optimal_silhouette': best_k['silhouette_score'],
            'avg_predictability': self.predictability_df['overall_predictability'].mean(),
            'avg_signature_strength': self.predictability_df['signature_strength'].mean(),
            'high_predictability_pct': (self.predictability_df['overall_predictability'] >= 0.7).mean() * 100
        }
        
        # Save summary
        summary_df = pd.DataFrame([summary])
        summary_df.to_csv('EDA/team_signatures_summary.csv', index=False)
        
        print(f"✅ Summary saved: EDA/team_signatures_summary.csv")
        
        return summary


def main():
    """Run complete team temporal signatures analysis"""
    try:
        # Initialize analyzer
        analyzer = TeamTemporalSignatureAnalyzer()
        
        # Extract team temporal data
        team_signatures = analyzer.extract_team_temporal_data()
        
        # Engineer signature features
        signature_features = analyzer.engineer_signature_features()
        
        # Optimize clustering
        results, best_k = analyzer.optimize_team_clustering()
        
        # Calculate similarities
        similarity_matrix, most_similar, least_similar = analyzer.calculate_team_similarities()
        
        # Analyze predictability
        predictability = analyzer.analyze_signature_predictability()
        
        # Generate summary
        summary = analyzer.generate_summary()
        
        print(f"\n🏆 TEAM TEMPORAL SIGNATURES ANALYSIS COMPLETE!")
        print("=" * 60)
        print(f"✅ Teams analyzed: {len(team_signatures)}")
        print(f"✅ Total observations: {team_signatures['total_observations'].sum():,}")
        print(f"✅ Optimal K: {best_k['k']} (Silhouette: {best_k['silhouette_score']:.3f})")
        print(f"✅ Avg predictability: {summary['avg_predictability']:.3f}")
        print("=" * 60)
        
        return analyzer, summary
        
    except Exception as e:
        print(f"❌ Error in team signatures analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    analyzer, summary = main() 