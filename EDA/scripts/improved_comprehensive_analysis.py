import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import ast
from collections import Counter, defaultdict
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
    """Analyze ALL continuous variables including timestamp"""
    
    # Define continuous variables (ALL of them)
    continuous_normal = ['duration', 'second', 'home_score']
    continuous_non_normal = ['index', 'minute', 'possession', 'away_score', 'timestamp']
    coordinate_arrays = ['location', 'visible_area', 'carry']
    
    all_continuous = continuous_normal + continuous_non_normal + coordinate_arrays
    
    print("\n" + "="*80)
    print("CONTINUOUS VARIABLES ANALYSIS (COMPLETE)")
    print("="*80)
    
    # Statistics for all continuous features
    stats_data = []
    outliers_data = []
    
    for col in all_continuous:
        if col not in df.columns:
            print(f"Warning: {col} not found in dataset")
            continue
            
        print(f"\nAnalyzing: {col}")
        
        if col in coordinate_arrays:
            # Special handling for coordinate arrays
            non_null_count = len(df) - df[col].isnull().sum()
            missing_count = df[col].isnull().sum()
            missing_pct = (missing_count / len(df)) * 100
            
            # Add extraction recommendations
            if col == 'location':
                extraction = "Extract location_x, location_y from [x,y] coordinates. Range: x(0-120), y(0-80)"
                outcome = "2 new features: location_x (horizontal position), location_y (vertical position)"
            elif col == 'visible_area':
                extraction = "Extract polygon area, centroid_x, centroid_y, area_size from coordinate array"
                outcome = "4 new features: visible_area_size, centroid_x, centroid_y, polygon_complexity"
            elif col == 'carry':
                extraction = "Parse JSON and extract end_location_x, end_location_y, calculate carry_distance, carry_angle"
                outcome = "4 new features: carry_end_x, carry_end_y, carry_distance, carry_direction"
            
            stats_data.append({
                'Feature': col,
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
            'Q75': series_clean.quantile(0.75),
            'Extraction_Method': 'Standard numerical analysis',
            'Expected_Outcome': 'Direct use as continuous feature'
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
            'Outliers_Pct': (len(outliers) / len(series_clean)) * 100 if len(series_clean) > 0 else 0
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
    stats_df.to_csv('EDA/continuous_stats_complete.csv', index=False)
    print(f"\nComplete continuous statistics saved to: EDA/continuous_stats_complete.csv")
    
    # Save outliers (only if any exist)
    if outliers_data:
        outliers_df = pd.DataFrame(outliers_data)
        outliers_df.to_csv('EDA/outliers_complete.csv', index=False)
        print(f"Complete outliers analysis saved to: EDA/outliers_complete.csv")
    else:
        print("No outliers detected in any continuous variables")
    
    return stats_data, outliers_data

def create_continuous_visualizations_complete(df):
    """Create histograms and box plots for ALL continuous variables"""
    
    # Include ALL continuous variables including timestamp
    continuous_vars = ['duration', 'second', 'home_score', 'index', 'minute', 'possession', 'away_score', 'timestamp']
    available_vars = [col for col in continuous_vars if col in df.columns]
    
    if not available_vars:
        print("No continuous variables available for visualization")
        return
    
    print(f"Creating visualizations for {len(available_vars)} continuous variables")
    
    # Create histograms
    n_vars = len(available_vars)
    n_cols = 3
    n_rows = (n_vars + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    if n_vars == 1:
        axes = [axes]
    
    for i, col in enumerate(available_vars):
        row, col_idx = i // n_cols, i % n_cols
        series = pd.to_numeric(df[col], errors='coerce').dropna()
        
        if len(series) > 0:
            if n_rows > 1:
                ax = axes[row, col_idx]
            else:
                ax = axes[col_idx] if n_vars > 1 else axes[0]
                
            ax.hist(series, bins=30, alpha=0.7, edgecolor='black')
            ax.set_title(f'Distribution of {col}')
            ax.set_xlabel(col)
            ax.set_ylabel('Frequency')
            ax.grid(True, alpha=0.3)
    
    # Remove empty subplots
    for i in range(len(available_vars), n_rows * n_cols):
        row, col_idx = i // n_cols, i % n_cols
        if n_rows > 1:
            axes[row, col_idx].remove()
        elif n_vars < n_cols:
            axes[col_idx].remove()
    
    plt.tight_layout()
    plt.savefig('EDA/continuous_histograms_complete.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Create box plots
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    if n_vars == 1:
        axes = [axes]
    
    for i, col in enumerate(available_vars):
        row, col_idx = i // n_cols, i % n_cols
        series = pd.to_numeric(df[col], errors='coerce').dropna()
        
        if len(series) > 0:
            if n_rows > 1:
                ax = axes[row, col_idx]
            else:
                ax = axes[col_idx] if n_vars > 1 else axes[0]
                
            ax.boxplot(series)
            ax.set_title(f'Box Plot of {col}')
            ax.set_ylabel(col)
            ax.grid(True, alpha=0.3)
    
    # Remove empty subplots
    for i in range(len(available_vars), n_rows * n_cols):
        row, col_idx = i // n_cols, i % n_cols
        if n_rows > 1:
            axes[row, col_idx].remove()
        elif n_vars < n_cols:
            axes[col_idx].remove()
    
    plt.tight_layout()
    plt.savefig('EDA/continuous_boxplots_complete.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Complete continuous visualizations saved: continuous_histograms_complete.png, continuous_boxplots_complete.png")

def safe_json_parse(value):
    """Safely parse JSON-like strings"""
    if pd.isna(value):
        return None
    
    try:
        # Try to parse as JSON
        if isinstance(value, str):
            # Handle single quotes
            value = value.replace("'", '"')
            return json.loads(value)
        return value
    except:
        try:
            # Try ast.literal_eval for Python literals
            return ast.literal_eval(str(value))
        except:
            return str(value)

def analyze_json_structure_detailed(parsed_samples, field_name, series):
    """Detailed analysis of JSON structure including all nested fields"""
    
    if not parsed_samples:
        return {'type': 'Empty', 'description': 'No parseable data'}
    
    # Analyze structure in detail
    all_keys = set()
    field_analysis = defaultdict(lambda: {'types': set(), 'values': set(), 'samples': []})
    
    for item in parsed_samples:
        if isinstance(item, dict):
            all_keys.update(item.keys())
            
            # Analyze each field in detail
            for key, value in item.items():
                field_analysis[key]['samples'].append(value)
                
                if isinstance(value, dict):
                    field_analysis[key]['types'].add('dict')
                    # Analyze nested dict
                    for nested_key, nested_val in value.items():
                        nested_field = f"{key}.{nested_key}"
                        field_analysis[nested_field]['samples'].append(nested_val)
                        field_analysis[nested_field]['types'].add(type(nested_val).__name__)
                        if isinstance(nested_val, (str, int, float)) and len(str(nested_val)) < 100:
                            field_analysis[nested_field]['values'].add(str(nested_val))
                
                elif isinstance(value, list):
                    field_analysis[key]['types'].add('list')
                    if len(value) > 0:
                        field_analysis[key]['values'].add(f"List length: {len(value)}")
                        if isinstance(value[0], (int, float)):
                            field_analysis[key]['values'].add("Coordinate array")
                
                else:
                    field_analysis[key]['types'].add(type(value).__name__)
                    if isinstance(value, (str, int, float)) and len(str(value)) < 100:
                        field_analysis[key]['values'].add(str(value))
    
    # Build detailed structure analysis
    structure_details = {}
    
    for field, info in field_analysis.items():
        field_info = {
            'data_type': list(info['types']),
            'unique_values': len(info['values']),
            'sample_values': list(info['values'])[:10] if len(info['values']) <= 50 else f"{len(info['values'])} unique values",
            'field_classification': classify_field_type(field, info)
        }
        structure_details[field] = field_info
    
    return {
        'type': 'JSON Object',
        'description': f'JSON structure with {len(all_keys)} main fields',
        'unique_count': series.nunique(),
        'sample': parsed_samples[0],
        'main_fields': list(all_keys),
        'detailed_structure': structure_details
    }

def classify_field_type(field_name, field_info):
    """Classify the type and meaning of a field"""
    
    field_lower = field_name.lower()
    sample_values = list(field_info['values'])[:5]
    
    if 'id' in field_lower:
        return f"ID field - {len(field_info['values'])} unique identifiers"
    elif 'name' in field_lower:
        return f"Name field - categorical labels ({len(field_info['values'])} categories)"
    elif any(word in field_lower for word in ['location', 'position', 'x', 'y']):
        return "Coordinate field - spatial data"
    elif any(word in field_lower for word in ['length', 'distance', 'angle', 'height']):
        return "Measurement field - numerical measurement"
    elif 'list' in str(field_info['types']):
        return "Array field - coordinate or multi-value data"
    elif len(field_info['values']) < 20:
        return f"Categorical field - {len(field_info['values'])} categories: {sample_values}"
    else:
        return f"Complex field - {len(field_info['values'])} unique values"

def analyze_nominal_structure_complete(df):
    """Complete analysis of ALL nominal variables (excluding 21 high-missing ones)"""
    
    # High-missing ones to exclude (96.66%-100%):
    high_missing = [
        'player_off', 'miscontrol', 'bad_behaviour', 'block', 'tactics', '50_50',
        'ball_recovery', 'foul_committed', 'substitution', 'foul_won', 'interception',
        'dribble', 'shot', 'goalkeeper', 'clearance', 'duel', 'ball_receipt',
        'carry', 'pass', 'freeze_frame', 'event_uuid'
    ]
    
    # All nominal variables in the dataset
    all_nominal = [
        'id', 'type', 'possession_team', 'play_pattern', 'team', 'player', 'position',
        'pass', 'ball_receipt', 'carry', 'dribble', 'shot', 'goalkeeper', 'clearance',
        'interception', 'duel', 'block', 'foul_committed', 'foul_won', 'card',
        'substitution', 'bad_behaviour', 'ball_recovery', 'dispossessed', 'error',
        'miscontrol', 'player_off', 'player_on', 'tactics', 'half_start', 'half_end',
        'starting_xi', 'freeze_frame', 'match_id', 'home_team_name', 'away_team_name',
        'home_team_id', 'away_team_id', 'event_uuid', '50_50', 'related_events'
    ]
    
    # Filter to reasonable nominal variables (excluding high-missing)
    nominal_vars = [var for var in all_nominal if var not in high_missing and var in df.columns]
    
    print("\n" + "="*80)
    print("COMPLETE NOMINAL VARIABLES STRUCTURE ANALYSIS")
    print("="*80)
    print(f"Analyzing {len(nominal_vars)} nominal variables")
    print(f"Excluded {len(high_missing)} high-missing variables")
    
    structure_analysis = []
    
    for col in nominal_vars:
        print(f"\n--- {col.upper()} ---")
        
        # Basic info
        series = df[col]
        missing_count = series.isnull().sum()
        missing_pct = (missing_count / len(series)) * 100
        non_null_series = series.dropna()
        
        print(f"Total values: {len(series):,}")
        print(f"Missing: {missing_count:,} ({missing_pct:.2f}%)")
        print(f"Non-null: {len(non_null_series):,}")
        
        if len(non_null_series) == 0:
            continue
        
        # Sample values to understand structure
        sample_values = non_null_series.head(10).tolist()
        print(f"Sample values:")
        for i, val in enumerate(sample_values[:3]):
            print(f"  {i+1}: {str(val)[:200]}...")
        
        # Analyze structure in detail
        structure_info = analyze_field_structure_complete(non_null_series, col)
        
        # Store detailed analysis
        analysis_entry = {
            'Feature': col,
            'Total_Values': len(series),
            'Missing_Count': missing_count,
            'Missing_Pct': missing_pct,
            'Non_Null_Count': len(non_null_series),
            'Structure_Type': structure_info['type'],
            'Description': structure_info['description'],
            'Unique_Values': structure_info['unique_count'],
            'Main_Fields': str(structure_info.get('main_fields', []))[:300],
            'Detailed_Structure': str(structure_info.get('detailed_structure', {}))[:1000],
            'Sample_Value': str(structure_info['sample'])[:300]
        }
        
        structure_analysis.append(analysis_entry)
        
        print(f"Structure Type: {structure_info['type']}")
        print(f"Description: {structure_info['description']}")
        print(f"Unique values: {structure_info['unique_count']:,}")
        
        if structure_info.get('detailed_structure'):
            print("Detailed field analysis:")
            for field, details in list(structure_info['detailed_structure'].items())[:5]:
                print(f"  {field}: {details['field_classification']}")
    
    # Save complete structure analysis
    structure_df = pd.DataFrame(structure_analysis)
    structure_df.to_csv('EDA/nominal_structure_complete.csv', index=False)
    print(f"\nComplete nominal structure analysis saved to: EDA/nominal_structure_complete.csv")
    
    return structure_analysis

def analyze_field_structure_complete(series, field_name):
    """Complete analysis of a field structure"""
    
    # Get larger sample for better analysis
    sample_values = series.head(100).tolist()
    unique_count = series.nunique()
    
    # Determine structure type
    structure_info = {
        'type': 'Unknown',
        'description': '',
        'unique_count': unique_count,
        'sample': sample_values[0] if sample_values else None
    }
    
    if len(sample_values) == 0:
        return structure_info
    
    first_value = sample_values[0]
    
    # Check if it's a simple string/number
    if isinstance(first_value, (str, int, float)) and not (isinstance(first_value, str) and ('{' in str(first_value) or '[' in str(first_value))):
        if field_name in ['player', 'home_team_name', 'away_team_name']:
            structure_info.update({
                'type': 'Simple Text',
                'description': f'Player/team names - {unique_count:,} unique values',
                'main_fields': ['name'],
                'detailed_structure': {'name': {'field_classification': f'{unique_count} unique names (player/team identifiers)'}}
            })
        else:
            # Analyze value distribution for simple categorical
            value_counts = series.value_counts().head(20)
            structure_info.update({
                'type': 'Simple Categorical',
                'description': f'Categorical values - {unique_count:,} unique categories',
                'main_fields': ['value'],
                'detailed_structure': {'value': {
                    'field_classification': f'Categorical with {unique_count} categories',
                    'top_categories': dict(value_counts)
                }}
            })
    
    else:
        # Try to parse as JSON/dict structure
        parsed_samples = []
        for val in sample_values[:50]:  # Larger sample for better analysis
            parsed = safe_json_parse(val)
            if parsed is not None:
                parsed_samples.append(parsed)
        
        if parsed_samples:
            # Detailed JSON structure analysis
            structure_info.update(analyze_json_structure_detailed(parsed_samples, field_name, series))
        else:
            structure_info.update({
                'type': 'Complex String',
                'description': f'Complex string format - {unique_count:,} unique values',
                'main_fields': ['complex_string'],
                'detailed_structure': {'complex_string': {'field_classification': f'{unique_count} unique values (structure unclear)'}}
            })
    
    return structure_info

def main():
    """Main improved analysis function"""
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Create EDA directory if it doesn't exist
    import os
    os.makedirs('EDA', exist_ok=True)
    
    print("Starting IMPROVED comprehensive variable analysis...")
    
    # 1. Complete continuous variables analysis (including timestamp)
    print("\n🔢 ANALYZING CONTINUOUS VARIABLES...")
    continuous_stats, outliers_data = analyze_continuous_variables(df)
    create_continuous_visualizations_complete(df)
    
    # 2. Complete nominal structure analysis
    print("\n📋 ANALYZING NOMINAL STRUCTURES...")
    structure_analysis = analyze_nominal_structure_complete(df)
    
    print("\n" + "="*80)
    print("IMPROVED ANALYSIS COMPLETE")
    print("="*80)
    print("Files generated:")
    print("✅ EDA/continuous_stats_complete.csv - ALL continuous variables")
    print("✅ EDA/outliers_complete.csv - Complete outliers analysis") 
    print("✅ EDA/nominal_structure_complete.csv - COMPLETE nominal structure")
    print("✅ EDA/continuous_histograms_complete.png - ALL continuous histograms")
    print("✅ EDA/continuous_boxplots_complete.png - ALL continuous boxplots")
    
    print("\n🎯 KEY IMPROVEMENTS:")
    print("• Added missing 'timestamp' to continuous analysis")
    print("• Detailed coordinate array extraction recommendations")
    print("• Complete JSON structure parsing for nominal variables")
    print("• Full field-by-field analysis with classifications")

if __name__ == "__main__":
    main() 