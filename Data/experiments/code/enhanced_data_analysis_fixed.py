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

def safe_check_json_strings(values):
    """Safely check if values contain JSON strings without array ambiguity errors"""
    try:
        if not values or len(values) == 0:
            return False
        
        # Convert to string and check first few values safely
        sample_size = min(5, len(values))
        for i in range(sample_size):
            val = values[i]
            if pd.notna(val):
                val_str = str(val)
                if val_str.startswith(('{', '[')):
                    return True
        return False
    except:
        return False

def get_statsbomb_data_type(col_name, sample_values):
    """Determine StatsBomb-specific data types based on documentation"""
    col_lower = col_name.lower()
    
    # Event-specific fields
    if 'event_uuid' in col_lower or ('id' in col_lower and col_name != 'index'):
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
        try:
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
        except:
            pass
    
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
        elif col_name == 'id':
            connections = {
                'primary_key': 'event_uuid/id',
                'connects_to': 'data_360_complete.csv (event_uuid)',
                'relationship': 'one-to-one'
            }
        elif 'player' in col_name.lower():
            connections = {
                'foreign_key': 'player.id',
                'connects_to': 'lineups_complete.csv (player_id)',
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
                'connects_to': 'events_complete.csv (id)',
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
    
    try:
        for val in values[:500]:  # Sample first 500 values for performance
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
                        for item in parsed[:2]:  # First 2 items
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
            top_items = counter.most_common(max_categories)
            total_count = sum(counter.values())
            
            result = []
            for item, count in top_items:
                percentage = (count / total_count) * 100
                result.append(f"{item} ({percentage:.1f}%)")
            
            return "; ".join(result)
        else:
            return "No subcategories found"
    except:
        return "No subcategories found"

def get_column_info(df, col_name, source_file):
    """Get comprehensive information about a column"""
    try:
        col = df[col_name]
        total_count = len(col)
        
        # Handle null values
        null_count = col.isnull().sum()
        non_null_count = total_count - null_count
        null_percentage = (null_count / total_count) * 100 if total_count > 0 else 0
        
        # Get sample values safely
        if non_null_count > 0:
            # Get non-null values for analysis
            non_null_values = col.dropna()
            sample_size = min(10, len(non_null_values))
            sample_values = non_null_values.iloc[:sample_size].tolist()
            
            # Parse JSON values safely
            parsed_values = []
            for val in sample_values:
                parsed_val = safe_eval_json(val)
                parsed_values.append(parsed_val)
            
            # Create data examples safely
            examples = []
            for i, val in enumerate(sample_values[:3]):
                try:
                    if isinstance(val, dict):
                        # Extract key info from dict
                        if 'id' in val and 'name' in val:
                            examples.append(f"Ex{i+1}: {{id: {val.get('id', 'N/A')}, name: '{val.get('name', 'N/A')}'}}") 
                        else:
                            examples.append(f"Ex{i+1}: {{id: N/A, name: 'N/A'}}")
                    elif isinstance(val, list) and val:
                        examples.append(f"Ex{i+1}: [{len(val)} items]")
                    else:
                        val_str = str(val)[:50]
                        examples.append(f"Ex{i+1}: {val_str}...")
                except:
                    examples.append(f"Ex{i+1}: [complex data]")
            
            data_examples = "; ".join(examples) if examples else "No examples available"
            
            # Get value distribution for categorical data safely
            try:
                if non_null_count > 0:
                    # Check if values are simple categorical data (not JSON)
                    is_simple_categorical = False
                    try:
                        if col.dtype == 'object':
                            # Safely check if values are JSON strings
                            has_json = safe_check_json_strings(sample_values)
                            is_simple_categorical = not has_json
                        else:
                            is_simple_categorical = True
                    except:
                        is_simple_categorical = False
                    
                    if is_simple_categorical and col.dtype in ['object', 'int64', 'float64']:
                        try:
                            value_counts = col.value_counts().head(5)
                            top_values = []
                            for val, count in value_counts.items():
                                percentage = (count / non_null_count) * 100
                                top_values.append(f"{val} ({percentage:.1f}%)")
                            common_values = "; ".join(top_values)
                        except:
                            common_values = extract_subcategories(parsed_values, max_categories=5)
                    else:
                        # For complex JSON data, extract subcategories
                        common_values = extract_subcategories(parsed_values, max_categories=5)
                else:
                    common_values = "No data available"
            except:
                common_values = "No data available"
                
            # Determine data range safely
            try:
                if col.dtype in ['int64', 'float64']:
                    # Check if values are simple numbers (not in JSON strings)
                    try:
                        has_json = safe_check_json_strings(sample_values[:5])
                        if not has_json:
                            min_val = col.min()
                            max_val = col.max()
                            data_range = f"{min_val} to {max_val}"
                        else:
                            unique_count = col.nunique()
                            data_range = f"{unique_count} unique values"
                    except:
                        unique_count = col.nunique()
                        data_range = f"{unique_count} unique values"
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
            'id': 'Unique identifier for each event (event_uuid)',
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
            'pass': 'Pass event details including recipient, length, angle, etc.',
            'shot': 'Shot event details including technique, body_part, outcome, etc.',
            'dribble': 'Dribbling event details including nutmeg, overrun, etc.',
            'carry': 'Ball carry event details including end_location',
            'ball_receipt': 'Ball receipt event details',
            'foul_committed': 'Foul committed event details including type',
            'card': 'Card event details including type (yellow/red)',
            'substitution': 'Substitution event details',
            'goalkeeper': 'Goalkeeper event details including technique, position',
            'clearance': 'Clearance event details',
            'interception': 'Interception event details',
            'block': 'Block event details',
            'counterpress': 'Counterpress event details',
            'duel': 'Duel event details including type and outcome',
            'ball_recovery': 'Ball recovery event details',
            'dispossessed': 'Dispossessed event details',
            'miscontrol': 'Miscontrol event details',
            'injury_stoppage': 'Injury stoppage event details',
            'foul_won': 'Foul won event details',
            'offside': 'Offside event details',
            '50_50': 'Fifty-fifty event details',
            'bad_behaviour': 'Bad behaviour event details',
            'own_goal_against': 'Own goal against event details',
            'own_goal_for': 'Own goal for event details',
            'player_off': 'Player off event details',
            'player_on': 'Player on event details',
            'shield': 'Shield event details',
            'error': 'Error event details',
            'referee_ball_drop': 'Referee ball drop event details',
            'pressure': 'Pressure event details',
            
            # Lineup data
            'team_id': 'Unique identifier for the team',
            'team_name': 'Name of the team',
            'lineup': 'List of players in the starting lineup with positions',
            'player_id': 'Unique identifier for each player',
            'player_name': 'Name of the player',
            'jersey_number': 'Jersey number worn by the player',
            'country': 'Player country information',
            
            # 360 data
            'event_uuid': 'Unique identifier linking to events_complete.csv',
            'visible_area': 'Area of the pitch visible to tracking cameras',
            'freeze_frame': 'Player and ball positions at moment of event',
            'teammate': 'Whether the tracked player is a teammate',
            'actor': 'Whether the tracked player is the one performing the action',
            'keeper': 'Whether the tracked player is a goalkeeper',
            'match_id': 'Match identifier linking to other files'
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
        
    except Exception as e:
        print(f"   ⚠️ Error processing column {col_name}: {str(e)}")
        # Return default info for failed columns
        return {
            'feature_name': col_name,
            'source': source_file,
            'description': f"StatsBomb data field: {col_name}",
            'data_type': 'Mixed',
            'unit_measure': 'various types',
            'range_values': "Processing error",
            'common_values_top5': "Processing error",
            'data_examples': "Processing error",
            'total_records': len(df) if df is not None else 0,
            'null_count': 0,
            'null_percentage': "0.00%",
            'notes': "Error during processing",
            'key_connections': "No connections identified"
        }

def main():
    """Main function to analyze all CSV files"""
    print("🔍 Starting Enhanced Euro 2024 Data Analysis (FIXED VERSION)...")
    
    # List of CSV files to analyze (with correct paths)
    csv_files = [
        'matches_complete.csv',
        'events_complete.csv', 
        'lineups_complete.csv',
        'data_360_complete.csv'
    ]
    
    all_columns_info = []
    
    for csv_file in csv_files:
        print(f"\n📊 Analyzing {csv_file}...")
        
        try:
            # Read CSV file
            df = pd.read_csv(csv_file)
            print(f"   ✓ Loaded {len(df)} rows, {len(df.columns)} columns")
            
            # Get just the filename for the source
            source_file = csv_file
            
            # Analyze each column with robust error handling
            for col_name in df.columns:
                try:
                    print(f"   🔍 Analyzing column: {col_name}")
                    col_info = get_column_info(df, col_name, source_file)
                    all_columns_info.append(col_info)
                    print(f"   ✅ Successfully processed: {col_name}")
                except Exception as e:
                    print(f"   ❌ Failed to process column {col_name}: {str(e)}")
                    # Add basic info even for failed columns
                    basic_info = {
                        'feature_name': col_name,
                        'source': source_file,
                        'description': f"StatsBomb data field: {col_name}",
                        'data_type': 'Mixed',
                        'unit_measure': 'various types',
                        'range_values': "Processing error",
                        'common_values_top5': "Processing error", 
                        'data_examples': "Processing error",
                        'total_records': len(df),
                        'null_count': 0,
                        'null_percentage': "0.00%",
                        'notes': "Error during processing",
                        'key_connections': "No connections identified"
                    }
                    all_columns_info.append(basic_info)
                    continue
                
        except Exception as e:
            print(f"   ❌ Error analyzing {csv_file}: {str(e)}")
            continue
    
    # Create documentation DataFrame
    doc_df = pd.DataFrame(all_columns_info)
    
    # Save to CSV (create specs directory if needed)
    output_file = '../specs/Euro_2024_Enhanced_Data_Documentation.csv'
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
    
    # Check if we got all expected columns
    expected_total = 88
    if len(all_columns_info) == expected_total:
        print(f"\n🎉 SUCCESS: All {expected_total} columns documented!")
    else:
        print(f"\n⚠️ Got {len(all_columns_info)}/{expected_total} columns")

if __name__ == "__main__":
    main() 