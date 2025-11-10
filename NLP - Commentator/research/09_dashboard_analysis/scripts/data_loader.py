"""
Data Loader for Commentary Analysis Dashboard

This module loads and processes all comparison CSV files,
selecting the best generated commentary for each real commentary.

Author: AI Assistant
Date: November 10, 2025
"""

import os
import pandas as pd
from pathlib import Path
import streamlit as st


class CommentaryDataLoader:
    """Load and process commentary comparison data."""
    
    def __init__(self):
        """Initialize the data loader."""
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.script_dir, '..', '..', '08_enhanced_comparison', 'data')
        self.all_data = None
        self.best_matches = None
        
    @st.cache_data
    def load_all_data(_self):
        """
        Load all comparison CSV files.
        
        Returns:
            pd.DataFrame: Combined data from all CSV files
        """
        csv_files = list(Path(_self.data_dir).glob('match_*_enhanced_comparison.csv'))
        
        if len(csv_files) == 0:
            st.error("No comparison CSV files found!")
            return None
        
        all_dfs = []
        
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                
                # Extract match_id and source from filename
                # Format: match_{ID}_{source}_enhanced_comparison.csv
                filename = csv_file.stem  # removes .csv
                parts = filename.split('_')
                match_id = parts[1]
                source = '_'.join(parts[2:-2])  # everything between match_id and "enhanced"
                
                df['match_id'] = match_id
                df['source'] = source.upper()
                
                all_dfs.append(df)
                
            except Exception as e:
                st.warning(f"Failed to load {csv_file.name}: {str(e)}")
                continue
        
        if len(all_dfs) == 0:
            st.error("Failed to load any CSV files!")
            return None
        
        combined_df = pd.concat(all_dfs, ignore_index=True)
        
        return combined_df
    
    @st.cache_data
    def get_best_matches(_self, score_type='average_score'):
        """
        For each unique real commentary, select the best generated match.
        
        Args:
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            pd.DataFrame: Best matches only
        """
        if _self.all_data is None:
            _self.all_data = _self.load_all_data()
        
        if _self.all_data is None:
            return None
        
        # Filter out rows with no generated commentary (sequence_id == -1)
        df = _self.all_data[_self.all_data['sequence_id'] != -1].copy()
        
        # Group by unique real commentary and select best match
        # Unique key: (source, match_id, minute, real_commentary)
        best_matches = (
            df.sort_values(score_type, ascending=False)
            .groupby(['source', 'match_id', 'minute', 'real_commentary'], as_index=False)
            .first()
        )
        
        return best_matches
    
    def get_general_info(self):
        """
        Get general information about the dataset.
        
        Returns:
            dict: General statistics
        """
        if self.all_data is None:
            self.all_data = self.load_all_data()
        
        if self.all_data is None:
            return {}
        
        # Count unique matches
        unique_matches = self.all_data['match_id'].nunique()
        
        # Count unique sources
        sources = self.all_data['source'].unique()
        
        # Games per source
        games_per_source = (
            self.all_data.groupby('source')['match_id']
            .nunique()
            .sort_values(ascending=False)
        )
        
        # Total comparisons
        total_comparisons = len(self.all_data)
        
        # Comparisons with generated commentary
        with_commentary = len(self.all_data[self.all_data['sequence_id'] != -1])
        
        return {
            'total_games': unique_matches,
            'total_sources': len(sources),
            'sources_list': sorted(sources.tolist()),
            'games_per_source': games_per_source,
            'total_comparisons': total_comparisons,
            'comparisons_with_commentary': with_commentary,
            'total_csv_files': len(list(Path(self.data_dir).glob('match_*_enhanced_comparison.csv')))
        }
    
    def get_summary_statistics(self, score_type='average_score'):
        """
        Calculate summary statistics for best matches.
        
        Args:
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            dict: Summary statistics
        """
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        # Calculate means for key metrics
        metrics = {
            'TF-IDF': best_matches['TF-IDF'].mean(),
            'Embeddings_BERT': best_matches['Embeddings_BERT'].mean(),
            'content_overlap_ratio': best_matches['content_overlap_ratio'].mean(),
            'sentiment_diff': best_matches['sentiment_diff'].mean(),
            'avg_score': best_matches['average_score'].mean(),
            'average_score_no_sentiment': best_matches['average_score_no_sentiment'].mean(),
            'commentary_count': len(best_matches),
            'unique_games': best_matches['match_id'].nunique(),
            'total_comparison_files': 69  # Total comparison CSVs (51 FlashScore + 6 SportsMole + 4 BBC + 4 FOX + 4 ESPN)
        }
        
        # Commentary per game average (divide by total comparison files, not unique matches)
        metrics['commentary_avg_per_game'] = metrics['commentary_count'] / metrics['total_comparison_files']
        
        # Word count averages
        metrics['real_word_count_avg'] = best_matches['real_word_count'].mean()
        metrics['generated_word_count_avg'] = best_matches['our_word_count'].mean()
        
        return metrics
    
    def get_overlap_percentage(self):
        """
        Calculate percentage where best by average_score == best by average_score_no_sentiment.
        
        Returns:
            float: Overlap percentage
        """
        # Get best matches by both methods
        best_with_sentiment = self.get_best_matches('average_score')
        best_without_sentiment = self.get_best_matches('average_score_no_sentiment')
        
        if best_with_sentiment is None or best_without_sentiment is None:
            return 0.0
        
        # Create unique keys for comparison
        best_with_sentiment['key'] = (
            best_with_sentiment['source'] + '_' + 
            best_with_sentiment['match_id'] + '_' + 
            best_with_sentiment['minute'].astype(str) + '_' +
            best_with_sentiment['real_commentary']
        )
        
        best_without_sentiment['key'] = (
            best_without_sentiment['source'] + '_' + 
            best_without_sentiment['match_id'] + '_' + 
            best_without_sentiment['minute'].astype(str) + '_' +
            best_without_sentiment['real_commentary']
        )
        
        # Create mapping of key to sequence_id
        with_sentiment_map = dict(zip(best_with_sentiment['key'], best_with_sentiment['sequence_id']))
        without_sentiment_map = dict(zip(best_without_sentiment['key'], best_without_sentiment['sequence_id']))
        
        # Count matches
        total_keys = len(with_sentiment_map)
        matching_keys = sum(
            1 for key in with_sentiment_map 
            if key in without_sentiment_map and with_sentiment_map[key] == without_sentiment_map[key]
        )
        
        overlap_pct = (matching_keys / total_keys * 100) if total_keys > 0 else 0.0
        
        return overlap_pct
    
    def get_bert_distribution(self, score_type='average_score'):
        """
        Get Embeddings_BERT distribution data for histogram.
        
        Args:
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            list: BERT similarity scores
        """
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return []
        
        return best_matches['Embeddings_BERT'].dropna().tolist()
    
    def get_sentiment_counts(self, score_type='average_score'):
        """
        Count commentaries by sentiment categories (negative, neutral, positive).
        
        Args:
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            dict: Counts for each sentiment category for real and generated
        """
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        # Real sentiment counts
        real_negative = (best_matches['real_sentiment'] < 0).sum()
        real_neutral = (best_matches['real_sentiment'] == 0).sum()
        real_positive = (best_matches['real_sentiment'] > 0).sum()
        
        # Generated sentiment counts
        our_negative = (best_matches['our_sentiment'] < 0).sum()
        our_neutral = (best_matches['our_sentiment'] == 0).sum()
        our_positive = (best_matches['our_sentiment'] > 0).sum()
        
        return {
            'real': {
                'negative': real_negative,
                'neutral': real_neutral,
                'positive': real_positive
            },
            'generated': {
                'negative': our_negative,
                'neutral': our_neutral,
                'positive': our_positive
            }
        }
    
    def get_sentiment_sign_agreement(self, score_type='average_score'):
        """
        Calculate percentage where real and generated have the same sentiment sign.
        
        Args:
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            dict: Agreement statistics
        """
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        # Create sign categories (-1, 0, 1)
        real_sign = best_matches['real_sentiment'].apply(lambda x: -1 if x < 0 else (1 if x > 0 else 0))
        our_sign = best_matches['our_sentiment'].apply(lambda x: -1 if x < 0 else (1 if x > 0 else 0))
        
        # Count agreements
        total = len(best_matches)
        same_sign = (real_sign == our_sign).sum()
        both_negative = ((real_sign == -1) & (our_sign == -1)).sum()
        both_neutral = ((real_sign == 0) & (our_sign == 0)).sum()
        both_positive = ((real_sign == 1) & (our_sign == 1)).sum()
        
        return {
            'total': total,
            'same_sign': same_sign,
            'same_sign_pct': (same_sign / total * 100) if total > 0 else 0,
            'both_negative': both_negative,
            'both_neutral': both_neutral,
            'both_positive': both_positive,
            'different_sign': total - same_sign,
            'different_sign_pct': ((total - same_sign) / total * 100) if total > 0 else 0
        }
    
    def get_real_type_counts(self):
        """
        Get counts of each real_type (counting each real commentary only once).
        
        Returns:
            dict: Real type counts sorted by frequency
        """
        # Use best matches to count each real commentary only once
        # We'll use 'average_score' as the default, but it doesn't matter which method
        # since we're just counting unique real commentaries
        best_matches = self.get_best_matches('average_score')
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        # Count real_type occurrences from best matches (unique real commentaries)
        type_counts = best_matches['real_type'].value_counts().to_dict()
        
        return type_counts
    
    def get_best_matches_by_type(self, real_type, score_type='average_score'):
        """
        Get best matches filtered by real_type.
        
        Args:
            real_type: The real_type to filter by
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            pd.DataFrame: Filtered best matches
        """
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return None
        
        # Filter by real_type
        filtered = best_matches[best_matches['real_type'] == real_type]
        
        return filtered if len(filtered) > 0 else None
    
    def get_summary_statistics_by_type(self, real_type, score_type='average_score'):
        """
        Calculate summary statistics for a specific real_type.
        
        Args:
            real_type: The real_type to filter by
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            dict: Summary statistics
        """
        best_matches = self.get_best_matches_by_type(real_type, score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        # Calculate metrics
        metrics = {
            'TF-IDF': best_matches['TF-IDF'].mean(),
            'Embeddings_BERT': best_matches['Embeddings_BERT'].mean(),
            'content_overlap_ratio': best_matches['content_overlap_ratio'].mean(),
            'sentiment_diff': best_matches['sentiment_diff'].mean(),
            'avg_score': best_matches['average_score'].mean(),
            'average_score_no_sentiment': best_matches['average_score_no_sentiment'].mean(),
            'commentary_count': len(best_matches),
        }
        
        # Word count averages
        metrics['real_word_count_avg'] = best_matches['real_word_count'].mean()
        metrics['generated_word_count_avg'] = best_matches['our_word_count'].mean()
        
        return metrics
    
    def get_bert_distribution_by_type(self, real_type, score_type='average_score'):
        """
        Get Embeddings_BERT distribution data for a specific real_type.
        
        Args:
            real_type: The real_type to filter by
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            list: BERT similarity scores
        """
        best_matches = self.get_best_matches_by_type(real_type, score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return []
        
        return best_matches['Embeddings_BERT'].dropna().tolist()
    
    def get_sentiment_counts_by_type(self, real_type, score_type='average_score'):
        """
        Count commentaries by sentiment categories for a specific real_type.
        
        Args:
            real_type: The real_type to filter by
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            dict: Counts for each sentiment category
        """
        best_matches = self.get_best_matches_by_type(real_type, score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        # Real sentiment counts
        real_negative = (best_matches['real_sentiment'] < 0).sum()
        real_neutral = (best_matches['real_sentiment'] == 0).sum()
        real_positive = (best_matches['real_sentiment'] > 0).sum()
        
        # Generated sentiment counts
        our_negative = (best_matches['our_sentiment'] < 0).sum()
        our_neutral = (best_matches['our_sentiment'] == 0).sum()
        our_positive = (best_matches['our_sentiment'] > 0).sum()
        
        return {
            'real': {
                'negative': real_negative,
                'neutral': real_neutral,
                'positive': real_positive
            },
            'generated': {
                'negative': our_negative,
                'neutral': our_neutral,
                'positive': our_positive
            }
        }
    
    def get_sentiment_sign_agreement_by_type(self, real_type, score_type='average_score'):
        """
        Calculate sentiment sign agreement for a specific real_type.
        
        Args:
            real_type: The real_type to filter by
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            dict: Agreement statistics
        """
        best_matches = self.get_best_matches_by_type(real_type, score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        # Create sign categories (-1, 0, 1)
        real_sign = best_matches['real_sentiment'].apply(lambda x: -1 if x < 0 else (1 if x > 0 else 0))
        our_sign = best_matches['our_sentiment'].apply(lambda x: -1 if x < 0 else (1 if x > 0 else 0))
        
        # Count agreements
        total = len(best_matches)
        same_sign = (real_sign == our_sign).sum()
        both_negative = ((real_sign == -1) & (our_sign == -1)).sum()
        both_neutral = ((real_sign == 0) & (our_sign == 0)).sum()
        both_positive = ((real_sign == 1) & (our_sign == 1)).sum()
        
        return {
            'total': total,
            'same_sign': same_sign,
            'same_sign_pct': (same_sign / total * 100) if total > 0 else 0,
            'both_negative': both_negative,
            'both_neutral': both_neutral,
            'both_positive': both_positive,
            'different_sign': total - same_sign,
            'different_sign_pct': ((total - same_sign) / total * 100) if total > 0 else 0
        }
    
    def get_bert_range_counts(self):
        """
        Get counts for BERT score ranges.
        
        Returns:
            dict: Counts for each BERT range
        """
        best_matches = self.get_best_matches('average_score')
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        # Categorize by BERT score ranges
        low = (best_matches['Embeddings_BERT'] < 0.45).sum()
        medium = ((best_matches['Embeddings_BERT'] >= 0.45) & (best_matches['Embeddings_BERT'] <= 0.55)).sum()
        high = (best_matches['Embeddings_BERT'] > 0.55).sum()
        
        return {
            'Low (< 0.45)': low,
            'Medium (0.45-0.55)': medium,
            'High (> 0.55)': high
        }
    
    def get_best_matches_by_bert_range(self, range_type, score_type='average_score'):
        """
        Get best matches filtered by BERT score range.
        
        Args:
            range_type: 'Low (< 0.45)', 'Medium (0.45-0.55)', or 'High (> 0.55)'
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            pd.DataFrame: Filtered best matches
        """
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return None
        
        # Filter by BERT range
        if range_type == 'Low (< 0.45)':
            filtered = best_matches[best_matches['Embeddings_BERT'] < 0.45]
        elif range_type == 'Medium (0.45-0.55)':
            filtered = best_matches[(best_matches['Embeddings_BERT'] >= 0.45) & (best_matches['Embeddings_BERT'] <= 0.55)]
        elif range_type == 'High (> 0.55)':
            filtered = best_matches[best_matches['Embeddings_BERT'] > 0.55]
        else:
            return None
        
        return filtered if len(filtered) > 0 else None
    
    def get_summary_statistics_by_bert_range(self, range_type, score_type='average_score'):
        """
        Calculate summary statistics for a specific BERT range.
        
        Args:
            range_type: 'Low (< 0.45)', 'Medium (0.45-0.55)', or 'High (> 0.55)'
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            dict: Summary statistics
        """
        best_matches = self.get_best_matches_by_bert_range(range_type, score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        # Calculate metrics
        metrics = {
            'TF-IDF': best_matches['TF-IDF'].mean(),
            'Embeddings_BERT': best_matches['Embeddings_BERT'].mean(),
            'content_overlap_ratio': best_matches['content_overlap_ratio'].mean(),
            'sentiment_diff': best_matches['sentiment_diff'].mean(),
            'avg_score': best_matches['average_score'].mean(),
            'average_score_no_sentiment': best_matches['average_score_no_sentiment'].mean(),
            'commentary_count': len(best_matches),
        }
        
        # Word count averages
        metrics['real_word_count_avg'] = best_matches['real_word_count'].mean()
        metrics['generated_word_count_avg'] = best_matches['our_word_count'].mean()
        
        return metrics
    
    def get_source_counts(self):
        """
        Get counts for each data source.
        
        Returns:
            dict: Counts for each source
        """
        best_matches = self.get_best_matches('average_score')
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        # Count by source
        source_counts = best_matches['source'].value_counts().to_dict()
        
        return source_counts
    
    def get_best_matches_by_source(self, source, score_type='average_score'):
        """
        Get best matches filtered by data source.
        
        Args:
            source: The data source to filter by
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            pd.DataFrame: Filtered best matches
        """
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return None
        
        # Filter by source
        filtered = best_matches[best_matches['source'] == source]
        
        return filtered if len(filtered) > 0 else None
    
    def get_summary_statistics_by_source(self, source, score_type='average_score'):
        """
        Calculate summary statistics for a specific data source.
        
        Args:
            source: The data source to filter by
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            dict: Summary statistics
        """
        best_matches = self.get_best_matches_by_source(source, score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        # Calculate metrics
        metrics = {
            'TF-IDF': best_matches['TF-IDF'].mean(),
            'Embeddings_BERT': best_matches['Embeddings_BERT'].mean(),
            'content_overlap_ratio': best_matches['content_overlap_ratio'].mean(),
            'sentiment_diff': best_matches['sentiment_diff'].mean(),
            'avg_score': best_matches['average_score'].mean(),
            'average_score_no_sentiment': best_matches['average_score_no_sentiment'].mean(),
            'commentary_count': len(best_matches),
        }
        
        # Word count averages
        metrics['real_word_count_avg'] = best_matches['real_word_count'].mean()
        metrics['generated_word_count_avg'] = best_matches['our_word_count'].mean()
        
        return metrics

