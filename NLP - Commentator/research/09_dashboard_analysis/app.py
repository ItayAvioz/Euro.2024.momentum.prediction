"""
Commentary Analysis Dashboard

Interactive Streamlit dashboard for analyzing generated vs real commentary comparisons.

Author: AI Assistant
Date: November 10, 2025
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from data_loader import CommentaryDataLoader


# Page configuration
st.set_page_config(
    page_title="Euro 2024 Commentary Analysis",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .big-metric {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 1rem;
        color: #666;
        margin-bottom: 0.5rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #333;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main dashboard application."""
    
    # Title
    st.title("⚽ Euro 2024 Commentary Analysis Dashboard")
    st.markdown("*Analyzing Generated vs Real Football Commentary*")
    st.markdown("---")
    
    # Initialize data loader
    loader = CommentaryDataLoader()
    
    # Sidebar
    st.sidebar.title("📊 Dashboard Info")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info(
        "This dashboard analyzes the comparison between our generated commentary "
        "and real commentary from multiple sources (FlashScore, SportsMole, BBC, FOX, ESPN). "
        "\n\n**Comparison:** All charts show both scoring methods side-by-side."
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Scoring Methods")
    st.sidebar.markdown("""
    **With Sentiment:**
    - Includes sentiment difference in score
    - Formula: (TF-IDF + BERT + Content + (1-Sentiment)) / 4
    
    **Without Sentiment:**
    - Excludes sentiment from score
    - Formula: (TF-IDF + BERT + Content) / 3
    """)
    
    # Load data
    with st.spinner("Loading data..."):
        general_info = loader.get_general_info()
    
    if not general_info:
        st.error("Failed to load data. Please check the data directory.")
        return
    
    # ========================================
    # SECTION 1: GENERAL INFO
    # ========================================
    st.markdown('<div class="section-header">📋 General Information</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-label">Total Games Covered</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="big-metric">{general_info["total_games"]}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-label">Data Sources</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="big-metric">{general_info["total_sources"]}</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-label">Total Comparisons</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="big-metric">{general_info["total_comparisons"]:,}</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-label">CSV Files Processed</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="big-metric">{general_info["total_csv_files"]}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Data sources breakdown
    st.subheader("📊 Games per Data Source")
    
    games_per_source_df = pd.DataFrame({
        'Data Source': general_info['games_per_source'].index,
        'Number of Games': general_info['games_per_source'].values
    })
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.dataframe(
            games_per_source_df,
            hide_index=True,
            use_container_width=True
        )
    
    with col2:
        st.bar_chart(
            games_per_source_df.set_index('Data Source'),
            height=300
        )
    
    # ========================================
    # SECTION 2: GENERAL STATISTICS
    # ========================================
    st.markdown('<div class="section-header">📊 Overall Statistics</div>', unsafe_allow_html=True)
    
    st.info(
        "**Best Match Selection:** For each real commentary entry, the generated sequence with the "
        "highest score is selected. Statistics below show comparison between two scoring methods."
    )
    
    # Get statistics for both methods
    with st.spinner("Calculating statistics..."):
        stats_with_sentiment = loader.get_summary_statistics('average_score')
        stats_without_sentiment = loader.get_summary_statistics('average_score_no_sentiment')
        overlap_pct = loader.get_overlap_percentage()
    
    if not stats_with_sentiment or not stats_without_sentiment:
        st.error("Failed to calculate statistics.")
        return
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Commentary Count",
            f"{stats_with_sentiment['commentary_count']:,}",
            help="Total number of best-match commentaries analyzed"
        )
    
    with col2:
        st.metric(
            "Total Comparison Files",
            f"{stats_with_sentiment['total_comparison_files']}",
            help="Total number of comparison CSVs (69 = 51 FlashScore + 6 SportsMole + 4 BBC + 4 FOX + 4 ESPN)"
        )
    
    with col3:
        st.metric(
            "Unique Games",
            f"{stats_with_sentiment['unique_games']}",
            help="Number of unique matches (some games have multiple sources)"
        )
    
    with col4:
        st.metric(
            "Avg Commentary per Game",
            f"{stats_with_sentiment['commentary_avg_per_game']:.1f}",
            help="Average number of commentaries per comparison file (Total Count ÷ 69)"
        )
    
    st.markdown("---")
    
    # Word count row
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Avg Real Commentary Words",
            f"{stats_with_sentiment['real_word_count_avg']:.1f}",
            help="Average word count in real commentary"
        )
    
    with col2:
        st.metric(
            "Avg Generated Commentary Words",
            f"{stats_with_sentiment['generated_word_count_avg']:.1f}",
            help="Average word count in our generated commentary"
        )
    
    st.markdown("---")
    
    # Selection overlap row
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Selection Overlap",
            f"{overlap_pct:.1f}%",
            help="Percentage where both methods select the same best sequence"
        )
    
    with col2:
        st.metric(
            "Different Selections",
            f"{100 - overlap_pct:.1f}%",
            help="Percentage where methods select different best sequences"
        )
    
    # ========================================
    # COMPARISON CHARTS
    # ========================================
    st.markdown('<div class="section-header">📊 Scoring Method Comparison</div>', unsafe_allow_html=True)
    
    st.info("Compare all metrics when selecting best matches **With Sentiment** vs **Without Sentiment**")
    
    # NER note
    ner_score_with = stats_with_sentiment.get('ner_score', 0)
    if ner_score_with > 0:
        st.info("ℹ️ **NER (Named Entity Recognition)** measures player/team/event matching. It is shown separately and **not included in the Average Score** because Content Overlap already captures word-level matching.")
    
    # Prepare data for grouped bar chart (metrics on X-axis)
    metrics = ['TF-IDF', 'Embeddings BERT', 'Content Overlap', 'NER', 'Sentiment Diff', 'Avg Score\n(With Sentiment)', 'Avg Score\n(Without Sentiment)']
    with_sentiment_values = [
        stats_with_sentiment['TF-IDF'],
        stats_with_sentiment['Embeddings_BERT'],
        stats_with_sentiment['content_overlap_ratio'],
        stats_with_sentiment.get('ner_score', 0),
        stats_with_sentiment['sentiment_diff'],
        stats_with_sentiment['avg_score'],
        stats_with_sentiment['average_score_no_sentiment']
    ]
    without_sentiment_values = [
        stats_without_sentiment['TF-IDF'],
        stats_without_sentiment['Embeddings_BERT'],
        stats_without_sentiment['content_overlap_ratio'],
        stats_without_sentiment.get('ner_score', 0),
        stats_without_sentiment['sentiment_diff'],
        stats_without_sentiment['avg_score'],
        stats_without_sentiment['average_score_no_sentiment']
    ]
    
    # Create grouped bar chart with metrics on X-axis
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='With Sentiment',
        x=metrics,
        y=with_sentiment_values,
        text=[f'{v:.4f}' for v in with_sentiment_values],
        textposition='auto',
        marker_color='#1f77b4'
    ))
    
    fig.add_trace(go.Bar(
        name='Without Sentiment',
        x=metrics,
        y=without_sentiment_values,
        text=[f'{v:.4f}' for v in without_sentiment_values],
        textposition='auto',
        marker_color='#ff7f0e'
    ))
    
    fig.update_layout(
        barmode='group',
        yaxis_title='Score (0-1)',
        xaxis_title='Metric',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        xaxis=dict(tickangle=0)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ========================================
    # ADDITIONAL ANALYSES
    # ========================================
    st.markdown('<div class="section-header">📈 Additional Analyses</div>', unsafe_allow_html=True)
    
    # Get data for both methods
    with st.spinner("Calculating additional analyses..."):
        bert_dist_with = loader.get_bert_distribution('average_score')
        bert_dist_without = loader.get_bert_distribution('average_score_no_sentiment')
        
        sentiment_counts_with = loader.get_sentiment_counts('average_score')
        sentiment_counts_without = loader.get_sentiment_counts('average_score_no_sentiment')
        
        sentiment_agreement_with = loader.get_sentiment_sign_agreement('average_score')
        sentiment_agreement_without = loader.get_sentiment_sign_agreement('average_score_no_sentiment')
    
    # BERT Distribution
    st.subheader("Embeddings_BERT Similarity Distribution")
    st.caption("Distribution of BERT semantic similarity scores (0-1 scale)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**With Sentiment Selection**")
        if bert_dist_with:
            fig_bert1 = go.Figure()
            fig_bert1.add_trace(go.Histogram(
                x=bert_dist_with,
                nbinsx=30,
                marker_color='#1f77b4',
                name='With Sentiment'
            ))
            fig_bert1.update_layout(
                xaxis_title='BERT Similarity Score',
                yaxis_title='Count',
                height=300,
                showlegend=False
            )
            st.plotly_chart(fig_bert1, use_container_width=True)
        else:
            st.info("No data available")
    
    with col2:
        st.markdown("**Without Sentiment Selection**")
        if bert_dist_without:
            fig_bert2 = go.Figure()
            fig_bert2.add_trace(go.Histogram(
                x=bert_dist_without,
                nbinsx=30,
                marker_color='#ff7f0e',
                name='Without Sentiment'
            ))
            fig_bert2.update_layout(
                xaxis_title='BERT Similarity Score',
                yaxis_title='Count',
                height=300,
                showlegend=False
            )
            st.plotly_chart(fig_bert2, use_container_width=True)
        else:
            st.info("No data available")
    
    st.markdown("---")
    
    # Sentiment Counts
    st.subheader("Sentiment Distribution (=0, >0, <0)")
    st.caption("Count of commentaries by sentiment category")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**With Sentiment Selection**")
        if sentiment_counts_with:
            fig_sent1 = go.Figure()
            
            fig_sent1.add_trace(go.Bar(
                name='Real',
                x=['Negative (<0)', 'Neutral (=0)', 'Positive (>0)'],
                y=[
                    sentiment_counts_with['real']['negative'],
                    sentiment_counts_with['real']['neutral'],
                    sentiment_counts_with['real']['positive']
                ],
                marker_color='#2ca02c'
            ))
            
            fig_sent1.add_trace(go.Bar(
                name='Generated',
                x=['Negative (<0)', 'Neutral (=0)', 'Positive (>0)'],
                y=[
                    sentiment_counts_with['generated']['negative'],
                    sentiment_counts_with['generated']['neutral'],
                    sentiment_counts_with['generated']['positive']
                ],
                marker_color='#d62728'
            ))
            
            fig_sent1.update_layout(
                barmode='group',
                yaxis_title='Count',
                height=300,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5
                )
            )
            st.plotly_chart(fig_sent1, use_container_width=True)
        else:
            st.info("No data available")
    
    with col2:
        st.markdown("**Without Sentiment Selection**")
        if sentiment_counts_without:
            fig_sent2 = go.Figure()
            
            fig_sent2.add_trace(go.Bar(
                name='Real',
                x=['Negative (<0)', 'Neutral (=0)', 'Positive (>0)'],
                y=[
                    sentiment_counts_without['real']['negative'],
                    sentiment_counts_without['real']['neutral'],
                    sentiment_counts_without['real']['positive']
                ],
                marker_color='#2ca02c'
            ))
            
            fig_sent2.add_trace(go.Bar(
                name='Generated',
                x=['Negative (<0)', 'Neutral (=0)', 'Positive (>0)'],
                y=[
                    sentiment_counts_without['generated']['negative'],
                    sentiment_counts_without['generated']['neutral'],
                    sentiment_counts_without['generated']['positive']
                ],
                marker_color='#d62728'
            ))
            
            fig_sent2.update_layout(
                barmode='group',
                yaxis_title='Count',
                height=300,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5
                )
            )
            st.plotly_chart(fig_sent2, use_container_width=True)
        else:
            st.info("No data available")
    
    st.markdown("---")
    
    # Sentiment Sign Agreement
    st.subheader("Sentiment Sign Agreement")
    st.caption("How often real and generated commentary have the same sentiment sign (both positive, both negative, or both neutral)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if sentiment_agreement_with:
            st.metric(
                "Agreement (With Sentiment)",
                f"{sentiment_agreement_with['same_sign_pct']:.1f}%",
                help=f"{sentiment_agreement_with['same_sign']:,} out of {sentiment_agreement_with['total']:,} have same sentiment sign"
            )
        
        if sentiment_agreement_without:
            st.metric(
                "Agreement (Without Sentiment)",
                f"{sentiment_agreement_without['same_sign_pct']:.1f}%",
                help=f"{sentiment_agreement_without['same_sign']:,} out of {sentiment_agreement_without['total']:,} have same sentiment sign"
            )
    
    with col2:
        st.markdown("**Agreement Breakdown (With Sentiment)**")
        if sentiment_agreement_with:
            st.write(f"- Both Negative: {sentiment_agreement_with['both_negative']:,}")
            st.write(f"- Both Neutral: {sentiment_agreement_with['both_neutral']:,}")
            st.write(f"- Both Positive: {sentiment_agreement_with['both_positive']:,}")
            st.write(f"- Different Signs: {sentiment_agreement_with['different_sign']:,} ({sentiment_agreement_with['different_sign_pct']:.1f}%)")
    
    with col3:
        st.markdown("**Agreement Breakdown (Without Sentiment)**")
        if sentiment_agreement_without:
            st.write(f"- Both Negative: {sentiment_agreement_without['both_negative']:,}")
            st.write(f"- Both Neutral: {sentiment_agreement_without['both_neutral']:,}")
            st.write(f"- Both Positive: {sentiment_agreement_without['both_positive']:,}")
            st.write(f"- Different Signs: {sentiment_agreement_without['different_sign']:,} ({sentiment_agreement_without['different_sign_pct']:.1f}%)")
    
    # ========================================
    # SUMMARY TABLE
    # ========================================
    st.markdown('<div class="section-header">📋 Complete Summary Table</div>', unsafe_allow_html=True)
    
    st.caption("Summary of all key metrics for both scoring methods")
    
    summary_df = pd.DataFrame({
        'Metric': [
            'TF-IDF',
            'Embeddings (BERT)',
            'Content Overlap Ratio',
            'NER Score',
            'Sentiment Diff',
            'Avg Score (With Sentiment)',
            'Avg Score (Without Sentiment)',
            'Total Commentary Count',
            'Total Comparison Files',
            'Unique Games',
            'Commentary Avg per Game',
            'Real Words (Avg)',
            'Generated Words (Avg)',
            'Selection Overlap %'
        ],
        'With Sentiment': [
            f"{stats_with_sentiment['TF-IDF']:.4f}",
            f"{stats_with_sentiment['Embeddings_BERT']:.4f}",
            f"{stats_with_sentiment['content_overlap_ratio']:.4f}",
            f"{stats_with_sentiment.get('ner_score', 0):.4f}",
            f"{stats_with_sentiment['sentiment_diff']:.4f}",
            f"{stats_with_sentiment['avg_score']:.4f}",
            f"{stats_with_sentiment['average_score_no_sentiment']:.4f}",
            f"{stats_with_sentiment['commentary_count']:,}",
            f"{stats_with_sentiment['total_comparison_files']}",
            f"{stats_with_sentiment['unique_games']}",
            f"{stats_with_sentiment['commentary_avg_per_game']:.1f}",
            f"{stats_with_sentiment['real_word_count_avg']:.1f}",
            f"{stats_with_sentiment['generated_word_count_avg']:.1f}",
            f"{overlap_pct:.1f}%"
        ],
        'Without Sentiment': [
            f"{stats_without_sentiment['TF-IDF']:.4f}",
            f"{stats_without_sentiment['Embeddings_BERT']:.4f}",
            f"{stats_without_sentiment['content_overlap_ratio']:.4f}",
            f"{stats_without_sentiment.get('ner_score', 0):.4f}",
            f"{stats_without_sentiment['sentiment_diff']:.4f}",
            f"{stats_without_sentiment['avg_score']:.4f}",
            f"{stats_without_sentiment['average_score_no_sentiment']:.4f}",
            f"{stats_without_sentiment['commentary_count']:,}",
            f"{stats_without_sentiment['total_comparison_files']}",
            f"{stats_without_sentiment['unique_games']}",
            f"{stats_without_sentiment['commentary_avg_per_game']:.1f}",
            f"{stats_without_sentiment['real_word_count_avg']:.1f}",
            f"{stats_without_sentiment['generated_word_count_avg']:.1f}",
            f"{overlap_pct:.1f}%"
        ]
    })
    
    st.dataframe(summary_df, hide_index=True, use_container_width=True)
    
    # ========================================
    # ANALYSIS BY REAL_TYPE
    # ========================================
    st.markdown('<div class="section-header">📋 Analysis by Event Type (real_type)</div>', unsafe_allow_html=True)
    
    st.info("Analyze performance metrics for specific event types in real commentary")
    
    # Get real_type counts
    with st.spinner("Loading event types..."):
        type_counts = loader.get_real_type_counts()
    
    if type_counts:
        # Display type counts
        st.subheader("Event Type Distribution")
        type_counts_df = pd.DataFrame({
            'Event Type': list(type_counts.keys()),
            'Count': list(type_counts.values())
        }).sort_values('Count', ascending=False)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Bar chart of counts
            fig_types = go.Figure()
            fig_types.add_trace(go.Bar(
                x=type_counts_df['Event Type'],
                y=type_counts_df['Count'],
                marker_color='#636EFA',
                text=type_counts_df['Count'],
                textposition='auto'
            ))
            fig_types.update_layout(
                xaxis_title='Event Type',
                yaxis_title='Count',
                height=300,
                showlegend=False
            )
            st.plotly_chart(fig_types, use_container_width=True)
        
        with col2:
            st.dataframe(type_counts_df, hide_index=True, use_container_width=True)
        
        st.markdown("---")
        
        # ========================================
        # MULTI-TYPE COMPARISON
        # ========================================
        st.subheader("Scoring Method Comparison Across Key Event Types")
        st.caption("Compare performance metrics across different event types")
        
        # Define key event types to analyze
        key_types = ['General', 'Corner', 'Shot', 'Substitution', 'Free Kick', 
                     'Yellow Card', 'Save', 'Goal']
        
        # Filter to only include types that exist in the data
        available_key_types = [t for t in key_types if t in type_counts]
        
        if available_key_types:
            # Select scoring method for comparison
            comparison_score_type = st.radio(
                "Select scoring method for comparison:",
                options=['average_score', 'average_score_no_sentiment'],
                format_func=lambda x: "With Sentiment" if x == 'average_score' else "Without Sentiment",
                horizontal=True,
                key='multi_type_comparison'
            )
            
            # Get statistics for all key types
            with st.spinner("Calculating statistics for all event types..."):
                type_stats = {}
                for event_type in available_key_types:
                    stats = loader.get_summary_statistics_by_type(event_type, comparison_score_type)
                    if stats:
                        type_stats[event_type] = stats
            
            if type_stats:
                # Prepare data for grouped bar charts
                event_types_list = list(type_stats.keys())
                
                # Create individual metric charts
                metrics_to_plot = [
                    ('TF-IDF', 'TF-IDF'),
                    ('Embeddings_BERT', 'Embeddings BERT'),
                    ('content_overlap_ratio', 'Content Overlap'),
                    ('ner_score', 'NER'),
                    ('sentiment_diff', 'Sentiment Diff'),
                    ('avg_score', 'Avg Score (With Sentiment)'),
                    ('average_score_no_sentiment', 'Avg Score (Without Sentiment)')
                ]
                
                # Create 2x3 grid of charts
                for i in range(0, len(metrics_to_plot), 3):
                    cols = st.columns(3)
                    
                    for j, col in enumerate(cols):
                        if i + j < len(metrics_to_plot):
                            metric_key, metric_label = metrics_to_plot[i + j]
                            
                            with col:
                                st.markdown(f"**{metric_label}**")
                                
                                values = [type_stats[t].get(metric_key, 0) for t in event_types_list]
                                
                                fig = go.Figure()
                                fig.add_trace(go.Bar(
                                    x=event_types_list,
                                    y=values,
                                    text=[f'{v:.3f}' for v in values],
                                    textposition='auto',
                                    marker_color='#1f77b4' if comparison_score_type == 'average_score' else '#ff7f0e'
                                ))
                                
                                fig.update_layout(
                                    yaxis_title='Score',
                                    height=300,
                                    showlegend=False,
                                    xaxis=dict(tickangle=-45)
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                
                # Summary table
                st.subheader("Summary Table: All Event Types")
                
                summary_data = []
                for event_type in event_types_list:
                    stats = type_stats[event_type]
                    summary_data.append({
                        'Event Type': event_type,
                        'Count': f"{stats['commentary_count']:,}",
                        'TF-IDF': f"{stats['TF-IDF']:.4f}",
                        'BERT': f"{stats['Embeddings_BERT']:.4f}",
                        'Content Overlap': f"{stats['content_overlap_ratio']:.4f}",
                        'NER': f"{stats.get('ner_score', 0):.4f}",
                        'Sentiment Diff': f"{stats['sentiment_diff']:.4f}",
                        'Avg Score (With)': f"{stats['avg_score']:.4f}",
                        'Avg Score (Without)': f"{stats['average_score_no_sentiment']:.4f}"
                    })
                
                summary_table_df = pd.DataFrame(summary_data)
                st.dataframe(summary_table_df, hide_index=True, use_container_width=True)
            else:
                st.warning("No statistics available for the selected event types")
        else:
            st.warning(f"None of the key event types {key_types} are available in the data")
        
        st.markdown("---")
        
        # Event type selector
        selected_type = st.selectbox(
            "Select Event Type to Analyze:",
            options=list(type_counts.keys()),
            help="Choose an event type to see detailed analysis"
        )
        
        if selected_type:
            st.subheader(f"Analysis for: {selected_type}")
            st.caption(f"Total occurrences: {type_counts[selected_type]:,}")
            
            # Get data for both methods
            with st.spinner(f"Analyzing {selected_type}..."):
                stats_with = loader.get_summary_statistics_by_type(selected_type, 'average_score')
                stats_without = loader.get_summary_statistics_by_type(selected_type, 'average_score_no_sentiment')
                
                bert_dist_with = loader.get_bert_distribution_by_type(selected_type, 'average_score')
                bert_dist_without = loader.get_bert_distribution_by_type(selected_type, 'average_score_no_sentiment')
                
                sentiment_counts_with = loader.get_sentiment_counts_by_type(selected_type, 'average_score')
                sentiment_counts_without = loader.get_sentiment_counts_by_type(selected_type, 'average_score_no_sentiment')
                
                sentiment_agreement_with = loader.get_sentiment_sign_agreement_by_type(selected_type, 'average_score')
                sentiment_agreement_without = loader.get_sentiment_sign_agreement_by_type(selected_type, 'average_score_no_sentiment')
            
            if stats_with and stats_without:
                # Scoring Method Comparison
                st.markdown("### Scoring Method Comparison")
                
                metrics = ['TF-IDF', 'Embeddings BERT', 'Content Overlap', 'NER', 'Sentiment Diff', 
                          'Avg Score\n(With Sentiment)', 'Avg Score\n(Without Sentiment)']
                with_sentiment_values = [
                    stats_with['TF-IDF'],
                    stats_with['Embeddings_BERT'],
                    stats_with['content_overlap_ratio'],
                    stats_with.get('ner_score', 0),
                    stats_with['sentiment_diff'],
                    stats_with['avg_score'],
                    stats_with['average_score_no_sentiment']
                ]
                without_sentiment_values = [
                    stats_without['TF-IDF'],
                    stats_without['Embeddings_BERT'],
                    stats_without['content_overlap_ratio'],
                    stats_without.get('ner_score', 0),
                    stats_without['sentiment_diff'],
                    stats_without['avg_score'],
                    stats_without['average_score_no_sentiment']
                ]
                
                fig_type_metrics = go.Figure()
                
                fig_type_metrics.add_trace(go.Bar(
                    name='With Sentiment',
                    x=metrics,
                    y=with_sentiment_values,
                    text=[f'{v:.4f}' for v in with_sentiment_values],
                    textposition='auto',
                    marker_color='#1f77b4'
                ))
                
                fig_type_metrics.add_trace(go.Bar(
                    name='Without Sentiment',
                    x=metrics,
                    y=without_sentiment_values,
                    text=[f'{v:.4f}' for v in without_sentiment_values],
                    textposition='auto',
                    marker_color='#ff7f0e'
                ))
                
                fig_type_metrics.update_layout(
                    barmode='group',
                    yaxis_title='Score (0-1)',
                    xaxis_title='Metric',
                    height=400,
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5
                    ),
                    xaxis=dict(tickangle=0)
                )
                
                st.plotly_chart(fig_type_metrics, use_container_width=True)
                
                st.markdown("---")
                
                # BERT Distribution
                st.markdown("### Embeddings_BERT Distribution")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**With Sentiment Selection**")
                    if bert_dist_with:
                        fig_bert1 = go.Figure()
                        fig_bert1.add_trace(go.Histogram(
                            x=bert_dist_with,
                            nbinsx=20,
                            marker_color='#1f77b4'
                        ))
                        fig_bert1.update_layout(
                            xaxis_title='BERT Similarity',
                            yaxis_title='Count',
                            height=250,
                            showlegend=False
                        )
                        st.plotly_chart(fig_bert1, use_container_width=True)
                    else:
                        st.info("No data available")
                
                with col2:
                    st.markdown("**Without Sentiment Selection**")
                    if bert_dist_without:
                        fig_bert2 = go.Figure()
                        fig_bert2.add_trace(go.Histogram(
                            x=bert_dist_without,
                            nbinsx=20,
                            marker_color='#ff7f0e'
                        ))
                        fig_bert2.update_layout(
                            xaxis_title='BERT Similarity',
                            yaxis_title='Count',
                            height=250,
                            showlegend=False
                        )
                        st.plotly_chart(fig_bert2, use_container_width=True)
                    else:
                        st.info("No data available")
                
                st.markdown("---")
                
                # Sentiment Distribution
                st.markdown("### Sentiment Distribution")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**With Sentiment Selection**")
                    if sentiment_counts_with:
                        fig_sent1 = go.Figure()
                        
                        fig_sent1.add_trace(go.Bar(
                            name='Real',
                            x=['Negative', 'Neutral', 'Positive'],
                            y=[
                                sentiment_counts_with['real']['negative'],
                                sentiment_counts_with['real']['neutral'],
                                sentiment_counts_with['real']['positive']
                            ],
                            marker_color='#2ca02c'
                        ))
                        
                        fig_sent1.add_trace(go.Bar(
                            name='Generated',
                            x=['Negative', 'Neutral', 'Positive'],
                            y=[
                                sentiment_counts_with['generated']['negative'],
                                sentiment_counts_with['generated']['neutral'],
                                sentiment_counts_with['generated']['positive']
                            ],
                            marker_color='#d62728'
                        ))
                        
                        fig_sent1.update_layout(
                            barmode='group',
                            yaxis_title='Count',
                            height=250,
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
                        )
                        st.plotly_chart(fig_sent1, use_container_width=True)
                    else:
                        st.info("No data available")
                
                with col2:
                    st.markdown("**Without Sentiment Selection**")
                    if sentiment_counts_without:
                        fig_sent2 = go.Figure()
                        
                        fig_sent2.add_trace(go.Bar(
                            name='Real',
                            x=['Negative', 'Neutral', 'Positive'],
                            y=[
                                sentiment_counts_without['real']['negative'],
                                sentiment_counts_without['real']['neutral'],
                                sentiment_counts_without['real']['positive']
                            ],
                            marker_color='#2ca02c'
                        ))
                        
                        fig_sent2.add_trace(go.Bar(
                            name='Generated',
                            x=['Negative', 'Neutral', 'Positive'],
                            y=[
                                sentiment_counts_without['generated']['negative'],
                                sentiment_counts_without['generated']['neutral'],
                                sentiment_counts_without['generated']['positive']
                            ],
                            marker_color='#d62728'
                        ))
                        
                        fig_sent2.update_layout(
                            barmode='group',
                            yaxis_title='Count',
                            height=250,
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
                        )
                        st.plotly_chart(fig_sent2, use_container_width=True)
                    else:
                        st.info("No data available")
                
                st.markdown("---")
                
                # Sentiment Sign Agreement
                st.markdown("### Sentiment Sign Agreement")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if sentiment_agreement_with:
                        st.metric(
                            "Agreement (With Sentiment)",
                            f"{sentiment_agreement_with['same_sign_pct']:.1f}%",
                            help=f"{sentiment_agreement_with['same_sign']:,} out of {sentiment_agreement_with['total']:,}"
                        )
                    
                    if sentiment_agreement_without:
                        st.metric(
                            "Agreement (Without Sentiment)",
                            f"{sentiment_agreement_without['same_sign_pct']:.1f}%",
                            help=f"{sentiment_agreement_without['same_sign']:,} out of {sentiment_agreement_without['total']:,}"
                        )
                
                with col2:
                    st.markdown("**With Sentiment**")
                    if sentiment_agreement_with:
                        st.write(f"- Both Negative: {sentiment_agreement_with['both_negative']:,}")
                        st.write(f"- Both Neutral: {sentiment_agreement_with['both_neutral']:,}")
                        st.write(f"- Both Positive: {sentiment_agreement_with['both_positive']:,}")
                        st.write(f"- Different: {sentiment_agreement_with['different_sign']:,}")
                
                with col3:
                    st.markdown("**Without Sentiment**")
                    if sentiment_agreement_without:
                        st.write(f"- Both Negative: {sentiment_agreement_without['both_negative']:,}")
                        st.write(f"- Both Neutral: {sentiment_agreement_without['both_neutral']:,}")
                        st.write(f"- Both Positive: {sentiment_agreement_without['both_positive']:,}")
                        st.write(f"- Different: {sentiment_agreement_without['different_sign']:,}")
            else:
                st.warning(f"No data available for {selected_type}")
    else:
        st.warning("No event type data available")
    
    # ========================================
    # ANALYSIS BY BERT SCORE RANGE
    # ========================================
    st.markdown('<div class="section-header">📊 Analysis by BERT Score Range</div>', unsafe_allow_html=True)
    
    st.info("Compare performance across different BERT similarity score ranges")
    
    # Get BERT range counts
    with st.spinner("Loading BERT ranges..."):
        bert_range_counts = loader.get_bert_range_counts()
    
    if bert_range_counts:
        # Display BERT range distribution
        st.subheader("BERT Score Range Distribution")
        
        bert_range_df = pd.DataFrame({
            'BERT Range': list(bert_range_counts.keys()),
            'Count': list(bert_range_counts.values())
        })
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig_bert_range = go.Figure()
            fig_bert_range.add_trace(go.Bar(
                x=bert_range_df['BERT Range'],
                y=bert_range_df['Count'],
                marker_color=['#d62728', '#ff7f0e', '#2ca02c'],  # Red, Orange, Green
                text=bert_range_df['Count'],
                textposition='auto'
            ))
            fig_bert_range.update_layout(
                xaxis_title='BERT Score Range',
                yaxis_title='Count',
                height=300,
                showlegend=False
            )
            st.plotly_chart(fig_bert_range, use_container_width=True)
        
        with col2:
            st.dataframe(bert_range_df, hide_index=True, use_container_width=True)
        
        st.markdown("---")
        
        # Multi-range comparison
        st.subheader("Scoring Method Comparison Across BERT Ranges")
        
        comparison_score_type_bert = st.radio(
            "Select scoring method for BERT range comparison:",
            options=['average_score', 'average_score_no_sentiment'],
            format_func=lambda x: "With Sentiment" if x == 'average_score' else "Without Sentiment",
            horizontal=True,
            key='bert_range_comparison'
        )
        
        # Get statistics for all BERT ranges
        with st.spinner("Calculating statistics for BERT ranges..."):
            bert_range_stats = {}
            for bert_range in bert_range_counts.keys():
                stats = loader.get_summary_statistics_by_bert_range(bert_range, comparison_score_type_bert)
                if stats:
                    bert_range_stats[bert_range] = stats
        
        if bert_range_stats:
            bert_ranges_list = list(bert_range_stats.keys())
            
            # Create grid of charts (7 metrics = 3+3+1)
            metrics_to_plot = [
                ('TF-IDF', 'TF-IDF'),
                ('Embeddings_BERT', 'Embeddings BERT'),
                ('content_overlap_ratio', 'Content Overlap'),
                ('ner_score', 'NER'),
                ('sentiment_diff', 'Sentiment Diff'),
                ('avg_score', 'Avg Score (With Sentiment)'),
                ('average_score_no_sentiment', 'Avg Score (Without Sentiment)')
            ]
            
            for i in range(0, len(metrics_to_plot), 3):
                cols = st.columns(3)
                
                for j, col in enumerate(cols):
                    if i + j < len(metrics_to_plot):
                        metric_key, metric_label = metrics_to_plot[i + j]
                        
                        with col:
                            st.markdown(f"**{metric_label}**")
                            
                            values = [bert_range_stats[r].get(metric_key, 0) for r in bert_ranges_list]
                            
                            fig = go.Figure()
                            fig.add_trace(go.Bar(
                                x=bert_ranges_list,
                                y=values,
                                text=[f'{v:.3f}' for v in values],
                                textposition='auto',
                                marker_color=['#d62728', '#ff7f0e', '#2ca02c']
                            ))
                            
                            fig.update_layout(
                                yaxis_title='Score',
                                height=300,
                                showlegend=False
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Summary table
            st.subheader("Summary Table: BERT Ranges")
            
            summary_data = []
            for bert_range in bert_ranges_list:
                stats = bert_range_stats[bert_range]
                summary_data.append({
                    'BERT Range': bert_range,
                    'Count': f"{stats['commentary_count']:,}",
                    'TF-IDF': f"{stats['TF-IDF']:.4f}",
                    'BERT': f"{stats['Embeddings_BERT']:.4f}",
                    'Content Overlap': f"{stats['content_overlap_ratio']:.4f}",
                    'NER': f"{stats.get('ner_score', 0):.4f}",
                    'Sentiment Diff': f"{stats['sentiment_diff']:.4f}",
                    'Avg Score (With)': f"{stats['avg_score']:.4f}",
                    'Avg Score (Without)': f"{stats['average_score_no_sentiment']:.4f}"
                })
            
            summary_table_df = pd.DataFrame(summary_data)
            st.dataframe(summary_table_df, hide_index=True, use_container_width=True)
            
            # ========================================
            # SENTIMENT DISTRIBUTION BY BERT RANGE
            # ========================================
            st.markdown("---")
            st.subheader("Sentiment Distribution by BERT Range")
            st.caption("Count of commentaries by sentiment category for each BERT range")
            
            # Selection Bias Explanation
            st.info("""
            **⚠️ Understanding the Selection Bias Phenomenon**
            
            You'll notice a counter-intuitive pattern: **Lower BERT similarity has HIGHER sentiment sign accuracy!**
            
            - **Low BERT (0-0.45)**: ~72% sentiment accuracy
            - **Medium BERT (0.45-0.55)**: ~68% sentiment accuracy  
            - **High BERT (>0.55)**: ~58% sentiment accuracy
            
            **Why does this happen?** It's selection bias from our "best match" selection process!
            
            📊 **Analogy: University Admission**
            - **Student A** (Low test score 33/100) → Only accepted if attendance is PERFECT
            - **Student B** (High test score 64/100) → Accepted with average attendance
            - Among accepted students, Student A types have better attendance - but only due to selection bias!
            
            **Same logic here:**
            - **Low BERT matches** must have excellent sentiment (and other scores) to be selected as "best match"
            - **High BERT matches** get selected even with mediocre sentiment (BERT score carries them)
            - Result: Among *selected* matches, low BERT shows higher sentiment accuracy
            
            **This is NOT causation** - it's an artifact of the multi-score selection filter!
            """)
            
            # Select BERT range
            selected_bert_range = st.radio(
                "Select BERT Range:",
                options=bert_ranges_list,
                horizontal=True,
                key='bert_range_sentiment_selector'
            )
            
            # Get sentiment counts for selected BERT range
            sentiment_counts_with = loader.get_sentiment_counts_by_bert_range(selected_bert_range, 'average_score')
            sentiment_counts_without = loader.get_sentiment_counts_by_bert_range(selected_bert_range, 'average_score_no_sentiment')
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**With Sentiment Selection**")
                if sentiment_counts_with:
                    fig_sent1 = go.Figure()
                    
                    fig_sent1.add_trace(go.Bar(
                        name='Real',
                        x=['Negative (<0)', 'Neutral (=0)', 'Positive (>0)'],
                        y=[
                            sentiment_counts_with['real']['negative'],
                            sentiment_counts_with['real']['neutral'],
                            sentiment_counts_with['real']['positive']
                        ],
                        marker_color='#2ca02c'
                    ))
                    
                    fig_sent1.add_trace(go.Bar(
                        name='Generated',
                        x=['Negative (<0)', 'Neutral (=0)', 'Positive (>0)'],
                        y=[
                            sentiment_counts_with['generated']['negative'],
                            sentiment_counts_with['generated']['neutral'],
                            sentiment_counts_with['generated']['positive']
                        ],
                        marker_color='#d62728'
                    ))
                    
                    fig_sent1.update_layout(
                        barmode='group',
                        yaxis_title='Count',
                        height=300,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="center",
                            x=0.5
                        )
                    )
                    st.plotly_chart(fig_sent1, use_container_width=True)
                else:
                    st.info("No data available")
            
            with col2:
                st.markdown("**Without Sentiment Selection**")
                if sentiment_counts_without:
                    fig_sent2 = go.Figure()
                    
                    fig_sent2.add_trace(go.Bar(
                        name='Real',
                        x=['Negative (<0)', 'Neutral (=0)', 'Positive (>0)'],
                        y=[
                            sentiment_counts_without['real']['negative'],
                            sentiment_counts_without['real']['neutral'],
                            sentiment_counts_without['real']['positive']
                        ],
                        marker_color='#2ca02c'
                    ))
                    
                    fig_sent2.add_trace(go.Bar(
                        name='Generated',
                        x=['Negative (<0)', 'Neutral (=0)', 'Positive (>0)'],
                        y=[
                            sentiment_counts_without['generated']['negative'],
                            sentiment_counts_without['generated']['neutral'],
                            sentiment_counts_without['generated']['positive']
                        ],
                        marker_color='#d62728'
                    ))
                    
                    fig_sent2.update_layout(
                        barmode='group',
                        yaxis_title='Count',
                        height=300,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="center",
                            x=0.5
                        )
                    )
                    st.plotly_chart(fig_sent2, use_container_width=True)
                else:
                    st.info("No data available")
            
            # Sentiment Sign Agreement
            st.markdown("---")
            st.markdown("### Sentiment Sign Agreement")
            
            sentiment_agreement_with = loader.get_sentiment_sign_agreement_by_bert_range(selected_bert_range, 'average_score')
            sentiment_agreement_without = loader.get_sentiment_sign_agreement_by_bert_range(selected_bert_range, 'average_score_no_sentiment')
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if sentiment_agreement_with:
                    st.metric(
                        "Agreement (With Sentiment)",
                        f"{sentiment_agreement_with['same_sign_pct']:.1f}%",
                        help=f"{sentiment_agreement_with['same_sign']:,} out of {sentiment_agreement_with['total']:,}"
                    )
                
                if sentiment_agreement_without:
                    st.metric(
                        "Agreement (Without Sentiment)",
                        f"{sentiment_agreement_without['same_sign_pct']:.1f}%",
                        help=f"{sentiment_agreement_without['same_sign']:,} out of {sentiment_agreement_without['total']:,}"
                    )
            
            with col2:
                st.markdown("**With Sentiment**")
                if sentiment_agreement_with:
                    st.write(f"- Both Negative: {sentiment_agreement_with['both_negative']:,}")
                    st.write(f"- Both Neutral: {sentiment_agreement_with['both_neutral']:,}")
                    st.write(f"- Both Positive: {sentiment_agreement_with['both_positive']:,}")
                    st.write(f"- Different: {sentiment_agreement_with['different_sign']:,}")
            
            with col3:
                st.markdown("**Without Sentiment**")
                if sentiment_agreement_without:
                    st.write(f"- Both Negative: {sentiment_agreement_without['both_negative']:,}")
                    st.write(f"- Both Neutral: {sentiment_agreement_without['both_neutral']:,}")
                    st.write(f"- Both Positive: {sentiment_agreement_without['both_positive']:,}")
                    st.write(f"- Different: {sentiment_agreement_without['different_sign']:,}")
            
            # ========================================
            # EVENT DISTRIBUTION BY BERT RANGE
            # ========================================
            st.markdown("---")
            st.subheader("📋 Top 15 Event Distribution by BERT Range")
            st.caption("Event type distribution with % of group and % of total event")
            
            # Select BERT range for event distribution
            selected_bert_range_events = st.radio(
                "Select BERT Range for Event Distribution:",
                options=bert_ranges_list,
                horizontal=True,
                key='bert_range_events_selector'
            )
            
            # Get event distribution for selected range
            with st.spinner(f"Loading event distribution for {selected_bert_range_events}..."):
                event_dist_with = loader.get_event_distribution_by_bert_range(selected_bert_range_events, 'average_score')
                event_dist_without = loader.get_event_distribution_by_bert_range(selected_bert_range_events, 'average_score_no_sentiment')
            
            # Bar charts
            if event_dist_with or event_dist_without:
                st.markdown("### 📊 Event Distribution Charts")
                
                col1_chart, col2_chart = st.columns(2)
                
                with col1_chart:
                    st.markdown("**With Sentiment Selection**")
                    if event_dist_with:
                        # Sort by count and take top 15
                        sorted_events = sorted(event_dist_with.items(), key=lambda x: x[1]['count'], reverse=True)[:15]
                        event_names = [event for event, data in sorted_events]
                        event_counts = [data['count'] for event, data in sorted_events]
                        
                        fig_events_with = go.Figure()
                        fig_events_with.add_trace(go.Bar(
                            x=event_counts,
                            y=event_names,
                            orientation='h',
                            marker_color='#1f77b4',
                            text=event_counts,
                            textposition='auto'
                        ))
                        
                        fig_events_with.update_layout(
                            xaxis_title='Count',
                            yaxis_title='Event Type',
                            height=500,
                            showlegend=False,
                            yaxis={'categoryorder': 'total ascending'}
                        )
                        
                        st.plotly_chart(fig_events_with, use_container_width=True)
                    else:
                        st.info("No data available")
                
                with col2_chart:
                    st.markdown("**Without Sentiment Selection**")
                    if event_dist_without:
                        # Sort by count and take top 15
                        sorted_events = sorted(event_dist_without.items(), key=lambda x: x[1]['count'], reverse=True)[:15]
                        event_names = [event for event, data in sorted_events]
                        event_counts = [data['count'] for event, data in sorted_events]
                        
                        fig_events_without = go.Figure()
                        fig_events_without.add_trace(go.Bar(
                            x=event_counts,
                            y=event_names,
                            orientation='h',
                            marker_color='#ff7f0e',
                            text=event_counts,
                            textposition='auto'
                        ))
                        
                        fig_events_without.update_layout(
                            xaxis_title='Count',
                            yaxis_title='Event Type',
                            height=500,
                            showlegend=False,
                            yaxis={'categoryorder': 'total ascending'}
                        )
                        
                        st.plotly_chart(fig_events_without, use_container_width=True)
                    else:
                        st.info("No data available")
                
                st.markdown("---")
            
            # Tables
            st.markdown("### 📋 Detailed Event Distribution Tables")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**With Sentiment Selection**")
                if event_dist_with:
                    # Sort by count and take top 15
                    sorted_events = sorted(event_dist_with.items(), key=lambda x: x[1]['count'], reverse=True)[:15]
                    
                    # Calculate % of group (total for ALL events in group, not just top 15)
                    total_in_group = sum(data['count'] for event_type, data in event_dist_with.items())
                    
                    table_data = []
                    for event_type, data in sorted_events:
                        pct_of_group = (data['count'] / total_in_group * 100) if total_in_group > 0 else 0
                        table_data.append({
                            'Event Type': event_type,
                            'Count': f"{data['count']:,}",
                            '% of Group': f"{pct_of_group:.1f}%",
                            '% of Total Event': f"{data['pct_of_total']:.1f}%"
                        })
                    
                    st.dataframe(pd.DataFrame(table_data), hide_index=True, use_container_width=True, height=400)
                else:
                    st.info("No data available")
            
            with col2:
                st.markdown("**Without Sentiment Selection**")
                if event_dist_without:
                    # Sort by count and take top 15
                    sorted_events = sorted(event_dist_without.items(), key=lambda x: x[1]['count'], reverse=True)[:15]
                    
                    # Calculate % of group (total for ALL events in group, not just top 15)
                    total_in_group = sum(data['count'] for event_type, data in event_dist_without.items())
                    
                    table_data = []
                    for event_type, data in sorted_events:
                        pct_of_group = (data['count'] / total_in_group * 100) if total_in_group > 0 else 0
                        table_data.append({
                            'Event Type': event_type,
                            'Count': f"{data['count']:,}",
                            '% of Group': f"{pct_of_group:.1f}%",
                            '% of Total Event': f"{data['pct_of_total']:.1f}%"
                        })
                    
                    st.dataframe(pd.DataFrame(table_data), hide_index=True, use_container_width=True, height=400)
                else:
                    st.info("No data available")
    else:
        st.warning("No BERT range data available")
    
    # ========================================
    # ANALYSIS BY DATA SOURCE
    # ========================================
    st.markdown('<div class="section-header">📰 Analysis by Data Source</div>', unsafe_allow_html=True)
    
    st.info("Compare performance across different commentary data sources")
    
    # Get source counts
    with st.spinner("Loading data sources..."):
        source_counts = loader.get_source_counts()
    
    if source_counts:
        # Display source distribution
        st.subheader("Data Source Distribution")
        
        source_df = pd.DataFrame({
            'Data Source': list(source_counts.keys()),
            'Count': list(source_counts.values())
        }).sort_values('Count', ascending=False)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig_source = go.Figure()
            fig_source.add_trace(go.Bar(
                x=source_df['Data Source'],
                y=source_df['Count'],
                marker_color='#9467bd',
                text=source_df['Count'],
                textposition='auto'
            ))
            fig_source.update_layout(
                xaxis_title='Data Source',
                yaxis_title='Count',
                height=300,
                showlegend=False
            )
            st.plotly_chart(fig_source, use_container_width=True)
        
        with col2:
            st.dataframe(source_df, hide_index=True, use_container_width=True)
        
        st.markdown("---")
        
        # Average Word Count by Data Source
        st.subheader("Average Words per Commentary by Data Source")
        
        # Get word count data for both scoring methods
        with st.spinner("Calculating average word counts..."):
            word_count_with = loader.get_avg_word_count_by_source('average_score')
            word_count_without = loader.get_avg_word_count_by_source('average_score_no_sentiment')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**With Sentiment Selection**")
            if word_count_with:
                # Sort by source name
                sorted_sources = sorted(word_count_with.keys())
                real_avgs = [word_count_with[source]['real_avg'] for source in sorted_sources]
                gen_avgs = [word_count_with[source]['generated_avg'] for source in sorted_sources]
                
                fig_words_with = go.Figure()
                
                fig_words_with.add_trace(go.Bar(
                    name='Real Commentary',
                    x=sorted_sources,
                    y=real_avgs,
                    marker_color='#2ca02c',
                    text=[f"{avg:.1f}" for avg in real_avgs],
                    textposition='auto'
                ))
                
                fig_words_with.add_trace(go.Bar(
                    name='Generated Commentary',
                    x=sorted_sources,
                    y=gen_avgs,
                    marker_color='#d62728',
                    text=[f"{avg:.1f}" for avg in gen_avgs],
                    textposition='auto'
                ))
                
                fig_words_with.update_layout(
                    barmode='group',
                    xaxis_title='Data Source',
                    yaxis_title='Average Word Count',
                    height=400,
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5
                    )
                )
                
                st.plotly_chart(fig_words_with, use_container_width=True)
            else:
                st.info("No data available")
        
        with col2:
            st.markdown("**Without Sentiment Selection**")
            if word_count_without:
                # Sort by source name
                sorted_sources = sorted(word_count_without.keys())
                real_avgs = [word_count_without[source]['real_avg'] for source in sorted_sources]
                gen_avgs = [word_count_without[source]['generated_avg'] for source in sorted_sources]
                
                fig_words_without = go.Figure()
                
                fig_words_without.add_trace(go.Bar(
                    name='Real Commentary',
                    x=sorted_sources,
                    y=real_avgs,
                    marker_color='#2ca02c',
                    text=[f"{avg:.1f}" for avg in real_avgs],
                    textposition='auto'
                ))
                
                fig_words_without.add_trace(go.Bar(
                    name='Generated Commentary',
                    x=sorted_sources,
                    y=gen_avgs,
                    marker_color='#d62728',
                    text=[f"{avg:.1f}" for avg in gen_avgs],
                    textposition='auto'
                ))
                
                fig_words_without.update_layout(
                    barmode='group',
                    xaxis_title='Data Source',
                    yaxis_title='Average Word Count',
                    height=400,
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5
                    )
                )
                
                st.plotly_chart(fig_words_without, use_container_width=True)
            else:
                st.info("No data available")
        
        st.markdown("---")
        
        # Multi-source comparison
        st.subheader("Scoring Method Comparison Across Data Sources")
        
        comparison_score_type_source = st.radio(
            "Select scoring method for data source comparison:",
            options=['average_score', 'average_score_no_sentiment'],
            format_func=lambda x: "With Sentiment" if x == 'average_score' else "Without Sentiment",
            horizontal=True,
            key='source_comparison'
        )
        
        # Get statistics for all sources
        with st.spinner("Calculating statistics for data sources..."):
            source_stats = {}
            for source in source_counts.keys():
                stats = loader.get_summary_statistics_by_source(source, comparison_score_type_source)
                if stats:
                    source_stats[source] = stats
        
        if source_stats:
            sources_list = list(source_stats.keys())
            
            # Create 2x3 grid of charts
            for i in range(0, len(metrics_to_plot), 3):
                cols = st.columns(3)
                
                for j, col in enumerate(cols):
                    if i + j < len(metrics_to_plot):
                        metric_key, metric_label = metrics_to_plot[i + j]
                        
                        with col:
                            st.markdown(f"**{metric_label}**")
                            
                            values = [source_stats[s].get(metric_key, 0) for s in sources_list]
                            
                            fig = go.Figure()
                            fig.add_trace(go.Bar(
                                x=sources_list,
                                y=values,
                                text=[f'{v:.3f}' for v in values],
                                textposition='auto',
                                marker_color='#9467bd'
                            ))
                            
                            fig.update_layout(
                                yaxis_title='Score',
                                height=300,
                                showlegend=False,
                                xaxis=dict(tickangle=-45)
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Summary table
            st.subheader("Summary Table: Data Sources")
            
            summary_data = []
            for source in sources_list:
                stats = source_stats[source]
                summary_data.append({
                    'Data Source': source,
                    'Count': f"{stats['commentary_count']:,}",
                    'TF-IDF': f"{stats['TF-IDF']:.4f}",
                    'BERT': f"{stats['Embeddings_BERT']:.4f}",
                    'Content Overlap': f"{stats['content_overlap_ratio']:.4f}",
                    'NER': f"{stats.get('ner_score', 0):.4f}",
                    'Sentiment Diff': f"{stats['sentiment_diff']:.4f}",
                    'Avg Score (With)': f"{stats['avg_score']:.4f}",
                    'Avg Score (Without)': f"{stats['average_score_no_sentiment']:.4f}"
                })
            
            summary_table_df = pd.DataFrame(summary_data)
            st.dataframe(summary_table_df, hide_index=True, use_container_width=True)
        
        st.markdown("---")
        
        # Average Word Count by Event Type per Data Source
        st.subheader("Average Words per Commentary by Top 10 Event Types (per Data Source)")
        st.caption("Select a data source to see average word counts for its top 10 event types")
        
        # Selector for data source
        selected_source_for_events = st.selectbox(
            "Select Data Source:",
            options=list(source_counts.keys()),
            key='source_event_word_count_selector'
        )
        
        # Get word count data for both scoring methods
        with st.spinner(f"Calculating average word counts for top 10 event types in {selected_source_for_events}..."):
            word_count_with = loader.get_avg_word_count_by_event_type_for_source(selected_source_for_events, 'average_score', top_n=10)
            word_count_without = loader.get_avg_word_count_by_event_type_for_source(selected_source_for_events, 'average_score_no_sentiment', top_n=10)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**With Sentiment Selection**")
            if word_count_with:
                # Sort by count (descending)
                sorted_events = sorted(word_count_with.items(), key=lambda x: x[1]['count'], reverse=True)
                event_names = [event for event, data in sorted_events]
                real_avgs = [data['real_avg'] for event, data in sorted_events]
                gen_avgs = [data['generated_avg'] for event, data in sorted_events]
                
                fig_words_event_with = go.Figure()
                
                fig_words_event_with.add_trace(go.Bar(
                    name='Real Commentary',
                    x=event_names,
                    y=real_avgs,
                    marker_color='#2ca02c',
                    text=[f"{avg:.1f}" for avg in real_avgs],
                    textposition='auto'
                ))
                
                fig_words_event_with.add_trace(go.Bar(
                    name='Generated Commentary',
                    x=event_names,
                    y=gen_avgs,
                    marker_color='#d62728',
                    text=[f"{avg:.1f}" for avg in gen_avgs],
                    textposition='auto'
                ))
                
                fig_words_event_with.update_layout(
                    barmode='group',
                    xaxis_title='Event Type',
                    yaxis_title='Average Word Count',
                    height=400,
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5
                    )
                )
                
                st.plotly_chart(fig_words_event_with, use_container_width=True)
            else:
                st.info("No data available")
        
        with col2:
            st.markdown("**Without Sentiment Selection**")
            if word_count_without:
                # Sort by count (descending)
                sorted_events = sorted(word_count_without.items(), key=lambda x: x[1]['count'], reverse=True)
                event_names = [event for event, data in sorted_events]
                real_avgs = [data['real_avg'] for event, data in sorted_events]
                gen_avgs = [data['generated_avg'] for event, data in sorted_events]
                
                fig_words_event_without = go.Figure()
                
                fig_words_event_without.add_trace(go.Bar(
                    name='Real Commentary',
                    x=event_names,
                    y=real_avgs,
                    marker_color='#2ca02c',
                    text=[f"{avg:.1f}" for avg in real_avgs],
                    textposition='auto'
                ))
                
                fig_words_event_without.add_trace(go.Bar(
                    name='Generated Commentary',
                    x=event_names,
                    y=gen_avgs,
                    marker_color='#d62728',
                    text=[f"{avg:.1f}" for avg in gen_avgs],
                    textposition='auto'
                ))
                
                fig_words_event_without.update_layout(
                    barmode='group',
                    xaxis_title='Event Type',
                    yaxis_title='Average Word Count',
                    height=400,
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5
                    )
                )
                
                st.plotly_chart(fig_words_event_without, use_container_width=True)
            else:
                st.info("No data available")
    else:
        st.warning("No data source information available")
    
    # ========================================
    # OVERLAP vs DIFFERENT SELECTIONS ANALYSIS
    # ========================================
    st.markdown('<div class="section-header">🔄 Overlap vs Different Selections Analysis</div>', unsafe_allow_html=True)
    
    st.info("""
    **Comparing Selection Agreement vs Disagreement**
    
    - **Overlap**: Both scoring methods (With Sentiment and Without Sentiment) selected the **same best match**
    - **Different Selections**: The two scoring methods selected **different best matches**
    """)
    
    # Load all data upfront
    with st.spinner("Loading analysis data..."):
        overlap_pct = loader.get_overlap_percentage()
        different_pct = loader.get_different_percentage()
        overlap_events = loader.get_overlap_event_distribution(top_n=10)
        different_events = loader.get_different_event_distribution(top_n=10)
        overlap_bert = loader.get_overlap_bert_distribution()
        different_bert = loader.get_different_bert_scores()
        overlap_sentiment_agree = loader.get_overlap_sentiment_agreement()
        different_sentiment_agree = loader.get_different_sentiment_agreement()
        overlap_sentiment_dist = loader.get_overlap_sentiment_distribution()
        different_sentiment_dist = loader.get_different_sentiment_distribution()
    
    # Overall Metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("🔄 Overlap Percentage", f"{overlap_pct:.1f}%", 
                  help="Both methods selected the same best match")
    
    with col2:
        st.metric("🔀 Different Selections Percentage", f"{different_pct:.1f}%", 
                  help="Methods selected different best matches")
    
    st.markdown("---")
    
    # ========================================
    # TOP 10 EVENT TYPES
    # ========================================
    st.subheader("📊 Top 10 Event Types Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔄 Overlap Matches**")
        if overlap_events:
            sorted_events = sorted(overlap_events.items(), key=lambda x: x[1]['count'], reverse=True)
            event_names = [event for event, data in sorted_events]
            event_counts = [data['count'] for event, data in sorted_events]
            event_pcts = [data['pct'] for event, data in sorted_events]
            
            fig_overlap = go.Figure()
            fig_overlap.add_trace(go.Bar(
                x=event_names,
                y=event_counts,
                marker_color='#17becf',
                text=[f"{count:,}<br>({pct:.1f}%)" for count, pct in zip(event_counts, event_pcts)],
                textposition='auto'
            ))
            
            fig_overlap.update_layout(
                xaxis_title='Event Type',
                yaxis_title='Count',
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig_overlap, use_container_width=True)
        else:
            st.warning("No data available")
    
    with col2:
        st.markdown("**🔀 Different Selection Matches**")
        if different_events:
            sorted_events_diff = sorted(different_events.items(), key=lambda x: x[1]['count'], reverse=True)
            event_names_diff = [event for event, data in sorted_events_diff]
            event_counts_diff = [data['count'] for event, data in sorted_events_diff]
            event_pcts_diff = [data['pct'] for event, data in sorted_events_diff]
            
            fig_different = go.Figure()
            fig_different.add_trace(go.Bar(
                x=event_names_diff,
                y=event_counts_diff,
                marker_color='#e377c2',
                text=[f"{count:,}<br>({pct:.1f}%)" for count, pct in zip(event_counts_diff, event_pcts_diff)],
                textposition='auto'
            ))
            
            fig_different.update_layout(
                xaxis_title='Event Type',
                yaxis_title='Count',
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig_different, use_container_width=True)
        else:
            st.warning("No data available")
    
    st.markdown("---")
    
    # ========================================
    # BERT SCORES
    # ========================================
    st.subheader("📈 BERT Score Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔄 Overlap Matches**")
        st.caption("Average BERT score (same match selected by both methods)")
        if overlap_bert:
            st.metric("Average BERT Score", f"{overlap_bert['mean']:.4f}",
                     help=f"Based on {overlap_bert['count']:,} matches")
        else:
            st.warning("No data available")
    
    with col2:
        st.markdown("**🔀 Different Selection Matches**")
        st.caption("Average BERT scores for each method's selection")
        if different_bert:
            subcol1, subcol2 = st.columns(2)
            with subcol1:
                st.metric("With Sentiment", f"{different_bert['with_sentiment']:.4f}",
                         help="Average BERT for 'with sentiment' selection")
            with subcol2:
                st.metric("Without Sentiment", f"{different_bert['without_sentiment']:.4f}",
                         help="Average BERT for 'without sentiment' selection")
        else:
            st.warning("No data available")
    
    st.markdown("---")
    
    # ========================================
    # SENTIMENT SIGN AGREEMENT
    # ========================================
    st.subheader("💭 Sentiment Sign Agreement Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔄 Overlap Matches**")
        if overlap_sentiment_agree:
            st.metric("Agreement Rate", f"{overlap_sentiment_agree['same_sign_pct']:.1f}%",
                     help=f"{overlap_sentiment_agree['same_sign']:,} / {overlap_sentiment_agree['total']:,}")
            
            st.markdown("**Breakdown:**")
            st.write(f"- Both Negative: {overlap_sentiment_agree['both_negative']:,}")
            st.write(f"- Both Neutral: {overlap_sentiment_agree['both_neutral']:,}")
            st.write(f"- Both Positive: {overlap_sentiment_agree['both_positive']:,}")
            st.write(f"- Different Signs: {overlap_sentiment_agree['different_sign']:,}")
        else:
            st.warning("No data available")
    
    with col2:
        st.markdown("**🔀 Different Selection Matches**")
        if different_sentiment_agree:
            st.metric("Agreement Rate", f"{different_sentiment_agree['same_sign_pct']:.1f}%",
                     help=f"{different_sentiment_agree['same_sign']:,} / {different_sentiment_agree['total']:,}")
            
            st.markdown("**Breakdown:**")
            st.write(f"- Both Negative: {different_sentiment_agree['both_negative']:,}")
            st.write(f"- Both Neutral: {different_sentiment_agree['both_neutral']:,}")
            st.write(f"- Both Positive: {different_sentiment_agree['both_positive']:,}")
            st.write(f"- Different Signs: {different_sentiment_agree['different_sign']:,}")
        else:
            st.warning("No data available")
    
    st.markdown("---")
    
    # ========================================
    # SENTIMENT DISTRIBUTION
    # ========================================
    st.subheader("📊 Sentiment Distribution Comparison")
    st.caption("Distribution of negative/neutral/positive sentiments in real vs generated commentary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔄 Overlap Matches**")
        if overlap_sentiment_dist:
            categories = ['Negative', 'Neutral', 'Positive']
            real_counts = [
                overlap_sentiment_dist['real']['negative'],
                overlap_sentiment_dist['real']['neutral'],
                overlap_sentiment_dist['real']['positive']
            ]
            gen_counts = [
                overlap_sentiment_dist['generated']['negative'],
                overlap_sentiment_dist['generated']['neutral'],
                overlap_sentiment_dist['generated']['positive']
            ]
            
            fig_overlap_sent = go.Figure()
            fig_overlap_sent.add_trace(go.Bar(
                name='Real',
                x=categories,
                y=real_counts,
                marker_color='#1f77b4',
                text=[f"{count:,}" for count in real_counts],
                textposition='auto'
            ))
            fig_overlap_sent.add_trace(go.Bar(
                name='Generated',
                x=categories,
                y=gen_counts,
                marker_color='#ff7f0e',
                text=[f"{count:,}" for count in gen_counts],
                textposition='auto'
            ))
            
            fig_overlap_sent.update_layout(
                barmode='group',
                yaxis_title='Count',
                height=300,
                showlegend=True
            )
            
            st.plotly_chart(fig_overlap_sent, use_container_width=True)
        else:
            st.warning("No data available")
    
    with col2:
        st.markdown("**🔀 Different Selection Matches**")
        if different_sentiment_dist:
            categories = ['Negative', 'Neutral', 'Positive']
            real_counts_diff = [
                different_sentiment_dist['real']['negative'],
                different_sentiment_dist['real']['neutral'],
                different_sentiment_dist['real']['positive']
            ]
            gen_counts_diff = [
                different_sentiment_dist['generated']['negative'],
                different_sentiment_dist['generated']['neutral'],
                different_sentiment_dist['generated']['positive']
            ]
            
            fig_different_sent = go.Figure()
            fig_different_sent.add_trace(go.Bar(
                name='Real',
                x=categories,
                y=real_counts_diff,
                marker_color='#1f77b4',
                text=[f"{count:,}" for count in real_counts_diff],
                textposition='auto'
            ))
            fig_different_sent.add_trace(go.Bar(
                name='Generated',
                x=categories,
                y=gen_counts_diff,
                marker_color='#ff7f0e',
                text=[f"{count:,}" for count in gen_counts_diff],
                textposition='auto'
            ))
            
            fig_different_sent.update_layout(
                barmode='group',
                yaxis_title='Count',
                height=300,
                showlegend=True
            )
            
            st.plotly_chart(fig_different_sent, use_container_width=True)
        else:
            st.warning("No data available")
    
    # ========================================
    # WORD MATCHING ANALYSIS
    # ========================================
    st.markdown('<div class="section-header">📝 Word Matching Analysis</div>', unsafe_allow_html=True)
    
    st.info("""
    **What is Word Matching?**
    
    This section analyzes how many **identical words** appear in both real and generated commentary, excluding common linking words (the, a, is, etc.).
    
    We track 4 types of matching words:
    - **Content Words**: Meaningful words like "attacks", "shoots", "saves" (excluding "the", "a", "is", etc.)
    - **Player Names**: Matching player names (e.g., "Yamal", "Williams")
    - **Team Names**: Matching team names (e.g., "Spain", "England")
    - **Event Keywords**: Matching event types (e.g., "shot", "pass", "goal", "foul")
    """)
    
    # Select scoring method for word matching
    comparison_score_type_words = st.radio(
        "Select scoring method for word matching analysis:",
        options=['average_score', 'average_score_no_sentiment'],
        format_func=lambda x: "With Sentiment" if x == 'average_score' else "Without Sentiment",
        horizontal=True,
        key='word_matching_comparison'
    )
    
    # Get word matching statistics
    with st.spinner("Calculating word matching statistics..."):
        word_stats_with = loader.get_word_matching_statistics('average_score')
        word_stats_without = loader.get_word_matching_statistics('average_score_no_sentiment')
    
    if word_stats_with and word_stats_without:
        # Choose which stats to display based on selection
        word_stats = word_stats_with if comparison_score_type_words == 'average_score' else word_stats_without
        
        # Overview metrics
        st.subheader("📊 Word Matching Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Avg Matching Content Words",
                f"{word_stats['avg_matching_content_words']:.2f}",
                help="Average number of matching content words (excluding linking words like 'the', 'a', etc.)"
            )
        
        with col2:
            st.metric(
                "Avg Matching Players",
                f"{word_stats['avg_matching_players']:.2f}",
                help="Average number of matching player names"
            )
        
        with col3:
            st.metric(
                "Avg Matching Teams",
                f"{word_stats['avg_matching_teams']:.2f}",
                help="Average number of matching team names"
            )
        
        with col4:
            st.metric(
                "Avg Matching Events",
                f"{word_stats['avg_matching_events']:.2f}",
                help="Average number of matching event keywords (shot, pass, goal, etc.)"
            )
        
        st.markdown("---")
        
        # Comparison between With/Without Sentiment
        st.subheader("⚖️ With vs Without Sentiment Comparison")
        
        st.info("""
        **Table Explanation:**
        
        This table compares word matching statistics between two scoring methods:
        
        - **With Sentiment**: Matches selected when sentiment is included in scoring
        - **Without Sentiment**: Matches selected when sentiment is excluded from scoring
        
        **Columns:**
        - **Avg Matching [Type]**: Average number of matching words of each type per commentary
        - **Entity Match Score**: Normalized score (0-1) measuring how well entities match between real and generated commentary
        
        **What to Look For:**
        - Higher numbers = better word alignment
        - Compare values to see if including sentiment affects which matches are selected
        """)
        
        comparison_data = {
            'Metric': [
                'Avg Matching Content Words',
                'Avg Matching Players',
                'Avg Matching Teams',
                'Avg Matching Events',
                'Entity Players Match Score',
                'Entity Teams Match Score',
                'Entity Events Match Score'
            ],
            'With Sentiment': [
                f"{word_stats_with['avg_matching_content_words']:.2f}",
                f"{word_stats_with['avg_matching_players']:.2f}",
                f"{word_stats_with['avg_matching_teams']:.2f}",
                f"{word_stats_with['avg_matching_events']:.2f}",
                f"{word_stats_with['avg_entity_players_match']:.3f}",
                f"{word_stats_with['avg_entity_teams_match']:.3f}",
                f"{word_stats_with['avg_entity_events_match']:.3f}"
            ],
            'Without Sentiment': [
                f"{word_stats_without['avg_matching_content_words']:.2f}",
                f"{word_stats_without['avg_matching_players']:.2f}",
                f"{word_stats_without['avg_matching_teams']:.2f}",
                f"{word_stats_without['avg_matching_events']:.2f}",
                f"{word_stats_without['avg_entity_players_match']:.3f}",
                f"{word_stats_without['avg_entity_teams_match']:.3f}",
                f"{word_stats_without['avg_entity_events_match']:.3f}"
            ]
        }
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, hide_index=True, use_container_width=True)
        
        # Visual comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Matching Words Comparison**")
            fig_words_comp = go.Figure()
            
            categories = ['Content Words', 'Players', 'Teams', 'Events']
            with_values = [
                word_stats_with['avg_matching_content_words'],
                word_stats_with['avg_matching_players'],
                word_stats_with['avg_matching_teams'],
                word_stats_with['avg_matching_events']
            ]
            without_values = [
                word_stats_without['avg_matching_content_words'],
                word_stats_without['avg_matching_players'],
                word_stats_without['avg_matching_teams'],
                word_stats_without['avg_matching_events']
            ]
            
            fig_words_comp.add_trace(go.Bar(
                name='With Sentiment',
                x=categories,
                y=with_values,
                marker_color='#1f77b4',
                text=[f'{v:.2f}' for v in with_values],
                textposition='auto'
            ))
            fig_words_comp.add_trace(go.Bar(
                name='Without Sentiment',
                x=categories,
                y=without_values,
                marker_color='#ff7f0e',
                text=[f'{v:.2f}' for v in without_values],
                textposition='auto'
            ))
            
            fig_words_comp.update_layout(
                yaxis_title='Average Count',
                barmode='group',
                height=400,
                showlegend=True
            )
            st.plotly_chart(fig_words_comp, use_container_width=True)
        
        with col2:
            st.markdown("**Entity Match Scores Comparison**")
            fig_entity_comp = go.Figure()
            
            categories_entity = ['Players', 'Teams', 'Events']
            with_entity_values = [
                word_stats_with['avg_entity_players_match'],
                word_stats_with['avg_entity_teams_match'],
                word_stats_with['avg_entity_events_match']
            ]
            without_entity_values = [
                word_stats_without['avg_entity_players_match'],
                word_stats_without['avg_entity_teams_match'],
                word_stats_without['avg_entity_events_match']
            ]
            
            fig_entity_comp.add_trace(go.Bar(
                name='With Sentiment',
                x=categories_entity,
                y=with_entity_values,
                marker_color='#1f77b4',
                text=[f'{v:.3f}' for v in with_entity_values],
                textposition='auto'
            ))
            fig_entity_comp.add_trace(go.Bar(
                name='Without Sentiment',
                x=categories_entity,
                y=without_entity_values,
                marker_color='#ff7f0e',
                text=[f'{v:.3f}' for v in without_entity_values],
                textposition='auto'
            ))
            
            fig_entity_comp.update_layout(
                yaxis_title='Match Score',
                barmode='group',
                height=400,
                showlegend=True
            )
            st.plotly_chart(fig_entity_comp, use_container_width=True)
        
        st.markdown("---")
        
        # Event Type Analysis
        st.subheader("🎯 Word Matching by Event Type")
        
        # Show which method is being used
        method_name = "With Sentiment" if comparison_score_type_words == 'average_score' else "Without Sentiment"
        st.warning(f"""
        **Currently Showing Results For: {method_name}** ⚠️
        
        The results below are based on the **{method_name}** scoring method you selected above.
        Since there are differences between the two methods, switch the radio button above to compare.
        """)
        
        st.info("""
        **Which Event Types Have the Most Matching Words?**
        
        This section shows word matching statistics for each event type (Pass, Shot, Goal, etc.).
        
        **Why This Matters:**
        - Some event types are easier to describe consistently (e.g., "Goal" → "scores", "goal")
        - Others have more varied vocabulary (e.g., "Pass" → "passes", "delivers", "finds", "plays")
        
        **Table Columns:**
        - **Count**: Number of commentaries for this event type
        - **Avg Content Words**: Average matching content words
        - **Avg Players/Teams/Events**: Average matching entities
        - **Total**: Sum of all matching words for this event type across ALL commentaries
        """)
        
        # Get event type statistics
        with st.spinner("Analyzing event types..."):
            event_type_stats = loader.get_word_matching_by_event_type(comparison_score_type_words)
        
        if event_type_stats:
            # Sort by avg matching content words
            sorted_event_types = sorted(event_type_stats.items(), 
                                       key=lambda x: x[1]['avg_matching_content_words'], 
                                       reverse=True)
            
            # Top 15 for chart
            top_15_events = sorted_event_types[:15]
            
            event_names = [e[0] for e in top_15_events]
            content_words = [e[1]['avg_matching_content_words'] for e in top_15_events]
            
            # Create bar chart
            st.markdown(f"**Top 15 Event Types by Matching Content Words ({method_name})**")
            
            fig_event_words = go.Figure()
            fig_event_words.add_trace(go.Bar(
                x=content_words,
                y=event_names,
                orientation='h',
                marker_color='#2ca02c',
                text=[f'{v:.2f}' for v in content_words],
                textposition='auto'
            ))
            fig_event_words.update_layout(
                xaxis_title='Avg Matching Content Words',
                yaxis_title='Event Type',
                height=500,
                showlegend=False,
                title=f'Based on {method_name} Scoring'
            )
            st.plotly_chart(fig_event_words, use_container_width=True)
            
            # Detailed table for all event types
            st.markdown(f"**Detailed Event Type Statistics ({method_name})**")
            
            event_table_data = []
            for event_type, stats in sorted_event_types:
                event_table_data.append({
                    'Event Type': event_type,
                    'Count': f"{stats['count']:,}",
                    'Avg Content Words': f"{stats['avg_matching_content_words']:.2f}",
                    'Avg Players': f"{stats['avg_matching_players']:.2f}",
                    'Avg Teams': f"{stats['avg_matching_teams']:.2f}",
                    'Avg Events': f"{stats['avg_matching_events']:.2f}",
                    'Total Content Words': f"{stats['total_matching_content_words']:,.0f}",
                    'Total Players': f"{stats['total_matching_players']:,.0f}",
                    'Total Teams': f"{stats['total_matching_teams']:,.0f}",
                    'Total Events': f"{stats['total_matching_events']:,.0f}"
                })
            
            event_table_df = pd.DataFrame(event_table_data)
            st.dataframe(event_table_df, hide_index=True, use_container_width=True)
            
            st.success("""
            **Example Interpretation:**
            
            If "Goal" shows:
            - **Avg Content Words: 4.5** → On average, goals have 4.5 matching content words
            - **Total Content Words: 450** → Across all 100 goal commentaries, there are 450 matching content words total
            - **Avg Players: 2.0** → On average, 2 player names match (e.g., scorer and assist provider)
            
            Higher "Avg" values mean better word-for-word alignment for that event type!
            """)
        else:
            st.warning("No event type data available")
        
        st.markdown("---")
        
        # Distribution Analysis
        st.subheader("📈 Word Matching Distribution")
        
        # Show which method is being used
        st.warning(f"""
        **Currently Showing Results For: {method_name}** ⚠️
        
        The distributions below are based on the **{method_name}** scoring method.
        """)
        
        st.info("""
        **Distribution of Matching Words**
        
        These histograms show how matching words are distributed across all commentaries.
        
        **What to Look For:**
        - **Mode** (peak): The most common number of matching words
        - **Spread**: How varied the matching is
        - **Outliers**: Commentaries with unusually high/low matching
        
        **Example:**
        If the "Content Words" histogram peaks at 3-4, it means most commentaries have 3-4 matching content words.
        """)
        
        # Get distribution data
        with st.spinner("Loading distribution data..."):
            dist_data = loader.get_word_matching_distribution(comparison_score_type_words)
        
        if dist_data:
            # Create histograms
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Content Words Distribution ({method_name})**")
                fig_dist_content = go.Figure()
                fig_dist_content.add_trace(go.Histogram(
                    x=dist_data['matching_content_words'],
                    marker_color='#1f77b4',
                    nbinsx=30
                ))
                fig_dist_content.update_layout(
                    xaxis_title='Matching Content Words',
                    yaxis_title='Frequency',
                    height=300,
                    showlegend=False
                )
                st.plotly_chart(fig_dist_content, use_container_width=True)
                
                st.markdown(f"**Teams Distribution ({method_name})**")
                fig_dist_teams = go.Figure()
                fig_dist_teams.add_trace(go.Histogram(
                    x=dist_data['matching_teams'],
                    marker_color='#d62728',
                    nbinsx=10
                ))
                fig_dist_teams.update_layout(
                    xaxis_title='Matching Teams',
                    yaxis_title='Frequency',
                    height=300,
                    showlegend=False
                )
                st.plotly_chart(fig_dist_teams, use_container_width=True)
            
            with col2:
                st.markdown(f"**Players Distribution ({method_name})**")
                fig_dist_players = go.Figure()
                fig_dist_players.add_trace(go.Histogram(
                    x=dist_data['matching_players'],
                    marker_color='#2ca02c',
                    nbinsx=15
                ))
                fig_dist_players.update_layout(
                    xaxis_title='Matching Players',
                    yaxis_title='Frequency',
                    height=300,
                    showlegend=False
                )
                st.plotly_chart(fig_dist_players, use_container_width=True)
                
                st.markdown(f"**Events Distribution ({method_name})**")
                fig_dist_events = go.Figure()
                fig_dist_events.add_trace(go.Histogram(
                    x=dist_data['matching_events'],
                    marker_color='#ff7f0e',
                    nbinsx=10
                ))
                fig_dist_events.update_layout(
                    xaxis_title='Matching Events',
                    yaxis_title='Frequency',
                    height=300,
                    showlegend=False
                )
                st.plotly_chart(fig_dist_events, use_container_width=True)
        else:
            st.warning("No distribution data available")
        
        st.markdown("---")
        
        # Event Type Keyword Presence Analysis
        st.subheader("🔍 Event Type Keyword Presence in Commentary")
        
        # Show which method is being used
        st.warning(f"""
        **Currently Showing Results For: {method_name}** ⚠️
        
        Analysis is based on the **{method_name}** scoring method.
        """)
        
        st.info("""
        **Does the Event Type Keyword Appear in the Commentary Text?**
        
        This analysis checks if the actual event type keyword (e.g., "goal", "shot", "pass") appears in the commentary text.
        
        **For Example:**
        - Event Type: **Goal** → Check if "goal", "goals", "scores", or "scored" appear in commentary
        - Event Type: **Pass** → Check if "pass", "passes", or "passed" appear in commentary
        
        **Categories:**
        - **In Real Only**: Keyword appears only in real commentary
        - **In Generated Only**: Keyword appears only in generated commentary
        - **In Both**: Keyword appears in both commentaries ✅
        - **In Neither**: Keyword doesn't appear in either commentary
        
        **Why This Matters:**
        - Shows if we're using the same vocabulary as real commentators
        - Identifies events where we use different terminology
        - "In Both" is ideal - means we're describing events with the same words
        
        **Note:** Chart shows **top 15 events** sorted by "In Both" percentage. Full table with all events shown below.
        """)
        
        # Get event type keyword presence data
        with st.spinner("Analyzing event type keyword presence..."):
            keyword_presence = loader.get_event_type_keyword_presence(comparison_score_type_words)
        
        if keyword_presence:
            # Sort by "in_both" percentage (descending) and filter out "General"
            sorted_events = sorted(
                [(k, v) for k, v in keyword_presence.items() if k != 'General'],
                key=lambda x: x[1]['pct_in_both'], 
                reverse=True
            )
            
            # Take only top 15 for chart
            top_15_events = sorted_events[:15]
            
            # Prepare data for visualization (top 15 only, vertical bars)
            event_names = [e[0] for e in top_15_events]
            in_real_only = [e[1]['in_real_only'] for e in top_15_events]
            in_generated_only = [e[1]['in_generated_only'] for e in top_15_events]
            in_both = [e[1]['in_both'] for e in top_15_events]
            in_neither = [e[1]['in_neither'] for e in top_15_events]
            
            # Stacked bar chart (vertical - events on x-axis)
            st.markdown(f"**Top 15 Event Types by 'In Both' Percentage ({method_name})**")
            
            fig_keyword = go.Figure()
            
            fig_keyword.add_trace(go.Bar(
                name='In Both ✅',
                x=event_names,
                y=in_both,
                marker_color='#2ca02c',
                text=in_both,
                textposition='inside'
            ))
            
            fig_keyword.add_trace(go.Bar(
                name='In Real Only',
                x=event_names,
                y=in_real_only,
                marker_color='#1f77b4',
                text=in_real_only,
                textposition='inside'
            ))
            
            fig_keyword.add_trace(go.Bar(
                name='In Generated Only',
                x=event_names,
                y=in_generated_only,
                marker_color='#ff7f0e',
                text=in_generated_only,
                textposition='inside'
            ))
            
            fig_keyword.add_trace(go.Bar(
                name='In Neither',
                x=event_names,
                y=in_neither,
                marker_color='#d62728',
                text=in_neither,
                textposition='inside'
            ))
            
            fig_keyword.update_layout(
                barmode='stack',
                xaxis_title='Event Type',
                yaxis_title='Count',
                height=600,  # Taller for vertical bars
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis_tickangle=-45  # Angle event names for readability
            )
            st.plotly_chart(fig_keyword, use_container_width=True)
            
            # Detailed table (all events)
            st.markdown(f"**Detailed Event Type Keyword Presence Statistics - All Events ({method_name})**")
            
            table_data = []
            for event_type, stats in sorted_events:
                table_data.append({
                    'Event Type': event_type,
                    'Total': f"{stats['total']:,}",
                    'In Both': f"{stats['in_both']:,} ({stats['pct_in_both']:.1f}%)",
                    'In Real Only': f"{stats['in_real_only']:,} ({stats['pct_in_real_only']:.1f}%)",
                    'In Generated Only': f"{stats['in_generated_only']:,} ({stats['pct_in_generated_only']:.1f}%)",
                    'In Neither': f"{stats['in_neither']:,} ({stats['pct_in_neither']:.1f}%)"
                })
            
            keyword_table_df = pd.DataFrame(table_data)
            st.dataframe(keyword_table_df, hide_index=True, use_container_width=True)
            
            st.success("""
            **How to Read the Results:**
            
            **Chart:** Shows the **top 15 event types** with highest "In Both" percentages - these are the events where we best match real commentary vocabulary!
            
            **Example Interpretation:**
            If "Goal" shows:
            - **In Both: 85 (85%)** → 85% of goal commentaries include the word "goal" in BOTH real and generated ✅
            - **In Real Only: 10 (10%)** → 10% have "goal" only in real commentary (we used different words)
            - **In Generated Only: 3 (3%)** → 3% have "goal" only in generated commentary (real used different words)
            - **In Neither: 2 (2%)** → 2% don't mention "goal" at all in either commentary
            
            **Goal:** Maximize "In Both" percentage - means we're using the same terminology as real commentators!
            
            **Table:** Shows complete statistics for **all event types** for detailed analysis.
            """)
        else:
            st.warning("No event type keyword presence data available")
    else:
        st.warning("No word matching data available")
    
    # ========================================
    # GENERAL EVENTS ANALYSIS
    # ========================================
    st.markdown("---")
    st.markdown('<div class="section-header">🔍 "General" Events Deep Dive Analysis</div>', unsafe_allow_html=True)
    
    # Show which method is being used
    method_name = "With Sentiment" if comparison_score_type_words == 'average_score' else "Without Sentiment"
    st.warning(f"""
    **Currently Showing Results For: {method_name}** ⚠️
    
    Analysis is based on the **{method_name}** scoring method.
    """)
    
    st.info("""
    **Understanding "General" Events:**
    
    - **Real Commentary** = General/vague descriptions (e.g., "Spain building from the back")
    - **Generated Commentary** = Specific event descriptions (e.g., "Rodri passes to Pedri, Pedri carries forward")
    
    **The Challenge**: Real commentators use general language during build-up play, but our commentary is built from specific events!
    
    **This analysis shows:**
    1. Which event types we reveal in generated commentary
    2. How much more specific we are compared to real commentary
    3. Vocabulary differences when event types are excluded
    """)
    
    # Get general events analysis
    with st.spinner("Analyzing General events..."):
        general_analysis = loader.get_general_events_analysis(comparison_score_type_words)
    
    if general_analysis and general_analysis.get('total_general_events', 0) > 0:
        st.success(f"**Analyzing {general_analysis['total_general_events']:,} General events**")
        
        # ========================================
        # 1. EVENT TYPE DETECTION
        # ========================================
        st.subheader("1️⃣ Event Type Detection in Commentary")
        
        st.markdown("""
        **Do event type keywords appear in "General" commentary?**
        
        Compare which specific event types (Pass, Shot, Carry, etc.) are mentioned in:
        - **Real Commentary**: Supposedly "general" - but do they mention event types?
        - **Generated Commentary**: Built from events - which types do we reveal?
        """)
        
        event_detection_gen = general_analysis.get('event_type_detection_generated', {})
        event_detection_real = general_analysis.get('event_type_detection_real', {})
        
        if event_detection_gen and event_detection_real:
            # Create side-by-side comparison
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📝 Real Commentary** (Classified as 'General')")
                
                # Sort by percentage descending
                sorted_real = sorted(event_detection_real.items(), key=lambda x: x[1]['percentage'], reverse=True)
                
                real_names = [e[0] for e in sorted_real]
                real_counts = [e[1]['count'] for e in sorted_real]
                real_pcts = [e[1]['percentage'] for e in sorted_real]
                
                # Bar chart
                fig_real = go.Figure()
                fig_real.add_trace(go.Bar(
                    x=real_names,
                    y=real_counts,
                    marker_color='#1f77b4',
                    text=[f"{c}<br>({p:.1f}%)" for c, p in zip(real_counts, real_pcts)],
                    textposition='outside'
                ))
                fig_real.update_layout(
                    xaxis_title='Event Type',
                    yaxis_title='Count',
                    height=500,
                    xaxis_tickangle=-45,
                    showlegend=False
                )
                st.plotly_chart(fig_real, use_container_width=True)
                
                # Top 3 for real
                if len(sorted_real) >= 3:
                    top_3_real = sorted_real[:3]
                    st.markdown(f"""
                    **Real Top 3:**
                    1. {top_3_real[0][0]}: {top_3_real[0][1]['percentage']:.1f}%
                    2. {top_3_real[1][0]}: {top_3_real[1][1]['percentage']:.1f}%
                    3. {top_3_real[2][0]}: {top_3_real[2][1]['percentage']:.1f}%
                    """)
            
            with col2:
                st.markdown("**🤖 Generated Commentary** (From Event Data)")
                
                # Sort by percentage descending
                sorted_gen = sorted(event_detection_gen.items(), key=lambda x: x[1]['percentage'], reverse=True)
                
                gen_names = [e[0] for e in sorted_gen]
                gen_counts = [e[1]['count'] for e in sorted_gen]
                gen_pcts = [e[1]['percentage'] for e in sorted_gen]
                
                # Bar chart
                fig_gen = go.Figure()
                fig_gen.add_trace(go.Bar(
                    x=gen_names,
                    y=gen_counts,
                    marker_color='#ff7f0e',
                    text=[f"{c}<br>({p:.1f}%)" for c, p in zip(gen_counts, gen_pcts)],
                    textposition='outside'
                ))
                fig_gen.update_layout(
                    xaxis_title='Event Type',
                    yaxis_title='Count',
                    height=500,
                    xaxis_tickangle=-45,
                    showlegend=False
                )
                st.plotly_chart(fig_gen, use_container_width=True)
                
                # Top 3 for generated
                if len(sorted_gen) >= 3:
                    top_3_gen = sorted_gen[:3]
                    st.markdown(f"""
                    **Generated Top 3:**
                    1. {top_3_gen[0][0]}: {top_3_gen[0][1]['percentage']:.1f}%
                    2. {top_3_gen[1][0]}: {top_3_gen[1][1]['percentage']:.1f}%
                    3. {top_3_gen[2][0]}: {top_3_gen[2][1]['percentage']:.1f}%
                    """)
            
            # Comparison analysis
            st.markdown("---")
            st.markdown("**🔍 Comparison Analysis:**")
            
            # Calculate differences
            comparison_data = []
            for event_type in event_detection_gen.keys():
                gen_pct = event_detection_gen[event_type]['percentage']
                real_pct = event_detection_real.get(event_type, {}).get('percentage', 0)
                diff = gen_pct - real_pct
                
                comparison_data.append({
                    'Event Type': event_type,
                    'Real %': f"{real_pct:.1f}%",
                    'Generated %': f"{gen_pct:.1f}%",
                    'Difference': f"+{diff:.1f}%" if diff > 0 else f"{diff:.1f}%"
                })
            
            # Sort by difference (descending)
            comparison_data.sort(key=lambda x: float(x['Difference'].replace('%', '').replace('+', '')), reverse=True)
            
            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, hide_index=True, use_container_width=True)
            
            # Key insights
            biggest_diff = comparison_data[0]
            st.success(f"""
            **Key Insights:**
            - **Biggest difference**: {biggest_diff['Event Type']} (Real: {biggest_diff['Real %']}, Generated: {biggest_diff['Generated %']}, Diff: {biggest_diff['Difference']})
            - Real commentary DOES sometimes mention event types even when classified as "General"!
            - However, we mention them significantly more often
            - This confirms our commentary is more event-specific than real commentary
            """)
        
        st.markdown("---")
        
        # ========================================
        # 2. SPECIFICITY ANALYSIS
        # ========================================
        st.subheader("2️⃣ Specificity Level Comparison")
        
        st.markdown("""
        **How much more specific are we compared to real commentary?**
        
        We analyze the percentage of:
        - **Specific action words** (pass, shot, carry, etc.) vs.
        - **Vague/general words** (building, play, possession, etc.)
        """)
        
        spec_analysis = general_analysis.get('specificity_analysis', {})
        if spec_analysis:
            real_spec = spec_analysis['real']['specific_percentage']
            gen_spec = spec_analysis['generated']['specific_percentage']
            real_vague = spec_analysis['real']['vague_percentage']
            gen_vague = spec_analysis['generated']['vague_percentage']
            
            # Side-by-side comparison
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "Real Commentary - Specific Words",
                    f"{real_spec:.1f}%",
                    delta=None
                )
                st.metric(
                    "Real Commentary - Vague Words",
                    f"{real_vague:.1f}%",
                    delta=None
                )
            
            with col2:
                st.metric(
                    "Generated Commentary - Specific Words",
                    f"{gen_spec:.1f}%",
                    delta=f"+{(gen_spec - real_spec):.1f}% vs Real",
                    delta_color="inverse"  # Red for higher specificity
                )
                st.metric(
                    "Generated Commentary - Vague Words",
                    f"{gen_vague:.1f}%",
                    delta=f"{(gen_vague - real_vague):+.1f}% vs Real",
                    delta_color="normal"  # Green for more vague
                )
            
            # Bar chart comparison
            fig_spec = go.Figure()
            fig_spec.add_trace(go.Bar(
                name='Specific Words',
                x=['Real Commentary', 'Generated Commentary'],
                y=[real_spec, gen_spec],
                marker_color='#d62728',
                text=[f"{real_spec:.1f}%", f"{gen_spec:.1f}%"],
                textposition='outside'
            ))
            fig_spec.add_trace(go.Bar(
                name='Vague Words',
                x=['Real Commentary', 'Generated Commentary'],
                y=[real_vague, gen_vague],
                marker_color='#2ca02c',
                text=[f"{real_vague:.1f}%", f"{gen_vague:.1f}%"],
                textposition='outside'
            ))
            fig_spec.update_layout(
                barmode='group',
                yaxis_title='Percentage of Words',
                height=400,
                title=f'Specificity Comparison ({method_name})'
            )
            st.plotly_chart(fig_spec, use_container_width=True)
            
            # Interpretation
            spec_diff = gen_spec - real_spec
            if spec_diff > 10:
                color = "🔴"
                message = "significantly more specific"
            elif spec_diff > 5:
                color = "🟠"
                message = "moderately more specific"
            else:
                color = "🟢"
                message = "similarly specific"
            
            st.markdown(f"""
            **Interpretation**: {color}
            
            Our generated commentary is **{message}** than real commentary:
            - We use specific action words **{spec_diff:+.1f}%** more than real commentary
            - Real uses vague/general words **{(real_vague - gen_vague):+.1f}%** more than us
            
            **Recommendation**: {'Consider using more general descriptions during build-up play!' if spec_diff > 10 else 'Good balance between specific and general language!'}
            """)
        
        st.markdown("---")
        
        # ========================================
        # 3. TOP WORDS ANALYSIS
        # ========================================
        st.subheader("3️⃣ Vocabulary Comparison (Top Words)")
        
        st.markdown("""
        **What words do we use vs. real commentary?**
        
        Compare top 15 words in two ways:
        1. **All words** - Including event type keywords
        2. **Excluding event types** - Focus on descriptive vocabulary only
        """)
        
        top_words = general_analysis.get('top_words_analysis', {})
        if top_words:
            # Toggle between all words and no event words
            word_filter = st.radio(
                "Select word filter:",
                ["All Words", "Excluding Event Type Words"],
                horizontal=True,
                key="general_word_filter"
            )
            
            if word_filter == "All Words":
                real_words = top_words.get('real_all', [])[:15]
                gen_words = top_words.get('generated_all', [])[:15]
                title_suffix = "(All Words)"
            else:
                real_words = top_words.get('real_no_event', [])[:15]
                gen_words = top_words.get('generated_no_event', [])[:15]
                title_suffix = "(Excluding Event Types)"
            
            # Side-by-side bar charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Real Commentary Top 15 {title_suffix}**")
                if real_words:
                    fig_real = go.Figure()
                    fig_real.add_trace(go.Bar(
                        y=[w['word'] for w in real_words][::-1],
                        x=[w['count'] for w in real_words][::-1],
                        orientation='h',
                        marker_color='#1f77b4',
                        text=[w['count'] for w in real_words][::-1],
                        textposition='outside'
                    ))
                    fig_real.update_layout(
                        xaxis_title='Count',
                        yaxis_title='Word',
                        height=500,
                        showlegend=False
                    )
                    st.plotly_chart(fig_real, use_container_width=True)
            
            with col2:
                st.markdown(f"**Generated Commentary Top 15 {title_suffix}**")
                if gen_words:
                    fig_gen = go.Figure()
                    fig_gen.add_trace(go.Bar(
                        y=[w['word'] for w in gen_words][::-1],
                        x=[w['count'] for w in gen_words][::-1],
                        orientation='h',
                        marker_color='#ff7f0e',
                        text=[w['count'] for w in gen_words][::-1],
                        textposition='outside'
                    ))
                    fig_gen.update_layout(
                        xaxis_title='Count',
                        yaxis_title='Word',
                        height=500,
                        showlegend=False
                    )
                    st.plotly_chart(fig_gen, use_container_width=True)
            
            # Word overlap analysis
            if real_words and gen_words:
                real_word_set = {w['word'] for w in real_words}
                gen_word_set = {w['word'] for w in gen_words}
                
                overlap = real_word_set & gen_word_set
                real_only = real_word_set - gen_word_set
                gen_only = gen_word_set - real_word_set
                
                st.markdown(f"""
                **Vocabulary Overlap**:
                - **Shared words** (in both): {len(overlap)} words → {', '.join(sorted(overlap)[:10])}{'...' if len(overlap) > 10 else ''}
                - **Only in Real**: {len(real_only)} words → {', '.join(sorted(real_only)[:10])}{'...' if len(real_only) > 10 else ''}
                - **Only in Generated**: {len(gen_only)} words → {', '.join(sorted(gen_only)[:10])}{'...' if len(gen_only) > 10 else ''}
                
                **Insight**: {f'Good overlap ({len(overlap)}/{len(real_word_set)} = {len(overlap)/len(real_word_set)*100:.0f}%)!' if len(overlap)/len(real_word_set) > 0.3 else f'Low overlap ({len(overlap)}/{len(real_word_set)} = {len(overlap)/len(real_word_set)*100:.0f}%) - consider using more words from real commentary!'}
                """)
    else:
        st.warning("No General events data available for analysis")
    
    # ========================================
    # SECTION: TOP 10 EVENT TYPES EXAMPLES
    # ========================================
    st.markdown('<div class="section-header">📝 Top 10 Event Types - Commentary Examples by BERT Groups</div>', unsafe_allow_html=True)
    
    st.info(
        "**Purpose**: Compare real vs. generated commentary for the top 10 event types. "
        "Use the selectors below to choose an event type and BERT similarity range, "
        "then view up to 5 random examples with detailed metrics."
    )
    
    st.caption("ℹ️ **Selection Method**: Examples are selected based on **Average Score (With Sentiment)** - the best match per minute uses this combined score.")
    
    # Get top 10 event examples
    with st.spinner("Loading top 10 event examples..."):
        top_10_examples = loader.get_top_10_event_examples('average_score')
    
    if top_10_examples:
        # Create selectors
        col1, col2 = st.columns(2)
        
        with col1:
            # Event type selector
            event_types = list(top_10_examples.keys())
            selected_event_type = st.selectbox(
                "Select Event Type",
                event_types,
                format_func=lambda x: f"{x} ({top_10_examples[x]['total_count']} total)",
                key="event_type_selector"
            )
        
        with col2:
            # BERT range selector
            bert_ranges = ['Low (<0.45)', 'Medium (0.45-0.55)', 'High (>0.55)']
            selected_bert_range = st.selectbox(
                "Select BERT Similarity Range",
                bert_ranges,
                key="bert_range_selector"
            )
        
        # Get data for selected combination
        if selected_event_type and selected_bert_range:
            event_data = top_10_examples[selected_event_type]
            range_data = event_data['examples'][selected_bert_range]
            
            st.markdown(f"### {selected_event_type} - {selected_bert_range}")
            st.markdown(f"**{range_data['count_in_range']} examples** available in this BERT range")
            st.markdown("---")
            
            if range_data['samples']:
                for idx, sample in enumerate(range_data['samples'], 1):
                    st.markdown(f"#### Example {idx}")
                    
                    # Display metrics in rows
                    # Row 1: Similarity Scores (BERT, TF-IDF, Content Overlap, NER)
                    st.markdown("**Similarity Scores**")
                    sim_col1, sim_col2, sim_col3, sim_col4 = st.columns(4)
                    with sim_col1:
                        st.metric("BERT", f"{sample['bert_score']:.3f}")
                    with sim_col2:
                        st.metric("TF-IDF", f"{sample.get('tfidf', 0):.3f}")
                    with sim_col3:
                        st.metric("Content Overlap", f"{sample.get('content_overlap', 0):.3f}")
                    with sim_col4:
                        st.metric("NER", f"{sample.get('ner_score', 0):.3f}")
                    
                    # Row 2: Sentiment Scores
                    st.markdown("**Sentiment Analysis**")
                    sent_col1, sent_col2, sent_col3 = st.columns(3)
                    with sent_col1:
                        real_sent_label = "Positive" if sample['real_sentiment'] > 0.2 else ("Negative" if sample['real_sentiment'] < -0.2 else "Neutral")
                        st.metric("Real Sentiment", f"{sample['real_sentiment']:.3f}", delta=real_sent_label, delta_color="off")
                    with sent_col2:
                        gen_sent_label = "Positive" if sample['generated_sentiment'] > 0.2 else ("Negative" if sample['generated_sentiment'] < -0.2 else "Neutral")
                        st.metric("Generated Sentiment", f"{sample['generated_sentiment']:.3f}", delta=gen_sent_label, delta_color="off")
                    with sent_col3:
                        agreement = "✅ Match" if abs(sample['sentiment_diff']) < 0.3 else "⚠️ Mismatch"
                        st.metric("Sentiment Difference", f"{sample['sentiment_diff']:.3f}", delta=agreement, delta_color="off")
                    
                    # Row 3: Event & Match Info
                    st.markdown("**Event Information**")
                    info_col1, info_col2, info_col3, info_col4 = st.columns(4)
                    with info_col1:
                        st.metric("Real Event Type", sample['real_event_type'])
                    with info_col2:
                        st.metric("Generated Event Type", sample['generated_event_type'])
                    with info_col3:
                        st.metric("Minute", sample['minute'])
                    with info_col4:
                        st.metric("Source", sample['source'])
                    
                    st.markdown("")  # Spacing
                    
                    # Bold matching words
                    formatted_real, formatted_gen = loader.bold_matching_words(
                        sample['real_commentary'],
                        sample['generated_commentary']
                    )
                    
                    # Display commentaries side by side with matching words bolded
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**🎙️ Real Commentary**")
                        st.markdown(
                            f'<div style="border: 1px solid #ddd; padding: 10px; border-radius: 5px; '
                            f'background-color: #f9f9f9; min-height: 200px; max-height: 300px; '
                            f'overflow-y: auto; font-size: 14px; line-height: 1.6;">{formatted_real}</div>',
                            unsafe_allow_html=True
                        )
                    
                    with col2:
                        st.markdown("**🤖 Generated Commentary**")
                        st.markdown(
                            f'<div style="border: 1px solid #ddd; padding: 10px; border-radius: 5px; '
                            f'background-color: #f9f9f9; min-height: 200px; max-height: 300px; '
                            f'overflow-y: auto; font-size: 14px; line-height: 1.6;">{formatted_gen}</div>',
                            unsafe_allow_html=True
                        )
                    
                    if idx < len(range_data['samples']):
                        st.markdown("---")
            else:
                st.warning(f"No examples available in the {selected_bert_range} BERT range for {selected_event_type}")
    else:
        st.warning("Unable to load event examples")
    
    # ========================================
    # FOOTER
    # ========================================
    st.markdown("---")
    st.markdown(
        "*Dashboard created for Euro 2024 NLP Commentator Project - "
        f"Analyzing {general_info['total_csv_files']} comparison files*"
    )


if __name__ == "__main__":
    main()

