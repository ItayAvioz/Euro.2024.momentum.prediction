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

def get_statsbomb_data_type(col_name, sample_values):
    """Determine StatsBomb-specific data types based on documentation"""
    col_lower = col_name.lower()
    
    # Event-specific fields
    if 'event_uuid' in col_lower or 'id' in col_lower:
        return 'UUID/ID', 'count'
    elif 'timestamp' in col_lower or 'time' in col_lower:
        return 'Timestamp', 'seconds/minutes'
    elif 'location' in col_lower or 'coordinates' in col_lower:
        return 'Coordinate', 'pitch coordinates (0-120, 0-80)'
    elif 'minute' in col_lower:
        return 'Integer', 'minutes'
    elif 'second' in col_lower:
        return 'Integer', 'seconds'
    elif any(x in col_lower for x in ['duration', 'time']):
        return 'Float', 'seconds'
    elif any(x in col_lower for x in ['angle', 'direction']):
        return 'Float', 'degrees (0-360)'
    elif any(x in col_lower for x in ['distance', 'length', 'height']):
        return 'Float', 'meters'
    elif any(x in col_lower for x in ['speed', 'velocity']):
        return 'Float', 'meters/second'
    elif any(x in col_lower for x in ['xg', 'expected']):
        return 'Float', 'probability (0-1)'
    elif any(x in col_lower for x in ['score', 'goals']):
        return 'Integer', 'count'
    elif any(x in col_lower for x in ['jersey', 'number']):
        return 'Integer', 'jersey number (1-99)'
    elif 'formation' in col_lower:
        return 'String', 'tactical formation (e.g., 4-4-2)'
    elif any(x in col_lower for x in ['team', 'player', 'competition', 'season']):
        return 'String/Object', 'name/object'
    
    # Check sample values for type detection
    if sample_values:
        first_val = sample_values[0]
        if isinstance(first_val, dict):
            return 'JSON Object', 'complex object'
        elif isinstance(first_val, list):
            return 'JSON Array', 'array of values'
        elif isinstance(first_val, bool):
            return 'Boolean', 'true/false'
        elif isinstance(first_val, (int, np.integer)):
            return 'Integer', 'count'
        elif isinstance(first_val, (float, np.floating)):
            return 'Float', 'decimal value'
        else:
            return 'String', 'text value'
    
    return 'Mixed', 'various types'

def get_connection_info(source_file, col_name):
    """Get connection information for linking between CSV files"""
    connections = {}
    
    # Define primary and foreign key relationships based on StatsBomb structure
    if source_file == 'matches_complete.csv':
        if 'match_id' in col_name.lower():
            connections = {
                'primary_key': 'match_id',
                'connects_to': 'events_complete.csv (match_id), lineups_complete.csv (match_id), data_360_complete.csv (match_id)',
                'relationship': 'one-to-many'
            }
        elif 'competition' in col_name.lower():
            connections = {
                'foreign_key': 'competition.competition_id',
                'connects_to': 'competition metadata',
                'relationship': 'many-to-one'
            }
        elif 'season' in col_name.lower():
            connections = {
                'foreign_key': 'season.season_id', 
                'connects_to': 'season metadata',
                'relationship': 'many-to-one'
            }
            
    elif source_file == 'events_complete.csv':
        if 'match_id' in col_name.lower():
            connections = {
                'foreign_key': 'match_id',
                'connects_to': 'matches_complete.csv (match_id)',
                'relationship': 'many-to-one'
            }
        elif 'event_uuid' in col_name.lower():
            connections = {
                'primary_key': 'event_uuid',
                'connects_to': 'data_360_complete.csv (event_uuid)',
                'relationship': 'one-to-one'
            }
        elif 'player' in col_name.lower():
            connections = {
                'foreign_key': 'player.id',
                'connects_to': 'lineups_complete.csv (player.id)',
                'relationship': 'many-to-one'
            }
        elif 'team' in col_name.lower():
            connections = {
                'foreign_key': 'team.id',
                'connects_to': 'matches_complete.csv (home_team.id, away_team.id)',
                'relationship': 'many-to-one'
            }
            
    elif source_file == 'lineups_complete.csv':
        if 'match_id' in col_name.lower():
            connections = {
                'foreign_key': 'match_id',
                'connects_to': 'matches_complete.csv (match_id)',
                'relationship': 'many-to-one'
            }
        elif 'player_id' in col_name.lower():
            connections = {
                'primary_key': 'player_id',
                'connects_to': 'events_complete.csv (player.id), data_360_complete.csv (player.id)',
                'relationship': 'one-to-many'
            }
        elif 'team_id' in col_name.lower():
            connections = {
                'foreign_key': 'team_id',
                'connects_to': 'matches_complete.csv (home_team.id, away_team.id)',
                'relationship': 'many-to-one'
            }
            
    elif source_file == 'data_360_complete.csv':
        if 'event_uuid' in col_name.lower():
            connections = {
                'foreign_key': 'event_uuid',
                'connects_to': 'events_complete.csv (event_uuid)',
                'relationship': 'one-to-one'
            }
        elif 'match_id' in col_name.lower():
            connections = {
                'foreign_key': 'match_id',
                'connects_to': 'matches_complete.csv (match_id)',
                'relationship': 'many-to-one'
            }
    
    return connections

def extract_subcategories(values, max_categories=5):
    """Extract subcategories from complex JSON/object values"""
    subcategories = []
    
    for val in values[:1000]:  # Sample first 1000 values for performance
        if pd.isna(val):
            continue
            
        try:
            # Handle JSON objects
            if isinstance(val, str) and (val.startswith('{') or val.startswith('[')):
                parsed = json.loads(val)
                if isinstance(parsed, dict):
                    for key, subval in parsed.items():
                        if isinstance(subval, (str, int, float)):
                            subcategories.append(f"{key}: {subval}")
                        elif isinstance(subval, dict) and 'id' in subval:
                            subcategories.append(f"{key}.id: {subval['id']}")
                        elif isinstance(subval, dict) and 'name' in subval:
                            subcategories.append(f"{key}.name: {subval['name']}")
                elif isinstance(parsed, list) and parsed:
                    for item in parsed[:3]:  # First 3 items
                        if isinstance(item, dict):
                            if 'id' in item:
                                subcategories.append(f"id: {item['id']}")
                            if 'name' in item:
                                subcategories.append(f"name: {item['name']}")
                            if 'type' in item:
                                subcategories.append(f"type: {item['type']}")
            elif isinstance(val, (str, int, float)):
                subcategories.append(str(val))
        except:
            continue
    
    # Count and return top subcategories
    if subcategories:
        counter = Counter(subcategories)
        total = len(subcategories)
        top_categories = []
        
        for cat, count in counter.most_common(max_categories):
            percentage = (count / total) * 100
            top_categories.append(f"{cat} ({percentage:.1f}%)")
        
        return "; ".join(top_categories)
    
    return "No subcategories found"

def get_column_info(df, col_name, source_file):
    """Get comprehensive information about a column"""
    col = df[col_name]
    
    # Basic statistics
    total_count = len(col)
    null_count = col.isnull().sum()
    null_percentage = (null_count / total_count) * 100
    non_null_count = total_count - null_count
    
    # Get sample of non-null values
    non_null_values = col.dropna()
    if len(non_null_values) > 0:
        sample_values = non_null_values.head(100).tolist()
        
        # Parse JSON values for better analysis
        parsed_values = []
        for val in sample_values:
            parsed = safe_eval_json(val)
            parsed_values.append(parsed)
        
        # Data examples (first 3 non-null values)
        examples = []
        for i, val in enumerate(parsed_values[:3]):
            if isinstance(val, dict):
                examples.append(f"Ex{i+1}: {{id: {val.get('id', 'N/A')}, name: '{val.get('name', 'N/A')}'}}")
            elif isinstance(val, list) and val:
                examples.append(f"Ex{i+1}: [{len(val)} items]")
            else:
                examples.append(f"Ex{i+1}: {str(val)[:50]}...")
        
        data_examples = "; ".join(examples) if examples else "No examples available"
        
        # Get value distribution for categorical data
        if non_null_count > 0:
            # For simple categorical data
            if col.dtype == 'object' and not any(str(val).startswith(('{', '[')) for val in sample_values[:10]):
                value_counts = col.value_counts().head(5)
                top_values = []
                for val, count in value_counts.items():
                    percentage = (count / non_null_count) * 100
                    top_values.append(f"{val} ({percentage:.1f}%)")
                common_values = "; ".join(top_values)
            else:
                # For complex JSON data, extract subcategories
                common_values = extract_subcategories(parsed_values, max_categories=5)
        else:
            common_values = "No data available"
            
        # Determine data range
        try:
            if col.dtype in ['int64', 'float64'] and not any(str(val).startswith(('{', '[')) for val in sample_values[:5]):
                min_val = col.min()
                max_val = col.max()
                data_range = f"{min_val} to {max_val}"
            else:
                unique_count = col.nunique()
                data_range = f"{unique_count} unique values"
        except:
            data_range = "Variable range"
            
    else:
        data_examples = "No data available"
        common_values = "No data available"
        data_range = "No data available"
        parsed_values = []
    
    # Get data type and unit
    data_type, unit = get_statsbomb_data_type(col_name, parsed_values[:5] if parsed_values else [])
    
    # Get connection information
    connection_info = get_connection_info(source_file, col_name)
    
    # Create enhanced description based on StatsBomb documentation
    descriptions = {
        # Match data
        'match_id': 'Unique identifier for each match in the tournament',
        'match_date': 'Date when the match was played',
        'kick_off': 'Official kick-off time of the match',
        'competition': 'Competition information including name, country, and ID',
        'season': 'Season details including name and ID',
        'home_team': 'Home team information including name, ID, and country',
        'away_team': 'Away team information including name, ID, and country',
        'home_score': 'Final score for the home team',
        'away_score': 'Final score for the away team',
        'match_status': 'Current status of the match (available, etc.)',
        'last_updated': 'Timestamp of last data update',
        'match_week': 'Week number within the competition',
        'competition_stage': 'Stage of competition (group, knockout, etc.)',
        'stadium': 'Stadium information where match was played',
        'referee': 'Match referee information',
        
        # Event data
        'event_uuid': 'Unique identifier for each event within a match',
        'index': 'Sequential order of events within the match',
        'period': 'Match period (1st half, 2nd half, extra time)',
        'timestamp': 'Exact time when the event occurred',
        'minute': 'Match minute when event occurred',
        'second': 'Second within the minute when event occurred',
        'type': 'Type of event (pass, shot, foul, etc.) based on StatsBomb taxonomy',
        'possession': 'Possession sequence number',
        'possession_team': 'Team that has possession during this event',
        'play_pattern': 'How the phase of play started (regular play, corner, free kick, etc.)',
        'team': 'Team that performed the action',
        'player': 'Player who performed the action',
        'position': 'Playing position of the player',
        'location': 'X,Y coordinates on the pitch where event occurred (0-120, 0-80)',
        'duration': 'Duration of the event in seconds',
        'under_pressure': 'Whether the player was under pressure from opponents',
        'related_events': 'UUIDs of related events in the sequence',
        'tactics': 'Tactical formation and player positions',
        
        # Lineup data
        'team_id': 'Unique identifier for the team',
        'team_name': 'Name of the team',
        'lineup': 'List of players in the starting lineup with positions',
        'player_id': 'Unique identifier for each player',
        'player_name': 'Name of the player',
        'jersey_number': 'Jersey number worn by the player',
        'country': 'Player country information',
        
        # 360 data
        'visible_area': 'Area of the pitch visible to tracking cameras',
        'freeze_frame': 'Player and ball positions at moment of event',
        'teammate': 'Whether the tracked player is a teammate',
        'actor': 'Whether the tracked player is the one performing the action',
        'keeper': 'Whether the tracked player is a goalkeeper'
    }
    
    # Get description
    description = descriptions.get(col_name, f"StatsBomb data field: {col_name}")
    
    # Add notes based on StatsBomb documentation
    notes = []
    if 'location' in col_name.lower():
        notes.append("Pitch coordinates: [0,0] = bottom-left, [120,80] = top-right")
    if 'timestamp' in col_name.lower():
        notes.append("Format: HH:MM:SS.mmm from match start")
    if 'xg' in col_name.lower():
        notes.append("Expected Goals: probability of shot resulting in goal")
    if 'freeze_frame' in col_name.lower():
        notes.append("360° tracking data: player positions at event moment")
    if 'pressure' in col_name.lower():
        notes.append("Indicates defensive pressure within 5 yards")
    
    notes_text = "; ".join(notes) if notes else "Standard StatsBomb field"
    
    # Format connection information
    if connection_info:
        connection_text = f"Key: {connection_info.get('primary_key', connection_info.get('foreign_key', 'N/A'))} | " \
                         f"Links: {connection_info.get('connects_to', 'N/A')} | " \
                         f"Type: {connection_info.get('relationship', 'N/A')}"
    else:
        connection_text = "No direct connections identified"
    
    return {
        'feature_name': col_name,
        'source': source_file,
        'description': description,
        'data_type': data_type,
        'unit_measure': unit,
        'range_values': data_range,
        'common_values_top5': common_values,
        'data_examples': data_examples,
        'total_records': total_count,
        'null_count': null_count,
        'null_percentage': f"{null_percentage:.2f}%",
        'notes': notes_text,
        'key_connections': connection_text
    }

def main():
    """Main function to analyze all CSV files"""
    print("🔍 Starting Enhanced Euro 2024 Data Analysis...")
    
    # List of CSV files to analyze (with correct paths)
    csv_files = [
        'Data/matches_complete.csv',
        'Data/events_complete.csv', 
        'Data/lineups_complete.csv',
        'Data/data_360_complete.csv'
    ]
    
    all_columns_info = []
    
    for csv_file in csv_files:
        print(f"\n📊 Analyzing {csv_file}...")
        
        try:
            # Read CSV file
            df = pd.read_csv(csv_file)
            print(f"   ✓ Loaded {len(df)} rows, {len(df.columns)} columns")
            
            # Get just the filename for the source
            source_file = csv_file.split('/')[-1]
            
            # Analyze each column
            for col_name in df.columns:
                print(f"   🔍 Analyzing column: {col_name}")
                col_info = get_column_info(df, col_name, source_file)
                all_columns_info.append(col_info)
                
        except Exception as e:
            print(f"   ❌ Error analyzing {csv_file}: {str(e)}")
            continue
    
    # Create documentation DataFrame
    doc_df = pd.DataFrame(all_columns_info)
    
    # Save to CSV
    output_file = 'specs/Euro_2024_Enhanced_Data_Documentation.csv'
    doc_df.to_csv(output_file, index=False)
    
    print(f"\n✅ Enhanced documentation completed!")
    print(f"📄 Output file: {output_file}")
    print(f"📊 Total columns documented: {len(all_columns_info)}")
    print(f"📋 Columns: {list(doc_df.columns)}")
    
    # Print summary statistics
    print(f"\n📈 Summary by source file:")
    for source in doc_df['source'].unique():
        count = len(doc_df[doc_df['source'] == source])
        print(f"   {source}: {count} columns")

if __name__ == "__main__":
    main() 