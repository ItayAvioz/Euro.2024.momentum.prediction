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
import re


class CommentaryDataLoader:
    """Load and process commentary comparison data."""
    
    def __init__(self):
        """Initialize the data loader."""
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.script_dir, '..', '..', '08_enhanced_comparison', 'data')
        self.all_data = None
        self.best_matches = None
    
    @staticmethod
    def bold_matching_words(text1, text2):
        """
        Bold words that appear in both texts.
        Common/linking words get light bold, important words get strong bold.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            tuple: (formatted_text1, formatted_text2) with matching words bolded
        """
        if not text1 or not text2:
            return text1, text2
        
        # Define common/linking words that should get light bold
        linking_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'can', 'this', 'that', 'it', 'its',
            'their', 'there', 'they', 'them', 'his', 'her', 'he', 'she', 'who',
            'which', 'what', 'when', 'where', 'why', 'how', 'all', 'each', 'every',
            'both', 'few', 'more', 'most', 'some', 'such', 'no', 'not', 'only',
            'own', 'same', 'so', 'than', 'too', 'very', 'now', 'just', 'then',
            'up', 'out', 'if', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'under', 'again', 'further',
            'once', 'here', 'any', 'well', 'right', 'down', 'off', 'over', 'back'
        }
        
        # Extract words (alphanumeric sequences)
        words1 = re.findall(r'\b[a-zA-Z0-9]+\b', text1.lower())
        words2 = re.findall(r'\b[a-zA-Z0-9]+\b', text2.lower())
        
        # Find common words (case-insensitive)
        common_words = set(words1) & set(words2)
        
        if not common_words:
            return text1, text2
        
        # Separate linking words from important words
        linking_common = common_words & linking_words
        important_common = common_words - linking_words
        
        # Function to bold matching words in text
        def bold_text(text, linking_set, important_set):
            # First, bold important words with strong emphasis (HTML)
            if important_set:
                pattern = r'\b(' + '|'.join(re.escape(word) for word in important_set) + r')\b'
                text = re.sub(pattern, r'<strong>\1</strong>', text, flags=re.IGNORECASE)
            
            # Then, bold linking words with light emphasis (HTML with lighter weight)
            if linking_set:
                pattern = r'\b(' + '|'.join(re.escape(word) for word in linking_set) + r')\b'
                text = re.sub(pattern, r'<span style="font-weight: 500; opacity: 0.7;">\1</span>', text, flags=re.IGNORECASE)
            
            return text
        
        formatted_text1 = bold_text(text1, linking_common, important_common)
        formatted_text2 = bold_text(text2, linking_common, important_common)
        
        return formatted_text1, formatted_text2
        
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
            'ner_score': best_matches['ner_score'].mean() if 'ner_score' in best_matches.columns else 0,
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
    
    def get_overlap_matches(self):
        """
        Get the data for matches where both scoring methods selected the same best match.
        
        Returns:
            pd.DataFrame: DataFrame of overlapping matches
        """
        # Get best matches by both methods
        best_with_sentiment = self.get_best_matches('average_score')
        best_without_sentiment = self.get_best_matches('average_score_no_sentiment')
        
        if best_with_sentiment is None or best_without_sentiment is None:
            return None
        
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
        
        # Filter to only overlapping keys where sequence_id matches
        overlapping_keys = [
            key for key in with_sentiment_map 
            if key in without_sentiment_map and with_sentiment_map[key] == without_sentiment_map[key]
        ]
        
        # Return the data for overlapping matches (using with_sentiment version)
        overlap_data = best_with_sentiment[best_with_sentiment['key'].isin(overlapping_keys)].copy()
        overlap_data.drop(columns=['key'], inplace=True)
        
        return overlap_data
    
    def get_overlap_event_distribution(self, top_n=10):
        """
        Get top N event types in overlap matches.
        
        Args:
            top_n: Number of top events to return
            
        Returns:
            dict: {event_type: {'count': int, 'pct': float}}
        """
        overlap_data = self.get_overlap_matches()
        
        if overlap_data is None or len(overlap_data) == 0:
            return {}
        
        # Count by real_type
        event_counts = overlap_data['real_type'].value_counts().head(top_n)
        total = len(overlap_data)
        
        results = {}
        for event_type, count in event_counts.items():
            results[event_type] = {
                'count': count,
                'pct': (count / total * 100) if total > 0 else 0
            }
        
        return results
    
    def get_overlap_bert_distribution(self):
        """
        Get BERT score distribution for overlap matches.
        
        Returns:
            dict: Statistics about BERT scores in overlap
        """
        overlap_data = self.get_overlap_matches()
        
        if overlap_data is None or len(overlap_data) == 0:
            return {}
        
        bert_col = 'Embeddings_BERT'
        
        if bert_col not in overlap_data.columns:
            return {}
        
        bert_scores = overlap_data[bert_col].dropna()
        
        if len(bert_scores) == 0:
            return {}
        
        return {
            'mean': bert_scores.mean(),
            'median': bert_scores.median(),
            'min': bert_scores.min(),
            'max': bert_scores.max(),
            'std': bert_scores.std(),
            'count': len(bert_scores)
        }
    
    def get_overlap_sentiment_agreement(self):
        """
        Get sentiment sign agreement for overlap matches.
        
        Returns:
            dict: Sentiment agreement statistics
        """
        overlap_data = self.get_overlap_matches()
        
        if overlap_data is None or len(overlap_data) == 0:
            return {}
        
        # Create sign categories (-1, 0, 1)
        real_sign = overlap_data['real_sentiment'].apply(lambda x: -1 if x < 0 else (1 if x > 0 else 0))
        our_sign = overlap_data['our_sentiment'].apply(lambda x: -1 if x < 0 else (1 if x > 0 else 0))
        
        # Count agreements
        total = len(overlap_data)
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
    
    def get_different_matches(self):
        """
        Get the data for matches where the two scoring methods selected DIFFERENT best matches.
        
        Returns:
            pd.DataFrame: DataFrame of different matches with both selections
        """
        # Get best matches by both methods
        best_with_sentiment = self.get_best_matches('average_score')
        best_without_sentiment = self.get_best_matches('average_score_no_sentiment')
        
        if best_with_sentiment is None or best_without_sentiment is None:
            return None
        
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
        
        # Filter to only keys where sequence_id is DIFFERENT
        different_keys = [
            key for key in with_sentiment_map 
            if key in without_sentiment_map and with_sentiment_map[key] != without_sentiment_map[key]
        ]
        
        # Return the data for different matches (using with_sentiment version)
        different_data = best_with_sentiment[best_with_sentiment['key'].isin(different_keys)].copy()
        different_data.drop(columns=['key'], inplace=True)
        
        return different_data
    
    def get_different_percentage(self):
        """
        Calculate percentage where best by average_score != best by average_score_no_sentiment.
        
        Returns:
            float: Different percentage
        """
        overlap_pct = self.get_overlap_percentage()
        return 100.0 - overlap_pct
    
    def get_different_event_distribution(self, top_n=10):
        """
        Get top N event types in different selection matches.
        
        Args:
            top_n: Number of top events to return
            
        Returns:
            dict: {event_type: {'count': int, 'pct': float}}
        """
        different_data = self.get_different_matches()
        
        if different_data is None or len(different_data) == 0:
            return {}
        
        # Count by real_type
        event_counts = different_data['real_type'].value_counts().head(top_n)
        total = len(different_data)
        
        results = {}
        for event_type, count in event_counts.items():
            results[event_type] = {
                'count': count,
                'pct': (count / total * 100) if total > 0 else 0
            }
        
        return results
    
    def get_different_bert_scores(self):
        """
        Get BERT scores for different selection matches - returns 2 scores:
        1. Average BERT score for "with sentiment" selection
        2. Average BERT score for "without sentiment" selection
        
        Returns:
            dict: {'with_sentiment': float, 'without_sentiment': float, 'count': int}
        """
        # Get best matches by both methods
        best_with_sentiment = self.get_best_matches('average_score')
        best_without_sentiment = self.get_best_matches('average_score_no_sentiment')
        
        if best_with_sentiment is None or best_without_sentiment is None:
            return {}
        
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
        
        # Filter to only keys where sequence_id is DIFFERENT
        different_keys = [
            key for key in with_sentiment_map 
            if key in without_sentiment_map and with_sentiment_map[key] != without_sentiment_map[key]
        ]
        
        # Get BERT scores for both selections
        with_sentiment_different = best_with_sentiment[best_with_sentiment['key'].isin(different_keys)]
        without_sentiment_different = best_without_sentiment[best_without_sentiment['key'].isin(different_keys)]
        
        bert_col = 'Embeddings_BERT'
        
        if bert_col not in with_sentiment_different.columns or bert_col not in without_sentiment_different.columns:
            return {}
        
        with_bert = with_sentiment_different[bert_col].dropna()
        without_bert = without_sentiment_different[bert_col].dropna()
        
        if len(with_bert) == 0 or len(without_bert) == 0:
            return {}
        
        return {
            'with_sentiment': with_bert.mean(),
            'without_sentiment': without_bert.mean(),
            'count': len(different_keys)
        }
    
    def get_different_sentiment_agreement(self):
        """
        Get sentiment sign agreement for different selection matches.
        
        Returns:
            dict: Sentiment agreement statistics
        """
        different_data = self.get_different_matches()
        
        if different_data is None or len(different_data) == 0:
            return {}
        
        # Create sign categories (-1, 0, 1)
        real_sign = different_data['real_sentiment'].apply(lambda x: -1 if x < 0 else (1 if x > 0 else 0))
        our_sign = different_data['our_sentiment'].apply(lambda x: -1 if x < 0 else (1 if x > 0 else 0))
        
        # Count agreements
        total = len(different_data)
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
    
    def get_overlap_sentiment_distribution(self):
        """
        Get sentiment distribution (negative/neutral/positive) for overlap matches.
        
        Returns:
            dict: {'real': {...}, 'generated': {...}}
        """
        overlap_data = self.get_overlap_matches()
        
        if overlap_data is None or len(overlap_data) == 0:
            return {}
        
        total = len(overlap_data)
        
        # Real sentiment distribution
        real_negative = (overlap_data['real_sentiment'] < 0).sum()
        real_neutral = (overlap_data['real_sentiment'] == 0).sum()
        real_positive = (overlap_data['real_sentiment'] > 0).sum()
        
        # Generated sentiment distribution
        gen_negative = (overlap_data['our_sentiment'] < 0).sum()
        gen_neutral = (overlap_data['our_sentiment'] == 0).sum()
        gen_positive = (overlap_data['our_sentiment'] > 0).sum()
        
        return {
            'real': {
                'negative': real_negative,
                'neutral': real_neutral,
                'positive': real_positive,
                'negative_pct': (real_negative / total * 100) if total > 0 else 0,
                'neutral_pct': (real_neutral / total * 100) if total > 0 else 0,
                'positive_pct': (real_positive / total * 100) if total > 0 else 0
            },
            'generated': {
                'negative': gen_negative,
                'neutral': gen_neutral,
                'positive': gen_positive,
                'negative_pct': (gen_negative / total * 100) if total > 0 else 0,
                'neutral_pct': (gen_neutral / total * 100) if total > 0 else 0,
                'positive_pct': (gen_positive / total * 100) if total > 0 else 0
            },
            'total': total
        }
    
    def get_different_sentiment_distribution(self):
        """
        Get sentiment distribution (negative/neutral/positive) for different selection matches.
        
        Returns:
            dict: {'real': {...}, 'generated': {...}}
        """
        different_data = self.get_different_matches()
        
        if different_data is None or len(different_data) == 0:
            return {}
        
        total = len(different_data)
        
        # Real sentiment distribution
        real_negative = (different_data['real_sentiment'] < 0).sum()
        real_neutral = (different_data['real_sentiment'] == 0).sum()
        real_positive = (different_data['real_sentiment'] > 0).sum()
        
        # Generated sentiment distribution
        gen_negative = (different_data['our_sentiment'] < 0).sum()
        gen_neutral = (different_data['our_sentiment'] == 0).sum()
        gen_positive = (different_data['our_sentiment'] > 0).sum()
        
        return {
            'real': {
                'negative': real_negative,
                'neutral': real_neutral,
                'positive': real_positive,
                'negative_pct': (real_negative / total * 100) if total > 0 else 0,
                'neutral_pct': (real_neutral / total * 100) if total > 0 else 0,
                'positive_pct': (real_positive / total * 100) if total > 0 else 0
            },
            'generated': {
                'negative': gen_negative,
                'neutral': gen_neutral,
                'positive': gen_positive,
                'negative_pct': (gen_negative / total * 100) if total > 0 else 0,
                'neutral_pct': (gen_neutral / total * 100) if total > 0 else 0,
                'positive_pct': (gen_positive / total * 100) if total > 0 else 0
            },
            'total': total
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
            'ner_score': best_matches['ner_score'].mean() if 'ner_score' in best_matches.columns else 0,
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
            'ner_score': best_matches['ner_score'].mean() if 'ner_score' in best_matches.columns else 0,
            'sentiment_diff': best_matches['sentiment_diff'].mean(),
            'avg_score': best_matches['average_score'].mean(),
            'average_score_no_sentiment': best_matches['average_score_no_sentiment'].mean(),
            'commentary_count': len(best_matches),
        }
        
        # Word count averages
        metrics['real_word_count_avg'] = best_matches['real_word_count'].mean()
        metrics['generated_word_count_avg'] = best_matches['our_word_count'].mean()
        
        return metrics
    
    def get_sentiment_sign_agreement_by_bert_range(self, range_type, score_type='average_score'):
        """
        Calculate sentiment sign agreement for a specific BERT range.
        
        Args:
            range_type: 'Low (< 0.45)', 'Medium (0.45-0.55)', or 'High (> 0.55)'
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            dict: Agreement statistics
        """
        best_matches = self.get_best_matches_by_bert_range(range_type, score_type)
        
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
    
    def get_event_distribution_by_bert_range(self, range_type, score_type='average_score'):
        """
        Get event type distribution for a specific BERT range with % of total.
        
        Args:
            range_type: 'Low (< 0.45)', 'Medium (0.45-0.55)', or 'High (> 0.55)'
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            dict: {event_type: {'count': int, 'pct_of_total': float}}
        """
        best_matches = self.get_best_matches_by_bert_range(range_type, score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        # Get overall event counts (across all BERT ranges)
        all_best_matches = self.get_best_matches(score_type)
        overall_event_counts = all_best_matches['real_type'].value_counts().to_dict()
        
        # Count by real_type for this BERT range
        range_event_counts = best_matches['real_type'].value_counts().to_dict()
        
        # Calculate % of total for each event
        event_data = {}
        for event_type, count in range_event_counts.items():
            total_count = overall_event_counts.get(event_type, count)
            pct_of_total = (count / total_count * 100) if total_count > 0 else 0
            event_data[event_type] = {
                'count': count,
                'pct_of_total': pct_of_total
            }
        
        return event_data
    
    def get_best_matches_by_sentiment_sign(self, agreement_type, score_type='average_score'):
        """
        Get best matches filtered by sentiment sign agreement.
        
        Args:
            agreement_type: 'Same Sign' or 'Different Sign'
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            DataFrame: Filtered best matches
        """
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return None
        
        # Calculate sentiment sign
        real_sign = (best_matches['real_sentiment'] > 0).astype(int) - (best_matches['real_sentiment'] < 0).astype(int)
        our_sign = (best_matches['our_sentiment'] > 0).astype(int) - (best_matches['our_sentiment'] < 0).astype(int)
        
        if agreement_type == 'Same Sign':
            # Same sign (including both zero)
            mask = (real_sign == our_sign)
        else:  # 'Different Sign'
            # Different sign
            mask = (real_sign != our_sign)
        
        return best_matches[mask]
    
    def get_event_distribution_by_sentiment_sign(self, agreement_type, score_type='average_score'):
        """
        Get event type distribution for matches with same or different sentiment signs.
        
        Args:
            agreement_type: 'Same Sign' or 'Different Sign'
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            dict: {event_type: {'count': int, 'pct_of_total': float}}
        """
        filtered_matches = self.get_best_matches_by_sentiment_sign(agreement_type, score_type)
        
        if filtered_matches is None or len(filtered_matches) == 0:
            return {}
        
        # Get overall event counts (across all sentiment sign categories)
        all_best_matches = self.get_best_matches(score_type)
        overall_event_counts = all_best_matches['real_type'].value_counts().to_dict()
        
        # Count by real_type for this sentiment sign category
        filtered_event_counts = filtered_matches['real_type'].value_counts().to_dict()
        
        # Calculate % of total for each event
        event_data = {}
        for event_type, count in filtered_event_counts.items():
            total_count = overall_event_counts.get(event_type, count)
            pct_of_total = (count / total_count * 100) if total_count > 0 else 0
            event_data[event_type] = {
                'count': count,
                'pct_of_total': pct_of_total
            }
        
        return event_data
    
    def get_sentiment_sign_counts(self, score_type='average_score'):
        """
        Get counts for same sign vs different sign sentiment agreement.
        
        Args:
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            dict: Counts for 'Same Sign' and 'Different Sign'
        """
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        # Calculate sentiment sign
        real_sign = (best_matches['real_sentiment'] > 0).astype(int) - (best_matches['real_sentiment'] < 0).astype(int)
        our_sign = (best_matches['our_sentiment'] > 0).astype(int) - (best_matches['our_sentiment'] < 0).astype(int)
        
        same_sign = (real_sign == our_sign).sum()
        different_sign = (real_sign != our_sign).sum()
        
        return {
            'Same Sign': int(same_sign),
            'Different Sign': int(different_sign)
        }
    
    def get_word_matching_statistics(self, score_type='average_score'):
        """
        Get statistics on word matching between real and generated commentary.
        
        Args:
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            dict: Word matching statistics
        """
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        return {
            # Content words (without linking words)
            'avg_matching_content_words': best_matches['matching_content_words'].mean(),
            'total_matching_content_words': best_matches['matching_content_words'].sum(),
            'avg_real_content_words': best_matches['real_content_words'].mean(),
            'avg_our_content_words': best_matches['our_content_words'].mean(),
            
            # Players
            'avg_matching_players': best_matches['matching_players'].mean(),
            'total_matching_players': best_matches['matching_players'].sum(),
            'avg_real_unique_players': best_matches['real_unique_players'].mean(),
            'avg_our_unique_players': best_matches['our_unique_players'].mean(),
            'avg_entity_players_match': best_matches['entity_players_match'].mean(),
            
            # Teams
            'avg_matching_teams': best_matches['matching_teams'].mean(),
            'total_matching_teams': best_matches['matching_teams'].sum(),
            'avg_real_unique_teams': best_matches['real_unique_teams'].mean(),
            'avg_our_unique_teams': best_matches['our_unique_teams'].mean(),
            'avg_entity_teams_match': best_matches['entity_teams_match'].mean(),
            
            # Events
            'avg_matching_events': best_matches['matching_events'].mean(),
            'total_matching_events': best_matches['matching_events'].sum(),
            'avg_real_unique_events': best_matches['real_unique_events'].mean(),
            'avg_our_unique_events': best_matches['our_unique_events'].mean(),
            'avg_entity_events_match': best_matches['entity_events_match'].mean(),
            
            'commentary_count': len(best_matches)
        }
    
    def get_word_matching_by_event_type(self, score_type='average_score'):
        """
        Get word matching statistics grouped by event type.
        
        Args:
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            dict: {event_type: {statistics}}
        """
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        event_stats = {}
        
        for event_type in best_matches['real_type'].unique():
            event_data = best_matches[best_matches['real_type'] == event_type]
            
            event_stats[event_type] = {
                'count': len(event_data),
                'avg_matching_content_words': event_data['matching_content_words'].mean(),
                'total_matching_content_words': event_data['matching_content_words'].sum(),
                'avg_matching_players': event_data['matching_players'].mean(),
                'total_matching_players': event_data['matching_players'].sum(),
                'avg_matching_teams': event_data['matching_teams'].mean(),
                'total_matching_teams': event_data['matching_teams'].sum(),
                'avg_matching_events': event_data['matching_events'].mean(),
                'total_matching_events': event_data['matching_events'].sum(),
                'avg_entity_players_match': event_data['entity_players_match'].mean(),
                'avg_entity_teams_match': event_data['entity_teams_match'].mean(),
                'avg_entity_events_match': event_data['entity_events_match'].mean()
            }
        
        return event_stats
    
    def get_word_matching_distribution(self, score_type='average_score'):
        """
        Get distribution data for matching words.
        
        Args:
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            dict: Distribution data for different word types
        """
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        return {
            'matching_content_words': best_matches['matching_content_words'].tolist(),
            'matching_players': best_matches['matching_players'].tolist(),
            'matching_teams': best_matches['matching_teams'].tolist(),
            'matching_events': best_matches['matching_events'].tolist()
        }
    
    def get_event_type_keyword_presence(self, score_type='average_score'):
        """
        Check if event type keyword appears in commentary text.
        For each event type (Goal, Shot, Pass, etc.), check if the keyword appears in:
        - Real commentary only
        - Generated commentary only
        - Both commentaries
        - Neither commentary
        
        Args:
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            dict: {event_type: {'in_real_only': int, 'in_generated_only': int, 
                               'in_both': int, 'in_neither': int, 'total': int}}
        """
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        # Event type keyword mappings (lowercase for matching)
        event_keywords = {
            'Pass': ['pass', 'passes', 'passed'],
            'Shot': ['shot', 'shots', 'shoots'],
            'Goal': ['goal', 'goals', 'scores', 'scored'],
            'Dribble': ['dribble', 'dribbles', 'dribbled'],
            'Pressure': ['pressure', 'pressures', 'pressed', 'pressing'],
            'Carry': ['carry', 'carries', 'carried', 'carrying'],
            'Clearance': ['clearance', 'cleared', 'clears'],
            'Interception': ['interception', 'intercepts', 'intercepted'],
            'Tackle': ['tackle', 'tackles', 'tackled'],
            'Block': ['block', 'blocks', 'blocked'],
            'Foul Committed': ['foul', 'fouls', 'fouled'],
            'Yellow Card': ['yellow', 'booked', 'card'],
            'Red Card': ['red', 'sent off', 'dismissed'],
            'Substitution': ['substitution', 'sub', 'subs', 'replaced', 'replaces'],
            'Offside': ['offside', 'offsides'],
            'Corner': ['corner', 'corners'],
            'Free Kick': ['free kick', 'free-kick'],
            'Throw-in': ['throw', 'throw-in'],
            'Goal Kick': ['goal kick'],
            'Penalty': ['penalty', 'penalties'],
            'Save': ['save', 'saves', 'saved'],
            'Own Goal': ['own goal'],
            'Injury': ['injury', 'injured'],
            'Tactical Shift': ['tactical', 'formation'],
            'Out': ['out']
        }
        
        event_stats = {}
        
        for event_type in best_matches['real_type'].unique():
            event_data = best_matches[best_matches['real_type'] == event_type]
            
            # Get keywords for this event type
            keywords = event_keywords.get(event_type, [event_type.lower()])
            
            in_real_only = 0
            in_generated_only = 0
            in_both = 0
            in_neither = 0
            
            for _, row in event_data.iterrows():
                real_text = str(row['real_commentary']).lower() if pd.notna(row['real_commentary']) else ''
                gen_text = str(row['our_sequence_commentary']).lower() if pd.notna(row['our_sequence_commentary']) else ''
                
                # Check if any keyword appears in the text
                keyword_in_real = any(keyword in real_text for keyword in keywords)
                keyword_in_generated = any(keyword in gen_text for keyword in keywords)
                
                if keyword_in_real and keyword_in_generated:
                    in_both += 1
                elif keyword_in_real:
                    in_real_only += 1
                elif keyword_in_generated:
                    in_generated_only += 1
                else:
                    in_neither += 1
            
            total = len(event_data)
            
            event_stats[event_type] = {
                'in_real_only': in_real_only,
                'in_generated_only': in_generated_only,
                'in_both': in_both,
                'in_neither': in_neither,
                'total': total,
                'pct_in_real_only': (in_real_only / total * 100) if total > 0 else 0,
                'pct_in_generated_only': (in_generated_only / total * 100) if total > 0 else 0,
                'pct_in_both': (in_both / total * 100) if total > 0 else 0,
                'pct_in_neither': (in_neither / total * 100) if total > 0 else 0
            }
        
        return event_stats
    
    def get_general_events_analysis(self, score_type='average_score'):
        """
        Analyze "General" events to understand event type detection, specificity, and vocabulary.
        
        Args:
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            dict: Analysis results for General events
        """
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        # Filter for General events only
        general_events = best_matches[best_matches['real_type'] == 'General'].copy()
        
        if len(general_events) == 0:
            return {}
        
        # Event type keywords mapping
        event_keywords = {
            'Pass': ['pass', 'passes', 'passed', 'passing'],
            'Shot': ['shot', 'shots', 'shoots', 'shooting'],
            'Goal': ['goal', 'goals', 'scores', 'scored', 'scoring'],
            'Dribble': ['dribble', 'dribbles', 'dribbled', 'dribbling'],
            'Pressure': ['pressure', 'pressures', 'pressed', 'pressing'],
            'Carry': ['carry', 'carries', 'carried', 'carrying'],
            'Clearance': ['clearance', 'cleared', 'clears', 'clearing'],
            'Interception': ['interception', 'intercepts', 'intercepted', 'intercepting'],
            'Tackle': ['tackle', 'tackles', 'tackled', 'tackling'],
            'Block': ['block', 'blocks', 'blocked', 'blocking'],
            'Foul': ['foul', 'fouls', 'fouled', 'fouling'],
            'Save': ['save', 'saves', 'saved', 'saving'],
        }
        
        # 1. Event Type Detection in Generated and Real Commentary
        event_type_counts_generated = {}
        event_type_counts_real = {}
        
        for event_type, keywords in event_keywords.items():
            gen_count = 0
            real_count = 0
            
            for _, row in general_events.iterrows():
                gen_text = str(row['our_sequence_commentary']).lower() if pd.notna(row['our_sequence_commentary']) else ''
                real_text = str(row['real_commentary']).lower() if pd.notna(row['real_commentary']) else ''
                
                if any(keyword in gen_text for keyword in keywords):
                    gen_count += 1
                if any(keyword in real_text for keyword in keywords):
                    real_count += 1
            
            event_type_counts_generated[event_type] = {
                'count': gen_count,
                'percentage': (gen_count / len(general_events) * 100) if len(general_events) > 0 else 0
            }
            event_type_counts_real[event_type] = {
                'count': real_count,
                'percentage': (real_count / len(general_events) * 100) if len(general_events) > 0 else 0
            }
        
        # 2. Specificity Analysis
        specific_action_words = set()
        for keywords in event_keywords.values():
            specific_action_words.update(keywords)
        
        # General/vague words commonly used in real commentary
        vague_words = {'building', 'play', 'playing', 'movement', 'moving', 'tempo', 
                      'possession', 'control', 'controlling', 'looking', 'trying'}
        
        real_specific_count = 0
        real_vague_count = 0
        real_total_words = 0
        
        gen_specific_count = 0
        gen_vague_count = 0
        gen_total_words = 0
        
        for _, row in general_events.iterrows():
            real_text = str(row['real_commentary']).lower() if pd.notna(row['real_commentary']) else ''
            gen_text = str(row['our_sequence_commentary']).lower() if pd.notna(row['our_sequence_commentary']) else ''
            
            real_words = real_text.split()
            gen_words = gen_text.split()
            
            real_total_words += len(real_words)
            gen_total_words += len(gen_words)
            
            for word in real_words:
                if word in specific_action_words:
                    real_specific_count += 1
                elif word in vague_words:
                    real_vague_count += 1
            
            for word in gen_words:
                if word in specific_action_words:
                    gen_specific_count += 1
                elif word in vague_words:
                    gen_vague_count += 1
        
        specificity_analysis = {
            'real': {
                'specific_count': real_specific_count,
                'vague_count': real_vague_count,
                'total_words': real_total_words,
                'specific_percentage': (real_specific_count / real_total_words * 100) if real_total_words > 0 else 0,
                'vague_percentage': (real_vague_count / real_total_words * 100) if real_total_words > 0 else 0
            },
            'generated': {
                'specific_count': gen_specific_count,
                'vague_count': gen_vague_count,
                'total_words': gen_total_words,
                'specific_percentage': (gen_specific_count / gen_total_words * 100) if gen_total_words > 0 else 0,
                'vague_percentage': (gen_vague_count / gen_total_words * 100) if gen_total_words > 0 else 0
            }
        }
        
        # 3. Top Words Analysis
        from collections import Counter
        import re
        
        # Stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                     'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
                     'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                     'could', 'should', 'may', 'might', 'can', 'this', 'that', 'it', 'its'}
        
        real_all_words = []
        real_no_event_words = []
        gen_all_words = []
        gen_no_event_words = []
        
        for _, row in general_events.iterrows():
            real_text = str(row['real_commentary']).lower() if pd.notna(row['real_commentary']) else ''
            gen_text = str(row['our_sequence_commentary']).lower() if pd.notna(row['our_sequence_commentary']) else ''
            
            # Clean text: remove punctuation and split
            real_words = re.findall(r'\b[a-z]+\b', real_text)
            gen_words = re.findall(r'\b[a-z]+\b', gen_text)
            
            # Filter stop words
            real_words = [w for w in real_words if w not in stop_words and len(w) > 2]
            gen_words = [w for w in gen_words if w not in stop_words and len(w) > 2]
            
            real_all_words.extend(real_words)
            gen_all_words.extend(gen_words)
            
            # Without event type words
            real_no_event = [w for w in real_words if w not in specific_action_words]
            gen_no_event = [w for w in gen_words if w not in specific_action_words]
            
            real_no_event_words.extend(real_no_event)
            gen_no_event_words.extend(gen_no_event)
        
        # Get top 30 words
        real_top_all = Counter(real_all_words).most_common(30)
        gen_top_all = Counter(gen_all_words).most_common(30)
        real_top_no_event = Counter(real_no_event_words).most_common(30)
        gen_top_no_event = Counter(gen_no_event_words).most_common(30)
        
        top_words_analysis = {
            'real_all': [{'word': word, 'count': count} for word, count in real_top_all],
            'generated_all': [{'word': word, 'count': count} for word, count in gen_top_all],
            'real_no_event': [{'word': word, 'count': count} for word, count in real_top_no_event],
            'generated_no_event': [{'word': word, 'count': count} for word, count in gen_top_no_event]
        }
        
        return {
            'total_general_events': len(general_events),
            'event_type_detection_generated': event_type_counts_generated,
            'event_type_detection_real': event_type_counts_real,
            'specificity_analysis': specificity_analysis,
            'top_words_analysis': top_words_analysis
        }
    
    def get_bert_sentiment_analysis(self, score_type='average_score'):
        """
        Analyze sentiment sign accuracy across BERT similarity groups.
        Reveals the counter-intuitive finding: Low BERT similarity has highest sentiment accuracy!
        
        Args:
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            dict: BERT groups with sentiment accuracy and the selection bias explanation
        """
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        # Get BERT similarity scores (Embeddings - BERT)
        bert_col = 'Embeddings - BERT (all-MiniLM-L6-v2)'
        if bert_col not in best_matches.columns:
            return {}
        
        # Get sentiment columns
        real_sent_col = 'real_sentiment'
        gen_sent_col = 'generated_sentiment'
        
        if real_sent_col not in best_matches.columns or gen_sent_col not in best_matches.columns:
            return {}
        
        # Create BERT groups (tertiles)
        best_matches['bert_score'] = best_matches[bert_col]
        
        # Define tertiles
        low_threshold = best_matches['bert_score'].quantile(0.33)
        high_threshold = best_matches['bert_score'].quantile(0.67)
        
        best_matches['bert_group'] = pd.cut(
            best_matches['bert_score'],
            bins=[0, low_threshold, high_threshold, 1.0],
            labels=['Low (0-33%)', 'Medium (33-67%)', 'High (67-100%)'],
            include_lowest=True
        )
        
        # Calculate sentiment sign accuracy for each group
        results = {}
        
        for group in ['Low (0-33%)', 'Medium (33-67%)', 'High (67-100%)']:
            group_data = best_matches[best_matches['bert_group'] == group]
            
            if len(group_data) == 0:
                continue
            
            # Calculate sentiment sign match
            # Both positive (>0), both negative (<0), or both neutral (=0)
            real_sent = group_data[real_sent_col]
            gen_sent = group_data[gen_sent_col]
            
            # Sign matching
            both_positive = ((real_sent > 0) & (gen_sent > 0)).sum()
            both_negative = ((real_sent < 0) & (gen_sent < 0)).sum()
            both_neutral = ((real_sent == 0) & (gen_sent == 0)).sum()
            
            sign_matches = both_positive + both_negative + both_neutral
            sign_accuracy = (sign_matches / len(group_data) * 100) if len(group_data) > 0 else 0
            
            # Average BERT score
            avg_bert = group_data['bert_score'].mean()
            
            results[group] = {
                'count': len(group_data),
                'avg_bert_score': avg_bert,
                'sentiment_sign_accuracy': sign_accuracy,
                'both_positive': both_positive,
                'both_negative': both_negative,
                'both_neutral': both_neutral,
                'sign_matches': sign_matches
            }
        
        return {
            'groups': results,
            'total_analyzed': len(best_matches),
            'low_threshold': low_threshold,
            'high_threshold': high_threshold
        }
    
    def get_sentiment_counts_by_bert_range(self, bert_range, score_type='average_score'):
        """
        Count commentaries by sentiment categories for a specific BERT range.
        
        Args:
            bert_range: The BERT range to filter by (e.g., 'Low (0-0.5)', 'Medium (0.5-0.8)', 'High (0.8-1.0)')
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            dict: Counts for each sentiment category
        """
        best_matches = self.get_best_matches_by_bert_range(bert_range, score_type)
        
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
    
    def get_avg_word_count_by_event_type_for_source(self, source, score_type='average_score', top_n=10):
        """
        Get average word count (real and generated) for top N event types within a specific data source.
        
        Args:
            source: Data source to filter by
            score_type: 'average_score' or 'average_score_no_sentiment'
            top_n: Number of top event types to return (default 10)
            
        Returns:
            dict: {event_type: {'real_avg': float, 'generated_avg': float, 'count': int}}
        """
        best_matches = self.get_best_matches_by_source(source, score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        # Get top N event types by count within this source
        top_event_types = best_matches['real_type'].value_counts().head(top_n).index.tolist()
        
        # Calculate averages for each top event type
        results = {}
        
        for event_type in top_event_types:
            event_data = best_matches[best_matches['real_type'] == event_type]
            
            real_avg = event_data['real_word_count'].mean() if 'real_word_count' in event_data.columns else 0
            generated_avg = event_data['our_word_count'].mean() if 'our_word_count' in event_data.columns else 0
            
            results[event_type] = {
                'real_avg': real_avg,
                'generated_avg': generated_avg,
                'count': len(event_data)
            }
        
        return results
    
    def get_avg_word_count_by_event_type(self, score_type='average_score', top_n=10):
        """
        Get average word count (real and generated) for top N event types.
        
        Args:
            score_type: 'average_score' or 'average_score_no_sentiment'
            top_n: Number of top event types to return (default 10)
            
        Returns:
            dict: {event_type: {'real_avg': float, 'generated_avg': float, 'count': int}}
        """
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        # Get top N event types by count
        top_event_types = best_matches['real_type'].value_counts().head(top_n).index.tolist()
        
        # Calculate averages for each top event type
        results = {}
        
        for event_type in top_event_types:
            event_data = best_matches[best_matches['real_type'] == event_type]
            
            real_avg = event_data['real_word_count'].mean() if 'real_word_count' in event_data.columns else 0
            generated_avg = event_data['our_word_count'].mean() if 'our_word_count' in event_data.columns else 0
            
            results[event_type] = {
                'real_avg': real_avg,
                'generated_avg': generated_avg,
                'count': len(event_data)
            }
        
        return results
    
    def get_avg_word_count_by_source(self, score_type='average_score'):
        """
        Get average word count (real and generated) for each data source.
        
        Args:
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            dict: {source: {'real_avg': float, 'generated_avg': float, 'count': int}}
        """
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        # Group by source and calculate averages
        results = {}
        
        for source in best_matches['source'].unique():
            source_data = best_matches[best_matches['source'] == source]
            
            real_avg = source_data['real_word_count'].mean() if 'real_word_count' in source_data.columns else 0
            generated_avg = source_data['our_word_count'].mean() if 'our_word_count' in source_data.columns else 0
            
            results[source] = {
                'real_avg': real_avg,
                'generated_avg': generated_avg,
                'count': len(source_data)
            }
        
        return results
    
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
            'ner_score': best_matches['ner_score'].mean() if 'ner_score' in best_matches.columns else 0,
            'sentiment_diff': best_matches['sentiment_diff'].mean(),
            'avg_score': best_matches['average_score'].mean(),
            'average_score_no_sentiment': best_matches['average_score_no_sentiment'].mean(),
            'commentary_count': len(best_matches),
        }
        
        # Word count averages
        metrics['real_word_count_avg'] = best_matches['real_word_count'].mean()
        metrics['generated_word_count_avg'] = best_matches['our_word_count'].mean()
        
        # Content word count averages (without linking words) - if available
        if 'real_content_word_count' in best_matches.columns:
            metrics['real_content_word_count_avg'] = best_matches['real_content_word_count'].mean()
        else:
            metrics['real_content_word_count_avg'] = 0.0
            
        if 'our_content_word_count' in best_matches.columns:
            metrics['generated_content_word_count_avg'] = best_matches['our_content_word_count'].mean()
        else:
            metrics['generated_content_word_count_avg'] = 0.0
        
        return metrics
    
    def get_sentiment_sign_agreement_by_source(self, source, score_type='average_score'):
        """
        Calculate sentiment sign agreement for a specific data source.
        
        Args:
            source: The data source to filter by
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            dict: Agreement statistics
        """
        best_matches = self.get_best_matches_by_source(source, score_type)
        
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
    
    def get_top_10_event_examples(self, score_type='average_score'):
        """
        Get top 10 event types with 2 random examples per BERT group.
        
        Args:
            score_type: 'average_score' or 'average_score_no_sentiment'
            
        Returns:
            dict: Top 10 event types with examples grouped by BERT ranges
        """
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        # Get top 10 event types by count
        event_counts = best_matches['real_type'].value_counts().head(10)
        top_10_events = event_counts.index.tolist()
        
        # Define BERT ranges
        bert_ranges = {
            'Low (<0.45)': (0, 0.45),
            'Medium (0.45-0.55)': (0.45, 0.55),
            'High (>0.55)': (0.55, 1.0)
        }
        
        results = {}
        
        for event_type in top_10_events:
            results[event_type] = {
                'total_count': int(event_counts[event_type]),
                'examples': {}
            }
            
            # Get all matches for this event type
            event_matches = best_matches[best_matches['real_type'] == event_type].copy()
            
            for range_name, (min_bert, max_bert) in bert_ranges.items():
                # Filter by BERT range
                range_matches = event_matches[
                    (event_matches['Embeddings_BERT'] >= min_bert) & 
                    (event_matches['Embeddings_BERT'] < max_bert)
                ].copy()
                
                # Get 5 random samples
                if len(range_matches) >= 5:
                    samples = range_matches.sample(n=5, random_state=42)
                elif len(range_matches) > 0:
                    samples = range_matches.sample(n=len(range_matches), random_state=42)
                else:
                    samples = pd.DataFrame()
                
                # Store examples
                examples_list = []
                for _, row in samples.iterrows():
                    examples_list.append({
                        'real_commentary': row['real_commentary'],
                        'generated_commentary': row['our_sequence_commentary'],
                        'bert_score': float(row['Embeddings_BERT']),
                        'tfidf': float(row['TF-IDF']),
                        'content_overlap': float(row['content_overlap_ratio']),
                        'ner_score': float(row['ner_score']) if 'ner_score' in row and pd.notna(row['ner_score']) else 0.0,
                        'real_sentiment': float(row['real_sentiment']),
                        'generated_sentiment': float(row['our_sentiment']),
                        'sentiment_diff': float(row['sentiment_diff']),
                        'real_event_type': row['real_type'],
                        'generated_event_type': row.get('event_type', 'N/A'),
                        'minute': row['minute'],
                        'source': row.get('source', 'Unknown'),
                        'match_id': row.get('match_id', 'Unknown')
                    })
                
                results[event_type]['examples'][range_name] = {
                    'count_in_range': len(range_matches),
                    'samples': examples_list
                }
        
        return results

