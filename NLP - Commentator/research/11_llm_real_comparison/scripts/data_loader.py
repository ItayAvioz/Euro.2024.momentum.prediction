"""
Data Loader for LLM vs Real Commentary Comparison Dashboard

This module loads and processes all LLM comparison CSV files,
matching the structure and methods from 09_dashboard_analysis.

Author: AI Assistant
Date: December 11, 2025
"""

import os
import pandas as pd
from pathlib import Path
import streamlit as st
import re


class CommentaryDataLoader:
    """Load and process LLM commentary comparison data."""
    
    def __init__(self):
        """Initialize the data loader."""
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.script_dir, '..', 'data')
        self.all_data = None
        self.best_matches = None
    
    @staticmethod
    def bold_matching_words(text1, text2):
        """
        Bold words that appear in both texts.
        Common/linking words get light bold, important words get strong bold.
        """
        if not text1 or not text2:
            return text1, text2
        
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
        
        words1 = re.findall(r'\b[a-zA-Z0-9]+\b', str(text1).lower())
        words2 = re.findall(r'\b[a-zA-Z0-9]+\b', str(text2).lower())
        
        common_words = set(words1) & set(words2)
        
        if not common_words:
            return text1, text2
        
        linking_common = common_words & linking_words
        important_common = common_words - linking_words
        
        def bold_text(text, linking_set, important_set):
            if important_set:
                pattern = r'\b(' + '|'.join(re.escape(word) for word in important_set) + r')\b'
                text = re.sub(pattern, r'<strong>\1</strong>', text, flags=re.IGNORECASE)
            if linking_set:
                pattern = r'\b(' + '|'.join(re.escape(word) for word in linking_set) + r')\b'
                text = re.sub(pattern, r'<span style="font-weight: 500; opacity: 0.7;">\1</span>', text, flags=re.IGNORECASE)
            return text
        
        formatted_text1 = bold_text(str(text1), linking_common, important_common)
        formatted_text2 = bold_text(str(text2), linking_common, important_common)
        
        return formatted_text1, formatted_text2
    
    @st.cache_data
    def load_all_data(_self):
        """Load all comparison CSV files."""
        csv_files = list(Path(_self.data_dir).glob('match_*_llm_comparison.csv'))
        
        if len(csv_files) == 0:
            st.error("No comparison CSV files found!")
            return None
        
        all_dfs = []
        
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                
                # Extract match_id from filename: match_{ID}_{source}_llm_comparison.csv
                filename = csv_file.stem  # removes .csv
                parts = filename.split('_')
                match_id = parts[1]  # extract ID
                
                df['match_id'] = match_id
                
                all_dfs.append(df)
            except Exception as e:
                st.warning(f"Failed to load {csv_file.name}: {str(e)}")
                continue
        
        if len(all_dfs) == 0:
            st.error("Failed to load any CSV files!")
            return None
        
        combined_df = pd.concat(all_dfs, ignore_index=True)
        
        # Rename columns to match expected names
        column_mapping = {
            'our_sequence_commentary': 'llm_commentary',
            'Embeddings_BERT': 'bert',
            'TF-IDF': 'tfidf',
            'content_overlap_ratio': 'content_overlap',
            'our_word_count': 'llm_word_count',
            'real_type': 'real_event_type',
            'our_sentiment': 'llm_sentiment'
        }
        
        for old_name, new_name in column_mapping.items():
            if old_name in combined_df.columns:
                combined_df[new_name] = combined_df[old_name]
        
        # Add word counts if not present
        if 'llm_word_count' not in combined_df.columns:
            combined_df['llm_word_count'] = combined_df['llm_commentary'].fillna('').apply(lambda x: len(str(x).split()))
        if 'real_word_count' not in combined_df.columns:
            combined_df['real_word_count'] = combined_df['real_commentary'].fillna('').apply(lambda x: len(str(x).split()))
        
        # Rename llm_event_type column (from generate_comparison, it might be missing)
        if 'llm_event_type' not in combined_df.columns:
            # Try to extract from llm_commentary (format: [EventType] text)
            combined_df['llm_event_type'] = combined_df['llm_commentary'].apply(
                lambda x: x.split(']')[0].replace('[', '').strip() if pd.notna(x) and '[' in str(x) else 'General'
            )
        
        return combined_df
    
    @st.cache_data
    def get_best_matches(_self, score_type='average_score'):
        """
        For each unique real commentary, select the best LLM match.
        """
        if _self.all_data is None:
            _self.all_data = _self.load_all_data()
        
        if _self.all_data is None:
            return None
        
        df = _self.all_data.copy()
        
        # Group by unique real commentary and select best match
        best_matches = (
            df.sort_values(score_type, ascending=False)
            .groupby(['data_source', 'match_id', 'minute', 'real_commentary'], as_index=False)
            .first()
        )
        
        return best_matches
    
    def get_general_info(self):
        """Get general information about the dataset."""
        if self.all_data is None:
            self.all_data = self.load_all_data()
        
        if self.all_data is None:
            return {}
        
        unique_matches = self.all_data['match_id'].nunique()
        sources = self.all_data['data_source'].unique()
        
        games_per_source = (
            self.all_data.groupby('data_source')['match_id']
            .nunique()
            .sort_values(ascending=False)
        )
        
        total_comparisons = len(self.all_data)
        
        return {
            'total_games': unique_matches,
            'total_sources': len(sources),
            'sources_list': sorted(sources.tolist()),
            'games_per_source': games_per_source,
            'total_comparisons': total_comparisons,
            'total_csv_files': len(list(Path(self.data_dir).glob('match_*_llm_comparison.csv')))
        }
    
    def get_summary_statistics(self, score_type='average_score'):
        """Calculate summary statistics for best matches."""
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        metrics = {
            'tfidf': best_matches['tfidf'].mean(),
            'bert': best_matches['bert'].mean(),
            'content_overlap': best_matches['content_overlap'].mean(),
            'ner_score': best_matches['ner_score'].mean() if 'ner_score' in best_matches.columns else 0,
            'sentiment_diff': best_matches['sentiment_diff'].mean() if 'sentiment_diff' in best_matches.columns else 0,
            'avg_score': best_matches['average_score'].mean(),
            'average_score_no_sentiment': best_matches['average_score_no_sentiment'].mean() if 'average_score_no_sentiment' in best_matches.columns else 0,
            'commentary_count': len(best_matches),
            'unique_games': best_matches['match_id'].nunique(),
            'total_comparison_files': len(list(Path(self.data_dir).glob('match_*_llm_comparison.csv')))
        }
        
        metrics['commentary_avg_per_game'] = metrics['commentary_count'] / max(metrics['total_comparison_files'], 1)
        
        if 'real_word_count' in best_matches.columns:
            metrics['real_word_count_avg'] = best_matches['real_word_count'].mean()
        if 'llm_word_count' in best_matches.columns:
            metrics['llm_word_count_avg'] = best_matches['llm_word_count'].mean()
        
        return metrics
    
    def get_overlap_percentage(self):
        """Calculate percentage where best by average_score == best by average_score_no_sentiment."""
        best_with_sentiment = self.get_best_matches('average_score')
        best_without_sentiment = self.get_best_matches('average_score_no_sentiment')
        
        if best_with_sentiment is None or best_without_sentiment is None:
            return 0.0
        
        best_with_sentiment['key'] = (
            best_with_sentiment['data_source'].astype(str) + '_' + 
            best_with_sentiment['match_id'].astype(str) + '_' + 
            best_with_sentiment['minute'].astype(str) + '_' +
            best_with_sentiment['real_commentary'].astype(str)
        )
        
        best_without_sentiment['key'] = (
            best_without_sentiment['data_source'].astype(str) + '_' + 
            best_without_sentiment['match_id'].astype(str) + '_' + 
            best_without_sentiment['minute'].astype(str) + '_' +
            best_without_sentiment['real_commentary'].astype(str)
        )
        
        # Use the correct column name for LLM commentary
        llm_col = 'llm_commentary' if 'llm_commentary' in best_with_sentiment.columns else 'our_sequence_commentary'
        
        with_sentiment_map = dict(zip(best_with_sentiment['key'], best_with_sentiment[llm_col]))
        without_sentiment_map = dict(zip(best_without_sentiment['key'], best_without_sentiment[llm_col]))
        
        total_keys = len(with_sentiment_map)
        matching_keys = sum(
            1 for key in with_sentiment_map 
            if key in without_sentiment_map and with_sentiment_map[key] == without_sentiment_map[key]
        )
        
        return (matching_keys / total_keys * 100) if total_keys > 0 else 0.0
    
    def get_bert_distribution(self, score_type='average_score'):
        """Get BERT distribution data for histogram."""
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return []
        
        return best_matches['bert'].dropna().tolist()
    
    def get_sentiment_counts(self, score_type='average_score'):
        """Count commentaries by sentiment categories."""
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        # Handle both column name variations
        real_sent_col = 'real_sentiment' if 'real_sentiment' in best_matches.columns else None
        llm_sent_col = 'llm_sentiment' if 'llm_sentiment' in best_matches.columns else ('our_sentiment' if 'our_sentiment' in best_matches.columns else None)
        
        real_sent = best_matches[real_sent_col] if real_sent_col else pd.Series([0]*len(best_matches))
        llm_sent = best_matches[llm_sent_col] if llm_sent_col else pd.Series([0]*len(best_matches))
        
        return {
            'real': {
                'negative': (real_sent < 0).sum(),
                'neutral': (real_sent == 0).sum(),
                'positive': (real_sent > 0).sum()
            },
            'llm': {
                'negative': (llm_sent < 0).sum(),
                'neutral': (llm_sent == 0).sum(),
                'positive': (llm_sent > 0).sum()
            }
        }
    
    def get_sentiment_sign_agreement(self, score_type='average_score'):
        """Calculate percentage where real and LLM have the same sentiment sign."""
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        # Handle both column name variations
        real_sent_col = 'real_sentiment' if 'real_sentiment' in best_matches.columns else None
        llm_sent_col = 'llm_sentiment' if 'llm_sentiment' in best_matches.columns else ('our_sentiment' if 'our_sentiment' in best_matches.columns else None)
        
        real_sent = best_matches[real_sent_col] if real_sent_col else pd.Series([0]*len(best_matches))
        llm_sent = best_matches[llm_sent_col] if llm_sent_col else pd.Series([0]*len(best_matches))
        
        real_sign = real_sent.apply(lambda x: -1 if x < 0 else (1 if x > 0 else 0))
        llm_sign = llm_sent.apply(lambda x: -1 if x < 0 else (1 if x > 0 else 0))
        
        total = len(best_matches)
        same_sign = (real_sign == llm_sign).sum()
        both_negative = ((real_sign == -1) & (llm_sign == -1)).sum()
        both_neutral = ((real_sign == 0) & (llm_sign == 0)).sum()
        both_positive = ((real_sign == 1) & (llm_sign == 1)).sum()
        
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
        """Get counts for BERT score ranges."""
        best_matches = self.get_best_matches('average_score')
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        low = (best_matches['bert'] < 0.45).sum()
        medium = ((best_matches['bert'] >= 0.45) & (best_matches['bert'] <= 0.55)).sum()
        high = (best_matches['bert'] > 0.55).sum()
        
        return {
            'Low (< 0.45)': low,
            'Medium (0.45-0.55)': medium,
            'High (> 0.55)': high
        }
    
    def get_best_matches_by_bert_range(self, range_type, score_type='average_score'):
        """Get best matches filtered by BERT score range."""
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return None
        
        if range_type == 'Low (< 0.45)':
            filtered = best_matches[best_matches['bert'] < 0.45]
        elif range_type == 'Medium (0.45-0.55)':
            filtered = best_matches[(best_matches['bert'] >= 0.45) & (best_matches['bert'] <= 0.55)]
        elif range_type == 'High (> 0.55)':
            filtered = best_matches[best_matches['bert'] > 0.55]
        else:
            return None
        
        return filtered if len(filtered) > 0 else None
    
    def get_summary_statistics_by_bert_range(self, range_type, score_type='average_score', source=None):
        """Calculate summary statistics for a specific BERT range, optionally filtered by source."""
        best_matches = self.get_best_matches_by_bert_range(range_type, score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        # Filter by source if specified
        if source and source != 'All':
            best_matches = best_matches[best_matches['data_source'] == source]
            if len(best_matches) == 0:
                return {}
        
        return {
            'tfidf': best_matches['tfidf'].mean(),
            'bert': best_matches['bert'].mean(),
            'content_overlap': best_matches['content_overlap'].mean(),
            'ner_score': best_matches['ner_score'].mean() if 'ner_score' in best_matches.columns else 0,
            'sentiment_diff': best_matches['sentiment_diff'].mean() if 'sentiment_diff' in best_matches.columns else 0,
            'avg_score': best_matches['average_score'].mean(),
            'average_score_no_sentiment': best_matches['average_score_no_sentiment'].mean() if 'average_score_no_sentiment' in best_matches.columns else 0,
            'commentary_count': len(best_matches)
        }
    
    def get_sentiment_counts_by_bert_range(self, range_type, score_type='average_score'):
        """Count commentaries by sentiment category for a specific BERT range."""
        best_matches = self.get_best_matches_by_bert_range(range_type, score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        real_sent_col = 'real_sentiment' if 'real_sentiment' in best_matches.columns else None
        llm_sent_col = 'llm_sentiment' if 'llm_sentiment' in best_matches.columns else ('our_sentiment' if 'our_sentiment' in best_matches.columns else None)
        
        real_sent = best_matches[real_sent_col] if real_sent_col else pd.Series([0]*len(best_matches))
        llm_sent = best_matches[llm_sent_col] if llm_sent_col else pd.Series([0]*len(best_matches))
        
        return {
            'real': {
                'negative': (real_sent < 0).sum(),
                'neutral': (real_sent == 0).sum(),
                'positive': (real_sent > 0).sum()
            },
            'llm': {
                'negative': (llm_sent < 0).sum(),
                'neutral': (llm_sent == 0).sum(),
                'positive': (llm_sent > 0).sum()
            }
        }
    
    def get_sentiment_sign_agreement_by_bert_range(self, range_type, score_type='average_score'):
        """Calculate sentiment sign agreement for a specific BERT range."""
        best_matches = self.get_best_matches_by_bert_range(range_type, score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        real_sent_col = 'real_sentiment' if 'real_sentiment' in best_matches.columns else None
        llm_sent_col = 'llm_sentiment' if 'llm_sentiment' in best_matches.columns else ('our_sentiment' if 'our_sentiment' in best_matches.columns else None)
        
        real_sent = best_matches[real_sent_col] if real_sent_col else pd.Series([0]*len(best_matches))
        llm_sent = best_matches[llm_sent_col] if llm_sent_col else pd.Series([0]*len(best_matches))
        
        real_sign = real_sent.apply(lambda x: -1 if x < 0 else (1 if x > 0 else 0))
        llm_sign = llm_sent.apply(lambda x: -1 if x < 0 else (1 if x > 0 else 0))
        
        total = len(best_matches)
        same_sign = (real_sign == llm_sign).sum()
        both_negative = ((real_sign == -1) & (llm_sign == -1)).sum()
        both_neutral = ((real_sign == 0) & (llm_sign == 0)).sum()
        both_positive = ((real_sign == 1) & (llm_sign == 1)).sum()
        
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
        """Get event type distribution for a specific BERT range with % of total."""
        best_matches = self.get_best_matches_by_bert_range(range_type, score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        if 'llm_event_type' not in best_matches.columns:
            return {}
        
        # Get overall event counts (across all BERT ranges)
        all_best_matches = self.get_best_matches(score_type)
        overall_event_counts = all_best_matches['llm_event_type'].value_counts().to_dict()
        
        # Count by llm_event_type for this BERT range
        range_event_counts = best_matches['llm_event_type'].value_counts().to_dict()
        
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
    
    def get_top_10_event_examples(self, score_type='average_score'):
        """Get examples for top 10 event types grouped by BERT range."""
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        if 'llm_event_type' not in best_matches.columns:
            return {}
        
        # Get top 10 event types by count
        top_10_types = best_matches['llm_event_type'].value_counts().head(10).index.tolist()
        
        result = {}
        
        for event_type in top_10_types:
            event_data = best_matches[best_matches['llm_event_type'] == event_type]
            
            # Define BERT ranges
            low = event_data[event_data['bert'] < 0.45]
            medium = event_data[(event_data['bert'] >= 0.45) & (event_data['bert'] <= 0.55)]
            high = event_data[event_data['bert'] > 0.55]
            
            def get_samples(df, n=5):
                """Get n random samples from dataframe."""
                if len(df) == 0:
                    return []
                sample_df = df.sample(n=min(n, len(df)), random_state=42)
                samples = []
                for _, row in sample_df.iterrows():
                    samples.append({
                        'real_commentary': row.get('real_commentary', 'N/A'),
                        'llm_commentary': row.get('llm_commentary', row.get('our_sequence_commentary', 'N/A')),
                        'bert_score': row.get('bert', 0),
                        'tfidf': row.get('tfidf', 0),
                        'content_overlap': row.get('content_overlap', 0),
                        'ner_score': row.get('ner_score', 0),
                        'avg_score': row.get('average_score', 0),
                        'real_sentiment': row.get('real_sentiment', 0),
                        'llm_sentiment': row.get('llm_sentiment', row.get('our_sentiment', 0)),
                        'sentiment_diff': row.get('sentiment_diff', 0),
                        'real_event_type': row.get('real_event_type', 'N/A'),
                        'llm_event_type': row.get('llm_event_type', 'N/A'),
                        'minute': row.get('minute', 'N/A'),
                        'source': row.get('data_source', 'N/A'),
                        'match_id': row.get('match_id', 'N/A')
                    })
                return samples
            
            result[event_type] = {
                'total_count': len(event_data),
                'examples': {
                    'Low (<0.45)': {
                        'count_in_range': len(low),
                        'samples': get_samples(low)
                    },
                    'Medium (0.45-0.55)': {
                        'count_in_range': len(medium),
                        'samples': get_samples(medium)
                    },
                    'High (>0.55)': {
                        'count_in_range': len(high),
                        'samples': get_samples(high)
                    }
                }
            }
        
        return result
    
    def get_real_type_counts(self):
        """Get counts of each real event type."""
        best_matches = self.get_best_matches('average_score')
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        if 'real_event_type' in best_matches.columns:
            return best_matches['real_event_type'].value_counts().to_dict()
        return {}
    
    def get_llm_type_counts(self):
        """Get counts of each LLM event type."""
        best_matches = self.get_best_matches('average_score')
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        if 'llm_event_type' in best_matches.columns:
            return best_matches['llm_event_type'].value_counts().to_dict()
        return {}
    
    def get_source_counts(self):
        """Get counts for each data source."""
        best_matches = self.get_best_matches('average_score')
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        return best_matches['data_source'].value_counts().to_dict()
    
    def get_best_matches_by_source(self, source, score_type='average_score'):
        """Get best matches filtered by data source."""
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return None
        
        filtered = best_matches[best_matches['data_source'] == source]
        return filtered if len(filtered) > 0 else None
    
    def get_summary_statistics_by_source(self, source, score_type='average_score'):
        """Calculate summary statistics for a specific data source."""
        best_matches = self.get_best_matches_by_source(source, score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        metrics = {
            'tfidf': best_matches['tfidf'].mean(),
            'bert': best_matches['bert'].mean(),
            'content_overlap': best_matches['content_overlap'].mean(),
            'ner_score': best_matches['ner_score'].mean() if 'ner_score' in best_matches.columns else 0,
            'sentiment_diff': best_matches['sentiment_diff'].mean() if 'sentiment_diff' in best_matches.columns else 0,
            'avg_score': best_matches['average_score'].mean(),
            'average_score_no_sentiment': best_matches['average_score_no_sentiment'].mean() if 'average_score_no_sentiment' in best_matches.columns else 0,
            'commentary_count': len(best_matches),
        }
        
        if 'real_word_count' in best_matches.columns:
            metrics['real_word_count_avg'] = best_matches['real_word_count'].mean()
        if 'llm_word_count' in best_matches.columns:
            metrics['llm_word_count_avg'] = best_matches['llm_word_count'].mean()
        
        return metrics
    
    def get_avg_score_by_event_type(self, score_type='average_score'):
        """Get average score for each LLM event type."""
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        if 'llm_event_type' not in best_matches.columns:
            return {}
        
        return best_matches.groupby('llm_event_type')[score_type].mean().sort_values(ascending=False).to_dict()
    
    def get_avg_bert_by_event_type(self, score_type='average_score'):
        """Get average BERT score for each LLM event type."""
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        if 'llm_event_type' not in best_matches.columns:
            return {}
        
        return best_matches.groupby('llm_event_type')['bert'].mean().sort_values(ascending=False).to_dict()
    
    def get_top_10_examples(self, score_type='average_score'):
        """Get top 10 best and worst matches."""
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {'best': [], 'worst': []}
        
        top_10 = best_matches.nlargest(10, score_type)
        bottom_10 = best_matches[best_matches[score_type] > 0].nsmallest(10, score_type)
        
        return {
            'best': top_10.to_dict('records'),
            'worst': bottom_10.to_dict('records')
        }
    
    def get_score_distribution(self, score_type='average_score'):
        """Get score distribution data."""
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return []
        
        return best_matches[score_type].dropna().tolist()
    
    def get_avg_word_count_by_source(self, score_type='average_score'):
        """Get average word count by source."""
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        results = {}
        for source in best_matches['data_source'].unique():
            source_data = best_matches[best_matches['data_source'] == source]
            results[source] = {
                'real_avg': source_data['real_word_count'].mean() if 'real_word_count' in source_data.columns else 0,
                'llm_avg': source_data['llm_word_count'].mean() if 'llm_word_count' in source_data.columns else 0,
                'count': len(source_data)
            }
        return results
    
    def get_avg_word_count_by_event_type(self, score_type='average_score', top_n=10):
        """Get average word count by event type."""
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        if 'llm_event_type' not in best_matches.columns:
            return {}
        
        top_event_types = best_matches['llm_event_type'].value_counts().head(top_n).index.tolist()
        
        results = {}
        for event_type in top_event_types:
            event_data = best_matches[best_matches['llm_event_type'] == event_type]
            results[event_type] = {
                'real_avg': event_data['real_word_count'].mean() if 'real_word_count' in event_data.columns else 0,
                'llm_avg': event_data['llm_word_count'].mean() if 'llm_word_count' in event_data.columns else 0,
                'count': len(event_data)
            }
        return results
    
    def get_best_matches_by_event_type(self, event_type, score_type='average_score'):
        """Get best matches filtered by LLM event type."""
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return None
        
        if 'llm_event_type' not in best_matches.columns:
            return None
        
        filtered = best_matches[best_matches['llm_event_type'] == event_type]
        return filtered if len(filtered) > 0 else None
    
    def get_summary_statistics_by_event_type(self, event_type, score_type='average_score'):
        """Calculate summary statistics for a specific LLM event type."""
        best_matches = self.get_best_matches_by_event_type(event_type, score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        return {
            'tfidf': best_matches['tfidf'].mean(),
            'bert': best_matches['bert'].mean(),
            'content_overlap': best_matches['content_overlap'].mean(),
            'ner_score': best_matches['ner_score'].mean() if 'ner_score' in best_matches.columns else 0,
            'sentiment_diff': best_matches['sentiment_diff'].mean() if 'sentiment_diff' in best_matches.columns else 0,
            'avg_score': best_matches['average_score'].mean(),
            'average_score_no_sentiment': best_matches['average_score_no_sentiment'].mean() if 'average_score_no_sentiment' in best_matches.columns else 0,
            'count': len(best_matches)
        }
    
    def get_bert_distribution_by_event_type(self, event_type, score_type='average_score'):
        """Get BERT distribution for a specific LLM event type."""
        best_matches = self.get_best_matches_by_event_type(event_type, score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return []
        
        return best_matches['bert'].dropna().tolist()
    
    def get_sentiment_counts_by_event_type(self, event_type, score_type='average_score'):
        """Count commentaries by sentiment category for a specific LLM event type."""
        best_matches = self.get_best_matches_by_event_type(event_type, score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        real_sent_col = 'real_sentiment' if 'real_sentiment' in best_matches.columns else None
        llm_sent_col = 'llm_sentiment' if 'llm_sentiment' in best_matches.columns else ('our_sentiment' if 'our_sentiment' in best_matches.columns else None)
        
        real_sent = best_matches[real_sent_col] if real_sent_col else pd.Series([0]*len(best_matches))
        llm_sent = best_matches[llm_sent_col] if llm_sent_col else pd.Series([0]*len(best_matches))
        
        return {
            'real': {
                'negative': (real_sent < 0).sum(),
                'neutral': (real_sent == 0).sum(),
                'positive': (real_sent > 0).sum()
            },
            'llm': {
                'negative': (llm_sent < 0).sum(),
                'neutral': (llm_sent == 0).sum(),
                'positive': (llm_sent > 0).sum()
            }
        }
    
    def get_sentiment_sign_agreement_by_event_type(self, event_type, score_type='average_score'):
        """Calculate sentiment sign agreement for a specific LLM event type."""
        best_matches = self.get_best_matches_by_event_type(event_type, score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        real_sent_col = 'real_sentiment' if 'real_sentiment' in best_matches.columns else None
        llm_sent_col = 'llm_sentiment' if 'llm_sentiment' in best_matches.columns else ('our_sentiment' if 'our_sentiment' in best_matches.columns else None)
        
        real_sent = best_matches[real_sent_col] if real_sent_col else pd.Series([0]*len(best_matches))
        llm_sent = best_matches[llm_sent_col] if llm_sent_col else pd.Series([0]*len(best_matches))
        
        real_sign = real_sent.apply(lambda x: -1 if x < 0 else (1 if x > 0 else 0))
        llm_sign = llm_sent.apply(lambda x: -1 if x < 0 else (1 if x > 0 else 0))
        
        total = len(best_matches)
        same_sign = (real_sign == llm_sign).sum()
        both_negative = ((real_sign == -1) & (llm_sign == -1)).sum()
        both_neutral = ((real_sign == 0) & (llm_sign == 0)).sum()
        both_positive = ((real_sign == 1) & (llm_sign == 1)).sum()
        
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
    
    # ========================================
    # WORD MATCHING METHODS
    # ========================================
    
    def get_word_matching_statistics(self, score_type='average_score'):
        """Get word matching statistics."""
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        return {
            'avg_matching_content_words': best_matches['matching_content_words'].mean() if 'matching_content_words' in best_matches.columns else 0,
            'avg_matching_players': best_matches['matching_players'].mean() if 'matching_players' in best_matches.columns else 0,
            'avg_matching_teams': best_matches['matching_teams'].mean() if 'matching_teams' in best_matches.columns else 0,
            'avg_matching_events': best_matches['matching_events'].mean() if 'matching_events' in best_matches.columns else 0,
            'avg_entity_players_match': best_matches['entity_players_match'].mean() if 'entity_players_match' in best_matches.columns else 0,
            'avg_entity_teams_match': best_matches['entity_teams_match'].mean() if 'entity_teams_match' in best_matches.columns else 0,
            'avg_entity_events_match': best_matches['entity_events_match'].mean() if 'entity_events_match' in best_matches.columns else 0,
        }
    
    def get_word_matching_by_event_type(self, score_type='average_score'):
        """Get word matching statistics by LLM event type."""
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        if 'llm_event_type' not in best_matches.columns:
            return {}
        
        result = {}
        for event_type in best_matches['llm_event_type'].unique():
            event_data = best_matches[best_matches['llm_event_type'] == event_type]
            result[event_type] = {
                'count': len(event_data),
                'avg_matching_content_words': event_data['matching_content_words'].mean() if 'matching_content_words' in event_data.columns else 0,
                'avg_matching_players': event_data['matching_players'].mean() if 'matching_players' in event_data.columns else 0,
                'avg_matching_teams': event_data['matching_teams'].mean() if 'matching_teams' in event_data.columns else 0,
                'avg_matching_events': event_data['matching_events'].mean() if 'matching_events' in event_data.columns else 0,
                'total_matching_content_words': event_data['matching_content_words'].sum() if 'matching_content_words' in event_data.columns else 0,
                'total_matching_players': event_data['matching_players'].sum() if 'matching_players' in event_data.columns else 0,
                'total_matching_teams': event_data['matching_teams'].sum() if 'matching_teams' in event_data.columns else 0,
                'total_matching_events': event_data['matching_events'].sum() if 'matching_events' in event_data.columns else 0,
            }
        
        return result
    
    def get_word_matching_distribution(self, score_type='average_score'):
        """Get word matching distribution data for histograms."""
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        return {
            'matching_content_words': best_matches['matching_content_words'].dropna().tolist() if 'matching_content_words' in best_matches.columns else [],
            'matching_players': best_matches['matching_players'].dropna().tolist() if 'matching_players' in best_matches.columns else [],
            'matching_teams': best_matches['matching_teams'].dropna().tolist() if 'matching_teams' in best_matches.columns else [],
            'matching_events': best_matches['matching_events'].dropna().tolist() if 'matching_events' in best_matches.columns else [],
        }
    
    # ========================================
    # EVENT TYPE MATCH ANALYSIS
    # ========================================
    
    def get_event_type_match_analysis(self, score_type='average_score'):
        """Compare real event type vs LLM event type - what % match and BERT by group."""
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        # Check for required columns
        real_col = 'real_event_type' if 'real_event_type' in best_matches.columns else ('real_type' if 'real_type' in best_matches.columns else None)
        llm_col = 'llm_event_type' if 'llm_event_type' in best_matches.columns else None
        
        if not real_col or not llm_col:
            return {}
        
        # Normalize event types for comparison (lowercase, strip)
        df = best_matches.copy()
        df['real_normalized'] = df[real_col].fillna('').astype(str).str.lower().str.strip()
        df['llm_normalized'] = df[llm_col].fillna('').astype(str).str.lower().str.strip()
        
        # Check for exact match
        df['type_match'] = df['real_normalized'] == df['llm_normalized']
        
        total = len(df)
        matches = df['type_match'].sum()
        match_pct = (matches / total * 100) if total > 0 else 0
        
        # BERT by match group
        matched_df = df[df['type_match'] == True]
        unmatched_df = df[df['type_match'] == False]
        
        return {
            'total': total,
            'matches': int(matches),
            'match_pct': match_pct,
            'non_matches': int(total - matches),
            'non_match_pct': 100 - match_pct,
            'bert_matched': matched_df['bert'].mean() if len(matched_df) > 0 else 0,
            'bert_unmatched': unmatched_df['bert'].mean() if len(unmatched_df) > 0 else 0,
            'avg_score_matched': matched_df['average_score'].mean() if len(matched_df) > 0 else 0,
            'avg_score_unmatched': unmatched_df['average_score'].mean() if len(unmatched_df) > 0 else 0,
        }
    
    def get_event_type_match_by_type(self, score_type='average_score'):
        """Get event type match statistics broken down by LLM event type."""
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        real_col = 'real_event_type' if 'real_event_type' in best_matches.columns else ('real_type' if 'real_type' in best_matches.columns else None)
        llm_col = 'llm_event_type' if 'llm_event_type' in best_matches.columns else None
        
        if not real_col or not llm_col:
            return {}
        
        df = best_matches.copy()
        df['real_normalized'] = df[real_col].fillna('').astype(str).str.lower().str.strip()
        df['llm_normalized'] = df[llm_col].fillna('').astype(str).str.lower().str.strip()
        df['type_match'] = df['real_normalized'] == df['llm_normalized']
        
        result = {}
        for event_type in df[llm_col].unique():
            event_df = df[df[llm_col] == event_type]
            total = len(event_df)
            matches = event_df['type_match'].sum()
            
            result[event_type] = {
                'total': total,
                'matches': int(matches),
                'match_pct': (matches / total * 100) if total > 0 else 0,
                'bert_avg': event_df['bert'].mean(),
                'bert_matched': event_df[event_df['type_match'] == True]['bert'].mean() if matches > 0 else 0,
                'bert_unmatched': event_df[event_df['type_match'] == False]['bert'].mean() if (total - matches) > 0 else 0,
            }
        
        return result
    
    def get_event_type_match_by_source(self, score_type='average_score'):
        """Get event type match statistics broken down by data source."""
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        real_col = 'real_event_type' if 'real_event_type' in best_matches.columns else ('real_type' if 'real_type' in best_matches.columns else None)
        llm_col = 'llm_event_type' if 'llm_event_type' in best_matches.columns else None
        
        if not real_col or not llm_col:
            return {}
        
        df = best_matches.copy()
        df['real_normalized'] = df[real_col].fillna('').astype(str).str.lower().str.strip()
        df['llm_normalized'] = df[llm_col].fillna('').astype(str).str.lower().str.strip()
        df['type_match'] = df['real_normalized'] == df['llm_normalized']
        
        result = {}
        for source in df['data_source'].unique():
            source_df = df[df['data_source'] == source]
            total = len(source_df)
            matches = source_df['type_match'].sum()
            
            matched_df = source_df[source_df['type_match'] == True]
            unmatched_df = source_df[source_df['type_match'] == False]
            
            result[source] = {
                'total': total,
                'matches': int(matches),
                'match_pct': (matches / total * 100) if total > 0 else 0,
                'bert_avg': source_df['bert'].mean(),
                'bert_matched': matched_df['bert'].mean() if matches > 0 else 0,
                'bert_unmatched': unmatched_df['bert'].mean() if (total - matches) > 0 else 0,
                'ner_avg': source_df['ner_score'].mean() if 'ner_score' in source_df.columns else 0,
                'ner_matched': matched_df['ner_score'].mean() if (matches > 0 and 'ner_score' in source_df.columns) else 0,
                'ner_unmatched': unmatched_df['ner_score'].mean() if ((total - matches) > 0 and 'ner_score' in source_df.columns) else 0,
                'avg_score': source_df['average_score'].mean(),
                'avg_score_matched': matched_df['average_score'].mean() if matches > 0 else 0,
                'avg_score_unmatched': unmatched_df['average_score'].mean() if (total - matches) > 0 else 0,
            }
        
        return result

    def get_bert_ner_discrepancy_analysis(self, score_type='average_score'):
        """
        Analyze discrepancies between BERT and NER scores.
        
        6 Groups (2x3 matrix):
        High BERT (>0.55):
          1. Low NER (<0.33) - "Semantic ✓, Entity ✗"
          2. Medium NER (0.33-0.55) - "Semantic ✓, Entity ~"
          3. High NER (>0.55) - "Full Match"
        Low BERT (<0.45):
          4. Low NER (<0.33) - "Full Mismatch"
          5. Medium NER (0.33-0.55) - "Semantic ✗, Entity ~"
          6. High NER (>0.55) - "Entity ✓, Semantic ✗"
        """
        best_matches = self.get_best_matches(score_type)
        
        if best_matches is None or len(best_matches) == 0:
            return {}
        
        df = best_matches.copy()
        
        # Ensure ner_score column exists
        if 'ner_score' not in df.columns:
            df['ner_score'] = 0
        
        total_count = len(df)
        
        # NER thresholds based on median (0.33) and high (0.55)
        NER_MEDIAN = 0.33
        NER_HIGH = 0.55
        BERT_HIGH = 0.55
        BERT_LOW = 0.45
        
        # Define 6 groups
        # High BERT groups
        high_bert_low_ner = df[(df['bert'] > BERT_HIGH) & (df['ner_score'] < NER_MEDIAN)]
        high_bert_med_ner = df[(df['bert'] > BERT_HIGH) & (df['ner_score'] >= NER_MEDIAN) & (df['ner_score'] <= NER_HIGH)]
        high_bert_high_ner = df[(df['bert'] > BERT_HIGH) & (df['ner_score'] > NER_HIGH)]
        
        # Low BERT groups
        low_bert_low_ner = df[(df['bert'] < BERT_LOW) & (df['ner_score'] < NER_MEDIAN)]
        low_bert_med_ner = df[(df['bert'] < BERT_LOW) & (df['ner_score'] >= NER_MEDIAN) & (df['ner_score'] <= NER_HIGH)]
        low_bert_high_ner = df[(df['bert'] < BERT_LOW) & (df['ner_score'] > NER_HIGH)]
        
        result = {
            # High BERT groups
            'high_bert_low_ner': {
                'name': 'High BERT (>0.55) + Low NER (<0.33)',
                'description': 'Semantic ✓, Entity ✗',
                'count': len(high_bert_low_ner),
                'pct': len(high_bert_low_ner) / total_count * 100 if total_count > 0 else 0,
                'avg_bert': high_bert_low_ner['bert'].mean() if len(high_bert_low_ner) > 0 else 0,
                'avg_ner': high_bert_low_ner['ner_score'].mean() if len(high_bert_low_ner) > 0 else 0,
                'df': high_bert_low_ner
            },
            'high_bert_med_ner': {
                'name': 'High BERT (>0.55) + Med NER (0.33-0.55)',
                'description': 'Semantic ✓, Entity ~',
                'count': len(high_bert_med_ner),
                'pct': len(high_bert_med_ner) / total_count * 100 if total_count > 0 else 0,
                'avg_bert': high_bert_med_ner['bert'].mean() if len(high_bert_med_ner) > 0 else 0,
                'avg_ner': high_bert_med_ner['ner_score'].mean() if len(high_bert_med_ner) > 0 else 0,
                'df': high_bert_med_ner
            },
            'high_bert_high_ner': {
                'name': 'High BERT (>0.55) + High NER (>0.55)',
                'description': 'Full Match ✓✓',
                'count': len(high_bert_high_ner),
                'pct': len(high_bert_high_ner) / total_count * 100 if total_count > 0 else 0,
                'avg_bert': high_bert_high_ner['bert'].mean() if len(high_bert_high_ner) > 0 else 0,
                'avg_ner': high_bert_high_ner['ner_score'].mean() if len(high_bert_high_ner) > 0 else 0,
                'df': high_bert_high_ner
            },
            # Low BERT groups
            'low_bert_low_ner': {
                'name': 'Low BERT (<0.45) + Low NER (<0.33)',
                'description': 'Full Mismatch ✗✗',
                'count': len(low_bert_low_ner),
                'pct': len(low_bert_low_ner) / total_count * 100 if total_count > 0 else 0,
                'avg_bert': low_bert_low_ner['bert'].mean() if len(low_bert_low_ner) > 0 else 0,
                'avg_ner': low_bert_low_ner['ner_score'].mean() if len(low_bert_low_ner) > 0 else 0,
                'df': low_bert_low_ner
            },
            'low_bert_med_ner': {
                'name': 'Low BERT (<0.45) + Med NER (0.33-0.55)',
                'description': 'Semantic ✗, Entity ~',
                'count': len(low_bert_med_ner),
                'pct': len(low_bert_med_ner) / total_count * 100 if total_count > 0 else 0,
                'avg_bert': low_bert_med_ner['bert'].mean() if len(low_bert_med_ner) > 0 else 0,
                'avg_ner': low_bert_med_ner['ner_score'].mean() if len(low_bert_med_ner) > 0 else 0,
                'df': low_bert_med_ner
            },
            'low_bert_high_ner': {
                'name': 'Low BERT (<0.45) + High NER (>0.55)',
                'description': 'Entity ✓, Semantic ✗',
                'count': len(low_bert_high_ner),
                'pct': len(low_bert_high_ner) / total_count * 100 if total_count > 0 else 0,
                'avg_bert': low_bert_high_ner['bert'].mean() if len(low_bert_high_ner) > 0 else 0,
                'avg_ner': low_bert_high_ner['ner_score'].mean() if len(low_bert_high_ner) > 0 else 0,
                'df': low_bert_high_ner
            },
            'total_count': total_count
        }
        
        return result
    
    def get_bert_ner_event_distribution(self, group_key, score_type='average_score'):
        """
        Get top 10 event type distribution for a BERT/NER discrepancy group.
        
        Args:
            group_key: 'high_bert_low_ner', 'low_bert_high_ner', or 'high_bert_high_ner'
            score_type: 'average_score' or 'average_score_no_sentiment'
        """
        analysis = self.get_bert_ner_discrepancy_analysis(score_type)
        
        if not analysis or group_key not in analysis:
            return {}
        
        group_df = analysis[group_key]['df']
        
        if len(group_df) == 0:
            return {}
        
        # Get event type column
        event_col = 'llm_event_type' if 'llm_event_type' in group_df.columns else 'real_type'
        
        # Count top 10 event types
        event_counts = group_df[event_col].value_counts().head(10)
        
        result = {
            'event_types': event_counts.index.tolist(),
            'counts': event_counts.values.tolist(),
            'total_in_group': len(group_df)
        }
        
        return result
    
    def get_bert_ner_examples(self, group_key, n_samples=10, score_type='average_score'):
        """
        Get random examples for a BERT/NER discrepancy group.
        
        Args:
            group_key: 'high_bert_low_ner', 'low_bert_high_ner', or 'high_bert_high_ner'
            n_samples: Number of examples to return
            score_type: 'average_score' or 'average_score_no_sentiment'
        """
        analysis = self.get_bert_ner_discrepancy_analysis(score_type)
        
        if not analysis or group_key not in analysis:
            return []
        
        group_df = analysis[group_key]['df']
        
        if len(group_df) == 0:
            return []
        
        # Sample random examples
        if len(group_df) >= n_samples:
            samples = group_df.sample(n=n_samples, random_state=42)
        else:
            samples = group_df.sample(n=len(group_df), random_state=42)
        
        examples = []
        for _, row in samples.iterrows():
            examples.append({
                'real_commentary': row.get('real_commentary', ''),
                'llm_commentary': row.get('llm_commentary', ''),
                'bert': float(row.get('bert', 0)),
                'ner_score': float(row.get('ner_score', 0)),
                'tfidf': float(row.get('tfidf', 0)),
                'content_overlap': float(row.get('content_overlap', 0)),
                'real_sentiment': float(row.get('real_sentiment', 0)),
                'llm_sentiment': float(row.get('llm_sentiment', 0)),
                'sentiment_diff': float(row.get('sentiment_diff', 0)),
                'average_score': float(row.get('average_score', 0)),
                'real_type': row.get('real_type', 'N/A'),
                'llm_event_type': row.get('llm_event_type', 'N/A'),
                'minute': row.get('minute', 0),
                'data_source': row.get('data_source', 'Unknown'),
                'match_id': row.get('match_id', 'Unknown')
            })
        
        return examples

