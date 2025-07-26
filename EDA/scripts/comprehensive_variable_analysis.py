import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import ast
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

def load_data():
    """Load the Euro 2024 dataset"""
    try:
        df = pd.read_csv('Data/euro_2024_complete_dataset.csv', low_memory=False)
        print(f"Dataset loaded: {df.shape[0]:,} rows × {df.shape[1]} columns")
        return df
    except FileNotFoundError:
        print("Dataset file not found!")
        return None

def analyze_continuous_variables(df):
    """Analyze continuous variables with statistics, outliers, and visualizations"""
    
    # Define continuous variables (excluding coordinate arrays)
    continuous_normal = ['duration', 'second', 'home_score']
    continuous_non_normal = ['index', 'minute', 'possession', 'away_score', 'timestamp']
    coordinate_arrays = ['location', 'visible_area', 'carry']
    
    all_continuous = continuous_normal + continuous_non_normal + coordinate_arrays
    
    print("\n" + "="*80)
    print("CONTINUOUS VARIABLES ANALYSIS")
    print("="*80)
    
    # Statistics for all continuous features
    stats_data = []
    outliers_data = []
    
    for col in all_continuous:
        if col not in df.columns:
            continue
            
        print(f"\nAnalyzing: {col}")
        
        if col in coordinate_arrays:
            # Special handling for coordinate arrays
            stats_data.append({
                'Feature': col,
                'Type': 'Coordinate Array',
                'Count': len(df) - df[col].isnull().sum(),
                'Missing': df[col].isnull().sum(),
                'Missing_Pct': (df[col].isnull().sum() / len(df)) * 100,
                'Note': 'Handled separately - coordinate extraction required',
                'Mean': 'N/A', 'Median': 'N/A', 'Std': 'N/A',
                'Min': 'N/A', 'Max': 'N/A', 'Q25': 'N/A', 'Q75': 'N/A',
                'IQR': 'N/A', 'Lower_Fence': 'N/A', 'Upper_Fence': 'N/A',
                'Outliers_Count': 'N/A', 'Outliers_Pct': 'N/A'
            })
            continue
        
        # Standard continuous analysis
        series = pd.to_numeric(df[col], errors='coerce')
        series_clean = series.dropna()
        
        if len(series_clean) == 0:
            continue
            
        # Basic statistics
        stats = {
            'Feature': col,
            'Type': 'Normal' if col in continuous_normal else 'Non-Normal',
            'Count': len(series_clean),
            'Missing': series.isnull().sum(),
            'Missing_Pct': (series.isnull().sum() / len(series)) * 100,
            'Mean': series_clean.mean(),
            'Median': series_clean.median(),
            'Std': series_clean.std(),
            'Min': series_clean.min(),
            'Max': series_clean.max(),
            'Q25': series_clean.quantile(0.25),
            'Q75': series_clean.quantile(0.75)
        }
        
        # Outlier analysis using 1.5×IQR rule
        Q1 = stats['Q25']
        Q3 = stats['Q75']
        IQR = Q3 - Q1
        lower_fence = Q1 - 1.5 * IQR
        upper_fence = Q3 + 1.5 * IQR
        
        outliers = series_clean[(series_clean < lower_fence) | (series_clean > upper_fence)]
        
        stats.update({
            'IQR': IQR,
            'Lower_Fence': lower_fence,
            'Upper_Fence': upper_fence,
            'Outliers_Count': len(outliers),
            'Outliers_Pct': (len(outliers) / len(series_clean)) * 100 if len(series_clean) > 0 else 0,
            'Note': 'Standard analysis'
        })
        
        stats_data.append(stats)
        
        # Add to outliers data if outliers exist
        if len(outliers) > 0:
            outliers_data.append({
                'Feature': col,
                'Type': stats['Type'],
                'Total_Values': len(series_clean),
                'Outliers_Count': len(outliers),
                'Outliers_Pct': stats['Outliers_Pct'],
                'Lower_Fence': lower_fence,
                'Upper_Fence': upper_fence,
                'Min_Outlier': outliers.min(),
                'Max_Outlier': outliers.max(),
                'Outlier_Range': f"< {lower_fence:.2f} or > {upper_fence:.2f}"
            })
    
    # Save statistics
    stats_df = pd.DataFrame(stats_data)
    stats_df.to_csv('EDA/continuous_stats.csv', index=False)
    print(f"\nContinuous statistics saved to: EDA/continuous_stats.csv")
    
    # Save outliers (only if any exist)
    if outliers_data:
        outliers_df = pd.DataFrame(outliers_data)
        outliers_df.to_csv('EDA/outliers.csv', index=False)
        print(f"Outliers analysis saved to: EDA/outliers.csv")
    else:
        print("No outliers detected in any continuous variables")
    
    return stats_data, outliers_data

def create_continuous_visualizations(df):
    """Create histograms and box plots for continuous variables"""
    
    continuous_vars = ['duration', 'second', 'home_score', 'index', 'minute', 'possession', 'away_score', 'timestamp']
    available_vars = [col for col in continuous_vars if col in df.columns]
    
    if not available_vars:
        print("No continuous variables available for visualization")
        return
    
    # Create histograms
    n_vars = len(available_vars)
    n_cols = 3
    n_rows = (n_vars + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    
    for i, col in enumerate(available_vars):
        row, col_idx = i // n_cols, i % n_cols
        series = pd.to_numeric(df[col], errors='coerce').dropna()
        
        if len(series) > 0:
            axes[row, col_idx].hist(series, bins=30, alpha=0.7, edgecolor='black')
            axes[row, col_idx].set_title(f'Distribution of {col}')
            axes[row, col_idx].set_xlabel(col)
            axes[row, col_idx].set_ylabel('Frequency')
            axes[row, col_idx].grid(True, alpha=0.3)
    
    # Remove empty subplots
    for i in range(len(available_vars), n_rows * n_cols):
        row, col_idx = i // n_cols, i % n_cols
        axes[row, col_idx].remove()
    
    plt.tight_layout()
    plt.savefig('EDA/continuous_histograms.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create box plots
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    
    for i, col in enumerate(available_vars):
        row, col_idx = i // n_cols, i % n_cols
        series = pd.to_numeric(df[col], errors='coerce').dropna()
        
        if len(series) > 0:
            axes[row, col_idx].boxplot(series)
            axes[row, col_idx].set_title(f'Box Plot of {col}')
            axes[row, col_idx].set_ylabel(col)
            axes[row, col_idx].grid(True, alpha=0.3)
    
    # Remove empty subplots
    for i in range(len(available_vars), n_rows * n_cols):
        row, col_idx = i // n_cols, i % n_cols
        axes[row, col_idx].remove()
    
    plt.tight_layout()
    plt.savefig('EDA/continuous_boxplots.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Continuous visualizations saved: continuous_histograms.png, continuous_boxplots.png")

def analyze_coordinate_arrays(df):
    """Special analysis for coordinate array features"""
    
    print("\n" + "="*60)
    print("COORDINATE ARRAYS SPECIAL ANALYSIS")
    print("="*60)
    
    coordinate_features = ['location', 'visible_area', 'carry']
    explanations = []
    
    for feature in coordinate_features:
        if feature not in df.columns:
            continue
            
        print(f"\n--- {feature.upper()} ---")
        
        # Get non-null values
        non_null = df[feature].dropna()
        print(f"Non-null values: {len(non_null):,}")
        print(f"Missing values: {df[feature].isnull().sum():,}")
        
        if len(non_null) == 0:
            continue
        
        # Sample some values to understand structure
        print(f"Sample values:")
        for i, val in enumerate(non_null.head(3)):
            print(f"  {i+1}: {str(val)[:100]}...")
        
        if feature == 'location':
            explanation = """
            LOCATION ANALYSIS:
            - Structure: [x, y] coordinates
            - Pitch dimensions: x (0-120), y (0-80)
            - Represents event location on football pitch
            - Extraction: Split into location_x, location_y features
            - Missing: Events without specific location (0.89%)
            """
            
        elif feature == 'visible_area':
            explanation = """
            VISIBLE_AREA ANALYSIS:
            - Structure: Array of [x, y] coordinate pairs
            - Represents visible area polygon on pitch
            - Contains multiple coordinate points defining area
            - Extraction: Could extract area size, centroid, shape features
            - Missing: Events without 360° data (12.95%)
            """
            
        elif feature == 'carry':
            explanation = """
            CARRY ANALYSIS:
            - Structure: JSON object with end_location coordinates
            - Contains carry distance, direction, end position
            - Extraction: Parse JSON, extract end_location [x, y]
            - Additional: Could extract carry_distance, carry_angle
            - Missing: Non-carry events (76.5%)
            """
        
        explanations.append({
            'Feature': feature,
            'Non_Null_Count': len(non_null),
            'Missing_Count': df[feature].isnull().sum(),
            'Missing_Pct': (df[feature].isnull().sum() / len(df)) * 100,
            'Explanation': explanation.strip(),
            'Extraction_Strategy': f"Parse and extract coordinate components for {feature}"
        })
        
        print(explanation)
    
    # Save coordinate analysis
    coord_df = pd.DataFrame(explanations)
    coord_df.to_csv('EDA/coordinate_arrays_analysis.csv', index=False)
    print(f"\nCoordinate arrays analysis saved to: EDA/coordinate_arrays_analysis.csv")
    
    return explanations

def analyze_categorical_variables(df):
    """Analyze binomial and ordinal categorical variables"""
    
    # Define categorical variables (excluding high-missing ones)
    binomial_vars = ['under_pressure', 'counterpress', 'off_camera', 'injury_stoppage', 'out']
    ordinal_vars = ['period', 'match_week', 'stage', 'match_date', 'kick_off']
    
    print("\n" + "="*80)
    print("CATEGORICAL VARIABLES ANALYSIS (BINOMIAL + ORDINAL)")
    print("="*80)
    
    categorical_stats = []
    
    for var_list, var_type in [(binomial_vars, 'Binomial'), (ordinal_vars, 'Ordinal')]:
        for col in var_list:
            if col not in df.columns:
                continue
                
            print(f"\n--- {col.upper()} ({var_type}) ---")
            
            # Basic counts
            series = df[col]
            missing_count = series.isnull().sum()
            missing_pct = (missing_count / len(series)) * 100
            non_null_series = series.dropna()
            
            print(f"Total values: {len(series):,}")
            print(f"Missing: {missing_count:,} ({missing_pct:.2f}%)")
            print(f"Non-null: {len(non_null_series):,}")
            
            if len(non_null_series) == 0:
                continue
            
            # Value counts
            value_counts = non_null_series.value_counts()
            total_categories = len(value_counts)
            
            print(f"Total categories: {total_categories}")
            print(f"Top 7 categories:")
            
            top_7 = value_counts.head(7)
            for val, count in top_7.items():
                pct = (count / len(non_null_series)) * 100
                print(f"  {val}: {count:,} ({pct:.2f}%)")
            
            # Store statistics
            categorical_stats.append({
                'Feature': col,
                'Type': var_type,
                'Total_Values': len(series),
                'Missing_Count': missing_count,
                'Missing_Pct': missing_pct,
                'Non_Null_Count': len(non_null_series),
                'Total_Categories': total_categories,
                'Top_Category': top_7.index[0] if len(top_7) > 0 else None,
                'Top_Category_Count': top_7.iloc[0] if len(top_7) > 0 else None,
                'Top_Category_Pct': (top_7.iloc[0] / len(non_null_series)) * 100 if len(top_7) > 0 else None,
                'Top_7_Categories': dict(top_7),
                'Distribution': dict(value_counts)
            })
    
    # Save categorical statistics
    # Convert complex dict columns to strings for CSV
    categorical_df = pd.DataFrame(categorical_stats)
    categorical_df['Top_7_Categories'] = categorical_df['Top_7_Categories'].astype(str)
    categorical_df['Distribution'] = categorical_df['Distribution'].astype(str)
    
    categorical_df.to_csv('EDA/categorical_stats.csv', index=False)
    print(f"\nCategorical statistics saved to: EDA/categorical_stats.csv")
    
    return categorical_stats

def create_categorical_visualizations(df):
    """Create bar charts and pie charts for categorical variables"""
    
    categorical_vars = ['under_pressure', 'counterpress', 'off_camera', 'injury_stoppage', 'out',
                       'period', 'match_week', 'stage', 'match_date', 'kick_off']
    available_vars = [col for col in categorical_vars if col in df.columns]
    
    if not available_vars:
        print("No categorical variables available for visualization")
        return
    
    # Create bar charts
    n_vars = len(available_vars)
    n_cols = 3
    n_rows = (n_vars + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 6*n_rows))
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    
    for i, col in enumerate(available_vars):
        row, col_idx = i // n_cols, i % n_cols
        series = df[col].dropna()
        
        if len(series) > 0:
            value_counts = series.value_counts().head(7)
            
            axes[row, col_idx].bar(range(len(value_counts)), value_counts.values)
            axes[row, col_idx].set_title(f'Distribution of {col}')
            axes[row, col_idx].set_xlabel('Categories')
            axes[row, col_idx].set_ylabel('Count')
            axes[row, col_idx].set_xticks(range(len(value_counts)))
            axes[row, col_idx].set_xticklabels([str(x) for x in value_counts.index], rotation=45, ha='right')
            axes[row, col_idx].grid(True, alpha=0.3)
    
    # Remove empty subplots
    for i in range(len(available_vars), n_rows * n_cols):
        row, col_idx = i // n_cols, i % n_cols
        axes[row, col_idx].remove()
    
    plt.tight_layout()
    plt.savefig('EDA/categorical_distributions.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Categorical visualizations saved: categorical_distributions.png")

def main():
    """Main analysis function"""
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Create EDA directory if it doesn't exist
    import os
    os.makedirs('EDA', exist_ok=True)
    
    print("Starting comprehensive variable analysis...")
    
    # 1. Continuous variables analysis
    continuous_stats, outliers_data = analyze_continuous_variables(df)
    create_continuous_visualizations(df)
    
    # 2. Coordinate arrays special analysis
    coordinate_analysis = analyze_coordinate_arrays(df)
    
    # 3. Categorical variables analysis
    categorical_stats = analyze_categorical_variables(df)
    create_categorical_visualizations(df)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print("Files generated:")
    print("- EDA/continuous_stats.csv")
    print("- EDA/outliers.csv (if outliers found)")
    print("- EDA/coordinate_arrays_analysis.csv")
    print("- EDA/categorical_stats.csv")
    print("- EDA/continuous_histograms.png")
    print("- EDA/continuous_boxplots.png") 
    print("- EDA/categorical_distributions.png")

if __name__ == "__main__":
    main() 