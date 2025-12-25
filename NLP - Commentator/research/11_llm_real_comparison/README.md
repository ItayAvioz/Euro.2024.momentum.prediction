# LLM vs Real Commentary Comparison

Compare AI-generated (GPT-4o-mini) commentary with real ESPN/BBC/Fox/FlashScore commentary.

## Structure

```
11_llm_real_comparison/
├── app.py                    # Streamlit dashboard
├── scripts/
│   └── generate_comparison.py  # Generate comparison CSVs
├── data/                     # Output comparison CSVs
├── utils/
├── requirements.txt
├── run_dashboard.bat
└── README.md
```

## Usage

### Step 1: Generate Comparison Data

```bash
cd scripts
python generate_comparison.py
```

This creates comparison CSVs in `data/` folder:
- `match_XXXXXX_espn_llm_comparison.csv`
- `match_XXXXXX_bbc_llm_comparison.csv`
- `match_XXXXXX_flashscore_llm_comparison.csv`
- etc.

### Step 2: Run Dashboard

```bash
streamlit run app.py
```

Or double-click `run_dashboard.bat`

## Features

### Dashboard Tabs

1. **Overview**: Score distribution, by event type, over time
2. **Side-by-Side**: Compare LLM vs Real commentary minute by minute
3. **Analysis**: Best/worst matches, statistics
4. **Data**: Raw data view with download

### Metrics

| Metric | Description |
|--------|-------------|
| **Average Score** | Combined similarity (TF-IDF + BERT + Overlap) with sentiment adjustment |
| **TF-IDF** | Term frequency similarity |
| **BERT** | Semantic embedding similarity |
| **Content Overlap** | Word overlap ratio |
| **Sentiment Diff** | Difference in sentiment polarity |

### Multi-Event Handling

When multiple events occur in the same minute:
- LLM: May have multiple commentaries (Goal + Card)
- Real: May have multiple lines
- **All combinations are compared** (2 LLM × 3 Real = 6 comparisons)

## Data Sources

### LLM Commentary
- V3 output from `10_llm_commentary/data/llm_commentary/all_matches_V3_*.csv`

### Real Commentary
From `05_real_commentary_comparison/data/`:
- ESPN (5 matches)
- BBC (5 matches)  
- Fox (5 matches)
- FlashScore (51 matches)
- Sports Mole (7 matches)

