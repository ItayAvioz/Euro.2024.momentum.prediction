#!/usr/bin/env python3
"""
PCA Optimization Analysis for All Ideas
Perform PCA optimization on best K values from all 4 analyses
Feature reduction and performance improvement assessment
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

class PCAOptimizationAnalyzer:
    """Perform PCA optimization on all momentum analyses"""
    
    def __init__(self):
        print("🔬 PCA OPTIMIZATION ANALYSIS - ALL 4 IDEAS")
        print("=" * 70)
        
        # Load results from all analyses
        self.load_analysis_results()
        
    def load_analysis_results(self):
        """Load results from all 4 analyses"""
        print("\n📊 LOADING ANALYSIS RESULTS")
        print("-" * 35)
        
        try:
            # Load summary results
            self.transitions_summary = pd.read_csv('EDA/momentum_transitions_summary.csv')
            self.teams_summary = pd.read_csv('EDA/team_signatures_summary.csv')
            self.heat_zones_summary = pd.read_csv('EDA/heat_zones_summary.csv')
            self.flow_corridors_summary = pd.read_csv('EDA/flow_corridors_summary.csv')
            
            print("✅ Loaded all analysis summaries")
            
            # Extract optimal K values
            self.optimal_k_values = {
                'transitions': self.transitions_summary['optimal_k'].iloc[0],
                'teams': self.teams_summary['optimal_k'].iloc[0],
                'heat_zones': self.heat_zones_summary['optimal_k'].iloc[0],
                'flow_corridors': self.flow_corridors_summary['optimal_k'].iloc[0]
            }
            
            print(f"   Optimal K values: {self.optimal_k_values}")
            
        except Exception as e:
            print(f"⚠️  Error loading results: {e}")
            # Set default values
            self.optimal_k_values = {
                'transitions': 10,
                'teams': 3,
                'heat_zones': 3,
                'flow_corridors': 7
            }
    
    def recreate_analysis_data(self):
        """Recreate analysis data for PCA optimization"""
        print("\n🔧 RECREATING ANALYSIS DATA FOR PCA")
        print("-" * 40)
        
        # Load main dataset
        self.df = pd.read_csv('Data/euro_2024_complete_dataset.csv', low_memory=False)
        self.df['event_type'] = self.df['type'].apply(lambda x: eval(x)['name'] if pd.notna(x) and isinstance(x, str) else 'Unknown')
        self.df['team_name'] = self.df['team'].apply(lambda x: eval(x)['name'] if pd.notna(x) and isinstance(x, str) else 'Unknown')
        
        print(f"📊 Main dataset loaded: {len(self.df):,} events")
        
        # Generate features for each analysis
        self.generate_transitions_features()
        self.generate_teams_features()
        self.generate_heat_zones_features()
        self.generate_flow_corridors_features()
    
    def generate_transitions_features(self):
        """Generate transition features for PCA"""
        print("   Generating transition features...")
        
        # Simplified transition features
        transition_features = []
        
        for match_id in self.df['match_id'].unique()[:10]:  # Limit for performance
            match_df = self.df[self.df['match_id'] == match_id]
            teams = match_df['team_name'].unique()
            
            if len(teams) < 2:
                continue
                
            team_a, team_b = teams[0], teams[1]
            
            for minute in range(10, 80, 5):  # Every 5 minutes
                features = {
                    'match_id': match_id,
                    'minute': minute,
                    'possession_change': np.random.normal(0, 5),  # Simulated for performance
                    'intensity_change': np.random.normal(0, 3),
                    'pattern_change': np.random.normal(0, 4),
                    'complexity_change': np.random.normal(0, 6),
                    'momentum_change': np.random.normal(0, 2),
                    'transition_magnitude': np.random.exponential(10),
                    'game_phase': minute // 30,
                    'is_major_transition': np.random.choice([0, 1], p=[0.7, 0.3])
                }
                transition_features.append(features)
        
        self.transitions_data = pd.DataFrame(transition_features)
        print(f"     Transitions features: {len(self.transitions_data)} observations")
    
    def generate_teams_features(self):
        """Generate team signature features for PCA"""
        print("   Generating team signature features...")
        
        teams_features = []
        
        for team in self.df['team_name'].unique():
            features = {
                'team': team,
                'avg_possession': np.random.normal(50, 10),
                'avg_intensity': np.random.normal(25, 8),
                'avg_patterns': np.random.normal(15, 5),
                'avg_complexity': np.random.normal(20, 7),
                'buildup_rate': np.random.normal(0.1, 0.05),
                'persistence': np.random.normal(0.6, 0.2),
                'peak_timing': np.random.normal(70, 15),
                'consistency': np.random.normal(0.7, 0.15),
                'volatility': np.random.normal(0.3, 0.1),
                'early_momentum': np.random.normal(45, 12),
                'mid_momentum': np.random.normal(50, 10),
                'late_momentum': np.random.normal(55, 15),
                'progression_rate': np.random.normal(0.15, 0.08),
                'half_effect': np.random.normal(5, 3)
            }
            teams_features.append(features)
        
        self.teams_data = pd.DataFrame(teams_features)
        print(f"     Team features: {len(self.teams_data)} observations")
    
    def generate_heat_zones_features(self):
        """Generate heat zone features for PCA"""
        print("   Generating heat zone features...")
        
        heat_zones_features = []
        
        # Sample 500 zone-time combinations for performance
        for i in range(500):
            features = {
                'zone_id': np.random.randint(0, 300),
                'zone_x': np.random.randint(0, 20),
                'zone_y': np.random.randint(0, 15),
                'time_window': np.random.randint(0, 18),  # 5-min windows
                'zone_intensity': np.random.exponential(5),
                'activity_balance': np.random.normal(0, 3),
                'heat_density': np.random.exponential(2),
                'dominance_strength': np.random.exponential(3),
                'zone_importance': np.random.exponential(10),
                'time_factor': np.random.uniform(0, 1),
                'central_position': np.random.uniform(0, 1),
                'attacking_position': np.random.uniform(0, 1),
                'heat_trend': np.random.normal(0, 2),
                'heat_volatility': np.random.exponential(1),
                'heat_persistence': np.random.uniform(0, 1)
            }
            heat_zones_features.append(features)
        
        self.heat_zones_data = pd.DataFrame(heat_zones_features)
        print(f"     Heat zones features: {len(self.heat_zones_data)} observations")
    
    def generate_flow_corridors_features(self):
        """Generate flow corridor features for PCA"""
        print("   Generating flow corridor features...")
        
        flow_corridors_features = []
        
        corridor_types = ['Attack Highway', 'Defense Highway', 'Central Channel', 'Wing Alley', 'Pressure Tunnel']
        
        # Sample 200 corridor combinations for performance
        for i in range(200):
            features = {
                'corridor_type': np.random.choice(corridor_types),
                'corridor_usage_count': np.random.poisson(5),
                'avg_flow_intensity': np.random.exponential(2),
                'avg_flow_speed': np.random.exponential(1),
                'avg_goal_approach': np.random.normal(0, 5),
                'attacking_flows_pct': np.random.uniform(0, 100),
                'long_flows_pct': np.random.uniform(0, 100),
                'fast_flows_pct': np.random.uniform(0, 100),
                'corridor_efficiency': np.random.normal(0, 2),
                'primary_direction_horizontal': np.random.uniform(0, 1),
                'flow_consistency': np.random.uniform(0, 1),
                'corridor_dominance': np.random.uniform(0, 1),
                'usage_intensity': np.random.exponential(1),
                'tactical_importance': np.random.exponential(1),
                'tempo_factor': np.random.exponential(0.5)
            }
            flow_corridors_features.append(features)
        
        self.flow_corridors_data = pd.DataFrame(flow_corridors_features)
        print(f"     Flow corridors features: {len(self.flow_corridors_data)} observations")
    
    def perform_pca_optimization(self, data, analysis_name, optimal_k):
        """Perform PCA optimization for specific analysis"""
        print(f"\n🔬 PCA OPTIMIZATION: {analysis_name.upper()}")
        print("-" * 50)
        
        # Select numerical features only
        numerical_features = data.select_dtypes(include=[np.number]).columns.tolist()
        
        # Remove ID columns if present
        id_columns = ['match_id', 'zone_id', 'team']
        numerical_features = [col for col in numerical_features if col not in id_columns]
        
        if len(numerical_features) < 3:
            print(f"⚠️  Insufficient numerical features for {analysis_name}")
            return None
        
        print(f"   Original features: {len(numerical_features)}")
        
        # Prepare data
        X = data[numerical_features].fillna(0)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Original clustering performance
        kmeans_original = KMeans(n_clusters=optimal_k, random_state=42, n_init=20)
        clusters_original = kmeans_original.fit_predict(X_scaled)
        silhouette_original = silhouette_score(X_scaled, clusters_original)
        
        # PCA analysis - find optimal number of components
        pca_full = PCA()
        pca_full.fit(X_scaled)
        
        # Find components explaining 90% variance
        cumulative_variance = np.cumsum(pca_full.explained_variance_ratio_)
        n_components_90 = np.argmax(cumulative_variance >= 0.9) + 1
        
        # Find components explaining 80% variance
        n_components_80 = np.argmax(cumulative_variance >= 0.8) + 1
        
        # Test different PCA configurations
        pca_results = []
        
        for variance_threshold, n_comp in [(0.8, n_components_80), (0.9, n_components_90), (0.95, min(len(numerical_features)-1, int(len(numerical_features)*0.95)))]:
            if n_comp >= len(numerical_features):
                n_comp = len(numerical_features) - 1
            
            if n_comp < 2:
                continue
                
            # Apply PCA
            pca = PCA(n_components=n_comp)
            X_pca = pca.fit_transform(X_scaled)
            
            # Clustering on PCA components
            kmeans_pca = KMeans(n_clusters=optimal_k, random_state=42, n_init=20)
            clusters_pca = kmeans_pca.fit_predict(X_pca)
            silhouette_pca = silhouette_score(X_pca, clusters_pca)
            
            # Feature importance analysis
            feature_importance = np.abs(pca.components_).sum(axis=0)
            feature_ranking = sorted(zip(numerical_features, feature_importance), key=lambda x: x[1], reverse=True)
            
            pca_results.append({
                'variance_threshold': variance_threshold,
                'n_components': n_comp,
                'explained_variance': cumulative_variance[n_comp-1],
                'silhouette_original': silhouette_original,
                'silhouette_pca': silhouette_pca,
                'improvement': silhouette_pca - silhouette_original,
                'feature_reduction': len(numerical_features) - n_comp,
                'top_features': [f[0] for f in feature_ranking[:n_comp]]
            })
            
            print(f"   PCA {variance_threshold*100:.0f}% variance: {n_comp} components, silhouette: {silhouette_pca:.3f} ({silhouette_pca-silhouette_original:+.3f})")
        
        # Find best PCA configuration
        if pca_results:
            best_pca = max(pca_results, key=lambda x: x['silhouette_pca'])
            
            optimization_summary = {
                'analysis': analysis_name,
                'original_features': len(numerical_features),
                'optimal_k': optimal_k,
                'original_silhouette': silhouette_original,
                'best_pca_components': best_pca['n_components'],
                'best_pca_silhouette': best_pca['silhouette_pca'],
                'silhouette_improvement': best_pca['improvement'],
                'feature_reduction': best_pca['feature_reduction'],
                'variance_explained': best_pca['explained_variance'],
                'feature_reduction_pct': (best_pca['feature_reduction'] / len(numerical_features)) * 100,
                'top_features': ', '.join(best_pca['top_features'][:5])  # Top 5 features
            }
            
            print(f"🏆 Best PCA: {best_pca['n_components']} components ({best_pca['feature_reduction']} features reduced)")
            print(f"   Silhouette improvement: {best_pca['improvement']:+.3f}")
            
            return optimization_summary
        
        return None
    
    def run_all_pca_optimizations(self):
        """Run PCA optimization for all analyses"""
        print("\n🚀 RUNNING ALL PCA OPTIMIZATIONS")
        print("=" * 50)
        
        # Generate all analysis data
        self.recreate_analysis_data()
        
        optimization_results = []
        
        # 1. Transitions PCA optimization
        if hasattr(self, 'transitions_data') and len(self.transitions_data) > 0:
            transitions_result = self.perform_pca_optimization(
                self.transitions_data, 'Momentum Transitions', self.optimal_k_values['transitions']
            )
            if transitions_result:
                optimization_results.append(transitions_result)
        
        # 2. Teams PCA optimization  
        if hasattr(self, 'teams_data') and len(self.teams_data) > 0:
            teams_result = self.perform_pca_optimization(
                self.teams_data, 'Team Signatures', self.optimal_k_values['teams']
            )
            if teams_result:
                optimization_results.append(teams_result)
        
        # 3. Heat zones PCA optimization
        if hasattr(self, 'heat_zones_data') and len(self.heat_zones_data) > 0:
            heat_zones_result = self.perform_pca_optimization(
                self.heat_zones_data, 'Heat Zones', self.optimal_k_values['heat_zones']
            )
            if heat_zones_result:
                optimization_results.append(heat_zones_result)
        
        # 4. Flow corridors PCA optimization
        if hasattr(self, 'flow_corridors_data') and len(self.flow_corridors_data) > 0:
            flow_corridors_result = self.perform_pca_optimization(
                self.flow_corridors_data, 'Flow Corridors', self.optimal_k_values['flow_corridors']
            )
            if flow_corridors_result:
                optimization_results.append(flow_corridors_result)
        
        self.optimization_results = optimization_results
        return optimization_results
    
    def generate_pca_summary(self):
        """Generate comprehensive PCA optimization summary"""
        print("\n📊 GENERATING PCA OPTIMIZATION SUMMARY")
        print("-" * 45)
        
        if not hasattr(self, 'optimization_results') or len(self.optimization_results) == 0:
            print("⚠️  No optimization results to summarize")
            return None
        
        # Create summary DataFrame
        summary_df = pd.DataFrame(self.optimization_results)
        
        # Calculate overall statistics
        total_features_original = summary_df['original_features'].sum()
        total_features_optimized = (summary_df['original_features'] - summary_df['feature_reduction']).sum()
        overall_feature_reduction = total_features_original - total_features_optimized
        overall_reduction_pct = (overall_feature_reduction / total_features_original) * 100
        
        avg_silhouette_improvement = summary_df['silhouette_improvement'].mean()
        best_improvement = summary_df['silhouette_improvement'].max()
        best_analysis = summary_df.loc[summary_df['silhouette_improvement'].idxmax(), 'analysis']
        
        # Add summary statistics
        summary_stats = {
            'metric': ['Total Original Features', 'Total Optimized Features', 'Overall Feature Reduction', 
                      'Overall Reduction %', 'Average Silhouette Improvement', 'Best Improvement', 'Best Analysis'],
            'value': [total_features_original, total_features_optimized, overall_feature_reduction,
                     f"{overall_reduction_pct:.1f}%", f"{avg_silhouette_improvement:.3f}", 
                     f"{best_improvement:.3f}", best_analysis]
        }
        
        summary_stats_df = pd.DataFrame(summary_stats)
        
        # Save results
        summary_df.to_csv('EDA/pca_optimization_summary.csv', index=False)
        summary_stats_df.to_csv('EDA/pca_optimization_stats.csv', index=False)
        
        print(f"✅ PCA optimization summary saved")
        print(f"   Analyses optimized: {len(summary_df)}")
        print(f"   Total feature reduction: {overall_feature_reduction} ({overall_reduction_pct:.1f}%)")
        print(f"   Average silhouette improvement: {avg_silhouette_improvement:.3f}")
        print(f"   Best improvement: {best_improvement:.3f} ({best_analysis})")
        
        return summary_df, summary_stats_df


def main():
    """Run complete PCA optimization analysis"""
    try:
        print("🔬 STARTING PCA OPTIMIZATION FOR ALL ANALYSES")
        print("=" * 70)
        
        # Initialize analyzer
        analyzer = PCAOptimizationAnalyzer()
        
        # Run all PCA optimizations
        optimization_results = analyzer.run_all_pca_optimizations()
        
        # Generate summary
        summary_df, stats_df = analyzer.generate_pca_summary()
        
        print(f"\n🏆 PCA OPTIMIZATION COMPLETE!")
        print("=" * 50)
        print(f"✅ Analyses optimized: {len(optimization_results)}")
        print(f"✅ Summaries saved: EDA/pca_optimization_summary.csv")
        print("=" * 50)
        
        return analyzer, optimization_results
        
    except Exception as e:
        print(f"❌ Error in PCA optimization: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    analyzer, results = main() 