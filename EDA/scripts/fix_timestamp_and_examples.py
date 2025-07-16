import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import ast
from datetime import datetime
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

def convert_timestamp_to_seconds(timestamp_str):
    """Convert timestamp string to total seconds"""
    try:
        if pd.isna(timestamp_str):
            return np.nan
        
        # Parse HH:MM:SS.mmm format
        time_parts = timestamp_str.split(':')
        hours = int(time_parts[0])
        minutes = int(time_parts[1])
        seconds_parts = time_parts[2].split('.')
        seconds = int(seconds_parts[0])
        milliseconds = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0
        
        total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000
        return total_seconds
    except:
        return np.nan

def analyze_timestamp_properly(df):
    """Properly analyze timestamp as a continuous variable"""
    
    print("\n🕐 ANALYZING TIMESTAMP AS CONTINUOUS VARIABLE")
    print("=" * 60)
    
    # Convert timestamp to seconds
    print("Converting timestamp strings to total seconds...")
    df['timestamp_seconds'] = df['timestamp'].apply(convert_timestamp_to_seconds)
    
    # Analyze as continuous variable
    series = df['timestamp_seconds'].dropna()
    
    if len(series) == 0:
        print("No valid timestamp data")
        return None
    
    # Basic statistics
    stats = {
        'Feature': 'timestamp',
        'Type': 'Non-Normal (Time)',
        'Count': len(series),
        'Missing': df['timestamp_seconds'].isnull().sum(),
        'Missing_Pct': (df['timestamp_seconds'].isnull().sum() / len(df)) * 100,
        'Mean': series.mean(),
        'Median': series.median(),
        'Std': series.std(),
        'Min': series.min(),
        'Max': series.max(),
        'Q25': series.quantile(0.25),
        'Q75': series.quantile(0.75)
    }
    
    # Outlier analysis
    Q1 = stats['Q25']
    Q3 = stats['Q75']
    IQR = Q3 - Q1
    lower_fence = Q1 - 1.5 * IQR
    upper_fence = Q3 + 1.5 * IQR
    
    outliers = series[(series < lower_fence) | (series > upper_fence)]
    
    stats.update({
        'IQR': IQR,
        'Lower_Fence': lower_fence,
        'Upper_Fence': upper_fence,
        'Outliers_Count': len(outliers),
        'Outliers_Pct': (len(outliers) / len(series)) * 100
    })
    
    print(f"Timestamp Statistics:")
    print(f"  Range: {stats['Min']:.2f} - {stats['Max']:.2f} seconds")
    print(f"  Mean: {stats['Mean']:.2f} seconds ({stats['Mean']/60:.1f} minutes)")
    print(f"  Outliers: {stats['Outliers_Count']} ({stats['Outliers_Pct']:.2f}%)")
    
    return stats

def create_coordinate_examples():
    """Create examples CSV showing coordinate transformations"""
    
    print("\n📋 CREATING COORDINATE EXAMPLES")
    print("=" * 50)
    
    # Sample data examples
    examples = [
        {
            'Feature': 'location',
            'Data_In': '[60.0, 40.0]',
            'Extraction_Method': 'Split array into x,y coordinates',
            'Outcome_Features': 'location_x, location_y',
            'Example_location_x': 60.0,
            'Example_location_y': 40.0,
            'Meaning': 'Pitch position: x=60 (middle field), y=40 (center width)',
            'Use_Case': 'Spatial analysis, heat maps, momentum by field position'
        },
        {
            'Feature': 'location',
            'Data_In': '[18.0, 80.0]',
            'Extraction_Method': 'Split array into x,y coordinates',
            'Outcome_Features': 'location_x, location_y',
            'Example_location_x': 18.0,
            'Example_location_y': 80.0,
            'Meaning': 'Pitch position: x=18 (defensive third), y=80 (left touchline)',
            'Use_Case': 'Defensive actions near touchline, momentum in defensive third'
        },
        {
            'Feature': 'visible_area',
            'Data_In': '[[10,0],[50,0],[60,20],[40,40],[15,30],[10,0]]',
            'Extraction_Method': 'Calculate polygon area and centroid',
            'Outcome_Features': 'area_size, centroid_x, centroid_y, polygon_complexity',
            'Example_area_size': 1250.5,
            'Example_centroid_x': 35.8,
            'Example_centroid_y': 18.3,
            'Example_polygon_complexity': 6,
            'Meaning': 'Visible field area: 1250.5 sq units, center at (35.8, 18.3), 6 vertices',
            'Use_Case': '360° data analysis, field visibility impact on momentum'
        },
        {
            'Feature': 'visible_area',
            'Data_In': '[[20,10],[80,10],[80,70],[20,70],[20,10]]',
            'Extraction_Method': 'Calculate polygon area and centroid',
            'Outcome_Features': 'area_size, centroid_x, centroid_y, polygon_complexity',
            'Example_area_size': 3600.0,
            'Example_centroid_x': 50.0,
            'Example_centroid_y': 40.0,
            'Meaning': 'Large rectangular visible area: 3600 sq units, centered at (50, 40)',
            'Use_Case': 'Full field visibility, comprehensive momentum tracking'
        },
        {
            'Feature': 'carry',
            'Data_In': '{"end_location": [45.2, 35.8]}',
            'Extraction_Method': 'Parse JSON, extract coordinates, calculate distance',
            'Outcome_Features': 'carry_end_x, carry_end_y, carry_distance, carry_direction',
            'Example_carry_end_x': 45.2,
            'Example_carry_end_y': 35.8,
            'Example_carry_distance': 12.3,
            'Example_carry_direction': 23.5,
            'Meaning': 'Player carried ball to (45.2, 35.8), distance: 12.3m, direction: 23.5°',
            'Use_Case': 'Player movement analysis, momentum through dribbling'
        },
        {
            'Feature': 'carry',
            'Data_In': '{"end_location": [78.9, 55.2]}',
            'Extraction_Method': 'Parse JSON, extract coordinates, calculate distance',
            'Outcome_Features': 'carry_end_x, carry_end_y, carry_distance, carry_direction',
            'Example_carry_end_x': 78.9,
            'Example_carry_end_y': 55.2,
            'Example_carry_distance': 8.7,
            'Example_carry_direction': -15.3,
            'Meaning': 'Player carried ball to (78.9, 55.2), distance: 8.7m, direction: -15.3°',
            'Use_Case': 'Attacking momentum, progression toward goal'
        }
    ]
    
    # Create DataFrame and save
    examples_df = pd.DataFrame(examples)
    examples_df.to_csv('EDA/coordinate_extraction_examples.csv', index=False)
    print("✅ Coordinate extraction examples saved to: EDA/coordinate_extraction_examples.csv")
    
    return examples_df

def create_individual_feature_plots(df):
    """Create separate plots for each continuous feature with stats"""
    
    print("\n📊 CREATING INDIVIDUAL FEATURE PLOTS")
    print("=" * 50)
    
    # All continuous features including timestamp
    continuous_features = ['duration', 'second', 'home_score', 'index', 'minute', 'possession', 'away_score']
    
    # Add timestamp conversion
    df['timestamp_seconds'] = df['timestamp'].apply(convert_timestamp_to_seconds)
    continuous_features.append('timestamp_seconds')
    
    for feature in continuous_features:
        if feature not in df.columns:
            continue
            
        print(f"Creating plots for: {feature}")
        
        # Get data
        if feature == 'timestamp_seconds':
            series = df[feature].dropna()
            feature_name = 'timestamp (seconds)'
        else:
            series = pd.to_numeric(df[feature], errors='coerce').dropna()
            feature_name = feature
        
        if len(series) == 0:
            continue
        
        # Calculate statistics
        stats = {
            'count': len(series),
            'mean': series.mean(),
            'std': series.std(),
            'min': series.min(),
            'max': series.max(),
            'q25': series.quantile(0.25),
            'median': series.median(),
            'q75': series.quantile(0.75)
        }
        
        # Outliers
        Q1, Q3 = stats['q25'], stats['q75']
        IQR = Q3 - Q1
        lower_fence = Q1 - 1.5 * IQR
        upper_fence = Q3 + 1.5 * IQR
        outliers = series[(series < lower_fence) | (series > upper_fence)]
        outlier_pct = (len(outliers) / len(series)) * 100
        
        # Create figure with 2 subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Histogram
        ax1.hist(series, bins=30, alpha=0.7, edgecolor='black', color='skyblue')
        ax1.set_title(f'Distribution of {feature_name}')
        ax1.set_xlabel(feature_name)
        ax1.set_ylabel('Frequency')
        ax1.grid(True, alpha=0.3)
        
        # Add statistics text
        stats_text = f"""Statistics:
Count: {stats['count']:,}
Mean: {stats['mean']:.2f}
Std: {stats['std']:.2f}
Min: {stats['min']:.2f}
Max: {stats['max']:.2f}
Q25: {stats['q25']:.2f}
Median: {stats['median']:.2f}
Q75: {stats['q75']:.2f}
Outliers: {len(outliers)} ({outlier_pct:.1f}%)"""
        
        ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                fontsize=9)
        
        # Box plot
        ax2.boxplot(series, vert=True)
        ax2.set_title(f'Box Plot of {feature_name}')
        ax2.set_ylabel(feature_name)
        ax2.grid(True, alpha=0.3)
        
        # Add outlier info
        outlier_text = f"""Outlier Analysis:
IQR: {IQR:.2f}
Lower Fence: {lower_fence:.2f}
Upper Fence: {upper_fence:.2f}
Outliers: {len(outliers)}
Outlier %: {outlier_pct:.1f}%"""
        
        ax2.text(0.02, 0.98, outlier_text, transform=ax2.transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                fontsize=9)
        
        plt.tight_layout()
        
        # Save plot
        safe_feature_name = feature.replace('_', '-')
        plt.savefig(f'EDA/plots/{safe_feature_name}_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    print("✅ Individual feature plots saved to: EDA/plots/")

def update_continuous_stats_with_timestamp(df):
    """Update continuous stats to include timestamp"""
    
    print("\n📈 UPDATING CONTINUOUS STATISTICS WITH TIMESTAMP")
    print("=" * 60)
    
    # Convert timestamp
    df['timestamp_seconds'] = df['timestamp'].apply(convert_timestamp_to_seconds)
    
    # All continuous features
    continuous_features = {
        'duration': 'Normal',
        'second': 'Normal', 
        'home_score': 'Normal',
        'index': 'Non-Normal',
        'minute': 'Non-Normal',
        'possession': 'Non-Normal',
        'away_score': 'Non-Normal',
        'timestamp_seconds': 'Non-Normal'
    }
    
    coordinate_arrays = ['location', 'visible_area', 'carry']
    
    # Analyze all features
    stats_data = []
    outliers_data = []
    
    for feature, feature_type in continuous_features.items():
        if feature not in df.columns:
            continue
            
        series = pd.to_numeric(df[feature], errors='coerce').dropna()
        
        if len(series) == 0:
            continue
        
        # Basic statistics
        stats = {
            'Feature': 'timestamp' if feature == 'timestamp_seconds' else feature,
            'Type': feature_type,
            'Count': len(series),
            'Missing': df[feature].isnull().sum(),
            'Missing_Pct': (df[feature].isnull().sum() / len(df)) * 100,
            'Mean': series.mean(),
            'Median': series.median(),
            'Std': series.std(),
            'Min': series.min(),
            'Max': series.max(),
            'Q25': series.quantile(0.25),
            'Q75': series.quantile(0.75)
        }
        
        # Outlier analysis
        Q1 = stats['Q25']
        Q3 = stats['Q75']
        IQR = Q3 - Q1
        lower_fence = Q1 - 1.5 * IQR
        upper_fence = Q3 + 1.5 * IQR
        
        outliers = series[(series < lower_fence) | (series > upper_fence)]
        
        stats.update({
            'IQR': IQR,
            'Lower_Fence': lower_fence,
            'Upper_Fence': upper_fence,
            'Outliers_Count': len(outliers),
            'Outliers_Pct': (len(outliers) / len(series)) * 100
        })
        
        stats_data.append(stats)
        
        # Add to outliers if any exist
        if len(outliers) > 0:
            outliers_data.append({
                'Feature': 'timestamp' if feature == 'timestamp_seconds' else feature,
                'Type': feature_type,
                'Total_Values': len(series),
                'Outliers_Count': len(outliers),
                'Outliers_Pct': stats['Outliers_Pct'],
                'Lower_Fence': lower_fence,
                'Upper_Fence': upper_fence,
                'Min_Outlier': outliers.min(),
                'Max_Outlier': outliers.max(),
                'Outlier_Range': f"< {lower_fence:.2f} or > {upper_fence:.2f}"
            })
    
    # Add coordinate arrays
    for feature in coordinate_arrays:
        if feature not in df.columns:
            continue
            
        non_null_count = len(df) - df[feature].isnull().sum()
        missing_count = df[feature].isnull().sum()
        missing_pct = (missing_count / len(df)) * 100
        
        if feature == 'location':
            extraction = "Extract location_x, location_y from [x,y] coordinates"
            outcome = "2 new features: location_x, location_y"
        elif feature == 'visible_area':
            extraction = "Extract area_size, centroid_x, centroid_y from polygon"
            outcome = "4 new features: area_size, centroid_x, centroid_y, polygon_complexity"
        elif feature == 'carry':
            extraction = "Parse JSON, extract end_location_x, end_location_y, calculate distance"
            outcome = "4 new features: carry_end_x, carry_end_y, carry_distance, carry_direction"
        
        stats_data.append({
            'Feature': feature,
            'Type': 'Coordinate Array',
            'Count': non_null_count,
            'Missing': missing_count,
            'Missing_Pct': missing_pct,
            'Extraction_Method': extraction,
            'Expected_Outcome': outcome,
            'Mean': 'N/A', 'Median': 'N/A', 'Std': 'N/A',
            'Min': 'N/A', 'Max': 'N/A', 'Q25': 'N/A', 'Q75': 'N/A',
            'IQR': 'N/A', 'Lower_Fence': 'N/A', 'Upper_Fence': 'N/A',
            'Outliers_Count': 'N/A', 'Outliers_Pct': 'N/A'
        })
    
    # Save updated statistics
    stats_df = pd.DataFrame(stats_data)
    stats_df.to_csv('EDA/continuous_stats_final.csv', index=False)
    print("✅ Final continuous statistics saved to: EDA/continuous_stats_final.csv")
    
    if outliers_data:
        outliers_df = pd.DataFrame(outliers_data)
        outliers_df.to_csv('EDA/outliers_final.csv', index=False)
        print("✅ Final outliers analysis saved to: EDA/outliers_final.csv")
    
    return stats_data, outliers_data

def organize_eda_folder():
    """Organize and clean up EDA folder"""
    
    print("\n🗂️ ORGANIZING EDA FOLDER")
    print("=" * 40)
    
    import os
    import shutil
    
    # Create organized subdirectories
    subdirs = ['plots', 'statistics', 'structures', 'archive']
    for subdir in subdirs:
        os.makedirs(f'EDA/{subdir}', exist_ok=True)
    
    # File organization mapping
    file_moves = {
        # Statistics files
        'statistics': [
            'continuous_stats_final.csv',
            'outliers_final.csv', 
            'categorical_stats.csv',
            'missing_values_analysis.csv',
            'coordinate_extraction_examples.csv'
        ],
        # Structure analysis files
        'structures': [
            'nominal_structure_complete.csv',
            'detailed_json_structure.csv',
            'coordinate_arrays_analysis.csv'
        ],
        # Archive old/duplicate files
        'archive': [
            'continuous_stats.csv',
            'continuous_stats_complete.csv',
            'outliers.csv',
            'outliers_complete.csv',
            'nominal_structure_analysis.csv',
            'missing_values_summary.md'
        ]
    }
    
    # Move files
    for target_dir, files in file_moves.items():
        for file in files:
            src = f'EDA/{file}'
            dst = f'EDA/{target_dir}/{file}'
            if os.path.exists(src):
                shutil.move(src, dst)
                print(f"  Moved {file} → {target_dir}/")
    
    # Move visualization files that exist
    viz_files = [
        'continuous_histograms.png',
        'continuous_boxplots.png', 
        'continuous_histograms_complete.png',
        'continuous_boxplots_complete.png',
        'categorical_distributions.png'
    ]
    
    for file in viz_files:
        src = f'EDA/{file}'
        if os.path.exists(src):
            dst = f'EDA/plots/{file}'
            shutil.move(src, dst)
            print(f"  Moved {file} → plots/")
    
    print("✅ EDA folder organized!")
    return True

def main():
    """Main function"""
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    print("🚀 FIXING TIMESTAMP AND CREATING EXAMPLES")
    print("=" * 80)
    
    # Create plots directory
    import os
    os.makedirs('EDA/plots', exist_ok=True)
    
    # 1. Fix timestamp analysis
    timestamp_stats = analyze_timestamp_properly(df)
    
    # 2. Create coordinate examples
    examples_df = create_coordinate_examples()
    
    # 3. Create individual feature plots with stats
    create_individual_feature_plots(df)
    
    # 4. Update continuous statistics with timestamp
    stats_data, outliers_data = update_continuous_stats_with_timestamp(df)
    
    # 5. Organize EDA folder
    organize_eda_folder()
    
    print("\n" + "="*80)
    print("🎉 ALL FIXES AND IMPROVEMENTS COMPLETE!")
    print("="*80)
    print("✅ Fixed timestamp analysis (converted to seconds)")
    print("✅ Created coordinate extraction examples CSV") 
    print("✅ Generated individual plots for each feature with statistics")
    print("✅ Updated all statistics files")
    print("✅ Organized EDA folder structure")
    print("\n📁 New folder structure:")
    print("  EDA/")
    print("    ├── statistics/     (all CSV statistics)")
    print("    ├── structures/     (nominal & JSON analysis)")
    print("    ├── plots/          (all visualizations)")
    print("    ├── archive/        (old/duplicate files)")
    print("    └── main files      (scripts & summary)")

if __name__ == "__main__":
    main() 