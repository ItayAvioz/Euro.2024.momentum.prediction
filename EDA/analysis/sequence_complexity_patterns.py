#!/usr/bin/env python3
"""
Sequence Complexity Signatures Analysis - Pattern 3
Discover hidden event sequence patterns in Euro 2024 data
Variables: related_events, possession, play_pattern, type, duration
Focus: Event chain complexity and momentum sequence patterns
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

class SequenceComplexityAnalyzer:
    """Analyze sequence complexity patterns in Euro 2024"""
    
    def __init__(self, dataset_path='Data/euro_2024_complete_dataset.csv'):
        """Initialize with full dataset"""
        print("⚡ SEQUENCE COMPLEXITY SIGNATURES - PATTERN 3 ANALYSIS")
        print("=" * 70)
        
        # Load complete dataset
        print("📊 Loading Euro 2024 complete dataset...")
        self.df = pd.read_csv(dataset_path, low_memory=False)
        print(f"   Total events: {len(self.df):,}")
        
        # Extract key fields for sequence analysis
        self.df['event_type'] = self.df['type'].apply(lambda x: eval(x)['name'] if pd.notna(x) and isinstance(x, str) else 'Unknown')
        self.df['play_pattern_name'] = self.df['play_pattern'].apply(lambda x: eval(x)['name'] if pd.notna(x) and isinstance(x, str) else 'Unknown')
        
        # Analyze related_events structure
        related_events_with_data = self.df['related_events'].notna().sum()
        print(f"   Events with related_events: {related_events_with_data:,} ({related_events_with_data/len(self.df)*100:.1f}%)")
        print(f"   Possession sequences: {self.df['possession'].nunique()} unique")
        print(f"   Play patterns: {self.df['play_pattern_name'].nunique()} unique")
        print(f"   Event types: {self.df['event_type'].nunique()} unique")
        
        # Prepare sequence complexity features
        self.prepare_sequence_features()
    
    def prepare_sequence_features(self):
        """Prepare sequence complexity features for clustering"""
        print("\n🔧 PREPARING SEQUENCE COMPLEXITY FEATURES")
        print("-" * 50)
        
        sequence_features = []
        processed = 0
        
        for _, row in self.df.iterrows():
            try:
                processed += 1
                
                # SEQUENCE COMPLEXITY FEATURES
                features = {
                    # RELATED EVENTS COMPLEXITY
                    'has_related_events': 1 if pd.notna(row['related_events']) else 0,
                    'related_events_count': len(eval(row['related_events'])) if pd.notna(row['related_events']) and isinstance(row['related_events'], str) else 0,
                    'is_sequence_start': 1 if (pd.notna(row['related_events']) and len(eval(row['related_events'])) == 0) else 0,
                    'is_chain_event': 1 if (pd.notna(row['related_events']) and len(eval(row['related_events'])) > 0) else 0,
                    
                    # POSSESSION SEQUENCE CONTEXT
                    'possession_id': row['possession'] if pd.notna(row['possession']) else 0,
                    'event_index': row['index'] if pd.notna(row['index']) else 0,
                    
                    # PLAY PATTERN CLASSIFICATION
                    'regular_play': 1 if row['play_pattern_name'] == 'Regular Play' else 0,
                    'from_free_kick': 1 if row['play_pattern_name'] == 'From Free Kick' else 0,
                    'from_corner': 1 if row['play_pattern_name'] == 'From Corner' else 0,
                    'from_throw_in': 1 if row['play_pattern_name'] == 'From Throw In' else 0,
                    'from_kick_off': 1 if row['play_pattern_name'] == 'From Kick Off' else 0,
                    'from_goal_kick': 1 if row['play_pattern_name'] == 'From Goal Kick' else 0,
                    
                    # EVENT TYPE COMPLEXITY
                    'is_pass': 1 if row['event_type'] == 'Pass' else 0,
                    'is_carry': 1 if row['event_type'] == 'Carry' else 0,
                    'is_ball_receipt': 1 if row['event_type'] == 'Ball Receipt*' else 0,
                    'is_pressure': 1 if row['event_type'] == 'Pressure' else 0,
                    'is_shot': 1 if row['event_type'] == 'Shot' else 0,
                    'is_dribble': 1 if row['event_type'] == 'Dribble' else 0,
                    'is_recovery': 1 if row['event_type'] == 'Ball Recovery' else 0,
                    'is_duel': 1 if row['event_type'] == 'Duel' else 0,
                    
                    # DURATION AND TIMING
                    'event_duration': row['duration'] if pd.notna(row['duration']) else 0.0,
                    'has_duration': 1 if (pd.notna(row['duration']) and row['duration'] > 0) else 0,
                    'quick_event': 1 if (pd.notna(row['duration']) and row['duration'] <= 0.1) else 0,
                    'extended_event': 1 if (pd.notna(row['duration']) and row['duration'] > 2.0) else 0,
                    
                    # TEMPORAL CONTEXT
                    'match_minute': row['minute'] if pd.notna(row['minute']) else 0,
                    'match_period': row['period'] if pd.notna(row['period']) else 0,
                    'first_half': 1 if (pd.notna(row['period']) and row['period'] == 1) else 0,
                    'second_half': 1 if (pd.notna(row['period']) and row['period'] == 2) else 0,
                    
                    # Metadata
                    'event_type': row['event_type'],
                    'play_pattern_name': row['play_pattern_name']
                }
                
                sequence_features.append(features)
                
            except Exception:
                continue
        
        self.sequence_df = pd.DataFrame(sequence_features)
        
        print(f"   Events processed: {len(self.sequence_df):,}")
        print(f"   Dataset coverage: {len(self.sequence_df)/len(self.df)*100:.1f}% of total events")
        
        # Analyze sequence complexity statistics
        has_related = self.sequence_df['has_related_events'].sum()
        chain_events = self.sequence_df['is_chain_event'].sum()
        sequence_starts = self.sequence_df['is_sequence_start'].sum()
        
        print(f"   Events with related_events: {has_related:,} ({has_related/len(self.sequence_df)*100:.1f}%)")
        print(f"   Chain events: {chain_events:,} ({chain_events/len(self.sequence_df)*100:.1f}%)")
        print(f"   Sequence starts: {sequence_starts:,} ({sequence_starts/len(self.sequence_df)*100:.1f}%)")
        print(f"   ✅ SEQUENCE COMPLEXITY FEATURES PREPARED")
    
    def find_optimal_k(self, k_min=2, k_max=10):
        """Find optimal number of clusters using silhouette analysis"""
        print(f"\n🔍 K-OPTIMIZATION FOR SEQUENCE COMPLEXITY (K={k_min} to {k_max})")
        print("-" * 60)
        
        # Prepare features for clustering (exclude metadata)
        feature_cols = [col for col in self.sequence_df.columns 
                       if col not in ['event_type', 'play_pattern_name']]
        
        X = self.sequence_df[feature_cols].fillna(0)
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Test different K values
        k_range = range(k_min, k_max + 1)
        silhouette_scores = []
        
        print("Testing K values for optimal clustering...")
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=20)
            cluster_labels = kmeans.fit_predict(X_scaled)
            silhouette_avg = silhouette_score(X_scaled, cluster_labels)
            silhouette_scores.append(silhouette_avg)
            print(f"   K={k:2d}: Silhouette Score = {silhouette_avg:.3f}")
        
        # Find optimal K
        best_k = k_range[np.argmax(silhouette_scores)]
        best_score = max(silhouette_scores)
        
        print(f"\n🎯 OPTIMAL K FOUND:")
        print(f"   Best K: {best_k}")
        print(f"   Best Silhouette Score: {best_score:.3f}")
        
        # Show top 3 K values
        top_indices = np.argsort(silhouette_scores)[-3:][::-1]
        print(f"\n   Top 3 K values:")
        for i, idx in enumerate(top_indices):
            k_val = k_range[idx]
            score = silhouette_scores[idx]
            print(f"   {i+1}. K={k_val}: {score:.3f}")
        
        self.k_scores = list(zip(k_range, silhouette_scores))
        self.best_k = best_k
        self.best_score = best_score
        self.selected_features = feature_cols
        
        return best_k, best_score
    
    def run_optimal_clustering(self):
        """Run clustering with optimal K"""
        print(f"\n⚡ SEQUENCE COMPLEXITY CLUSTERING (K={self.best_k})")
        print("-" * 50)
        
        # Use all features
        X_opt = self.sequence_df[self.selected_features].fillna(0)
        
        # Standardize features
        scaler = StandardScaler()
        X_opt_scaled = scaler.fit_transform(X_opt)
        
        # K-means clustering
        kmeans = KMeans(n_clusters=self.best_k, random_state=42, n_init=20)
        clusters = kmeans.fit_predict(X_opt_scaled)
        
        # Add clusters to dataframe
        self.sequence_df['cluster'] = clusters
        
        print(f"   Events clustered: {len(self.sequence_df):,}")
        print(f"   Features used: {len(self.selected_features)}")
        print(f"   Silhouette score: {self.best_score:.3f}")
        
        # Analyze clusters
        self.analyze_sequence_clusters()
        
        return self.best_score
    
    def analyze_sequence_clusters(self):
        """Analyze the discovered sequence complexity clusters"""
        print(f"\n📊 SEQUENCE COMPLEXITY CLUSTER ANALYSIS")
        print("-" * 60)
        
        cluster_analysis = []
        
        for cluster_id in range(self.best_k):
            cluster_data = self.sequence_df[self.sequence_df['cluster'] == cluster_id]
            size_pct = len(cluster_data) / len(self.sequence_df) * 100
            
            # Key sequence complexity metrics
            related_rate = cluster_data['has_related_events'].mean() * 100
            chain_rate = cluster_data['is_chain_event'].mean() * 100
            avg_related_count = cluster_data['related_events_count'].mean()
            
            # Play pattern distribution
            regular_play_rate = cluster_data['regular_play'].mean() * 100
            set_piece_rate = (cluster_data['from_free_kick'].sum() + cluster_data['from_corner'].sum() + 
                            cluster_data['from_throw_in'].sum() + cluster_data['from_goal_kick'].sum()) / len(cluster_data) * 100
            
            # Event type patterns
            pass_rate = cluster_data['is_pass'].mean() * 100
            pressure_rate = cluster_data['is_pressure'].mean() * 100
            skill_rate = (cluster_data['is_shot'].sum() + cluster_data['is_dribble'].sum()) / len(cluster_data) * 100
            
            # Duration patterns
            avg_duration = cluster_data['event_duration'].mean()
            quick_event_rate = cluster_data['quick_event'].mean() * 100
            
            analysis = {
                'cluster_id': cluster_id,
                'size_pct': size_pct,
                'related_rate': related_rate,
                'chain_rate': chain_rate,
                'avg_related_count': avg_related_count,
                'regular_play_rate': regular_play_rate,
                'set_piece_rate': set_piece_rate,
                'pass_rate': pass_rate,
                'pressure_rate': pressure_rate,
                'skill_rate': skill_rate,
                'avg_duration': avg_duration,
                'quick_event_rate': quick_event_rate,
                'dominant_event': cluster_data['event_type'].mode().iloc[0] if len(cluster_data) > 0 else 'Mixed',
                'dominant_pattern': cluster_data['play_pattern_name'].mode().iloc[0] if len(cluster_data) > 0 else 'Mixed'
            }
            
            cluster_analysis.append(analysis)
            
            print(f"Cluster {cluster_id} ({size_pct:.1f}%): "
                  f"Related:{related_rate:.0f}% | "
                  f"Chain:{chain_rate:.0f}% | "
                  f"Pass:{pass_rate:.0f}% | "
                  f"Pressure:{pressure_rate:.0f}% | "
                  f"Duration:{avg_duration:.2f}s")
        
        self.cluster_analysis = cluster_analysis
        return cluster_analysis
    
    def identify_sequence_patterns(self):
        """Identify key sequence complexity patterns for momentum prediction"""
        print(f"\n🎯 SEQUENCE COMPLEXITY PATTERNS")
        print("-" * 50)
        
        sequence_patterns = []
        
        for cluster in self.cluster_analysis:
            pattern_type = "Unknown"
            complexity_level = "Low"
            momentum_impact = "Low"
            
            # Classify based on sequence complexity
            if cluster['chain_rate'] >= 80:
                if cluster['avg_related_count'] >= 2:
                    pattern_type = "Multi-Chain Sequences"
                    complexity_level = "High"
                    momentum_impact = "High"
                else:
                    pattern_type = "Simple Chain Events"
                    complexity_level = "Medium"
                    momentum_impact = "Medium"
            
            elif cluster['related_rate'] >= 60:
                if cluster['set_piece_rate'] >= 50:
                    pattern_type = "Set Piece Sequences"
                    complexity_level = "Medium"
                    momentum_impact = "Medium"
                else:
                    pattern_type = "Linked Event Patterns"
                    complexity_level = "Medium"
                    momentum_impact = "Medium"
            
            elif cluster['pressure_rate'] >= 40:
                pattern_type = "Pressure Sequence Events"
                complexity_level = "Medium"
                momentum_impact = "High"
            
            elif cluster['pass_rate'] >= 70:
                if cluster['quick_event_rate'] >= 60:
                    pattern_type = "Rapid Pass Sequences"
                    complexity_level = "Low"
                    momentum_impact = "Medium"
                else:
                    pattern_type = "Standard Pass Flow"
                    complexity_level = "Low"
                    momentum_impact = "Low"
            
            elif cluster['skill_rate'] >= 30:
                pattern_type = "Skill Sequence Events"
                complexity_level = "High"
                momentum_impact = "High"
            
            else:
                pattern_type = "Isolated Events"
                complexity_level = "Low"
                momentum_impact = "Low"
            
            pattern = {
                'cluster_id': cluster['cluster_id'],
                'pattern_type': pattern_type,
                'complexity_level': complexity_level,
                'momentum_impact': momentum_impact,
                'size_pct': cluster['size_pct'],
                'related_rate': cluster['related_rate'],
                'dominant_event': cluster['dominant_event'],
                'avg_related_count': cluster['avg_related_count']
            }
            
            sequence_patterns.append(pattern)
            
            print(f"Cluster {cluster['cluster_id']}: {pattern_type} ({cluster['size_pct']:.1f}%) - {complexity_level} complexity, {momentum_impact} momentum impact")
        
        self.sequence_patterns = sequence_patterns
        return sequence_patterns
    
    def generate_examples(self):
        """Generate 5 input/output examples for sequence complexity patterns"""
        print(f"\n📋 SEQUENCE COMPLEXITY EXAMPLES")
        print("-" * 50)
        
        examples = []
        
        # Example 1: Multi-chain sequence
        multi_chain = next((p for p in self.sequence_patterns if 'Multi-Chain' in p['pattern_type']), self.sequence_patterns[0])
        examples.append({
            'id': 1,
            'scenario': 'Complex multi-event sequence with multiple related events',
            'input': {
                'has_related_events': 1,
                'related_events_count': 3,
                'is_chain_event': 1,
                'regular_play': 1,
                'is_pass': 1,
                'event_duration': 1.5,
                'match_minute': 25
            },
            'output': {
                'cluster': multi_chain['cluster_id'],
                'pattern_type': multi_chain['pattern_type'],
                'complexity_level': multi_chain['complexity_level'],
                'momentum_impact': multi_chain['momentum_impact']
            }
        })
        
        # Example 2: Set piece sequence
        set_piece = next((p for p in self.sequence_patterns if 'Set Piece' in p['pattern_type']), self.sequence_patterns[1])
        examples.append({
            'id': 2,
            'scenario': 'Set piece initiated sequence with tactical setup',
            'input': {
                'has_related_events': 1,
                'related_events_count': 1,
                'is_chain_event': 1,
                'from_free_kick': 1,
                'is_pass': 1,
                'event_duration': 0.8,
                'match_minute': 42
            },
            'output': {
                'cluster': set_piece['cluster_id'],
                'pattern_type': set_piece['pattern_type'],
                'complexity_level': set_piece['complexity_level'],
                'momentum_impact': set_piece['momentum_impact']
            }
        })
        
        # Example 3: Pressure sequence
        pressure_seq = next((p for p in self.sequence_patterns if 'Pressure' in p['pattern_type']), self.sequence_patterns[2])
        examples.append({
            'id': 3,
            'scenario': 'High pressure defensive sequence disrupting attack',
            'input': {
                'has_related_events': 0,
                'related_events_count': 0,
                'is_chain_event': 0,
                'regular_play': 1,
                'is_pressure': 1,
                'event_duration': 0.2,
                'match_minute': 67
            },
            'output': {
                'cluster': pressure_seq['cluster_id'],
                'pattern_type': pressure_seq['pattern_type'],
                'complexity_level': pressure_seq['complexity_level'],
                'momentum_impact': pressure_seq['momentum_impact']
            }
        })
        
        # Example 4: Rapid pass sequence
        rapid_pass = next((p for p in self.sequence_patterns if 'Rapid Pass' in p['pattern_type']), self.sequence_patterns[3])
        examples.append({
            'id': 4,
            'scenario': 'Quick passing sequence in buildup play',
            'input': {
                'has_related_events': 1,
                'related_events_count': 1,
                'is_chain_event': 1,
                'regular_play': 1,
                'is_pass': 1,
                'quick_event': 1,
                'event_duration': 0.05,
                'match_minute': 15
            },
            'output': {
                'cluster': rapid_pass['cluster_id'],
                'pattern_type': rapid_pass['pattern_type'],
                'complexity_level': rapid_pass['complexity_level'],
                'momentum_impact': rapid_pass['momentum_impact']
            }
        })
        
        # Example 5: Skill sequence
        skill_seq = next((p for p in self.sequence_patterns if 'Skill' in p['pattern_type']), self.sequence_patterns[4])
        examples.append({
            'id': 5,
            'scenario': 'Individual skill event creating momentum shift',
            'input': {
                'has_related_events': 1,
                'related_events_count': 2,
                'is_chain_event': 1,
                'regular_play': 1,
                'is_dribble': 1,
                'event_duration': 2.1,
                'match_minute': 78
            },
            'output': {
                'cluster': skill_seq['cluster_id'],
                'pattern_type': skill_seq['pattern_type'],
                'complexity_level': skill_seq['complexity_level'],
                'momentum_impact': skill_seq['momentum_impact']
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
            print(f"    complexity_level: {example['output']['complexity_level']}")
            print(f"    momentum_impact: {example['output']['momentum_impact']}")
        
        return examples


def main():
    """Run complete sequence complexity pattern analysis"""
    try:
        # Initialize analyzer with full dataset
        analyzer = SequenceComplexityAnalyzer()
        
        # Find optimal K (K=2 to K=10)
        best_k, best_score = analyzer.find_optimal_k(k_min=2, k_max=10)
        
        # Run optimal clustering
        final_score = analyzer.run_optimal_clustering()
        
        # Identify sequence patterns
        sequence_patterns = analyzer.identify_sequence_patterns()
        
        # Generate examples
        examples = analyzer.generate_examples()
        
        print(f"\n✅ SEQUENCE COMPLEXITY ANALYSIS COMPLETE")
        print(f"   Dataset Coverage: {len(analyzer.sequence_df):,} events ({len(analyzer.sequence_df)/len(analyzer.df)*100:.1f}%)")
        print(f"   Optimal K: {best_k}")
        print(f"   Silhouette Score: {best_score:.3f}")
        print(f"   Sequence Patterns: {len(sequence_patterns)} discovered")
        print(f"   Features: {len(analyzer.selected_features)} sequence complexity features")
        
        return analyzer, sequence_patterns, examples
        
    except Exception as e:
        print(f"❌ Error in sequence complexity analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None, None

if __name__ == "__main__":
    analyzer, patterns, examples = main() 