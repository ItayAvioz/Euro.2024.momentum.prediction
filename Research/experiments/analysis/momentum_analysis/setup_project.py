#!/usr/bin/env python3
"""
StatsBomb Project Setup Script
Sets up your environment for soccer prediction and commentary analysis.
"""

import os
import subprocess
import sys
from pathlib import Path

def install_packages():
    """Install required packages for the project."""
    packages = [
        'pandas',
        'numpy',
        'requests',
        'matplotlib',
        'seaborn',
        'statsbombpy',
        'jupyter',
        'scikit-learn',
        'nltk',
        'transformers'  # For NLP/commentary tasks
    ]
    
    print("📦 Installing required packages...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
    
    print("\n🎉 Package installation complete!")

def create_project_structure():
    """Create the project directory structure."""
    dirs = [
        'data',
        'notebooks',
        'scripts',
        'models',
        'outputs',
        'docs'
    ]
    
    print("📁 Creating project structure...")
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✅ Created {dir_name}/ directory")
    
    # Create a basic README
    readme_content = """# Soccer Prediction & Commentary Project

This project uses StatsBomb Open Data to build:
1. Automatic soccer commentary system
2. Move quality prediction models
3. Tactical analysis tools

## Project Structure
- `data/`: Raw and processed data files
- `notebooks/`: Jupyter notebooks for exploration and analysis
- `scripts/`: Python scripts for data processing and modeling
- `models/`: Trained models and model artifacts
- `outputs/`: Generated reports, visualizations, and results
- `docs/`: Documentation and guides

## Getting Started
1. Run `python statsbomb_explorer.py` to explore the data
2. Check out the notebooks for detailed analysis
3. Use the scripts for automated data processing

## Data Sources
- StatsBomb Open Data: https://github.com/statsbomb/open-data
- Competitions: Premier League, Champions League, World Cup, Euro
"""
    
    with open('README.md', 'w') as f:
        f.write(readme_content)
    
    print("✅ Created README.md")

def create_requirements_file():
    """Create a requirements.txt file."""
    requirements = """pandas>=1.5.0
numpy>=1.20.0
requests>=2.25.0
matplotlib>=3.5.0
seaborn>=0.11.0
statsbombpy>=1.0.0
jupyter>=1.0.0
scikit-learn>=1.0.0
nltk>=3.6.0
transformers>=4.0.0
"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    
    print("✅ Created requirements.txt")

def create_sample_notebook():
    """Create a sample Jupyter notebook."""
    notebook_content = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# StatsBomb Data Exploration\n",
                    "\n",
                    "This notebook demonstrates how to explore StatsBomb Open Data for soccer analysis.\n",
                    "\n",
                    "## Objectives\n",
                    "1. Load and explore competition data\n",
                    "2. Analyze match events for commentary\n",
                    "3. Extract features for move quality prediction\n",
                    "4. Visualize tactical patterns"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "import pandas as pd\n",
                    "import numpy as np\n",
                    "import matplotlib.pyplot as plt\n",
                    "import seaborn as sns\n",
                    "import statsbombpy as sb\n",
                    "\n",
                    "# Set plotting style\n",
                    "plt.style.use('seaborn-v0_8')\n",
                    "sns.set_palette('husl')\n",
                    "\n",
                    "print(\"🚀 StatsBomb Data Analysis Environment Ready!\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 1. Explore Available Competitions"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "# Get all available competitions\n",
                    "competitions = sb.competitions()\n",
                    "print(f\"📊 Total competitions available: {len(competitions)}\")\n",
                    "\n",
                    "# Display major competitions\n",
                    "major_comps = competitions[competitions['competition_name'].isin([\n",
                    "    'FIFA World Cup', 'UEFA Euro', 'Premier League', 'La Liga'\n",
                    "])]\n",
                    "\n",
                    "display(major_comps[['competition_name', 'season_name', 'competition_id', 'season_id']])"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 2. Load Match Data\n",
                    "\n",
                    "Let's focus on Euro 2024 for our analysis."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "# Load Euro 2024 matches\n",
                    "matches = sb.matches(competition_id=55, season_id=282)\n",
                    "print(f\"⚽ Found {len(matches)} matches in Euro 2024\")\n",
                    "\n",
                    "# Display first few matches\n",
                    "display(matches[['match_date', 'home_team', 'away_team', 'home_score', 'away_score']].head())"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 3. Analyze Match Events\n",
                    "\n",
                    "Now let's dive into the event data for detailed analysis."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "# Get events for the first match\n",
                    "sample_match = matches.iloc[0]\n",
                    "events = sb.events(match_id=sample_match['match_id'])\n",
                    "\n",
                    "print(f\"🎯 Analyzing: {sample_match['home_team']} vs {sample_match['away_team']}\")\n",
                    "print(f\"📈 Total events: {len(events)}\")\n",
                    "\n",
                    "# Show event type distribution\n",
                    "event_counts = events['type'].value_counts()\n",
                    "print(\"\\nTop event types:\")\n",
                    "print(event_counts.head(10))"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 4. Your Analysis Here\n",
                    "\n",
                    "Add your own analysis cells below to explore:\n",
                    "- Commentary generation\n",
                    "- Move quality prediction\n",
                    "- Tactical analysis\n",
                    "- Player performance metrics"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.5"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    import json
    with open('notebooks/01_data_exploration.ipynb', 'w') as f:
        json.dump(notebook_content, f, indent=2)
    
    print("✅ Created sample notebook: notebooks/01_data_exploration.ipynb")

def main():
    """Main setup function."""
    print("🚀 StatsBomb Soccer Prediction & Commentary Project Setup")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("statsbomb_explorer.py").exists():
        print("⚠️  Make sure you're in the project directory with statsbomb_explorer.py")
        return
    
    # Create project structure
    create_project_structure()
    
    # Create requirements file
    create_requirements_file()
    
    # Install packages
    install_choice = input("\n📦 Do you want to install required packages now? (y/n): ").lower()
    if install_choice == 'y':
        install_packages()
    else:
        print("📝 Run 'pip install -r requirements.txt' later to install packages")
    
    # Create sample notebook
    create_sample_notebook()
    
    print("\n🎉 Project setup complete!")
    print("\n🎯 Next Steps:")
    print("1. Run: python statsbomb_explorer.py")
    print("2. Open: notebooks/01_data_exploration.ipynb")
    print("3. Start building your soccer analysis!")
    
    print("\n📚 Useful Resources:")
    print("- StatsBomb Open Data: https://github.com/statsbomb/open-data")
    print("- StatsBombPy Docs: https://github.com/statsbomb/statsbombpy")
    print("- Your project guide: StatsBomb_Data_Guide.md")

if __name__ == "__main__":
    main() 