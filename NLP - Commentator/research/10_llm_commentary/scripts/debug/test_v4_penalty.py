"""
V4 Penalty Test - Specific Minutes Only

Test Cases:
1. Portugal vs France (3942349) - ALL Period 5 (Penalty Shootout)
2. Germany vs Scotland (3930158) - Minutes 45-47, Period 1 (Stoppage time)
3. Georgia vs Portugal (3938644) - Minutes 56-58, Period 2
4. Portugal vs Slovenia (3941020) - Minute 104 to end of Period 3 (Extra time)
"""

import os
import sys
import ast
import pandas as pd
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gpt_commentator_v4 import GPTCommentator
from run_final_test_v4 import (
    detect_all_important_events_v4,
    extract_event_specific_data_v4,
    extract_shot_type,
    extract_shot_outcome,
)

# Paths
SCRIPT_DIR = Path(__file__).parent
PHASE7_DATA = SCRIPT_DIR.parent.parent / "07_all_games_commentary" / "data"
COMPLETE_DATA = Path("C:/Users/yonatanam/Desktop/Euro 2024 - momentum - DS-AI project/Data/euro_2024_complete_dataset.csv")
OUTPUT_DIR = SCRIPT_DIR.parent / "data" / "llm_commentary"

# Test cases
TEST_CASES = [
    {
        'match_id': 3942349,
        'home_team': 'Portugal',
        'away_team': 'France',
        'stage': 'Quarter-finals',
        'description': 'Portugal vs France - Period 5 (Penalty Shootout)',
        'filter': lambda df: df[df['period'] == 5]
    },
    {
        'match_id': 3930158,
        'home_team': 'Germany',
        'away_team': 'Scotland',
        'stage': 'Group Stage',
        'description': 'Germany vs Scotland - Minutes 45-47, Period 1 (Stoppage)',
        'filter': lambda df: df[(df['minute'] >= 45) & (df['minute'] <= 47) & (df['period'] == 1)]
    },
    {
        'match_id': 3938644,
        'home_team': 'Georgia',
        'away_team': 'Portugal',
        'stage': 'Group Stage',
        'description': 'Georgia vs Portugal - Minutes 56-58, Period 2',
        'filter': lambda df: df[(df['minute'] >= 56) & (df['minute'] <= 58) & (df['period'] == 2)]
    },
    {
        'match_id': 3941020,
        'home_team': 'Portugal',
        'away_team': 'Slovenia',
        'stage': 'Round of 16',
        'description': 'Portugal vs Slovenia - Minute 104+ Period 3 (Extra Time)',
        'filter': lambda df: df[(df['minute'] >= 104) & (df['period'] == 3)]
    },
]


def load_match_data(match_id, complete_df):
    """Load and merge match data."""
    csv_file = PHASE7_DATA / f"match_{match_id}_rich_commentary.csv"
    
    if not csv_file.exists():
        print(f"  [WARN] File not found: {csv_file}")
        return None
    
    df = pd.read_csv(csv_file)
    
    # Merge columns from complete dataset
    match_complete = complete_df[complete_df['match_id'] == match_id].copy().reset_index(drop=True)
    
    if len(df) == len(match_complete):
        df['foul_committed'] = match_complete['foul_committed'].values
        df['bad_behaviour'] = match_complete['bad_behaviour'].values
        df['shot'] = match_complete['shot'].values
        df['goalkeeper'] = match_complete['goalkeeper'].values
    
    return df


def main():
    print("=" * 70)
    print("V4 PENALTY TEST - Specific Minutes Only")
    print("=" * 70)
    
    # Load complete dataset once
    print("\n[LOAD] Loading complete dataset...")
    complete_df = pd.read_csv(COMPLETE_DATA, low_memory=False)
    print(f"[OK] Loaded {len(complete_df)} events")
    
    # Initialize commentator
    print("\n[GPT] Initializing GPT Commentator V4...")
    commentator = GPTCommentator()
    print(f"[OK] Model: {commentator.model}")
    
    all_results = []
    
    # Process each test case
    for i, test in enumerate(TEST_CASES):
        print(f"\n{'='*70}")
        print(f"TEST {i+1}: {test['description']}")
        print(f"{'='*70}")
        
        # Load match data
        df = load_match_data(test['match_id'], complete_df)
        if df is None:
            continue
        
        # Filter to specific minutes
        filtered_df = test['filter'](df)
        print(f"[INFO] Total events in filter: {len(filtered_df)}")
        print(f"[INFO] Periods: {sorted(filtered_df['period'].unique())}")
        print(f"[INFO] Minutes: {sorted(filtered_df['minute'].unique())}")
        
        # Check for penalties in data
        penalty_shots = 0
        for idx, row in filtered_df.iterrows():
            shot_type = extract_shot_type(row.get('shot', ''))
            if shot_type == 'Penalty':
                penalty_shots += 1
        print(f"[INFO] Penalty shots found: {penalty_shots}")
        
        # Reset shootout trackers
        from run_final_test_v4 import shootout_score, penalty_count
        import run_final_test_v4
        run_final_test_v4.shootout_score = {'home': 0, 'away': 0}
        run_final_test_v4.penalty_count = 0
        
        # Group by minute/period
        minute_periods = filtered_df.groupby(['minute', 'period']).size().reset_index()[['minute', 'period']]
        minute_periods = minute_periods.sort_values(['period', 'minute'])
        
        print(f"\n[PROCESS] {len(minute_periods)} minute-period combinations")
        print("-" * 70)
        
        for _, mp_row in minute_periods.iterrows():
            minute = mp_row['minute']
            period = mp_row['period']
            
            minute_df = filtered_df[(filtered_df['minute'] == minute) & (filtered_df['period'] == period)].copy()
            
            detection_info = {
                'stage': test['stage'],
                'period': period
            }
            
            # Detect events
            events = detect_all_important_events_v4(
                minute_df, detection_info, 
                test['home_team'], test['away_team']
            )
            
            for detected_type, main_row, extra_info in events:
                # Extract event data
                event_data = extract_event_specific_data_v4(
                    detected_type, main_row, minute_df, extra_info,
                    test['home_team'], test['away_team']
                )
                
                # Build context
                context = {
                    'home_team': test['home_team'],
                    'away_team': test['away_team'],
                    'home_score': 0,
                    'away_score': 0,
                    'stage': test['stage'],
                    'period': period,
                    'detected_type': detected_type,
                    'event_data': event_data,
                }
                
                # Generate commentary
                llm_commentary = commentator.generate_minute_commentary(
                    minute=int(minute),
                    events_data=[],
                    match_context=context
                )
                
                # Display
                period_label = f"P{period}" if period >= 3 else ""
                player = event_data.get('player', '')
                
                print(f"\nMinute {minute}' {period_label}")
                print(f"  Type: [{detected_type}]")
                print(f"  Player: {player}")
                
                if period == 5:
                    ss = event_data.get('shootout_score', {})
                    pn = event_data.get('penalty_number', 0)
                    print(f"  Penalty #{pn} | Shootout: {test['home_team']} {ss.get('home',0)} - {ss.get('away',0)} {test['away_team']}")
                
                safe_comm = llm_commentary.encode('ascii', 'replace').decode('ascii')
                print(f"  LLM: {safe_comm}")
                
                # Save result
                all_results.append({
                    'test_case': test['description'],
                    'match_id': test['match_id'],
                    'minute': minute,
                    'period': period,
                    'detected_type': detected_type,
                    'player': player,
                    'llm_commentary': llm_commentary,
                    'is_penalty': 'Penalty' in detected_type,
                    'penalty_number': event_data.get('penalty_number', 0),
                })
    
    # Save results
    if all_results:
        results_df = pd.DataFrame(all_results)
        output_file = OUTPUT_DIR / f"V4_penalty_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        results_df.to_csv(output_file, index=False)
        
        print(f"\n{'='*70}")
        print(f"TEST COMPLETE!")
        print(f"{'='*70}")
        print(f"Total commentaries: {len(all_results)}")
        print(f"Penalties detected: {len([r for r in all_results if r['is_penalty']])}")
        print(f"Output: {output_file}")
        
        # Summary by type
        print(f"\n[EVENT BREAKDOWN]")
        print(results_df['detected_type'].value_counts().to_string())


if __name__ == "__main__":
    main()

