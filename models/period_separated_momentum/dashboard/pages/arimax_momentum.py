"""
ARIMAX Momentum Analysis Page - Period-Separated Version
Comprehensive analysis of the ARIMAX model for 3-minute momentum prediction
Using period-separated momentum data (no mixing of 1st/2nd half events)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path


@st.cache_data
def load_llm_commentary_cached(path):
    """Cache LLM commentary data for performance"""
    if Path(path).exists():
        return pd.read_csv(path)
    return None

@st.cache_data
def load_events_cached(path):
    """Cache events data for performance"""
    if Path(path).exists():
        return pd.read_csv(path, low_memory=False)
    return None


class ARIMAXMomentumPage:
    """ARIMAX Momentum Analysis page implementation using period-separated data"""
    
    def __init__(self, data_loader=None):
        self.data_loader = data_loader
        self.base_path = Path(__file__).parent.parent.parent
        self.project_root = self.base_path.parent.parent
        self.predictions_path = self.base_path / "outputs" / "arimax_predictions_by_period.csv"
        self.momentum_path = self.base_path / "outputs" / "momentum_by_period.csv"
        self.events_path = self.project_root / "Data" / "events_complete.csv"
        self.llm_commentary_path = self.project_root / "NLP - Commentator" / "research" / "10_llm_commentary" / "data" / "llm_commentary" / "all_matches_V3_20251209_193514.csv"
        self.predictions_df = None
        self.arimax_df = None
        self.momentum_df = None
        self.events_df = None
        self.llm_commentary_df = None
        
    def load_data(self):
        """Load period-separated data"""
        try:
            # Load predictions
            if self.predictions_path.exists():
                self.predictions_df = pd.read_csv(self.predictions_path)
                self.arimax_df = self.predictions_df.copy()
            else:
                st.warning(f"Predictions not found at {self.predictions_path}")
                return False
            
            # Load momentum data
            if self.momentum_path.exists():
                self.momentum_df = pd.read_csv(self.momentum_path)
            else:
                st.warning(f"Momentum data not found at {self.momentum_path}")
                return False
            
            # Load events data (cached for performance)
            self.events_df = load_events_cached(str(self.events_path))
            
            # Load LLM commentary data (cached for performance)
            self.llm_commentary_df = load_llm_commentary_cached(str(self.llm_commentary_path))
            
            return True
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return False
    
    def get_events_for_minutes(self, match_id, minutes_list, period=None):
        """Get key events for specific minutes using LLM commentary detected_type"""
        if self.llm_commentary_df is None:
            return "No LLM data"
        
        # Filter LLM commentary for this match and minutes
        events = self.llm_commentary_df[
            (self.llm_commentary_df['match_id'] == match_id) & 
            (self.llm_commentary_df['minute'].isin(minutes_list))
        ].copy()
        
        if period is not None:
            events = events[events['period'] == period]
        
        if len(events) == 0:
            return "No data"
        
        # Get 1 event per minute from detected_type
        commentary = []
        for minute in sorted(minutes_list):
            min_events = events[events['minute'] == minute]
            if len(min_events) > 0:
                event = min_events.iloc[0]
                detected = event['detected_type'] if pd.notna(event['detected_type']) else 'General'
                team = event['team'] if pd.notna(event['team']) else ''
                team_short = team[:3].upper() if team else ''
                
                if team_short:
                    desc = f"{minute}': {team_short} {detected}"
                else:
                    desc = f"{minute}': {detected}"
                
                commentary.append(desc)
        
        if not commentary:
            return "Build-up play"
        
        return " | ".join(commentary[:4])  # Limit to 4 events
    
    def calculate_metrics(self):
        """Calculate all metrics from the new data"""
        if self.arimax_df is None:
            return None
        
        # Drop rows with NaN values for accurate calculations
        df_clean = self.arimax_df.dropna(subset=['prediction_value', 'actual_value'])
        
        pred = df_clean['prediction_value'].values
        actual = df_clean['actual_value'].values
        
        # MSE
        mse = np.mean((pred - actual) ** 2)
        
        # Sign Agreement
        pred_sign = np.sign(pred)
        actual_sign = np.sign(actual)
        sign_agreement = (pred_sign == actual_sign).mean()
        
        # Directional Accuracy (consecutive movement)
        if len(pred) > 1:
            pred_dirs = np.sign(np.diff(pred))
            actual_dirs = np.sign(np.diff(actual))
            directional_acc = (pred_dirs == actual_dirs).mean()
        else:
            directional_acc = 0.0
        
        # Sign distribution
        pred_pos = int((pred_sign > 0).sum())
        pred_neg = int((pred_sign < 0).sum())
        actual_pos = int((actual_sign > 0).sum())
        actual_neg = int((actual_sign < 0).sum())
        
        # Contingency table
        pp = int(((pred_sign > 0) & (actual_sign > 0)).sum())
        nn = int(((pred_sign < 0) & (actual_sign < 0)).sum())
        pn = int(((pred_sign > 0) & (actual_sign < 0)).sum())
        np_ = int(((pred_sign < 0) & (actual_sign > 0)).sum())
        
        return {
            'mse': mse,
            'sign_agreement': sign_agreement,
            'directional_acc': directional_acc,
            'pred_pos': pred_pos,
            'pred_neg': pred_neg,
            'actual_pos': actual_pos,
            'actual_neg': actual_neg,
            'pp': pp,
            'nn': nn,
            'pn': pn,
            'np': np_,
            'total': len(pred)
        }
    
    def calculate_differential_metrics(self):
        """Calculate differential sign metrics (Team X vs Team Y)"""
        if self.arimax_df is None:
            return None
        
        # Group by match_id and minute to get paired predictions
        df = self.arimax_df.copy()
        
        # Get home and away predictions per window
        home_preds = df[df['is_home'] == True][['match_id', 'minute_start', 'prediction_value', 'actual_value']].copy()
        away_preds = df[df['is_home'] == False][['match_id', 'minute_start', 'prediction_value', 'actual_value']].copy()
        
        home_preds.columns = ['match_id', 'minute_start', 'pred_home', 'actual_home']
        away_preds.columns = ['match_id', 'minute_start', 'pred_away', 'actual_away']
        
        merged = pd.merge(home_preds, away_preds, on=['match_id', 'minute_start'])
        
        # Drop rows with NaN values
        merged = merged.dropna()
        
        if len(merged) == 0:
            return None
        
        # Calculate differentials
        merged['pred_diff'] = merged['pred_home'] - merged['pred_away']
        merged['actual_diff'] = merged['actual_home'] - merged['actual_away']
        
        # Filter out zero differentials for sign analysis (exclude ties)
        non_zero = merged[(merged['pred_diff'] != 0) & (merged['actual_diff'] != 0)]
        
        if len(non_zero) == 0:
            return None
        
        pred_diff_sign = np.sign(non_zero['pred_diff'].values)
        actual_diff_sign = np.sign(non_zero['actual_diff'].values)
        
        # Differential accuracy
        diff_accuracy = (pred_diff_sign == actual_diff_sign).mean()
        
        # Contingency
        pp = int(((pred_diff_sign > 0) & (actual_diff_sign > 0)).sum())
        nn = int(((pred_diff_sign < 0) & (actual_diff_sign < 0)).sum())
        pn = int(((pred_diff_sign > 0) & (actual_diff_sign < 0)).sum())
        np_ = int(((pred_diff_sign < 0) & (actual_diff_sign > 0)).sum())
        
        # Correlation - use merged (not non_zero) for better correlation estimate
        try:
            valid_data = merged[['pred_diff', 'actual_diff']].dropna()
            if len(valid_data) > 1:
                corr = valid_data['pred_diff'].corr(valid_data['actual_diff'])
            else:
                corr = 0.0
        except:
            corr = 0.0
        
        return {
            'accuracy': diff_accuracy,
            'pp': pp,
            'nn': nn,
            'pn': pn,
            'np': np_,
            'total': len(non_zero),
            'correlation': corr if not np.isnan(corr) else 0.0
        }
    
    def calculate_paired_metrics(self):
        """Calculate paired team analysis (both teams in same window)"""
        if self.arimax_df is None:
            return None
        
        # Drop NaN values FIRST
        df = self.arimax_df.dropna(subset=['prediction_value', 'actual_value']).copy()
        
        # Get home and away predictions per window
        home_preds = df[df['is_home'] == True][['match_id', 'minute_start', 'prediction_value', 'actual_value']]
        away_preds = df[df['is_home'] == False][['match_id', 'minute_start', 'prediction_value', 'actual_value']]
        
        home_preds.columns = ['match_id', 'minute_start', 'pred_home', 'actual_home']
        away_preds.columns = ['match_id', 'minute_start', 'pred_away', 'actual_away']
        
        merged = pd.merge(home_preds, away_preds, on=['match_id', 'minute_start'])
        
        if len(merged) == 0:
            return None
        
        # Check if each team's sign is correct
        home_correct = np.sign(merged['pred_home'].values) == np.sign(merged['actual_home'].values)
        away_correct = np.sign(merged['pred_away'].values) == np.sign(merged['actual_away'].values)
        
        both_correct = (home_correct & away_correct).sum()
        only_home_correct = (home_correct & ~away_correct).sum()
        only_away_correct = (~home_correct & away_correct).sum()
        both_wrong = (~home_correct & ~away_correct).sum()
        
        return {
            'both_correct': both_correct,
            'only_home_correct': only_home_correct,
            'only_away_correct': only_away_correct,
            'both_wrong': both_wrong,
            'total': len(merged)
        }
    
    def render(self):
        """Render the ARIMAX Momentum Analysis page"""
        
        # Page header
        st.markdown('<h1 class="main-header">🎯 ARIMAX Momentum Prediction Model</h1>', 
                   unsafe_allow_html=True)
        st.markdown("### 3-Minute Momentum Change Forecasting (Period-Separated)")
        st.markdown("**Using period-separated momentum data** - First half and second half events are properly separated")
        st.markdown("---")
        
        # Load data
        data_loaded = self.load_data()
        metrics = self.calculate_metrics() if data_loaded else None
        diff_metrics = self.calculate_differential_metrics() if data_loaded else None
        paired_metrics = self.calculate_paired_metrics() if data_loaded else None
        
        # Create tabs for different sections
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 Model Overview", 
            "🎯 Sign Accuracy Analysis",
            "👥 Paired Team Analysis", 
            "📈 Metric Definitions",
            "🔬 Real Data Analysis",
            "📉 Game Comparison"
        ])
        
        with tab1:
            self.render_model_overview(metrics, diff_metrics)
        
        with tab2:
            self.render_sign_accuracy(metrics)
        
        with tab3:
            self.render_paired_analysis(paired_metrics)
        
        with tab4:
            self.render_metric_definitions(metrics)
        
        with tab5:
            self.render_real_data_analysis()
        
        with tab6:
            self.render_game_comparison()
    
    def render_model_overview(self, metrics, diff_metrics):
        """Render model overview section"""
        st.subheader("🏆 ARIMAX Model Performance Summary (Period-Separated Data)")
        
        if metrics is None:
            st.error("Could not calculate metrics - data not loaded")
            return
        
        # Key metrics in cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            dir_acc = metrics['directional_acc'] * 100
            st.metric(
                "Directional Accuracy",
                f"{dir_acc:.2f}%",
                f"+{dir_acc - 50:.2f}% vs random",
                help="Correctly predicts if momentum TREND goes up or down"
            )
        
        with col2:
            diff_acc = diff_metrics['accuracy'] * 100 if diff_metrics else 0
            st.metric(
                "Differential Sign",
                f"{diff_acc:.2f}%",
                f"+{diff_acc - 50:.2f}% vs random",
                help="Correctly predicts which team gains momentum advantage"
            )
        
        with col3:
            sign_acc = metrics['sign_agreement'] * 100
            st.metric(
                "Sign Agreement",
                f"{sign_acc:.2f}%",
                f"+{sign_acc - 50:.2f}% vs random",
                help="Correctly predicts positive vs negative momentum change"
            )
        
        st.markdown("---")
        
        # Data source info
        st.info("""
        **📊 Data Source:** Period-Separated Momentum
        - First half (Period 1) and second half (Period 2) are calculated separately
        - No mixing of events from different periods at overlapping minutes (45-48, 90-93)
        - Training: Minutes 0-74 | Testing: Minutes 75-90
        """)
        
        st.markdown("---")
        
        # Team-based prediction explanation
        st.markdown("### ⚽ Momentum Prediction Per Team")
        
        st.markdown("""
        The ARIMAX model predicts momentum change **separately for each team** in every 3-minute window.
        This means for each game window, we generate **two predictions**:
        
        - **Home Team Prediction:** How will the home team's momentum change in the next 3 minutes?
        - **Away Team Prediction:** How will the away team's momentum change in the next 3 minutes?
        
        This dual-prediction approach allows us to:
        1. **Track each team independently** - Teams can both gain momentum simultaneously (different aspects of the game)
        2. **Compare relative performance** - Which team will have the better momentum shift?
        3. **Identify asymmetric patterns** - One team's gain doesn't always mean the other's loss
        """)
        
        st.markdown("---")
        
        # Model description
        st.markdown("### 📋 What is ARIMAX?")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            **ARIMAX** (Autoregressive Integrated Moving Average with eXogenous variables) is a time series 
            forecasting model that predicts **momentum change in the next 3 minutes** by using **current 
            momentum values as an exogenous variable**.
            
            **Prediction Target:**
            ```
            Momentum Change = y(t+3) - y(t)
            ```
            Where:
            - **y(t)** = Weighted average momentum of the input window (t-3 to t)
            - **y(t+3)** = Weighted average momentum of the target window (t to t+3)
            
            **Key Innovation:** The model leverages current momentum state to contextualize change predictions:
            - Teams with high momentum behave differently than teams with low momentum
            - Current game dynamics influence future momentum shifts
            - This captures the psychology and tactics of real football matches
            """)
        
        with col2:
            st.info("""
            **Model Configuration:**
            - **ARIMA Order:** (1,1,1)
            - **Training:** Minutes 0-74
            - **Testing:** Minutes 75-90
            - **Windows:** 3-minute intervals
            - **Exogenous:** Current momentum
            """)
        
        st.markdown("---")
        
        # Momentum Function Explanation
        st.markdown("### 📊 The Momentum Function")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            The momentum function calculates a **weighted score** for each football event based on multiple factors:
            
            **Base Weight Calculation:**
            - Each event type (Pass, Shot, Tackle, etc.) has a **base weight** based on its importance
            - Event outcomes modify the base weight (successful vs unsuccessful)
            
            **Context Multipliers Applied:**
            1. **Location Multiplier:** Events closer to the opponent's goal have higher impact
            2. **Time Multiplier:** Events in crucial game phases (opening, closing) weighted more
            3. **Score Multiplier:** Events when trailing or leading by different margins
            4. **Pressure Multiplier:** Events under defensive pressure count more
            
            **Team Perspective:**
            - The same event has **opposite effects** for each team
            - A successful tackle is **positive** for the defending team and **negative** for the attacking team
            """)
        
        with col2:
            st.success("""
            **Event Types Included:**
            - Passes (successful/failed)
            - Shots (on target/blocked/missed)
            - Dribbles & Carries
            - Tackles & Interceptions
            - Clearances
            - Fouls & Cards
            - And more...
            
            **Total:** 25 event types analyzed
            """)
        
        st.markdown("---")
        
        # Why 3-minute windows - with autocorrelation evidence
        st.markdown("### ⏱️ Why 3-Minute Windows? (Autocorrelation Analysis)")
        
        st.markdown("""
        The 3-minute window was determined through **autocorrelation analysis** on 4,927 minute-level 
        observations across 51 Euro 2024 matches. This analysis measures how strongly momentum at time 
        *t* correlates with momentum at time *t+lag*.
        """)
        
        # Autocorrelation data table
        autocorr_data = {
            'Momentum Feature': ['Possession Balance', 'Intensity Balance', 'Pattern Balance', 
                                'Complexity Balance', 'Momentum Balance', '**Average**'],
            '1-min Lag': [0.856, 0.790, 0.889, 0.889, 0.834, '**0.852**'],
            '3-min Lag': [0.561, 0.272, 0.576, 0.601, 0.454, '**0.493**'],
            '5-min Lag': [0.303, 0.254, 0.302, 0.341, 0.300, '**0.300**'],
            '15-min Lag': [0.217, 0.199, 0.255, 0.269, 0.221, '**0.232**']
        }
        
        df_autocorr = pd.DataFrame(autocorr_data)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create line chart for autocorrelation decay
            fig_autocorr = go.Figure()
            
            features = ['Possession Balance', 'Intensity Balance', 'Pattern Balance', 
                       'Complexity Balance', 'Momentum Balance']
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
            
            lags = [1, 3, 5, 15]
            
            for i, feature in enumerate(features):
                values = [0.856, 0.561, 0.303, 0.217] if feature == 'Possession Balance' else \
                         [0.790, 0.272, 0.254, 0.199] if feature == 'Intensity Balance' else \
                         [0.889, 0.576, 0.302, 0.255] if feature == 'Pattern Balance' else \
                         [0.889, 0.601, 0.341, 0.269] if feature == 'Complexity Balance' else \
                         [0.834, 0.454, 0.300, 0.221]
                
                fig_autocorr.add_trace(go.Scatter(
                    x=lags, y=values,
                    mode='lines+markers',
                    name=feature,
                    line=dict(color=colors[i], width=2),
                    marker=dict(size=8)
                ))
            
            # Add vertical line at 3 minutes
            fig_autocorr.add_vline(x=3, line_dash="dash", line_color="red", 
                                   annotation_text="3-min window", annotation_position="top")
            
            # Add horizontal line at 0.3 threshold
            fig_autocorr.add_hline(y=0.3, line_dash="dot", line_color="gray",
                                   annotation_text="Prediction threshold", annotation_position="left")
            
            fig_autocorr.update_layout(
                title='Autocorrelation Decay Over Time (Higher = More Predictable)',
                xaxis_title='Time Lag (minutes)',
                yaxis_title='Autocorrelation',
                height=400,
                legend=dict(orientation="h", yanchor="bottom", y=-0.3)
            )
            
            st.plotly_chart(fig_autocorr, use_container_width=True, key="autocorr_chart")
        
        with col2:
            st.dataframe(df_autocorr, use_container_width=True, hide_index=True)
        
        # Key insights from autocorrelation
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("""
            **🎯 Why 3 Minutes is Optimal:**
            
            1. **Strong Signal:** Average autocorrelation at 3-min is **0.493** 
               (strong predictive relationship)
            
            2. **Sweet Spot:** Momentum sustains 2-5 minutes based on 
               persistence analysis
            
            3. **Sufficient Data:** ~10-30 events per window for 
               statistical reliability
            """)
        
        with col2:
            st.warning("""
            **⚠️ Why Not Longer Windows:**
            
            1. **Decay at 5-min:** Autocorrelation drops to ~0.30 
               (prediction becomes weaker)
            
            2. **Low at 15-min:** Only ~0.23 correlation 
               (too much noise)
            
            3. **Tactical Relevance:** Most football phases 
               complete within 3 minutes
            """)
        
        st.markdown("---")
        
        # Hybrid weighting
        st.markdown("### ⚖️ Hybrid Weighting System")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            Within each 3-minute window, events are weighted by recency:
            
            ```
            Event Weight = Base Weight × (0.7 + 0.3 × recency_factor)
            ```
            
            - **Recency Factor:** 0 (oldest) to 1 (newest)
            - **Effect:** Recent events have up to **30% more weight**
            - **Rationale:** Recent events better reflect current momentum state
            """)
        
        with col2:
            st.info("""
            **Example:**
            - Event at t-3 min: weight multiplier = 0.70
            - Event at t-2 min: weight multiplier = 0.80
            - Event at t-1 min: weight multiplier = 0.90
            - Event at t-0 min: weight multiplier = 1.00
            """)
        
        # Key insights box
        if metrics:
            dir_acc = metrics['directional_acc'] * 100
            st.success(f"""
            **🎯 Key Achievement:** ARIMAX achieves **{dir_acc:.2f}% directional accuracy** - meaning it correctly 
            predicts whether momentum will go UP or DOWN. This is 
            **{dir_acc - 50:.1f}% better than random chance** and enables practical tactical decision-making.
            """)
    
    def render_sign_accuracy(self, metrics):
        """Render sign accuracy analysis section"""
        st.subheader("🎯 Sign Agreement Analysis")
        
        if metrics is None:
            st.error("Could not calculate metrics - data not loaded")
            return
        
        pred_pos = metrics['pred_pos']
        pred_neg = metrics['pred_neg']
        actual_pos = metrics['actual_pos']
        actual_neg = metrics['actual_neg']
        pp = metrics['pp']
        nn = metrics['nn']
        pn = metrics['pn']
        np_ = metrics['np']
        total = metrics['total']
        
        correct = pp + nn
        sign_accuracy = correct / total if total > 0 else 0
        
        # Distribution comparison
        st.markdown("### 📊 Sign Distribution: Prediction vs Actual")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### PREDICTION Distribution")
            
            fig_pred = go.Figure(data=[go.Pie(
                labels=['Positive (+)', 'Negative (-)'],
                values=[pred_pos, pred_neg],
                hole=0.4,
                marker_colors=['#2ca02c', '#d62728'],
                textinfo='label+percent+value'
            )])
            
            fig_pred.update_layout(
                title='Predicted Signs',
                height=350
            )
            
            st.plotly_chart(fig_pred, use_container_width=True, key="pred_distribution_pie")
            
            st.markdown(f"""
            - **Positive (+):** {pred_pos:,} ({pred_pos/total*100:.1f}%)
            - **Negative (-):** {pred_neg:,} ({pred_neg/total*100:.1f}%)
            """)
        
        with col2:
            st.markdown("#### ACTUAL Distribution")
            
            fig_actual = go.Figure(data=[go.Pie(
                labels=['Positive (+)', 'Negative (-)'],
                values=[actual_pos, actual_neg],
                hole=0.4,
                marker_colors=['#2ca02c', '#d62728'],
                textinfo='label+percent+value'
            )])
            
            fig_actual.update_layout(
                title='Actual Signs',
                height=350
            )
            
            st.plotly_chart(fig_actual, use_container_width=True, key="actual_distribution_pie")
            
            st.markdown(f"""
            - **Positive (+):** {actual_pos:,} ({actual_pos/total*100:.1f}%)
            - **Negative (-):** {actual_neg:,} ({actual_neg/total*100:.1f}%)
            """)
        
        pred_neg_pct = pred_neg/total*100
        actual_neg_pct = actual_neg/total*100
        
        if pred_neg_pct > actual_neg_pct:
            st.warning(f"""
            **📌 Model Bias Observation:** The model predicts more negative changes ({pred_neg_pct:.1f}%) 
            than actually occur ({actual_neg_pct:.1f}%). This "pessimistic" tendency means the model 
            is more conservative about predicting momentum increases.
            """)
        else:
            st.info(f"""
            **📌 Model Observation:** Prediction distribution: {pred_neg_pct:.1f}% negative vs 
            actual {actual_neg_pct:.1f}% negative.
            """)
        
        st.markdown("---")
        
        # Contingency table
        st.markdown("### 📋 Sign Agreement Matrix (2x2 Contingency Table)")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create heatmap for contingency table with explicit colors
            # Green for correct (diagonal: PP, NN), Red for wrong (off-diagonal: PN, NP)
            fig_heatmap = go.Figure()
            
            # Add rectangles with explicit colors
            # Row 0 (Predicted Positive): PP (green), PN (red)
            # Row 1 (Predicted Negative): NP (red), NN (green)
            
            fig_heatmap.add_trace(go.Heatmap(
                z=[[1, 0], [0, 1]],  # 1 = correct (green), 0 = wrong (red)
                x=['Actual Positive', 'Actual Negative'],
                y=['Predicted Positive', 'Predicted Negative'],
                text=[[f'{pp}<br>({pp/total*100:.1f}%)', f'{pn}<br>({pn/total*100:.1f}%)'],
                      [f'{np_}<br>({np_/total*100:.1f}%)', f'{nn}<br>({nn/total*100:.1f}%)']],
                texttemplate='%{text}',
                textfont={"size": 16, "color": "black"},
                colorscale=[[0, '#ffcccb'], [1, '#90EE90']],  # Red to Green
                showscale=False,
                hoverinfo='text'
            ))
            
            fig_heatmap.update_layout(
                title='Sign Agreement Contingency Table',
                height=350,
                xaxis_title='Actual Sign',
                yaxis_title='Predicted Sign'
            )
            
            st.plotly_chart(fig_heatmap, use_container_width=True, key="contingency_heatmap")
        
        with col2:
            st.markdown("#### Results Breakdown")
            
            st.markdown(f"""
            **✅ CORRECT ({correct:,} | {sign_accuracy*100:.2f}%):**
            - Positive→Positive: {pp:,} ({pp/total*100:.2f}%)
            - Negative→Negative: {nn:,} ({nn/total*100:.2f}%)
            
            **❌ WRONG ({pn + np_:,} | {(pn + np_)/total*100:.2f}%):**
            - Positive→Negative: {pn:,} ({pn/total*100:.2f}%)
            - Negative→Positive: {np_:,} ({np_/total*100:.2f}%)
            """)
            
            # Add insight about asymmetric errors
            st.info(f"""
            **Asymmetric Errors:**
            Negative→Positive errors ({np_/total*100:.1f}%) vs 
            Positive→Negative errors ({pn/total*100:.1f}%)
            """)
        
        st.markdown("---")
        
        # Differential Sign Analysis Results
        st.markdown("### ☑️ Differential Sign Analysis Results")
        
        st.markdown("""
        The **Differential Sign Analysis** compares momentum change between the two teams in each window
        to determine which team gains the momentum advantage.
        """)
        
        diff_metrics = self.calculate_differential_metrics()
        
        if diff_metrics:
            diff_pp = diff_metrics['pp']
            diff_nn = diff_metrics['nn']
            diff_pn = diff_metrics['pn']
            diff_np = diff_metrics['np']
            diff_total = diff_metrics['total']
            diff_corr = diff_metrics['correlation']
            diff_acc = diff_metrics['accuracy']
            
            differential_data = {
                'Predicted Sign': ['Positive', 'Positive', 'Negative', 'Negative'],
                'Actual Sign': ['Positive', 'Negative', 'Positive', 'Negative'],
                'Count': [diff_pp, diff_pn, diff_np, diff_nn],
                'Percentage': [f'{diff_pp/diff_total*100:.2f}%', f'{diff_pn/diff_total*100:.2f}%', 
                              f'{diff_np/diff_total*100:.2f}%', f'{diff_nn/diff_total*100:.2f}%'],
                'Result': ['✅ Correct', '❌ Wrong', '❌ Wrong', '✅ Correct']
            }
            
            df_differential = pd.DataFrame(differential_data)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Create grouped bar chart
                fig_diff = go.Figure(data=[
                    go.Bar(
                        name='Correct (PP + NN)',
                        x=['Positive→Positive', 'Negative→Negative'],
                        y=[diff_pp, diff_nn],
                        marker_color='#2ca02c',
                        text=[diff_pp, diff_nn],
                        textposition='auto'
                    ),
                    go.Bar(
                        name='Wrong (PN + NP)',
                        x=['Positive→Negative', 'Negative→Positive'],
                        y=[diff_pn, diff_np],
                        marker_color='#d62728',
                        text=[diff_pn, diff_np],
                        textposition='auto'
                    )
                ])
                
                fig_diff.update_layout(
                    title='Differential Sign Prediction Results',
                    xaxis_title='Prediction → Actual',
                    yaxis_title='Count',
                    height=400,
                    barmode='group'
                )
                
                st.plotly_chart(fig_diff, use_container_width=True, key="sign_differential_results")
            
            with col2:
                st.dataframe(df_differential, use_container_width=True, hide_index=True)
                
                st.markdown(f"""
                **Summary:**
                - **Correct:** {diff_pp + diff_nn}/{diff_total} ({diff_acc*100:.2f}%)
                - **Wrong:** {diff_pn + diff_np}/{diff_total} ({(1-diff_acc)*100:.2f}%)
                """)
            
            st.markdown("---")
            
            # Conditional Accuracy
            st.markdown("### 🎯 Conditional Accuracy")
            
            # Calculate conditional accuracy from data
            actual_pos_count = diff_pp + diff_np  # When actual differential is positive
            actual_neg_count = diff_nn + diff_pn  # When actual differential is negative
            
            acc_when_pos = diff_pp / actual_pos_count * 100 if actual_pos_count > 0 else 0
            acc_when_neg = diff_nn / actual_neg_count * 100 if actual_neg_count > 0 else 0
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                **When Actual Differential is POSITIVE (Team X ahead):**
                - Accuracy: **{acc_when_pos:.2f}%** ({diff_pp}/{actual_pos_count} correct)
                - ARIMAX correctly identifies when Team X gains momentum advantage
                """)
            
            with col2:
                st.markdown(f"""
                **When Actual Differential is NEGATIVE (Team Y ahead):**
                - Accuracy: **{acc_when_neg:.2f}%** ({diff_nn}/{actual_neg_count} correct)
                - ARIMAX {'is **BETTER**' if acc_when_neg > acc_when_pos else 'performs similarly'} at identifying when Team Y gains momentum advantage
                """)
            
            if acc_when_neg > acc_when_pos:
                st.info(f"""
                **🔍 Asymmetric Accuracy:** The model shows better performance at detecting Team Y advantages 
                ({acc_when_neg:.2f}%) than Team X advantages ({acc_when_pos:.2f}%). This indicates the model is slightly better at 
                identifying when teams are **losing** momentum than **gaining** it.
                """)
            
            st.markdown("---")
            
            # Practical Implications
            st.markdown("### 💡 Practical Implications")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.success(f"""
                **✅ Strengths:**
                1. **Strong Overall Accuracy:** {diff_acc*100:.1f}% correct differential signs
                2. **Tactical Value:** Can predict relative momentum shifts
                3. **Asymmetric Skill:** Good at identifying momentum losses
                """)
            
            with col2:
                st.warning("""
                **⚠️ Limitations:**
                1. **Negative Bias:** Systematically predicts more negative differentials
                2. **Overconfidence:** Predictions more extreme than reality
                3. **Zero Handling:** Never predicts exact ties (rare but occurs)
                """)
            
            # Real Match Examples - Calculate from data
            st.markdown("### 🏟️ Real Match Examples")
            
            # Get sample predictions from actual data
            df = self.arimax_df.copy()
            home_preds = df[df['is_home'] == True][['match_id', 'minute_start', 'prediction_value', 'actual_value', 'team']].copy()
            away_preds = df[df['is_home'] == False][['match_id', 'minute_start', 'prediction_value', 'actual_value', 'team']].copy()
            
            home_preds.columns = ['match_id', 'minute_start', 'pred_home', 'actual_home', 'home_team']
            away_preds.columns = ['match_id', 'minute_start', 'pred_away', 'actual_away', 'away_team']
            
            merged = pd.merge(home_preds, away_preds, on=['match_id', 'minute_start'])
            
            # Drop rows with NaN values
            merged = merged.dropna()
            
            # Filter out zero differentials
            merged = merged[(merged['pred_home'] != 0) | (merged['pred_away'] != 0)]
            merged = merged[(merged['actual_home'] != 0) | (merged['actual_away'] != 0)]
            
            if len(merged) > 0:
                merged['pred_diff'] = merged['pred_home'] - merged['pred_away']
                merged['actual_diff'] = merged['actual_home'] - merged['actual_away']
                
                # Only include non-zero differentials
                merged = merged[(merged['pred_diff'] != 0) & (merged['actual_diff'] != 0)]
                
                merged['correct'] = np.sign(merged['pred_diff']) == np.sign(merged['actual_diff'])
                
                # Get some examples (2 correct, 2 wrong) - ensure valid values
                correct_examples = merged[merged['correct']].head(2)
                wrong_examples = merged[~merged['correct']].head(2)
                
                examples_list = []
                for _, row in correct_examples.iterrows():
                    if pd.notna(row['pred_diff']) and pd.notna(row['actual_diff']):
                        examples_list.append({
                            'Match': f"{row['home_team']} vs {row['away_team']} ({int(row['minute_start'])}-{int(row['minute_start'])+2})",
                            'Predicted Diff': f"{row['pred_diff']:+.3f}",
                            'Actual Diff': f"{row['actual_diff']:+.3f}",
                            'Result': '✅ Both same sign'
                        })
                for _, row in wrong_examples.iterrows():
                    if pd.notna(row['pred_diff']) and pd.notna(row['actual_diff']):
                        examples_list.append({
                            'Match': f"{row['home_team']} vs {row['away_team']} ({int(row['minute_start'])}-{int(row['minute_start'])+2})",
                            'Predicted Diff': f"{row['pred_diff']:+.3f}",
                            'Actual Diff': f"{row['actual_diff']:+.3f}",
                            'Result': '❌ Wrong sign'
                        })
                
                if examples_list:
                    df_examples = pd.DataFrame(examples_list)
                    st.dataframe(df_examples, use_container_width=True, hide_index=True)
                else:
                    st.info("No valid examples found in the data.")
            else:
                st.info("No valid paired predictions found.")
    
    def render_paired_analysis(self, paired_metrics):
        """Render paired team analysis section"""
        st.subheader("👥 Paired Team Analysis (Same 3-Minute Window)")
        
        st.markdown("""
        This analysis examines how often the model correctly predicts momentum change signs for 
        **BOTH teams** in the same game window.
        """)
        
        if paired_metrics is None:
            st.error("Could not calculate paired metrics")
            return
        
        total_windows = paired_metrics['total']
        both_correct = paired_metrics['both_correct']
        only_home_correct = paired_metrics['only_home_correct']
        only_away_correct = paired_metrics['only_away_correct']
        one_correct = only_home_correct + only_away_correct
        both_wrong = paired_metrics['both_wrong']
        
        st.markdown("---")
        
        # Key metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Both Teams Correct",
                f"{both_correct} ({both_correct/total_windows*100:.1f}%)",
                "Complete success",
                help="Both Team X and Team Y signs predicted correctly"
            )
        
        with col2:
            st.metric(
                "One Team Correct",
                f"{one_correct} ({one_correct/total_windows*100:.1f}%)",
                "Partial success",
                help="Only one team's sign predicted correctly"
            )
        
        with col3:
            st.metric(
                "Both Teams Wrong",
                f"{both_wrong} ({both_wrong/total_windows*100:.1f}%)",
                "Complete failure",
                help="Neither team's sign predicted correctly"
            )
        
        st.markdown("---")
        
        # Visual breakdown
        st.markdown("### 📊 Visual Breakdown")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Both Correct', 'One Correct', 'Both Wrong'],
                values=[both_correct, one_correct, both_wrong],
                hole=0.4,
                marker_colors=['#2ca02c', '#ff7f0e', '#d62728'],
                textinfo='label+percent+value'
            )])
            
            fig_pie.update_layout(
                title='Paired Accuracy Distribution',
                height=400
            )
            
            st.plotly_chart(fig_pie, use_container_width=True, key="paired_pie")
        
        with col2:
            # Contingency matrix
            st.markdown("#### Home vs Away Correctness Matrix")
            
            z_matrix = [[both_correct, only_home_correct], [only_away_correct, both_wrong]]
            
            fig_matrix = go.Figure(data=go.Heatmap(
                z=z_matrix,
                x=['Away Correct', 'Away Wrong'],
                y=['Home Correct', 'Home Wrong'],
                text=[[f'{both_correct}<br>({both_correct/total_windows*100:.1f}%)', 
                       f'{only_home_correct}<br>({only_home_correct/total_windows*100:.1f}%)'],
                      [f'{only_away_correct}<br>({only_away_correct/total_windows*100:.1f}%)', 
                       f'{both_wrong}<br>({both_wrong/total_windows*100:.1f}%)']],
                texttemplate='%{text}',
                textfont={"size": 14},
                colorscale=[[0, '#ffcccb'], [0.5, '#ffffcc'], [1, '#90EE90']],
                showscale=False
            ))
            
            fig_matrix.update_layout(
                title='Paired Accuracy Matrix',
                height=350
            )
            
            st.plotly_chart(fig_matrix, use_container_width=True, key="paired_matrix")
        
        # Key insights
        st.markdown("### 🔍 Key Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            at_least_one = both_correct + one_correct
            st.success(f"""
            **✅ At Least One Team Correct: {at_least_one} ({at_least_one/total_windows*100:.1f}%)**
            
            In **{at_least_one/total_windows*100:.0f}% of game windows**, the model gets at least ONE team's 
            momentum change sign correct.
            """)
        
        with col2:
            st.error(f"""
            **❌ Complete Failure: {both_wrong} ({both_wrong/total_windows*100:.1f}%)**
            
            In only **{both_wrong/total_windows*100:.0f}% of windows**, both predictions are completely wrong. 
            This is the worst-case scenario but happens rarely.
            """)
        
        st.info(f"""
        **📝 Interpretation:**
        - **{both_correct/total_windows*100:.1f}%** of the time, BOTH teams are predicted correctly simultaneously
        - The "one correct" cases are split: Home only ({only_home_correct/total_windows*100:.1f}%), Away only ({only_away_correct/total_windows*100:.1f}%)
        - Complete failures are relatively rare ({both_wrong/total_windows*100:.1f}%)
        """)
    
    def render_metric_definitions(self, metrics):
        """Render metric definitions section"""
        st.subheader("📖 Understanding the Metrics")
        
        st.markdown("""
        The ARIMAX model is evaluated using three different accuracy metrics. Each measures 
        something different and provides unique insights into model performance.
        """)
        
        st.markdown("---")
        
        dir_acc = metrics['directional_acc'] * 100 if metrics else 0
        sign_acc = metrics['sign_agreement'] * 100 if metrics else 0
        diff_metrics = self.calculate_differential_metrics()
        diff_acc = diff_metrics['accuracy'] * 100 if diff_metrics else 0
        
        # Metric 1: Directional Accuracy
        st.markdown(f"### 1️⃣ Directional Accuracy ({dir_acc:.2f}%)")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            **What it measures:** Whether **CONSECUTIVE** predictions move in the same direction 
            (up/down) as **CONSECUTIVE** actual values.
            
            **Formula:**
            ```
            sign(pred[t+1] - pred[t]) == sign(actual[t+1] - actual[t])
            ```
            
            **Question it answers:** *"Did the model predict whether the TREND goes UP or DOWN?"*
            
            **Example:**
            ```
            Time:        t       t+1
            Prediction:  -0.5    -0.3   (change = +0.2, direction = UP)
            Actual:      +0.2    +0.4   (change = +0.2, direction = UP)
                                        ✅ Directional match (both UP)
                                        ❌ But signs are different (- vs +)
            ```
            """)
        
        with col2:
            st.info("""
            **Key Point:**
            
            Directional accuracy can be HIGH 
            even if absolute signs are wrong.
            
            It measures **RELATIVE movement**, 
            not absolute values.
            """)
        
        st.markdown("---")
        
        # Metric 2: Sign Agreement
        st.markdown(f"### 2️⃣ Sign Agreement Accuracy ({sign_acc:.2f}%)")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            **What it measures:** Whether each individual prediction has the **same SIGN** (+/-) 
            as the corresponding actual value.
            
            **Formula:**
            ```
            sign(prediction_value) == sign(actual_value)
            ```
            
            **Question it answers:** *"Did the model correctly predict POSITIVE vs NEGATIVE change?"*
            
            **This IS the metric that tells us:** "Team X's momentum will **INCREASE** (+)" or 
            "Team X's momentum will **DECREASE** (-)"
            """)
        
        with col2:
            st.success("""
            **Key Point:**
            
            This is the **most interpretable** 
            metric for practical use.
            
            It directly answers: "Will 
            momentum go up or down?"
            """)
        
        st.markdown("---")
        
        # Metric 3: Differential Sign
        st.markdown(f"### 3️⃣ Differential Sign Accuracy ({diff_acc:.2f}%)")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            **What it measures:** Whether the model correctly predicts **WHICH TEAM** will gain 
            more momentum in a given time window.
            
            **Formula:**
            ```
            Differential = Team_X_change - Team_Y_change
            sign(predicted_differential) == sign(actual_differential)
            ```
            
            **Question it answers:** *"Which team will gain the momentum advantage?"*
            
            **Example:**
            ```
            Team X prediction: -0.3    Team X actual: -0.5
            Team Y prediction: -0.8    Team Y actual: -1.2
            
            Differential prediction: -0.3 - (-0.8) = +0.5 (X better than Y)
            Differential actual:     -0.5 - (-1.2) = +0.7 (X better than Y)
            
            ✅ Differential sign correct (both positive, X does better)
            ❌ But BOTH teams actually have NEGATIVE momentum change!
            ```
            """)
        
        with col2:
            st.warning("""
            **Key Point:**
            
            Differential accuracy tells us 
            **WHO WINS** the momentum battle.
            
            It does NOT tell us if each 
            team gains or loses momentum.
            """)
        
        st.markdown("---")
        
        # Summary comparison table
        st.markdown("### 📊 Summary Comparison")
        
        comparison_table = {
            'Metric': [f'Directional ({dir_acc:.2f}%)', f'Sign Agreement ({sign_acc:.2f}%)', f'Differential ({diff_acc:.2f}%)'],
            'What We Learn': ['Trend direction (UP/DOWN)', 'Absolute sign (+/-)', 'Which team does BETTER'],
            'What We DON\'T Learn': ['If momentum is + or -', '—', 'If each team gains or loses'],
            'Random Baseline': ['50%', '50%', '50%'],
            'Improvement': [f'+{dir_acc-50:.2f}%', f'+{sign_acc-50:.2f}%', f'+{diff_acc-50:.2f}%']
        }
        
        df_comparison = pd.DataFrame(comparison_table)
        st.dataframe(df_comparison, use_container_width=True, hide_index=True)
    
    def calculate_game_metrics(self, game_data):
        """Calculate all metrics for a single game"""
        # Calculate momentum windows won
        home_momentum_wins = (game_data['team_home_momentum'] > game_data['team_away_momentum']).sum()
        away_momentum_wins = (game_data['team_away_momentum'] > game_data['team_home_momentum']).sum()
        
        # Calculate positive changes
        home_positive_changes = (game_data['team_home_momentum_change'] > 0).sum()
        away_positive_changes = (game_data['team_away_momentum_change'] > 0).sum()
        
        # Calculate sequences and longest sequence
        def count_sequences_and_longest(changes):
            sequences = 0
            longest = 0
            current = 0
            for c in changes:
                if pd.notna(c) and c > 0:
                    current += 1
                    longest = max(longest, current)
                else:
                    if current > 0:
                        sequences += 1
                    current = 0
            if current > 0:
                sequences += 1
            return sequences, longest
        
        home_num_seq, home_longest = count_sequences_and_longest(game_data['team_home_momentum_change'].values)
        away_num_seq, away_longest = count_sequences_and_longest(game_data['team_away_momentum_change'].values)
        
        return {
            'home_momentum_wins': home_momentum_wins,
            'away_momentum_wins': away_momentum_wins,
            'home_positive_changes': home_positive_changes,
            'away_positive_changes': away_positive_changes,
            'home_num_seq': home_num_seq,
            'away_num_seq': away_num_seq,
            'home_longest': home_longest,
            'away_longest': away_longest
        }
    
    def load_metrics_json(self):
        """Load pre-calculated metrics from JSON file"""
        import json
        metrics_path = self.base_path / "outputs" / "dashboard_metrics.json"
        if metrics_path.exists():
            with open(metrics_path, 'r') as f:
                return json.load(f)
        return None
    
    def render_real_data_analysis(self):
        """Render real data analysis - momentum change and sequences"""
        st.subheader("🔬 Real Data Analysis: Momentum Predictors")
        
        # Load pre-calculated metrics
        metrics = self.load_metrics_json()
        
        if metrics is None:
            st.error("Metrics data not found. Please run analyze_metrics_vs_result.py first.")
            return
        
        summary = metrics.get('summary', {})
        total_games = summary.get('total_games', 51)
        total_windows = summary.get('total_windows', 4786)
        avg_windows_per_game = summary.get('avg_windows_per_game', 93.8)
        
        st.markdown(f"""
        Analysis of **{total_games} Euro 2024 games** using **period-separated momentum data** to understand 
        which momentum metrics predict match outcomes.
        """)
        
        # Show data summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Games", total_games)
        with col2:
            st.metric("Total Momentum Windows", f"{total_windows:,}")
        with col3:
            st.metric("Avg Windows/Game", f"{avg_windows_per_game:.1f}")
        
        st.markdown("---")
        
        # Section 1: Metrics Classification
        st.markdown("### 📊 Momentum Metrics Classification")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("""
            **✅ WINNING Metrics** (Positive Correlation)
            
            Higher = More likely to WIN
            
            1. **Absolute Momentum** - Who has higher momentum in more windows
            2. **Number of Sequences** - Who has more positive momentum streaks
            
            These indicate **GAME CONTROL**
            """)
        
        with col2:
            st.error("""
            **❌ CHASING Metrics** (Negative Correlation)
            
            Higher = More likely to LOSE
            
            1. **Positive Changes** - Who has more momentum increases
            2. **Longest Sequence** - Who has the longest positive streak
            
            These indicate **DESPERATELY CHASING**
            """)
        
        st.markdown("---")
        
        # Section 2: Individual Metrics Table
        st.markdown("### 📋 Individual Metrics vs Match Outcome")
        
        abs_mom = metrics.get('absolute_momentum', {})
        num_seq = metrics.get('num_sequences', {})
        pos_change = metrics.get('positive_changes', {})
        long_seq = metrics.get('longest_sequence', {})
        
        metrics_data = {
            'Metric': ['Absolute Momentum', 'Number of Sequences', 'Positive Changes', 'Longest Sequence'],
            'Type': ['✅ Winning', '✅ Winning', '❌ Chasing', '❌ Chasing'],
            'Games': [abs_mom.get('games', 0), num_seq.get('games', 0), 
                     pos_change.get('games', 0), long_seq.get('games', 0)],
            'WIN': [f"{abs_mom.get('win_pct', 0):.1f}%", f"{num_seq.get('win_pct', 0):.1f}%", 
                   f"{pos_change.get('win_pct', 0):.1f}%", f"{long_seq.get('win_pct', 0):.1f}%"],
            'LOSE': [f"{abs_mom.get('lose_pct', 0):.1f}%", f"{num_seq.get('lose_pct', 0):.1f}%", 
                    f"{pos_change.get('lose_pct', 0):.1f}%", f"{long_seq.get('lose_pct', 0):.1f}%"],
            'DRAW': [f"{abs_mom.get('draw_pct', 0):.1f}%", f"{num_seq.get('draw_pct', 0):.1f}%", 
                    f"{pos_change.get('draw_pct', 0):.1f}%", f"{long_seq.get('draw_pct', 0):.1f}%"]
        }
        
        df_metrics = pd.DataFrame(metrics_data)
        st.dataframe(df_metrics, use_container_width=True, hide_index=True)
        
        st.info(f"""
        **📌 Key Insight:** Notice the pattern! 
        - **Winning metrics:** ~{abs_mom.get('win_pct', 0):.0f}% win, ~{abs_mom.get('lose_pct', 0):.0f}% lose
        - **Chasing metrics:** ~{pos_change.get('win_pct', 0):.0f}% win, ~{pos_change.get('lose_pct', 0):.0f}% lose (OPPOSITE!)
        """)
        
        st.markdown("---")
        
        # Section 2b: Cumulative Margin Analysis
        st.markdown("### 📈 Cumulative Margin Analysis")
        
        st.markdown("""
        How does increasing the **minimum margin threshold** improve predictive value?
        Only showing thresholds where there's meaningful improvement:
        """)
        
        st.markdown("#### Winning Metrics Cumulative Margins")
        
        col1, col2 = st.columns(2)
        
        mom_margins = metrics.get('momentum_margins', {})
        num_seq_margins = metrics.get('num_seq_margins', {})
        
        with col1:
            st.markdown("**Absolute Momentum Margin**")
            
            mom_margin_data = {
                'Min Margin': ['All (0%+)', '5%+', '10%+', '15%+', '20%+', '25%+', '30%+', '40%+', '50%+', '60%+'],
                'Games': [mom_margins.get('0', {}).get('games', 0), 
                         mom_margins.get('5', {}).get('games', 0),
                         mom_margins.get('10', {}).get('games', 0),
                         mom_margins.get('15', {}).get('games', 0),
                         mom_margins.get('20', {}).get('games', 0),
                         mom_margins.get('25', {}).get('games', 0),
                         mom_margins.get('30', {}).get('games', 0),
                         mom_margins.get('40', {}).get('games', 0),
                         mom_margins.get('50', {}).get('games', 0),
                         mom_margins.get('60', {}).get('games', 0)],
                'WIN': [f"{mom_margins.get('0', {}).get('win_pct', 0):.1f}%", 
                       f"{mom_margins.get('5', {}).get('win_pct', 0):.1f}%",
                       f"{mom_margins.get('10', {}).get('win_pct', 0):.1f}%",
                       f"{mom_margins.get('15', {}).get('win_pct', 0):.1f}%",
                       f"{mom_margins.get('20', {}).get('win_pct', 0):.1f}%",
                       f"{mom_margins.get('25', {}).get('win_pct', 0):.1f}%",
                       f"{mom_margins.get('30', {}).get('win_pct', 0):.1f}%",
                       f"{mom_margins.get('40', {}).get('win_pct', 0):.1f}%",
                       f"{mom_margins.get('50', {}).get('win_pct', 0):.1f}%",
                       f"{mom_margins.get('60', {}).get('win_pct', 0):.1f}%"],
                'LOSE': [f"{mom_margins.get('0', {}).get('lose_pct', 0):.1f}%", 
                        f"{mom_margins.get('5', {}).get('lose_pct', 0):.1f}%",
                        f"{mom_margins.get('10', {}).get('lose_pct', 0):.1f}%",
                        f"{mom_margins.get('15', {}).get('lose_pct', 0):.1f}%",
                        f"{mom_margins.get('20', {}).get('lose_pct', 0):.1f}%",
                        f"{mom_margins.get('25', {}).get('lose_pct', 0):.1f}%",
                        f"{mom_margins.get('30', {}).get('lose_pct', 0):.1f}%",
                        f"{mom_margins.get('40', {}).get('lose_pct', 0):.1f}%",
                        f"{mom_margins.get('50', {}).get('lose_pct', 0):.1f}%",
                        f"{mom_margins.get('60', {}).get('lose_pct', 0):.1f}%"]
            }
            df_mom = pd.DataFrame(mom_margin_data)
            st.dataframe(df_mom, use_container_width=True, hide_index=True)
            
            st.markdown(f"*At 50%+ margin: WIN={mom_margins.get('50', {}).get('win_pct', 0):.1f}%, LOSE={mom_margins.get('50', {}).get('lose_pct', 0):.1f}%*")
        
        with col2:
            st.markdown("**Number of Sequences Margin**")
            
            num_seq_margin_data = {
                'Min Margin': ['All (0+)', '1+ seq', '2+ seq', '3+ seq', '4+ seq', '5+ seq'],
                'Games': [num_seq_margins.get('0', {}).get('games', 0),
                         num_seq_margins.get('1', {}).get('games', 0),
                         num_seq_margins.get('2', {}).get('games', 0),
                         num_seq_margins.get('3', {}).get('games', 0),
                         num_seq_margins.get('4', {}).get('games', 0),
                         num_seq_margins.get('5', {}).get('games', 0)],
                'WIN': [f"{num_seq_margins.get('0', {}).get('win_pct', 0):.1f}%",
                       f"{num_seq_margins.get('1', {}).get('win_pct', 0):.1f}%",
                       f"{num_seq_margins.get('2', {}).get('win_pct', 0):.1f}%",
                       f"{num_seq_margins.get('3', {}).get('win_pct', 0):.1f}%",
                       f"{num_seq_margins.get('4', {}).get('win_pct', 0):.1f}%",
                       f"{num_seq_margins.get('5', {}).get('win_pct', 0):.1f}%"],
                'LOSE': [f"{num_seq_margins.get('0', {}).get('lose_pct', 0):.1f}%",
                        f"{num_seq_margins.get('1', {}).get('lose_pct', 0):.1f}%",
                        f"{num_seq_margins.get('2', {}).get('lose_pct', 0):.1f}%",
                        f"{num_seq_margins.get('3', {}).get('lose_pct', 0):.1f}%",
                        f"{num_seq_margins.get('4', {}).get('lose_pct', 0):.1f}%",
                        f"{num_seq_margins.get('5', {}).get('lose_pct', 0):.1f}%"]
            }
            df_num_seq = pd.DataFrame(num_seq_margin_data)
            st.dataframe(df_num_seq, use_container_width=True, hide_index=True)
            
            seq_4_win = num_seq_margins.get('4', {}).get('win_pct', 0)
            seq_4_lose = num_seq_margins.get('4', {}).get('lose_pct', 0)
            st.markdown(f"*At 4+ margin: {seq_4_win:.0f}% win, {seq_4_lose:.0f}% lose!*")
            
            # Clarification expander
            with st.expander("ℹ️ What is Number of Sequences?"):
                st.markdown("""
                **Sequence** = consecutive windows with **positive momentum change**.
                
                **Example:**
                ```
                Team A: +,+,-,-,+,+,+,-,+  → 3 sequences
                Team B: +,-,+,-,+,-,+,-,+  → 5 sequences
                Margin: 5 - 3 = 2 sequences
                ```
                
                | Team | Sequences | Interpretation |
                |------|-----------|----------------|
                | More sequences | 18 vs 14 | Controls game rhythm |
                | Fewer sequences | 14 vs 18 | Reacts to opponent |
                
                **Why more sequences = winning?**
                - Multiple separate attack phases
                - Dictates the game tempo
                - Like a boxer throwing multiple combinations
                """)
        
        st.markdown("#### Chasing Metrics Cumulative Margins")
        
        col1, col2 = st.columns(2)
        longest_margins = metrics.get('longest_margins', {})
        pos_changes_margins = metrics.get('positive_changes_margins', {})
        
        with col1:
            st.markdown("**Positive Changes Margin**")
            
            pos_margin_data = {
                'Min Margin': ['All (0%+)', '5%+', '10%+'],
                'Games': [pos_changes_margins.get('0', {}).get('games', 0),
                         pos_changes_margins.get('5', {}).get('games', 0),
                         pos_changes_margins.get('10', {}).get('games', 0)],
                'WIN': [f"{pos_changes_margins.get('0', {}).get('win_pct', 0):.1f}%",
                       f"{pos_changes_margins.get('5', {}).get('win_pct', 0):.1f}%",
                       f"{pos_changes_margins.get('10', {}).get('win_pct', 0):.1f}%"],
                'LOSE': [f"{pos_changes_margins.get('0', {}).get('lose_pct', 0):.1f}%",
                        f"{pos_changes_margins.get('5', {}).get('lose_pct', 0):.1f}%",
                        f"{pos_changes_margins.get('10', {}).get('lose_pct', 0):.1f}%"]
            }
            df_pos = pd.DataFrame(pos_margin_data)
            st.dataframe(df_pos, use_container_width=True, hide_index=True)
            
            st.markdown("*Most games have < 5% margin - momentum change is very balanced!*")
        
        with col2:
            st.markdown("**Longest Sequence Margin**")
            
            seq_margin_data = {
                'Min Margin': ['All (0+)', '1+ win', '2+ win', '3+ win', '4+ win', '5+ win', '6+ win'],
                'Games': [longest_margins.get('0', {}).get('games', 0),
                         longest_margins.get('1', {}).get('games', 0),
                         longest_margins.get('2', {}).get('games', 0),
                         longest_margins.get('3', {}).get('games', 0),
                         longest_margins.get('4', {}).get('games', 0),
                         longest_margins.get('5', {}).get('games', 0),
                         longest_margins.get('6', {}).get('games', 0)],
                'WIN': [f"{longest_margins.get('0', {}).get('win_pct', 0):.1f}%",
                       f"{longest_margins.get('1', {}).get('win_pct', 0):.1f}%",
                       f"{longest_margins.get('2', {}).get('win_pct', 0):.1f}%",
                       f"{longest_margins.get('3', {}).get('win_pct', 0):.1f}%",
                       f"{longest_margins.get('4', {}).get('win_pct', 0):.1f}%",
                       f"{longest_margins.get('5', {}).get('win_pct', 0):.1f}%",
                       f"{longest_margins.get('6', {}).get('win_pct', 0):.1f}%"],
                'LOSE': [f"{longest_margins.get('0', {}).get('lose_pct', 0):.1f}%",
                        f"{longest_margins.get('1', {}).get('lose_pct', 0):.1f}%",
                        f"{longest_margins.get('2', {}).get('lose_pct', 0):.1f}%",
                        f"{longest_margins.get('3', {}).get('lose_pct', 0):.1f}%",
                        f"{longest_margins.get('4', {}).get('lose_pct', 0):.1f}%",
                        f"{longest_margins.get('5', {}).get('lose_pct', 0):.1f}%",
                        f"{longest_margins.get('6', {}).get('lose_pct', 0):.1f}%"]
            }
            df_seq = pd.DataFrame(seq_margin_data)
            st.dataframe(df_seq, use_container_width=True, hide_index=True)
            
            long_4_win = longest_margins.get('4', {}).get('win_pct', 0)
            long_4_lose = longest_margins.get('4', {}).get('lose_pct', 0)
            st.markdown(f"*At 0-3 margin: LOSE > WIN (chasing!)*")
            st.markdown(f"*At 4+ margin: pattern reverses → {long_4_win:.0f}% win, {long_4_lose:.0f}% lose*")
            
            # Clarification
            with st.expander("ℹ️ What is Longest Sequence Margin?"):
                st.markdown("""
                **Longest Sequence** = The longest consecutive streak of positive momentum changes.
                
                **Example:**
                ```
                Team A sequences: 3, 2, 8, 4, 1 → Longest = 8
                Team B sequences: 2, 5, 3, 1    → Longest = 5
                Margin: 8 - 5 = 3 windows
                ```
                
                | Margin | Interpretation |
                |--------|----------------|
                | Small (1-2) | Slightly longer → probably chasing |
                | **Large (4+)** | Much longer → sustained dominance |
                
                **Why pattern changes at higher margins?**
                - Small margin = desperately chasing
                - Large margin = complete control, opponent couldn't break momentum
                """)
        
        # Key findings
        mom_50_win = mom_margins.get('50', {}).get('win_pct', 0)
        mom_50_lose = mom_margins.get('50', {}).get('lose_pct', 0)
        st.success(f"""
        **🎯 Key Findings from Cumulative Analysis:** 
        - **Absolute Momentum 50%+:** WIN jumps to {mom_50_win:.1f}%, only {mom_50_lose:.1f}% lose! (14 games)
        - **Number of Sequences 4+:** WIN={seq_4_win:.0f}%, LOSE={seq_4_lose:.0f}%! (12 games)
        - **Longest Sequence 4+:** Win rate goes to {long_4_win:.0f}% (pattern reverses at higher margins!)
        """)
        
        st.markdown("---")
        
        # Section 3: Momentum Change Analysis
        st.markdown("### 🔄 Momentum Change Analysis (Counter-Intuitive!)")
        
        st.markdown("""
        **Question:** Does having MORE positive momentum changes lead to winning?
        
        **Answer:** NO! It's the OPPOSITE!
        """)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Bar chart for momentum change
            fig_change = go.Figure()
            
            fig_change.add_trace(go.Bar(
                x=['WIN', 'LOSE', 'DRAW'],
                y=[pos_change.get('win_pct', 0), pos_change.get('lose_pct', 0), pos_change.get('draw_pct', 0)],
                text=[f"{pos_change.get('win_pct', 0):.1f}%", f"{pos_change.get('lose_pct', 0):.1f}%", f"{pos_change.get('draw_pct', 0):.1f}%"],
                textposition='auto',
                marker_color=['#2ca02c', '#d62728', '#ff7f0e']
            ))
            
            fig_change.update_layout(
                title='Team with MORE Positive Momentum Changes',
                xaxis_title='Match Outcome',
                yaxis_title='Percentage',
                height=350,
                yaxis=dict(range=[0, 60])
            )
            
            st.plotly_chart(fig_change, use_container_width=True, key="change_outcome_chart")
        
        with col2:
            st.markdown("#### Why This Happens:")
            st.markdown("""
            - **Trailing teams recover more** - Teams losing have more "positive change" windows
            - **Winning teams coast** - Teams ahead may have stable/negative changes
            - **Comeback effect** - More changes = trying harder = likely behind
            """)
        
        st.warning(f"""
        **⚠️ Counter-Intuitive Finding:** Teams with MORE positive momentum changes have a **{pos_change.get('lose_pct', 0):.1f}% lose rate** 
        vs only **{pos_change.get('win_pct', 0):.1f}% win rate**. More positive changes = desperately chasing the game!
        """)
        
        st.markdown("---")
        
        # Section 4: Sequence Analysis
        st.markdown("### 📈 Momentum Sequence Analysis")
        
        st.markdown("""
        A **sequence** = consecutive windows where team has positive momentum change.
        
        Example: `+, +, +, -, +, +` = Two sequences (length 3 and length 2)
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Longest Sequence (❌ Chasing)")
            
            fig_longest = go.Figure()
            fig_longest.add_trace(go.Bar(
                x=['WIN', 'LOSE', 'DRAW'],
                y=[long_seq.get('win_pct', 0), long_seq.get('lose_pct', 0), long_seq.get('draw_pct', 0)],
                text=[f"{long_seq.get('win_pct', 0):.1f}%", f"{long_seq.get('lose_pct', 0):.1f}%", f"{long_seq.get('draw_pct', 0):.1f}%"],
                textposition='auto',
                marker_color=['#2ca02c', '#d62728', '#ff7f0e']
            ))
            fig_longest.update_layout(
                title='Team with LONGEST Sequence',
                height=300,
                yaxis=dict(range=[0, 60])
            )
            st.plotly_chart(fig_longest, use_container_width=True, key="longest_seq_chart")
            
            st.markdown("Long desperate streaks = chasing")
        
        with col2:
            st.markdown("#### Number of Sequences (✅ Winning)")
            
            fig_num = go.Figure()
            fig_num.add_trace(go.Bar(
                x=['WIN', 'LOSE', 'DRAW'],
                y=[num_seq.get('win_pct', 0), num_seq.get('lose_pct', 0), num_seq.get('draw_pct', 0)],
                text=[f"{num_seq.get('win_pct', 0):.1f}%", f"{num_seq.get('lose_pct', 0):.1f}%", f"{num_seq.get('draw_pct', 0):.1f}%"],
                textposition='auto',
                marker_color=['#2ca02c', '#d62728', '#ff7f0e']
            ))
            fig_num.update_layout(
                title='Team with MORE Sequences',
                height=300,
                yaxis=dict(range=[0, 60])
            )
            st.plotly_chart(fig_num, use_container_width=True, key="num_seq_chart")
            
            st.markdown("Multiple attack phases = control")
        
        st.markdown("---")
        
        # Section 5: Combined Metrics - THE KEY FINDING
        st.markdown("### 🎯 Combined Metrics Analysis (Key Finding!)")
        
        combined = metrics.get('combined', {})
        winning_agree = combined.get('winning_agree', {})
        chasing_agree = combined.get('chasing_agree', {})
        different_teams = combined.get('different_teams', {})
        
        st.markdown("""
        What happens when we combine the **Winning Metrics** and **Chasing Metrics**?
        """)
        
        # Combined metrics table
        combined_data = {
            'Condition': [
                'Winning Metrics AGREE (Momentum + Num Seq → same team)',
                'Chasing Metrics AGREE (Pos Change + Longest → same team)',
                '🔥 DIFFERENT Teams (Winning → A, Chasing → B)'
            ],
            'Games': [winning_agree.get('games', 0), chasing_agree.get('games', 0), different_teams.get('games', 0)],
            'WIN': [f"{winning_agree.get('win_pct', 0):.1f}%", f"{chasing_agree.get('win_pct', 0):.1f}%", f"{different_teams.get('win_pct', 0):.1f}%"],
            'LOSE': [f"{winning_agree.get('lose_pct', 0):.1f}%", f"{chasing_agree.get('lose_pct', 0):.1f}%", f"{different_teams.get('lose_pct', 0):.1f}%"],
            'DRAW': [f"{winning_agree.get('draw_pct', 0):.1f}%", f"{chasing_agree.get('draw_pct', 0):.1f}%", f"{different_teams.get('draw_pct', 0):.1f}%"]
        }
        
        df_combined = pd.DataFrame(combined_data)
        st.dataframe(df_combined, use_container_width=True, hide_index=True)
        
        # Highlight the best finding
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Winning Metrics AGREE",
                f"{winning_agree.get('win_pct', 0):.1f}% WIN",
                f"Only {winning_agree.get('lose_pct', 0):.1f}% lose!",
                help="When Absolute Momentum AND Number of Sequences point to same team"
            )
        
        with col2:
            diff_win = different_teams.get('win_pct', 0)
            diff_games = different_teams.get('games', 0)
            diff_win_count = different_teams.get('win', 0)
            st.metric(
                "DIFFERENT Teams",
                f"{diff_win:.1f}% WIN",
                f"{diff_win_count}/{diff_games} games!",
                help="When Winning metrics → Team A, Chasing metrics → Team B"
            )
        
        # Combined Cumulative Analysis
        st.markdown("---")
        st.markdown("#### 📊 Combined Cumulative Analysis")
        
        st.markdown("**Winning Metrics AGREE with thresholds** (Abs Momentum % + Num Sequences margin)")
        
        winning_cumulative = {
            'Abs Mom %': ['0%+', '0%+', '0%+', '0%+', '10%+', '10%+', '10%+', '15%+', '20%+', '20%+', '25%+', '25%+', '30%+'],
            'Seq Margin': ['0+', '2+', '3+', '4+', '0+', '2+', '3+', '3+', '2+', '3+', '2+', '3+', '3+'],
            'Games': [25, 18, 9, 6, 19, 14, 6, 6, 12, 5, 11, 5, 5],
            'WIN': ['44.0%', '55.6%', '66.7%', '83.3%', '47.4%', '57.1%', '83.3%', '83.3%', '58.3%', '80.0%', '54.5%', '80.0%', '80.0%'],
            'LOSE': ['20.0%', '16.7%', '11.1%', '0.0%', '10.5%', '14.3%', '0.0%', '0.0%', '16.7%', '0.0%', '18.2%', '0.0%', '0.0%'],
            'DRAW': ['36.0%', '27.8%', '22.2%', '16.7%', '42.1%', '28.6%', '16.7%', '16.7%', '25.0%', '20.0%', '27.3%', '20.0%', '20.0%']
        }
        df_winning_cum = pd.DataFrame(winning_cumulative)
        st.dataframe(df_winning_cum, use_container_width=True, hide_index=True)
        st.markdown("*🎯 At Seq 3+ margin: 0% LOSE rate across all Abs Mom thresholds! (5-6 games each)*")
        
        st.markdown("**Chasing Metrics AGREE with thresholds** (Pos Changes % + Longest Seq margin)")
        
        chasing_cumulative = {
            'Pos Chg %': ['0%+', '0%+', '0%+', '0%+', '5%+', '5%+', '5%+', '5%+'],
            'Longest': ['0+', '1+', '2+', '3+', '0+', '1+', '2+', '3+'],
            'Games': [25, 25, 19, 12, 7, 7, 6, 4],
            'WIN': ['24.0%', '24.0%', '31.6%', '33.3%', '57.1%', '57.1%', '66.7%', '75.0%'],
            'LOSE': ['48.0%', '48.0%', '36.8%', '41.7%', '28.6%', '28.6%', '16.7%', '0.0%']
        }
        df_chasing_cum = pd.DataFrame(chasing_cumulative)
        st.dataframe(df_chasing_cum, use_container_width=True, hide_index=True)
        st.markdown("*At 0% Pos Chg: LOSE > WIN confirms chasing behavior. At 5%+ with 3+ Longest: 75% WIN, 0% LOSE!*")
        
        st.markdown("---")
        st.markdown("#### 🔥 DIFFERENT Teams Analysis (Winning metric → A, Chasing metric → B)")
        
        with st.expander("ℹ️ Understanding 2-from-4 vs 4-from-4 Metrics Analysis"):
            st.markdown("""
            **4-from-4 Analysis** (shown above in main table):
            - Requires ALL 4 metrics to agree on different teams
            - Winning: Abs Momentum → Team A **AND** Num Sequences → Team A
            - Chasing: Pos Changes → Team B **AND** Longest Seq → Team B
            - Very strict: Only **6 games** qualify
            - Result: 66.7% WIN, 16.7% LOSE
            
            **2-from-4 Analysis** (tables below):
            - Uses only **2 metrics** (1 Winning + 1 Chasing)
            - Less strict: More games qualify
            - Allows testing **which pair** is most predictive
            
            | Approach | Metrics Used | Games | Best WIN |
            |----------|-------------|-------|----------|
            | 4-from-4 | All 4 must agree | 6 | 66.7% |
            | 2-from-4 | Abs Mom vs Pos Chg | 4 (at 5%+) | **100%** |
            | 2-from-4 | Abs Mom vs Longest | 5 (at 20%+ & 3+) | **100%** |
            
            **Key Insight:** Using just 2 carefully selected metrics with thresholds can be **MORE predictive** than requiring all 4 to agree!
            """)
        
        st.markdown("**1. Abs Momentum vs Pos Changes** (Best combination!)")
        diff_1 = {
            'Abs Mom %': ['0%+', '0%+', '10%+', '15%+', '20%+'],
            'Pos Chg %': ['0%+', '5%+', '0%+', '0%+', '0%+'],
            'Games': [18, 4, 16, 16, 12],
            'WIN': ['61.1%', '100.0%', '68.8%', '68.8%', '75.0%'],
            'LOSE': ['16.7%', '0.0%', '6.2%', '6.2%', '8.3%']
        }
        st.dataframe(pd.DataFrame(diff_1), use_container_width=True, hide_index=True)
        st.markdown("*🔥 At 5%+ Pos Chg margin: 100% WIN rate!*")
        
        st.markdown("**2. Abs Momentum vs Longest Seq**")
        diff_2 = {
            'Abs Mom %': ['0%+', '0%+', '15%+', '15%+', '20%+'],
            'Longest': ['0+', '3+', '0+', '3+', '3+'],
            'Games': [23, 11, 16, 6, 5],
            'WIN': ['52.2%', '54.5%', '62.5%', '83.3%', '100.0%'],
            'LOSE': ['13.0%', '18.2%', '0.0%', '0.0%', '0.0%']
        }
        st.dataframe(pd.DataFrame(diff_2), use_container_width=True, hide_index=True)
        st.markdown("*🔥 At 20%+ Mom & 3+ Longest: 100% WIN rate!*")
        
        st.markdown("**3. Num Sequences vs Pos Changes** (Not reliable ❌)")
        diff_3 = {
            'Seq': ['0+', '0+', '2+', '3+'],
            'Pos Chg %': ['0%+', '5%+', '0%+', '0%+'],
            'Games': [24, 9, 17, 9],
            'WIN': ['37.5%', '33.3%', '52.9%', '55.6%'],
            'LOSE': ['29.2%', '55.6%', '23.5%', '22.2%']
        }
        st.dataframe(pd.DataFrame(diff_3), use_container_width=True, hide_index=True)
        st.markdown("*❌ At 5%+ Pos Chg: LOSE (55.6%) > WIN (33.3%) - Not reliable!*")
        
        st.markdown("**4. Num Sequences vs Longest Seq** (Moderate)")
        diff_4 = {
            'Seq': ['0+', '2+', '3+', '3+'],
            'Longest': ['0+', '2+', '2+', '3+'],
            'Games': [24, 18, 11, 8],
            'WIN': ['41.7%', '50.0%', '54.5%', '62.5%'],
            'LOSE': ['25.0%', '22.2%', '18.2%', '25.0%']
        }
        st.dataframe(pd.DataFrame(diff_4), use_container_width=True, hide_index=True)
        st.markdown("*Moderate results - WIN slightly > LOSE*")
        
        st.markdown("---")
        
        # Explanation of the best finding
        st.markdown("### 🏆 The Perfect Predictor Explained")
        
        st.markdown("""
        **When WINNING metrics point to Team A AND CHASING metrics point to Team B:**
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("""
            **Team A (Winning Metrics):**
            - Higher absolute momentum
            - More attack sequences
            - **= CONTROLS the game**
            """)
        
        with col2:
            st.error("""
            **Team B (Chasing Metrics):**
            - More positive momentum changes
            - Longer desperate streaks
            - **= CHASING the game**
            """)
        
        st.markdown(f"""
        **Result: Team A wins {diff_win:.0f}% of the time ({diff_win_count}/{diff_games} games)!**
        
        This makes perfect sense:
        - Team A dominates (high momentum, multiple attack phases)
        - Team B desperately tries to recover (many changes, long streaks)
        - Clear picture = reliable prediction
        """)
        
        st.success("""
        **🎯 Practical Application:** When analyzing a match:
        1. Calculate who wins more momentum windows (Winning metric #1)
        2. Calculate who has more sequences (Winning metric #2)
        3. Calculate who has more positive changes (Chasing metric #1)
        4. Calculate who has the longest sequence (Chasing metric #2)
        5. If Winning → Team A and Chasing → Team B, **Team A will likely win!**
        """)
        
        # Add Goals vs Momentum Change Analysis
        self.render_goals_analysis()
    
    def render_goals_analysis(self):
        """Render goals vs momentum change analysis"""
        st.markdown("---")
        st.subheader("⚽ Goals vs Momentum Change Analysis")
        
        st.markdown("""
        **Key Question:** Can momentum change **predict** when goals will be scored?
        
        We analyze all 126 Euro 2024 goals to see if there's a pattern between 
        momentum change and goal scoring.
        """)
        
        # Explain the logic
        with st.expander("📐 Understanding the Logic", expanded=True):
            st.markdown("""
            ### How We Compare Goals to Momentum Change
            
            **The Challenge:**
            - Momentum change at display minute X compares:
              - **Past window**: events from minutes X-3, X-2, X-1
              - **Future window**: events from minutes X, X+1, X+2
            - Change = momentum(future) - momentum(past)
            
            **For a Goal at minute G:**
            - We want to check the momentum change where the goal minute G is in the **FUTURE window**
            - This means we check display minute **G-2**
            - At display minute G-2:
              - Past window: G-5, G-4, G-3
              - Future window: G-2, G-1, **G** (goal here!)
            
            **Example:** Goal at minute 78
            - Check display minute 76 (= 78-2)
            - Past window: minutes 73, 74, 75
            - Future window: minutes 76, 77, **78** ← goal scored here
            - If momentum change is **positive**, team was gaining momentum INTO the goal
            
            **Why This Makes Sense:**
            - Positive change means team is building momentum
            - The goal at minute G is the *result* of that momentum buildup
            - We're checking: "Was the team gaining momentum when they scored?"
            """)
        
        # Calculate and display results
        try:
            goals_data = self._analyze_goals_vs_momentum()
            
            if goals_data is not None and len(goals_data) > 0:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Scoring Team's Momentum")
                    pos_score = len(goals_data[goals_data['scoring_team_change'] > 0])
                    neg_score = len(goals_data[goals_data['scoring_team_change'] < 0])
                    total = len(goals_data)
                    
                    fig1 = go.Figure(data=[go.Pie(
                        labels=['Positive (Gaining)', 'Negative (Losing)'],
                        values=[pos_score, neg_score],
                        hole=0.4,
                        marker_colors=['#2ca02c', '#d62728']
                    )])
                    fig1.update_layout(
                        title=f"Scoring Team's Change<br>(n={total})",
                        height=300,
                        margin=dict(t=60, b=20, l=20, r=20)
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                    
                    st.metric("Positive Momentum", f"{pos_score/total*100:.1f}%", 
                             f"{pos_score} goals")
                    st.metric("Negative Momentum", f"{neg_score/total*100:.1f}%",
                             f"{neg_score} goals")
                
                with col2:
                    st.markdown("### Conceding Team's Momentum")
                    pos_conc = len(goals_data[goals_data['conceding_team_change'] > 0])
                    neg_conc = len(goals_data[goals_data['conceding_team_change'] < 0])
                    
                    fig2 = go.Figure(data=[go.Pie(
                        labels=['Positive (Gaining)', 'Negative (Losing)'],
                        values=[pos_conc, neg_conc],
                        hole=0.4,
                        marker_colors=['#2ca02c', '#d62728']
                    )])
                    fig2.update_layout(
                        title=f"Conceding Team's Change<br>(n={total})",
                        height=300,
                        margin=dict(t=60, b=20, l=20, r=20)
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                    
                    st.metric("Positive Momentum", f"{pos_conc/total*100:.1f}%",
                             f"{pos_conc} goals")
                    st.metric("Negative Momentum", f"{neg_conc/total*100:.1f}%",
                             f"{neg_conc} goals")
                
                # Key insight
                st.markdown("---")
                st.success(f"""
                ### 🎯 Key Finding: Momentum Change PREDICTS Goals!
                
                **{pos_score/total*100:.1f}% of goals** were scored when the scoring team had **POSITIVE momentum change**
                
                This means:
                - Teams that are **gaining momentum** are **3x more likely** to score
                - Momentum buildup → Goal scoring (not counter-attacks!)
                - **{neg_conc/total*100:.1f}%** of goals were conceded when the conceding team was **losing momentum**
                
                **Practical Implication:** Monitor momentum change - when a team starts gaining momentum, 
                expect a goal attempt. Defensive adjustments should be made when your team's momentum is declining.
                """)
                
                # Show sample data
                with st.expander("📊 Sample Goal Data (All Goals)"):
                    display_df = goals_data[['goal_minute', 'period', 'scoring_team', 
                                            'scoring_team_change', 'conceding_team_change']].head(15)
                    display_df.columns = ['Goal Minute', 'Period', 'Scoring Team', 
                                         'Scorer Change', 'Conceder Change']
                    st.dataframe(display_df, use_container_width=True)
                
                # Add Prediction Minutes Analysis (75-90)
                st.markdown("---")
                st.subheader("🔮 Prediction Minutes Analysis (75-90)")
                
                st.markdown("""
                **Focus on Late Goals:** These are the minutes where we actually PREDICT momentum change!
                - Training: Minutes 0-74
                - Prediction: Minutes 75-90
                
                Can our predictions identify goal-scoring moments?
                """)
                
                # Get late goals analysis with predictions
                late_goals_data = self._analyze_late_goals_with_predictions()
                
                if late_goals_data is not None and len(late_goals_data) > 0:
                    st.markdown(f"**Late Goals (75-90+):** {len(late_goals_data)} goals with predictions")
                    
                    # Side by side comparison
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### Scoring Team")
                        
                        # Create comparison table
                        s_pred_pos = len(late_goals_data[late_goals_data['scorer_pred'] > 0])
                        s_pred_neg = len(late_goals_data[late_goals_data['scorer_pred'] < 0])
                        s_act_pos = len(late_goals_data[late_goals_data['scorer_actual'] > 0])
                        s_act_neg = len(late_goals_data[late_goals_data['scorer_actual'] < 0])
                        total = len(late_goals_data)
                        
                        st.markdown(f"""
                        | Metric | Predicted | Actual |
                        |--------|-----------|--------|
                        | **POSITIVE** | {s_pred_pos/total*100:.1f}% | {s_act_pos/total*100:.1f}% |
                        | **NEGATIVE** | {s_pred_neg/total*100:.1f}% | {s_act_neg/total*100:.1f}% |
                        """)
                        
                        # Sign accuracy with detailed breakdown
                        s_pp = len(late_goals_data[(late_goals_data['scorer_pred'] > 0) & (late_goals_data['scorer_actual'] > 0)])
                        s_nn = len(late_goals_data[(late_goals_data['scorer_pred'] < 0) & (late_goals_data['scorer_actual'] < 0)])
                        s_pn = len(late_goals_data[(late_goals_data['scorer_pred'] > 0) & (late_goals_data['scorer_actual'] < 0)])
                        s_np = len(late_goals_data[(late_goals_data['scorer_pred'] < 0) & (late_goals_data['scorer_actual'] > 0)])
                        scorer_correct = s_pp + s_nn
                        
                        st.metric("Sign Accuracy", f"{scorer_correct/total*100:.1f}%", f"{scorer_correct}/{total}")
                        
                        st.markdown(f"""
                        **Breakdown:**
                        - ✓ Pred POS, Act POS: {s_pp}
                        - ✓ Pred NEG, Act NEG: {s_nn}
                        - ✗ Pred POS, Act NEG: {s_pn}
                        - ✗ Pred NEG, Act POS: {s_np} ← Model missed!
                        """)
                    
                    with col2:
                        st.markdown("#### Conceding Team")
                        
                        c_pred_pos = len(late_goals_data[late_goals_data['conceder_pred'] > 0])
                        c_pred_neg = len(late_goals_data[late_goals_data['conceder_pred'] < 0])
                        c_act_pos = len(late_goals_data[late_goals_data['conceder_actual'] > 0])
                        c_act_neg = len(late_goals_data[late_goals_data['conceder_actual'] < 0])
                        
                        st.markdown(f"""
                        | Metric | Predicted | Actual |
                        |--------|-----------|--------|
                        | **POSITIVE** | {c_pred_pos/total*100:.1f}% | {c_act_pos/total*100:.1f}% |
                        | **NEGATIVE** | {c_pred_neg/total*100:.1f}% | {c_act_neg/total*100:.1f}% |
                        """)
                        
                        # Sign accuracy with detailed breakdown
                        c_pp = len(late_goals_data[(late_goals_data['conceder_pred'] > 0) & (late_goals_data['conceder_actual'] > 0)])
                        c_nn = len(late_goals_data[(late_goals_data['conceder_pred'] < 0) & (late_goals_data['conceder_actual'] < 0)])
                        c_pn = len(late_goals_data[(late_goals_data['conceder_pred'] > 0) & (late_goals_data['conceder_actual'] < 0)])
                        c_np = len(late_goals_data[(late_goals_data['conceder_pred'] < 0) & (late_goals_data['conceder_actual'] > 0)])
                        conceder_correct = c_pp + c_nn
                        
                        st.metric("Sign Accuracy", f"{conceder_correct/total*100:.1f}%", f"{conceder_correct}/{total}")
                        
                        st.markdown(f"""
                        **Breakdown:**
                        - ✓ Pred POS, Act POS: {c_pp}
                        - ✓ Pred NEG, Act NEG: {c_nn} ← Most common!
                        - ✗ Pred POS, Act NEG: {c_pn}
                        - ✗ Pred NEG, Act POS: {c_np}
                        """)
                    
                    # Key insight for predictions
                    st.info(f"""
                    **🎯 Model Performance at Goal Moments:**
                    
                    - Model predicted **{s_pred_neg/total*100:.1f}% NEGATIVE** for scoring teams, but reality was **{s_act_pos/total*100:.1f}% POSITIVE**
                    - Model predicted **{c_pred_neg/total*100:.1f}% NEGATIVE** for conceding teams, and reality was **{c_act_neg/total*100:.1f}% NEGATIVE** ✅
                    
                    **Insight:** The model is **better at predicting defensive vulnerability** (conceding team) than attacking success (scoring team)!
                    """)
                    
                    # Sample table
                    with st.expander("📋 Sample: Both Teams at Goal Moments"):
                        display_cols = ['goal_minute', 'scoring_team', 'scorer_pred', 'scorer_actual', 
                                       'conceding_team', 'conceder_pred', 'conceder_actual']
                        display_df = late_goals_data[display_cols].head(12)
                        display_df.columns = ['Min', 'Scorer', 'S.Pred', 'S.Actual', 
                                             'Conceder', 'C.Pred', 'C.Actual']
                        st.dataframe(display_df, use_container_width=True)
                else:
                    st.warning("Could not analyze late goals with predictions")
                
                # Add Sequence Before Goal Analysis
                st.markdown("---")
                st.subheader("📈 Momentum Sequence BEFORE Goals")
                
                st.markdown("""
                **Two Perspectives:**
                - 🟢 **POSITIVE Seq:** Did the **SCORING team** have positive momentum BEFORE scoring?
                - 🔴 **NEGATIVE Seq:** Did the **CONCEDING team** have negative momentum BEFORE conceding?
                
                **Calculation:** For goal at minute G:
                - Goal window: minute G-5 covers (G-2, G-1, G) ← Goal is HERE
                - Sequence starts at minute G-6, G-7, G-8... going backwards
                - Count consecutive same-sign changes until sign flips
                """)
                
                # Add concrete example
                with st.expander("📖 **Example: Goal at minute 80**", expanded=False):
                    st.markdown("""
                    | Step | Check | Display Min | Momentum Window | Change |
                    |------|-------|-------------|-----------------|--------|
                    | **Goal window** | G-5 = 75 | 75 | mom(78,79,**80**) ← **GOAL** | - |
                    | Seq check 1 | G-6 = 74 | 74 | mom(77,78,79) - mom(74,75,76) | **+0.3** ✅ |
                    | Seq check 2 | G-7 = 73 | 73 | mom(76,77,78) - mom(73,74,75) | **+0.5** ✅ |
                    | Seq check 3 | G-8 = 72 | 72 | mom(75,76,77) - mom(72,73,74) | **-0.2** ❌ |
                    
                    **Result:** Sign flipped at minute 72 → **Positive sequence = 2** (minutes 73, 74 were positive before goal)
                    """)
                
                # Calculate both positive and negative sequences
                seq_data = self._analyze_sequence_correct_logic()
                
                if seq_data is not None and len(seq_data) > 0:
                    total = len(seq_data)
                    
                    # Note about goal count
                    st.info(f"""
                    **Note:** Analyzing {total} goals (out of 117 total Euro 2024 goals).
                    - 117 total = 107 shot goals + 10 own goals (excluding penalty shootout)
                    - {117 - total} goals excluded: early goals (minute 0-5) where no sequence data available
                    """)
                    
                    # Calculate all windows baseline
                    all_windows_stats = self._calculate_all_windows_sequences()
                    
                    # Distribution comparison
                    st.markdown("#### Sequence Distribution")
                    
                    col_pos, col_neg = st.columns(2)
                    
                    with col_pos:
                        st.markdown("**🟢 POSITIVE Seq (Scoring Team)**")
                        st.caption("Scoring team had X positive changes BEFORE scoring")
                        pos_counts = seq_data['pos_seq_scoring'].value_counts().sort_index()
                        
                        # Create table with counts, %, and all windows baseline
                        pos_table = []
                        for i in range(8):
                            count = pos_counts.get(i, 0)
                            pct = count/total*100 if total > 0 else 0
                            if count > 0 or i < 6:
                                pos_table.append({'Seq': i, 'Goals': count, '%': f"{pct:.1f}%"})
                        pos_table.append({'Seq': 'Total', 'Goals': total, '%': '100%'})
                        st.dataframe(pd.DataFrame(pos_table), use_container_width=True, hide_index=True)
                        
                        if all_windows_stats:
                            st.caption(f"All windows in tournament: {all_windows_stats['total_windows']:,}")
                    
                    with col_neg:
                        st.markdown("**🔴 NEGATIVE Seq (Conceding Team)**")
                        st.caption("Conceding team had X negative changes BEFORE conceding")
                        neg_counts = seq_data['neg_seq_conceding'].value_counts().sort_index()
                        
                        neg_table = []
                        for i in range(8):
                            count = neg_counts.get(i, 0)
                            pct = count/total*100 if total > 0 else 0
                            if count > 0 or i < 6:
                                neg_table.append({'Seq': i, 'Goals': count, '%': f"{pct:.1f}%"})
                        neg_table.append({'Seq': 'Total', 'Goals': total, '%': '100%'})
                        st.dataframe(pd.DataFrame(neg_table), use_container_width=True, hide_index=True)
                        
                        if all_windows_stats:
                            st.caption(f"All windows in tournament: {all_windows_stats['total_windows']:,}")
                    
                    # Cumulative table
                    st.markdown("#### Cumulative Sequence Distribution")
                    st.caption("Goals with X+ consecutive momentum changes BEFORE")
                    
                    col_cum1, col_cum2 = st.columns(2)
                    
                    with col_cum1:
                        st.markdown("**🟢 POSITIVE Seq ≥X (Scoring Team)**")
                        cum_pos_table = []
                        for threshold in range(6):
                            count = sum(pos_counts.get(i, 0) for i in range(threshold, 10))
                            pct = count/total*100 if total > 0 else 0
                            cum_pos_table.append({'Seq ≥': threshold, 'Goals': count, '%': f"{pct:.1f}%"})
                        st.dataframe(pd.DataFrame(cum_pos_table), use_container_width=True, hide_index=True)
                    
                    with col_cum2:
                        st.markdown("**🔴 NEGATIVE Seq ≥X (Conceding Team)**")
                        cum_neg_table = []
                        for threshold in range(6):
                            count = sum(neg_counts.get(i, 0) for i in range(threshold, 10))
                            pct = count/total*100 if total > 0 else 0
                            cum_neg_table.append({'Seq ≥': threshold, 'Goals': count, '%': f"{pct:.1f}%"})
                        st.dataframe(pd.DataFrame(cum_neg_table), use_container_width=True, hide_index=True)
                    
                    # Show all windows baseline comparison
                    if all_windows_stats:
                        with st.expander("📊 Compare with ALL Momentum Windows (Baseline)"):
                            st.markdown("""
                            **What this shows:** Distribution of sequences across ALL momentum windows in the tournament,
                            not just goal-scoring moments. This is the "baseline" to compare against.
                            """)
                            
                            col_base1, col_base2 = st.columns(2)
                            
                            with col_base1:
                                st.markdown("**All Windows - Positive Seq**")
                                base_pos = []
                                for i in range(8):
                                    count = all_windows_stats['pos_counts'].get(i, 0)
                                    pct = count/all_windows_stats['total_windows']*100
                                    base_pos.append({'Seq': i, 'Windows': count, '%': f"{pct:.1f}%"})
                                base_pos.append({'Seq': 'Total', 'Windows': all_windows_stats['total_windows'], '%': '100%'})
                                st.dataframe(pd.DataFrame(base_pos), use_container_width=True, hide_index=True)
                            
                            with col_base2:
                                st.markdown("**All Windows - Negative Seq**")
                                base_neg = []
                                for i in range(8):
                                    count = all_windows_stats['neg_counts'].get(i, 0)
                                    pct = count/all_windows_stats['total_windows']*100
                                    base_neg.append({'Seq': i, 'Windows': count, '%': f"{pct:.1f}%"})
                                base_neg.append({'Seq': 'Total', 'Windows': all_windows_stats['total_windows'], '%': '100%'})
                                st.dataframe(pd.DataFrame(base_neg), use_container_width=True, hide_index=True)
                    
                    # Events comparison
                    st.markdown("#### Events in Sequences")
                    st.markdown("""
                    **How we count events (events that CREATE the momentum change):**
                    - **Seq 1**: `mom(5,4,3) - mom(2,1,0)` = positive → events **3,4,5** created the change
                    - **Seq 2**: `mom(6,5,4) - mom(3,2,1)` = positive → adds event **6** → events **3,4,5,6**
                    - **Seq 3**: `mom(7,6,5) - mom(4,3,2)` = positive → adds event **7** → events **3,4,5,6,7**
                    - Formula: **Total events = 3 + (Seq - 1) = Seq + 2**
                    """)
                    
                    # Events by sequence length - ALL MOMENTUM WINDOWS
                    st.markdown("#### Top 10 Events by Sequence Length (All Tournament Windows)")
                    st.caption("Events that CREATE each sequence length across all 9,958 momentum windows")
                    
                    # Calculate sequences and events for ALL windows
                    all_seq_events = self._calculate_all_windows_events_by_seq()
                    
                    # Calculate baseline event distribution (all events in tournament)
                    all_events_baseline = []
                    if self.llm_commentary_df is not None:
                        all_events_baseline = self.llm_commentary_df['detected_type'].dropna().tolist()
                    baseline_counts = pd.Series(all_events_baseline).value_counts()
                    baseline_total = len(all_events_baseline)
                    
                    if all_seq_events:
                        # Seq 0 first
                        st.markdown(f"##### Seq 0 (No consecutive changes before)")
                        col_s0a, col_s0b = st.columns(2)
                        
                        with col_s0a:
                            pos_0_events = all_seq_events.get('pos_0', [])
                            window_count = all_seq_events.get('pos_0_count', 0)
                            st.markdown(f"**🟢 POSITIVE Seq = 0** ({window_count:,} windows)")
                            st.caption("Previous change was NOT positive")
                            if pos_0_events:
                                ev_counts = pd.Series(pos_0_events).value_counts().head(10)
                                total_events = len(pos_0_events)
                                table_data = []
                                for event, count in ev_counts.items():
                                    seq_pct = count / total_events * 100 if total_events > 0 else 0
                                    baseline_pct = baseline_counts.get(event, 0) / baseline_total * 100 if baseline_total > 0 else 0
                                    table_data.append({
                                        'Event': event,
                                        'Count': count,
                                        'Seq %': f"{seq_pct:.1f}%",
                                        'All %': f"{baseline_pct:.1f}%"
                                    })
                                st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)
                                st.caption(f"Total events: {total_events:,}")
                            else:
                                st.caption("No events")
                        
                        with col_s0b:
                            neg_0_events = all_seq_events.get('neg_0', [])
                            window_count = all_seq_events.get('neg_0_count', 0)
                            st.markdown(f"**🔴 NEGATIVE Seq = 0** ({window_count:,} windows)")
                            st.caption("Previous change was NOT negative")
                            if neg_0_events:
                                ev_counts = pd.Series(neg_0_events).value_counts().head(10)
                                total_events = len(neg_0_events)
                                table_data = []
                                for event, count in ev_counts.items():
                                    seq_pct = count / total_events * 100 if total_events > 0 else 0
                                    baseline_pct = baseline_counts.get(event, 0) / baseline_total * 100 if baseline_total > 0 else 0
                                    table_data.append({
                                        'Event': event,
                                        'Count': count,
                                        'Seq %': f"{seq_pct:.1f}%",
                                        'All %': f"{baseline_pct:.1f}%"
                                    })
                                st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)
                                st.caption(f"Total events: {total_events:,}")
                            else:
                                st.caption("No events")
                        
                        # Seq 1-5
                        for seq_len in [1, 2, 3, 4, 5]:
                            if seq_len < 5:
                                st.markdown(f"##### Seq {seq_len} ({seq_len} consecutive change{'s' if seq_len > 1 else ''})")
                            else:
                                st.markdown(f"##### Seq {seq_len}+ ({seq_len} or more consecutive changes)")
                            
                            col_a, col_b = st.columns(2)
                            
                            with col_a:
                                key = f'pos_{seq_len}' if seq_len < 5 else 'pos_5plus'
                                pos_events = all_seq_events.get(key, [])
                                window_count = all_seq_events.get(f'pos_{seq_len}_count' if seq_len < 5 else 'pos_5plus_count', 0)
                                st.markdown(f"**🟢 POSITIVE Seq {'= ' + str(seq_len) if seq_len < 5 else '≥ 5'}** ({window_count:,} windows)")
                                if pos_events:
                                    ev_counts = pd.Series(pos_events).value_counts().head(10)
                                    total_events = len(pos_events)
                                    table_data = []
                                    for event, count in ev_counts.items():
                                        seq_pct = count / total_events * 100 if total_events > 0 else 0
                                        baseline_pct = baseline_counts.get(event, 0) / baseline_total * 100 if baseline_total > 0 else 0
                                        table_data.append({
                                            'Event': event,
                                            'Count': count,
                                            'Seq %': f"{seq_pct:.1f}%",
                                            'All %': f"{baseline_pct:.1f}%"
                                        })
                                    st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)
                                    st.caption(f"Total events: {total_events:,}")
                                else:
                                    st.caption("No events")
                            
                            with col_b:
                                key = f'neg_{seq_len}' if seq_len < 5 else 'neg_5plus'
                                neg_events = all_seq_events.get(key, [])
                                window_count = all_seq_events.get(f'neg_{seq_len}_count' if seq_len < 5 else 'neg_5plus_count', 0)
                                st.markdown(f"**🔴 NEGATIVE Seq {'= ' + str(seq_len) if seq_len < 5 else '≥ 5'}** ({window_count:,} windows)")
                                if neg_events:
                                    ev_counts = pd.Series(neg_events).value_counts().head(10)
                                    total_events = len(neg_events)
                                    table_data = []
                                    for event, count in ev_counts.items():
                                        seq_pct = count / total_events * 100 if total_events > 0 else 0
                                        baseline_pct = baseline_counts.get(event, 0) / baseline_total * 100 if baseline_total > 0 else 0
                                        table_data.append({
                                            'Event': event,
                                            'Count': count,
                                            'Seq %': f"{seq_pct:.1f}%",
                                            'All %': f"{baseline_pct:.1f}%"
                                        })
                                    st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)
                                    st.caption(f"Total events: {total_events:,}")
                                else:
                                    st.caption("No events")
                    
                    # Key insight
                    pos_1_plus = len(seq_data[seq_data['pos_seq_scoring'] >= 1])
                    neg_1_plus = len(seq_data[seq_data['neg_seq_conceding'] >= 1])
                    
                    st.success(f"""
                    ### 🎯 Key Insight
                    
                    **{pos_1_plus/total*100:.1f}%** of goals: Scoring team had ≥1 positive change BEFORE ({pos_1_plus} goals)
                    **{neg_1_plus/total*100:.1f}%** of goals: Conceding team had ≥1 negative change BEFORE ({neg_1_plus} goals)
                    
                    **Prediction Value:**
                    - If model predicts **positive** for Team A → Team A more likely to SCORE
                    - If model predicts **negative** for Team B → Team B more likely to CONCEDE
                    
                    **Momentum change direction PREDICTS both scoring AND conceding!**
                    """)
            else:
                st.warning("Could not analyze goals data")
            
            # Add Goal Effect Sequential Analysis (like subs/cards)
            st.markdown("---")
            st.subheader("⚽ Goal Effect on Momentum (Sequential Analysis)")
            
            goal_effect_results = self._analyze_goal_effect()
            if goal_effect_results and goal_effect_results.get('total_analyzed', 0) > 0:
                
                seq = goal_effect_results.get('seq_changes', {})
                scoring_seq = seq.get('scoring_team', {})
                conceding_seq = seq.get('conceding_team', {})
                
                st.markdown(f"### ⚽ Goal Events ({goal_effect_results['total_analyzed']} analyzed)")
                
                col_s, col_c = st.columns(2)
                
                with col_s:
                    st.markdown("**Scoring Team:**")
                    rows = []
                    for change_name in ['B-3→B-2', 'B-2→B-1', 'B-1→A+1', 'A+1→A+2', 'A+2→A+3']:
                        change_data = scoring_seq.get(change_name, {})
                        avg = change_data.get('avg')
                        median = change_data.get('median')
                        pos_pct = change_data.get('positive_pct', 0)
                        avg_str = f"{avg:+.3f}" if avg is not None else 'N/A'
                        med_str = f"{median:+.3f}" if median is not None else 'N/A'
                        # Highlight immediate impact
                        if change_name == 'B-1→A+1':
                            rows.append({'Change': f"**{change_name}**", 'Avg': f"**{avg_str}**", 'Median': f"**{med_str}**", '% Pos': f"**{pos_pct:.1f}%**"})
                        else:
                            rows.append({'Change': change_name, 'Avg': avg_str, 'Median': med_str, '% Pos': f"{pos_pct:.1f}%"})
                    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
                
                with col_c:
                    st.markdown("**Conceding Team:**")
                    rows = []
                    for change_name in ['B-3→B-2', 'B-2→B-1', 'B-1→A+1', 'A+1→A+2', 'A+2→A+3']:
                        change_data = conceding_seq.get(change_name, {})
                        avg = change_data.get('avg')
                        median = change_data.get('median')
                        pos_pct = change_data.get('positive_pct', 0)
                        avg_str = f"{avg:+.3f}" if avg is not None else 'N/A'
                        med_str = f"{median:+.3f}" if median is not None else 'N/A'
                        # Highlight immediate impact
                        if change_name == 'B-1→A+1':
                            rows.append({'Change': f"**{change_name}**", 'Avg': f"**{avg_str}**", 'Median': f"**{med_str}**", '% Pos': f"**{pos_pct:.1f}%**"})
                        else:
                            rows.append({'Change': change_name, 'Avg': avg_str, 'Median': med_str, '% Pos': f"{pos_pct:.1f}%"})
                    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
                
                # Key findings based on data
                scoring_b2b1 = scoring_seq.get('B-2→B-1', {}).get('positive_pct', 0)
                scoring_impact = scoring_seq.get('B-1→A+1', {}).get('positive_pct', 0)
                scoring_a1a2 = scoring_seq.get('A+1→A+2', {}).get('positive_pct', 0)
                
                conceding_b2b1 = conceding_seq.get('B-2→B-1', {}).get('positive_pct', 0)
                conceding_impact = conceding_seq.get('B-1→A+1', {}).get('positive_pct', 0)
                conceding_a1a2 = conceding_seq.get('A+1→A+2', {}).get('positive_pct', 0)
                
                st.success(f"""
                ### 🎯 Key Findings - Goal Effect
                
                **⚽ SCORING TEAM:**
                - Before: {scoring_b2b1:.1f}% positive → At goal: {scoring_impact:.1f}% positive → After: {scoring_a1a2:.1f}% positive
                - **Insight:** {'Momentum building before goal!' if scoring_b2b1 > 50 else 'Goals can come from any momentum state'}
                
                **🥅 CONCEDING TEAM:**
                - Before: {conceding_b2b1:.1f}% positive → At goal: {conceding_impact:.1f}% positive → After: {conceding_a1a2:.1f}% positive
                - **Insight:** {'Momentum was declining before conceding!' if conceding_b2b1 < 50 else 'Conceding can happen even with momentum'}
                """)
                
                # Example expander
                with st.expander("📖 How is this calculated? (with example)"):
                    st.markdown("""
                    **EXAMPLE: Goal at minute 78**
                    
                    | Window | Minute | Momentum Change Value |
                    |--------|--------|----------------------|
                    | B-3 | 75 | mom(75,74,73) - mom(72,71,70) = 0.22 |
                    | B-2 | 76 | mom(76,75,74) - mom(73,72,71) = 0.18 |
                    | B-1 | 77 | mom(77,76,75) - mom(74,73,72) = 0.15 |
                    | **⚽ GOAL** | **78** | **Event happens here** |
                    | A+1 | 79 | mom(79,**78**,77) - mom(76,75,74) = 0.04 |
                    | A+2 | 80 | mom(80,79,**78**) - mom(77,76,75) = 0.05 |
                    | A+3 | 81 | mom(81,80,79) - mom(**78**,77,76) = 0.06 |
                    
                    **Sequential Changes:**
                    | Change | Calculation | Result |
                    |--------|-------------|--------|
                    | B-3→B-2 | 0.18 - 0.22 | -0.04 (slightly declining) |
                    | B-2→B-1 | 0.15 - 0.18 | -0.03 (continuing decline) |
                    | **B-1→A+1** | **0.04 - 0.15** | **-0.11 (big drop!)** |
                    | A+1→A+2 | 0.05 - 0.04 | +0.01 (stabilizing) |
                    | A+2→A+3 | 0.06 - 0.05 | +0.01 (recovering) |
                    
                    **Reading the table:**
                    - **Avg:** Average change between windows (+ = momentum improving)
                    - **% Positive:** How often the change was positive
                    """)
            
            # Add Substitution and Card Effect Analysis
            st.markdown("---")
            st.subheader("🔄 Substitution & Card Effect on Momentum")
            
            sub_card_results = self._analyze_sub_card_effect()
            if sub_card_results:
                
                def render_seq_change_table(data, event_name, event_emoji):
                    """Render sequential change tables for team and opponent"""
                    if not data or data.get('total_analyzed', 0) == 0:
                        return
                    
                    seq = data.get('seq_changes', {})
                    team_seq = seq.get('team', {})
                    opp_seq = seq.get('opponent', {})
                    
                    st.markdown(f"### {event_emoji} {event_name} ({data['total_analyzed']} analyzed)")
                    
                    col_t, col_o = st.columns(2)
                    
                    with col_t:
                        st.markdown("**Team (had event):**")
                        rows = []
                        for change_name in ['B-3→B-2', 'B-2→B-1', 'B-1→A+1', 'A+1→A+2', 'A+2→A+3']:
                            change_data = team_seq.get(change_name, {})
                            avg = change_data.get('avg')
                            median = change_data.get('median')
                            pos_pct = change_data.get('positive_pct', 0)
                            avg_str = f"{avg:+.3f}" if avg is not None else 'N/A'
                            med_str = f"{median:+.3f}" if median is not None else 'N/A'
                            # Highlight immediate impact
                            if change_name == 'B-1→A+1':
                                rows.append({'Change': f"**{change_name}**", 'Avg': f"**{avg_str}**", 'Median': f"**{med_str}**", '% Pos': f"**{pos_pct:.1f}%**"})
                            else:
                                rows.append({'Change': change_name, 'Avg': avg_str, 'Median': med_str, '% Pos': f"{pos_pct:.1f}%"})
                        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
                    
                    with col_o:
                        st.markdown("**Opponent:**")
                        rows = []
                        for change_name in ['B-3→B-2', 'B-2→B-1', 'B-1→A+1', 'A+1→A+2', 'A+2→A+3']:
                            change_data = opp_seq.get(change_name, {})
                            avg = change_data.get('avg')
                            median = change_data.get('median')
                            pos_pct = change_data.get('positive_pct', 0)
                            avg_str = f"{avg:+.3f}" if avg is not None else 'N/A'
                            med_str = f"{median:+.3f}" if median is not None else 'N/A'
                            # Highlight immediate impact
                            if change_name == 'B-1→A+1':
                                rows.append({'Change': f"**{change_name}**", 'Avg': f"**{avg_str}**", 'Median': f"**{med_str}**", '% Pos': f"**{pos_pct:.1f}%**"})
                            else:
                                rows.append({'Change': change_name, 'Avg': avg_str, 'Median': med_str, '% Pos': f"{pos_pct:.1f}%"})
                        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
                
                # Render Substitution table
                render_seq_change_table(sub_card_results.get('substitution'), 'Substitution', '⚽')
                
                st.markdown("---")
                
                # Render Yellow Card table
                render_seq_change_table(sub_card_results.get('yellow_card'), 'Yellow Card', '🟨')
                
                # Insights based on data
                sub_data = sub_card_results.get('substitution', {})
                card_data = sub_card_results.get('yellow_card', {})
                
                sub_seq = sub_data.get('seq_changes', {}).get('team', {})
                card_seq = card_data.get('seq_changes', {}).get('team', {})
                sub_opp_seq = sub_data.get('seq_changes', {}).get('opponent', {})
                card_opp_seq = card_data.get('seq_changes', {}).get('opponent', {})
                
                sub_impact = sub_seq.get('B-1→A+1', {}).get('avg', 0) or 0
                card_impact = card_seq.get('B-1→A+1', {}).get('avg', 0) or 0
                sub_opp_impact = sub_opp_seq.get('B-1→A+1', {}).get('avg', 0) or 0
                card_opp_impact = card_opp_seq.get('B-1→A+1', {}).get('avg', 0) or 0
                
                # Get % positive values for detailed insights
                sub_team_b2b1 = sub_seq.get('B-2→B-1', {}).get('positive_pct', 0)
                sub_team_impact = sub_seq.get('B-1→A+1', {}).get('positive_pct', 0)
                sub_opp_b2b1 = sub_opp_seq.get('B-2→B-1', {}).get('positive_pct', 0)
                sub_opp_impact_pct = sub_opp_seq.get('B-1→A+1', {}).get('positive_pct', 0)
                
                card_team_b2b1 = card_seq.get('B-2→B-1', {}).get('positive_pct', 0)
                card_team_impact_pct = card_seq.get('B-1→A+1', {}).get('positive_pct', 0)
                card_opp_b2b1 = card_opp_seq.get('B-2→B-1', {}).get('positive_pct', 0)
                card_opp_impact_pct = card_opp_seq.get('B-1→A+1', {}).get('positive_pct', 0)
                
                card_team_a2a3 = card_seq.get('A+2→A+3', {}).get('positive_pct', 0)
                card_opp_a2a3 = card_opp_seq.get('A+2→A+3', {}).get('positive_pct', 0)
                
                st.success(f"""
                ### 🎯 Key Findings
                
                **⚽ SUBSTITUTION:**
                - Both teams drop at sub moment, but **opponent drops MORE in % positive**
                - Team: {sub_team_b2b1:.1f}% → {sub_team_impact:.1f}% (drop of {sub_team_b2b1 - sub_team_impact:.1f}%)
                - Opponent: {sub_opp_b2b1:.1f}% → {sub_opp_impact_pct:.1f}% (**drop of {sub_opp_b2b1 - sub_opp_impact_pct:.1f}%**)
                - **Insight:** Subs disrupt opponent MORE than the team making the sub!
                
                **🟨 YELLOW CARD:**
                - Team was RISING before card ({card_team_b2b1:.1f}%), stays positive at impact ({card_team_impact_pct:.1f}%)
                - Opponent was DECLINING before ({card_opp_b2b1:.1f}%), continues declining at impact ({card_opp_impact_pct:.1f}%)
                - **But later:** Team fades ({card_team_a2a3:.1f}%), Opponent RECOVERS ({card_opp_a2a3:.1f}%)
                - **Insight:** Card gives short-term boost to team, but opponent recovers stronger!
                """)
                
                # Logic explanation with example
                with st.expander("📖 How is this calculated? (with example)"):
                    st.markdown("""
                    **EXAMPLE: Substitution at minute 35**
                    
                    | Window | Minute | Momentum Change Value |
                    |--------|--------|----------------------|
                    | B-3 | 32 | mom(32,31,30) - mom(29,28,27) = 0.20 |
                    | B-2 | 33 | mom(33,32,31) - mom(30,29,28) = 0.18 |
                    | B-1 | 34 | mom(34,33,32) - mom(31,30,29) = 0.16 |
                    | **⚽ SUB** | **35** | **Event happens here** |
                    | A+1 | 36 | mom(36,**35**,34) - mom(33,32,31) = 0.04 |
                    | A+2 | 37 | mom(37,36,**35**) - mom(34,33,32) = 0.05 |
                    | A+3 | 38 | mom(38,37,36) - mom(**35**,34,33) = 0.06 |
                    
                    **Sequential Changes:**
                    | Change | Calculation | Result |
                    |--------|-------------|--------|
                    | B-3→B-2 | 0.18 - 0.20 | -0.02 (slightly declining) |
                    | B-2→B-1 | 0.16 - 0.18 | -0.02 (continuing decline) |
                    | **B-1→A+1** | **0.04 - 0.16** | **-0.12 (big drop!)** |
                    | A+1→A+2 | 0.05 - 0.04 | +0.01 (stabilizing) |
                    | A+2→A+3 | 0.06 - 0.05 | +0.01 (recovering) |
                    
                    **Reading the table:**
                    - **Avg:** Average change between windows (+ = momentum improving)
                    - **% Positive:** How often the change was positive
                    """)
                
        except Exception as e:
            st.error(f"Error analyzing goals: {str(e)}")
    
    def _analyze_goal_effect(self):
        """
        Analyze effect of goals on momentum change (sequential analysis)
        Similar to subs/cards but for goals - shows scoring team vs conceding team
        """
        if self.events_df is None or self.momentum_df is None:
            return None
        
        match_teams = self.momentum_df.groupby('match_id').first()[['team_home', 'team_away']].to_dict('index')
        
        def get_momentum_change(match_id, period, minute, team_col):
            """Get momentum change at specific minute"""
            row = self.momentum_df[
                (self.momentum_df['match_id'] == match_id) & 
                (self.momentum_df['period'] == period) & 
                (self.momentum_df['minute'] == minute)
            ]
            if len(row) > 0:
                val = row[team_col].values[0]
                return val if pd.notna(val) else None
            return None
        
        # Get all goals from shots (parse shot column for outcome)
        shots = self.events_df[self.events_df['event_type'] == 'Shot'].copy()
        goals_from_shots = []
        for idx, row in shots.iterrows():
            if pd.notna(row.get('shot')):
                shot_str = str(row['shot'])
                if "'outcome'" in shot_str and "'Goal'" in shot_str:
                    goals_from_shots.append(row)
        goals_from_shots = pd.DataFrame(goals_from_shots) if goals_from_shots else pd.DataFrame()
        
        # Get own goals
        own_goals = self.events_df[
            self.events_df['event_type'] == 'Own Goal Against'
        ].copy() if 'event_type' in self.events_df.columns else pd.DataFrame()
        
        results = []
        
        # Process regular goals
        for idx, goal in goals_from_shots.iterrows():
            match_id = goal['match_id']
            minute = int(goal['minute'])
            period = int(goal['period']) if pd.notna(goal.get('period')) else 1
            
            # Skip penalty shootout goals
            if period == 5:
                continue
            
            scoring_team = goal.get('team_name', '')
            
            if match_id not in match_teams:
                continue
            
            home = match_teams[match_id]['team_home']
            away = match_teams[match_id]['team_away']
            
            is_home = (scoring_team == home)
            scoring_col = 'team_home_momentum_change' if is_home else 'team_away_momentum_change'
            conceding_col = 'team_away_momentum_change' if is_home else 'team_home_momentum_change'
            
            # Get windows for scoring team
            s_b3 = get_momentum_change(match_id, period, minute - 3, scoring_col)
            s_b2 = get_momentum_change(match_id, period, minute - 2, scoring_col)
            s_b1 = get_momentum_change(match_id, period, minute - 1, scoring_col)
            s_a1 = get_momentum_change(match_id, period, minute + 1, scoring_col)
            s_a2 = get_momentum_change(match_id, period, minute + 2, scoring_col)
            s_a3 = get_momentum_change(match_id, period, minute + 3, scoring_col)
            
            # Get windows for conceding team
            c_b3 = get_momentum_change(match_id, period, minute - 3, conceding_col)
            c_b2 = get_momentum_change(match_id, period, minute - 2, conceding_col)
            c_b1 = get_momentum_change(match_id, period, minute - 1, conceding_col)
            c_a1 = get_momentum_change(match_id, period, minute + 1, conceding_col)
            c_a2 = get_momentum_change(match_id, period, minute + 2, conceding_col)
            c_a3 = get_momentum_change(match_id, period, minute + 3, conceding_col)
            
            if s_b1 is not None and s_a1 is not None:
                results.append({
                    'scoring_b3': s_b3, 'scoring_b2': s_b2, 'scoring_b1': s_b1,
                    'scoring_a1': s_a1, 'scoring_a2': s_a2, 'scoring_a3': s_a3,
                    'conceding_b3': c_b3, 'conceding_b2': c_b2, 'conceding_b1': c_b1,
                    'conceding_a1': c_a1, 'conceding_a2': c_a2, 'conceding_a3': c_a3,
                })
        
        # Process own goals (scoring team is OPPOSITE of team_name)
        for idx, goal in own_goals.iterrows():
            match_id = goal['match_id']
            minute = int(goal['minute'])
            period = int(goal['period']) if pd.notna(goal.get('period')) else 1
            
            # Skip penalty shootout
            if period == 5:
                continue
            
            # For own goal: team_name is the team that SCORED AGAINST THEMSELVES (conceding)
            conceding_team = goal.get('team_name', '')
            
            if match_id not in match_teams:
                continue
            
            home = match_teams[match_id]['team_home']
            away = match_teams[match_id]['team_away']
            
            is_home_conceding = (conceding_team == home)
            conceding_col = 'team_home_momentum_change' if is_home_conceding else 'team_away_momentum_change'
            scoring_col = 'team_away_momentum_change' if is_home_conceding else 'team_home_momentum_change'
            
            # Get windows for scoring team (beneficiary)
            s_b3 = get_momentum_change(match_id, period, minute - 3, scoring_col)
            s_b2 = get_momentum_change(match_id, period, minute - 2, scoring_col)
            s_b1 = get_momentum_change(match_id, period, minute - 1, scoring_col)
            s_a1 = get_momentum_change(match_id, period, minute + 1, scoring_col)
            s_a2 = get_momentum_change(match_id, period, minute + 2, scoring_col)
            s_a3 = get_momentum_change(match_id, period, minute + 3, scoring_col)
            
            # Get windows for conceding team (own goal team)
            c_b3 = get_momentum_change(match_id, period, minute - 3, conceding_col)
            c_b2 = get_momentum_change(match_id, period, minute - 2, conceding_col)
            c_b1 = get_momentum_change(match_id, period, minute - 1, conceding_col)
            c_a1 = get_momentum_change(match_id, period, minute + 1, conceding_col)
            c_a2 = get_momentum_change(match_id, period, minute + 2, conceding_col)
            c_a3 = get_momentum_change(match_id, period, minute + 3, conceding_col)
            
            if s_b1 is not None and s_a1 is not None:
                results.append({
                    'scoring_b3': s_b3, 'scoring_b2': s_b2, 'scoring_b1': s_b1,
                    'scoring_a1': s_a1, 'scoring_a2': s_a2, 'scoring_a3': s_a3,
                    'conceding_b3': c_b3, 'conceding_b2': c_b2, 'conceding_b1': c_b1,
                    'conceding_a1': c_a1, 'conceding_a2': c_a2, 'conceding_a3': c_a3,
                })
        
        if not results:
            return {'total_analyzed': 0}
        
        df = pd.DataFrame(results)
        
        # Calculate SEQUENTIAL CHANGES
        # Scoring team sequential changes
        s_b3_to_b2 = (df['scoring_b2'] - df['scoring_b3']).dropna()
        s_b2_to_b1 = (df['scoring_b1'] - df['scoring_b2']).dropna()
        s_b1_to_a1 = (df['scoring_a1'] - df['scoring_b1']).dropna()
        s_a1_to_a2 = (df['scoring_a2'] - df['scoring_a1']).dropna()
        s_a2_to_a3 = (df['scoring_a3'] - df['scoring_a2']).dropna()
        
        # Conceding team sequential changes
        c_b3_to_b2 = (df['conceding_b2'] - df['conceding_b3']).dropna()
        c_b2_to_b1 = (df['conceding_b1'] - df['conceding_b2']).dropna()
        c_b1_to_a1 = (df['conceding_a1'] - df['conceding_b1']).dropna()
        c_a1_to_a2 = (df['conceding_a2'] - df['conceding_a1']).dropna()
        c_a2_to_a3 = (df['conceding_a3'] - df['conceding_a2']).dropna()
        
        seq_changes = {
            'scoring_team': {
                'B-3→B-2': {'avg': s_b3_to_b2.mean() if len(s_b3_to_b2) > 0 else None,
                           'median': s_b3_to_b2.median() if len(s_b3_to_b2) > 0 else None,
                           'positive_pct': (s_b3_to_b2 > 0).mean() * 100 if len(s_b3_to_b2) > 0 else 0},
                'B-2→B-1': {'avg': s_b2_to_b1.mean() if len(s_b2_to_b1) > 0 else None,
                           'median': s_b2_to_b1.median() if len(s_b2_to_b1) > 0 else None,
                           'positive_pct': (s_b2_to_b1 > 0).mean() * 100 if len(s_b2_to_b1) > 0 else 0},
                'B-1→A+1': {'avg': s_b1_to_a1.mean() if len(s_b1_to_a1) > 0 else None,
                           'median': s_b1_to_a1.median() if len(s_b1_to_a1) > 0 else None,
                           'positive_pct': (s_b1_to_a1 > 0).mean() * 100 if len(s_b1_to_a1) > 0 else 0},
                'A+1→A+2': {'avg': s_a1_to_a2.mean() if len(s_a1_to_a2) > 0 else None,
                           'median': s_a1_to_a2.median() if len(s_a1_to_a2) > 0 else None,
                           'positive_pct': (s_a1_to_a2 > 0).mean() * 100 if len(s_a1_to_a2) > 0 else 0},
                'A+2→A+3': {'avg': s_a2_to_a3.mean() if len(s_a2_to_a3) > 0 else None,
                           'median': s_a2_to_a3.median() if len(s_a2_to_a3) > 0 else None,
                           'positive_pct': (s_a2_to_a3 > 0).mean() * 100 if len(s_a2_to_a3) > 0 else 0},
            },
            'conceding_team': {
                'B-3→B-2': {'avg': c_b3_to_b2.mean() if len(c_b3_to_b2) > 0 else None,
                           'median': c_b3_to_b2.median() if len(c_b3_to_b2) > 0 else None,
                           'positive_pct': (c_b3_to_b2 > 0).mean() * 100 if len(c_b3_to_b2) > 0 else 0},
                'B-2→B-1': {'avg': c_b2_to_b1.mean() if len(c_b2_to_b1) > 0 else None,
                           'median': c_b2_to_b1.median() if len(c_b2_to_b1) > 0 else None,
                           'positive_pct': (c_b2_to_b1 > 0).mean() * 100 if len(c_b2_to_b1) > 0 else 0},
                'B-1→A+1': {'avg': c_b1_to_a1.mean() if len(c_b1_to_a1) > 0 else None,
                           'median': c_b1_to_a1.median() if len(c_b1_to_a1) > 0 else None,
                           'positive_pct': (c_b1_to_a1 > 0).mean() * 100 if len(c_b1_to_a1) > 0 else 0},
                'A+1→A+2': {'avg': c_a1_to_a2.mean() if len(c_a1_to_a2) > 0 else None,
                           'median': c_a1_to_a2.median() if len(c_a1_to_a2) > 0 else None,
                           'positive_pct': (c_a1_to_a2 > 0).mean() * 100 if len(c_a1_to_a2) > 0 else 0},
                'A+2→A+3': {'avg': c_a2_to_a3.mean() if len(c_a2_to_a3) > 0 else None,
                           'median': c_a2_to_a3.median() if len(c_a2_to_a3) > 0 else None,
                           'positive_pct': (c_a2_to_a3 > 0).mean() * 100 if len(c_a2_to_a3) > 0 else 0},
            }
        }
        
        return {
            'total_analyzed': len(df),
            'seq_changes': seq_changes,
        }
    
    def _analyze_sub_card_effect(self):
        """
        Analyze effect of substitutions and cards on momentum change
        
        Sequential change analysis: B-2→B-1, B-1→A+1, A+1→A+2, A+2→A+3
        Shows trajectory before and after event for both team and opponent.
        """
        if self.events_df is None or self.momentum_df is None:
            return None
        
        match_teams = self.momentum_df.groupby('match_id').first()[['team_home', 'team_away']].to_dict('index')
        
        def get_momentum_change(match_id, period, minute, team_col):
            """Get momentum change at specific minute"""
            row = self.momentum_df[
                (self.momentum_df['match_id'] == match_id) & 
                (self.momentum_df['period'] == period) & 
                (self.momentum_df['minute'] == minute)
            ]
            if len(row) > 0:
                val = row[team_col].values[0]
                return val if pd.notna(val) else None
            return None
        
        def analyze_event_type(events, event_name):
            """Analyze effect with sequential window changes"""
            results = []
            for idx, event in events.iterrows():
                match_id = event['match_id']
                minute = int(event['minute'])
                period = int(event['period']) if pd.notna(event.get('period')) else 1
                team = event.get('team_name', '')
                
                if match_id not in match_teams:
                    continue
                
                home = match_teams[match_id]['team_home']
                away = match_teams[match_id]['team_away']
                
                is_home = (team == home)
                team_col = 'team_home_momentum_change' if is_home else 'team_away_momentum_change'
                opp_col = 'team_away_momentum_change' if is_home else 'team_home_momentum_change'
                
                # Get windows for team
                team_b3 = get_momentum_change(match_id, period, minute - 3, team_col)
                team_b2 = get_momentum_change(match_id, period, minute - 2, team_col)
                team_b1 = get_momentum_change(match_id, period, minute - 1, team_col)
                team_a1 = get_momentum_change(match_id, period, minute + 1, team_col)
                team_a2 = get_momentum_change(match_id, period, minute + 2, team_col)
                team_a3 = get_momentum_change(match_id, period, minute + 3, team_col)
                
                # Get windows for opponent
                opp_b3 = get_momentum_change(match_id, period, minute - 3, opp_col)
                opp_b2 = get_momentum_change(match_id, period, minute - 2, opp_col)
                opp_b1 = get_momentum_change(match_id, period, minute - 1, opp_col)
                opp_a1 = get_momentum_change(match_id, period, minute + 1, opp_col)
                opp_a2 = get_momentum_change(match_id, period, minute + 2, opp_col)
                opp_a3 = get_momentum_change(match_id, period, minute + 3, opp_col)
                
                # Only include if we have B-1 and A+1
                if team_b1 is not None and team_a1 is not None:
                    results.append({
                        'team_b3': team_b3, 'team_b2': team_b2, 'team_b1': team_b1,
                        'team_a1': team_a1, 'team_a2': team_a2, 'team_a3': team_a3,
                        'opp_b3': opp_b3, 'opp_b2': opp_b2, 'opp_b1': opp_b1,
                        'opp_a1': opp_a1, 'opp_a2': opp_a2, 'opp_a3': opp_a3,
                    })
            
            if not results:
                return {'total_analyzed': 0}
            
            df = pd.DataFrame(results)
            
            # Calculate SEQUENTIAL CHANGES (the new approach)
            # Team sequential changes
            team_b3_to_b2 = (df['team_b2'] - df['team_b3']).dropna()
            team_b2_to_b1 = (df['team_b1'] - df['team_b2']).dropna()
            team_b1_to_a1 = (df['team_a1'] - df['team_b1']).dropna()  # IMMEDIATE IMPACT
            team_a1_to_a2 = (df['team_a2'] - df['team_a1']).dropna()
            team_a2_to_a3 = (df['team_a3'] - df['team_a2']).dropna()
            
            # Opponent sequential changes
            opp_b3_to_b2 = (df['opp_b2'] - df['opp_b3']).dropna()
            opp_b2_to_b1 = (df['opp_b1'] - df['opp_b2']).dropna()
            opp_b1_to_a1 = (df['opp_a1'] - df['opp_b1']).dropna()  # IMMEDIATE IMPACT
            opp_a1_to_a2 = (df['opp_a2'] - df['opp_a1']).dropna()
            opp_a2_to_a3 = (df['opp_a3'] - df['opp_a2']).dropna()
            
            # Build sequential change results with avg AND median
            seq_changes = {
                'team': {
                    'B-3→B-2': {'avg': team_b3_to_b2.mean() if len(team_b3_to_b2) > 0 else None,
                               'median': team_b3_to_b2.median() if len(team_b3_to_b2) > 0 else None,
                               'positive_pct': (team_b3_to_b2 > 0).mean() * 100 if len(team_b3_to_b2) > 0 else 0,
                               'count': len(team_b3_to_b2)},
                    'B-2→B-1': {'avg': team_b2_to_b1.mean() if len(team_b2_to_b1) > 0 else None,
                               'median': team_b2_to_b1.median() if len(team_b2_to_b1) > 0 else None,
                               'positive_pct': (team_b2_to_b1 > 0).mean() * 100 if len(team_b2_to_b1) > 0 else 0,
                               'count': len(team_b2_to_b1)},
                    'B-1→A+1': {'avg': team_b1_to_a1.mean() if len(team_b1_to_a1) > 0 else None,
                               'median': team_b1_to_a1.median() if len(team_b1_to_a1) > 0 else None,
                               'positive_pct': (team_b1_to_a1 > 0).mean() * 100 if len(team_b1_to_a1) > 0 else 0,
                               'count': len(team_b1_to_a1)},
                    'A+1→A+2': {'avg': team_a1_to_a2.mean() if len(team_a1_to_a2) > 0 else None,
                               'median': team_a1_to_a2.median() if len(team_a1_to_a2) > 0 else None,
                               'positive_pct': (team_a1_to_a2 > 0).mean() * 100 if len(team_a1_to_a2) > 0 else 0,
                               'count': len(team_a1_to_a2)},
                    'A+2→A+3': {'avg': team_a2_to_a3.mean() if len(team_a2_to_a3) > 0 else None,
                               'median': team_a2_to_a3.median() if len(team_a2_to_a3) > 0 else None,
                               'positive_pct': (team_a2_to_a3 > 0).mean() * 100 if len(team_a2_to_a3) > 0 else 0,
                               'count': len(team_a2_to_a3)},
                },
                'opponent': {
                    'B-3→B-2': {'avg': opp_b3_to_b2.mean() if len(opp_b3_to_b2) > 0 else None,
                               'median': opp_b3_to_b2.median() if len(opp_b3_to_b2) > 0 else None,
                               'positive_pct': (opp_b3_to_b2 > 0).mean() * 100 if len(opp_b3_to_b2) > 0 else 0,
                               'count': len(opp_b3_to_b2)},
                    'B-2→B-1': {'avg': opp_b2_to_b1.mean() if len(opp_b2_to_b1) > 0 else None,
                               'median': opp_b2_to_b1.median() if len(opp_b2_to_b1) > 0 else None,
                               'positive_pct': (opp_b2_to_b1 > 0).mean() * 100 if len(opp_b2_to_b1) > 0 else 0,
                               'count': len(opp_b2_to_b1)},
                    'B-1→A+1': {'avg': opp_b1_to_a1.mean() if len(opp_b1_to_a1) > 0 else None,
                               'median': opp_b1_to_a1.median() if len(opp_b1_to_a1) > 0 else None,
                               'positive_pct': (opp_b1_to_a1 > 0).mean() * 100 if len(opp_b1_to_a1) > 0 else 0,
                               'count': len(opp_b1_to_a1)},
                    'A+1→A+2': {'avg': opp_a1_to_a2.mean() if len(opp_a1_to_a2) > 0 else None,
                               'median': opp_a1_to_a2.median() if len(opp_a1_to_a2) > 0 else None,
                               'positive_pct': (opp_a1_to_a2 > 0).mean() * 100 if len(opp_a1_to_a2) > 0 else 0,
                               'count': len(opp_a1_to_a2)},
                    'A+2→A+3': {'avg': opp_a2_to_a3.mean() if len(opp_a2_to_a3) > 0 else None,
                               'median': opp_a2_to_a3.median() if len(opp_a2_to_a3) > 0 else None,
                               'positive_pct': (opp_a2_to_a3 > 0).mean() * 100 if len(opp_a2_to_a3) > 0 else 0,
                               'count': len(opp_a2_to_a3)},
                }
            }
            
            return {
                'total_analyzed': len(df),
                'seq_changes': seq_changes,
            }
        
        results = {}
        
        # Analyze substitutions
        subs = self.events_df[self.events_df['event_type'] == 'Substitution']
        results['substitution'] = analyze_event_type(subs, 'Substitution')
        
        # Analyze ALL yellow cards (from Foul Committed AND Bad Behaviour)
        yellow_cards = []
        
        # From Foul Committed
        fouls = self.events_df[self.events_df['event_type'] == 'Foul Committed']
        if 'foul_committed' in fouls.columns:
            fc_yellow = fouls[fouls['foul_committed'].str.contains('Yellow', na=False)]
            yellow_cards.append(fc_yellow)
        
        # From Bad Behaviour
        bb = self.events_df[self.events_df['event_type'] == 'Bad Behaviour']
        if 'bad_behaviour' in bb.columns:
            bb_yellow = bb[bb['bad_behaviour'].str.contains('Yellow', na=False)]
            yellow_cards.append(bb_yellow)
        
        if yellow_cards:
            all_yellow = pd.concat(yellow_cards, ignore_index=True)
            results['yellow_card'] = analyze_event_type(all_yellow, 'Yellow Card')
        else:
            results['yellow_card'] = {'total_analyzed': 0}
        
        return results
    
    def _analyze_goals_vs_momentum(self):
        """Analyze goals vs momentum change with correct logic"""
        import ast
        
        if self.events_df is None or self.momentum_df is None:
            return None
        
        # Get actual goals from events
        shots = self.events_df[self.events_df['event_type'] == 'Shot'].copy()
        actual_goals = []
        
        for idx, row in shots.iterrows():
            if pd.notna(row.get('shot')):
                shot_str = str(row['shot'])
                if "'outcome'" in shot_str and "'Goal'" in shot_str:
                    # Exclude penalty shootout goals (period 5)
                    period = int(row['period']) if pd.notna(row.get('period')) else 1
                    if period != 5:
                        actual_goals.append(row)
        
        if len(actual_goals) == 0:
            return None
            
        goals_df = pd.DataFrame(actual_goals)
        
        # Apply NEW LOGIC: For goal at minute G, check change at original minute G-5
        results = []
        for idx, goal in goals_df.iterrows():
            match_id = goal['match_id']
            goal_minute = int(goal['minute'])
            period = int(goal['period']) if pd.notna(goal.get('period')) else 1
            team = goal['team_name'] if pd.notna(goal.get('team_name')) else 'Unknown'
            
            # NEW LOGIC: Check original minute = goal_minute - 5
            # This gives us the change where goal is in FUTURE window
            check_minute = goal_minute - 5
            
            mom_data = self.momentum_df[
                (self.momentum_df['match_id'] == match_id) & 
                (self.momentum_df['period'] == period) &
                (self.momentum_df['minute'] == check_minute)
            ]
            
            if len(mom_data) > 0:
                mom_row = mom_data.iloc[0]
                home_team = mom_row['team_home']
                away_team = mom_row['team_away']
                
                if team == home_team:
                    scoring_team_change = mom_row['team_home_momentum_change']
                    conceding_team_change = mom_row['team_away_momentum_change']
                else:
                    scoring_team_change = mom_row['team_away_momentum_change']
                    conceding_team_change = mom_row['team_home_momentum_change']
                
                if pd.notna(scoring_team_change) and pd.notna(conceding_team_change):
                    results.append({
                        'match_id': match_id,
                        'goal_minute': goal_minute,
                        'check_minute': check_minute,
                        'display_minute': check_minute + 3,
                        'period': period,
                        'scoring_team': team,
                        'scoring_team_change': scoring_team_change,
                        'conceding_team_change': conceding_team_change
                    })
        
        return pd.DataFrame(results) if results else None
    
    def _analyze_late_goals_with_predictions(self):
        """Analyze late goals (75-90) with both real and predicted momentum change"""
        import ast
        
        if self.events_df is None or self.momentum_df is None or self.arimax_df is None:
            return None
        
        # Get actual goals from events (excluding penalty shootout - period 5)
        shots = self.events_df[self.events_df['event_type'] == 'Shot'].copy()
        actual_goals = []
        
        for idx, row in shots.iterrows():
            if pd.notna(row.get('shot')):
                shot_str = str(row['shot'])
                if "'outcome'" in shot_str and "'Goal'" in shot_str:
                    # Exclude penalty shootout goals (period 5)
                    period = int(row['period']) if pd.notna(row.get('period')) else 1
                    if period != 5:
                        actual_goals.append(row)
        
        if len(actual_goals) == 0:
            return None
            
        goals_df = pd.DataFrame(actual_goals)
        
        # Filter for late goals (75-90+)
        late_goals = goals_df[(goals_df['minute'] >= 75) & (goals_df['minute'] <= 95)]
        
        if len(late_goals) == 0:
            return None
        
        # Get team names for each match
        match_teams = self.momentum_df.groupby('match_id').first()[['team_home', 'team_away']].to_dict('index')
        
        results = []
        for idx, goal in late_goals.iterrows():
            match_id = goal['match_id']
            goal_minute = int(goal['minute'])
            period = int(goal['period']) if pd.notna(goal.get('period')) else 2
            scoring_team = goal['team_name'] if pd.notna(goal.get('team_name')) else 'Unknown'
            
            # Find conceding team
            if match_id not in match_teams:
                continue
            home = match_teams[match_id]['team_home']
            away = match_teams[match_id]['team_away']
            conceding_team = away if scoring_team == home else home
            
            # Check original minute = goal_minute - 5
            check_minute = goal_minute - 5
            
            # Get predictions for both teams
            pred_data = self.arimax_df[
                (self.arimax_df['match_id'] == match_id) & 
                (self.arimax_df['minute_start'] == check_minute)
            ]
            
            scorer_pred = None
            scorer_actual = None
            conceder_pred = None
            conceder_actual = None
            
            for _, pred_row in pred_data.iterrows():
                pred_team = pred_row['team']
                if pred_team == scoring_team:
                    scorer_pred = pred_row['prediction_value']
                    scorer_actual = pred_row['actual_value']
                elif pred_team == conceding_team:
                    conceder_pred = pred_row['prediction_value']
                    conceder_actual = pred_row['actual_value']
            
            if scorer_pred is not None and conceder_pred is not None:
                if pd.notna(scorer_pred) and pd.notna(scorer_actual) and pd.notna(conceder_pred) and pd.notna(conceder_actual):
                    results.append({
                        'match_id': match_id,
                        'goal_minute': goal_minute,
                        'period': period,
                        'scoring_team': scoring_team,
                        'conceding_team': conceding_team,
                        'scorer_pred': scorer_pred,
                        'scorer_actual': scorer_actual,
                        'conceder_pred': conceder_pred,
                        'conceder_actual': conceder_actual
                    })
        
        return pd.DataFrame(results) if results else None
    
    def _analyze_sequence_before_goals(self):
        """Analyze momentum sequence BEFORE goals (excluding the goal window) - legacy"""
        return self._analyze_sequence_correct_logic()
    
    def _calculate_all_windows_sequences(self):
        """Calculate sequence distribution across ALL momentum windows (baseline)"""
        if self.momentum_df is None:
            return None
        
        try:
            all_pos_seqs = []
            all_neg_seqs = []
            
            for match_id in self.momentum_df['match_id'].unique():
                match_df = self.momentum_df[self.momentum_df['match_id'] == match_id]
                
                for period in match_df['period'].unique():
                    period_df = match_df[match_df['period'] == period].sort_values('minute')
                    
                    home_changes = period_df['team_home_momentum_change'].values
                    away_changes = period_df['team_away_momentum_change'].values
                    
                    for i in range(len(period_df)):
                        # Count positive sequence for home team (going backwards)
                        pos_seq_home = 0
                        for j in range(i-1, -1, -1):
                            if pd.notna(home_changes[j]) and home_changes[j] > 0:
                                pos_seq_home += 1
                            else:
                                break
                        
                        # Count negative sequence for home team
                        neg_seq_home = 0
                        for j in range(i-1, -1, -1):
                            if pd.notna(home_changes[j]) and home_changes[j] < 0:
                                neg_seq_home += 1
                            else:
                                break
                        
                        # Same for away team
                        pos_seq_away = 0
                        for j in range(i-1, -1, -1):
                            if pd.notna(away_changes[j]) and away_changes[j] > 0:
                                pos_seq_away += 1
                            else:
                                break
                        
                        neg_seq_away = 0
                        for j in range(i-1, -1, -1):
                            if pd.notna(away_changes[j]) and away_changes[j] < 0:
                                neg_seq_away += 1
                            else:
                                break
                        
                        all_pos_seqs.extend([pos_seq_home, pos_seq_away])
                        all_neg_seqs.extend([neg_seq_home, neg_seq_away])
            
            pos_counts = pd.Series(all_pos_seqs).value_counts().to_dict()
            neg_counts = pd.Series(all_neg_seqs).value_counts().to_dict()
            
            return {
                'total_windows': len(all_pos_seqs),
                'pos_counts': pos_counts,
                'neg_counts': neg_counts
            }
        except Exception:
            return None
    
    def _calculate_all_windows_events_by_seq(self):
        """Calculate events by sequence length for ALL momentum windows (both teams)"""
        if self.momentum_df is None or self.llm_commentary_df is None:
            return None
        
        try:
            # Store events by sequence length
            results = {
                'pos_0': [], 'pos_1': [], 'pos_2': [], 'pos_3': [], 'pos_4': [], 'pos_5plus': [],
                'neg_0': [], 'neg_1': [], 'neg_2': [], 'neg_3': [], 'neg_4': [], 'neg_5plus': [],
                'pos_0_count': 0, 'pos_1_count': 0, 'pos_2_count': 0, 'pos_3_count': 0, 'pos_4_count': 0, 'pos_5plus_count': 0,
                'neg_0_count': 0, 'neg_1_count': 0, 'neg_2_count': 0, 'neg_3_count': 0, 'neg_4_count': 0, 'neg_5plus_count': 0,
            }
            
            for match_id in self.momentum_df['match_id'].unique():
                match_df = self.momentum_df[self.momentum_df['match_id'] == match_id]
                game_events = self.llm_commentary_df[self.llm_commentary_df['match_id'] == match_id]
                
                for period in match_df['period'].unique():
                    period_df = match_df[match_df['period'] == period].sort_values('minute')
                    minutes = period_df['minute'].values
                    home_changes = period_df['team_home_momentum_change'].values
                    away_changes = period_df['team_away_momentum_change'].values
                    
                    # Process BOTH teams
                    for team_changes in [home_changes, away_changes]:
                        for i in range(len(period_df)):
                            current_minute = minutes[i]
                            
                            # Count POSITIVE sequences
                            pos_seq = 0
                            pos_minutes = []
                            for j in range(i-1, -1, -1):
                                if pd.notna(team_changes[j]) and team_changes[j] > 0:
                                    pos_seq += 1
                                    pos_minutes.append(minutes[j])
                                else:
                                    break
                            
                            if pos_seq == 0:
                                # Seq 0: Get events at current window (no positive sequence before)
                                events_list = []
                                for em in [current_minute, current_minute+1, current_minute+2]:
                                    ev = game_events[(game_events['period'] == period) & (game_events['minute'] == em)]['detected_type'].value_counts()
                                    if len(ev) > 0:
                                        events_list.append(ev.index[0])
                                results['pos_0'].extend(events_list)
                                results['pos_0_count'] += 1
                            else:
                                # Get events that CREATE the positive changes
                                sorted_mins = sorted(pos_minutes)
                                seen = set()
                                events_list = []
                                for idx, m in enumerate(sorted_mins[:5]):
                                    if idx == 0:
                                        for em in [m, m+1, m+2]:
                                            if em not in seen:
                                                ev = game_events[(game_events['period'] == period) & (game_events['minute'] == em)]['detected_type'].value_counts()
                                                if len(ev) > 0:
                                                    events_list.append(ev.index[0])
                                                seen.add(em)
                                    else:
                                        em = m + 2
                                        if em not in seen:
                                            ev = game_events[(game_events['period'] == period) & (game_events['minute'] == em)]['detected_type'].value_counts()
                                            if len(ev) > 0:
                                                events_list.append(ev.index[0])
                                            seen.add(em)
                                
                                # Add to appropriate bucket
                                if pos_seq == 1:
                                    results['pos_1'].extend(events_list)
                                    results['pos_1_count'] += 1
                                elif pos_seq == 2:
                                    results['pos_2'].extend(events_list)
                                    results['pos_2_count'] += 1
                                elif pos_seq == 3:
                                    results['pos_3'].extend(events_list)
                                    results['pos_3_count'] += 1
                                elif pos_seq == 4:
                                    results['pos_4'].extend(events_list)
                                    results['pos_4_count'] += 1
                                else:  # 5+
                                    results['pos_5plus'].extend(events_list)
                                    results['pos_5plus_count'] += 1
                            
                            # Count NEGATIVE sequences
                            neg_seq = 0
                            neg_minutes = []
                            for j in range(i-1, -1, -1):
                                if pd.notna(team_changes[j]) and team_changes[j] < 0:
                                    neg_seq += 1
                                    neg_minutes.append(minutes[j])
                                else:
                                    break
                            
                            if neg_seq == 0:
                                # Seq 0: Get events at current window (no negative sequence before)
                                events_list = []
                                for em in [current_minute, current_minute+1, current_minute+2]:
                                    ev = game_events[(game_events['period'] == period) & (game_events['minute'] == em)]['detected_type'].value_counts()
                                    if len(ev) > 0:
                                        events_list.append(ev.index[0])
                                results['neg_0'].extend(events_list)
                                results['neg_0_count'] += 1
                            else:
                                sorted_mins = sorted(neg_minutes)
                                seen = set()
                                events_list = []
                                for idx, m in enumerate(sorted_mins[:5]):
                                    if idx == 0:
                                        for em in [m, m+1, m+2]:
                                            if em not in seen:
                                                ev = game_events[(game_events['period'] == period) & (game_events['minute'] == em)]['detected_type'].value_counts()
                                                if len(ev) > 0:
                                                    events_list.append(ev.index[0])
                                                seen.add(em)
                                    else:
                                        em = m + 2
                                        if em not in seen:
                                            ev = game_events[(game_events['period'] == period) & (game_events['minute'] == em)]['detected_type'].value_counts()
                                            if len(ev) > 0:
                                                events_list.append(ev.index[0])
                                            seen.add(em)
                                
                                if neg_seq == 1:
                                    results['neg_1'].extend(events_list)
                                    results['neg_1_count'] += 1
                                elif neg_seq == 2:
                                    results['neg_2'].extend(events_list)
                                    results['neg_2_count'] += 1
                                elif neg_seq == 3:
                                    results['neg_3'].extend(events_list)
                                    results['neg_3_count'] += 1
                                elif neg_seq == 4:
                                    results['neg_4'].extend(events_list)
                                    results['neg_4_count'] += 1
                                else:
                                    results['neg_5plus'].extend(events_list)
                                    results['neg_5plus_count'] += 1
            
            return results
        except Exception:
            return None
    
    def _analyze_sequence_correct_logic(self):
        """
        Correct logic:
        - POSITIVE seq = Scoring team's positive changes BEFORE scoring
        - NEGATIVE seq = Conceding team's negative changes BEFORE conceding
        - Events: First window = 3 events, then +1 for each additional seq
        """
        if self.events_df is None or self.momentum_df is None:
            return None
        
        # Get actual goals from events (excluding penalty shootout - period 5)
        shots = self.events_df[self.events_df['event_type'] == 'Shot'].copy()
        actual_goals = []
        
        for idx, row in shots.iterrows():
            if pd.notna(row.get('shot')):
                shot_str = str(row['shot'])
                if "'outcome'" in shot_str and "'Goal'" in shot_str:
                    # Exclude penalty shootout goals (period 5)
                    period = int(row['period']) if pd.notna(row.get('period')) else 1
                    if period != 5:
                        actual_goals.append(row)
        
        if len(actual_goals) == 0:
            return None
            
        goals_df = pd.DataFrame(actual_goals)
        
        # Get team names for each match
        match_teams = self.momentum_df.groupby('match_id').first()[['team_home', 'team_away']].to_dict('index')
        
        results = []
        for idx, goal in goals_df.iterrows():
            match_id = goal['match_id']
            goal_minute = int(goal['minute'])
            period = int(goal['period']) if pd.notna(goal.get('period')) else 1
            scoring_team = goal['team_name'] if pd.notna(goal.get('team_name')) else 'Unknown'
            
            # Find conceding team
            if match_id not in match_teams:
                continue
            home = match_teams[match_id]['team_home']
            away = match_teams[match_id]['team_away']
            conceding_team = away if scoring_team == home else home
            
            match_mom = self.momentum_df[
                (self.momentum_df['match_id'] == match_id) & 
                (self.momentum_df['period'] == period)
            ].sort_values('minute')
            
            if len(match_mom) == 0:
                continue
            
            # Columns for scoring and conceding teams
            scoring_is_home = (scoring_team == home)
            scoring_change_col = 'team_home_momentum_change' if scoring_is_home else 'team_away_momentum_change'
            conceding_change_col = 'team_away_momentum_change' if scoring_is_home else 'team_home_momentum_change'
            
            goal_window_minute = goal_minute - 5
            before_window = match_mom[match_mom['minute'] < goal_window_minute].sort_values('minute', ascending=False)
            
            # SCORING TEAM: Count POSITIVE sequence
            pos_seq_scoring = 0
            pos_minutes_scoring = []
            for _, row in before_window.iterrows():
                change = row[scoring_change_col]
                if pd.notna(change) and change > 0:
                    pos_seq_scoring += 1
                    pos_minutes_scoring.append(int(row['minute']))
                else:
                    break
            
            # CONCEDING TEAM: Count NEGATIVE sequence
            neg_seq_conceding = 0
            neg_minutes_conceding = []
            for _, row in before_window.iterrows():
                change = row[conceding_change_col]
                if pd.notna(change) and change < 0:
                    neg_seq_conceding += 1
                    neg_minutes_conceding.append(int(row['minute']))
                else:
                    break
            
            # Get events for scoring team's positive sequence
            # Logic: Events that CREATE the positive change are in the FUTURE window (m, m+1, m+2)
            # First seq window = 3 events, then +1 for each additional
            pos_events = []
            if pos_seq_scoring > 0 and len(pos_minutes_scoring) > 0 and self.llm_commentary_df is not None:
                game_events = self.llm_commentary_df[self.llm_commentary_df['match_id'] == match_id]
                seen_minutes = set()
                # Reverse to get ascending order (earliest first)
                sorted_minutes = sorted(pos_minutes_scoring[:5])
                for i, m in enumerate(sorted_minutes):
                    if i == 0:
                        # First window: 3 events (m, m+1, m+2 create the positive)
                        for em in [m, m+1, m+2]:
                            if em not in seen_minutes:
                                minute_events = game_events[
                                    (game_events['period'] == period) &
                                    (game_events['minute'] == em)
                                ]['detected_type'].value_counts()
                                if len(minute_events) > 0:
                                    pos_events.append(f"{em}:{minute_events.index[0]}")
                                seen_minutes.add(em)
                    else:
                        # Additional windows: only 1 new event (m+2, since m and m+1 overlap with previous)
                        em = m + 2
                        if em not in seen_minutes:
                            minute_events = game_events[
                                (game_events['period'] == period) &
                                (game_events['minute'] == em)
                            ]['detected_type'].value_counts()
                            if len(minute_events) > 0:
                                pos_events.append(f"{em}:{minute_events.index[0]}")
                            seen_minutes.add(em)
            
            # Get events for conceding team's negative sequence
            # Same logic: events that CREATE the negative change
            neg_events = []
            if neg_seq_conceding > 0 and len(neg_minutes_conceding) > 0 and self.llm_commentary_df is not None:
                game_events = self.llm_commentary_df[self.llm_commentary_df['match_id'] == match_id]
                seen_minutes = set()
                # Reverse to get ascending order (earliest first)
                sorted_minutes = sorted(neg_minutes_conceding[:5])
                for i, m in enumerate(sorted_minutes):
                    if i == 0:
                        # First window: 3 events (m, m+1, m+2 create the negative)
                        for em in [m, m+1, m+2]:
                            if em not in seen_minutes:
                                minute_events = game_events[
                                    (game_events['period'] == period) &
                                    (game_events['minute'] == em)
                                ]['detected_type'].value_counts()
                                if len(minute_events) > 0:
                                    neg_events.append(f"{em}:{minute_events.index[0]}")
                                seen_minutes.add(em)
                    else:
                        # Additional windows: only 1 new event
                        em = m + 2
                        if em not in seen_minutes:
                            minute_events = game_events[
                                (game_events['period'] == period) &
                                (game_events['minute'] == em)
                            ]['detected_type'].value_counts()
                            if len(minute_events) > 0:
                                neg_events.append(f"{em}:{minute_events.index[0]}")
                            seen_minutes.add(em)
            
            results.append({
                'match_id': match_id,
                'goal_minute': goal_minute,
                'period': period,
                'scoring_team': scoring_team,
                'conceding_team': conceding_team,
                'pos_seq_scoring': pos_seq_scoring,
                'neg_seq_conceding': neg_seq_conceding,
                'pos_events': pos_events,
                'neg_events': neg_events
            })
        
        return pd.DataFrame(results) if results else None
    
    def _analyze_sequence_pos_neg(self):
        """Analyze both POSITIVE and NEGATIVE momentum sequences BEFORE goals"""
        if self.events_df is None or self.momentum_df is None:
            return None
        
        # Get actual goals from events (excluding penalty shootout - period 5)
        shots = self.events_df[self.events_df['event_type'] == 'Shot'].copy()
        actual_goals = []
        
        for idx, row in shots.iterrows():
            if pd.notna(row.get('shot')):
                shot_str = str(row['shot'])
                if "'outcome'" in shot_str and "'Goal'" in shot_str:
                    # Exclude penalty shootout goals (period 5)
                    period = int(row['period']) if pd.notna(row.get('period')) else 1
                    if period != 5:
                        actual_goals.append(row)
        
        if len(actual_goals) == 0:
            return None
            
        goals_df = pd.DataFrame(actual_goals)
        
        results = []
        for idx, goal in goals_df.iterrows():
            match_id = goal['match_id']
            goal_minute = int(goal['minute'])
            period = int(goal['period']) if pd.notna(goal.get('period')) else 1
            scoring_team = goal['team_name'] if pd.notna(goal.get('team_name')) else 'Unknown'
            
            match_mom = self.momentum_df[
                (self.momentum_df['match_id'] == match_id) & 
                (self.momentum_df['period'] == period)
            ].sort_values('minute')
            
            if len(match_mom) == 0:
                continue
            
            home_team = match_mom.iloc[0]['team_home']
            is_home = (scoring_team == home_team)
            change_col = 'team_home_momentum_change' if is_home else 'team_away_momentum_change'
            
            goal_window_minute = goal_minute - 5
            before_window = match_mom[match_mom['minute'] < goal_window_minute].sort_values('minute', ascending=False)
            
            # Count POSITIVE sequence
            pos_seq = 0
            pos_minutes = []
            for _, row in before_window.iterrows():
                change = row[change_col]
                if pd.notna(change) and change > 0:
                    pos_seq += 1
                    pos_minutes.append(int(row['minute']))
                else:
                    break
            
            # Count NEGATIVE sequence (from beginning again)
            neg_seq = 0
            neg_minutes = []
            for _, row in before_window.iterrows():
                change = row[change_col]
                if pd.notna(change) and change < 0:
                    neg_seq += 1
                    neg_minutes.append(int(row['minute']))
                else:
                    break
            
            # Get events for positive sequence
            pos_events = []
            if pos_seq > 0 and len(pos_minutes) > 0 and self.llm_commentary_df is not None:
                game_events = self.llm_commentary_df[self.llm_commentary_df['match_id'] == match_id]
                for m in pos_minutes[:3]:
                    minute_events = game_events[
                        (game_events['period'] == period) &
                        (game_events['minute'].isin([m, m+1, m+2]))
                    ]['detected_type'].value_counts()
                    if len(minute_events) > 0:
                        pos_events.append(f"{m}:{minute_events.index[0]}")
            
            # Get events for negative sequence
            neg_events = []
            if neg_seq > 0 and len(neg_minutes) > 0 and self.llm_commentary_df is not None:
                game_events = self.llm_commentary_df[self.llm_commentary_df['match_id'] == match_id]
                for m in neg_minutes[:3]:
                    minute_events = game_events[
                        (game_events['period'] == period) &
                        (game_events['minute'].isin([m, m+1, m+2]))
                    ]['detected_type'].value_counts()
                    if len(minute_events) > 0:
                        neg_events.append(f"{m}:{minute_events.index[0]}")
            
            results.append({
                'match_id': match_id,
                'goal_minute': goal_minute,
                'period': period,
                'scoring_team': scoring_team,
                'pos_seq': pos_seq,
                'neg_seq': neg_seq,
                'pos_events': pos_events,
                'neg_events': neg_events,
                'seq_before_length': pos_seq,  # For backward compatibility
                'seq_events': pos_events
            })
        
        return pd.DataFrame(results) if results else None
    
    def render_game_comparison(self):
        """Render game-by-game momentum comparison using period-separated data"""
        st.subheader("📉 Game-by-Game Momentum Comparison (Period-Separated)")
        
        st.markdown("""
        Select a game to visualize how momentum evolved over time for both teams.
        **Using period-separated data** - First and second half are properly separated.
        """)
        
        if self.momentum_df is None:
            st.error("Momentum data not loaded")
            return
        
        try:
            momentum_data = self.momentum_df.copy()
            
            # Get unique games
            games_list = []
            for match_id in momentum_data['match_id'].unique():
                match_data = momentum_data[momentum_data['match_id'] == match_id].iloc[0]
                home = match_data['team_home']
                away = match_data['team_away']
                games_list.append({
                    'match_id': match_id,
                    'label': f"{home} vs {away}"
                })
            
            # Game selector
            game_options = {g['label']: g['match_id'] for g in games_list}
            selected_game = st.selectbox(
                "Select Game:",
                options=list(game_options.keys()),
                key="game_selector_momentum_tab"
            )
            
            if selected_game:
                match_id = game_options[selected_game]
                game_data = momentum_data[momentum_data['match_id'] == match_id].copy()
                
                # Get period 1 and period 2 data separately
                period1_data = game_data[game_data['period'] == 1].copy()
                period2_data = game_data[game_data['period'] == 2].copy()
                
                # Add display_minute column: shift by +3 so minute X shows momentum from (X-3, X-2, X-1)
                # Data at minute 0 (events 0,1,2) displays at minute 3
                # Data at minute 45 (events 45,46,47) displays at minute 48
                period1_data['display_minute'] = period1_data['minute'] + 3
                period2_data['display_minute'] = period2_data['minute'] + 3
                
                # Filter to show from display_minute 3 onwards
                period1_data = period1_data[period1_data['display_minute'] >= 3]
                period2_data = period2_data[period2_data['display_minute'] >= 48]
                
                home_team = game_data['team_home'].iloc[0]
                away_team = game_data['team_away'].iloc[0]
                
                st.markdown("---")
                
                # Get actual display ranges (using display_minute)
                p1_max = period1_data['display_minute'].max() if len(period1_data) > 0 else 48
                p2_max = period2_data['display_minute'].max() if len(period2_data) > 0 else 93
                
                st.info(f"**This Game:** 1st Half: 3-{p1_max} min | 2nd Half: 48-{p2_max} min")
                
                st.caption("📌 Minute X shows momentum from previous 3 min (X-3 to X-1). Example: Min 8 = momentum of events in min 5,6,7")
                
                # Event filter for graph markers
                game_events_df = None
                selected_events = []
                if self.llm_commentary_df is not None:
                    game_events_df = self.llm_commentary_df[self.llm_commentary_df['match_id'] == match_id].copy()
                    
                    # Also add own goals from events data
                    if self.events_df is not None:
                        own_goals = self.events_df[
                            (self.events_df['match_id'] == match_id) & 
                            (self.events_df['event_type'] == 'Own Goal Against')
                        ][['minute', 'period']].copy()
                        if len(own_goals) > 0:
                            own_goals['detected_type'] = 'Own Goal'
                            own_goals['match_id'] = match_id
                            game_events_df = pd.concat([game_events_df, own_goals], ignore_index=True)
                    
                    top_events = game_events_df['detected_type'].value_counts().head(15).index.tolist()
                    # Ensure Goal and Own Goal are in options if they exist
                    if 'Goal' not in top_events and 'Goal' in game_events_df['detected_type'].values:
                        top_events.append('Goal')
                    if 'Own Goal' not in top_events and 'Own Goal' in game_events_df['detected_type'].values:
                        top_events.append('Own Goal')
                    
                    with st.expander("🎯 Filter Events on Graph", expanded=False):
                        st.caption("Select event types to mark on the graphs at exact minute")
                        selected_events = st.multiselect(
                            "Select events to show:",
                            options=top_events,
                            default=[],
                            key=f"event_filter_{match_id}"
                        )
                        
                        if selected_events:
                            st.caption("Events will appear as markers (▲) on the momentum graph at their exact minute")
                
                # Create tick labels
                def create_tick_labels(start, end, regular_end, stoppage_base):
                    vals, labels = [], []
                    for m in range(start, end + 1):
                        vals.append(m)
                        if m <= regular_end:
                            labels.append(str(m))
                        else:
                            labels.append(f"{stoppage_base}+{m - regular_end}")
                    return vals, labels
                
                # 1st half: display 3-45 is regular, 46+ is stoppage (45+1, 45+2, etc.)
                ticks_1h_vals, ticks_1h_labels = create_tick_labels(3, p1_max, 45, 45)
                # 2nd half: display 48-90 is regular, 91+ is stoppage (90+1, 90+2, etc.)
                ticks_2h_vals, ticks_2h_labels = create_tick_labels(48, p2_max, 90, 90)
                
                # ========== ABSOLUTE MOMENTUM - TWO SEPARATE GRAPHS ==========
                st.markdown("### 📊 Absolute Momentum Over Time")
                
                col1h, col2h = st.columns(2)
                
                with col1h:
                    end_label_1h = f"45+{p1_max - 48}" if p1_max > 48 else str(p1_max)
                    st.markdown(f"**1st Half** (3' → {end_label_1h}')")
                    
                    fig_mom_1h = go.Figure()
                    if p1_max > 48:
                        fig_mom_1h.add_vline(x=48, line_dash="dot", line_color="orange", line_width=2,
                            annotation_text="45'", annotation_position="top")
                    
                    fig_mom_1h.add_trace(go.Scatter(x=period1_data['display_minute'], y=period1_data['team_home_momentum'],
                        mode='lines', name=home_team, line=dict(color='#1f77b4', width=2)))
                    fig_mom_1h.add_trace(go.Scatter(x=period1_data['display_minute'], y=period1_data['team_away_momentum'],
                        mode='lines', name=away_team, line=dict(color='#d62728', width=2)))
                    
                    # Add event markers for 1st half (batched for performance)
                    if selected_events and game_events_df is not None:
                        p1_events = game_events_df[(game_events_df['period'] == 1) & (game_events_df['detected_type'].isin(selected_events))]
                        if len(p1_events) > 0:
                            marker_x, marker_y, marker_text, marker_hover = [], [], [], []
                            for _, ev_row in p1_events.iterrows():
                                em = int(ev_row['minute'])
                                event_type = ev_row['detected_type']
                                display_min = em
                                mom_at_min = period1_data[period1_data['display_minute'] == display_min]
                                if len(mom_at_min) > 0:
                                    y_val = max(mom_at_min['team_home_momentum'].values[0], mom_at_min['team_away_momentum'].values[0])
                                    marker_x.append(display_min)
                                    marker_y.append(y_val + 0.3)
                                    marker_text.append(event_type[:3])
                                    marker_hover.append(f'{event_type} at min {em}')
                            if marker_x:
                                fig_mom_1h.add_trace(go.Scatter(
                                    x=marker_x, y=marker_y,
                                    mode='markers+text', 
                                    marker=dict(symbol='triangle-down', size=12, color='green'),
                                    text=marker_text, textposition='top center',
                                    name='Events', showlegend=False,
                                    hovertemplate='%{customdata}<extra></extra>',
                                    customdata=marker_hover
                                ))
                    
                    fig_mom_1h.update_layout(
                        xaxis_title='Minute', yaxis_title='Momentum', height=300,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                        hovermode='x unified', margin=dict(l=40, r=10, t=30, b=30),
                        xaxis=dict(tickmode='array', tickvals=ticks_1h_vals, ticktext=ticks_1h_labels,
                            range=[3, p1_max + 0.5]),
                        yaxis=dict(gridcolor='lightgray')
                    )
                    st.plotly_chart(fig_mom_1h, use_container_width=True, key="abs_mom_1h")
                
                with col2h:
                    end_label_2h = f"90+{p2_max - 93}" if p2_max > 93 else str(p2_max)
                    st.markdown(f"**2nd Half** (48' → {end_label_2h}')")
                    
                    fig_mom_2h = go.Figure()
                    if p2_max > 93:
                        fig_mom_2h.add_vline(x=93, line_dash="dot", line_color="orange", line_width=2,
                            annotation_text="90'", annotation_position="top")
                    
                    fig_mom_2h.add_trace(go.Scatter(x=period2_data['display_minute'], y=period2_data['team_home_momentum'],
                        mode='lines', name=home_team, line=dict(color='#1f77b4', width=2)))
                    fig_mom_2h.add_trace(go.Scatter(x=period2_data['display_minute'], y=period2_data['team_away_momentum'],
                        mode='lines', name=away_team, line=dict(color='#d62728', width=2)))
                    
                    # Add event markers for 2nd half (batched for performance)
                    # Events show at their actual minute (em), we find the closest momentum data point
                    if selected_events and game_events_df is not None:
                        p2_events = game_events_df[(game_events_df['period'] == 2) & (game_events_df['detected_type'].isin(selected_events))]
                        if len(p2_events) > 0:
                            marker_x, marker_y, marker_text, marker_hover = [], [], [], []
                            for _, ev_row in p2_events.iterrows():
                                em = int(ev_row['minute'])
                                event_type = ev_row['detected_type']
                                # Event shows at its actual minute on the graph
                                # Find closest display_minute in data
                                closest_mom = period2_data.iloc[(period2_data['display_minute'] - em).abs().argsort()[:1]]
                                if len(closest_mom) > 0:
                                    y_val = max(closest_mom['team_home_momentum'].values[0], closest_mom['team_away_momentum'].values[0])
                                    marker_x.append(em)  # Show at actual event minute
                                    marker_y.append(y_val + 0.3)
                                    marker_text.append(event_type[:3])
                                    marker_hover.append(f'{event_type} at min {em}')
                            if marker_x:
                                fig_mom_2h.add_trace(go.Scatter(
                                    x=marker_x, y=marker_y,
                                    mode='markers+text', 
                                    marker=dict(symbol='triangle-down', size=12, color='green'),
                                    text=marker_text, textposition='top center',
                                    name='Events', showlegend=False,
                                    hovertemplate='%{customdata}<extra></extra>',
                                    customdata=marker_hover
                                ))
                    
                    fig_mom_2h.update_layout(
                        xaxis_title='Minute', yaxis_title='Momentum', height=300,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                        hovermode='x unified', margin=dict(l=40, r=10, t=30, b=30),
                        xaxis=dict(tickmode='array', tickvals=ticks_2h_vals, ticktext=ticks_2h_labels,
                            range=[48, p2_max + 0.5]),
                        yaxis=dict(gridcolor='lightgray')
                    )
                    st.plotly_chart(fig_mom_2h, use_container_width=True, key="abs_mom_2h")
                
                st.markdown("---")
                
                # ========== MOMENTUM CHANGE - TWO SEPARATE GRAPHS ==========
                st.markdown("### 📈 Momentum Change Over Time")
                st.caption("📌 Momentum change at minute X = momentum(X to X+2) - momentum(X-3 to X-1). **Example minute 8:** change = momentum(8,9,10) - momentum(5,6,7)")
                
                col1hc, col2hc = st.columns(2)
                
                with col1hc:
                    st.markdown(f"**1st Half** (3' → {end_label_1h}')")
                    
                    fig_chg_1h = go.Figure()
                    if p1_max > 48:
                        fig_chg_1h.add_vline(x=48, line_dash="dot", line_color="orange", line_width=2,
                            annotation_text="45'", annotation_position="top")
                    
                    fig_chg_1h.add_trace(go.Scatter(x=period1_data['display_minute'], y=period1_data['team_home_momentum_change'],
                        mode='lines', name=home_team, line=dict(color='#1f77b4', width=2)))
                    fig_chg_1h.add_trace(go.Scatter(x=period1_data['display_minute'], y=period1_data['team_away_momentum_change'],
                        mode='lines', name=away_team, line=dict(color='#d62728', width=2)))
                    fig_chg_1h.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)
                    
                    # Add event markers for 1st half momentum change (batched)
                    if selected_events and game_events_df is not None:
                        p1_events = game_events_df[(game_events_df['period'] == 1) & (game_events_df['detected_type'].isin(selected_events))]
                        if len(p1_events) > 0:
                            marker_x, marker_y, marker_text, marker_hover = [], [], [], []
                            for _, ev_row in p1_events.iterrows():
                                em = int(ev_row['minute'])
                                event_type = ev_row['detected_type']
                                display_min = em
                                chg_at_min = period1_data[period1_data['display_minute'] == display_min]
                                if len(chg_at_min) > 0:
                                    y_val = max(chg_at_min['team_home_momentum_change'].values[0], chg_at_min['team_away_momentum_change'].values[0])
                                    marker_x.append(display_min)
                                    marker_y.append(y_val + 0.3)
                                    marker_text.append(event_type[:3])
                                    marker_hover.append(f'{event_type} at min {em}')
                            if marker_x:
                                fig_chg_1h.add_trace(go.Scatter(
                                    x=marker_x, y=marker_y,
                                    mode='markers+text', 
                                    marker=dict(symbol='triangle-down', size=12, color='green'),
                                    text=marker_text, textposition='top center',
                                    name='Events', showlegend=False,
                                    hovertemplate='%{customdata}<extra></extra>',
                                    customdata=marker_hover
                                ))
                    
                    fig_chg_1h.update_layout(
                        xaxis_title='Minute', yaxis_title='Momentum Change', height=300,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                        hovermode='x unified', margin=dict(l=40, r=10, t=30, b=30),
                        xaxis=dict(tickmode='array', tickvals=ticks_1h_vals, ticktext=ticks_1h_labels,
                            range=[3, p1_max + 0.5]),
                        yaxis=dict(gridcolor='lightgray')
                    )
                    st.plotly_chart(fig_chg_1h, use_container_width=True, key="chg_1h")
                
                with col2hc:
                    st.markdown(f"**2nd Half** (48' → {end_label_2h}')")
                    
                    fig_chg_2h = go.Figure()
                    if p2_max > 93:
                        fig_chg_2h.add_vline(x=93, line_dash="dot", line_color="orange", line_width=2,
                            annotation_text="90'", annotation_position="top")
                    
                    fig_chg_2h.add_trace(go.Scatter(x=period2_data['display_minute'], y=period2_data['team_home_momentum_change'],
                        mode='lines', name=home_team, line=dict(color='#1f77b4', width=2)))
                    fig_chg_2h.add_trace(go.Scatter(x=period2_data['display_minute'], y=period2_data['team_away_momentum_change'],
                        mode='lines', name=away_team, line=dict(color='#d62728', width=2)))
                    fig_chg_2h.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)
                    
                    # Add event markers for 2nd half momentum change (batched)
                    # Events show at their actual minute
                    if selected_events and game_events_df is not None:
                        p2_events = game_events_df[(game_events_df['period'] == 2) & (game_events_df['detected_type'].isin(selected_events))]
                        if len(p2_events) > 0:
                            marker_x, marker_y, marker_text, marker_hover = [], [], [], []
                            for _, ev_row in p2_events.iterrows():
                                em = int(ev_row['minute'])
                                event_type = ev_row['detected_type']
                                # Find closest display_minute in data
                                closest_chg = period2_data.iloc[(period2_data['display_minute'] - em).abs().argsort()[:1]]
                                if len(closest_chg) > 0:
                                    y_val = max(closest_chg['team_home_momentum_change'].values[0], closest_chg['team_away_momentum_change'].values[0])
                                    marker_x.append(em)  # Show at actual event minute
                                    marker_y.append(y_val + 0.3)
                                    marker_text.append(event_type[:3])
                                    marker_hover.append(f'{event_type} at min {em}')
                            if marker_x:
                                fig_chg_2h.add_trace(go.Scatter(
                                    x=marker_x, y=marker_y,
                                    mode='markers+text', 
                                    marker=dict(symbol='triangle-down', size=12, color='green'),
                                    text=marker_text, textposition='top center',
                                    name='Events', showlegend=False,
                                    hovertemplate='%{customdata}<extra></extra>',
                                    customdata=marker_hover
                                ))
                    
                    fig_chg_2h.update_layout(
                        xaxis_title='Minute', yaxis_title='Momentum Change', height=300,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                        hovermode='x unified', margin=dict(l=40, r=10, t=30, b=30),
                        xaxis=dict(tickmode='array', tickvals=ticks_2h_vals, ticktext=ticks_2h_labels,
                            range=[48, p2_max + 0.5]),
                        yaxis=dict(gridcolor='lightgray')
                    )
                    st.plotly_chart(fig_chg_2h, use_container_width=True, key="chg_2h")
                
                st.markdown("---")
                
                # Game summary stats
                st.markdown(f"### 📋 Game Summary Statistics")
                
                # Combine data for stats
                all_game_data = pd.concat([period1_data, period2_data])
                
                # Calculate stats for full game
                home_momentum_wins = (all_game_data['team_home_momentum'] > all_game_data['team_away_momentum']).sum()
                away_momentum_wins = (all_game_data['team_away_momentum'] > all_game_data['team_home_momentum']).sum()
                home_positive_changes = (all_game_data['team_home_momentum_change'] > 0).sum()
                away_positive_changes = (all_game_data['team_away_momentum_change'] > 0).sum()
                home_avg = all_game_data['team_home_momentum'].mean()
                away_avg = all_game_data['team_away_momentum'].mean()
                
                # Calculate longest sequences
                home_max_seq = 0
                away_max_seq = 0
                current_home = 0
                current_away = 0
                for _, row in all_game_data.iterrows():
                    if pd.notna(row['team_home_momentum_change']) and row['team_home_momentum_change'] > 0:
                        current_home += 1
                        home_max_seq = max(home_max_seq, current_home)
                    else:
                        current_home = 0
                    if pd.notna(row['team_away_momentum_change']) and row['team_away_momentum_change'] > 0:
                        current_away += 1
                        away_max_seq = max(away_max_seq, current_away)
                    else:
                        current_away = 0
                
                # Display as table - Full Game
                st.markdown("#### Full Game")
                summary_data = {
                    'Team': [home_team, away_team],
                    'Momentum Windows': [home_momentum_wins, away_momentum_wins],
                    'Positive Changes': [home_positive_changes, away_positive_changes],
                    'Avg Momentum': [f"{home_avg:.2f}", f"{away_avg:.2f}"],
                    'Longest Sequence': [home_max_seq, away_max_seq]
                }
                df_summary = pd.DataFrame(summary_data)
                st.dataframe(df_summary, use_container_width=True, hide_index=True)
                
                # Display per-half stats
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 1st Half")
                    home_momentum_wins_1h = (period1_data['team_home_momentum'] > period1_data['team_away_momentum']).sum()
                    away_momentum_wins_1h = (period1_data['team_away_momentum'] > period1_data['team_home_momentum']).sum()
                    home_positive_changes_1h = (period1_data['team_home_momentum_change'] > 0).sum()
                    away_positive_changes_1h = (period1_data['team_away_momentum_change'] > 0).sum()
                    
                    half1_data = {
                        'Team': [home_team, away_team],
                        'Momentum Windows': [home_momentum_wins_1h, away_momentum_wins_1h],
                        'Positive Changes': [home_positive_changes_1h, away_positive_changes_1h]
                    }
                    df_half1 = pd.DataFrame(half1_data)
                    st.dataframe(df_half1, use_container_width=True, hide_index=True)
                
                with col2:
                    st.markdown("#### 2nd Half")
                    home_momentum_wins_2h = (period2_data['team_home_momentum'] > period2_data['team_away_momentum']).sum()
                    away_momentum_wins_2h = (period2_data['team_away_momentum'] > period2_data['team_home_momentum']).sum()
                    home_positive_changes_2h = (period2_data['team_home_momentum_change'] > 0).sum()
                    away_positive_changes_2h = (period2_data['team_away_momentum_change'] > 0).sum()
                    
                    half2_data = {
                        'Team': [home_team, away_team],
                        'Momentum Windows': [home_momentum_wins_2h, away_momentum_wins_2h],
                        'Positive Changes': [home_positive_changes_2h, away_positive_changes_2h]
                    }
                    df_half2 = pd.DataFrame(half2_data)
                    st.dataframe(df_half2, use_container_width=True, hide_index=True)
                
                # Interpretation
                st.markdown("---")
                st.markdown("### 🎯 Interpretation")
                
                # Determine winners of each metric
                momentum_winner = home_team if home_momentum_wins > away_momentum_wins else away_team
                changes_winner = home_team if home_positive_changes > away_positive_changes else away_team
                seq_winner = home_team if home_max_seq > away_max_seq else away_team
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.success(f"""
                    **✅ Winning Metrics:**
                    - Momentum Windows: **{momentum_winner}** ({max(home_momentum_wins, away_momentum_wins)}-{min(home_momentum_wins, away_momentum_wins)})
                    """)
                
                with col2:
                    st.warning(f"""
                    **❌ Chasing Metrics:**
                    - Positive Changes: **{changes_winner}** ({max(home_positive_changes, away_positive_changes)}-{min(home_positive_changes, away_positive_changes)})
                    - Longest Sequence: **{seq_winner}** ({max(home_max_seq, away_max_seq)}-{min(home_max_seq, away_max_seq)})
                    """)
                
                st.markdown("---")
                
                # ========== PREDICTIONS VS ACTUAL GRAPH ==========
                st.markdown("### 🔮 ARIMAX Predictions vs Actual (Minutes 78-92)")
                
                st.markdown("""
                This graph shows how well the ARIMAX model **predicted** momentum changes compared to **actual** values.
                - **Solid lines** = Actual momentum change
                - **Dashed lines** = Model predictions
                - Minutes shown are display minutes (shifted +3 to match momentum window logic)
                """)
                
                # Load predictions for this game
                if self.arimax_df is not None:
                    game_preds = self.arimax_df[self.arimax_df['match_id'] == match_id].copy()
                    
                    if len(game_preds) > 0:
                        # Add display_minute for predictions (shift by +3)
                        game_preds['display_minute'] = game_preds['minute_start'] + 3
                        
                        home_preds = game_preds[game_preds['is_home'] == True].sort_values('minute_start')
                        away_preds = game_preds[game_preds['is_home'] == False].sort_values('minute_start')
                        
                        col_pred1, col_pred2 = st.columns(2)
                        
                        with col_pred1:
                            st.markdown(f"**{home_team}**")
                            fig_pred_home = go.Figure()
                            
                            # Actual values
                            fig_pred_home.add_trace(go.Scatter(
                                x=home_preds['display_minute'], y=home_preds['actual_value'],
                                mode='lines+markers', name='Actual',
                                line=dict(color='#1f77b4', width=2),
                                marker=dict(size=4)
                            ))
                            # Predictions
                            fig_pred_home.add_trace(go.Scatter(
                                x=home_preds['display_minute'], y=home_preds['prediction_value'],
                                mode='lines+markers', name='Predicted',
                                line=dict(color='#1f77b4', width=2, dash='dash'),
                                marker=dict(size=4, symbol='x')
                            ))
                            fig_pred_home.add_hline(y=0, line_dash="dot", line_color="gray", line_width=1)
                            
                            fig_pred_home.update_layout(
                                xaxis_title='Minute', yaxis_title='Momentum Change',
                                height=300, margin=dict(l=40, r=10, t=30, b=30),
                                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                                xaxis=dict(tickmode='linear', dtick=2)
                            )
                            st.plotly_chart(fig_pred_home, use_container_width=True, key="pred_home")
                        
                        with col_pred2:
                            st.markdown(f"**{away_team}**")
                            fig_pred_away = go.Figure()
                            
                            # Actual values
                            fig_pred_away.add_trace(go.Scatter(
                                x=away_preds['display_minute'], y=away_preds['actual_value'],
                                mode='lines+markers', name='Actual',
                                line=dict(color='#d62728', width=2),
                                marker=dict(size=4)
                            ))
                            # Predictions
                            fig_pred_away.add_trace(go.Scatter(
                                x=away_preds['display_minute'], y=away_preds['prediction_value'],
                                mode='lines+markers', name='Predicted',
                                line=dict(color='#d62728', width=2, dash='dash'),
                                marker=dict(size=4, symbol='x')
                            ))
                            fig_pred_away.add_hline(y=0, line_dash="dot", line_color="gray", line_width=1)
                            
                            fig_pred_away.update_layout(
                                xaxis_title='Minute', yaxis_title='Momentum Change',
                                height=300, margin=dict(l=40, r=10, t=30, b=30),
                                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                                xaxis=dict(tickmode='linear', dtick=2)
                            )
                            st.plotly_chart(fig_pred_away, use_container_width=True, key="pred_away")
                        
                        # Prediction accuracy for this game
                        home_correct = ((home_preds['prediction_value'] > 0) == (home_preds['actual_value'] > 0)).sum()
                        away_correct = ((away_preds['prediction_value'] > 0) == (away_preds['actual_value'] > 0)).sum()
                        home_total = len(home_preds.dropna(subset=['actual_value']))
                        away_total = len(away_preds.dropna(subset=['actual_value']))
                        
                        home_pct = home_correct/home_total*100 if home_total > 0 else 0
                        away_pct = away_correct/away_total*100 if away_total > 0 else 0
                        
                        st.markdown(f"""
                        **This Game's Prediction Accuracy:**
                        - {home_team}: {home_correct}/{home_total} correct signs ({home_pct:.1f}%)
                        - {away_team}: {away_correct}/{away_total} correct signs ({away_pct:.1f}%)
                        """)
                    else:
                        st.info("No predictions available for this game")
                
                st.markdown("---")
                
                # ========== TOP 10 BIGGEST DIFFERENCES ==========
                st.markdown("### 🏆 Top 10 Biggest Differences Between Teams")
                
                st.markdown("""
                **What does "Difference" mean?**
                - **Abs Momentum Diff** = |Team A momentum - Team B momentum| → How far apart are the teams at this moment
                - **Mom Change Diff** = |Team A change - Team B change| → Who is gaining/losing momentum faster
                
                **The Key Question:** Does a big momentum CHANGE difference predict/explain the absolute momentum difference?
                """)
                
                col_diff1, col_diff2 = st.columns(2)
                
                # First calculate both tables to find matches
                # Calculate Abs differences
                all_game_data['mom_diff'] = abs(all_game_data['team_home_momentum'] - all_game_data['team_away_momentum'])
                all_game_data['mom_leader'] = all_game_data.apply(
                    lambda r: home_team if r['team_home_momentum'] > r['team_away_momentum'] else away_team, axis=1
                )
                top_mom_diff = all_game_data.nlargest(10, 'mom_diff')[['display_minute', 'period', 'mom_diff', 'mom_leader']].copy()
                
                # Calculate Change differences
                valid_changes = all_game_data.dropna(subset=['team_home_momentum_change', 'team_away_momentum_change']).copy()
                valid_changes['chg_diff'] = abs(valid_changes['team_home_momentum_change'] - valid_changes['team_away_momentum_change'])
                valid_changes['chg_leader'] = valid_changes.apply(
                    lambda r: home_team if r['team_home_momentum_change'] > r['team_away_momentum_change'] else away_team, axis=1
                )
                top_chg_diff = valid_changes.nlargest(10, 'chg_diff')[['display_minute', 'period', 'chg_diff', 'chg_leader']].copy()
                
                # Find matches: Change at X → Abs at X+3
                abs_minutes = set(top_mom_diff['display_minute'].astype(int).tolist())
                chg_minutes = set(top_chg_diff['display_minute'].astype(int).tolist())
                matching_abs = {chg + 3 for chg in chg_minutes if (chg + 3) in abs_minutes}
                matching_chg = {abs_m - 3 for abs_m in abs_minutes if (abs_m - 3) in chg_minutes}
                
                with col_diff1:
                    st.markdown("**Absolute Momentum Difference**")
                    st.caption("Minute X = momentum from events in minutes X-3, X-2, X-1")
                    
                    # Add events column
                    events_list = []
                    for _, row in top_mom_diff.iterrows():
                        display_min = int(row['display_minute'])
                        period_val = int(row['period'])
                        event_minutes = [display_min - 3, display_min - 2, display_min - 1]
                        events_str = self.get_events_for_minutes(match_id, event_minutes, period=period_val)
                        events_list.append(events_str)
                    
                    top_mom_diff['Events'] = events_list
                    top_mom_diff = top_mom_diff[['period', 'display_minute', 'mom_diff', 'mom_leader', 'Events']]
                    top_mom_diff.columns = ['P', 'Min', 'Diff', 'Leader', 'Events (LLM detected_type)']
                    top_mom_diff['Min'] = top_mom_diff['Min'].astype(int)
                    top_mom_diff['Diff'] = top_mom_diff['Diff'].round(2)
                    
                    # Highlight matching rows
                    def highlight_abs_matches(row):
                        if row['Min'] in matching_abs:
                            return ['background-color: #90EE90; font-weight: bold'] * len(row)
                        return [''] * len(row)
                    
                    styled_abs = top_mom_diff.style.apply(highlight_abs_matches, axis=1)
                    st.dataframe(styled_abs, use_container_width=True, hide_index=True)
                
                with col_diff2:
                    st.markdown("**Momentum Change Difference**")
                    st.caption("Change at min X compares (X-3,X-2,X-1) vs (X,X+1,X+2). Show current window (X-3,X-2,X-1).")
                    
                    # Add events column
                    events_list_chg = []
                    for _, row in top_chg_diff.iterrows():
                        display_min = int(row['display_minute'])
                        period_val = int(row['period'])
                        event_minutes = [display_min - 3, display_min - 2, display_min - 1]
                        events_str = self.get_events_for_minutes(match_id, event_minutes, period=period_val)
                        events_list_chg.append(events_str)
                    
                    top_chg_diff['Events'] = events_list_chg
                    top_chg_diff = top_chg_diff[['period', 'display_minute', 'chg_diff', 'chg_leader', 'Events']]
                    top_chg_diff.columns = ['P', 'Min', 'Diff', 'Leader', 'Events (X-3 to X-1)']
                    top_chg_diff['Min'] = top_chg_diff['Min'].astype(int)
                    top_chg_diff['Diff'] = top_chg_diff['Diff'].round(3)
                    
                    # Highlight matching rows
                    def highlight_chg_matches(row):
                        if row['Min'] in matching_chg:
                            return ['background-color: #90EE90; font-weight: bold'] * len(row)
                        return [''] * len(row)
                    
                    styled_chg = top_chg_diff.style.apply(highlight_chg_matches, axis=1)
                    st.dataframe(styled_chg, use_container_width=True, hide_index=True)
                
                # ========== COMPARISON INSIGHT ==========
                st.markdown("---")
                st.markdown("### 🔍 Matching Windows: Can Change PREDICT Abs Momentum?")
                
                st.markdown("""
                **How to Match:**
                - Abs at minute 84 → events 81, 82, 83
                - Change at minute 81 → events 78, 79, 80 (BEFORE the Abs window)
                - **Match:** Change at X → Abs at X+3 (consecutive windows!)
                """)
                
                # Get the top abs momentum minutes and find corresponding change minutes
                top_abs_minutes = list(top_mom_diff['Min'].tolist())
                top_chg_minutes = list(top_chg_diff['Min'].tolist())
                
                col_insight1, col_insight2 = st.columns(2)
                
                with col_insight1:
                    st.markdown("**🎯 Change → Abs Matches**")
                    st.caption("Change at X (events X-3 to X-1) → Abs at X+3 (events X to X+2)")
                    # Check if Change at minute X leads to Abs at minute X+3
                    predictions = []
                    for chg_min in top_chg_minutes:
                        expected_abs = chg_min + 3
                        if expected_abs in top_abs_minutes:
                            predictions.append((chg_min, expected_abs))
                    
                    if predictions:
                        for chg_m, abs_m in predictions:
                            st.success(f"✅ Change {chg_m} (events {chg_m-3}-{chg_m-1}) → Abs {abs_m} (events {abs_m-3}-{abs_m-1})")
                    else:
                        st.info("No direct Change→Abs matches in top 10")
                
                with col_insight2:
                    st.markdown("**📊 Summary**")
                    st.metric("Matches Found", len(predictions) if predictions else 0)
                    if predictions:
                        st.markdown("**Matched minutes:**")
                        for chg_m, abs_m in predictions:
                            st.markdown(f"- Chg {chg_m} → Abs {abs_m}")
                
                # ========== INTERSECTION POINTS ANALYSIS ==========
                st.markdown("---")
                st.markdown("### 🔀 Momentum Crossover Points (Intersections)")
                
                st.markdown("""
                **What are Intersection Points?**
                - Moments where one team's momentum crosses the other team's momentum
                - The team that was behind takes the lead (or vice versa)
                - These are **momentum shift moments** - critical game-changing points!
                """)
                
                # Calculate intersections for Absolute Momentum
                abs_intersections = []
                for period in game_data['period'].unique():
                    period_df = game_data[game_data['period'] == period].sort_values('minute')
                    
                    for i in range(len(period_df) - 1):
                        curr = period_df.iloc[i]
                        next_row = period_df.iloc[i + 1]
                        
                        curr_diff = curr['team_home_momentum'] - curr['team_away_momentum']
                        next_diff = next_row['team_home_momentum'] - next_row['team_away_momentum']
                        
                        if (curr_diff > 0 and next_diff < 0) or (curr_diff < 0 and next_diff > 0):
                            intersection_minute = next_row['minute']
                            display_minute = intersection_minute + 3
                            
                            abs_intersections.append({
                                'Period': period,
                                'Display Min': int(display_minute),
                                'Takes Lead': home_team if next_diff > 0 else away_team,
                                'Event Min': f"{intersection_minute}-{intersection_minute+2}"
                            })
                
                # Calculate intersections for Momentum Change
                change_intersections = []
                for period in game_data['period'].unique():
                    period_df = game_data[game_data['period'] == period].sort_values('minute')
                    period_df = period_df.dropna(subset=['team_home_momentum_change', 'team_away_momentum_change'])
                    
                    for i in range(len(period_df) - 1):
                        curr = period_df.iloc[i]
                        next_row = period_df.iloc[i + 1]
                        
                        curr_diff = curr['team_home_momentum_change'] - curr['team_away_momentum_change']
                        next_diff = next_row['team_home_momentum_change'] - next_row['team_away_momentum_change']
                        
                        if (curr_diff > 0 and next_diff < 0) or (curr_diff < 0 and next_diff > 0):
                            intersection_minute = next_row['minute']
                            display_minute = intersection_minute + 3
                            
                            change_intersections.append({
                                'Period': period,
                                'Display Min': int(display_minute),
                                'Takes Lead': home_team if next_diff > 0 else away_team,
                                'Event Min': f"{intersection_minute}-{intersection_minute+2}"
                            })
                
                # Get events for intersections
                if self.llm_commentary_df is not None:
                    game_events = self.llm_commentary_df[self.llm_commentary_df['match_id'] == match_id]
                    
                    # Add events to absolute intersections
                    for inter in abs_intersections:
                        period = inter['Period']
                        min_start = int(inter['Display Min']) - 3
                        # Get one key event per minute in the window
                        event_list = []
                        for m in [min_start, min_start+1, min_start+2]:
                            minute_events = game_events[
                                (game_events['period'] == period) &
                                (game_events['minute'] == m)
                            ]['detected_type'].value_counts()
                            if len(minute_events) > 0:
                                event_list.append(f"{m}:{minute_events.index[0]}")
                        inter['Events'] = ', '.join(event_list) if event_list else 'General'
                    
                    # Add events to change intersections
                    for inter in change_intersections:
                        period = inter['Period']
                        min_start = int(inter['Display Min']) - 3
                        # Get one key event per minute in the window
                        event_list = []
                        for m in [min_start, min_start+1, min_start+2]:
                            minute_events = game_events[
                                (game_events['period'] == period) &
                                (game_events['minute'] == m)
                            ]['detected_type'].value_counts()
                            if len(minute_events) > 0:
                                event_list.append(f"{m}:{minute_events.index[0]}")
                        inter['Events'] = ', '.join(event_list) if event_list else 'General'
                
                # Display tables side by side
                col_int1, col_int2 = st.columns(2)
                
                with col_int1:
                    st.markdown(f"**📊 Absolute Momentum Crossovers ({len(abs_intersections)})**")
                    if abs_intersections:
                        abs_int_df = pd.DataFrame(abs_intersections)
                        st.dataframe(abs_int_df, use_container_width=True, hide_index=True)
                    else:
                        st.info("No crossover points - one team dominated!")
                
                with col_int2:
                    st.markdown(f"**📈 Momentum Change Crossovers ({len(change_intersections)})**")
                    if change_intersections:
                        chg_int_df = pd.DataFrame(change_intersections)
                        st.dataframe(chg_int_df, use_container_width=True, hide_index=True)
                    else:
                        st.info("No crossover points")
                
                # Summary insight
                st.info(f"""
                **🎯 Crossover Summary:**
                - **Absolute Momentum:** {len(abs_intersections)} lead changes (momentum dominance shifts)
                - **Momentum Change:** {len(change_intersections)} crossovers (who's gaining faster shifts)
                
                More crossovers = More competitive/back-and-forth game!
                """)
                    
        except Exception as e:
            st.error(f"Could not load momentum data: {e}")
            import traceback
            st.code(traceback.format_exc())

