"""
Generate Commentary for ALL Euro 2024 Matches - Batch Processing
=================================================================
Runs extraction + commentary generation for all 51 matches.

Usage:
    python generate_all_matches.py
"""

import pandas as pd
import os
import sys
import subprocess
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR))))
DATA_DIR = os.path.join(PROJECT_ROOT, 'Data')

def get_all_matches():
    """Load all Euro 2024 matches"""
    matches_path = os.path.join(DATA_DIR, 'matches_complete.csv')
    df = pd.read_csv(matches_path)
    
    # Sort by date for chronological processing
    df['match_date'] = pd.to_datetime(df['match_date'])
    df = df.sort_values('match_date')
    
    return df

def run_extraction(match_id):
    """Run extraction script for one match"""
    script_path = os.path.join(SCRIPT_DIR, 'extract_match_data.py')
    result = subprocess.run(
        [sys.executable, script_path, str(match_id)],
        capture_output=True,
        text=True
    )
    return result.returncode == 0, result.stdout, result.stderr

def run_commentary(match_id):
    """Run commentary generation for one match"""
    script_path = os.path.join(SCRIPT_DIR, 'generate_match_commentary.py')
    result = subprocess.run(
        [sys.executable, script_path, str(match_id)],
        capture_output=True,
        text=True
    )
    return result.returncode == 0, result.stdout, result.stderr

def main():
    """Main batch processing"""
    start_time = datetime.now()
    
    print("="*80)
    print("PHASE 2: GENERATE COMMENTARY FOR ALL EURO 2024 MATCHES")
    print("="*80)
    print()
    
    # Load matches
    print("Loading match data...")
    matches_df = get_all_matches()
    total_matches = len(matches_df)
    
    print(f"Found {total_matches} Euro 2024 matches")
    print()
    
    # Track results
    results = []
    successful = 0
    failed = 0
    
    # Process each match
    for idx, (_, match) in enumerate(matches_df.iterrows(), 1):
        match_id = match['match_id']
        home_team = match['home_team_name']
        away_team = match['away_team_name']
        score = f"{match['home_score']}-{match['away_score']}"
        
        print(f"[{idx}/{total_matches}] {home_team} vs {away_team} ({score})")
        print(f"  Match ID: {match_id}")
        
        # Step 1: Extract data
        print(f"  Step 1/2: Extracting data...", end=" ")
        extract_success, extract_out, extract_err = run_extraction(match_id)
        
        if not extract_success:
            print("FAILED!")
            print(f"  Error: {extract_err[:200]}")
            failed += 1
            results.append({
                'match_id': match_id,
                'match': f"{home_team} vs {away_team}",
                'status': 'FAILED - Extraction',
                'error': extract_err[:200]
            })
            continue
        
        print("OK")
        
        # Step 2: Generate commentary
        print(f"  Step 2/2: Generating commentary...", end=" ")
        comment_success, comment_out, comment_err = run_commentary(match_id)
        
        if not comment_success:
            print("FAILED!")
            print(f"  Error: {comment_err[:200]}")
            failed += 1
            results.append({
                'match_id': match_id,
                'match': f"{home_team} vs {away_team}",
                'status': 'FAILED - Commentary',
                'error': comment_err[:200]
            })
            continue
        
        print("OK")
        print(f"  Status: SUCCESS")
        print()
        
        successful += 1
        results.append({
            'match_id': match_id,
            'match': f"{home_team} vs {away_team}",
            'status': 'SUCCESS',
            'error': None
        })
    
    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("="*80)
    print("BATCH PROCESSING COMPLETE")
    print("="*80)
    print(f"Total matches: {total_matches}")
    print(f"Successful: {successful} ({successful/total_matches*100:.1f}%)")
    print(f"Failed: {failed} ({failed/total_matches*100:.1f}%)")
    print(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    print(f"Average: {duration/total_matches:.1f} seconds per match")
    print()
    
    # Save results
    results_df = pd.DataFrame(results)
    results_file = os.path.join(SCRIPT_DIR, '..', 'data', 'batch_processing_results.csv')
    results_df.to_csv(results_file, index=False)
    print(f"Results saved to: {results_file}")
    
    # Show failures if any
    if failed > 0:
        print()
        print("FAILED MATCHES:")
        print("-"*80)
        for r in results:
            if r['status'] != 'SUCCESS':
                print(f"  {r['match']} (ID: {r['match_id']})")
                print(f"    Error: {r['error']}")
    
    print()
    print("="*80)
    
    if successful == total_matches:
        print("ALL MATCHES PROCESSED SUCCESSFULLY!")
    else:
        print(f"COMPLETED WITH {failed} ERRORS")
    
    print("="*80)

if __name__ == "__main__":
    main()

