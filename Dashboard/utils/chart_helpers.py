"""
Chart and Visualization Helpers
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
try:
    from .config import DashboardConfig
except ImportError:
    from config import DashboardConfig

class ChartHelpers:
    """Helper functions for creating charts"""
    
    def __init__(self):
        self.config = DashboardConfig()
        self.colors = self.config.COLOR_SCHEME
    
    def create_metric_cards_chart(self, metrics_data):
        """Create metric cards visualization"""
        fig = go.Figure()
        
        # This will be handled by Streamlit metrics, not plotly
        return None
    
    def create_stage_distribution_pie(self, stage_data):
        """Create tournament stage distribution pie chart"""
        if not stage_data:
            return go.Figure()
        
        labels = list(stage_data.keys())
        values = list(stage_data.values())
        
        fig = px.pie(
            values=values,
            names=labels,
            title="Tournament Stage Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Matches: %{value}<br>Percentage: %{percent}<extra></extra>'
        )
        
        fig.update_layout(
            height=self.config.CHART_HEIGHT,
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5)
        )
        
        return fig
    
    def create_goals_by_stage_chart(self, stage_analysis):
        """Create goals by stage bar chart"""
        if not stage_analysis:
            return go.Figure()
        
        stages = []
        goals = []
        matches = []
        
        for stage, data in stage_analysis.items():
            stages.append(stage.replace('_', ' ').title())
            goals.append(data.get('avg_goals', 0))
            matches.append(data.get('matches', 0))
        
        if not stages or not goals:
            return go.Figure()
        
        fig = px.bar(
            x=stages,
            y=goals,
            title="Average Goals per Match by Tournament Stage",
            labels={'x': 'Tournament Stage', 'y': 'Average Goals per Match'},
            color=goals,
            color_continuous_scale='Blues'
        )
        
        # Add match count as text on bars
        fig.update_traces(
            text=[f"{g:.2f}<br>({m} matches)" for g, m in zip(goals, matches)],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Avg Goals: %{y:.2f}<br>Matches: %{customdata}<extra></extra>',
            customdata=matches
        )
        
        fig.update_layout(
            height=self.config.CHART_HEIGHT,
            showlegend=False,
            xaxis_tickangle=-45
        )
        
        return fig
    
    def create_event_distribution_chart(self, event_data):
        """Create event type distribution chart"""
        if not event_data or 'counts' not in event_data:
            return go.Figure()
        
        # Get top 10 events
        top_events = dict(list(event_data['counts'].items())[:10])
        
        fig = px.bar(
            x=list(top_events.values()),
            y=list(top_events.keys()),
            orientation='h',
            title="Top 10 Event Types",
            labels={'x': 'Number of Events', 'y': 'Event Type'},
            color=list(top_events.values()),
            color_continuous_scale='Viridis'
        )
        
        # Add percentage text
        total_events = sum(event_data['counts'].values())
        percentages = [(count/total_events)*100 for count in top_events.values()]
        
        fig.update_traces(
            text=[f"{count:,}<br>({pct:.1f}%)" for count, pct in zip(top_events.values(), percentages)],
            textposition='inside',
            hovertemplate='<b>%{y}</b><br>Count: %{x:,}<br>Percentage: %{customdata:.1f}%<extra></extra>',
            customdata=percentages
        )
        
        fig.update_layout(
            height=self.config.CHART_HEIGHT,
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'}
        )
        
        return fig
    
    def create_kickoff_time_comparison(self, time_analysis):
        """Create kickoff time comparison chart - FIXED VERSION"""
        if not time_analysis or 'kickoff_times' not in time_analysis:
            return go.Figure()
        
        kickoff_data = time_analysis['kickoff_times']
        
        if not kickoff_data:
            return go.Figure()
        
        times = list(kickoff_data.keys())
        goals = [data.get('avg_goals', 0) for data in kickoff_data.values()]
        draws = [data.get('draw_rate', 0) for data in kickoff_data.values()]
        matches = [data.get('matches', 0) for data in kickoff_data.values()]
        
        # Create subplot with secondary y-axis
        fig = make_subplots(
            specs=[[{"secondary_y": True}]],
            subplot_titles=["Kickoff Time Impact Analysis"]
        )
        
        # Add goals bar chart
        fig.add_trace(
            go.Bar(
                x=times,
                y=goals,
                name="Avg Goals/Match",
                marker_color=self.colors['secondary'],
                text=[f"{g:.2f}" for g in goals],
                textposition='outside'
            ),
            secondary_y=False,
        )
        
        # Add draw rate line
        fig.add_trace(
            go.Scatter(
                x=times,
                y=draws,
                mode='lines+markers',
                name="Draw Rate (%)",
                line=dict(color=self.colors['neutral'], width=3),
                marker=dict(size=10)
            ),
            secondary_y=True,
        )
        
        # Update layout
        fig.update_xaxes(title_text="Kickoff Time")
        fig.update_yaxes(title_text="Average Goals per Match", secondary_y=False)
        fig.update_yaxes(title_text="Draw Rate (%)", secondary_y=True)
        
        fig.update_layout(
            height=self.config.CHART_HEIGHT,
            hovermode='x unified'
        )
        
        return fig
    
    def create_half_comparison_chart(self, time_analysis):
        """Create first half vs second half comparison - FIXED VERSION"""
        if not time_analysis or 'half_comparison' not in time_analysis:
            return go.Figure()
        
        half_data = time_analysis['half_comparison']
        
        if not half_data:
            return go.Figure()
        
        categories = ['Events', 'Goals', 'Shots', 'Yellow Cards']
        first_half = [
            half_data.get('first_half', {}).get('events', 0),
            half_data.get('first_half', {}).get('goals', 0),
            half_data.get('first_half', {}).get('shots', 0),
            half_data.get('first_half', {}).get('yellow_cards', 0)
        ]
        second_half = [
            half_data.get('second_half', {}).get('events', 0),
            half_data.get('second_half', {}).get('goals', 0),
            half_data.get('second_half', {}).get('shots', 0),
            half_data.get('second_half', {}).get('yellow_cards', 0)
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='First Half',
            x=categories,
            y=first_half,
            marker_color=self.colors['primary'],
            text=first_half,
            textposition='outside'
        ))
        
        fig.add_trace(go.Bar(
            name='Second Half',
            x=categories,
            y=second_half,
            marker_color=self.colors['success'],
            text=second_half,
            textposition='outside'
        ))
        
        fig.update_layout(
            title="First Half vs Second Half Comparison",
            xaxis_title="Metric",
            yaxis_title="Count",
            barmode='group',
            height=self.config.CHART_HEIGHT
        )
        
        return fig
    
    def create_tournament_progression_chart(self, stage_analysis):
        """Create tournament progression line chart - FIXED VERSION"""
        if not stage_analysis:
            return go.Figure()
        
        stages = ['Group Stage', 'Round of 16', 'Quarter Finals', 'Semi Finals', 'Final']
        goals_per_match = []
        competitiveness = []  # Inverse of average goal difference
        
        stage_mapping = {
            'Group Stage': 'group_stage',
            'Round of 16': 'round_16',
            'Quarter Finals': 'quarter_finals',
            'Semi Finals': 'semi_finals',
            'Final': 'final'
        }
        
        for stage in stages:
            stage_key = stage_mapping[stage]
            if stage_key in stage_analysis:
                goals_per_match.append(stage_analysis[stage_key].get('avg_goals', 0))
                # Competitiveness inverse of goal difference (lower diff = more competitive)
                if stage_key == 'round_16':
                    avg_diff = stage_analysis[stage_key].get('avg_goal_diff', 1.0)
                    competitiveness.append(1/avg_diff if avg_diff > 0 else 1.0)
                else:
                    competitiveness.append(1.0)  # Default high competitiveness for finals
            else:
                goals_per_match.append(0)
                competitiveness.append(0)
        
        if not any(goals_per_match):
            return go.Figure()
        
        fig = make_subplots(
            specs=[[{"secondary_y": True}]],
            subplot_titles=["Tournament Progression Analysis"]
        )
        
        # Goals per match
        fig.add_trace(
            go.Scatter(
                x=stages,
                y=goals_per_match,
                mode='lines+markers',
                name="Goals per Match",
                line=dict(color=self.colors['secondary'], width=3),
                marker=dict(size=10)
            ),
            secondary_y=False,
        )
        
        # Competitiveness
        fig.add_trace(
            go.Scatter(
                x=stages,
                y=competitiveness,
                mode='lines+markers',
                name="Competitiveness Index",
                line=dict(color=self.colors['primary'], width=3, dash='dash'),
                marker=dict(size=8)
            ),
            secondary_y=True,
        )
        
        fig.update_xaxes(title_text="Tournament Stage")
        fig.update_yaxes(title_text="Average Goals per Match", secondary_y=False)
        fig.update_yaxes(title_text="Competitiveness Index", secondary_y=True)
        
        fig.update_layout(
            height=self.config.CHART_HEIGHT,
            hovermode='x unified'
        )
        
        return fig
