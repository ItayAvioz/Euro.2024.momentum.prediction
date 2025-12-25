"""
ARIMAX Momentum Analysis Page
Comprehensive analysis of the ARIMAX model for 3-minute momentum prediction
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path

# Cache events data for faster loading
@st.cache_data
def load_events_data():
    """Load and cache the events dataset"""
    events_path = Path(__file__).parent.parent.parent / "Data" / "euro_2024_complete_dataset.csv"
    if events_path.exists():
        return pd.read_csv(events_path, low_memory=False)
    return None

@st.cache_data
def load_momentum_predictions():
    """Load and cache momentum predictions"""
    pred_path = Path(__file__).parent.parent.parent / "models" / "modeling" / "scripts" / "outputs" / "predictions" / "arimax_predictions.csv"
    if pred_path.exists():
        return pd.read_csv(pred_path)
    return None

class ARIMAXMomentumPage:
    """ARIMAX Momentum Analysis page implementation"""
    
    def __init__(self, data_loader=None):
        self.data_loader = data_loader
        self.predictions_path = Path(__file__).parent.parent.parent / "models" / "modeling" / "scripts" / "outputs" / "predictions" / "arimax_predictions.csv"
        self.predictions_df = None
        self.arimax_df = None
        
    def load_predictions(self):
        """Load ARIMAX predictions data"""
        try:
            if self.predictions_path.exists():
                self.predictions_df = pd.read_csv(self.predictions_path)
                self.arimax_df = self.predictions_df[
                    self.predictions_df['model_type'] == 'momentum_to_change_arimax'
                ].copy()
                return True
            else:
                return False
        except Exception as e:
            st.error(f"Error loading predictions: {e}")
            return False
    
    def render(self):
        """Render the ARIMAX Momentum Analysis page"""
        
        # Page header
        st.markdown('<h1 class="main-header">🎯 ARIMAX Momentum Prediction Model</h1>', 
                   unsafe_allow_html=True)
        st.markdown("### 3-Minute Momentum Change Forecasting for Euro 2024")
        st.markdown("---")
        
        # Load data
        data_loaded = self.load_predictions()
        
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
            self.render_model_overview()
        
        with tab2:
            self.render_sign_accuracy(data_loaded)
        
        with tab3:
            self.render_paired_analysis(data_loaded)
        
        with tab4:
            self.render_metric_definitions()
        
        with tab5:
            self.render_real_data_analysis()
        
        with tab6:
            self.render_game_comparison()
    
    def render_model_overview(self):
        """Render model overview section"""
        st.subheader("🏆 ARIMAX Model Performance Summary")
        
        # Key metrics in cards - removed MSE
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Directional Accuracy",
                "81.61%",
                "+31.61% vs random",
                help="Correctly predicts if momentum TREND goes up or down"
            )
        
        with col2:
            st.metric(
                "Differential Sign",
                "71.11%",
                "+21.11% vs random",
                help="Correctly predicts which team gains momentum advantage"
            )
        
        with col3:
            st.metric(
                "Sign Agreement",
                "67.35%",
                "+17.35% vs random",
                help="Correctly predicts positive vs negative momentum change"
            )
        
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
            - **Training:** Minutes 0-75
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
        st.success("""
        **🎯 Key Achievement:** ARIMAX achieves **81.61% directional accuracy** - meaning it correctly 
        predicts whether momentum will go UP or DOWN in 8 out of 10 predictions. This is 
        **32% better than random chance** and enables practical tactical decision-making.
        """)
        
    
    def render_sign_accuracy(self, data_loaded):
        """Render sign accuracy analysis section"""
        st.subheader("🎯 Sign Agreement Analysis")
        
        if not data_loaded or self.arimax_df is None:
            # Use hardcoded values from our analysis
            pred_pos, pred_neg, pred_zero = 630, 886, 0
            actual_pos, actual_neg, actual_zero = 810, 705, 1
            pp, nn, pn, np_ = 473, 548, 157, 337
            total = 1516
        else:
            # Calculate from data
            pred = self.arimax_df['prediction_value'].values
            actual = self.arimax_df['actual_value'].values
            
            pred_sign = np.sign(pred)
            actual_sign = np.sign(actual)
            
            pred_pos = (pred_sign > 0).sum()
            pred_neg = (pred_sign < 0).sum()
            pred_zero = (pred_sign == 0).sum()
            
            actual_pos = (actual_sign > 0).sum()
            actual_neg = (actual_sign < 0).sum()
            actual_zero = (actual_sign == 0).sum()
            
            pp = ((pred_sign > 0) & (actual_sign > 0)).sum()
            nn = ((pred_sign < 0) & (actual_sign < 0)).sum()
            pn = ((pred_sign > 0) & (actual_sign < 0)).sum()
            np_ = ((pred_sign < 0) & (actual_sign > 0)).sum()
            total = len(pred)
        
        correct = pp + nn
        sign_accuracy = correct / total
        
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
        
        st.warning(f"""
        **📌 Model Bias Observation:** The model predicts more negative changes ({pred_neg/total*100:.1f}%) 
        than actually occur ({actual_neg/total*100:.1f}%). This "pessimistic" tendency means the model 
        is more conservative about predicting momentum increases.
        """)
        
        st.markdown("---")
        
        # Contingency table
        st.markdown("### 📋 Sign Agreement Matrix (2x2 Contingency Table)")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create heatmap for contingency table
            z_data = [[pp, pn], [np_, nn]]
            
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=z_data,
                x=['Actual Positive', 'Actual Negative'],
                y=['Predicted Positive', 'Predicted Negative'],
                text=[[f'{pp}<br>({pp/total*100:.1f}%)', f'{pn}<br>({pn/total*100:.1f}%)'],
                      [f'{np_}<br>({np_/total*100:.1f}%)', f'{nn}<br>({nn/total*100:.1f}%)']],
                texttemplate='%{text}',
                textfont={"size": 16},
                colorscale=[[0, '#ffcccb'], [0.5, '#ffffcc'], [1, '#90EE90']],
                showscale=False
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
            Negative→Positive errors ({np_/total*100:.1f}%) are more common than 
            Positive→Negative errors ({pn/total*100:.1f}%), confirming the model's 
            conservative/pessimistic tendency.
            """)
        
        st.markdown("---")
        
        # Differential Sign Analysis Results
        st.markdown("### ☑️ Differential Sign Analysis Results")
        
        st.markdown("""
        The **Differential Sign Analysis** compares momentum change between the two teams in each window
        to determine which team gains the momentum advantage.
        """)
        
        # From ARIMAX_DIFFERENTIAL_ANALYSIS_SUMMARY.md
        differential_data = {
            'Predicted Sign': ['Positive', 'Positive', 'Negative', 'Negative'],
            'Actual Sign': ['Positive', 'Negative', 'Positive', 'Negative'],
            'Count': [247, 94, 124, 292],
            'Percentage': ['32.59%', '12.40%', '16.36%', '38.52%'],
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
                    y=[247, 292],
                    marker_color='#2ca02c',
                    text=[247, 292],
                    textposition='auto'
                ),
                go.Bar(
                    name='Wrong (PN + NP)',
                    x=['Positive→Negative', 'Negative→Positive'],
                    y=[94, 124],
                    marker_color='#d62728',
                    text=[94, 124],
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
            
            st.markdown("""
            **Summary:**
            - **Correct:** 539/758 (71.11%)
            - **Wrong:** 218/758 (28.76%)
            - **Correlation:** r = 0.559
            """)
        
        st.markdown("---")
        
        # Conditional Accuracy
        st.markdown("### 🎯 Conditional Accuracy")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **When Actual Differential is POSITIVE (Team X ahead):**
            - Accuracy: **66.58%** (247/371 correct)
            - ARIMAX correctly identifies when Team X gains momentum advantage
            """)
        
        with col2:
            st.markdown("""
            **When Actual Differential is NEGATIVE (Team Y ahead):**
            - Accuracy: **75.65%** (292/386 correct)
            - ARIMAX is **BETTER** at identifying when Team Y gains momentum advantage
            """)
        
        st.info("""
        **🔍 Asymmetric Accuracy:** The model shows better performance at detecting Team Y advantages 
        (75.65%) than Team X advantages (66.58%). This indicates the model is slightly better at 
        identifying when teams are **losing** momentum than **gaining** it.
        """)
        
        st.markdown("---")
        
        # Practical implications
        st.markdown("### 💡 Practical Implications")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("""
            **✅ Strengths:**
            1. **Strong Overall Accuracy:** 71% correct differential signs
            2. **Pattern Recognition:** 56% correlation between predicted/actual
            3. **Tactical Value:** Can predict relative momentum shifts
            4. **Asymmetric Skill:** Good at identifying momentum losses
            """)
        
        with col2:
            st.warning("""
            **⚠️ Limitations:**
            1. **Negative Bias:** Systematically predicts more negative differentials
            2. **Overconfidence:** Predictions more extreme than reality
            3. **Zero Handling:** Never predicts exact ties (rare but occurs)
            """)
        
        # Application examples
        st.markdown("### 🏟️ Real Match Examples")
        
        examples = {
            'Match': ['Germany vs Switzerland (76-78)', 'Portugal vs Slovenia (87-89)', 
                     'Croatia vs Spain (75-77)', 'Slovakia vs Ukraine (83-85)'],
            'Predicted Diff': ['+0.447', '+0.809', '+0.945', '-1.157'],
            'Actual Diff': ['+1.303', '+0.587', '-3.603', '+1.243'],
            'Result': ['✅ Both positive', '✅ Both positive', '❌ Wrong sign', '❌ Wrong sign']
        }
        
        df_examples = pd.DataFrame(examples)
        st.dataframe(df_examples, use_container_width=True, hide_index=True)
    
    def render_paired_analysis(self, data_loaded):
        """Render paired team analysis section"""
        st.subheader("👥 Paired Team Analysis (Same 3-Minute Window)")
        
        st.markdown("""
        This analysis examines how often the model correctly predicts momentum change signs for 
        **BOTH teams** in the same game window.
        """)
        
        # Hardcoded values from our analysis
        total_windows = 758
        both_correct = 353
        only_x_correct = 158
        only_y_correct = 157
        one_correct = only_x_correct + only_y_correct
        both_wrong = 90
        
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
            st.markdown("#### Team X vs Team Y Correctness Matrix")
            
            z_matrix = [[both_correct, only_x_correct], [only_y_correct, both_wrong]]
            
            fig_matrix = go.Figure(data=go.Heatmap(
                z=z_matrix,
                x=['Team Y Correct', 'Team Y Wrong'],
                y=['Team X Correct', 'Team X Wrong'],
                text=[[f'{both_correct}<br>({both_correct/total_windows*100:.1f}%)', 
                       f'{only_x_correct}<br>({only_x_correct/total_windows*100:.1f}%)'],
                      [f'{only_y_correct}<br>({only_y_correct/total_windows*100:.1f}%)', 
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
            
            In **88% of game windows**, the model gets at least ONE team's 
            momentum change sign correct.
            """)
        
        with col2:
            st.error(f"""
            **❌ Complete Failure: {both_wrong} ({both_wrong/total_windows*100:.1f}%)**
            
            In only **12% of windows**, both predictions are completely wrong. 
            This is the worst-case scenario but happens rarely.
            """)
        
        st.info("""
        **📝 Interpretation:**
        - **Nearly half the time (46.6%)**, BOTH teams are predicted correctly simultaneously
        - The "one correct" cases are evenly split (~20.8% each), meaning the model doesn't 
          systematically favor one team over another
        - Complete failures are relatively rare (11.9%)
        """)
    
    def render_metric_definitions(self):
        """Render metric definitions section"""
        st.subheader("📖 Understanding the Metrics")
        
        st.markdown("""
        The ARIMAX model is evaluated using three different accuracy metrics. Each measures 
        something different and provides unique insights into model performance.
        """)
        
        st.markdown("---")
        
        # Metric 1: Directional Accuracy
        st.markdown("### 1️⃣ Directional Accuracy (81.61%)")
        
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
        st.markdown("### 2️⃣ Sign Agreement Accuracy (67.35%)")
        
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
        st.markdown("### 3️⃣ Differential Sign Accuracy (71.11%)")
        
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
            'Metric': ['Directional (81.61%)', 'Sign Agreement (67.35%)', 'Differential (71.11%)'],
            'What We Learn': ['Trend direction (UP/DOWN)', 'Absolute sign (+/-)', 'Which team does BETTER'],
            'What We DON\'T Learn': ['If momentum is + or -', '—', 'If each team gains or loses'],
            'Random Baseline': ['50%', '50%', '50%'],
            'Improvement': ['+31.61%', '+17.35%', '+21.11%']
        }
        
        df_comparison = pd.DataFrame(comparison_table)
        st.dataframe(df_comparison, use_container_width=True, hide_index=True)
    
    def render_real_data_analysis(self):
        """Render real data analysis - momentum change and sequences"""
        st.subheader("🔬 Real Data Analysis: Momentum Predictors")
        
        st.markdown("""
        Analysis of **51 Euro 2024 games** with **~94 momentum windows per game** to understand 
        which momentum metrics predict match outcomes.
        """)
        
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
        
        metrics_data = {
            'Metric': ['Absolute Momentum', 'Number of Sequences', 'Positive Changes', 'Longest Sequence'],
            'Type': ['✅ Winning', '✅ Winning', '❌ Chasing', '❌ Chasing'],
            'Games': [51, 45, 45, 46],
            'WIN': ['51.0%', '42.2%', '22.2%', '26.1%'],
            'LOSE': ['15.7%', '26.7%', '46.7%', '43.5%'],
            'DRAW': ['33.3%', '31.1%', '31.1%', '30.4%']
        }
        
        df_metrics = pd.DataFrame(metrics_data)
        st.dataframe(df_metrics, use_container_width=True, hide_index=True)
        
        st.info("""
        **📌 Key Insight:** Notice the pattern! 
        - **Winning metrics:** ~50% win, ~20% lose
        - **Chasing metrics:** ~25% win, ~45% lose (OPPOSITE!)
        """)
        
        st.markdown("---")
        
        # Section 2b: Cumulative Margin Analysis (Only where it adds value)
        st.markdown("### 📈 Cumulative Margin Analysis")
        
        st.markdown("""
        How does increasing the **minimum margin threshold** improve predictive value?
        Only showing thresholds where there's meaningful improvement:
        """)
        
        st.markdown("#### Winning Metrics Cumulative Margins")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Absolute Momentum Margin**")
            
            # Only show thresholds with meaningful improvement
            mom_margin_data = {
                'Min Margin': ['All (0%+)', '15%+', '20%+'],
                'Games': [51, 40, 35],
                'WIN': ['51.0%', '52.5%', '54.3%'],
                'LOSE': ['15.7%', '12.5%', '11.4%'],
                'Meaning': ['Any difference', '15%+ more windows', '20%+ more windows']
            }
            df_mom = pd.DataFrame(mom_margin_data)
            st.dataframe(df_mom, use_container_width=True, hide_index=True)
            
            st.markdown("*35/51 games (69%) have 20%+ margin*")
        
        with col2:
            st.markdown("**Number of Sequences Margin**")
            
            # Only show thresholds with meaningful improvement
            num_seq_margin_data = {
                'Min Margin': ['All (0+)', '3+ seq', '4+ seq'],
                'Games': [45, 16, 5],
                'WIN': ['42.2%', '56.2%', '80.0%'],
                'LOSE': ['26.7%', '18.8%', '0.0%'],
                'Meaning': ['Has more sequences', '3+ more sequences', '4+ more sequences']
            }
            df_num_seq = pd.DataFrame(num_seq_margin_data)
            st.dataframe(df_num_seq, use_container_width=True, hide_index=True)
            
            st.markdown("*At 4+ margin: 80% win, 0% lose!*")
            
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
        
        with col1:
            st.markdown("**Positive Changes Margin**")
            st.markdown("*Most games have < 5% margin - momentum change is very balanced!*")
            st.markdown("No significant added value from margin thresholds.")
        
        with col2:
            st.markdown("**Longest Sequence Margin**")
            
            # Only show thresholds with meaningful improvement
            seq_margin_data = {
                'Min Margin': ['All (0+)', '3+ windows', '5+ windows'],
                'Games': [46, 19, 6],
                'WIN': ['26.1%', '36.8%', '50.0%'],
                'LOSE': ['43.5%', '36.8%', '16.7%'],
                'Meaning': ['Best streak is longer', 'Best streak 3+ windows longer', 'Best streak 5+ windows longer']
            }
            df_seq = pd.DataFrame(seq_margin_data)
            st.dataframe(df_seq, use_container_width=True, hide_index=True)
            
            st.markdown("*At 5+ margin, pattern REVERSES!*")
            
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
                | **Large (5+)** | Much longer → sustained dominance |
                
                **Why pattern reverses at 5+?**
                - Small margin = desperately chasing
                - Large margin = complete control, opponent couldn't break momentum
                """)
        
        st.success("""
        **🎯 Key Findings from Cumulative Analysis:** 
        - **Absolute Momentum 20%+:** Lose rate drops from 15.7% → 11.4%
        - **Number of Sequences 4+:** WIN jumps to 80%, LOSE drops to 0%!
        - **Longest Sequence 5+:** Lose rate drops from 43.5% → 16.7% (pattern reverses!)
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
                y=[22.2, 46.7, 31.1],
                text=['22.2%', '46.7%', '31.1%'],
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
        
        st.warning("""
        **⚠️ Counter-Intuitive Finding:** Teams with MORE positive momentum changes have a **46.7% lose rate** 
        vs only **22.2% win rate**. More positive changes = desperately chasing the game!
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
                y=[26.1, 43.5, 30.4],
                text=['26.1%', '43.5%', '30.4%'],
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
                y=[42.2, 26.7, 31.1],
                text=['42.2%', '26.7%', '31.1%'],
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
            'Games': [19, 28, 9],
            'WIN': ['73.7%', '25.0%', '100%'],
            'LOSE': ['10.5%', '53.6%', '0%'],
            'DRAW': ['15.8%', '21.4%', '0%']
        }
        
        df_combined = pd.DataFrame(combined_data)
        st.dataframe(df_combined, use_container_width=True, hide_index=True)
        
        # Highlight the best finding
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Winning Metrics AGREE",
                "73.7% WIN",
                "Only 10.5% lose!",
                help="When Absolute Momentum AND Number of Sequences point to same team"
            )
        
        with col2:
            st.metric(
                "DIFFERENT Teams",
                "100% WIN",
                "9/9 games!",
                help="When Winning metrics → Team A, Chasing metrics → Team B"
            )
        
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
        
        st.markdown("""
        **Result: Team A wins 100% of the time (9/9 games)!**
        
        This makes perfect sense:
        - Team A dominates (high momentum, multiple attack phases)
        - Team B desperately tries to recover (many changes, long streaks)
        - Clear picture = reliable prediction
        """)
        
        # Example games
        st.markdown("### 🏟️ Example Games")
        
        examples_data = {
            'Match': ['Germany 5-1 Scotland', 'Spain 3-0 Croatia', 'Italy 2-1 Albania', 
                     'Portugal 2-1 Czech Rep.', 'Switzerland 3-1 Hungary'],
            'Winning Metrics →': ['Germany', 'Spain', 'Italy', 'Portugal', 'Switzerland'],
            'Chasing Metrics →': ['Scotland', 'Croatia', 'Albania', 'Czech Rep.', 'Hungary'],
            'Result': ['Germany ✓', 'Spain ✓', 'Italy ✓', 'Portugal ✓', 'Switzerland ✓']
        }
        
        df_examples = pd.DataFrame(examples_data)
        st.dataframe(df_examples, use_container_width=True, hide_index=True)
        
        st.success("""
        **🎯 Practical Application:** When analyzing a match:
        1. Calculate who wins more momentum windows (Winning metric #1)
        2. Calculate who has more sequences (Winning metric #2)
        3. Calculate who has more positive changes (Chasing metric #1)
        4. Calculate who has the longest sequence (Chasing metric #2)
        5. If Winning → Team A and Chasing → Team B, **Team A will likely win!**
        """)
    
    def render_game_comparison(self):
        """Render game-by-game momentum comparison"""
        st.subheader("📉 Game-by-Game Momentum Comparison")
        
        st.markdown("""
        Select a game to visualize how momentum evolved over time for both teams.
        """)
        
        # Load momentum data
        try:
            momentum_path = Path(__file__).parent.parent.parent / "models" / "preprocessing" / "data" / "targets" / "momentum_targets_streamlined.csv"
            momentum_data = pd.read_csv(momentum_path)
            
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
                
                # Extract minute from minute_range (e.g., "0-2" -> 0)
                game_data['minute'] = game_data['minute_range'].apply(lambda x: int(x.split('-')[0]))
                game_data = game_data.sort_values('minute')
                
                # Filter to start from minute 3 (first valid momentum change)
                game_data = game_data[game_data['minute'] >= 3].copy()
                
                home_team = game_data['team_home'].iloc[0]
                away_team = game_data['team_away'].iloc[0]
                
                # Calculate actual data range from momentum data (not events)
                max_minute_data = game_data['minute'].max()
                min_minute_2h = game_data[game_data['minute'] >= 48]['minute'].min() if len(game_data[game_data['minute'] >= 48]) > 0 else 48
                
                # First half ends where there's a gap (usually around 48-51)
                first_half_data = game_data[game_data['minute'] < 48]
                first_half_end_data = first_half_data['minute'].max() if len(first_half_data) > 0 else 48
                
                # Calculate stoppage from actual data range
                stoppage_1h = max(0, first_half_end_data - 48 + 1) if first_half_end_data > 47 else 0
                stoppage_2h = max(0, max_minute_data - 93 + 1) if max_minute_data > 92 else 0
                
                # Use actual data max, not events
                first_half_max = first_half_end_data if first_half_end_data >= 48 else 48
                second_half_max = max_minute_data if max_minute_data >= 90 else 90
                
                st.markdown("---")
                
                # Display stoppage time info
                st.info(f"**This Game:** 1st Half ends at min {first_half_end_data} | 2nd Half ends at min {max_minute_data}")
                
                # Split data by half - use actual data range
                first_half_end_minute = first_half_end_data
                second_half_start_minute = 48
                second_half_end_minute = max_minute_data
                
                # Filter data for each half
                first_half_data = game_data[game_data['minute'] <= first_half_end_minute].copy()
                second_half_data = game_data[game_data['minute'] >= second_half_start_minute].copy()
                
                st.caption("📌 Minute X shows momentum from previous 3 min (X-3 to X-1). Example: Min 48 = momentum of min 45-47")
                
                # Create tick labels (every 1 minute, stoppage time notation after 48/93)
                def create_tick_labels(start, end, regular_end, stoppage_base):
                    """Create tick labels with stoppage notation after regular_end"""
                    vals, labels = [], []
                    for m in range(start, end + 1):
                        vals.append(m)
                        if m <= regular_end:
                            labels.append(str(m))
                        else:
                            labels.append(f"{stoppage_base}+{m - regular_end}")
                    return vals, labels
                
                ticks_1h_vals, ticks_1h_labels = create_tick_labels(3, first_half_end_minute, 48, 45)
                ticks_2h_vals, ticks_2h_labels = create_tick_labels(48, second_half_end_minute, 93, 90)
                
                # ========== ABSOLUTE MOMENTUM - TWO SEPARATE GRAPHS ==========
                st.markdown("### 📊 Absolute Momentum Over Time")
                
                col1h, col2h = st.columns(2)
                
                with col1h:
                    end_label_1h = f"45+{first_half_end_minute - 48}" if first_half_end_minute > 48 else "48"
                    st.markdown(f"**1st Half** (3' → {end_label_1h}')")
                    
                    fig_mom_1h = go.Figure()
                    # Vertical line at 45' (minute 48 on graph)
                    if first_half_end_minute > 48:
                        fig_mom_1h.add_vline(x=48, line_dash="dot", line_color="orange", line_width=2,
                            annotation_text="45'", annotation_position="top")
                    
                    fig_mom_1h.add_trace(go.Scatter(x=first_half_data['minute'], y=first_half_data['team_home_momentum'],
                        mode='lines', name=home_team, line=dict(color='#1f77b4', width=2)))
                    fig_mom_1h.add_trace(go.Scatter(x=first_half_data['minute'], y=first_half_data['team_away_momentum'],
                        mode='lines', name=away_team, line=dict(color='#d62728', width=2)))
                    
                    fig_mom_1h.update_layout(
                        xaxis_title='Minute', yaxis_title='Momentum', height=300,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                        hovermode='x unified', margin=dict(l=40, r=10, t=30, b=30),
                        xaxis=dict(tickmode='array', tickvals=ticks_1h_vals, ticktext=ticks_1h_labels,
                            range=[3, first_half_end_minute + 0.5]),
                        yaxis=dict(gridcolor='lightgray')
                    )
                    st.plotly_chart(fig_mom_1h, use_container_width=True, key="abs_mom_1h")
                
                with col2h:
                    end_label_2h = f"90+{second_half_end_minute - 93}" if second_half_end_minute > 93 else str(second_half_end_minute)
                    st.markdown(f"**2nd Half** (48' → {end_label_2h}')")
                    
                    fig_mom_2h = go.Figure()
                    # Vertical line at 90' (minute 93 on graph)
                    if second_half_end_minute > 93:
                        fig_mom_2h.add_vline(x=93, line_dash="dot", line_color="orange", line_width=2,
                            annotation_text="90'", annotation_position="top")
                    
                    fig_mom_2h.add_trace(go.Scatter(x=second_half_data['minute'], y=second_half_data['team_home_momentum'],
                        mode='lines', name=home_team, line=dict(color='#1f77b4', width=2)))
                    fig_mom_2h.add_trace(go.Scatter(x=second_half_data['minute'], y=second_half_data['team_away_momentum'],
                        mode='lines', name=away_team, line=dict(color='#d62728', width=2)))
                    
                    fig_mom_2h.update_layout(
                        xaxis_title='Minute', yaxis_title='Momentum', height=300,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                        hovermode='x unified', margin=dict(l=40, r=10, t=30, b=30),
                        xaxis=dict(tickmode='array', tickvals=ticks_2h_vals, ticktext=ticks_2h_labels,
                            range=[48, second_half_end_minute + 0.5]),
                        yaxis=dict(gridcolor='lightgray')
                    )
                    st.plotly_chart(fig_mom_2h, use_container_width=True, key="abs_mom_2h")
                
                st.markdown("---")
                
                # ========== MOMENTUM CHANGE - TWO SEPARATE GRAPHS ==========
                st.markdown("### 📈 Momentum Change Over Time")
                
                col1hc, col2hc = st.columns(2)
                
                with col1hc:
                    st.markdown(f"**1st Half** (3' → {end_label_1h}')")
                    
                    fig_chg_1h = go.Figure()
                    if first_half_end_minute > 48:
                        fig_chg_1h.add_vline(x=48, line_dash="dot", line_color="orange", line_width=2,
                            annotation_text="45'", annotation_position="top")
                    
                    fig_chg_1h.add_trace(go.Scatter(x=first_half_data['minute'], y=first_half_data['team_home_momentum_change'],
                        mode='lines', name=home_team, line=dict(color='#1f77b4', width=2)))
                    fig_chg_1h.add_trace(go.Scatter(x=first_half_data['minute'], y=first_half_data['team_away_momentum_change'],
                        mode='lines', name=away_team, line=dict(color='#d62728', width=2)))
                    fig_chg_1h.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)
                    
                    fig_chg_1h.update_layout(
                        xaxis_title='Minute', yaxis_title='Momentum Change', height=300,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                        hovermode='x unified', margin=dict(l=40, r=10, t=30, b=30),
                        xaxis=dict(tickmode='array', tickvals=ticks_1h_vals, ticktext=ticks_1h_labels,
                            range=[3, first_half_end_minute + 0.5]),
                        yaxis=dict(gridcolor='lightgray')
                    )
                    st.plotly_chart(fig_chg_1h, use_container_width=True, key="chg_1h")
                
                with col2hc:
                    st.markdown(f"**2nd Half** (48' → {end_label_2h}')")
                    
                    fig_chg_2h = go.Figure()
                    if second_half_end_minute > 93:
                        fig_chg_2h.add_vline(x=93, line_dash="dot", line_color="orange", line_width=2,
                            annotation_text="90'", annotation_position="top")
                    
                    fig_chg_2h.add_trace(go.Scatter(x=second_half_data['minute'], y=second_half_data['team_home_momentum_change'],
                        mode='lines', name=home_team, line=dict(color='#1f77b4', width=2)))
                    fig_chg_2h.add_trace(go.Scatter(x=second_half_data['minute'], y=second_half_data['team_away_momentum_change'],
                        mode='lines', name=away_team, line=dict(color='#d62728', width=2)))
                    fig_chg_2h.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)
                    
                    fig_chg_2h.update_layout(
                        xaxis_title='Minute', yaxis_title='Momentum Change', height=300,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                        hovermode='x unified', margin=dict(l=40, r=10, t=30, b=30),
                        xaxis=dict(tickmode='array', tickvals=ticks_2h_vals, ticktext=ticks_2h_labels,
                            range=[48, second_half_end_minute + 0.5]),
                        yaxis=dict(gridcolor='lightgray')
                    )
                    st.plotly_chart(fig_chg_2h, use_container_width=True, key="chg_2h")
                
                st.markdown("---")
                
                # Game summary stats
                st.markdown(f"### 📋 Game Summary Statistics")
                
                # Use filtered data
                first_half = first_half_data
                second_half = second_half_data
                
                # Calculate stats for full game
                home_momentum_wins = (game_data['team_home_momentum'] > game_data['team_away_momentum']).sum()
                away_momentum_wins = (game_data['team_away_momentum'] > game_data['team_home_momentum']).sum()
                home_positive_changes = (game_data['team_home_momentum_change'] > 0).sum()
                away_positive_changes = (game_data['team_away_momentum_change'] > 0).sum()
                home_avg = game_data['team_home_momentum'].mean()
                away_avg = game_data['team_away_momentum'].mean()
                
                # Calculate stats for first half
                home_momentum_wins_1h = (first_half['team_home_momentum'] > first_half['team_away_momentum']).sum()
                away_momentum_wins_1h = (first_half['team_away_momentum'] > first_half['team_home_momentum']).sum()
                home_positive_changes_1h = (first_half['team_home_momentum_change'] > 0).sum()
                away_positive_changes_1h = (first_half['team_away_momentum_change'] > 0).sum()
                
                # Calculate stats for second half
                home_momentum_wins_2h = (second_half['team_home_momentum'] > second_half['team_away_momentum']).sum()
                away_momentum_wins_2h = (second_half['team_away_momentum'] > second_half['team_home_momentum']).sum()
                home_positive_changes_2h = (second_half['team_home_momentum_change'] > 0).sum()
                away_positive_changes_2h = (second_half['team_away_momentum_change'] > 0).sum()
                
                # Calculate longest sequences
                home_max_seq = 0
                away_max_seq = 0
                current_home = 0
                current_away = 0
                for _, row in game_data.iterrows():
                    if row['team_home_momentum_change'] > 0:
                        current_home += 1
                        home_max_seq = max(home_max_seq, current_home)
                    else:
                        current_home = 0
                    if row['team_away_momentum_change'] > 0:
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
                    st.markdown("#### 1st Half (3-48')")
                    half1_data = {
                        'Team': [home_team, away_team],
                        'Momentum Windows': [home_momentum_wins_1h, away_momentum_wins_1h],
                        'Positive Changes': [home_positive_changes_1h, away_positive_changes_1h]
                    }
                    df_half1 = pd.DataFrame(half1_data)
                    st.dataframe(df_half1, use_container_width=True, hide_index=True)
                
                with col2:
                    st.markdown("#### 2nd Half (48-90'+)")
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
                    
        except Exception as e:
            st.error(f"Could not load momentum data: {e}")
            st.info("Make sure the momentum data file exists at: models/preprocessing/data/targets/momentum_targets_streamlined.csv")

