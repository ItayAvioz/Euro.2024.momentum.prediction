# Commentary Analysis Dashboard

Interactive Streamlit dashboard for analyzing generated vs real football commentary comparisons.

## 📊 Overview

This dashboard provides a comprehensive analysis of our generated commentary compared to real commentary from multiple sources:
- **FlashScore** (51 games)
- **SportsMole** (6 games)
- **BBC** (4 games)
- **FOX** (4 games)
- **ESPN** (4 games)

## 🚀 How to Run

### Prerequisites

Make sure you have Python 3.8+ installed.

### Installation

1. Navigate to this directory:
```bash
cd "C:\Users\yonatanam\Desktop\Euro 2024 - momentum - DS-AI project\NLP - Commentator\research\09_dashboard_analysis"
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

### Running the Dashboard

```bash
streamlit run app.py
```

The dashboard will automatically open in your default web browser at `http://localhost:8501`

## 📈 Dashboard Features

### Section 1: General Information
- Total games covered
- Number of data sources
- Total comparisons performed
- Games per data source breakdown (table + chart)

### Section 2: Best Commentary Selection
For each real commentary entry, the dashboard:
- Selects the best generated sequence match
- Two selection methods available:
  - **With Sentiment**: Uses `avg_score` (includes sentiment difference)
  - **Without Sentiment**: Uses `average_score_no_sentiment` (excludes sentiment)

### Section 3: Summary Statistics
Calculated on best matches only:
- **TF-IDF**: Mean cosine similarity using TF-IDF vectors
- **Embeddings (BERT)**: Mean cosine similarity using BERT embeddings
- **Content Overlap Ratio**: Mean Jaccard similarity of content words
- **Sentiment Diff**: Mean absolute difference in sentiment
- **Avg Score**: Mean overall score (with sentiment)
- **Avg Score (No Sentiment)**: Mean overall score (without sentiment)
- **Total Commentary Count**: Total best-match commentaries
- **Commentary Avg per Game**: Average commentaries per game
- **Selection Overlap %**: Percentage where both methods select the same sequence

## 📁 Data Source

The dashboard loads data from:
```
../08_enhanced_comparison/data/match_*_enhanced_comparison.csv
```

**Total Files**: 69 CSV files (all Euro 2024 matches across all sources)

## 🔧 Technical Details

### Data Processing Logic

1. **Load All Data**: Combines all 69 comparison CSVs
2. **Best Match Selection**: For each unique real commentary (identified by source, match_id, minute, real_commentary), selects the generated sequence with the highest score
3. **Statistics Calculation**: Computes mean values across all best matches

### Scoring Methods

#### With Sentiment (`avg_score`)
```
avg_score = (TF-IDF + Embeddings_BERT + content_overlap_ratio + (1 - sentiment_diff)) / 4
```

#### Without Sentiment (`average_score_no_sentiment`)
```
average_score_no_sentiment = (TF-IDF + Embeddings_BERT + content_overlap_ratio) / 3
```

## 📊 Metrics Explained

| Metric | Description | Range |
|--------|-------------|-------|
| **TF-IDF** | Lexical similarity (word overlap) | 0-1 |
| **Embeddings (BERT)** | Semantic similarity (meaning) | 0-1 |
| **Content Overlap** | Jaccard similarity of content words | 0-1 |
| **Sentiment Diff** | Absolute difference in sentiment | 0-2 |
| **Avg Score** | Overall similarity (with sentiment) | 0-1 |
| **Avg Score (No Sentiment)** | Overall similarity (without sentiment) | 0-1 |

## 🎯 Use Cases

1. **Performance Evaluation**: Understand how well our generated commentary matches real commentary
2. **Source Comparison**: See which data source we match best
3. **Metric Analysis**: Identify which similarity metrics are most important
4. **Sentiment Impact**: Compare results with and without sentiment consideration

## 📝 Notes

- The dashboard uses Streamlit's caching to optimize performance
- Data is loaded once and cached for the session
- Switching between "With Sentiment" and "Without Sentiment" recalculates best matches instantly
- All stoppage time, extra time, and penalty commentary is included in counts

## 🔄 Future Enhancements

Potential additions to the dashboard:
- Match-specific drill-down view
- Source-specific comparison
- Time-series analysis (minute-by-minute)
- Distribution visualizations (histograms, box plots)
- Top/bottom performing sequences viewer
- Export functionality for filtered results

## 📧 Support

For issues or questions, refer to the main project documentation.

---

**Last Updated**: November 10, 2025  
**Version**: 1.0.0  
**Project**: Euro 2024 NLP Commentator

