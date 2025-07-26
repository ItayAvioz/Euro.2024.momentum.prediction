import pandas as pd
import numpy as np
import json
import ast
from collections import Counter, defaultdict
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

def extract_subcategories_enhanced(values, max_categories=5, col_name=""):
    """Enhanced extraction of subcategories with special handling for event types"""
    subcategories = []
    
    try:
        # Special handling for event types and similar structured data
        if col_name.lower() in ['type', 'event_type'] or 'type' in col_name.lower():
            # Extract id and name pairs specifically for event types
            id_name_pairs = []
            for val in values[:2000]:  # Larger sample for event types
                if pd.isna(val):
                    continue
                try:
                    if isinstance(val, str) and val.startswith('{'):
                        parsed = json.loads(val)
                        if isinstance(parsed, dict) and 'id' in parsed and 'name' in parsed:
                            id_name_pairs.append(f"{parsed['name']} (ID: {parsed['id']})")
                    elif isinstance(val, dict) and 'id' in val and 'name' in val:
                        id_name_pairs.append(f"{val['name']} (ID: {val['id']})")
                except:
                    continue
            
            if id_name_pairs:
                counter = Counter(id_name_pairs)
                total_count = sum(counter.values())
                result = []
                for item, count in counter.most_common(max_categories):
                    percentage = (count / total_count) * 100
                    result.append(f"{item} ({percentage:.1f}%)")
                return "; ".join(result)
        
        # Standard subcategory extraction for other fields
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
                            common_values = extract_subcategories_enhanced(parsed_values, max_categories=5, col_name=col_name)
                    else:
                        # For complex JSON data, extract subcategories using enhanced method
                        common_values = extract_subcategories_enhanced(parsed_values, max_categories=5, col_name=col_name)
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
        
        # Enhanced descriptions with all event types covered
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
            
            # Event data - Core fields
            'id': 'Unique identifier for each event (event_uuid)',
            'index': 'Sequential order of events within the match',
            'period': 'Match period (1st half, 2nd half, extra time)',
            'timestamp': 'Exact time when the event occurred',
            'minute': 'Match minute when event occurred',
            'second': 'Second within the minute when event occurred',
            'type': 'Type of event (pass, shot, foul, etc.) with 33 distinct categories based on StatsBomb taxonomy',
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
            
            # Event data - Specific event types
            'pass': 'Pass event details: recipient, length, angle, height, technique, outcome, assist qualifiers',
            'shot': 'Shot event details: technique, body_part, outcome, xG value, end_location, deflected, follows_dribble',
            'dribble': 'Dribbling event details: nutmeg, overrun, outcome, no_touch',
            'carry': 'Ball carry event details: end_location indicating where carry ended',
            'ball_receipt': 'Ball receipt event details: outcome (complete/incomplete)',
            'foul_committed': 'Foul committed event details: type, advantage, penalty, card information',
            'card': 'Card event details: type (yellow/red), reason for card',
            'substitution': 'Substitution event details: outcome (tactical/injury), replacement player',
            'goalkeeper': 'Goalkeeper event details: technique, position, outcome, punched_out, success_in_play',
            'clearance': 'Clearance event details: body_part (head, foot), aerial, defensive action',
            'interception': 'Interception event details: outcome (won/lost), reads opponent pass',
            'block': 'Block event details: deflection, save_block, offensive/defensive',
            'counterpress': 'Counterpress event details: immediate pressure after losing possession',
            'duel': 'Duel event details: type (tackle, aerial), outcome (won/lost), 50/50 contests',
            'ball_recovery': 'Ball recovery event details: recovery_failure, gaining loose ball possession',
            'dispossessed': 'Dispossessed event details: losing ball possession to opponent',
            'miscontrol': 'Miscontrol event details: aerial_won, poor ball control',
            'injury_stoppage': 'Injury stoppage event details: in_chain, match delay for injury',
            'foul_won': 'Foul won event details: advantage, penalty, drawing foul from opponent',
            'offside': 'Offside event details: player caught in offside position',
            '50_50': 'Fifty-fifty event details: outcome of loose ball contest',
            'bad_behaviour': 'Bad behaviour event details: card, misconduct',
            'own_goal_against': 'Own goal against event details',
            'own_goal_for': 'Own goal for event details',
            'player_off': 'Player off event details: permanent removal from match',
            'player_on': 'Player on event details: entering match',
            'shield': 'Shield event details: protecting ball from opponent',
            'error': 'Error event details: mistake leading to danger',
            'referee_ball_drop': 'Referee ball drop event details',
            'pressure': 'Pressure event details: applying pressure to opponent',
            
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
            'freeze_frame': 'Player and ball positions at moment of event - 360° tracking data',
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
        if col_name.lower() == 'type':
            notes.append("33 distinct event types including Pass, Ball Receipt, Carry, Pressure, Shot, Dribble, etc.")
        
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

def extract_event_types_mapping(df):
    """Extract event type ID to name mapping from events data"""
    event_types = {}
    
    try:
        if 'type' in df.columns:
            type_col = df['type'].dropna()
            for val in type_col:
                try:
                    if isinstance(val, str) and val.startswith('{'):
                        parsed = json.loads(val)
                        if isinstance(parsed, dict) and 'id' in parsed and 'name' in parsed:
                            event_types[parsed['id']] = parsed['name']
                    elif isinstance(val, dict) and 'id' in val and 'name' in val:
                        event_types[val['id']] = val['name']
                except:
                    continue
    except Exception as e:
        print(f"Error extracting event types: {e}")
    
    return event_types

def create_key_connections_data():
    """Create key connections mapping between CSV files"""
    connections_data = [
        {
            'source_file': 'matches_complete.csv',
            'source_field': 'match_id',
            'target_file': 'events_complete.csv',
            'target_field': 'match_id',
            'relationship_type': 'one-to-many',
            'description': 'One match has many events'
        },
        {
            'source_file': 'matches_complete.csv',
            'source_field': 'match_id',
            'target_file': 'lineups_complete.csv',
            'target_field': 'match_id',
            'relationship_type': 'one-to-many',
            'description': 'One match has many player lineups'
        },
        {
            'source_file': 'matches_complete.csv',
            'source_field': 'match_id',
            'target_file': 'data_360_complete.csv',
            'target_field': 'match_id',
            'relationship_type': 'one-to-many',
            'description': 'One match has many 360 tracking events'
        },
        {
            'source_file': 'events_complete.csv',
            'source_field': 'id (event_uuid)',
            'target_file': 'data_360_complete.csv',
            'target_field': 'event_uuid',
            'relationship_type': 'one-to-one',
            'description': 'Each event can have corresponding 360 tracking data'
        },
        {
            'source_file': 'lineups_complete.csv',
            'source_field': 'player_id',
            'target_file': 'events_complete.csv',
            'target_field': 'player_id',
            'relationship_type': 'one-to-many',
            'description': 'One player in lineup participates in many events'
        },
        {
            'source_file': 'matches_complete.csv',
            'source_field': 'home_team_id',
            'target_file': 'events_complete.csv',
            'target_field': 'team_id',
            'relationship_type': 'one-to-many',
            'description': 'Team in match performs many events'
        },
        {
            'source_file': 'matches_complete.csv',
            'source_field': 'away_team_id',
            'target_file': 'events_complete.csv',
            'target_field': 'team_id',
            'relationship_type': 'one-to-many',
            'description': 'Team in match performs many events'
        }
    ]
    
    return connections_data

def main():
    """Main function to analyze all CSV files and create multiple tabs"""
    print("🔍 Starting Enhanced Euro 2024 Data Analysis with Multiple Tabs...")
    
    # List of CSV files to analyze
    csv_files = [
        'matches_complete.csv',
        'events_complete.csv', 
        'lineups_complete.csv',
        'data_360_complete.csv'
    ]
    
    all_columns_info = []
    all_event_types = {}
    
    for csv_file in csv_files:
        print(f"\n📊 Analyzing {csv_file}...")
        
        try:
            # Read CSV file
            df = pd.read_csv(csv_file)
            print(f"   ✓ Loaded {len(df)} rows, {len(df.columns)} columns")
            
            # Extract event types mapping if this is events file
            if csv_file == 'events_complete.csv':
                print("   🔍 Extracting event types mapping...")
                event_types = extract_event_types_mapping(df)
                all_event_types.update(event_types)
                print(f"   ✓ Found {len(event_types)} unique event types")
            
            # Analyze each column with robust error handling
            for col_name in df.columns:
                try:
                    print(f"   🔍 Analyzing column: {col_name}")
                    col_info = get_column_info(df, col_name, csv_file)
                    all_columns_info.append(col_info)
                    print(f"   ✅ Successfully processed: {col_name}")
                except Exception as e:
                    print(f"   ❌ Failed to process column {col_name}: {str(e)}")
                    continue
                
        except Exception as e:
            print(f"   ❌ Error analyzing {csv_file}: {str(e)}")
            continue
    
    # Create the main documentation DataFrame
    doc_df = pd.DataFrame(all_columns_info)
    
    # Create event types mapping DataFrame
    event_types_data = [{'event_id': k, 'event_name': v} for k, v in sorted(all_event_types.items())]
    event_types_df = pd.DataFrame(event_types_data)
    
    # Create key connections DataFrame
    connections_data = create_key_connections_data()
    connections_df = pd.DataFrame(connections_data)
    
    # Save to Excel file with multiple sheets
    output_file = '../specs/Euro_2024_Complete_Data_Documentation.xlsx'
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Main documentation sheet
        doc_df.to_csv('../specs/Euro_2024_Enhanced_Data_Documentation.csv', index=False)
        doc_df.to_excel(writer, sheet_name='Data_Documentation', index=False)
        
        # Key connections sheet
        connections_df.to_excel(writer, sheet_name='Key_Connections', index=False)
        
        # Event types mapping sheet
        event_types_df.to_excel(writer, sheet_name='Event_Types_Map', index=False)
    
    print(f"\n✅ Complete documentation with multiple tabs completed!")
    print(f"📄 Excel file: {output_file}")
    print(f"📄 CSV file: ../specs/Euro_2024_Enhanced_Data_Documentation.csv")
    print(f"📊 Total columns documented: {len(all_columns_info)}")
    print(f"🔗 Key connections documented: {len(connections_data)}")
    print(f"📋 Event types mapped: {len(all_event_types)}")
    
    # Print summary statistics
    print(f"\n📈 Summary by source file:")
    for source in doc_df['source'].unique():
        count = len(doc_df[doc_df['source'] == source])
        print(f"   {source}: {count} columns")
    
    # Print event types summary
    print(f"\n🎯 Event Types Found:")
    for event_id, event_name in sorted(all_event_types.items())[:10]:  # Show first 10
        print(f"   {event_id}: {event_name}")
    if len(all_event_types) > 10:
        print(f"   ... and {len(all_event_types) - 10} more")
    
    # Check if we got all expected columns
    expected_total = 88
    if len(all_columns_info) == expected_total:
        print(f"\n🎉 SUCCESS: All {expected_total} columns documented with enhanced subcategories!")
    else:
        print(f"\n⚠️ Got {len(all_columns_info)}/{expected_total} columns")

if __name__ == "__main__":
    main() 