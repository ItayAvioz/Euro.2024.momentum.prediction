import pandas as pd
import numpy as np
from scipy import stats
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def analyze_variable_types(data_path: str):
    """Analyze and classify all variables in the Euro 2024 dataset."""
    
    # Load dataset sample for analysis
    print("Loading dataset sample...")
    df = pd.read_csv(data_path, nrows=10000)  # Sample for analysis
    
    print(f"Dataset shape: {df.shape}")
    print(f"Total columns: {len(df.columns)}")
    
    # Initialize classification dictionaries
    continuous_normal = []
    continuous_non_normal = []
    categorical_ordinal = []
    categorical_nominal = []
    categorical_binomial = []
    
    # Analyze each column
    for col in df.columns:
        print(f"\nAnalyzing column: {col}")
        
        # Get basic info
        dtype = str(df[col].dtype)
        null_count = df[col].isnull().sum()
        null_percentage = (null_count / len(df)) * 100
        unique_count = df[col].nunique()
        
        # Check if column is numeric
        if pd.api.types.is_numeric_dtype(df[col]):
            # Check if it's actually binary/binomial
            unique_vals = df[col].dropna().unique()
            if len(unique_vals) <= 2:
                # Binomial (including cases with missing values)
                categorical_binomial.append({
                    'column': col,
                    'dtype': dtype,
                    'unique_values': unique_vals.tolist(),
                    'null_count': null_count,
                    'null_percentage': round(null_percentage, 2),
                    'description': 'Numeric binary variable'
                })
            else:
                # Continuous variable - test for normality
                sample_data = df[col].dropna()
                if len(sample_data) > 3:  # Need at least 4 values for normality test
                    try:
                        # Shapiro-Wilk test for normality (use subset if too large)
                        test_sample = sample_data.sample(min(5000, len(sample_data)), random_state=42)
                        stat, p_value = stats.shapiro(test_sample)
                        is_normal = p_value > 0.05
                        
                        var_info = {
                            'column': col,
                            'dtype': dtype,
                            'unique_count': unique_count,
                            'null_count': null_count,
                            'null_percentage': round(null_percentage, 2),
                            'mean': round(sample_data.mean(), 4),
                            'std': round(sample_data.std(), 4),
                            'min': round(sample_data.min(), 4),
                            'max': round(sample_data.max(), 4),
                            'shapiro_stat': round(stat, 4),
                            'shapiro_p_value': round(p_value, 6),
                            'is_normal': is_normal
                        }
                        
                        if is_normal:
                            continuous_normal.append(var_info)
                        else:
                            continuous_non_normal.append(var_info)
                    except:
                        # If normality test fails, classify as non-normal
                        continuous_non_normal.append({
                            'column': col,
                            'dtype': dtype,
                            'unique_count': unique_count,
                            'null_count': null_count,
                            'null_percentage': round(null_percentage, 2),
                            'note': 'Normality test failed - classified as non-normal'
                        })
                else:
                    continuous_non_normal.append({
                        'column': col,
                        'dtype': dtype,
                        'unique_count': unique_count,
                        'null_count': null_count,
                        'null_percentage': round(null_percentage, 2),
                        'note': 'Insufficient data for normality test'
                    })
        else:
            # Categorical variable
            sample_data = df[col].dropna()
            unique_vals = sample_data.unique()
            
            # Check if binomial (including string true/false)
            if len(unique_vals) <= 2:
                # Check for boolean-like values
                str_vals = [str(v).lower() for v in unique_vals if pd.notna(v)]
                boolean_indicators = {'true', 'false', '1', '0', 'yes', 'no', 'y', 'n'}
                
                if any(val in boolean_indicators for val in str_vals) or len(unique_vals) <= 2:
                    categorical_binomial.append({
                        'column': col,
                        'dtype': dtype,
                        'unique_values': unique_vals.tolist()[:10],  # Limit display
                        'unique_count': len(unique_vals),
                        'null_count': null_count,
                        'null_percentage': round(null_percentage, 2),
                        'description': 'Categorical binary variable'
                    })
                else:
                    categorical_nominal.append({
                        'column': col,
                        'dtype': dtype,
                        'unique_count': unique_count,
                        'null_count': null_count,
                        'null_percentage': round(null_percentage, 2),
                        'sample_values': unique_vals.tolist()[:10],
                        'description': 'Low cardinality nominal'
                    })
            else:
                # Check if ordinal (look for obvious ordering patterns)
                ordinal_patterns = ['period', 'minute', 'second', 'index', 'week', 'stage', 'level', 'rank']
                is_ordinal = any(pattern in col.lower() for pattern in ordinal_patterns)
                
                # Also check for numeric-like strings that suggest ordering
                if not is_ordinal:
                    try:
                        # Try to convert to numeric to see if it's ordinal
                        numeric_vals = pd.to_numeric(sample_data, errors='coerce')
                        if not numeric_vals.isnull().all():
                            is_ordinal = True
                    except:
                        pass
                
                var_info = {
                    'column': col,
                    'dtype': dtype,
                    'unique_count': unique_count,
                    'null_count': null_count,
                    'null_percentage': round(null_percentage, 2),
                    'sample_values': unique_vals.tolist()[:10]
                }
                
                if is_ordinal:
                    var_info['description'] = 'Categorical with natural ordering'
                    categorical_ordinal.append(var_info)
                else:
                    var_info['description'] = 'Categorical without natural ordering'
                    categorical_nominal.append(var_info)
    
    # Create summary statistics
    summary = {
        'total_variables': len(df.columns),
        'continuous_normal': len(continuous_normal),
        'continuous_non_normal': len(continuous_non_normal),
        'categorical_ordinal': len(categorical_ordinal),
        'categorical_nominal': len(categorical_nominal),
        'categorical_binomial': len(categorical_binomial)
    }
    
    return {
        'summary': summary,
        'continuous_normal': continuous_normal,
        'continuous_non_normal': continuous_non_normal,
        'categorical_ordinal': categorical_ordinal,
        'categorical_nominal': categorical_nominal,
        'categorical_binomial': categorical_binomial
    }

def save_variable_classifications(results: dict, output_dir: str):
    """Save variable classifications to separate documents."""
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save summary
    with open(output_path / 'variable_classification_summary.json', 'w') as f:
        json.dump(results['summary'], f, indent=4)
    
    # Save each group
    groups = ['continuous_normal', 'continuous_non_normal', 'categorical_ordinal', 
              'categorical_nominal', 'categorical_binomial']
    
    for group in groups:
        with open(output_path / f'{group}_variables.json', 'w') as f:
            json.dump(results[group], f, indent=4)
        
        # Also create markdown documentation
        create_markdown_doc(results[group], group, output_path)

def create_markdown_doc(variables: list, group_name: str, output_path: Path):
    """Create markdown documentation for each variable group."""
    
    # Define group descriptions
    descriptions = {
        'continuous_normal': 'Continuous Variables with Normal Distribution',
        'continuous_non_normal': 'Continuous Variables with Non-Normal Distribution',
        'categorical_ordinal': 'Categorical Variables with Natural Ordering',
        'categorical_nominal': 'Categorical Variables without Natural Ordering',
        'categorical_binomial': 'Binary/Binomial Variables (True/False with possible missing values)'
    }
    
    md_content = f"# {descriptions[group_name]}\n\n"
    md_content += f"**Total Variables in Group:** {len(variables)}\n\n"
    
    if group_name.startswith('continuous'):
        md_content += "## Statistical Properties\n\n"
        md_content += "| Variable | Data Type | Null Count | Null % | Mean | Std | Min | Max | Shapiro p-value | Normal? |\n"
        md_content += "|----------|-----------|------------|--------|------|-----|-----|-----|-----------------|----------|\n"
        
        for var in variables:
            mean_val = var.get('mean', 'N/A')
            std_val = var.get('std', 'N/A')
            min_val = var.get('min', 'N/A')
            max_val = var.get('max', 'N/A')
            p_val = var.get('shapiro_p_value', 'N/A')
            is_normal = var.get('is_normal', 'N/A')
            
            md_content += f"| {var['column']} | {var['dtype']} | {var['null_count']} | {var['null_percentage']}% | {mean_val} | {std_val} | {min_val} | {max_val} | {p_val} | {is_normal} |\n"
    
    else:
        md_content += "## Variable Properties\n\n"
        md_content += "| Variable | Data Type | Unique Count | Null Count | Null % | Sample Values | Description |\n"
        md_content += "|----------|-----------|--------------|------------|--------|---------------|-------------|\n"
        
        for var in variables:
            sample_vals = var.get('sample_values', var.get('unique_values', []))
            sample_str = ', '.join(str(v)[:50] for v in sample_vals[:5])
            if len(sample_vals) > 5:
                sample_str += "..."
            
            description = var.get('description', 'N/A')
            unique_count = var.get('unique_count', 'N/A')
            
            md_content += f"| {var['column']} | {var['dtype']} | {unique_count} | {var['null_count']} | {var['null_percentage']}% | {sample_str} | {description} |\n"
    
    md_content += f"\n\n## Analysis Notes\n\n"
    
    if group_name == 'continuous_normal':
        md_content += "- Variables in this group follow a normal distribution (Shapiro-Wilk p > 0.05)\n"
        md_content += "- Can use parametric statistical tests\n"
        md_content += "- Suitable for correlation analysis, regression modeling\n"
    elif group_name == 'continuous_non_normal':
        md_content += "- Variables in this group do not follow a normal distribution (Shapiro-Wilk p ≤ 0.05)\n"
        md_content += "- May require transformation or non-parametric tests\n"
        md_content += "- Consider log, square root, or other transformations\n"
    elif group_name == 'categorical_ordinal':
        md_content += "- Variables with natural ordering (can be ranked)\n"
        md_content += "- Can use rank-based correlation measures\n"
        md_content += "- Suitable for ordinal regression analysis\n"
    elif group_name == 'categorical_nominal':
        md_content += "- Variables without natural ordering\n"
        md_content += "- Require dummy encoding for modeling\n"
        md_content += "- Use chi-square tests for associations\n"
    elif group_name == 'categorical_binomial':
        md_content += "- Binary variables (True/False, 0/1, Yes/No)\n"
        md_content += "- Missing values are still considered binomial variables\n"
        md_content += "- Can be used directly in logistic regression\n"
        md_content += "- Consider imputation strategies for missing values\n"
    
    # Save markdown file
    with open(output_path / f'{group_name}_variables.md', 'w', encoding='utf-8') as f:
        f.write(md_content)

if __name__ == '__main__':
    # Analyze the dataset
    data_path = '../Data/euro_2024_complete_dataset.csv'
    output_dir = 'variable_classifications'
    
    print("Starting variable type analysis...")
    results = analyze_variable_types(data_path)
    
    print("\n=== CLASSIFICATION SUMMARY ===")
    for key, value in results['summary'].items():
        print(f"{key}: {value}")
    
    print(f"\nSaving classifications to {output_dir}...")
    save_variable_classifications(results, output_dir)
    
    print("Analysis complete!")
    print(f"\nFiles created:")
    print(f"- variable_classification_summary.json")
    for group in ['continuous_normal', 'continuous_non_normal', 'categorical_ordinal', 
                  'categorical_nominal', 'categorical_binomial']:
        print(f"- {group}_variables.json")
        print(f"- {group}_variables.md") 