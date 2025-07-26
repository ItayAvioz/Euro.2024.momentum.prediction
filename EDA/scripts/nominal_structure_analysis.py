import pandas as pd
import numpy as np
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

def analyze_nominal_structure(df):
    """Analyze structure of nominal categorical variables (excluding high-missing ones)"""
    
    # Define nominal variables (excluding 21 high-missing ones)
    # High-missing ones to exclude (96.66%-100%):
    high_missing = [
        'player_off', 'miscontrol', 'bad_behaviour', 'block', 'tactics', '50_50',
        'ball_recovery', 'foul_committed', 'substitution', 'foul_won', 'interception',
        'dribble', 'shot', 'goalkeeper', 'clearance', 'duel', 'ball_receipt',
        'carry', 'pass', 'freeze_frame', 'event_uuid'
    ]
    
    # All nominal variables
    all_nominal = [
        'id', 'type', 'possession_team', 'play_pattern', 'team', 'player', 'position',
        'pass', 'ball_receipt', 'carry', 'dribble', 'shot', 'goalkeeper', 'clearance',
        'interception', 'duel', 'block', 'foul_committed', 'foul_won', 'card',
        'substitution', 'bad_behaviour', 'ball_recovery', 'dispossessed', 'error',
        'miscontrol', 'player_off', 'player_on', 'tactics', 'half_start', 'half_end',
        'starting_xi', 'freeze_frame', 'match_id', 'home_team_name', 'away_team_name',
        'home_team_id', 'away_team_id', 'event_uuid', '50_50'
    ]
    
    # Filter to reasonable nominal variables (excluding high-missing)
    nominal_vars = [var for var in all_nominal if var not in high_missing and var in df.columns]
    
    print("\n" + "="*80)
    print("NOMINAL VARIABLES STRUCTURE ANALYSIS")
    print("="*80)
    print(f"Analyzing {len(nominal_vars)} nominal variables (excluding {len(high_missing)} high-missing)")
    
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
        sample_values = non_null_series.head(5).tolist()
        print(f"Sample values:")
        for i, val in enumerate(sample_values):
            print(f"  {i+1}: {str(val)[:150]}...")
        
        # Analyze structure
        structure_info = analyze_field_structure(non_null_series, col)
        
        # Store analysis
        analysis_entry = {
            'Feature': col,
            'Total_Values': len(series),
            'Missing_Count': missing_count,
            'Missing_Pct': missing_pct,
            'Non_Null_Count': len(non_null_series),
            'Structure_Type': structure_info['type'],
            'Description': structure_info['description'],
            'Unique_Values': structure_info['unique_count'],
            'Sample_Structure': str(structure_info['sample'])[:200],
            'Key_Fields': str(structure_info['key_fields'])[:200] if structure_info['key_fields'] else None,
            'Subcategory_Analysis': str(structure_info['subcategories'])[:300] if structure_info['subcategories'] else None
        }
        
        structure_analysis.append(analysis_entry)
        
        print(f"Structure Type: {structure_info['type']}")
        print(f"Description: {structure_info['description']}")
        print(f"Unique values: {structure_info['unique_count']:,}")
        
        if structure_info['key_fields']:
            print(f"Key fields: {structure_info['key_fields']}")
        
        if structure_info['subcategories']:
            print(f"Subcategories: {structure_info['subcategories']}")
    
    # Save structure analysis
    structure_df = pd.DataFrame(structure_analysis)
    structure_df.to_csv('EDA/nominal_structure_analysis.csv', index=False)
    print(f"\nNominal structure analysis saved to: EDA/nominal_structure_analysis.csv")
    
    return structure_analysis

def analyze_field_structure(series, field_name):
    """Analyze the structure of a specific field"""
    
    # Get sample of non-null values
    sample_values = series.head(100).tolist()
    unique_count = series.nunique()
    
    # Determine structure type
    structure_info = {
        'type': 'Unknown',
        'description': '',
        'unique_count': unique_count,
        'sample': sample_values[0] if sample_values else None,
        'key_fields': None,
        'subcategories': None
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
                'subcategories': f'{unique_count} unique names (not analyzed in detail)'
            })
        else:
            # Analyze value distribution for simple categorical
            value_counts = series.value_counts().head(10)
            structure_info.update({
                'type': 'Simple Categorical',
                'description': f'Categorical values - {unique_count:,} unique categories',
                'subcategories': dict(value_counts)
            })
    
    else:
        # Try to parse as JSON/dict structure
        parsed_samples = []
        for val in sample_values[:20]:
            parsed = safe_json_parse(val)
            if parsed is not None:
                parsed_samples.append(parsed)
        
        if parsed_samples:
            # Analyze JSON structure
            structure_info.update(analyze_json_structure(parsed_samples, field_name, series))
        else:
            structure_info.update({
                'type': 'Complex String',
                'description': f'Complex string format - {unique_count:,} unique values',
                'subcategories': f'{unique_count} unique values (structure unclear)'
            })
    
    return structure_info

def analyze_json_structure(parsed_samples, field_name, series):
    """Analyze JSON/dict structure and extract subcategories"""
    
    if not parsed_samples:
        return {'type': 'Empty', 'description': 'No parseable data'}
    
    # Analyze structure
    all_keys = set()
    id_fields = defaultdict(set)
    name_fields = defaultdict(set)
    
    for item in parsed_samples:
        if isinstance(item, dict):
            all_keys.update(item.keys())
            
            # Look for id/name patterns
            for key, value in item.items():
                if isinstance(value, dict):
                    if 'id' in value:
                        id_fields[key].add(value['id'])
                    if 'name' in value:
                        name_fields[key].add(value['name'])
                elif key == 'id':
                    id_fields['_root'].add(value)
                elif key == 'name':
                    name_fields['_root'].add(value)
    
    # Build analysis
    structure_type = 'JSON Object'
    description = f'JSON structure with keys: {list(all_keys)[:5]}'
    key_fields = list(all_keys)[:10]
    
    # Analyze subcategories for id fields
    subcategories = {}
    for field, ids in id_fields.items():
        if len(ids) < 100:  # Only analyze if reasonable number of categories
            subcategories[f'{field}_ids'] = f'{len(ids)} unique IDs'
        else:
            subcategories[f'{field}_ids'] = f'{len(ids)} unique IDs (too many to list)'
    
    for field, names in name_fields.items():
        if len(names) < 50:  # Only analyze if reasonable number
            subcategories[f'{field}_names'] = list(names)[:10]  # Top 10
        else:
            subcategories[f'{field}_names'] = f'{len(names)} unique names (e.g., player/team names)'
    
    return {
        'type': structure_type,
        'description': description,
        'unique_count': series.nunique(),
        'sample': parsed_samples[0],
        'key_fields': key_fields,
        'subcategories': subcategories
    }

def main():
    """Main analysis function"""
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Create EDA directory if it doesn't exist
    import os
    os.makedirs('EDA', exist_ok=True)
    
    print("Starting nominal variables structure analysis...")
    
    # Analyze nominal structure
    structure_analysis = analyze_nominal_structure(df)
    
    print("\n" + "="*60)
    print("NOMINAL STRUCTURE ANALYSIS COMPLETE")
    print("="*60)
    print("File generated:")
    print("- EDA/nominal_structure_analysis.csv")

if __name__ == "__main__":
    main() 