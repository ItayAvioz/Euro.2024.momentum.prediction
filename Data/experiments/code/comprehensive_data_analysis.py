import pandas as pd
import numpy as np
import json
import ast
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

def safe_eval_json(val):
    """Safely evaluate JSON-like strings"""
    if pd.isna(val) or val == '':
        return None
    try:
        # Try parsing as JSON first
        if isinstance(val, str) and (val.startswith('{') or val.startswith('[')):
            return json.loads(val)
        return val
    except:
        try:
            # Try parsing as Python literal
            return ast.literal_eval(val)
        except:
            return val

def get_column_info(df, col_name, source_file):
    """Get comprehensive information about a column"""
    col = df[col_name]
    
    # Basic info
    total_count = len(col)
    null_count = col.isnull().sum()
    non_null_count = total_count - null_count
    
    # Data type detection
    sample_values = col.dropna().head(10).tolist()
    
    # Determine data type
    if col.dtype == 'object':
        # Check if it's JSON-like
        sample_non_null = col.dropna().iloc[0] if not col.dropna().empty else ""
        if isinstance(sample_non_null, str) and (sample_non_null.startswith('{') or sample_non_null.startswith('[')):
            data_type = "JSON/Dict"
        elif col.nunique() < 0.5 * non_null_count and non_null_count > 10:
            data_type = "Categorical"
        else:
            data_type = "String"
    elif col.dtype in ['int64', 'int32', 'float64', 'float32']:
        if col.dtype in ['int64', 'int32']:
            data_type = "Integer"
        else:
            data_type = "Float"
    elif col.dtype == 'bool':
        data_type = "Boolean"
    elif 'datetime' in str(col.dtype):
        data_type = "Datetime"
    else:
        data_type = str(col.dtype)
    
    # Range calculation
    if data_type in ["Integer", "Float"]:
        min_val = col.min() if not col.empty else "N/A"
        max_val = col.max() if not col.empty else "N/A"
        value_range = f"{min_val} to {max_val}"
    elif data_type == "String" or data_type == "Categorical":
        unique_count = col.nunique()
        value_range = f"{unique_count} unique values"
    else:
        value_range = "Variable"
    
    # Top 5 values with percentages
    if non_null_count > 0:
        value_counts = col.value_counts().head(5)
        top_values = []
        for val, count in value_counts.items():
            percentage = (count / total_count) * 100
            if isinstance(val, str) and len(str(val)) > 50:
                val_str = str(val)[:47] + "..."
            else:
                val_str = str(val)
            top_values.append(f"{val_str} ({percentage:.1f}%)")
        top_values_str = "; ".join(top_values)
    else:
        top_values_str = "No data"
    
    # Create description based on column name and patterns
    description = generate_description(col_name, sample_values, data_type, source_file)
    
    return {
        'feature_name': col_name,
        'source': source_file,
        'value_type': data_type,
        'scale': 'Nominal' if data_type in ['String', 'Categorical', 'Boolean'] else 'Interval',
        'data_type': data_type,
        'unique_count': col.nunique() if non_null_count > 0 else 0,
        'measure_unit': get_measure_unit(col_name, data_type),
        'conversion_factor': 1,
        'min': col.min() if data_type in ["Integer", "Float"] and not col.empty else "",
        'max': col.max() if data_type in ["Integer", "Float"] and not col.empty else "",
        'null': null_count,
        'notes': description,
        'top_values': top_values_str,
        'range': value_range
    }

def generate_description(col_name, sample_values, data_type, source_file):
    """Generate description based on column name and content"""
    descriptions = {
        'match_id': 'Unique identifier for each match in the tournament',
        'event_uuid': 'Unique identifier for each event occurrence during matches',
        'player_id': 'Unique identifier for each player in the dataset',
        'team_id': 'Unique identifier for each team participating',
        'team_name': 'Name of the team (e.g., Spain, England, Netherlands)',
        'player_name': 'Full name of the player',
        'jersey_number': 'Player\'s jersey number during the match',
        'position': 'Player\'s field position (e.g., Goalkeeper, Center Forward)',
        'stage': 'Tournament stage (Group Stage, Quarter-finals, Semi-finals, Final)',
        'match_date': 'Date when the match was played (YYYY-MM-DD format)',
        'kick_off': 'Match start time in HH:MM:SS format',
        'home_team': 'JSON object containing home team information and lineup details',
        'away_team': 'JSON object containing away team information and lineup details',
        'home_score': 'Goals scored by the home team',
        'away_score': 'Goals scored by the away team',
        'competition': 'JSON object with competition details (UEFA Euro 2024)',
        'season': 'JSON object with season information (2024)',
        'match_status': 'Status of match data availability',
        'match_status_360': 'Status of 360-degree tracking data availability',
        'stadium': 'JSON object with stadium information where match was played',
        'referee': 'JSON object with referee information for the match',
        'visible_area': 'Array defining the visible tracking area coordinates on the pitch',
        'freeze_frame': 'JSON array containing player positions at a specific moment',
        'home_team_name': 'Simple name of the home team',
        'away_team_name': 'Simple name of the away team',
        'home_team_id': 'Unique identifier for the home team',
        'away_team_id': 'Unique identifier for the away team',
        'match_week': 'Week number in the tournament schedule',
        'competition_stage': 'JSON object with detailed stage information',
        'metadata': 'JSON object containing data version and fidelity information'
    }
    
    # Check for known patterns
    col_lower = col_name.lower()
    
    if col_name in descriptions:
        return descriptions[col_name]
    elif 'id' in col_lower:
        return f'Unique identifier related to {col_name.replace("_id", "").replace("_", " ")}'
    elif 'name' in col_lower:
        return f'Name or title of {col_name.replace("_name", "").replace("_", " ")}'
    elif 'time' in col_lower or 'timestamp' in col_lower:
        return f'Timestamp or time-related information for {col_name.replace("_", " ")}'
    elif 'location' in col_lower or 'coordinate' in col_lower:
        return f'Spatial coordinates or location data for {col_name.replace("_", " ")}'
    elif data_type == 'JSON/Dict':
        return f'Complex structured data containing {col_name.replace("_", " ")} information'
    elif data_type == 'Boolean':
        return f'Boolean flag indicating {col_name.replace("_", " ")} status'
    else:
        return f'Data field containing {col_name.replace("_", " ")} information'

def get_measure_unit(col_name, data_type):
    """Determine measurement unit based on column name"""
    col_lower = col_name.lower()
    
    if 'time' in col_lower and 'timestamp' not in col_lower:
        return 'seconds'
    elif 'coordinate' in col_lower or 'location' in col_lower:
        return 'pitch_units'
    elif 'score' in col_lower:
        return 'goals'
    elif 'number' in col_lower:
        return 'count'
    elif data_type in ['Integer', 'Float']:
        return 'numeric'
    else:
        return 'text'

def analyze_csv_file(file_path, file_name):
    """Analyze a single CSV file"""
    print(f"Analyzing {file_name}...")
    
    try:
        # Read with different encodings if needed
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='latin-1')
        
        results = []
        
        for col in df.columns:
            try:
                col_info = get_column_info(df, col, file_name)
                results.append(col_info)
            except Exception as e:
                print(f"Error analyzing column {col} in {file_name}: {e}")
                # Create basic info for problematic columns
                results.append({
                    'feature_name': col,
                    'source': file_name,
                    'value_type': 'Unknown',
                    'scale': 'Unknown',
                    'data_type': 'Unknown',
                    'unique_count': 0,
                    'measure_unit': 'unknown',
                    'conversion_factor': 1,
                    'min': '',
                    'max': '',
                    'null': len(df),
                    'notes': f'Error analyzing column: {str(e)}',
                    'top_values': 'Error in analysis',
                    'range': 'Unknown'
                })
        
        return results
        
    except Exception as e:
        print(f"Error reading {file_name}: {e}")
        return []

def create_connection_info():
    """Create information about how to connect the CSV files"""
    connections = {
        'matches_complete.csv': {
            'primary_key': 'match_id',
            'connects_to': ['events_complete.csv', 'lineups_complete.csv', 'data_360_complete.csv'],
            'connection_method': 'Use match_id to join with other files for event, lineup and tracking data'
        },
        'events_complete.csv': {
            'primary_key': 'event_uuid',
            'foreign_keys': ['match_id', 'player_id', 'team_id'],
            'connects_to': ['matches_complete.csv', 'lineups_complete.csv', 'data_360_complete.csv'],
            'connection_method': 'Use match_id to join with matches, player_id/team_id for lineups, event_uuid for 360 data'
        },
        'lineups_complete.csv': {
            'primary_key': 'player_id + match_id',
            'foreign_keys': ['match_id', 'team_id'],
            'connects_to': ['matches_complete.csv', 'events_complete.csv'],
            'connection_method': 'Use match_id and team_id to join with matches and events data'
        },
        'data_360_complete.csv': {
            'primary_key': 'event_uuid',
            'foreign_keys': ['match_id'],
            'connects_to': ['events_complete.csv', 'matches_complete.csv'],
            'connection_method': 'Use event_uuid to join with events data, match_id for match information'
        }
    }
    return connections

def main():
    # File paths
    files = {
        'matches_complete.csv': 'Data/matches_complete.csv',
        'events_complete.csv': 'Data/events_complete.csv',
        'lineups_complete.csv': 'Data/lineups_complete.csv',
        'data_360_complete.csv': 'Data/data_360_complete.csv'
    }
    
    all_results = []
    
    # Analyze each file
    for file_name, file_path in files.items():
        results = analyze_csv_file(file_path, file_name)
        all_results.extend(results)
    
    # Create connection information
    connections = create_connection_info()
    
    # Add connection information to notes
    for result in all_results:
        source_file = result['source']
        if source_file in connections:
            conn_info = connections[source_file]
            result['notes'] += f" | CONNECTIONS: {conn_info['connection_method']}"
    
    # Convert to DataFrame for CSV output
    output_df = pd.DataFrame(all_results)
    
    # Reorder columns to match the template structure
    column_order = [
        'feature_name', 'source', 'value_type', 'scale', 'data_type', 
        'unique_count', 'measure_unit', 'conversion_factor', 'min', 'max', 
        'null', 'notes', 'top_values', 'range'
    ]
    
    # Ensure all columns exist
    for col in column_order:
        if col not in output_df.columns:
            output_df[col] = ''
    
    output_df = output_df[column_order]
    
    # Save to specs folder
    output_path = 'specs/Euro_2024_Data_Documentation.csv'
    output_df.to_csv(output_path, index=False)
    
    print(f"\n✅ Analysis complete!")
    print(f"📄 Documentation saved to: {output_path}")
    print(f"📊 Total columns analyzed: {len(all_results)}")
    print(f"📁 Files analyzed: {len(files)}")
    
    # Print summary statistics
    print("\n📈 Summary by file:")
    for file_name in files.keys():
        file_results = [r for r in all_results if r['source'] == file_name]
        print(f"  {file_name}: {len(file_results)} columns")
    
    print("\n🔗 Connection Summary:")
    for file_name, conn_info in connections.items():
        print(f"  {file_name}:")
        print(f"    Primary Key: {conn_info.get('primary_key', 'N/A')}")
        print(f"    Connects to: {', '.join(conn_info.get('connects_to', []))}")

if __name__ == "__main__":
    main() 