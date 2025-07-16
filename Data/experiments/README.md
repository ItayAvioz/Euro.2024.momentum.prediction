# 🔬 Data/experiments - Data Processing Experiments

## 🎯 Overview

This folder contains **experimental data processing scripts** and **intermediate datasets** used during the development of the final data pipeline. These files show the iterative process of data cleaning, feature engineering, and quality improvement.

## 📋 File Categories

### 📁 **Code Folder Structure**
```
Data/experiments/
├── code/                       # Experimental data scripts and datasets
│   ├── Data Processing Scripts/
│   │   ├── add_event_uuid_back.py
│   │   ├── add_team_ids_back.py
│   │   ├── add_team_names_back.py
│   │   ├── clean_events_360.py
│   │   ├── clean_matches_lineups.py
│   │   ├── create_events_360.py
│   │   └── create_matches_lineups.py
│   ├── Analysis & Validation Scripts/
│   │   ├── analyze_360_data_coverage.py
│   │   ├── analyze_events_360_columns.py
│   │   ├── analyze_team_duplicates.py
│   │   ├── check_missing_team_names.py
│   │   ├── check_stats.py
│   │   └── remove_team_duplicates.py
│   ├── Data Analysis & Documentation/
│   │   ├── comprehensive_data_analysis.py
│   │   ├── enhanced_data_analysis.py
│   │   ├── enhanced_data_analysis_complete.py
│   │   ├── enhanced_data_analysis_fixed.py
│   │   └── euro_2024_data_transformation_summary.py
│   ├── Documentation Scripts/
│   │   ├── create_enhanced_documentation.py
│   │   └── simple_documentation_creator.py
│   └── Dataset Files/
│       ├── events_360.csv
│       └── matches_lineups.csv
└── README.md                   # This documentation
```

### 🔧 **Data Processing Scripts**
- **`code/add_event_uuid_back.py`** - Restore event UUIDs for 360° linking
- **`code/add_team_ids_back.py`** - Add team identification columns
- **`code/add_team_names_back.py`** - Restore team name information
- **`code/clean_events_360.py`** - Clean 360° tracking data
- **`code/clean_matches_lineups.py`** - Process match and lineup data
- **`code/create_events_360.py`** - Create 360° event dataset
- **`code/create_matches_lineups.py`** - Merge match and lineup data

### 🔍 **Analysis & Validation Scripts**
- **`code/analyze_360_data_coverage.py`** - Check 360° data completeness
- **`code/analyze_events_360_columns.py`** - Analyze 360° column structure
- **`code/analyze_team_duplicates.py`** - Find duplicate team entries
- **`code/check_missing_team_names.py`** - Validate team name completeness
- **`code/check_stats.py`** - General data quality checks
- **`code/remove_team_duplicates.py`** - Clean duplicate team records

### 📊 **Data Analysis & Documentation**
- **`code/comprehensive_data_analysis.py`** - Complete data analysis
- **`code/enhanced_data_analysis.py`** - Enhanced analysis with insights
- **`code/enhanced_data_analysis_complete.py`** - Full analysis pipeline
- **`code/enhanced_data_analysis_fixed.py`** - Fixed analysis version
- **`code/euro_2024_data_transformation_summary.py`** - Data transformation summary

### 📝 **Documentation Scripts**
- **`code/create_enhanced_documentation.py`** - Create comprehensive docs
- **`code/simple_documentation_creator.py`** - Simple documentation generator

### 📋 **Dataset Files**
- **`code/events_360.csv`** - 360° events (intermediate)
- **`code/matches_lineups.csv`** - Match-lineup merge (intermediate)

## 🔄 Processing Pipeline Evolution

### Phase 1: Initial Data Loading
```
Raw StatsBomb Files
    ↓
Basic CSV Loading
    ↓
Initial Data Exploration
```

### Phase 2: Data Cleaning
```
Data Quality Issues Identified
    ↓
clean_events_360.py
    ↓
clean_matches_lineups.py
    ↓
remove_team_duplicates.py
```

### Phase 3: Feature Integration
```
Separate Data Sources
    ↓
add_event_uuid_back.py
    ↓
add_team_ids_back.py
    ↓
add_team_names_back.py
```

### Phase 4: Quality Validation
```
Data Integration Complete
    ↓
analyze_360_data_coverage.py
    ↓
check_missing_team_names.py
    ↓
comprehensive_data_analysis.py
```

## 🚀 Key Experiments

### 1. **360° Data Integration**
**Problem**: 360° tracking data was separate from events
**Solution**: `create_events_360.py` + `add_event_uuid_back.py`
**Result**: 87% coverage (163,521/187,858 events)

### 2. **Team Information Consistency**
**Problem**: Team names/IDs inconsistent across datasets
**Solution**: `add_team_names_back.py` + `analyze_team_duplicates.py`
**Result**: 100% team identification accuracy

### 3. **Match Context Integration**
**Problem**: Events lacked full match context
**Solution**: `create_matches_lineups.py`
**Result**: Complete match information for all events

### 4. **Data Quality Assurance**
**Problem**: Unknown data quality issues
**Solution**: `comprehensive_data_analysis.py`
**Result**: <0.1% missing values in critical columns

## 📊 Experimental Results

### Data Coverage Analysis
```python
# From analyze_360_data_coverage.py
Total Events: 187,858
360° Events: 163,521 (87.0%)
Missing 360°: 24,337 (13.0%)
```

### Team Validation Results
```python
# From check_missing_team_names.py
Team Name Coverage: 100%
Team ID Coverage: 100%
Duplicate Teams: 0 (after cleaning)
```

### Match Context Results
```python
# From comprehensive_data_analysis.py
Complete Match Info: 100%
Lineup Coverage: 100%
Score Information: 100%
```

## 🔍 Usage Examples

### Run Data Quality Check
```python
# Check overall data quality
python check_stats.py

# Analyze 360° coverage
python analyze_360_data_coverage.py

# Check team information
python check_missing_team_names.py
```

### Recreate Data Pipeline
```python
# Step 1: Clean base data
python clean_events_360.py
python clean_matches_lineups.py

# Step 2: Add identifiers
python add_event_uuid_back.py
python add_team_ids_back.py

# Step 3: Comprehensive analysis
python comprehensive_data_analysis.py
```

## 📈 Performance Lessons

### What Worked
- **Incremental Processing**: Small, focused scripts
- **Validation at Each Step**: Catch issues early
- **Comprehensive Analysis**: Full data understanding

### What Didn't Work
- **Monolithic Processing**: Large scripts were harder to debug
- **Skip Validation**: Led to downstream issues
- **Assume Data Quality**: Always validate first

## 🚨 Important Notes

1. **Experimental Nature**: These are development files
2. **Not Production**: Use `Data/final/` for production work
3. **Documentation**: Each major experiment documented
4. **Version Control**: Track changes in these experiments
5. **Learning Value**: Shows problem-solving process

## 🔄 Evolution to Final Pipeline

```
🔬 EXPERIMENTS (This Folder)
    ↓
Lessons Learned
    ↓
Best Practices Identified
    ↓
📊 FINAL PIPELINE (Data/final/)
```

## 📞 Support

- **Historical Context**: See git history for development timeline
- **Questions**: Compare with final pipeline in `Data/final/`
- **Issues**: These are experimental - use final versions

---

**🔬 Development Archive**: Shows the journey to production-ready data 