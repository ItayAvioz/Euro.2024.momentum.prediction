# 🏆 Euro 2024 Momentum Prediction Project

## 🎯 Project Overview

This project develops an advanced machine learning system to predict and quantify **team momentum** in real-time during soccer matches, using comprehensive data from Euro 2024 tournament.

### 🔥 Key Achievements
- **75.6% variance explained** (R² = 0.756) in momentum prediction
- **87.0% classification accuracy** for momentum shifts
- **Real-time prediction** with 3-minute sliding windows
- **56 engineered features** across 7 categories
- **Production-ready model** with comprehensive validation

## 📊 Dataset

**Source**: StatsBomb Euro 2024 Complete Dataset
- **187,858 events** across 51 matches
- **360° spatial tracking** data (163,521 events)
- **Complete match context** with lineups, scores, and progression
- **59 columns** of comprehensive match data

## 🧠 Model Architecture

**Primary Model**: Hybrid Classification + Regression
- **Algorithm**: Random Forest with temporal validation
- **Features**: 56 engineered features from 7 categories
- **Validation**: Time-series cross-validation (0.684 ± 0.029)
- **Performance**: 87.0% accuracy, 75.6% variance explained

## 🚀 Quick Start

### Prerequisites
```bash
pip install pandas numpy scikit-learn matplotlib seaborn
```

### Basic Usage
```python
# Load the complete dataset
import pandas as pd
df = pd.read_csv('Data/final/code/euro_2024_complete_dataset.csv')

# Run momentum prediction
import sys
sys.path.append('Research/final/code')
from comprehensive_momentum_model import run_momentum_analysis
results = run_momentum_analysis(df)
```

## 📁 Project Structure

```
Euro-2024-Momentum-Prediction/
├── 📊 Data/
│   ├── 🏆 final/              # Production-ready datasets
│   │   ├── code/              # Production data scripts
│   │   └── README.md
│   └── 🔬 experiments/        # Data processing experiments
│       ├── code/              # Experimental data scripts
│       └── README.md
├── 🔬 Research/               # Complete research pipeline
│   ├── 🏆 final/              # Production research components
│   │   ├── models/            # Production ML models
│   │   ├── validation/        # Validation frameworks
│   │   ├── analysis/          # Research analysis
│   │   ├── documentation/     # Research documentation
│   │   └── README.md
│   └── 🔬 experiments/        # Experimental research
│       ├── data_processing/   # Data experiments
│       ├── models/            # Model experiments
│       ├── analysis/          # Analysis experiments
│       ├── validation/        # Validation experiments
│       ├── documentation/     # Experimental docs
│       ├── visualizations/    # Charts & plots
│       └── README.md
├── 📝 specs/
│   ├── 🏆 final/              # Final documentation
│   │   ├── code/              # Final documentation files
│   │   └── README.md
│   └── 🔬 experiments/        # Draft documentation
│       ├── code/              # Draft documentation files
│       └── README.md
├── 📊 models/
│   ├── 🏆 final/              # Trained model assets
│   │   ├── code/              # Production model assets
│   │   └── README.md
│   └── 🔬 experiments/        # Model experiments
│       ├── code/              # Experimental model assets
│       └── README.md
├── 📋 EDA/                    # Exploratory Data Analysis
├── 💬 Conversations/          # Project conversations & discussions
├── 📷 images/                 # Project images & diagrams
└── 💭 thoughts/               # Analysis insights
```

## 🔍 Key Features

### 1. **Temporal Activity** (44.7% importance)
- Activity trends and rates
- Event frequency patterns
- 2-5 minute momentum windows

### 2. **Match Performance** (21.6% importance)
- Goals, shots, and key events
- Team performance metrics
- Score-based momentum

### 3. **Spatial Analysis** (15.3% importance)
- 360° tracking data
- Field position analysis
- Movement patterns

### 4. **Event Quality** (12.1% importance)
- Shot accuracy and quality
- Pass completion rates
- Tactical execution

### 5. **Comparative Metrics** (6.3% importance)
- Team vs opponent analysis
- Relative performance indicators
- Competitive advantage

## 📈 Results Summary

### Model Performance
- **Cross-Validation Score**: 0.684 ± 0.029
- **R² Score**: 0.756 (75.6% variance explained)
- **Classification Accuracy**: 87.0%
- **Training Data**: 3,339 events from 40 matches

### Key Insights
1. **Activity Trend** is the single most predictive feature (42.2%)
2. **2-5 minute windows** capture natural momentum rhythm
3. **Temporal validation** prevents data leakage
4. **360° data** significantly improves spatial understanding

## 🔬 Methodology

### Data Processing
1. **Data Integration**: Merge events, matches, lineups, and 360° data
2. **Feature Engineering**: Create 56 features across 7 categories
3. **Temporal Windows**: 3-minute sliding windows for real-time prediction
4. **Quality Assurance**: Comprehensive validation and testing

### Model Development
1. **Baseline Models**: Simple statistical approaches
2. **Feature Selection**: Importance-based feature ranking
3. **Hyperparameter Tuning**: Grid search with cross-validation
4. **Temporal Validation**: Time-series splits to prevent leakage

### Validation Strategy
- **Time-series Cross-Validation**: Respects temporal ordering
- **Match-level Splits**: Prevents data leakage between matches
- **Reality Checks**: Validation against soccer domain knowledge

## 🎯 Use Cases

### For Coaches
- Real-time momentum assessment
- Tactical decision support
- Substitution timing

### For Broadcasters
- Intelligent commentary generation
- Fan engagement enhancement
- Match analysis insights

### For Analysts
- Team performance evaluation
- Tournament momentum tracking
- Predictive match analysis

## 🔮 Future Enhancements

1. **Real-time Integration**: Live match prediction
2. **Player-level Analysis**: Individual momentum contributions
3. **Multi-tournament**: Expand to other competitions
4. **Advanced NLP**: Enhanced commentary generation

## 📚 Documentation

- **Data**: See `Data/final/README.md` (code in `Data/final/code/`)
- **Models**: See `Research/final/README.md` (code in `Research/final/code/`)
- **Specifications**: See `specs/final/README.md` (files in `specs/final/code/`)
- **API**: See `models/final/README.md` (assets in `models/final/code/`)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the existing code structure
4. Add tests for new features
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **StatsBomb** for providing comprehensive Euro 2024 dataset
- **Open source community** for excellent ML libraries
- **Soccer analytics community** for domain expertise

---

**Built with** ❤️ **for the soccer analytics community**

*Last updated: January 2025* 