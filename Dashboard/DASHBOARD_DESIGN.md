# 📊 Euro 2024 Momentum Analytics Dashboard Design

## 🎯 Overall Structure

The dashboard will be organized into multiple pages:
1. **Tournament Overview** (Current Focus)
2. Game Analysis (TBD)
3. Time Analysis (TBD)
4. Momentum Prediction (TBD)
5. ARIMAX Model Results (TBD)

---

## 📈 Page 1: Tournament Overview

### 1. Header Section
```python
st.title("Euro 2024 Tournament Analytics")
st.subheader("Comprehensive Tournament Analysis & Momentum Insights")

# Tournament Summary Stats in Columns
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Matches", "51")
with col2:
    st.metric("Total Events", "187,858")
with col3:
    st.metric("Total Goals", "126")
with col4:
    st.metric("Avg Goals/Match", "2.47")
```

### 2. Tournament Stage Distribution
```python
# Interactive Pie Chart
st.subheader("Tournament Stage Distribution")
stage_data = {
    "Group Stage": 36,
    "Round of 16": 8,
    "Quarter-finals": 4,
    "Semi-finals": 2,
    "Final": 1
}
# Plotly pie chart with hover info showing matches and goals per stage
```

### 3. Scoring Patterns
```python
# Multi-tab section
tab1, tab2 = st.tabs(["Goals Distribution", "Scoring Times"])

with tab1:
    st.subheader("Goals Distribution by Stage")
    # Bar chart showing:
    # - Group Stage: 2.25 goals/game
    # - Round of 16: 2.00 goals/game
    # - Quarter-finals: 1.60 goals/game (normalized)
    # - Semi-finals & Final: 1.00 goals/game

with tab2:
    st.subheader("Goal Timing Analysis")
    # Line chart showing:
    # - First Half: 47 goals (37.3%)
    # - Second Half: 58 goals (46.0%)
    # - Extra Time: 21 goals (16.7%)
```

### 4. Match Outcome Analysis
```python
# Interactive section with filters
st.subheader("Match Outcomes Analysis")

# Selectbox for viewing different metrics
metric = st.selectbox("Select Metric", 
    ["Result Distribution", "Goal Margin", "Draw Analysis"])

if metric == "Result Distribution":
    # Pie chart showing:
    # - Home wins: 35%
    # - Away wins: 32%
    # - Draws: 33%
elif metric == "Goal Margin":
    # Bar chart showing:
    # - 1-goal margin: 39.2%
    # - 2+ goals margin: 27.5%
    # - Draws: 33.3%
else:  # Draw Analysis
    # Line chart showing draw progression:
    # - Halftime: 52.9% draws
    # - Full-time: 33.3% draws
    # - Draw → Win conversion: 27.5%
```

### 5. Event Analysis
```python
# Expandable section
with st.expander("Detailed Event Analysis"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Event Type Distribution")
        # Bar chart showing top events:
        # - Pass: 53,890 (28.7%)
        # - Carry: 44,139 (23.5%)
        # - Pressure: 19,242 (10.2%)
        # - Ball Recovery: 14,673 (7.8%)
        # - Others: 29.8%

    with col2:
        st.subheader("Shot Analysis")
        # Pie chart showing shot outcomes:
        # - On Target: 557 (41.6%)
        # - Off Target: 397 (29.6%)
        # - Blocked: 386 (28.8%)
        # - Goals: 126 (9.4%)
```

### 6. Time-Based Insights
```python
# Interactive time analysis
st.subheader("Kickoff Time Impact")

# Three-column metrics for different kickoff times
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("16:00 Kickoffs", 
              "3.00 goals/match",
              "Highest scoring")
    st.text("42.9% draws")
    
with col2:
    st.metric("19:00 Kickoffs",
              "2.44 goals/match",
              "Balanced outcomes")
    st.text("33.3% draws")
    
with col3:
    st.metric("22:00 Kickoffs",
              "2.00 goals/match",
              "Most decisive")
    st.text("30.8% draws")
```

### 7. Half-by-Half Comparison
```python
# Side-by-side comparison
st.subheader("First Half vs Second Half")

comparison_data = {
    "Total Events": ["93,628", "88,447"],
    "Goals": ["47", "58"],
    "Shots": ["568", "694"],
    "Yellow Cards": ["9", "42"],
    "Substitutions": ["6", "443"],
    "Goal/Shot Ratio": ["8.3%", "8.4%"]
}

# Create a styled DataFrame with color coding
# Green highlights for better performance
```

### 8. Tournament Progression
```python
# Line chart showing key metrics over tournament phases
st.subheader("Tournament Evolution")

# Multi-line chart showing:
# 1. Goals per match trend
# 2. Events per match trend
# 3. Cards per match trend
# 4. Draw percentage trend

# Add annotations for key points:
# - Group Stage adaptation
# - Knockout intensity
# - Final stages caution
```

### 9. Interactive Data Explorer
```python
# Advanced data exploration section
st.subheader("Custom Data Analysis")

# Allow users to:
# 1. Select metrics to compare
# 2. Choose visualization type
# 3. Filter by tournament phase
# 4. Export selected data

# Include download buttons for:
# - Full statistics CSV
# - Generated charts
# - Analysis summary
```

### 10. Key Insights Summary
```python
# Collapsible sections with key findings
st.subheader("Tournament Key Insights")

with st.expander("Scoring Patterns"):
    st.write("""
    - Second half 23.4% more efficient
    - Late goals (75-90 min) most common
    - 27.5% of draws become wins
    """)

with st.expander("Match Evolution"):
    st.write("""
    - 41.2% matches change result HT-FT
    - 52.9% draws at HT → 33.3% at FT
    - 89% increase in goal difference HT-FT
    """)

with st.expander("Time Impact"):
    st.write("""
    - 16:00: Highest scoring (3.00 goals/match)
    - 19:00: Most balanced (2.44 goals/match)
    - 22:00: Most decisive (2.00 goals/match)
    """)
```

---

## 🎨 Design Elements

### Color Scheme
- Primary: #1f77b4 (Tournament blue)
- Secondary: #ff7f0e (Goal orange)
- Success: #2ca02c (Win green)
- Warning: #d62728 (Loss red)
- Neutral: #7f7f7f (Draw gray)

### Interactive Features
- Hover tooltips with detailed stats
- Click-through capabilities for drill-down analysis
- Dynamic filters for all visualizations
- Export functionality for all charts and data
- Responsive layout for different screen sizes

### Data Updates
- Real-time calculation of statistics
- Caching for heavy computations
- Progress bars for long-loading sections
- Error handling with user-friendly messages

---

## 📱 Responsive Design

### Desktop View
- Full-width visualizations
- Side-by-side comparisons
- Detailed tooltips and legends

### Tablet View
- Stacked layout for complex charts
- Scrollable tables
- Simplified tooltips

### Mobile View
- Single column layout
- Collapsible sections
- Essential metrics only

---

## 🔄 Next Steps

1. Implement Tournament Overview page
2. Gather feedback on layout and metrics
3. Design Game Analysis page
4. Add interactive features
5. Implement data caching
6. Add export functionality

---

*Note: This design focuses on the Tournament Overview page. Subsequent pages will be designed after implementation and feedback on this initial page.*
