import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Union
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
from datetime import datetime
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import acf, pacf, adfuller, kpss, grangercausalitytests
from statsmodels.tsa.api import VAR
from statsmodels.stats.stattools import durbin_watson
from statsmodels.stats.multivariate import multivariate_stats
from scipy import stats
from scipy.stats import chi2_contingency, spearmanr, kendalltau
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans, DBSCAN, SpectralClustering
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.sentiment import SentimentIntensityAnalyzer
import networkx as nx
from itertools import combinations, product
import warnings
from ruptures import Bkps  # For change point detection
from hmmlearn import hmm  # For state classification
warnings.filterwarnings('ignore')

class Euro2024EDA:
    def __init__(self, data_path: str):
        """Initialize the EDA class with path to the Euro 2024 dataset."""
        self.data_path = data_path
        self.data = None
        self.output_dir = Path('EDA/outputs')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_data(self) -> None:
        """Load the Euro 2024 dataset."""
        self.data = pd.read_csv(self.data_path)
        self.data['timestamp'] = pd.to_datetime(self.data['match_date']) + \
                                pd.to_timedelta(self.data['minute'], unit='m') + \
                                pd.to_timedelta(self.data['second'], unit='s')
        
    def save_analysis(self, analysis_name: str, results: Dict) -> None:
        """Save analysis results to JSON file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f'{analysis_name}_{timestamp}.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=4)
            
    def basic_statistics(self) -> Dict:
        """Calculate basic dataset statistics."""
        stats = {
            'total_matches': len(self.data['match_id'].unique()),
            'total_events': len(self.data),
            'events_per_match': self.data.groupby('match_id').size().describe().to_dict(),
            'missing_values': self.data.isnull().sum().to_dict(),
            'data_types': self.data.dtypes.astype(str).to_dict()
        }
        self.save_analysis('basic_statistics', stats)
        return stats
    
    def event_distribution(self) -> Dict:
        """Analyze event distribution patterns."""
        event_dist = {
            'event_types': self.data['event_type'].value_counts().to_dict(),
            'period_distribution': self.data['period'].value_counts().to_dict(),
            'time_windows': self.create_time_windows(),
            'team_distribution': self.data['team_name'].value_counts().to_dict()
        }
        self.save_analysis('event_distribution', event_dist)
        return event_dist
    
    def create_time_windows(self, window_size: int = 5) -> Dict:
        """Create time windows for event analysis."""
        self.data['time_window'] = self.data['minute'] // window_size * window_size
        return self.data.groupby('time_window').size().to_dict()
    
    def temporal_analysis(self) -> Dict:
        """Analyze temporal patterns in events."""
        temporal = {
            'inter_event_times': self.calculate_inter_event_times(),
            'event_transitions': self.analyze_event_transitions(),
            'event_density': self.calculate_event_density()
        }
        self.save_analysis('temporal_analysis', temporal)
        return temporal
    
    def calculate_inter_event_times(self) -> Dict:
        """Calculate time between consecutive events."""
        self.data = self.data.sort_values(['match_id', 'minute', 'second'])
        return self.data.groupby('match_id')['minute'].diff().describe().to_dict()
    
    def analyze_event_transitions(self) -> Dict:
        """Analyze transitions between different event types."""
        transitions = pd.crosstab(
            self.data['event_type'],
            self.data['event_type'].shift(-1)
        ).to_dict()
        return transitions
    
    def calculate_event_density(self, window_size: int = 5) -> Dict:
        """Calculate event density over time windows."""
        return self.data.groupby(['match_id', 'time_window']).size().describe().to_dict()
    
    def momentum_analysis(self) -> Dict:
        """Analyze momentum-related patterns."""
        momentum = {
            'goal_patterns': self.analyze_goal_patterns(),
            'pressure_sequences': self.analyze_pressure_sequences(),
            'recovery_patterns': self.analyze_recovery_patterns()
        }
        self.save_analysis('momentum_analysis', momentum)
        return momentum
    
    def analyze_goal_patterns(self) -> Dict:
        """Analyze patterns around goal events."""
        goals = self.data[self.data['event_type'] == 'Goal']
        return {
            'goals_by_period': goals['period'].value_counts().to_dict(),
            'goals_by_time': goals['minute'].describe().to_dict()
        }
    
    def analyze_pressure_sequences(self) -> Dict:
        """Analyze sequences of high-pressure events."""
        # Implementation depends on how pressure is defined in the data
        pass
    
    def analyze_recovery_patterns(self) -> Dict:
        """Analyze team recovery patterns after conceding."""
        # Implementation depends on specific recovery metrics
        pass
    
    def analyze_match_time_structure(self) -> Dict:
        """Analyze game phases and time-based patterns."""
        # Create 15-minute phases
        self.data['phase'] = pd.cut(self.data['minute'], 
                                  bins=[0, 15, 30, 45, 60, 75, 90, np.inf],
                                  labels=['0-15', '15-30', '30-45', '45-60', '60-75', '75-90', 'Extra'])
        
        phase_analysis = {
            'events_per_phase': self.data.groupby('phase').size().to_dict(),
            'high_tempo_periods': self._identify_high_tempo_periods(),
            'halftime_impact': self._analyze_halftime_impact(),
            'injury_time_patterns': self._analyze_injury_time()
        }
        
        self.save_analysis('match_time_structure', phase_analysis)
        return phase_analysis
    
    def _identify_high_tempo_periods(self, window: int = 5) -> Dict:
        """Identify periods of high event frequency."""
        events_per_window = self.data.groupby(['match_id', 
                                             self.data['minute'] // window]).size()
        threshold = events_per_window.mean() + events_per_window.std()
        high_tempo = events_per_window[events_per_window > threshold]
        return {
            'high_tempo_windows': high_tempo.to_dict(),
            'threshold': float(threshold),
            'window_size': window
        }
    
    def analyze_time_series_components(self) -> Dict:
        """Analyze seasonality, periodicity, and autocorrelation."""
        # Resample to minute frequency for time series analysis
        events_ts = self.data.groupby(['match_id', 'minute']).size().reset_index()
        events_ts = events_ts.set_index('minute')
        
        # Decomposition
        decomposition = seasonal_decompose(events_ts[0], period=45)
        
        # Autocorrelation for different lags
        acf_1 = acf(events_ts[0], nlags=1)[1]
        acf_3 = acf(events_ts[0], nlags=3)[1:].mean()
        acf_5 = acf(events_ts[0], nlags=5)[1:].mean()
        
        components = {
            'seasonality': {
                'trend': decomposition.trend.dropna().to_dict(),
                'seasonal': decomposition.seasonal.dropna().to_dict(),
                'resid': decomposition.resid.dropna().to_dict()
            },
            'autocorrelation': {
                '1_minute': float(acf_1),
                '3_minute_avg': float(acf_3),
                '5_minute_avg': float(acf_5)
            },
            'rolling_stats': self._calculate_rolling_stats(events_ts[0])
        }
        
        self.save_analysis('time_series_components', components)
        return components
    
    def _calculate_rolling_stats(self, series: pd.Series, windows: List[int] = [3, 5, 10]) -> Dict:
        """Calculate rolling statistics for different window sizes."""
        stats = {}
        for window in windows:
            stats[f'{window}_min_rolling'] = {
                'mean': series.rolling(window).mean().dropna().to_dict(),
                'std': series.rolling(window).std().dropna().to_dict()
            }
        return stats
    
    def analyze_tactical_changes(self) -> Dict:
        """Analyze tactical changes at tournament and match level."""
        tactical_analysis = {
            'tournament_patterns': self._analyze_tournament_patterns(),
            'match_level_changes': self._analyze_match_changes(),
            'time_specific_tactics': self._analyze_time_tactics()
        }
        
        self.save_analysis('tactical_changes', tactical_analysis)
        return tactical_analysis
    
    def _analyze_tournament_patterns(self) -> Dict:
        """Analyze tactical evolution through tournament."""
        return {
            'stage_tactics': self.data.groupby(['tournament_stage', 'event_type']).size().to_dict(),
            'team_adaptation': self._analyze_team_adaptation(),
            'rest_impact': self._analyze_rest_impact()
        }
    
    def _analyze_match_changes(self) -> Dict:
        """Analyze within-match tactical changes."""
        return {
            'substitutions': self._analyze_substitutions(),
            'cards_impact': self._analyze_cards_impact(),
            'goals_impact': self._analyze_goals_impact()
        }
    
    def analyze_event_categories(self) -> Dict:
        """Analyze different types of events and their interactions."""
        categories = {
            'action_distribution': self._analyze_action_distribution(),
            'category_transitions': self._analyze_category_transitions(),
            'text_analysis': self._analyze_event_text()
        }
        
        self.save_analysis('event_categories', categories)
        return categories
    
    def _analyze_action_distribution(self) -> Dict:
        """Analyze distribution of different action types over time."""
        # Categorize events into attack, midfield, defense
        self.data['action_category'] = self.data['event_type'].map(self._get_action_category())
        
        return {
            'time_distribution': self.data.groupby(['action_category', 
                                                  self.data['minute'] // 5]).size().to_dict(),
            'set_pieces': self._analyze_set_pieces(),
            'transitions': self._analyze_transitions()
        }
    
    def _analyze_event_text(self) -> Dict:
        """Analyze event descriptions and commentary."""
        if 'description' in self.data.columns:
            vectorizer = TfidfVectorizer(max_features=100)
            text_features = vectorizer.fit_transform(self.data['description'])
            
            return {
                'top_terms': dict(zip(vectorizer.get_feature_names_out(), 
                                    text_features.sum(axis=0).A1)),
                'sentiment': self._analyze_text_sentiment(),
                'tactical_terms': self._extract_tactical_terms()
            }
        return {}
    
    def analyze_momentum_flow(self) -> Dict:
        """Analyze momentum patterns and triggers."""
        momentum = {
            'triggers': self._analyze_momentum_triggers(),
            'measurements': self._analyze_momentum_measurements(),
            'autocorrelation': self._analyze_momentum_autocorrelation()
        }
        
        self.save_analysis('momentum_flow', momentum)
        return momentum
    
    def _analyze_momentum_triggers(self) -> Dict:
        """Analyze events that trigger momentum changes."""
        return {
            'goals_impact': self._analyze_goal_momentum(),
            'cards_effect': self._analyze_card_momentum(),
            'substitutions_effect': self._analyze_sub_momentum()
        }
    
    def _analyze_momentum_autocorrelation(self) -> Dict:
        """Analyze autocorrelation in momentum indicators."""
        # Calculate momentum proxy (e.g., rolling event pressure)
        momentum_proxy = self._calculate_momentum_proxy()
        
        return {
            'short_term': float(acf(momentum_proxy, nlags=1)[1]),
            'medium_term': float(acf(momentum_proxy, nlags=3)[1:].mean()),
            'long_term': float(acf(momentum_proxy, nlags=5)[1:].mean())
        }
    
    def create_time_based_features(self) -> Dict:
        """Create time-based features for modeling."""
        features = {
            'rolling_events': self._create_rolling_features(),
            'momentum_velocity': self._calculate_momentum_velocity(),
            'phase_indicators': self._create_phase_indicators()
        }
        
        self.save_analysis('time_based_features', features)
        return features
    
    def create_visualizations(self) -> None:
        """Create required visualizations."""
        self._plot_time_structure()
        self._plot_tactical_changes()
        self._plot_momentum_flow()
        self._plot_autocorrelation()
    
    def _plot_time_structure(self) -> None:
        """Plot match time structure analysis."""
        fig = go.Figure()
        events_by_phase = self.data.groupby('phase').size()
        
        fig.add_trace(go.Bar(x=events_by_phase.index, 
                           y=events_by_phase.values,
                           name='Events per Phase'))
        
        fig.update_layout(title='Match Phase Event Distribution',
                         xaxis_title='Match Phase',
                         yaxis_title='Number of Events')
        
        fig.write_html(self.output_dir / 'time_structure.html')
    
    def analyze_relationships(self) -> Dict:
        """Analyze relationships between variables and subcategories."""
        relationships = {
            'variable_correlations': self._analyze_variable_correlations(),
            'subcategory_analysis': self._analyze_subcategories(),
            'context_relations': self._analyze_context_relations(),
            'multi_level_analysis': self._analyze_multi_level_relationships(),
            'statistical_tests': self._perform_statistical_tests()
        }
        self.save_analysis('relationship_analysis', relationships)
        return relationships

    def _analyze_variable_correlations(self) -> Dict:
        """Analyze correlations between numerical and categorical variables."""
        # Numerical correlations
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        correlation_matrix = self.data[numeric_cols].corr()
        
        # Time-lagged correlations
        lagged_corr = self._calculate_time_lagged_correlations(numeric_cols)
        
        # Categorical associations
        categorical_cols = self.data.select_dtypes(include=['object']).columns
        chi_square_results = self._analyze_categorical_associations(categorical_cols)
        
        return {
            'numeric_correlations': correlation_matrix.to_dict(),
            'time_lagged_correlations': lagged_corr,
            'categorical_associations': chi_square_results,
            'mutual_information': self._calculate_mutual_information()
        }

    def _analyze_subcategories(self) -> Dict:
        """Analyze relationships between different event types and team behaviors."""
        return {
            'event_type_relations': self._analyze_event_type_relationships(),
            'team_comparisons': self._analyze_team_relationships(),
            'tactical_patterns': self._analyze_tactical_relationships(),
            'opposition_analysis': self._analyze_opposition_relationships()
        }

    def _analyze_context_relations(self) -> Dict:
        """Analyze how relationships change under different contexts."""
        return {
            'score_state_impact': self._analyze_score_state_relationships(),
            'time_variations': self._analyze_time_based_relationships(),
            'momentum_dependencies': self._analyze_momentum_relationships(),
            'fatigue_effects': self._analyze_fatigue_impact()
        }

    def _analyze_multi_level_relationships(self) -> Dict:
        """Analyze hierarchical relationships and interaction effects."""
        return {
            'tournament_patterns': self._analyze_tournament_level_relationships(),
            'match_patterns': self._analyze_match_level_relationships(),
            'phase_patterns': self._analyze_phase_level_relationships(),
            'interactions': self._analyze_interaction_effects()
        }

    def _perform_statistical_tests(self) -> Dict:
        """Perform advanced statistical tests on relationships."""
        return {
            'group_comparisons': self._perform_group_comparisons(),
            'non_parametric_tests': self._perform_non_parametric_tests(),
            'effect_sizes': self._calculate_effect_sizes(),
            'bootstrap_analysis': self._perform_bootstrap_analysis()
        }

    def _calculate_time_lagged_correlations(self, columns: List[str], 
                                          max_lag: int = 5) -> Dict:
        """Calculate time-lagged correlations for specified columns."""
        results = {}
        for col in columns:
            lagged_corr = {}
            series = self.data[col]
            for lag in range(1, max_lag + 1):
                corr = series.corr(series.shift(lag))
                lagged_corr[f'lag_{lag}'] = float(corr)
            results[col] = lagged_corr
        return results

    def _analyze_categorical_associations(self, columns: List[str]) -> Dict:
        """Analyze associations between categorical variables."""
        results = {}
        for col1, col2 in combinations(columns, 2):
            contingency = pd.crosstab(self.data[col1], self.data[col2])
            chi2, p_val, dof, expected = chi2_contingency(contingency)
            cramer_v = np.sqrt(chi2 / (len(self.data) * min(contingency.shape)))
            
            results[f'{col1}_vs_{col2}'] = {
                'chi_square': float(chi2),
                'p_value': float(p_val),
                'cramers_v': float(cramer_v)
            }
        return results

    def analyze_advanced_patterns(self) -> Dict:
        """Analyze advanced patterns in the data."""
        patterns = {
            'sequential_patterns': self._analyze_sequential_patterns(),
            'clustering_results': self._perform_advanced_clustering(),
            'pattern_metrics': self._calculate_pattern_metrics(),
            'change_detection': self._detect_pattern_changes()
        }
        self.save_analysis('advanced_patterns', patterns)
        return patterns

    def _analyze_sequential_patterns(self, min_support: float = 0.01) -> Dict:
        """Analyze sequential patterns in events."""
        from mlxtend.frequent_patterns import fpgrowth
        from mlxtend.preprocessing import TransactionEncoder
        
        # Create event sequences
        sequences = self._create_event_sequences()
        
        # Find frequent patterns
        te = TransactionEncoder()
        te_ary = te.fit_transform(sequences)
        df = pd.DataFrame(te_ary, columns=te.columns_)
        
        # Extract patterns
        patterns = fpgrowth(df, min_support=min_support, use_colnames=True)
        
        return {
            'frequent_patterns': patterns.to_dict('records'),
            'pattern_stats': self._calculate_sequence_stats(sequences)
        }

    def _perform_advanced_clustering(self) -> Dict:
        """Perform advanced clustering analysis."""
        # Prepare feature matrix
        features = self._prepare_clustering_features()
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        
        # Dimensionality reduction
        pca = PCA(n_components=0.95)
        pca_result = pca.fit_transform(scaled_features)
        
        # Multiple clustering approaches
        kmeans = KMeans(n_clusters=5, random_state=42)
        dbscan = DBSCAN(eps=0.5, min_samples=5)
        spectral = SpectralClustering(n_clusters=5, random_state=42)
        
        return {
            'kmeans': self._evaluate_clustering(kmeans, pca_result),
            'dbscan': self._evaluate_clustering(dbscan, pca_result),
            'spectral': self._evaluate_clustering(spectral, pca_result)
        }

    def _calculate_pattern_metrics(self) -> Dict:
        """Calculate advanced pattern metrics."""
        return {
            'entropy': self._calculate_pattern_entropy(),
            'complexity': self._calculate_pattern_complexity(),
            'network_metrics': self._calculate_network_metrics(),
            'diversity_indices': self._calculate_diversity_indices()
        }

    def _detect_pattern_changes(self) -> Dict:
        """Detect changes in patterns over time."""
        return {
            'change_points': self._detect_change_points(),
            'regime_switches': self._detect_regime_switches(),
            'anomalies': self._detect_pattern_anomalies(),
            'formation_changes': self._detect_formation_changes()
        }

    def analyze_text_patterns(self) -> Dict:
        """Analyze patterns in text descriptions and commentary."""
        text_patterns = {
            'nlp_analysis': self._perform_nlp_analysis(),
            'semantic_analysis': self._perform_semantic_analysis(),
            'pattern_text_integration': self._integrate_patterns_and_text(),
            'advanced_text_mining': self._perform_advanced_text_mining()
        }
        self.save_analysis('text_patterns', text_patterns)
        return text_patterns

    def _perform_nlp_analysis(self) -> Dict:
        """Perform advanced NLP analysis on text data."""
        if 'description' not in self.data.columns:
            return {}
            
        # Custom tokenization and preprocessing
        processed_text = self._preprocess_football_text()
        
        # Word embeddings
        embeddings = self._create_football_embeddings(processed_text)
        
        return {
            'preprocessing_stats': self._get_preprocessing_stats(),
            'embedding_analysis': self._analyze_embeddings(embeddings),
            'context_windows': self._analyze_context_windows()
        }

    def analyze_zonal_patterns(self) -> Dict:
        """Analyze spatial patterns over time."""
        zonal_analysis = {
            'density_maps': self._create_zone_density_maps(),
            'time_evolution': self._analyze_zone_time_evolution(),
            'transitions': self._analyze_zone_transitions(),
            'momentum_zones': self._analyze_zone_momentum()
        }
        self.save_analysis('zonal_patterns', zonal_analysis)
        return zonal_analysis
    
    def _create_zone_density_maps(self) -> Dict:
        """Create heat maps for different game phases."""
        phases = {
            'first_half': self.data[self.data['period'] == 1],
            'second_half': self.data[self.data['period'] == 2],
            'pre_goal': self._get_pre_goal_events(),
            'post_goal': self._get_post_goal_events(),
            'high_pressure': self._identify_high_pressure_periods()
        }
        
        density_maps = {}
        for phase_name, phase_data in phases.items():
            density_maps[phase_name] = self._generate_heat_map(phase_data)
        return density_maps
    
    def _analyze_zone_time_evolution(self) -> Dict:
        """Analyze how zone usage evolves over time."""
        return {
            'zone_usage_trends': self._calculate_zone_usage_trends(),
            'territorial_control': self._analyze_territorial_control(),
            'tactical_shifts': self._detect_spatial_tactical_shifts()
        }
    
    def _analyze_zone_transitions(self) -> Dict:
        """Analyze transitions between zones."""
        return {
            'transition_matrix': self._calculate_zone_transitions(),
            'preferred_paths': self._identify_preferred_paths(),
            'transition_speeds': self._analyze_transition_speeds()
        }
    
    def _analyze_zone_momentum(self) -> Dict:
        """Analyze momentum indicators by zone."""
        return {
            'zone_pressure': self._calculate_zone_pressure(),
            'momentum_hotspots': self._identify_momentum_hotspots(),
            'zone_control_impact': self._analyze_zone_control_impact()
        }

    def analyze_momentum_changes(self) -> Dict:
        """Enhanced analysis of momentum changes and states."""
        momentum_changes = {
            'change_points': self._detect_momentum_changes(),
            'burst_analysis': self._analyze_bursts_vs_momentum(),
            'state_classification': self._classify_momentum_states(),
            'validation': self._validate_momentum_changes()
        }
        self.save_analysis('momentum_changes', momentum_changes)
        return momentum_changes
    
    def _detect_momentum_changes(self) -> Dict:
        """Detect points of momentum change."""
        # Use ruptures for change point detection
        model = Bkps(model="rbf", min_size=3, jump=1)
        signal = self._create_momentum_signal()
        change_points = model.fit_predict(signal)
        
        return {
            'sudden_shifts': self._analyze_sudden_shifts(change_points),
            'gradual_changes': self._analyze_gradual_changes(signal),
            'decay_patterns': self._analyze_momentum_decay(signal)
        }
    
    def _analyze_bursts_vs_momentum(self) -> Dict:
        """Differentiate between short bursts and sustained momentum."""
        return {
            'burst_characteristics': self._identify_burst_characteristics(),
            'sustained_patterns': self._identify_sustained_patterns(),
            'false_positives': self._identify_false_momentum(),
            'validation_metrics': self._calculate_momentum_validation_metrics()
        }
    
    def _classify_momentum_states(self) -> Dict:
        """Classify different momentum states using HMM."""
        # Use HMM for state classification
        model = hmm.GaussianHMM(n_components=5, covariance_type="full")
        features = self._create_momentum_features()
        states = model.fit_predict(features)
        
        return {
            'state_sequences': self._analyze_state_sequences(states),
            'transition_patterns': self._analyze_state_transitions(states),
            'state_stability': self._analyze_state_stability(states),
            'team_specific_states': self._analyze_team_states(states)
        }
    
    def _validate_momentum_changes(self) -> Dict:
        """Validate detected momentum changes."""
        return {
            'statistical_validation': self._perform_momentum_statistical_tests(),
            'factor_confirmation': self._confirm_multiple_factors(),
            'false_positive_analysis': self._analyze_false_positives(),
            'context_validation': self._validate_context()
        }
    
    def _create_momentum_signal(self) -> np.ndarray:
        """Create a continuous momentum signal from events."""
        # Implement momentum signal creation logic
        pass
    
    def _create_momentum_features(self) -> np.ndarray:
        """Create feature matrix for momentum state classification."""
        features = []
        # Add relevant features:
        # - Event density
        # - Territory control
        # - Shot quality
        # - Pressure indicators
        # - Team dominance metrics
        return np.array(features)
    
    def run_complete_analysis(self) -> None:
        """Run all analysis steps and generate report."""
        self.load_data()
        
        # Run analyses including new components
        zonal_patterns = self.analyze_zonal_patterns()
        momentum_changes = self.analyze_momentum_changes()
        relationships = self.analyze_relationships()
        patterns = self.analyze_advanced_patterns()
        text_patterns = self.analyze_text_patterns()
        
        # Previous analyses
        time_structure = self.analyze_match_time_structure()
        time_series = self.analyze_time_series_components()
        tactical = self.analyze_tactical_changes()
        categories = self.analyze_event_categories()
        momentum = self.analyze_momentum_flow()
        features = self.create_time_based_features()
        
        # Create visualizations
        self.create_visualizations()
        
        # Generate comprehensive report
        report = {
            'timestamp': datetime.now().isoformat(),
            'zonal_analysis': zonal_patterns,
            'momentum_changes': momentum_changes,
            'relationship_analysis': relationships,
            'advanced_patterns': patterns,
            'text_patterns': text_patterns,
            'time_structure_analysis': time_structure,
            'time_series_analysis': time_series,
            'tactical_analysis': tactical,
            'event_categories': categories,
            'momentum_analysis': momentum,
            'engineered_features': features
        }
        
        # Save final report
        self.save_analysis('complete_analysis', report)

if __name__ == '__main__':
    # Initialize and run analysis
    eda = Euro2024EDA('path/to/euro_2024_complete_dataset.csv')
    eda.run_complete_analysis() 