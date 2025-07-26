"""
Update Coordinate Examples with Real Data and Create Categorical Feature Plots
============================================================================

This script:
1. Updates coordinate_extraction_examples.csv with real dataset values
2. Creates separate bar charts and pie charts for each ordinal and binomial feature
3. Generates comprehensive statistics for each categorical feature
4. Saves all plots and updated CSV files

Dataset: euro_2024_complete_dataset.csv (187,858 rows × 59 columns)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import ast
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style for better plots
plt.style.use('default')
sns.set_palette("husl")

def safe_parse_json(x):
    """Safely parse JSON strings"""
    if pd.isna(x) or x == '':
        return None
    try:
        if isinstance(x, str):
            return json.loads(x.replace("'", '"'))
        return x
    except:
        try:
            return ast.literal_eval(str(x))
        except:
            return None

def safe_parse_list(x):
    """Safely parse list strings"""
    if pd.isna(x) or x == '':
        return None
    try:
        if isinstance(x, str):
            return ast.literal_eval(x)
        return x
    except:
        return None

def calculate_distance(start, end):
    """Calculate Euclidean distance between two points"""
    if start is None or end is None:
        return None
    try:
        return np.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
    except:
        return None

def calculate_direction(start, end):
    """Calculate direction angle in degrees"""
    if start is None or end is None:
        return None
    try:
        return np.degrees(np.arctan2(end[1] - start[1], end[0] - start[0]))
    except:
        return None

def extract_real_coordinate_examples(df):
    """Extract real coordinate examples from the dataset"""
    
    print("🔍 Extracting real coordinate examples...")
    
    examples = []
    
    # Get real location examples
    location_data = df['location'].dropna().head(1000)
    location_parsed = [safe_parse_list(x) for x in location_data if safe_parse_list(x) is not None]
    location_valid = [x for x in location_parsed if x and len(x) == 2]
    
    if location_valid:
        # Sample various location examples
        sample_locations = np.random.choice(len(location_valid), min(5, len(location_valid)), replace=False)
        for i in sample_locations:
            loc = location_valid[i]
            examples.append({
                'feature': 'location',
                'original_value': str(loc),
                'extracted_features': f'location_x: {loc[0]}, location_y: {loc[1]}',
                'meaning': f'Pitch coordinates - X: {loc[0]} (0-120m field width), Y: {loc[1]} (0-80m field height)',
                'momentum_relevance': 'Position on field indicates attack/defense zones, proximity to goal'
            })
    
    # Get real carry examples  
    carry_data = df['carry'].dropna().head(1000)
    carry_parsed = [safe_parse_json(x) for x in carry_data if safe_parse_json(x) is not None]
    carry_valid = [x for x in carry_parsed if x and 'end_location' in x and x['end_location']]
    
    if carry_valid:
        sample_carries = np.random.choice(len(carry_valid), min(5, len(carry_valid)), replace=False)
        for i in sample_carries:
            carry = carry_valid[i]
            end_loc = carry['end_location']
            # Get corresponding start location if available
            carry_row_idx = df[df['carry'].notna()].index[i] if i < len(df[df['carry'].notna()]) else None
            start_loc = None
            if carry_row_idx is not None:
                start_loc_str = df.loc[carry_row_idx, 'location']
                start_loc = safe_parse_list(start_loc_str)
            
            distance = calculate_distance(start_loc, end_loc) if start_loc else None
            direction = calculate_direction(start_loc, end_loc) if start_loc else None
            
            extracted = f'carry_end_x: {end_loc[0]}, carry_end_y: {end_loc[1]}'
            if distance:
                extracted += f', carry_distance: {distance:.1f}m'
            if direction:
                extracted += f', carry_direction: {direction:.1f}°'
                
            examples.append({
                'feature': 'carry',
                'original_value': str(carry),
                'extracted_features': extracted,
                'meaning': f'Ball carry ending at ({end_loc[0]}, {end_loc[1]}) - ' + 
                          ('forward carry (attacking)' if direction and -90 < direction < 90 else 'backward/sideways carry'),
                'momentum_relevance': 'Forward carries = positive momentum, backward = defensive pressure, distance = momentum magnitude'
            })
    
    # Get real visible_area examples
    visible_area_data = df['visible_area'].dropna().head(1000)
    visible_area_parsed = [safe_parse_list(x) for x in visible_area_data if safe_parse_list(x) is not None]
    visible_area_valid = [x for x in visible_area_parsed if x and len(x) > 0]
    
    if visible_area_valid:
        sample_areas = np.random.choice(len(visible_area_valid), min(3, len(visible_area_valid)), replace=False)
        for i in sample_areas:
            area = visible_area_valid[i]
            area_size = len(area)
            
            # Calculate centroid if polygon has enough points
            centroid_x = centroid_y = None
            if area_size >= 3:
                try:
                    x_coords = [point[0] for point in area if len(point) >= 2]
                    y_coords = [point[1] for point in area if len(point) >= 2]
                    centroid_x = np.mean(x_coords)
                    centroid_y = np.mean(y_coords)
                except:
                    pass
            
            extracted = f'area_size: {area_size} points'
            if centroid_x is not None:
                extracted += f', centroid_x: {centroid_x:.1f}, centroid_y: {centroid_y:.1f}'
                
            examples.append({
                'feature': 'visible_area',
                'original_value': str(area)[:100] + '...' if len(str(area)) > 100 else str(area),
                'extracted_features': extracted,
                'meaning': f'360° tracking polygon with {area_size} boundary points' + 
                          (f', centered at ({centroid_x:.1f}, {centroid_y:.1f})' if centroid_x else ''),
                'momentum_relevance': 'Larger visible areas = better field control, centroids indicate pressure zones'
            })
    
    return pd.DataFrame(examples)

def create_categorical_plots(df, feature, feature_type, output_dir):
    """Create bar chart and pie chart for a categorical feature"""
    
    print(f"📊 Creating plots for {feature} ({feature_type})")
    
    # Get value counts
    value_counts = df[feature].value_counts(dropna=False)
    total_count = len(df)
    
    # Calculate statistics
    unique_values = df[feature].nunique(dropna=False)
    missing_count = df[feature].isna().sum()
    missing_pct = (missing_count / total_count) * 100
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Bar Chart
    bars = ax1.bar(range(len(value_counts)), value_counts.values, 
                   color=plt.cm.Set3(np.linspace(0, 1, len(value_counts))))
    ax1.set_title(f'{feature.title()} - Bar Chart\n({feature_type.title()})', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Categories', fontsize=12)
    ax1.set_ylabel('Frequency', fontsize=12)
    
    # Rotate x-axis labels if too many categories
    if len(value_counts) > 10:
        ax1.set_xticks(range(min(10, len(value_counts))))
        ax1.set_xticklabels([str(x)[:15] + '...' if len(str(x)) > 15 else str(x) 
                            for x in value_counts.index[:10]], rotation=45, ha='right')
        if len(value_counts) > 10:
            ax1.text(0.5, 0.95, f'Showing top 10 of {len(value_counts)} categories', 
                    transform=ax1.transAxes, ha='center', va='top', fontsize=10)
    else:
        ax1.set_xticks(range(len(value_counts)))
        ax1.set_xticklabels([str(x)[:20] + '...' if len(str(x)) > 20 else str(x) 
                            for x in value_counts.index], rotation=45, ha='right')
    
    # Add value labels on bars
    for i, (bar, value) in enumerate(zip(bars, value_counts.values)):
        if i < 10:  # Only label first 10 bars
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(value_counts.values)*0.01,
                    f'{value:,}', ha='center', va='bottom', fontsize=9)
    
    ax1.grid(axis='y', alpha=0.3)
    
    # Pie Chart (top categories only for readability)
    top_categories = value_counts.head(8)
    if len(value_counts) > 8:
        other_sum = value_counts.iloc[8:].sum()
        top_categories = pd.concat([top_categories, pd.Series([other_sum], index=['Others'])])
    
    colors = plt.cm.Set3(np.linspace(0, 1, len(top_categories)))
    wedges, texts, autotexts = ax2.pie(top_categories.values, labels=None, autopct='%1.1f%%',
                                      colors=colors, startangle=90)
    
    ax2.set_title(f'{feature.title()} - Pie Chart\n({feature_type.title()})', fontsize=14, fontweight='bold')
    
    # Create legend with category names and counts
    legend_labels = [f'{cat}: {count:,}' for cat, count in top_categories.items()]
    ax2.legend(wedges, legend_labels, title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    
    # Add statistics text
    stats_text = f"""
    Statistics:
    Total Values: {total_count:,}
    Unique Values: {unique_values:,}
    Missing Values: {missing_count:,} ({missing_pct:.1f}%)
    Most Frequent: {value_counts.index[0]} ({value_counts.iloc[0]:,})
    """
    
    fig.text(0.02, 0.02, stats_text, fontsize=10, verticalalignment='bottom',
             bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    
    # Save plot
    plot_file = output_dir / f"{feature}_{feature_type}_chart.png"
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    # Return statistics
    return {
        'feature': feature,
        'type': feature_type,
        'total_values': total_count,
        'unique_values': unique_values,
        'missing_count': missing_count,
        'missing_percentage': missing_pct,
        'most_frequent_value': str(value_counts.index[0]),
        'most_frequent_count': int(value_counts.iloc[0]),
        'top_5_values': ', '.join([f"{val}({cnt})" for val, cnt in value_counts.head(5).items()])
    }

def main():
    """Main execution function"""
    
    print("🚀 Starting coordinate update and categorical plotting...")
    print("=" * 60)
    
    # Load dataset
    print("📂 Loading Euro 2024 dataset...")
    df = pd.read_csv('../Data/euro_2024_complete_dataset.csv', low_memory=False)
    print(f"   Dataset shape: {df.shape}")
    
    # Create output directories
    statistics_dir = Path('statistics')
    plots_dir = Path('plots')
    statistics_dir.mkdir(exist_ok=True)
    plots_dir.mkdir(exist_ok=True)
    
    # 1. Update coordinate examples with real data
    print("\n" + "="*50)
    print("1. UPDATING COORDINATE EXAMPLES WITH REAL DATA")
    print("="*50)
    
    real_examples = extract_real_coordinate_examples(df)
    
    # Save updated coordinate examples
    coord_file = statistics_dir / 'coordinate_extraction_examples.csv'
    real_examples.to_csv(coord_file, index=False)
    print(f"✅ Updated coordinate examples saved: {coord_file}")
    print(f"   Real examples extracted: {len(real_examples)}")
    
    # 2. Create categorical feature plots
    print("\n" + "="*50)
    print("2. CREATING CATEGORICAL FEATURE PLOTS")
    print("="*50)
    
    # Define ordinal and binomial features based on final classification
    ordinal_features = ['period', 'match_week', 'minute', 'second', 'timestamp_seconds']
    binomial_features = ['under_pressure', 'off_camera', 'counterpress', 'out', 'injury_stoppage']
    
    categorical_stats = []
    
    # Create plots for ordinal features
    print("\n📊 Creating ordinal feature plots...")
    for feature in ordinal_features:
        if feature in df.columns:
            stats = create_categorical_plots(df, feature, 'ordinal', plots_dir)
            categorical_stats.append(stats)
        else:
            print(f"   ⚠️  Feature '{feature}' not found in dataset")
    
    # Create plots for binomial features  
    print("\n📊 Creating binomial feature plots...")
    for feature in binomial_features:
        if feature in df.columns:
            stats = create_categorical_plots(df, feature, 'binomial', plots_dir)
            categorical_stats.append(stats)
        else:
            print(f"   ⚠️  Feature '{feature}' not found in dataset")
    
    # Save categorical statistics
    if categorical_stats:
        categorical_stats_df = pd.DataFrame(categorical_stats)
        stats_file = statistics_dir / 'categorical_feature_statistics.csv'
        categorical_stats_df.to_csv(stats_file, index=False)
        print(f"\n✅ Categorical statistics saved: {stats_file}")
    
    # Summary
    print("\n" + "="*60)
    print("📋 SUMMARY")
    print("="*60)
    print(f"✅ Updated coordinate examples: {len(real_examples)} real examples")
    print(f"✅ Created plots for: {len(categorical_stats)} categorical features")
    print(f"   📁 Ordinal features: {len([f for f in ordinal_features if f in df.columns])}")
    print(f"   📁 Binomial features: {len([f for f in binomial_features if f in df.columns])}")
    print(f"📂 Files saved in:")
    print(f"   📊 Plots: {plots_dir}/")
    print(f"   📈 Statistics: {statistics_dir}/")
    
    print("\n🎯 All coordinate examples updated with real data and categorical plots created!")

if __name__ == "__main__":
    main() 