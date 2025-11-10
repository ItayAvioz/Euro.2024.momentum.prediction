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
    
    # Prepare data for grouped bar chart (metrics on X-axis)
    metrics = ['TF-IDF', 'Embeddings BERT', 'Content Overlap', 'Sentiment Diff', 'Avg Score\n(With Sentiment)', 'Avg Score\n(Without Sentiment)']
    with_sentiment_values = [
        stats_with_sentiment['TF-IDF'],
        stats_with_sentiment['Embeddings_BERT'],
        stats_with_sentiment['content_overlap_ratio'],
        stats_with_sentiment['sentiment_diff'],
        stats_with_sentiment['avg_score'],
        stats_with_sentiment['average_score_no_sentiment']
    ]
    without_sentiment_values = [
        stats_without_sentiment['TF-IDF'],
        stats_without_sentiment['Embeddings_BERT'],
        stats_without_sentiment['content_overlap_ratio'],
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
                
                metrics = ['TF-IDF', 'Embeddings BERT', 'Content Overlap', 'Sentiment Diff', 
                          'Avg Score\n(With Sentiment)', 'Avg Score\n(Without Sentiment)']
                with_sentiment_values = [
                    stats_with['TF-IDF'],
                    stats_with['Embeddings_BERT'],
                    stats_with['content_overlap_ratio'],
                    stats_with['sentiment_diff'],
                    stats_with['avg_score'],
                    stats_with['average_score_no_sentiment']
                ]
                without_sentiment_values = [
                    stats_without['TF-IDF'],
                    stats_without['Embeddings_BERT'],
                    stats_without['content_overlap_ratio'],
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
            
            # Create 2x3 grid of charts
            metrics_to_plot = [
                ('TF-IDF', 'TF-IDF'),
                ('Embeddings_BERT', 'Embeddings BERT'),
                ('content_overlap_ratio', 'Content Overlap'),
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
                    'Sentiment Diff': f"{stats['sentiment_diff']:.4f}",
                    'Avg Score (With)': f"{stats['avg_score']:.4f}",
                    'Avg Score (Without)': f"{stats['average_score_no_sentiment']:.4f}"
                })
            
            summary_table_df = pd.DataFrame(summary_data)
            st.dataframe(summary_table_df, hide_index=True, use_container_width=True)
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
                    'Sentiment Diff': f"{stats['sentiment_diff']:.4f}",
                    'Avg Score (With)': f"{stats['avg_score']:.4f}",
                    'Avg Score (Without)': f"{stats['average_score_no_sentiment']:.4f}"
                })
            
            summary_table_df = pd.DataFrame(summary_data)
            st.dataframe(summary_table_df, hide_index=True, use_container_width=True)
    else:
        st.warning("No data source information available")
    
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

