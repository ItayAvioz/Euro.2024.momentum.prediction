# Euro 2024 Momentum Analytics Dashboard

## 🎯 Overview

Interactive Streamlit dashboard showcasing comprehensive analysis of Euro 2024 tournament data, including momentum prediction models and tactical insights.

## 📊 Features

### Current Pages
- **Tournament Overview**: Complete tournament statistics, scoring patterns, and key insights

### Planned Pages
- **Game Analysis**: Individual match analysis and momentum tracking
- **Time Analysis**: Temporal patterns and critical moments
- **Momentum Prediction**: Real-time momentum forecasting
- **ARIMAX Model Results**: Model performance and predictions

## 🚀 Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
```

### Running the Dashboard
```bash
cd Dashboard
streamlit run main.py
```

### Data Requirements
Ensure the following data files are available in the project:
- `Data/euro_2024_complete_dataset.csv`
- `Data/events_complete.csv` 
- `Data/matches_complete.csv`
- `thoughts/eda_insights.csv`
- `models/preprocessing/input_generation/momentum_windows_complete.csv`
- `models/modeling/scripts/outputs/predictions/arimax_predictions.csv`

## 📁 Project Structure

```
Dashboard/
├── main.py                    # Main Streamlit application
├── requirements.txt           # Python dependencies
├── README.md                 # This file
├── pages/                    # Dashboard pages
│   ├── __init__.py
│   └── tournament_overview.py
└── utils/                    # Utilities and helpers
    ├── __init__.py
    ├── config.py             # Configuration settings
    ├── data_loader.py        # Data loading utilities
    └── chart_helpers.py      # Chart creation helpers
```

## 📈 Key Metrics Displayed

### Tournament Overview
- **187,858 events** across 51 matches
- **126 goals** with 2.47 average per match
- **Stage-by-stage analysis** from group to final
- **Time-based patterns** including kickoff time impact
- **Half comparison** showing second half efficiency
- **Key insights** from comprehensive EDA analysis

## 🎨 Features

### Interactive Visualizations
- Plotly charts with hover details
- Multi-tab analysis sections
- Expandable insight summaries
- Responsive design for all screen sizes

### Data Insights
- EDA-validated tournament patterns
- Real statistical analysis
- Time-based momentum trends
- Stage progression analysis

### Performance Optimizations
- Streamlit caching for data loading
- Efficient chart rendering
- Modular component architecture

## 🔧 Technical Details

### Built With
- **Streamlit**: Interactive web application framework
- **Plotly**: Advanced charting and visualization
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations

### Data Sources
- Euro 2024 complete dataset (187,858 events)
- EDA insights (82 documented findings)
- ARIMAX model predictions
- Momentum calculation windows

## 📊 Dashboard Pages (Planned)

### 1. Tournament Overview ✅
- Complete tournament statistics
- Scoring patterns and trends
- Time-based analysis
- Key insights summary

### 2. Game Analysis 🔄
- Individual match breakdowns
- Team performance comparison
- Event timeline analysis
- Momentum flow visualization

### 3. Time Analysis 🔄
- Critical time windows
- Momentum peak detection
- Seasonal patterns
- Tactical timing insights

### 4. Momentum Prediction 🔄
- Real-time momentum forecasting
- 3-minute prediction windows
- Model confidence intervals
- Interactive prediction tools

### 5. ARIMAX Model Results 🔄
- 81.61% directional accuracy
- Model performance metrics
- Prediction comparisons
- Technical implementation details

## 🎯 Usage Examples

### View Tournament Statistics
Navigate to Tournament Overview to see:
- Overall tournament metrics
- Stage distribution analysis
- Scoring pattern insights
- Time-based performance

### Explore Data Interactively
- Click on charts for detailed views
- Use expandable sections for deeper analysis
- Export charts and data
- Filter by different criteria

## 🔄 Development Status

- ✅ **Tournament Overview**: Complete with all visualizations
- 🔄 **Game Analysis**: In development
- 🔄 **Time Analysis**: Planned
- 🔄 **Momentum Prediction**: Planned  
- 🔄 **ARIMAX Results**: Planned

## 📝 Notes

- Dashboard uses cached data loading for performance
- All statistics are based on real Euro 2024 data
- Insights derived from comprehensive EDA analysis
- Charts are interactive with hover tooltips
- Responsive design works on desktop, tablet, and mobile

## 🚀 Next Steps

1. Test Tournament Overview page with real data
2. Implement Game Analysis page
3. Add Time Analysis visualizations
4. Integrate ARIMAX model results
5. Add export and sharing capabilities

---

*Dashboard created for Euro 2024 Momentum Prediction Project*  
*Data: 187,858 events, 51 matches, 82 EDA insights*  
*Model: 81.61% ARIMAX directional accuracy*
