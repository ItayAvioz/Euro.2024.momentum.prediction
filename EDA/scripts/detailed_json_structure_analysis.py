import pandas as pd
import numpy as np
import json
import ast
from collections import Counter, defaultdict
import warnings
warnings.filterwarnings('ignore')

def safe_json_parse(value):
    """Safely parse JSON-like strings"""
    if pd.isna(value):
        return None
    
    try:
        if isinstance(value, str):
            value = value.replace("'", '"')
            return json.loads(value)
        return value
    except:
        try:
            return ast.literal_eval(str(value))
        except:
            return None

def analyze_complex_json_features(df):
    """Analyze complex JSON features in detail"""
    
    # Focus on complex JSON features (even high-missing ones for structure understanding)
    complex_features = ['pass', 'shot', 'carry', 'dribble', 'goalkeeper', 'clearance', 
                       'interception', 'duel', 'block', 'foul_committed', 'foul_won', 
                       'ball_receipt', 'card', 'substitution']
    
    print("\n" + "="*80)
    print("DETAILED JSON STRUCTURE ANALYSIS")
    print("="*80)
    
    all_analysis = []
    
    for feature in complex_features:
        if feature not in df.columns:
            continue
            
        print(f"\n{'='*60}")
        print(f"ANALYZING: {feature.upper()}")
        print(f"{'='*60}")
        
        # Basic stats
        series = df[feature]
        missing_count = series.isnull().sum()
        missing_pct = (missing_count / len(series)) * 100
        non_null_series = series.dropna()
        
        print(f"Total values: {len(series):,}")
        print(f"Missing: {missing_count:,} ({missing_pct:.2f}%)")
        print(f"Non-null: {len(non_null_series):,}")
        
        if len(non_null_series) == 0:
            print("No data to analyze")
            continue
        
        # Parse JSON samples
        parsed_samples = []
        for i, val in enumerate(non_null_series.head(100)):
            parsed = safe_json_parse(val)
            if parsed is not None:
                parsed_samples.append(parsed)
            if i >= 50:  # Limit to 50 samples for analysis
                break
        
        if not parsed_samples:
            print("No parseable JSON data found")
            continue
        
        print(f"\nParsed {len(parsed_samples)} samples for analysis")
        
        # Detailed structure analysis
        structure_analysis = analyze_detailed_structure(parsed_samples, feature)
        
        # Store results
        analysis_entry = {
            'Feature': feature,
            'Missing_Count': missing_count,
            'Missing_Pct': missing_pct,
            'Non_Null_Count': len(non_null_series),
            'Parsed_Samples': len(parsed_samples),
            'Structure_Analysis': structure_analysis
        }
        
        all_analysis.append(analysis_entry)
        
        # Print detailed results
        print_detailed_analysis(feature, structure_analysis)
    
    # Save detailed analysis
    save_detailed_analysis(all_analysis)
    
    return all_analysis

def analyze_detailed_structure(parsed_samples, feature_name):
    """Analyze detailed structure of parsed JSON samples"""
    
    field_analysis = defaultdict(lambda: {
        'data_types': set(),
        'sample_values': [],
        'unique_values': set(),
        'nested_fields': defaultdict(set),
        'value_analysis': defaultdict(int)
    })
    
    # Analyze all samples
    for sample in parsed_samples:
        if isinstance(sample, dict):
            analyze_dict_recursively(sample, field_analysis, "")
    
    # Process analysis results
    structure_summary = {}
    
    for field_path, analysis in field_analysis.items():
        if not field_path:  # Skip empty path
            continue
            
        # Classify field
        field_classification = classify_detailed_field(field_path, analysis)
        
        # Get sample values
        sample_vals = list(analysis['unique_values'])[:10] if len(analysis['unique_values']) <= 20 else f"{len(analysis['unique_values'])} unique values"
        
        structure_summary[field_path] = {
            'classification': field_classification,
            'data_types': list(analysis['data_types']),
            'unique_count': len(analysis['unique_values']),
            'sample_values': sample_vals,
            'nested_fields': dict(analysis['nested_fields']) if analysis['nested_fields'] else None
        }
    
    return structure_summary

def analyze_dict_recursively(data, field_analysis, parent_path):
    """Recursively analyze dictionary structure"""
    
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{parent_path}.{key}" if parent_path else key
            
            # Record this field
            field_analysis[current_path]['data_types'].add(type(value).__name__)
            
            if isinstance(value, (str, int, float)):
                field_analysis[current_path]['unique_values'].add(str(value))
                field_analysis[current_path]['sample_values'].append(value)
                
            elif isinstance(value, list):
                field_analysis[current_path]['data_types'].add('list')
                if len(value) > 0:
                    if isinstance(value[0], (int, float)):
                        field_analysis[current_path]['unique_values'].add(f"coordinate_array_length_{len(value)}")
                    else:
                        field_analysis[current_path]['unique_values'].add(f"list_length_{len(value)}")
                
            elif isinstance(value, dict):
                field_analysis[current_path]['data_types'].add('dict')
                # Recursively analyze nested dict
                analyze_dict_recursively(value, field_analysis, current_path)
                
                # Also record nested field names
                for nested_key in value.keys():
                    field_analysis[current_path]['nested_fields'][nested_key].add(type(value[nested_key]).__name__)

def classify_detailed_field(field_path, analysis):
    """Classify field based on detailed analysis"""
    
    field_lower = field_path.lower()
    unique_count = len(analysis['unique_values'])
    data_types = analysis['data_types']
    
    # Coordinate fields
    if any(word in field_lower for word in ['location', 'x', 'y', 'position']):
        if 'list' in data_types:
            return "Coordinate Array - [x, y] position data"
        else:
            return "Coordinate Value - single position value"
    
    # Measurement fields
    elif any(word in field_lower for word in ['length', 'distance', 'angle', 'height', 'width']):
        return f"Measurement - numerical value ({unique_count} unique measurements)"
    
    # ID fields
    elif 'id' in field_lower:
        return f"ID Field - categorical identifier ({unique_count} unique IDs)"
    
    # Name fields
    elif 'name' in field_lower:
        sample_names = list(analysis['unique_values'])[:5]
        return f"Name Field - categorical labels ({unique_count} categories: {sample_names})"
    
    # Recipient/player fields
    elif any(word in field_lower for word in ['recipient', 'player']):
        return "Player Reference - contains player identification"
    
    # Body part / technique fields
    elif any(word in field_lower for word in ['body', 'foot', 'technique', 'type']):
        categories = list(analysis['unique_values'])[:10]
        return f"Technique/Method - categorical ({unique_count} categories: {categories})"
    
    # Boolean-like fields
    elif unique_count <= 5 and any(val in str(analysis['unique_values']).lower() for val in ['true', 'false', 'yes', 'no']):
        return f"Boolean/Flag - {unique_count} values: {list(analysis['unique_values'])}"
    
    # Small categorical
    elif unique_count <= 20:
        return f"Small Categorical - {unique_count} categories: {list(analysis['unique_values'])}"
    
    # Large categorical or continuous
    else:
        if 'float' in data_types or 'int' in data_types:
            return f"Numerical - {unique_count} unique values (likely continuous)"
        else:
            return f"Large Categorical - {unique_count} unique values"

def print_detailed_analysis(feature_name, structure_analysis):
    """Print detailed analysis results"""
    
    print(f"\n📋 STRUCTURE BREAKDOWN for {feature_name.upper()}:")
    print("-" * 50)
    
    for field_path, details in structure_analysis.items():
        print(f"\n🔸 {field_path}:")
        print(f"   Classification: {details['classification']}")
        print(f"   Data Types: {details['data_types']}")
        print(f"   Unique Values: {details['unique_count']}")
        
        if isinstance(details['sample_values'], list) and len(details['sample_values']) <= 10:
            print(f"   Sample Values: {details['sample_values']}")
        else:
            print(f"   Sample Values: {details['sample_values']}")
        
        if details['nested_fields']:
            print(f"   Nested Fields: {details['nested_fields']}")

def save_detailed_analysis(all_analysis):
    """Save detailed analysis to CSV"""
    
    # Flatten structure for CSV
    csv_data = []
    
    for analysis in all_analysis:
        feature = analysis['Feature']
        base_info = {
            'Feature': feature,
            'Missing_Count': analysis['Missing_Count'],
            'Missing_Pct': analysis['Missing_Pct'],
            'Non_Null_Count': analysis['Non_Null_Count']
        }
        
        if 'Structure_Analysis' in analysis:
            for field_path, details in analysis['Structure_Analysis'].items():
                row = base_info.copy()
                row.update({
                    'Field_Path': field_path,
                    'Classification': details['classification'],
                    'Data_Types': str(details['data_types']),
                    'Unique_Count': details['unique_count'],
                    'Sample_Values': str(details['sample_values'])[:200],
                    'Nested_Fields': str(details['nested_fields'])[:200] if details['nested_fields'] else None
                })
                csv_data.append(row)
        else:
            csv_data.append(base_info)
    
    # Save to CSV
    df_detailed = pd.DataFrame(csv_data)
    df_detailed.to_csv('EDA/detailed_json_structure.csv', index=False)
    print(f"\n📁 Detailed JSON structure analysis saved to: EDA/detailed_json_structure.csv")

def main():
    """Main function"""
    # Load data
    try:
        df = pd.read_csv('Data/euro_2024_complete_dataset.csv', low_memory=False)
        print(f"Dataset loaded: {df.shape[0]:,} rows × {df.shape[1]} columns")
    except FileNotFoundError:
        print("Dataset file not found!")
        return
    
    print("Starting detailed JSON structure analysis...")
    
    # Analyze complex JSON features
    analysis_results = analyze_complex_json_features(df)
    
    print("\n" + "="*80)
    print("DETAILED JSON ANALYSIS COMPLETE")
    print("="*80)
    print("This analysis provides complete structure breakdown for complex JSON features")
    print("including the 'pass' feature example you mentioned.")

if __name__ == "__main__":
    main() 