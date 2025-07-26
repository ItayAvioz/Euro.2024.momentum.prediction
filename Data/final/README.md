# 📊 Data/final - Production-Ready Datasets

## 🎯 Overview

This folder contains the **production-ready datasets** used for momentum prediction analysis. These are the clean, validated, and feature-engineered datasets that power the final model.

## 📋 Dataset Files

### 📁 **Code Folder Structure**
```
Data/final/
├── code/                       # Production data scripts and datasets
│   ├── euro_2024_complete_dataset.csv
│   ├── events_complete.csv
│   ├── matches_complete.csv
│   ├── lineups_complete.csv
│   ├── data_360_complete.csv
│   └── create_final_euro_2024_dataset.py
└── README.md                   # This documentation
```

### 🏆 **Primary Dataset**
- **`code/euro_2024_complete_dataset.csv`** *(187,858 rows × 59 columns)*
  - **Description**: Complete Euro 2024 dataset with all events and features
  - **Size**: ~45MB
  - **Key Features**: 360° tracking, team context, match progression
  - **Status**: ✅ Production Ready

### 🔧 **Component Datasets**
- **`code/events_complete.csv`** *(Event-level data)*
  - All match events with contextual information
  - Includes passes, shots, tackles, etc.
  - Event UUIDs for 360° data linkage

- **`code/matches_complete.csv`** *(Match-level data)*
  - Complete match information
  - Scores, dates, tournament progression
  - Team lineups and formations

- **`code/lineups_complete.csv`** *(Player-level data)*
  - Starting lineups for all matches
  - Player positions and jersey numbers
  - Substitution information

- **`code/data_360_complete.csv`** *(Spatial tracking data)*
  - 360° player and ball tracking
  - Field coordinates and movement
  - Available for 163,521 events

### 🔄 **Data Pipeline**
- **`code/create_final_euro_2024_dataset.py`** *(Main data pipeline)*
  - **Purpose**: Creates the complete dataset from components
  - **Input**: Raw StatsBomb files
  - **Output**: Production-ready euro_2024_complete_dataset.csv
  - **Status**: ✅ Production Ready

## 📊 Data Schema

### Key Columns
```python
# Event Information
- event_id, event_uuid, index, period, timestamp, minute, second
- type_name, team_name, player_name, position_name

# Match Context  
- match_id, match_date, home_team_name, away_team_name
- home_score, away_score, competition_stage_name

# 360° Data
- freeze_frame (when available)
- player_coordinates, ball_coordinates

# Engineered Features
- momentum_score, activity_trend, team_events_2min
- shot_accuracy, pass_completion_rate, spatial_control
```

## 🔍 Data Quality

### ✅ **Validation Status**
- **Data Completeness**: 100% for core events
- **360° Coverage**: 87.0% (163,521/187,858 events)
- **Missing Values**: <0.1% in critical columns
- **Consistency**: All matches validated

### 📊 **Statistics**
- **Total Events**: 187,858
- **Total Matches**: 51
- **Date Range**: June 14 - July 14, 2024
- **Teams**: 24 national teams
- **Event Types**: 42 different types

## 🚀 Usage Examples

### Load Complete Dataset
```python
import pandas as pd

# Load main dataset
df = pd.read_csv('Data/final/code/euro_2024_complete_dataset.csv')
print(f"Dataset shape: {df.shape}")
print(f"Memory usage: {df.memory_usage().sum() / 1024**2:.1f} MB")
```

### Filter by Match
```python
# Get specific match
england_spain_final = df[
    (df['home_team_name'] == 'England') & 
    (df['away_team_name'] == 'Spain')
]
```

### Access 360° Data
```python
# Get events with 360° tracking
events_360 = df[df['event_uuid'].notna()]
print(f"360° events: {len(events_360):,}")
```

## 🔗 Data Relationships

```
euro_2024_complete_dataset.csv
├── Links to → events_complete.csv (via event_id)
├── Links to → matches_complete.csv (via match_id)  
├── Links to → lineups_complete.csv (via match_id)
└── Links to → data_360_complete.csv (via event_uuid)
```

## 📈 Performance Considerations

### Memory Usage
- **Full Dataset**: ~45MB RAM
- **Recommended**: 8GB+ system RAM
- **Optimization**: Use chunking for large operations

### Loading Time
- **SSD**: ~2-3 seconds
- **HDD**: ~8-12 seconds
- **Network**: Depends on bandwidth

## 🚨 Important Notes

1. **Data Integrity**: Never modify files in this folder directly
2. **Versioning**: All datasets are final versions
3. **Backup**: Keep copies before major analysis
4. **Memory**: Large datasets - monitor RAM usage
5. **Consistency**: All files use UTF-8 encoding

## 🔄 Data Lineage

```
Raw StatsBomb Data
    ↓
Data Processing Pipeline
    ↓
Feature Engineering
    ↓
Quality Validation
    ↓
📊 FINAL DATASETS (This Folder)
    ↓
ML Model Training
```

## 📞 Support

- **Issues**: Report data quality issues via GitHub
- **Questions**: See main project README
- **Updates**: Check version history in git commits

---

**⚠️ Production Data**: Handle with care - used by production models 