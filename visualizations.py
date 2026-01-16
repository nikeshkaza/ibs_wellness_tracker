import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, Any, List

class Visualizer:
    def create_symptom_chart(self, data: pd.DataFrame) -> go.Figure:
        """Create interactive symptom severity trend chart."""
        if data.empty or 'symptom_severity' not in data.columns:
            return self._create_empty_figure("No Data Available")

        fig = go.Figure()
        
        # Add line trace with fill
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['symptom_severity'],
            mode='lines+markers',
            fill='tozeroy',
            name='Severity',
            line=dict(color='#FF4B4B', width=3),
            marker=dict(size=8, color='#FF4B4B'),
            hovertemplate='<b>Date</b>: %{x}<br><b>Severity</b>: %{y}<extra></extra>'
        ))

        fig.update_layout(
            title="Symptom Severity Trend",
            yaxis=dict(title="Severity (1-10)", range=[0, 11]),
            xaxis=dict(title="Date", tickformat="%d %b"),
            hovermode="x unified",
            template="plotly_white",
            height=400
        )
        return fig

    def create_sleep_chart(self, data: pd.DataFrame) -> go.Figure:
        """Create dual-axis sleep chart (hours vs quality)."""
        if data.empty or 'sleep_hours' not in data.columns:
            return self._create_empty_figure("No Data Available")

        fig = go.Figure()

        # Bar chart for hours
        fig.add_trace(go.Bar(
            x=data.index,
            y=data['sleep_hours'],
            name='Sleep Hours',
            marker_color='#4B9CFF',
            opacity=0.7,
            hovertemplate='<b>Hours</b>: %{y}<extra></extra>'
        ))

        # Line chart for quality
        if 'sleep_quality' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['sleep_quality'],
                name='Sleep Quality',
                yaxis='y2',
                mode='lines+markers',
                line=dict(color='#FFB347', width=3),
                marker=dict(symbol='square', size=8),
                hovertemplate='<b>Quality</b>: %{y}/10<extra></extra>'
            ))

        fig.update_layout(
            title="Sleep Duration & Quality",
            yaxis=dict(title="Hours"),
            yaxis2=dict(
                title="Quality (1-10)",
                overlaying='y',
                side='right',
                range=[0, 11]
            ),
            xaxis=dict(title="Date", tickformat="%d %b"),
            barmode='group',
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=400
        )
        return fig

    def create_stress_chart(self, data: pd.DataFrame) -> go.Figure:
        """Create color-coded stress level chart."""
        if data.empty or 'stress_level' not in data.columns:
            return self._create_empty_figure("No Data Available")

        # Color generation
        colors = ['#4CAF50' if x < 4 else '#FF9800' if x < 8 else '#F44336' for x in data['stress_level']]

        fig = go.Figure(go.Bar(
            x=data.index,
            y=data['stress_level'],
            marker_color=colors,
            text=data['stress_level'],
            textposition='auto',
            name='Stress Level',
            hovertemplate='<b>Stress Level</b>: %{y}/10<extra></extra>'
        ))

        fig.update_layout(
            title="Daily Stress Levels",
            yaxis=dict(title="Stress Level (1-10)", range=[0, 11]),
            xaxis=dict(title="Date", tickformat="%d %b"),
            template="plotly_white",
            showlegend=False,
            height=400
        )
        return fig
        
    def create_correlation_heatmap(self, data: pd.DataFrame) -> go.Figure:
        """Create a correlation heatmap of key metrics."""
        if data.empty or len(data) < 3: # Need minimal data for correlation
            return self._create_empty_figure("Needs more data for correlation")
            
        cols = ['symptom_severity', 'sleep_hours', 'sleep_quality', 'stress_level', 'exercise']
        # Filter for existing columns
        valid_cols = [c for c in cols if c in data.columns]
        
        if len(valid_cols) < 2:
             return self._create_empty_figure("Not enough metrics for correlation")

        corr = data[valid_cols].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr.values,
            x=valid_cols,
            y=valid_cols,
            colorscale='RdBu_r', # Red = positive correlation (bad for symptoms), Blue = negative
            zmin=-1, zmax=1,
            text=corr.values,
            texttemplate="%{text:.2f}"
        ))
        
        fig.update_layout(
            title="Correlation Matrix (What affects what?)",
            height=400,
            template="plotly_white"
        )
        return fig

    def create_lagged_correlation_chart(self, data: pd.DataFrame) -> go.Figure:
        """
        Create a bar chart showing correlation of Today's Symptoms vs:
        1. Today's Stress/Sleep (Lag 0)
        2. Yesterday's Stress/Sleep (Lag 1)
        """
        if data.empty or len(data) < 3:
            return self._create_empty_figure("Need more data for lag analysis")
            
        target = 'symptom_severity'
        if target not in data.columns:
            return self._create_empty_figure("No symptom data")

        # Define features to test
        features = {
            'Stress (Today)': 'stress_level',
            'Stress (Yesterday)': 'stress_lag1',
            'Sleep (Hours Today)': 'sleep_hours',
            'Sleep (Yesterday)': 'sleep_lag1'
        }
        
        correlations = {}
        for label, col in features.items():
            if col in data.columns:
                # Calculate correlation, ignoring NaNs
                corr = data[[target, col]].corr().iloc[0, 1]
                correlations[label] = corr
        
        if not correlations:
             return self._create_empty_figure("Not enough matched data")

        # Convert to DF for plotting
        corr_df = pd.DataFrame(list(correlations.items()), columns=['Factor', 'Correlation'])
        
        # Color: Red for positive correlation (bad), Blue for negative (good/neutral)
        corr_df['Color'] = ['#FF4B4B' if x > 0 else '#4B9CFF' for x in corr_df['Correlation']]

        fig = go.Figure(go.Bar(
            x=corr_df['Factor'],
            y=corr_df['Correlation'],
            marker_color=corr_df['Color'],
            text=corr_df['Correlation'].apply(lambda x: f"{x:.2f}"),
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Correlation: %{y:.2f}<extra></extra>'
        ))

        fig.update_layout(
            title="Symptom Drivers: Today vs. Yesterday",
            yaxis=dict(title="Correlation (-1 to +1)", range=[-1, 1]),
            template="plotly_white",
            height=400,
            showlegend=False
        )
        # Add interpretation line
        fig.add_hline(y=0, line_dash="solid", line_color="black", opacity=0.3)
        
        return fig

    def _create_empty_figure(self, message: str) -> go.Figure:
        """Helper to create an empty figure with a message."""
        fig = go.Figure()
        fig.update_layout(
            xaxis={"visible": False},
            yaxis={"visible": False},
            annotations=[
                {
                    "text": message,
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {"size": 20}
                }
            ]
        )
        return fig
