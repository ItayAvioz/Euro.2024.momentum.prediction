#!/usr/bin/env python3
"""
Analysis of Complex Nominal Features in Euro 2024 Dataset
Focuses on features with JSON structures, arrays, and complex data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import ast
import json
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

def safe_eval_json(value):
    """Safely evaluate JSON-like strings"""
    if pd.isna(value) or value == '' or value == 'nan':
        return None
    try:
        if isinstance(value, str):
            return ast.literal_eval(value)
        return value
    except:
        return None

def analyze_related_events(df):
    """Analyze related_events feature - count of related events per event"""
    print("Analyzing related_events...")
    
    total_rows = len(df)
    missing_mask = df['related_events'].isna() | (df['related_events'] == '') | (df['related_events'] == 'nan')
    missing_count = missing_mask.sum()
    missing_percentage = (missing_count / total_rows) * 100
    valid_count = total_rows - missing_count
    
    # Count related events per row
    related_counts = []
    for value in df['related_events']:
        if pd.isna(value) or value == '' or value == 'nan':
            related_counts.append(0)
        else:
            try:
                parsed = safe_eval_json(value)
                if parsed is None:
                    related_counts.append(0)
                elif isinstance(parsed, list):
                    related_counts.append(len(parsed))
                else:
                    related_counts.append(1)
            except:
                related_counts.append(0)
    
    related_counts_series = pd.Series(related_counts)
    value_counts = related_counts_series.value_counts().sort_index()
    
    # Get top 7 categories
    top_categories = value_counts.head(7)
    unique_count = len(value_counts)
    
    analysis = {
        'feature': 'related_events_count',
        'total_rows': total_rows,
        'missing_count': missing_count,
        'missing_percentage': missing_percentage,
        'valid_count': valid_count,
        'unique_count': unique_count,
        'top_categories': top_categories,
        'value_counts': value_counts,
        'description': 'Number of related events per event'
    }
    
    return analysis

def analyze_player_feature(df):
    """Analyze player feature - extract player names/IDs"""
    print("Analyzing player...")
    
    total_rows = len(df)
    missing_mask = df['player'].isna() | (df['player'] == '') | (df['player'] == 'nan')
    missing_count = missing_mask.sum()
    missing_percentage = (missing_count / total_rows) * 100
    valid_count = total_rows - missing_count
    
    # Extract player names
    player_names = []
    for value in df['player']:
        if pd.isna(value) or value == '' or value == 'nan':
            player_names.append('No Player')
        else:
            try:
                parsed = safe_eval_json(value)
                if parsed and isinstance(parsed, dict) and 'name' in parsed:
                    player_names.append(parsed['name'])
                else:
                    player_names.append('Unknown Player')
            except:
                player_names.append('Unknown Player')
    
    player_series = pd.Series(player_names)
    value_counts = player_series.value_counts()
    
    # Get top 7 categories
    top_categories = value_counts.head(7)
    unique_count = len(value_counts)
    
    analysis = {
        'feature': 'player',
        'total_rows': total_rows,
        'missing_count': missing_count,
        'missing_percentage': missing_percentage,
        'valid_count': valid_count,
        'unique_count': unique_count,
        'top_categories': top_categories,
        'value_counts': value_counts,
        'description': 'Player names extracted from JSON objects'
    }
    
    return analysis

def analyze_pass_feature(df):
    """Analyze pass feature - presence and types"""
    print("Analyzing pass...")
    
    total_rows = len(df)
    missing_mask = df['pass'].isna() | (df['pass'] == '') | (df['pass'] == 'nan')
    missing_count = missing_mask.sum()
    missing_percentage = (missing_count / total_rows) * 100
    valid_count = total_rows - missing_count
    
    # Classify pass events
    pass_types = []
    for value in df['pass']:
        if pd.isna(value) or value == '' or value == 'nan':
            pass_types.append('No Pass')
        else:
            try:
                parsed = safe_eval_json(value)
                if parsed and isinstance(parsed, dict):
                    # Look for pass type indicators
                    if 'height' in parsed:
                        height = parsed['height']['name'] if isinstance(parsed['height'], dict) else str(parsed['height'])
                        pass_types.append(f"Pass - {height}")
                    elif 'body_part' in parsed:
                        body_part = parsed['body_part']['name'] if isinstance(parsed['body_part'], dict) else str(parsed['body_part'])
                        pass_types.append(f"Pass - {body_part}")
                    else:
                        pass_types.append('Pass - Standard')
                else:
                    pass_types.append('Pass - Unknown')
            except:
                pass_types.append('Pass - Error')
    
    pass_series = pd.Series(pass_types)
    value_counts = pass_series.value_counts()
    
    # Get top 7 categories
    top_categories = value_counts.head(7)
    unique_count = len(value_counts)
    
    analysis = {
        'feature': 'pass',
        'total_rows': total_rows,
        'missing_count': missing_count,
        'missing_percentage': missing_percentage,
        'valid_count': valid_count,
        'unique_count': unique_count,
        'top_categories': top_categories,
        'value_counts': value_counts,
        'description': 'Pass types and presence'
    }
    
    return analysis

def analyze_freeze_frame_feature(df):
    """Analyze freeze_frame feature - shot situation snapshots"""
    print("Analyzing freeze_frame...")
    
    total_rows = len(df)
    missing_mask = df['freeze_frame'].isna() | (df['freeze_frame'] == '') | (df['freeze_frame'] == 'nan')
    missing_count = missing_mask.sum()
    missing_percentage = (missing_count / total_rows) * 100
    valid_count = total_rows - missing_count
    
    # Count players in freeze frame
    frame_counts = []
    for value in df['freeze_frame']:
        if pd.isna(value) or value == '' or value == 'nan':
            frame_counts.append('No Freeze Frame')
        else:
            try:
                parsed = safe_eval_json(value)
                if parsed and isinstance(parsed, list):
                    count = len(parsed)
                    if count == 0:
                        frame_counts.append('Empty Frame')
                    elif count <= 5:
                        frame_counts.append(f'{count} Players')
                    elif count <= 10:
                        frame_counts.append('6-10 Players')
                    elif count <= 15:
                        frame_counts.append('11-15 Players')
                    else:
                        frame_counts.append('16+ Players')
                else:
                    frame_counts.append('Invalid Frame')
            except:
                frame_counts.append('Error Frame')
    
    frame_series = pd.Series(frame_counts)
    value_counts = frame_series.value_counts()
    
    # Get top 7 categories
    top_categories = value_counts.head(7)
    unique_count = len(value_counts)
    
    analysis = {
        'feature': 'freeze_frame',
        'total_rows': total_rows,
        'missing_count': missing_count,
        'missing_percentage': missing_percentage,
        'valid_count': valid_count,
        'unique_count': unique_count,
        'top_categories': top_categories,
        'value_counts': value_counts,
        'description': 'Player count in shot freeze frames'
    }
    
    return analysis

def create_complex_visualization(analysis, output_dir):
    """Create visualization for complex features"""
    feature = analysis['feature']
    top_categories = analysis['top_categories']
    missing_count = analysis['missing_count']
    missing_percentage = analysis['missing_percentage']
    unique_count = analysis['unique_count']
    description = analysis.get('description', '')
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Left plot: Top 7 categories
    colors = plt.cm.Set3(np.linspace(0, 1, len(top_categories)))
    bars = ax1.bar(range(len(top_categories)), top_categories.values, color=colors)
    ax1.set_xlabel('Categories')
    ax1.set_ylabel('Count')
    ax1.set_title(f'Top 7 Categories - {feature}\n{description}\n(Total: {unique_count} unique categories)')
    ax1.set_xticks(range(len(top_categories)))
    ax1.set_xticklabels([str(cat)[:20] for cat in top_categories.index], rotation=45, ha='right')
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        percentage = (height / analysis['total_rows']) * 100
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

def update_nominal_summary(new_analyses, output_dir):
    """Update the nominal features summary CSV with new analyses"""
    
    # Read existing summary
    existing_csv = output_dir / 'nominal_features_summary.csv'
    if existing_csv.exists():
        existing_df = pd.read_csv(existing_csv)
    else:
        existing_df = pd.DataFrame()
    
    # Create new summary data
    new_summary_data = []
    
    for analysis in new_analyses:
        # Get top 3 categories for summary
        top_3 = list(analysis['top_categories'].head(3).index)
        top_3_counts = list(analysis['top_categories'].head(3).values)
        top_3_str = ', '.join([f"{cat}({count:,})" for cat, count in zip(top_3, top_3_counts)])
        
        new_summary_data.append({
            'Feature': analysis['feature'],
            'Total_Rows': analysis['total_rows'],
            'Valid_Count': analysis['valid_count'],
            'Missing_Count': analysis['missing_count'],
            'Missing_Percentage': round(analysis['missing_percentage'], 2),
            'Unique_Categories': analysis['unique_count'],
            'Top_3_Categories': top_3_str,
            'Most_Common_Category': analysis['top_categories'].index[0] if len(analysis['top_categories']) > 0 else 'N/A',
            'Most_Common_Count': analysis['top_categories'].iloc[0] if len(analysis['top_categories']) > 0 else 0,
            'Most_Common_Percentage': round((analysis['top_categories'].iloc[0] / analysis['total_rows']) * 100, 2) if len(analysis['top_categories']) > 0 and analysis['total_rows'] > 0 else 0,
            'Description': analysis.get('description', '')
        })
    
    new_df = pd.DataFrame(new_summary_data)
    
    # Combine with existing data
    if not existing_df.empty:
        # Remove any existing entries for features we're updating
        existing_features = new_df['Feature'].tolist()
        existing_df = existing_df[~existing_df['Feature'].isin(existing_features)]
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        combined_df = new_df
    
    # Sort by missing percentage
    combined_df = combined_df.sort_values('Missing_Percentage')
    
    # Save updated CSV
    csv_path = output_dir / 'nominal_features_summary_updated.csv'
    combined_df.to_csv(csv_path, index=False)
    
    print(f"\nUpdated Nominal Features Summary saved to: {csv_path}")
    print(f"Total features in summary: {len(combined_df)}")
    
    return combined_df

def main():
    """Main analysis function"""
    print("=" * 80)
    print("EURO 2024 COMPLEX NOMINAL FEATURES ANALYSIS")
    print("=" * 80)
    
    # Create output directory
    output_dir = Path("EDA/visualizations/nominal_features")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Load data
        df = load_euro_2024_data()
        
        # Define complex features to analyze
        complex_features = ['related_events', 'player', 'pass', 'freeze_frame']
        
        # Check which features exist
        available_features = [col for col in complex_features if col in df.columns]
        missing_features = [col for col in complex_features if col not in df.columns]
        
        if missing_features:
            print(f"Warning: These features are not in the dataset: {missing_features}")
        
        print(f"Analyzing {len(available_features)} complex nominal features...")
        
        # Analyze each complex feature
        analyses = []
        
        for feature in available_features:
            print(f"\nProcessing: {feature}")
            
            if feature == 'related_events':
                analysis = analyze_related_events(df)
            elif feature == 'player':
                analysis = analyze_player_feature(df)
            elif feature == 'pass':
                analysis = analyze_pass_feature(df)
            elif feature == 'freeze_frame':
                analysis = analyze_freeze_frame_feature(df)
            
            analyses.append(analysis)
            
            # Create visualization
            create_complex_visualization(analysis, output_dir)
        
        # Update summary CSV
        if analyses:
            summary_df = update_nominal_summary(analyses, output_dir)
        
        print(f"\n" + "=" * 80)
        print("COMPLEX NOMINAL FEATURES ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"✅ Analyzed {len(analyses)} complex nominal features")
        print(f"📊 Created visualizations in: {output_dir}")
        print(f"📋 Updated summary CSV with complex features")
        
        # Print summary of new analyses
        for analysis in analyses:
            print(f"\n{analysis['feature'].upper()}:")
            print(f"  Missing: {analysis['missing_percentage']:.1f}%")
            print(f"  Categories: {analysis['unique_count']}")
            print(f"  Most common: {analysis['top_categories'].index[0]} ({analysis['top_categories'].iloc[0]:,} events)")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        raise

if __name__ == "__main__":
    main() 