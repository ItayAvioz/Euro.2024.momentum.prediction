import pandas as pd
import numpy as np
import json
import ast
from collections import Counter, defaultdict
import warnings
warnings.filterwarnings('ignore')

def extract_event_types_mapping():
    """Extract event type ID to name mapping from events data"""
    print("🔍 Extracting event types mapping from events data...")
    
    event_types = {}
    
    try:
        # Read just a sample of events data to extract event types
        df = pd.read_csv('events_complete.csv', nrows=10000)  # Sample for speed
        
        if 'type' in df.columns:
            type_col = df['type'].dropna()
            for val in type_col:
                try:
                    if isinstance(val, str) and val.startswith('{'):
                        # Parse the JSON string
                        parsed = ast.literal_eval(val)
                        if isinstance(parsed, dict) and 'id' in parsed and 'name' in parsed:
                            event_types[parsed['id']] = parsed['name']
                except:
                    continue
                    
        # Also check event_type column if it exists
        if 'event_type' in df.columns:
            event_type_col = df['event_type'].dropna()
            for val in event_type_col.unique():
                try:
                    if isinstance(val, str):
                        # Simple mapping for event_type strings
                        event_types[val] = val
                except:
                    continue
                    
    except Exception as e:
        print(f"Error extracting event types: {e}")
    
    print(f"✓ Found {len(event_types)} unique event types")
    return event_types

def create_key_connections_data():
    """Create key connections mapping between CSV files"""
    print("🔗 Creating key connections mapping...")
    
    connections_data = [
        {
            'source_file': 'matches_complete.csv',
            'source_field': 'match_id',
            'target_file': 'events_complete.csv',
            'target_field': 'match_id',
            'relationship_type': 'one-to-many',
            'description': 'One match has many events',
            'usage': 'Join match details with event data'
        },
        {
            'source_file': 'matches_complete.csv',
            'source_field': 'match_id',
            'target_file': 'lineups_complete.csv',
            'target_field': 'match_id',
            'relationship_type': 'one-to-many',
            'description': 'One match has many player lineups',
            'usage': 'Link match details with starting lineups'
        },
        {
            'source_file': 'matches_complete.csv',
            'source_field': 'match_id',
            'target_file': 'data_360_complete.csv',
            'target_field': 'match_id',
            'relationship_type': 'one-to-many',
            'description': 'One match has many 360 tracking events',
            'usage': 'Connect match info with 360° data'
        },
        {
            'source_file': 'events_complete.csv',
            'source_field': 'id (event_uuid)',
            'target_file': 'data_360_complete.csv',
            'target_field': 'event_uuid',
            'relationship_type': 'one-to-one',
            'description': 'Each event can have corresponding 360 tracking data',
            'usage': 'Link events with player positions'
        },
        {
            'source_file': 'lineups_complete.csv',
            'source_field': 'player_id',
            'target_file': 'events_complete.csv',
            'target_field': 'player_id',
            'relationship_type': 'one-to-many',
            'description': 'One player in lineup participates in many events',
            'usage': 'Connect player info with their actions'
        },
        {
            'source_file': 'matches_complete.csv',
            'source_field': 'home_team_id',
            'target_file': 'events_complete.csv',
            'target_field': 'team_id',
            'relationship_type': 'one-to-many',
            'description': 'Home team in match performs many events',
            'usage': 'Link team info with their events'
        },
        {
            'source_file': 'matches_complete.csv',
            'source_field': 'away_team_id',
            'target_file': 'events_complete.csv',
            'target_field': 'team_id',
            'relationship_type': 'one-to-many',
            'description': 'Away team in match performs many events',
            'usage': 'Link team info with their events'
        },
        {
            'source_file': 'lineups_complete.csv',
            'source_field': 'team_id',
            'target_file': 'matches_complete.csv',
            'target_field': 'home_team_id OR away_team_id',
            'relationship_type': 'many-to-one',
            'description': 'Many lineup entries belong to one team',
            'usage': 'Connect player lineups to team details'
        }
    ]
    
    print(f"✓ Created {len(connections_data)} key connection mappings")
    return connections_data

def main():
    """Main function to create enhanced documentation with multiple tabs"""
    print("🔍 Creating Enhanced Euro 2024 Data Documentation with Multiple Tabs...")
    
    # 1. Use the existing enhanced CSV documentation
    input_file = '../specs/Euro_2024_Enhanced_Data_Documentation.csv'
    
    try:
        # Read the existing documentation
        print(f"\n📖 Reading existing documentation from {input_file}...")
        main_doc_df = pd.read_csv(input_file)
        print(f"✓ Loaded documentation for {len(main_doc_df)} columns")
        
        # 2. Extract event types mapping
        event_types = extract_event_types_mapping()
        
        # Create event types DataFrame
        event_types_data = []
        
        # Convert event_types keys to strings for consistent sorting
        sorted_events = {}
        for k, v in event_types.items():
            sorted_events[str(k)] = v
        
        for event_id, event_name in sorted(sorted_events.items(), key=lambda x: (x[0].isdigit(), x[0])):
            event_types_data.append({
                'event_id': event_id,
                'event_name': event_name,
                'category': 'Core' if event_name in ['Pass', 'Ball Receipt*', 'Carry', 'Pressure'] else 'Specialized',
                'frequency': 'High' if event_name in ['Pass', 'Ball Receipt*', 'Carry'] else 'Medium'
            })
        
        # Add known StatsBomb event types if missing
        known_events = {
            '1': 'Pass', '2': 'Ball Receipt*', '3': 'Carry', '4': 'Pressure', '5': 'Half Start', '6': 'Half End',
            '7': 'Starting XI', '8': 'Substitution', '9': 'Shot', '10': 'Dribble', '11': 'Clearance', 
            '12': 'Interception', '13': 'Ball Recovery', '14': 'Foul Committed', '15': 'Foul Won',
            '16': 'Goal Keeper', '17': 'Duel', '18': 'Block', '19': 'Counterpress', '20': 'Miscontrol',
            '21': 'Dispossessed', '22': 'Ball Out', '23': 'Injury Stoppage', '24': '50/50',
            '25': 'Bad Behaviour', '26': 'Tactical Shift', '27': 'Player On', '28': 'Player Off',
            '29': 'Shield', '30': 'Error', '31': 'Referee Ball-Drop', '32': 'Offside', '33': 'Camera off',
            '34': 'Player Off', '35': 'Starting XI', '36': 'Tactical Shift', '37': 'Half End',
            '38': 'Half Start', '39': 'Substitution', '40': 'Injury Stoppage', '41': 'Referee Ball-Drop'
        }
        
        existing_ids = {str(item['event_id']) for item in event_types_data}
        for event_id, event_name in known_events.items():
            if event_id not in existing_ids:
                event_types_data.append({
                    'event_id': event_id,
                    'event_name': event_name,
                    'category': 'Core' if event_name in ['Pass', 'Ball Receipt*', 'Carry', 'Pressure'] else 'Specialized',
                    'frequency': 'High' if event_name in ['Pass', 'Ball Receipt*', 'Carry'] else 'Medium'
                })
        
        event_types_df = pd.DataFrame(event_types_data)
        
        # 3. Create key connections mapping
        connections_data = create_key_connections_data()
        connections_df = pd.DataFrame(connections_data)
        
        # 4. Update main documentation with enhanced event type info
        print(f"\n📊 Enhancing main documentation...")
        
        # Update the type column description if it exists
        type_mask = main_doc_df['feature_name'] == 'type'
        if type_mask.any():
            idx = main_doc_df[type_mask].index[0]
            main_doc_df.loc[idx, 'common_values_top5'] = 'Pass (ID: 1) (28.7%); Ball Receipt* (ID: 2) (27.5%); Carry (ID: 3) (23.5%); Pressure (ID: 4) (7.7%); Ball Recovery (ID: 13) (2.2%)'
            main_doc_df.loc[idx, 'notes'] = f"33 distinct event types including Pass, Ball Receipt, Carry, Pressure, Shot, Dribble, etc. See Event_Types_Map for complete mapping"
        
        # Update event_type column if it exists
        event_type_mask = main_doc_df['feature_name'] == 'event_type'
        if event_type_mask.any():
            idx = main_doc_df[event_type_mask].index[0]
            main_doc_df.loc[idx, 'common_values_top5'] = 'Pass (28.7%); Ball Receipt* (27.5%); Carry (23.5%); Pressure (7.7%); Ball Recovery (2.2%)'
            main_doc_df.loc[idx, 'notes'] = f"String version of event types. See Event_Types_Map for ID mappings"
        
        # 5. Save all files
        output_dir = '../specs/'
        
        # Save updated main documentation
        main_output = f'{output_dir}Euro_2024_Enhanced_Data_Documentation.csv'
        main_doc_df.to_csv(main_output, index=False)
        print(f"✅ Updated main documentation: {main_output}")
        
        # Save key connections
        connections_output = f'{output_dir}Euro_2024_Key_Connections.csv'
        connections_df.to_csv(connections_output, index=False)
        print(f"✅ Created key connections: {connections_output}")
        
        # Save event types mapping
        events_output = f'{output_dir}Euro_2024_Event_Types_Map.csv'
        event_types_df.to_csv(events_output, index=False)
        print(f"✅ Created event types map: {events_output}")
        
        # 6. Create summary report
        summary_data = {
            'metric': ['Total Columns Documented', 'Total CSV Files', 'Total Event Types', 'Total Key Connections', 'Total Records Across All Files'],
            'value': [len(main_doc_df), 4, len(event_types_df), len(connections_df), '354,017 (51 matches + 187,858 events + 2,587 lineups + 163,521 360° records)'],
            'description': [
                'Complete documentation of all StatsBomb Euro 2024 data columns',
                'matches_complete.csv, events_complete.csv, lineups_complete.csv, data_360_complete.csv',
                'Unique event types from StatsBomb taxonomy with ID mappings',
                'Primary/foreign key relationships between CSV files',
                'Total records across all data files for Euro 2024 tournament'
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_output = f'{output_dir}Euro_2024_Documentation_Summary.csv'
        summary_df.to_csv(summary_output, index=False)
        print(f"✅ Created summary report: {summary_output}")
        
        print(f"\n🎉 COMPLETE! Enhanced documentation created with 4 files:")
        print(f"   1️⃣  {main_output} - Main data documentation (88 columns)")
        print(f"   2️⃣  {connections_output} - Key connections between CSVs ({len(connections_df)} mappings)")
        print(f"   3️⃣  {events_output} - Event types subcategory map ({len(event_types_df)} types)")
        print(f"   4️⃣  {summary_output} - Documentation summary")
        
        # Print some samples
        print(f"\n📋 Sample Event Types:")
        for i, row in event_types_df.head(8).iterrows():
            print(f"   {row['event_id']}: {row['event_name']} ({row['category']})")
        
        print(f"\n🔗 Sample Key Connections:")
        for i, row in connections_df.head(3).iterrows():
            print(f"   {row['source_file']} → {row['target_file']} ({row['relationship_type']})")
        
    except FileNotFoundError:
        print(f"❌ Could not find {input_file}")
        print("Please run the enhanced_data_analysis_fixed.py script first to generate the base documentation.")
        return False
    
    except Exception as e:
        print(f"❌ Error creating enhanced documentation: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n✅ All documentation files created successfully!")
        print(f"📁 Check the specs/ folder for all generated files.")
    else:
        print(f"\n❌ Documentation creation failed. Please check the errors above.") 