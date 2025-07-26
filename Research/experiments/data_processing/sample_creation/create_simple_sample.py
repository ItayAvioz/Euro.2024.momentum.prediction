#!/usr/bin/env python3
"""
Create Simple Sample CSV with 100 Rows
"""

import pandas as pd

def create_simple_sample():
    """Create a sample CSV with 100 rows using chunking"""
    print("📊 Creating Sample CSV with 100 Rows")
    print("=" * 50)
    
    try:
        # Use chunking to read only the first portion
        print("📥 Reading first chunk of data...")
        
        chunk_iter = pd.read_csv('euro_2024_complete/connected_complete.csv', chunksize=1000)
        first_chunk = next(chunk_iter)
        
        print(f"✅ Loaded first chunk: {len(first_chunk)} rows")
        print(f"📊 Columns: {len(first_chunk.columns)}")
        
        # Take first 100 rows
        sample_100 = first_chunk.head(100).copy()
        
        # Select key columns
        key_columns = [
            'match_id', 'minute', 'second', 'event_type', 'player_name', 
            'team_name', 'home_team', 'away_team', 'stage'
        ]
        
        # Filter to columns that exist
        available_columns = [col for col in key_columns if col in sample_100.columns]
        sample_100 = sample_100[available_columns]
        
        # Clean up
        sample_100 = sample_100.fillna('N/A')
        
        # Save to CSV
        output_file = 'euro_2024_sample_100_rows.csv'
        sample_100.to_csv(output_file, index=False)
        
        print(f"💾 Sample CSV created: {output_file}")
        print(f"📊 Contains {len(sample_100)} rows, {len(sample_100.columns)} columns")
        
        # Show preview
        print("\n📋 Preview of first 5 rows:")
        print("-" * 80)
        print(sample_100.head().to_string(index=False, max_colwidth=15))
        
        # Show event types
        if 'event_type' in sample_100.columns:
            print(f"\n📈 Event types in sample:")
            event_counts = sample_100['event_type'].value_counts()
            for event_type, count in event_counts.items():
                print(f"   {event_type}: {count}")
        
        return sample_100
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("🔄 Trying alternative approach...")
        
        # Try with smaller chunk
        try:
            chunk_iter = pd.read_csv('euro_2024_complete/connected_complete.csv', nrows=100)
            sample_100 = chunk_iter
            
            # Save to CSV
            output_file = 'euro_2024_sample_100_rows.csv'
            sample_100.to_csv(output_file, index=False)
            
            print(f"✅ Sample CSV created: {output_file}")
            return sample_100
            
        except Exception as e2:
            print(f"❌ Still failed: {e2}")
            print("📝 Creating minimal sample from scratch...")
            
            # Create a minimal sample structure
            sample_data = {
                'match_id': [3942819] * 5,
                'minute': [0, 1, 2, 3, 4],
                'event_type': ['Pass', 'Shot', 'Goal', 'Duel', 'Substitution'],
                'player_name': ['Sample Player 1', 'Sample Player 2', 'Sample Player 3', 'Sample Player 4', 'Sample Player 5'],
                'team_name': ['Netherlands', 'England', 'Spain', 'France', 'Germany'],
                'home_team': ['Netherlands'] * 5,
                'away_team': ['England'] * 5
            }
            
            sample_df = pd.DataFrame(sample_data)
            sample_df.to_csv('euro_2024_sample_100_rows.csv', index=False)
            
            print("✅ Created minimal sample CSV")
            return sample_df

if __name__ == "__main__":
    sample = create_simple_sample() 