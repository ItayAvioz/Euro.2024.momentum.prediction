#!/usr/bin/env python3
"""
Comprehensive Analysis of Nominal Features in Euro 2024 Dataset
Excludes features with ~100% missing values, focuses on meaningful nominal variables
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def load_euro_2024_data():
    """Load the main Euro 2024 dataset"""
    data_path = Path("Data/euro_2024_complete_dataset.csv")
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found at {data_path}")
    
    print("Loading Euro 2024 dataset...")
    df = pd.read_csv(data_path)
    print(f"Dataset loaded: {df.shape[0]:,} rows × {df.shape[1]} columns")
    return df

def identify_nominal_features(df):
    """
    Identify nominal features with reasonable data coverage
    Exclude those with ~100% missing values based on documentation
    """
    # Primary nominal features from documentation with good coverage
    nominal_features = [
        'type',              # Event type classifications (~35 types)
        'event_type',        # Simplified event types (~35 types)
        'possession_team',   # Team in possession (24 teams)
        'team',              # Team performing event (24 teams)
        'home_team_name',    # Home team identifiers (24 teams)
        'away_team_name',    # Away team identifiers (24 teams)
        'home_team_id',      # Home team ID numbers (24 IDs)
        'away_team_id',      # Away team ID numbers (24 IDs)
        'play_pattern',      # How play started (9 patterns)
        'position',          # Player positions (~25 positions)
        'match_id',          # Match identifiers (51 matches)
        'stadium',           # Venues (10 stadiums)
        'referee'            # Match officials (~20 referees)
    ]
    
    # Check which features exist in the dataset
    available_features = [col for col in nominal_features if col in df.columns]
    missing_features = [col for col in nominal_features if col not in df.columns]
    
    if missing_features:
        print(f"Warning: These nominal features are not in the dataset: {missing_features}")
    
    print(f"Analyzing {len(available_features)} nominal features with good coverage...")
    return available_features

def analyze_nominal_feature(df, feature):
    """Analyze a single nominal feature"""
    total_rows = len(df)
    
    # Handle different types of missing values
    missing_mask = df[feature].isna() | (df[feature] == '') | (df[feature] == 'nan')
    missing_count = missing_mask.sum()
    missing_percentage = (missing_count / total_rows) * 100
    valid_count = total_rows - missing_count
    
    # Get value counts for non-missing values
    valid_data = df[feature][~missing_mask]
    value_counts = valid_data.value_counts()
    unique_count = len(value_counts)
    
    # Get top 7 categories
    top_categories = value_counts.head(7)
    
    analysis = {
        'feature': feature,
        'total_rows': total_rows,
        'missing_count': missing_count,
        'missing_percentage': missing_percentage,
        'valid_count': valid_count,
        'unique_count': unique_count,
        'top_categories': top_categories,
        'value_counts': value_counts
    }
    
    return analysis

def create_nominal_visualization(analysis, output_dir):
    """Create visualization for a nominal feature"""
    feature = analysis['feature']
    top_categories = analysis['top_categories']
    missing_count = analysis['missing_count']
    missing_percentage = analysis['missing_percentage']
    unique_count = analysis['unique_count']
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Left plot: Top 7 categories
    colors = plt.cm.Set3(np.linspace(0, 1, len(top_categories)))
    bars = ax1.bar(range(len(top_categories)), top_categories.values, color=colors)
    ax1.set_xlabel('Categories')
    ax1.set_ylabel('Count')
    ax1.set_title(f'Top 7 Categories - {feature}\n(Total: {unique_count} unique categories)')
    ax1.set_xticks(range(len(top_categories)))
    ax1.set_xticklabels([str(cat)[:20] for cat in top_categories.index], rotation=45, ha='right')
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        percentage = (height / analysis['valid_count']) * 100
        ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{int(height):,}\n({percentage:.1f}%)',
                ha='center', va='bottom', fontsize=9)
    
    # Right plot: Missing vs Valid pie chart
    missing_data = [analysis['valid_count'], missing_count]
    labels = [f'Valid Data\n({analysis["valid_count"]:,})', 
              f'Missing\n({missing_count:,})']
    colors_pie = ['lightblue', 'lightcoral']
    
    wedges, texts, autotexts = ax2.pie(missing_data, labels=labels, colors=colors_pie, 
                                       autopct='%1.1f%%', startangle=90)
    ax2.set_title(f'Data Coverage - {feature}\n(Missing: {missing_percentage:.1f}%)')
    
    plt.tight_layout()
    
    # Save the plot
    output_path = output_dir / f'nominal_{feature.lower()}_analysis.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Created visualization: {output_path}")

def create_summary_csv(analyses, output_dir):
    """Create CSV summary of nominal features analysis"""
    summary_data = []
    
    for analysis in analyses:
        # Get top 3 categories for summary
        top_3 = list(analysis['top_categories'].head(3).index)
        top_3_counts = list(analysis['top_categories'].head(3).values)
        top_3_str = ', '.join([f"{cat}({count:,})" for cat, count in zip(top_3, top_3_counts)])
        
        summary_data.append({
            'Feature': analysis['feature'],
            'Total_Rows': analysis['total_rows'],
            'Valid_Count': analysis['valid_count'],
            'Missing_Count': analysis['missing_count'],
            'Missing_Percentage': round(analysis['missing_percentage'], 2),
            'Unique_Categories': analysis['unique_count'],
            'Top_3_Categories': top_3_str,
            'Most_Common_Category': analysis['top_categories'].index[0] if len(analysis['top_categories']) > 0 else 'N/A',
            'Most_Common_Count': analysis['top_categories'].iloc[0] if len(analysis['top_categories']) > 0 else 0,
            'Most_Common_Percentage': round((analysis['top_categories'].iloc[0] / analysis['valid_count']) * 100, 2) if len(analysis['top_categories']) > 0 and analysis['valid_count'] > 0 else 0
        })
    
    summary_df = pd.DataFrame(summary_data)
    
    # Sort by missing percentage (ascending) to show best coverage first
    summary_df = summary_df.sort_values('Missing_Percentage')
    
    # Save CSV
    csv_path = output_dir / 'nominal_features_summary.csv'
    summary_df.to_csv(csv_path, index=False)
    
    print(f"\nNominal Features Summary saved to: {csv_path}")
    print("\nTop 5 nominal features by data coverage:")
    print(summary_df[['Feature', 'Missing_Percentage', 'Unique_Categories', 'Most_Common_Category']].head())
    
    return summary_df

def main():
    """Main analysis function"""
    print("=" * 80)
    print("EURO 2024 NOMINAL FEATURES ANALYSIS")
    print("=" * 80)
    
    # Create output directory
    output_dir = Path("EDA/visualizations/nominal_features")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Load data
        df = load_euro_2024_data()
        
        # Identify nominal features
        nominal_features = identify_nominal_features(df)
        
        if not nominal_features:
            print("No nominal features found to analyze!")
            return
        
        # Analyze each nominal feature
        analyses = []
        print(f"\nAnalyzing {len(nominal_features)} nominal features...")
        
        for feature in nominal_features:
            print(f"Processing: {feature}")
            analysis = analyze_nominal_feature(df, feature)
            analyses.append(analysis)
            
            # Skip visualization if too many missing values
            if analysis['missing_percentage'] < 95:  # Only visualize if less than 95% missing
                create_nominal_visualization(analysis, output_dir)
            else:
                print(f"  Skipping visualization for {feature} (too many missing values: {analysis['missing_percentage']:.1f}%)")
        
        # Create summary CSV
        summary_df = create_summary_csv(analyses, output_dir)
        
        print(f"\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"✅ Analyzed {len(nominal_features)} nominal features")
        print(f"📊 Created visualizations in: {output_dir}")
        print(f"📋 Summary CSV: {output_dir}/nominal_features_summary.csv")
        
        # Print feature coverage summary
        good_coverage = sum(1 for a in analyses if a['missing_percentage'] < 20)
        medium_coverage = sum(1 for a in analyses if 20 <= a['missing_percentage'] < 50)
        poor_coverage = sum(1 for a in analyses if a['missing_percentage'] >= 50)
        
        print(f"\nData Coverage Summary:")
        print(f"  🟢 Good coverage (<20% missing): {good_coverage} features")
        print(f"  🟡 Medium coverage (20-50% missing): {medium_coverage} features")
        print(f"  🔴 Poor coverage (≥50% missing): {poor_coverage} features")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        raise

if __name__ == "__main__":
    main() 