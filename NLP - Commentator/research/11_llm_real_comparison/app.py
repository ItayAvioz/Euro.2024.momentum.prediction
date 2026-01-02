"""
LLM vs Real Commentary Comparison Dashboard

Interactive Streamlit dashboard for analyzing LLM-generated vs real commentary.
Matching the structure and calculations from 09_dashboard_analysis.

Author: AI Assistant
Date: December 11, 2025
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
    page_title="LLM vs Real Commentary Analysis",
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
    .commentary-box {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #1f77b4;
    }
    .real-box {
        border-left-color: #28a745;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main dashboard application."""
    
    # Title
    st.title("⚽ LLM vs Real Commentary Analysis Dashboard")
    st.markdown("*Analyzing GPT-4o-mini Generated vs Real Football Commentary*")
    st.markdown("---")
    
    # Initialize data loader
    loader = CommentaryDataLoader()
    
    # Sidebar
    st.sidebar.title("📊 Dashboard Info")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info(
        "This dashboard analyzes the comparison between LLM-generated commentary (V3) "
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
        fig = px.bar(games_per_source_df, x='Data Source', y='Number of Games',
                     color='Number of Games', color_continuous_scale='Blues')
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True, key="games_per_source")
    
    # ========================================
    # SECTION 2: GENERAL STATISTICS
    # ========================================
    st.markdown('<div class="section-header">📊 Overall Statistics</div>', unsafe_allow_html=True)
    
    st.info(
        "**Best Match Selection:** For each real commentary entry, the LLM commentary with the "
        "highest score is selected. Statistics below show comparison between two scoring methods."
    )
    
    # Get statistics
    with st.spinner("Calculating statistics..."):
        stats_with_sentiment = loader.get_summary_statistics('average_score')
        overlap_pct = loader.get_overlap_percentage()
    
    if not stats_with_sentiment:
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
            help="Total number of comparison CSVs"
        )
    
    with col3:
        st.metric(
            "Unique Games",
            f"{stats_with_sentiment['unique_games']}",
            help="Number of unique matches (some games have multiple sources)"
        )
    
    with col4:
        st.metric(
            "Avg Commentary per File",
            f"{stats_with_sentiment['commentary_avg_per_game']:.1f}",
            help="Average number of commentaries per comparison file"
        )
    
    st.markdown("---")
    
    # Word count row
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Avg Real Commentary Words",
            f"{stats_with_sentiment.get('real_word_count_avg', 0):.1f}",
            help="Average word count in real commentary"
        )
    
    with col2:
        st.metric(
            "Avg LLM Commentary Words",
            f"{stats_with_sentiment.get('llm_word_count_avg', 0):.1f}",
            help="Average word count in LLM commentary"
        )
    
    st.markdown("---")
    
    # Only show with/without sentiment comparison if overlap is NOT 100%
    if overlap_pct < 100:
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Selection Overlap",
                f"{overlap_pct:.1f}%",
                help="Percentage where both methods select the same best match"
            )
        
        with col2:
            st.metric(
                "Different Selections",
                f"{100 - overlap_pct:.1f}%",
                help="Percentage where methods select different best matches"
            )
    else:
        st.success("✅ 100% Selection Overlap - With/Without Sentiment methods select identical best matches")
    
    # ========================================
    # MAIN METRICS CHART
    # ========================================
    st.markdown('<div class="section-header">📊 Average Similarity Metrics</div>', unsafe_allow_html=True)
    
    # Prepare data for bar chart (including NER and sentiment diff)
    ner_score = stats_with_sentiment.get('ner_score', 0)
    has_ner = ner_score > 0
    
    if has_ner:
        metrics = ['TF-IDF', 'BERT', 'Content Overlap', 'NER', 'Sentiment Diff', 'Average Score']
        values = [
            stats_with_sentiment['tfidf'],
            stats_with_sentiment['bert'],
            stats_with_sentiment['content_overlap'],
            ner_score,
            stats_with_sentiment.get('sentiment_diff', 0),
            stats_with_sentiment['avg_score']
        ]
        colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#17becf', '#9467bd', '#d62728']
    else:
        metrics = ['TF-IDF', 'BERT', 'Content Overlap', 'Sentiment Diff', 'Average Score']
        values = [
            stats_with_sentiment['tfidf'],
            stats_with_sentiment['bert'],
            stats_with_sentiment['content_overlap'],
            stats_with_sentiment.get('sentiment_diff', 0),
            stats_with_sentiment['avg_score']
        ]
        colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#9467bd', '#d62728']
    
    # Create single bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=metrics,
        y=values,
        text=[f'{v:.4f}' for v in values],
        textposition='auto',
        marker_color=colors
    ))
    
    fig.update_layout(
        yaxis_title='Score (0-1)',
        xaxis_title='Metric',
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True, key="main_comparison_chart")
    
    # Show NER info
    if has_ner:
        st.info("ℹ️ **NER (Named Entity Recognition)** measures player/team/event matching. It is shown separately and **not included in the Average Score** because Content Overlap already captures word-level matching.")
    else:
        st.info("💡 NER score not available. Run `add_ner_metric.py` to add Named Entity Recognition scores.")
    
    # ========================================
    # ADDITIONAL ANALYSES
    # ========================================
    st.markdown('<div class="section-header">📈 Additional Analyses</div>', unsafe_allow_html=True)
    
    with st.spinner("Calculating additional analyses..."):
        bert_dist = loader.get_bert_distribution('average_score')
        sentiment_counts = loader.get_sentiment_counts('average_score')
        sentiment_agreement = loader.get_sentiment_sign_agreement('average_score')
    
    # BERT Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("BERT Similarity Distribution")
        st.caption("Distribution of BERT semantic similarity scores (0-1 scale)")
        if bert_dist:
            fig_bert = go.Figure()
            fig_bert.add_trace(go.Histogram(
                x=bert_dist,
                nbinsx=30,
                marker_color='#2ca02c'
            ))
            fig_bert.update_layout(
                xaxis_title='BERT Similarity Score',
                yaxis_title='Count',
                height=350,
                showlegend=False
            )
            st.plotly_chart(fig_bert, use_container_width=True, key="bert_hist")
    
    with col2:
        st.subheader("Sentiment Distribution")
        st.caption("Count of commentaries by sentiment category")
        if sentiment_counts:
            fig_sent = go.Figure()
            
            fig_sent.add_trace(go.Bar(
                name='Real',
                x=['Negative (<0)', 'Neutral (=0)', 'Positive (>0)'],
                y=[
                    sentiment_counts['real']['negative'],
                    sentiment_counts['real']['neutral'],
                    sentiment_counts['real']['positive']
                ],
                marker_color='#2ca02c'
            ))
            
            fig_sent.add_trace(go.Bar(
                name='LLM',
                x=['Negative (<0)', 'Neutral (=0)', 'Positive (>0)'],
                y=[
                    sentiment_counts['llm']['negative'],
                    sentiment_counts['llm']['neutral'],
                    sentiment_counts['llm']['positive']
                ],
                marker_color='#1f77b4'
            ))
            
            fig_sent.update_layout(
                barmode='group',
                yaxis_title='Count',
                height=350,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_sent, use_container_width=True, key="sent_dist")
    
    st.markdown("---")
    
    # Sentiment Sign Agreement
    st.subheader("Sentiment Sign Agreement")
    st.caption("How often real and LLM commentary have the same sentiment sign")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if sentiment_agreement:
            st.metric(
                "Same Sign Agreement",
                f"{sentiment_agreement['same_sign_pct']:.1f}%",
                help=f"{sentiment_agreement['same_sign']:,} out of {sentiment_agreement['total']:,}"
            )
    
    with col2:
        if sentiment_agreement:
            different_sign = sentiment_agreement['total'] - sentiment_agreement['same_sign']
            different_pct = 100 - sentiment_agreement['same_sign_pct']
            st.metric(
                "Different Sign",
                f"{different_pct:.1f}%",
                help=f"{different_sign:,} out of {sentiment_agreement['total']:,}"
            )
    
    with col3:
        st.markdown("**Breakdown (Same Sign)**")
        if sentiment_agreement:
            st.write(f"- Both Negative: {sentiment_agreement['both_negative']:,}")
            st.write(f"- Both Neutral: {sentiment_agreement['both_neutral']:,}")
            st.write(f"- Both Positive: {sentiment_agreement['both_positive']:,}")
    
    st.markdown("---")
    
    # ========================================
    # EVENT TYPE DISTRIBUTION
    # ========================================
    st.subheader("Event Type Distribution")
    
    event_type_counts = loader.get_llm_type_counts()
    
    if event_type_counts:
        # Sort by count descending
        sorted_events = sorted(event_type_counts.items(), key=lambda x: x[1], reverse=True)
        event_types = [e[0] for e in sorted_events]
        counts = [e[1] for e in sorted_events]
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Bar chart
            fig_event_dist = go.Figure()
            fig_event_dist.add_trace(go.Bar(
                x=event_types,
                y=counts,
                text=counts,
                textposition='outside',
                marker_color='#1f77b4'
            ))
            fig_event_dist.update_layout(
                xaxis_title='Event Type',
                yaxis_title='Count',
                height=400,
                showlegend=False,
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_event_dist, use_container_width=True, key="event_type_distribution")
        
        with col2:
            # Table
            event_df = pd.DataFrame({
                'Event Type': event_types,
                'Count': counts
            })
            st.dataframe(event_df, hide_index=True, use_container_width=True, height=400)
    
    # ========================================
    # BERT RANGE ANALYSIS
    # ========================================
    st.markdown('<div class="section-header">📊 Analysis by BERT Score Range</div>', unsafe_allow_html=True)
    
    st.info("Compare performance across different BERT similarity score ranges")
    
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
            fig_bert_range_bar = go.Figure()
            fig_bert_range_bar.add_trace(go.Bar(
                x=bert_range_df['BERT Range'],
                y=bert_range_df['Count'],
                marker_color=['#d62728', '#ff7f0e', '#2ca02c'],  # Red, Orange, Green
                text=bert_range_df['Count'],
                textposition='auto'
            ))
            fig_bert_range_bar.update_layout(
                xaxis_title='BERT Score Range',
                yaxis_title='Count',
                height=300,
                showlegend=False
            )
            st.plotly_chart(fig_bert_range_bar, use_container_width=True, key="bert_range_bar")
        
        with col2:
            st.dataframe(bert_range_df, hide_index=True, use_container_width=True)
        
        st.markdown("---")
        
        # Scoring Method Comparison Across BERT Ranges
        st.subheader("Scoring Method Comparison Across BERT Ranges")
        
        # Data source selector
        source_counts = loader.get_source_counts()
        source_options = ['All'] + list(source_counts.keys()) if source_counts else ['All']
        selected_source_bert = st.selectbox(
            "Filter by Data Source:",
            options=source_options,
            key="bert_range_source_selector"
        )
        
        # Get statistics for all BERT ranges
        with st.spinner("Calculating statistics for BERT ranges..."):
            bert_range_stats = {}
            for bert_range in bert_range_counts.keys():
                stats = loader.get_summary_statistics_by_bert_range(bert_range, 'average_score', selected_source_bert)
                if stats:
                    bert_range_stats[bert_range] = stats
        
        if bert_range_stats:
            bert_ranges_list = list(bert_range_stats.keys())
            
            # Create 2x3 grid of charts
            metrics_to_plot = [
                ('tfidf', 'TF-IDF'),
                ('bert', 'BERT'),
                ('content_overlap', 'Content Overlap'),
                ('ner_score', 'NER'),
                ('sentiment_diff', 'Sentiment Diff'),
                ('avg_score', 'Average Score')
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
                            
                            st.plotly_chart(fig, use_container_width=True, key=f"bert_range_{metric_key}")
            
            st.markdown("---")
            
            # Summary table
            st.subheader("Summary Table: BERT Ranges")
            
            summary_data = []
            for bert_range in bert_ranges_list:
                stats = bert_range_stats[bert_range]
                summary_data.append({
                    'BERT Range': bert_range,
                    'Count': f"{stats['commentary_count']:,}",
                    'TF-IDF': f"{stats['tfidf']:.4f}",
                    'BERT': f"{stats['bert']:.4f}",
                    'Content Overlap': f"{stats['content_overlap']:.4f}",
                    'NER': f"{stats.get('ner_score', 0):.4f}",
                    'Sentiment Diff': f"{stats['sentiment_diff']:.4f}",
                    'Avg Score': f"{stats['avg_score']:.4f}"
                })
            
            summary_table_df = pd.DataFrame(summary_data)
            st.dataframe(summary_table_df, hide_index=True, use_container_width=True)
            
            st.markdown("---")
            
            # Sentiment Distribution by BERT Range
            st.subheader("Sentiment Distribution by BERT Range")
            st.caption("Count of commentaries by sentiment category for each BERT range")
            
            cols = st.columns(3)
            
            for idx, bert_range in enumerate(bert_ranges_list):
                with cols[idx]:
                    st.markdown(f"**{bert_range}**")
                    
                    sent_counts = loader.get_sentiment_counts_by_bert_range(bert_range, 'average_score')
                    
                    if sent_counts:
                        fig_sent = go.Figure()
                        
                        fig_sent.add_trace(go.Bar(
                            name='Real',
                            x=['Negative', 'Neutral', 'Positive'],
                            y=[
                                sent_counts['real']['negative'],
                                sent_counts['real']['neutral'],
                                sent_counts['real']['positive']
                            ],
                            marker_color='#2ca02c'
                        ))
                        
                        fig_sent.add_trace(go.Bar(
                            name='LLM',
                            x=['Negative', 'Neutral', 'Positive'],
                            y=[
                                sent_counts['llm']['negative'],
                                sent_counts['llm']['neutral'],
                                sent_counts['llm']['positive']
                            ],
                            marker_color='#1f77b4'
                        ))
                        
                        fig_sent.update_layout(
                            barmode='group',
                            yaxis_title='Count',
                            height=300,
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
                        )
                        
                        st.plotly_chart(fig_sent, use_container_width=True, key=f"bert_range_sent_{idx}")
            
            st.markdown("---")
            
            # Sentiment Sign Agreement by BERT Range
            st.subheader("Sentiment Sign Agreement by BERT Range")
            
            cols = st.columns(3)
            
            for idx, bert_range in enumerate(bert_ranges_list):
                with cols[idx]:
                    st.markdown(f"**{bert_range}**")
                    
                    agreement = loader.get_sentiment_sign_agreement_by_bert_range(bert_range, 'average_score')
                    
                    if agreement:
                        st.metric(
                            "Same Sign",
                            f"{agreement['same_sign_pct']:.1f}%",
                            help=f"{agreement['same_sign']:,} out of {agreement['total']:,}"
                        )
                        st.metric(
                            "Different Sign",
                            f"{agreement['different_sign_pct']:.1f}%"
                        )
                        st.caption(f"Both Neg: {agreement['both_negative']:,} | Both Pos: {agreement['both_positive']:,}")
            
            st.markdown("---")
            
            # ========================================
            # TOP 15 EVENT DISTRIBUTION BY BERT RANGE
            # ========================================
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
                event_dist = loader.get_event_distribution_by_bert_range(selected_bert_range_events, 'average_score')
            
            # Bar chart
            if event_dist:
                st.markdown("### 📊 Event Distribution Chart")
                
                # Sort by count and take top 15
                sorted_events = sorted(event_dist.items(), key=lambda x: x[1]['count'], reverse=True)[:15]
                event_names = [event for event, data in sorted_events]
                event_counts = [data['count'] for event, data in sorted_events]
                
                fig_events = go.Figure()
                fig_events.add_trace(go.Bar(
                    x=event_counts,
                    y=event_names,
                    orientation='h',
                    marker_color='#1f77b4',
                    text=event_counts,
                    textposition='auto'
                ))
                
                fig_events.update_layout(
                    xaxis_title='Count',
                    yaxis_title='Event Type',
                    height=500,
                    showlegend=False,
                    yaxis={'categoryorder': 'total ascending'}
                )
                
                st.plotly_chart(fig_events, use_container_width=True, key="bert_range_event_dist_chart")
                
                st.markdown("---")
                
                # Table
                st.markdown("### 📋 Detailed Event Distribution Table")
                
                # Calculate % of group (total for ALL events in group, not just top 15)
                total_in_group = sum(data['count'] for event_type, data in event_dist.items())
                
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
                st.info("No event distribution data available")
    
    # ========================================
    # EVENT TYPE ANALYSIS
    # ========================================
    st.markdown('<div class="section-header">📊 Event Type Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        llm_type_counts = loader.get_llm_type_counts()
        if llm_type_counts:
            st.subheader("LLM Event Types")
            llm_types_df = pd.DataFrame({
                'Event Type': list(llm_type_counts.keys())[:15],
                'Count': list(llm_type_counts.values())[:15]
            })
            fig_llm = px.bar(llm_types_df, x='Count', y='Event Type', orientation='h',
                            color='Count', color_continuous_scale='Blues')
            fig_llm.update_layout(height=400, showlegend=False, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_llm, use_container_width=True, key="llm_event_types")
    
    with col2:
        avg_scores = loader.get_avg_score_by_event_type('average_score')
        if avg_scores:
            st.subheader("Avg Score by LLM Event Type")
            score_df = pd.DataFrame({
                'Event Type': list(avg_scores.keys())[:15],
                'Avg Score': list(avg_scores.values())[:15]
            })
            fig_score = px.bar(score_df, x='Avg Score', y='Event Type', orientation='h',
                              color='Avg Score', color_continuous_scale='Greens')
            fig_score.update_layout(height=400, showlegend=False, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_score, use_container_width=True, key="event_scores")
    
    # Add BERT score by event type
    bert_by_type = loader.get_avg_bert_by_event_type('average_score')
    if bert_by_type:
        st.subheader("Avg BERT Score by LLM Event Type")
        bert_df = pd.DataFrame({
            'Event Type': list(bert_by_type.keys())[:15],
            'Avg BERT': list(bert_by_type.values())[:15]
        })
        fig_bert = px.bar(bert_df, x='Avg BERT', y='Event Type', orientation='h',
                          color='Avg BERT', color_continuous_scale='Purples')
        fig_bert.update_layout(height=400, showlegend=False, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bert, use_container_width=True, key="bert_by_event_type")
    
    st.markdown("---")
    
    # ========================================
    # EVENT TYPE MATCH ANALYSIS (Real vs LLM)
    # ========================================
    st.subheader("🔄 Real vs LLM Event Type Match Analysis")
    
    st.info("""
    **Do Real and LLM event types match?**
    
    This analysis compares the event type from real commentary (e.g., "Goal", "Foul") 
    with the event type detected by our LLM system. Higher match % = better event detection.
    """)
    
    with st.spinner("Analyzing event type matches..."):
        match_analysis = loader.get_event_type_match_analysis('average_score')
        match_by_type = loader.get_event_type_match_by_type('average_score')
    
    if match_analysis:
        # Overall match statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Event Type Match",
                f"{match_analysis['match_pct']:.1f}%",
                help=f"{match_analysis['matches']:,} out of {match_analysis['total']:,}"
            )
        
        with col2:
            st.metric(
                "Non-Match",
                f"{match_analysis['non_match_pct']:.1f}%",
                help=f"{match_analysis['non_matches']:,} out of {match_analysis['total']:,}"
            )
        
        with col3:
            st.metric(
                "BERT (Matched)",
                f"{match_analysis['bert_matched']:.3f}",
                help="Average BERT score when event types match"
            )
        
        with col4:
            st.metric(
                "BERT (Non-Matched)",
                f"{match_analysis['bert_unmatched']:.3f}",
                help="Average BERT score when event types don't match"
            )
        
        # BERT comparison chart
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**BERT Score by Match Status**")
            fig_match_bert = go.Figure()
            fig_match_bert.add_trace(go.Bar(
                x=['Matched', 'Non-Matched'],
                y=[match_analysis['bert_matched'], match_analysis['bert_unmatched']],
                marker_color=['#2ca02c', '#d62728'],
                text=[f"{match_analysis['bert_matched']:.3f}", f"{match_analysis['bert_unmatched']:.3f}"],
                textposition='auto'
            ))
            fig_match_bert.update_layout(
                yaxis_title='BERT Score',
                height=300,
                showlegend=False
            )
            st.plotly_chart(fig_match_bert, use_container_width=True, key="match_bert_chart")
        
        with col2:
            st.markdown("**Match Distribution**")
            fig_match_pie = go.Figure()
            fig_match_pie.add_trace(go.Pie(
                labels=['Matched', 'Non-Matched'],
                values=[match_analysis['matches'], match_analysis['non_matches']],
                marker_colors=['#2ca02c', '#d62728'],
                textinfo='label+percent',
                hole=0.4
            ))
            fig_match_pie.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig_match_pie, use_container_width=True, key="match_pie_chart")
        
        # Match % by Event Type
        if match_by_type:
            st.markdown("---")
            st.markdown("**Match % by LLM Event Type**")
            
            # Sort by match percentage
            sorted_types = sorted(match_by_type.items(), key=lambda x: x[1]['match_pct'], reverse=True)[:15]
            
            type_names = [t[0] for t in sorted_types]
            match_pcts = [t[1]['match_pct'] for t in sorted_types]
            bert_avgs = [t[1]['bert_avg'] for t in sorted_types]
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_type_match = go.Figure()
                fig_type_match.add_trace(go.Bar(
                    x=match_pcts,
                    y=type_names,
                    orientation='h',
                    marker_color='#2ca02c',
                    text=[f'{p:.1f}%' for p in match_pcts],
                    textposition='auto'
                ))
                fig_type_match.update_layout(
                    xaxis_title='Match %',
                    yaxis_title='Event Type',
                    height=500,
                    showlegend=False,
                    yaxis={'categoryorder': 'total ascending'}
                )
                st.plotly_chart(fig_type_match, use_container_width=True, key="type_match_pct_chart")
            
            with col2:
                fig_type_bert = go.Figure()
                fig_type_bert.add_trace(go.Bar(
                    x=bert_avgs,
                    y=type_names,
                    orientation='h',
                    marker_color='#1f77b4',
                    text=[f'{b:.3f}' for b in bert_avgs],
                    textposition='auto'
                ))
                fig_type_bert.update_layout(
                    xaxis_title='Avg BERT',
                    yaxis_title='Event Type',
                    height=500,
                    showlegend=False,
                    yaxis={'categoryorder': 'total ascending'}
                )
                st.plotly_chart(fig_type_bert, use_container_width=True, key="type_bert_avg_chart")
            
            # Detailed table
            st.markdown("**Detailed Event Type Match Statistics**")
            
            table_data = []
            for event_type, stats in sorted(match_by_type.items(), key=lambda x: x[1]['match_pct'], reverse=True):
                table_data.append({
                    'Event Type': event_type,
                    'Total': stats['total'],
                    'Matches': stats['matches'],
                    'Match %': f"{stats['match_pct']:.1f}%",
                    'BERT Avg': f"{stats['bert_avg']:.3f}",
                    'BERT Matched': f"{stats['bert_matched']:.3f}" if stats['matches'] > 0 else "N/A",
                    'BERT Non-Matched': f"{stats['bert_unmatched']:.3f}" if (stats['total'] - stats['matches']) > 0 else "N/A",
                })
            
            st.dataframe(pd.DataFrame(table_data), hide_index=True, use_container_width=True)
        
        # Match % by Data Source
        st.markdown("---")
        st.markdown("**Match % by Data Source**")
        
        match_by_source = loader.get_event_type_match_by_source('average_score')
        
        if match_by_source:
            # Sort by match percentage
            sorted_sources = sorted(match_by_source.items(), key=lambda x: x[1]['match_pct'], reverse=True)
            
            source_names = [s[0] for s in sorted_sources]
            source_match_pcts = [s[1]['match_pct'] for s in sorted_sources]
            source_bert_avgs = [s[1]['bert_avg'] for s in sorted_sources]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                fig_source_match = go.Figure()
                fig_source_match.add_trace(go.Bar(
                    x=source_names,
                    y=source_match_pcts,
                    marker_color='#9467bd',
                    text=[f'{p:.1f}%' for p in source_match_pcts],
                    textposition='auto'
                ))
                fig_source_match.update_layout(
                    title='Event Type Match % by Source',
                    yaxis_title='Match %',
                    xaxis_title='Data Source',
                    height=350,
                    showlegend=False
                )
                st.plotly_chart(fig_source_match, use_container_width=True, key="source_match_pct_chart")
            
            with col2:
                # Use BERT for matched events only
                source_bert_matched = [s[1]['bert_matched'] for s in sorted_sources]
                
                fig_source_bert = go.Figure()
                fig_source_bert.add_trace(go.Bar(
                    x=source_names,
                    y=source_bert_matched,
                    marker_color='#2ca02c',
                    text=[f'{b:.3f}' for b in source_bert_matched],
                    textposition='auto'
                ))
                fig_source_bert.update_layout(
                    title='BERT Score (Matched Events Only)',
                    yaxis_title='BERT Score',
                    xaxis_title='Data Source',
                    height=350,
                    showlegend=False
                )
                st.plotly_chart(fig_source_bert, use_container_width=True, key="source_bert_matched_chart")
            
            with col3:
                # NER for matched events only
                source_ner_matched = [s[1].get('ner_matched', 0) for s in sorted_sources]
                
                fig_source_ner = go.Figure()
                fig_source_ner.add_trace(go.Bar(
                    x=source_names,
                    y=source_ner_matched,
                    marker_color='#17becf',
                    text=[f'{n:.3f}' for n in source_ner_matched],
                    textposition='auto'
                ))
                fig_source_ner.update_layout(
                    title='NER Score (Matched Events Only)',
                    yaxis_title='NER Score',
                    xaxis_title='Data Source',
                    height=350,
                    showlegend=False
                )
                st.plotly_chart(fig_source_ner, use_container_width=True, key="source_ner_matched_chart")
            
            # Source table
            source_table_data = []
            for source, stats in sorted_sources:
                source_table_data.append({
                    'Data Source': source,
                    'Total': stats['total'],
                    'Matches': stats['matches'],
                    'Match %': f"{stats['match_pct']:.1f}%",
                    'BERT Matched': f"{stats['bert_matched']:.3f}" if stats['matches'] > 0 else "N/A",
                    'BERT Non-Match': f"{stats['bert_unmatched']:.3f}" if (stats['total'] - stats['matches']) > 0 else "N/A",
                    'NER Matched': f"{stats.get('ner_matched', 0):.3f}" if stats['matches'] > 0 else "N/A",
                    'NER Non-Match': f"{stats.get('ner_unmatched', 0):.3f}" if (stats['total'] - stats['matches']) > 0 else "N/A",
                    'Avg Matched': f"{stats.get('avg_score_matched', 0):.3f}" if stats['matches'] > 0 else "N/A",
                    'Avg Non-Match': f"{stats.get('avg_score_unmatched', 0):.3f}" if (stats['total'] - stats['matches']) > 0 else "N/A",
                })
            
            st.dataframe(pd.DataFrame(source_table_data), hide_index=True, use_container_width=True)
    
    st.markdown("---")
    
    # ========================================
    # SELECT EVENT TYPE TO ANALYZE (Detailed)
    # ========================================
    llm_type_counts = loader.get_llm_type_counts()
    
    if llm_type_counts:
        selected_type = st.selectbox(
            "Select Event Type to Analyze:",
            options=list(llm_type_counts.keys()),
            help="Choose an event type to see detailed analysis"
        )
        
        if selected_type:
            st.subheader(f"Analysis for: {selected_type}")
            st.caption(f"Total occurrences: {llm_type_counts[selected_type]:,}")
            
            # Get data for this event type
            with st.spinner(f"Analyzing {selected_type}..."):
                type_stats = loader.get_summary_statistics_by_event_type(selected_type, 'average_score')
                type_bert_dist = loader.get_bert_distribution_by_event_type(selected_type, 'average_score')
                type_sentiment_counts = loader.get_sentiment_counts_by_event_type(selected_type, 'average_score')
                type_sentiment_agreement = loader.get_sentiment_sign_agreement_by_event_type(selected_type, 'average_score')
            
            if type_stats:
                # Scoring Method Comparison
                st.markdown("### Scoring Method Comparison")
                
                metrics = ['TF-IDF', 'BERT', 'Content Overlap', 'NER', 'Sentiment Diff', 'Average Score']
                values = [
                    type_stats['tfidf'],
                    type_stats['bert'],
                    type_stats['content_overlap'],
                    type_stats.get('ner_score', 0),
                    type_stats['sentiment_diff'],
                    type_stats['avg_score']
                ]
                
                fig_type_metrics = go.Figure()
                
                fig_type_metrics.add_trace(go.Bar(
                    x=metrics,
                    y=values,
                    text=[f'{v:.4f}' for v in values],
                    textposition='auto',
                    marker_color=['#1f77b4', '#2ca02c', '#ff7f0e', '#17becf', '#9467bd', '#d62728']
                ))
                
                fig_type_metrics.update_layout(
                    yaxis_title='Score (0-1)',
                    xaxis_title='Metric',
                    height=400,
                    showlegend=False,
                    xaxis=dict(tickangle=0)
                )
                
                st.plotly_chart(fig_type_metrics, use_container_width=True, key="type_metrics_chart")
                
                st.markdown("---")
                
                # BERT Distribution for this type
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### BERT Distribution")
                    if type_bert_dist:
                        fig_bert_type = go.Figure()
                        fig_bert_type.add_trace(go.Histogram(
                            x=type_bert_dist,
                            nbinsx=20,
                            marker_color='#2ca02c'
                        ))
                        fig_bert_type.update_layout(
                            xaxis_title='BERT Similarity',
                            yaxis_title='Count',
                            height=300,
                            showlegend=False
                        )
                        st.plotly_chart(fig_bert_type, use_container_width=True, key="type_bert_hist")
                    else:
                        st.info("No data available")
                
                with col2:
                    st.markdown("### Sentiment Distribution")
                    if type_sentiment_counts:
                        fig_sent_type = go.Figure()
                        
                        fig_sent_type.add_trace(go.Bar(
                            name='Real',
                            x=['Negative', 'Neutral', 'Positive'],
                            y=[
                                type_sentiment_counts['real']['negative'],
                                type_sentiment_counts['real']['neutral'],
                                type_sentiment_counts['real']['positive']
                            ],
                            marker_color='#2ca02c'
                        ))
                        
                        fig_sent_type.add_trace(go.Bar(
                            name='LLM',
                            x=['Negative', 'Neutral', 'Positive'],
                            y=[
                                type_sentiment_counts['llm']['negative'],
                                type_sentiment_counts['llm']['neutral'],
                                type_sentiment_counts['llm']['positive']
                            ],
                            marker_color='#1f77b4'
                        ))
                        
                        fig_sent_type.update_layout(
                            barmode='group',
                            yaxis_title='Count',
                            height=300,
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
                        )
                        st.plotly_chart(fig_sent_type, use_container_width=True, key="type_sent_dist")
                    else:
                        st.info("No data available")
                
                st.markdown("---")
                
                # Sentiment Sign Agreement for this type
                st.markdown("### Sentiment Sign Agreement")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if type_sentiment_agreement:
                        st.metric(
                            "Same Sign Agreement",
                            f"{type_sentiment_agreement['same_sign_pct']:.1f}%",
                            help=f"{type_sentiment_agreement['same_sign']:,} out of {type_sentiment_agreement['total']:,}"
                        )
                
                with col2:
                    if type_sentiment_agreement:
                        st.metric(
                            "Different Sign",
                            f"{type_sentiment_agreement['different_sign_pct']:.1f}%",
                            help=f"{type_sentiment_agreement['different_sign']:,} out of {type_sentiment_agreement['total']:,}"
                        )
                
                with col3:
                    st.markdown("**Breakdown (Same Sign)**")
                    if type_sentiment_agreement:
                        st.write(f"- Both Negative: {type_sentiment_agreement['both_negative']:,}")
                        st.write(f"- Both Neutral: {type_sentiment_agreement['both_neutral']:,}")
                        st.write(f"- Both Positive: {type_sentiment_agreement['both_positive']:,}")
            else:
                st.warning(f"No data available for {selected_type}")
    
    # ========================================
    # SOURCE ANALYSIS
    # ========================================
    st.markdown('<div class="section-header">📡 Data Source Analysis</div>', unsafe_allow_html=True)
    
    source_counts = loader.get_source_counts()
    
    if source_counts:
        # Source selector
        selected_source = st.selectbox("Select Data Source", options=list(source_counts.keys()))
        
        source_stats = loader.get_summary_statistics_by_source(selected_source, 'average_score')
        
        if source_stats:
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Commentary Count", f"{source_stats['commentary_count']:,}")
            with col2:
                st.metric("Avg Score", f"{source_stats['avg_score']:.3f}")
            with col3:
                st.metric("Avg BERT", f"{source_stats['bert']:.3f}")
            with col4:
                st.metric("Avg TF-IDF", f"{source_stats['tfidf']:.3f}")
            with col5:
                st.metric("Avg NER", f"{source_stats.get('ner_score', 0):.3f}")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Avg Content Overlap", f"{source_stats['content_overlap']:.3f}")
            with col2:
                st.metric("Avg Sentiment Diff", f"{source_stats.get('sentiment_diff', 0):.3f}")
            with col3:
                st.metric("Avg Real Words", f"{source_stats.get('real_word_count_avg', 0):.1f}")
            with col4:
                st.metric("Avg LLM Words", f"{source_stats.get('llm_word_count_avg', 0):.1f}")
    
    # ========================================
    # WORD COUNT ANALYSIS
    # ========================================
    st.markdown('<div class="section-header">📝 Word Count Analysis</div>', unsafe_allow_html=True)
    
    word_counts_by_source = loader.get_avg_word_count_by_source('average_score')
    
    if word_counts_by_source:
        sources = list(word_counts_by_source.keys())
        real_avgs = [word_counts_by_source[s]['real_avg'] for s in sources]
        llm_avgs = [word_counts_by_source[s]['llm_avg'] for s in sources]
        
        fig_wc = go.Figure()
        fig_wc.add_trace(go.Bar(name='Real', x=sources, y=real_avgs, marker_color='#2ca02c'))
        fig_wc.add_trace(go.Bar(name='LLM', x=sources, y=llm_avgs, marker_color='#1f77b4'))
        fig_wc.update_layout(
            barmode='group',
            title='Average Word Count by Source',
            yaxis_title='Word Count',
            xaxis_title='Source',
            height=400
        )
        st.plotly_chart(fig_wc, use_container_width=True, key="word_count_source")
    
    # Word count by event type
    word_counts_by_type = loader.get_avg_word_count_by_event_type('average_score', top_n=10)
    
    if word_counts_by_type:
        types = list(word_counts_by_type.keys())
        real_avgs = [word_counts_by_type[t]['real_avg'] for t in types]
        llm_avgs = [word_counts_by_type[t]['llm_avg'] for t in types]
        
        fig_wc_type = go.Figure()
        fig_wc_type.add_trace(go.Bar(name='Real', x=types, y=real_avgs, marker_color='#2ca02c'))
        fig_wc_type.add_trace(go.Bar(name='LLM', x=types, y=llm_avgs, marker_color='#1f77b4'))
        fig_wc_type.update_layout(
            barmode='group',
            title='Average Word Count by Event Type (Top 10)',
            yaxis_title='Word Count',
            xaxis_title='Event Type',
            height=400
        )
        st.plotly_chart(fig_wc_type, use_container_width=True, key="word_count_type")
    
    # ========================================
    # WORD MATCHING ANALYSIS
    # ========================================
    st.markdown('<div class="section-header">📝 Word Matching Analysis</div>', unsafe_allow_html=True)
    
    st.info("""
    **What is Word Matching?**
    
    This section analyzes how many **identical words** appear in both real and LLM commentary, excluding common linking words (the, a, is, etc.).
    
    We track 4 types of matching words:
    - **Content Words**: Meaningful words like "attacks", "shoots", "saves"
    - **Player Names**: Matching player names (e.g., "Yamal", "Williams")
    - **Team Names**: Matching team names (e.g., "Spain", "England")
    - **Event Keywords**: Matching event types (e.g., "shot", "pass", "goal")
    """)
    
    # Get word matching statistics
    with st.spinner("Calculating word matching statistics..."):
        word_stats = loader.get_word_matching_statistics('average_score')
    
    if word_stats:
        # Overview metrics
        st.subheader("📊 Word Matching Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Avg Matching Content Words",
                f"{word_stats['avg_matching_content_words']:.2f}",
                help="Average number of matching content words"
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
                help="Average number of matching event keywords"
            )
        
        st.markdown("---")
        
        # Matching Words Chart
        st.subheader("📊 Matching Words & Entity Scores")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Matching Words**")
            fig_words = go.Figure()
            
            categories = ['Content Words', 'Players', 'Teams', 'Events']
            values = [
                word_stats['avg_matching_content_words'],
                word_stats['avg_matching_players'],
                word_stats['avg_matching_teams'],
                word_stats['avg_matching_events']
            ]
            
            fig_words.add_trace(go.Bar(
                x=categories,
                y=values,
                marker_color=['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728'],
                text=[f'{v:.2f}' for v in values],
                textposition='auto'
            ))
            
            fig_words.update_layout(
                yaxis_title='Average Count',
                height=350,
                showlegend=False
            )
            st.plotly_chart(fig_words, use_container_width=True, key="word_matching_chart")
        
        with col2:
            st.markdown("**Entity Match Scores**")
            fig_entity = go.Figure()
            
            categories_entity = ['Players', 'Teams', 'Events']
            entity_values = [
                word_stats['avg_entity_players_match'],
                word_stats['avg_entity_teams_match'],
                word_stats['avg_entity_events_match']
            ]
            
            fig_entity.add_trace(go.Bar(
                x=categories_entity,
                y=entity_values,
                marker_color=['#2ca02c', '#ff7f0e', '#d62728'],
                text=[f'{v:.3f}' for v in entity_values],
                textposition='auto'
            ))
            
            fig_entity.update_layout(
                yaxis_title='Match Score (0-1)',
                height=350,
                showlegend=False
            )
            st.plotly_chart(fig_entity, use_container_width=True, key="entity_match_chart")
        
        st.markdown("---")
        
        # Word Matching by Event Type
        st.subheader("🎯 Word Matching by Event Type")
        
        with st.spinner("Analyzing event types..."):
            event_type_stats = loader.get_word_matching_by_event_type('average_score')
        
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
            st.markdown("**Top 15 Event Types by Matching Content Words**")
            
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
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig_event_words, use_container_width=True, key="event_word_matching_chart")
            
            # Detailed table for all event types
            st.markdown("**Detailed Event Type Statistics**")
            
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
        
        st.markdown("---")
        
        # Distribution Analysis
        st.subheader("📈 Word Matching Distribution")
        
        with st.spinner("Loading distribution data..."):
            dist_data = loader.get_word_matching_distribution('average_score')
        
        if dist_data:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Content Words Distribution**")
                if dist_data.get('matching_content_words'):
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
                    st.plotly_chart(fig_dist_content, use_container_width=True, key="dist_content")
                
                st.markdown("**Teams Distribution**")
                if dist_data.get('matching_teams'):
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
                    st.plotly_chart(fig_dist_teams, use_container_width=True, key="dist_teams")
            
            with col2:
                st.markdown("**Players Distribution**")
                if dist_data.get('matching_players'):
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
                    st.plotly_chart(fig_dist_players, use_container_width=True, key="dist_players")
                
                st.markdown("**Events Distribution**")
                if dist_data.get('matching_events'):
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
                    st.plotly_chart(fig_dist_events, use_container_width=True, key="dist_events")
    else:
        st.warning("No word matching data available")
    
    # ========================================
    # TOP 10 EVENT TYPES EXAMPLES
    # ========================================
    st.markdown('<div class="section-header">📝 Top 10 Event Types - Commentary Examples by BERT Groups</div>', unsafe_allow_html=True)
    
    st.info(
        "**Purpose**: Compare real vs. LLM commentary for the top 10 event types. "
        "Use the selectors below to choose an event type and BERT similarity range, "
        "then view up to 5 random examples with detailed metrics."
    )
    
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
                key="event_type_selector_examples"
            )
        
        with col2:
            # BERT range selector
            bert_ranges = ['Low (<0.45)', 'Medium (0.45-0.55)', 'High (>0.55)']
            selected_bert_range_ex = st.selectbox(
                "Select BERT Similarity Range",
                bert_ranges,
                key="bert_range_selector_examples"
            )
        
        # Get data for selected combination
        if selected_event_type and selected_bert_range_ex:
            event_data = top_10_examples[selected_event_type]
            range_data = event_data['examples'][selected_bert_range_ex]
            
            st.markdown(f"### {selected_event_type} - {selected_bert_range_ex}")
            st.markdown(f"**{range_data['count_in_range']} examples** available in this BERT range")
            st.markdown("---")
            
            if range_data['samples']:
                for idx, sample in enumerate(range_data['samples'], 1):
                    st.markdown(f"#### Example {idx}")
                    
                    # Display metrics - Row 1
                    st.markdown("**Similarity Scores**")
                    met_col1, met_col2, met_col3, met_col4, met_col5 = st.columns(5)
                    with met_col1:
                        st.metric("BERT Score", f"{sample['bert_score']:.3f}")
                    with met_col2:
                        st.metric("TF-IDF", f"{sample.get('tfidf', 0):.3f}")
                    with met_col3:
                        st.metric("Content Overlap", f"{sample.get('content_overlap', 0):.3f}")
                    with met_col4:
                        st.metric("NER Score", f"{sample.get('ner_score', 0):.3f}")
                    with met_col5:
                        st.metric("Avg Score", f"{sample.get('avg_score', 0):.3f}")
                    
                    # Display metrics - Row 2
                    st.markdown("**Sentiment**")
                    sent_col1, sent_col2, sent_col3 = st.columns(3)
                    with sent_col1:
                        st.metric("Real Sentiment", f"{sample['real_sentiment']:.3f}")
                    with sent_col2:
                        st.metric("LLM Sentiment", f"{sample['llm_sentiment']:.3f}")
                    with sent_col3:
                        agreement = "✅" if abs(sample['sentiment_diff']) < 0.3 else "⚠️"
                        st.metric("Sent. Diff", f"{sample['sentiment_diff']:.3f} {agreement}")
                    
                    # Event info
                    st.markdown("**Event Information**")
                    info_col1, info_col2, info_col3 = st.columns(3)
                    with info_col1:
                        st.metric("Match", sample['match_id'])
                    with info_col2:
                        st.metric("Minute", sample['minute'])
                    with info_col3:
                        st.metric("Source", sample['source'])
                    
                    # Commentaries side by side with highlighted matching words
                    real_text = sample["real_commentary"]
                    llm_text = sample["llm_commentary"]
                    
                    # Get highlighted versions with matching words bolded
                    real_highlighted, llm_highlighted = loader.bold_matching_words(real_text, llm_text)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**📺 Real Commentary**")
                        st.markdown(
                            f'<div style="border: 1px solid #28a745; padding: 10px; border-radius: 5px; '
                            f'background-color: #f8fff8; min-height: 100px; font-size: 14px; line-height: 1.6;">'
                            f'{real_highlighted}</div>',
                            unsafe_allow_html=True
                        )
                    
                    with col2:
                        st.markdown("**🤖 LLM Commentary**")
                        st.markdown(
                            f'<div style="border: 1px solid #1f77b4; padding: 10px; border-radius: 5px; '
                            f'background-color: #f8f8ff; min-height: 100px; font-size: 14px; line-height: 1.6;">'
                            f'{llm_highlighted}</div>',
                            unsafe_allow_html=True
                        )
                    
                    # Legend for highlighting
                    st.markdown(
                        '<div style="font-size: 11px; color: #666; margin-top: 5px;">'
                        '<strong>Bold</strong> = matching important words &nbsp;|&nbsp; '
                        '<span style="font-weight: 500; opacity: 0.7;">Light bold</span> = matching linking words'
                        '</div>',
                        unsafe_allow_html=True
                    )
                    
                    if idx < len(range_data['samples']):
                        st.markdown("---")
            else:
                st.warning(f"No examples available in the {selected_bert_range_ex} BERT range for {selected_event_type}")
    else:
        st.warning("Unable to load event examples")
    
    # ========================================
    # SECTION: BERT vs NER DISCREPANCY ANALYSIS
    # ========================================
    st.markdown('<div class="section-header">🔍 BERT vs NER Discrepancy Analysis</div>', unsafe_allow_html=True)
    
    st.info("""
    **Purpose**: Analyze BERT (semantic similarity) vs NER (entity matching) in a 2x3 matrix.
    
    |  | Low NER (<0.33) | Medium NER (0.33-0.55) | High NER (>0.55) |
    |---|---|---|---|
    | **High BERT (>0.55)** | 🟠 Semantic ✓, Entity ✗ | 🟡 Semantic ✓, Entity ~ | 🟢 Full Match |
    | **Low BERT (<0.45)** | ⚫ Full Mismatch | 🟣 Semantic ✗, Entity ~ | 🔴 Entity ✓, Semantic ✗ |
    """)
    
    st.caption("""
    **NER Thresholds (Best Matches)** | 25th: 0.20 | 50th (Median): 0.33 | 75th: 0.60 | Mean: 0.40  
    → Low NER (<0.33) = below median | Medium (0.33-0.55) | High NER (>0.55) ≈ top 30%
    """)
    
    # Get discrepancy analysis
    with st.spinner("Analyzing BERT vs NER discrepancies..."):
        discrepancy_analysis = loader.get_bert_ner_discrepancy_analysis('average_score')
    
    if discrepancy_analysis:
        # Overview metrics
        st.subheader("📊 Group Overview (2x3 Matrix)")
        
        # High BERT row header
        st.markdown("**High BERT (>0.55)**")
        col1, col2, col3 = st.columns(3)
        
        high_bert_groups = ['high_bert_low_ner', 'high_bert_med_ner', 'high_bert_high_ner']
        high_bert_colors = ['#ff7f0e', '#f1c40f', '#2ca02c']
        
        for i, (group_key, color) in enumerate(zip(high_bert_groups, high_bert_colors)):
            group = discrepancy_analysis[group_key]
            with [col1, col2, col3][i]:
                st.markdown(f"""
                <div style="background-color: {color}20; padding: 12px; border-radius: 8px; border-left: 4px solid {color};">
                    <h5 style="margin: 0; color: {color};">{group['description']}</h5>
                    <p style="font-size: 11px; margin: 3px 0; color: #666;">{group['name']}</p>
                    <h3 style="margin: 8px 0;">{group['count']:,}</h3>
                    <p style="margin: 0; font-size: 12px;">({group['pct']:.1f}%)</p>
                    <p style="margin: 5px 0 0 0; font-size: 11px;">BERT: {group['avg_bert']:.3f} | NER: {group['avg_ner']:.3f}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("")  # Spacing
        
        # Low BERT row header
        st.markdown("**Low BERT (<0.45)**")
        col4, col5, col6 = st.columns(3)
        
        low_bert_groups = ['low_bert_low_ner', 'low_bert_med_ner', 'low_bert_high_ner']
        low_bert_colors = ['#666666', '#9b59b6', '#d62728']
        
        for i, (group_key, color) in enumerate(zip(low_bert_groups, low_bert_colors)):
            group = discrepancy_analysis[group_key]
            with [col4, col5, col6][i]:
                st.markdown(f"""
                <div style="background-color: {color}20; padding: 12px; border-radius: 8px; border-left: 4px solid {color};">
                    <h5 style="margin: 0; color: {color};">{group['description']}</h5>
                    <p style="font-size: 11px; margin: 3px 0; color: #666;">{group['name']}</p>
                    <h3 style="margin: 8px 0;">{group['count']:,}</h3>
                    <p style="margin: 0; font-size: 12px;">({group['pct']:.1f}%)</p>
                    <p style="margin: 5px 0 0 0; font-size: 11px;">BERT: {group['avg_bert']:.3f} | NER: {group['avg_ner']:.3f}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Group selector for detailed analysis
        st.subheader("📋 Detailed Group Analysis")
        
        group_options = {
            'high_bert_low_ner': '🟠 High BERT + Low NER (Semantic ✓, Entity ✗)',
            'high_bert_med_ner': '🟡 High BERT + Med NER (Semantic ✓, Entity ~)',
            'high_bert_high_ner': '🟢 High BERT + High NER (Full Match ✓✓)',
            'low_bert_low_ner': '⚫ Low BERT + Low NER (Full Mismatch ✗✗)',
            'low_bert_med_ner': '🟣 Low BERT + Med NER (Semantic ✗, Entity ~)',
            'low_bert_high_ner': '🔴 Low BERT + High NER (Entity ✓, Semantic ✗)'
        }
        
        selected_group = st.selectbox(
            "Select group to analyze:",
            options=list(group_options.keys()),
            format_func=lambda x: group_options[x],
            key='bert_ner_group_selector'
        )
        
        if selected_group:
            group_info = discrepancy_analysis[selected_group]
            
            st.markdown(f"**{group_info['description']}**: {group_info['count']:,} commentaries ({group_info['pct']:.1f}%)")
            
            # Event distribution
            st.markdown("### Top 10 Event Types Distribution")
            
            event_dist = loader.get_bert_ner_event_distribution(selected_group, 'average_score')
            
            if event_dist and event_dist.get('event_types'):
                # Create bar chart
                group_colors = {
                    'high_bert_low_ner': '#ff7f0e',
                    'high_bert_med_ner': '#f1c40f',
                    'high_bert_high_ner': '#2ca02c',
                    'low_bert_low_ner': '#666666',
                    'low_bert_med_ner': '#9b59b6',
                    'low_bert_high_ner': '#d62728'
                }
                fig_events = go.Figure()
                fig_events.add_trace(go.Bar(
                    x=event_dist['event_types'],
                    y=event_dist['counts'],
                    text=event_dist['counts'],
                    textposition='auto',
                    marker_color=group_colors.get(selected_group, '#1f77b4')
                ))
                fig_events.update_layout(
                    xaxis_title='Event Type',
                    yaxis_title='Count',
                    height=400,
                    xaxis=dict(tickangle=-45)
                )
                st.plotly_chart(fig_events, use_container_width=True, key=f'bert_ner_events_{selected_group}')
                
                # Event table
                event_table = pd.DataFrame({
                    'Event Type': event_dist['event_types'],
                    'Count': event_dist['counts'],
                    '% of Group': [f"{c/event_dist['total_in_group']*100:.1f}%" for c in event_dist['counts']]
                })
                st.dataframe(event_table, hide_index=True, use_container_width=True)
            else:
                st.warning("No event distribution data available for this group")
            
            st.markdown("---")
            
            # Examples
            st.markdown("### 📝 10 Example Commentaries")
            
            examples = loader.get_bert_ner_examples(selected_group, n_samples=10, score_type='average_score')
            
            if examples:
                for idx, example in enumerate(examples, 1):
                    with st.expander(f"Example {idx} | BERT: {example['bert']:.3f} | NER: {example['ner_score']:.3f} | {example['llm_event_type']}"):
                        # Metrics row
                        m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
                        with m_col1:
                            st.metric("BERT", f"{example['bert']:.3f}")
                        with m_col2:
                            st.metric("NER", f"{example['ner_score']:.3f}")
                        with m_col3:
                            st.metric("TF-IDF", f"{example['tfidf']:.3f}")
                        with m_col4:
                            st.metric("Content Overlap", f"{example['content_overlap']:.3f}")
                        with m_col5:
                            st.metric("Avg Score", f"{example['average_score']:.3f}")
                        
                        # Info row
                        i_col1, i_col2, i_col3, i_col4 = st.columns(4)
                        with i_col1:
                            st.caption(f"**Real Type:** {example['real_type']}")
                        with i_col2:
                            st.caption(f"**LLM Type:** {example['llm_event_type']}")
                        with i_col3:
                            st.caption(f"**Minute:** {example['minute']}")
                        with i_col4:
                            st.caption(f"**Source:** {example['data_source']}")
                        
                        # Commentary comparison
                        real_highlighted, llm_highlighted = loader.bold_matching_words(
                            example['real_commentary'],
                            example['llm_commentary']
                        )
                        
                        comm_col1, comm_col2 = st.columns(2)
                        with comm_col1:
                            st.markdown("**📺 Real Commentary**")
                            st.markdown(
                                f'<div style="border: 1px solid #28a745; padding: 10px; border-radius: 5px; '
                                f'background-color: #f8fff8; font-size: 13px; line-height: 1.5;">'
                                f'{real_highlighted}</div>',
                                unsafe_allow_html=True
                            )
                        with comm_col2:
                            st.markdown("**🤖 LLM Commentary**")
                            st.markdown(
                                f'<div style="border: 1px solid #1f77b4; padding: 10px; border-radius: 5px; '
                                f'background-color: #f8f8ff; font-size: 13px; line-height: 1.5;">'
                                f'{llm_highlighted}</div>',
                                unsafe_allow_html=True
                            )
            else:
                st.warning("No examples available for this group")
    else:
        st.warning("Unable to load BERT vs NER discrepancy analysis")
    
    # ========================================
    # FOOTER
    # ========================================
    st.markdown("---")
    st.markdown(
        "*Dashboard created for Euro 2024 LLM Commentator Project - "
        f"Analyzing {general_info['total_csv_files']} comparison files*"
    )
    
    # Sidebar footer
    st.sidebar.divider()
    st.sidebar.caption(f"📊 Data: {general_info['total_comparisons']:,} total comparisons")
    st.sidebar.caption(f"🎮 Matches: {general_info['total_games']}")
    st.sidebar.caption(f"📡 Sources: {', '.join(general_info['sources_list'])}")


if __name__ == "__main__":
    main()
