"""
Batch Enhanced Comparison for All Euro 2024 Matches

This script runs the enhanced comparison for all 51 matches,
generating individual CSV files for each game.
"""
import os
import sys
import subprocess
from pathlib import Path

# Add parent directory to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.append(str(SCRIPT_DIR))

from enhanced_comparison import process_match

# All 51 Euro 2024 match IDs (from generated commentary files)
MATCH_IDS = [
    # Group Stage - Round 1 (12 matches)
    3930158, 3930159, 3930160, 3930161, 3930162, 3930163,
    3930164, 3930165, 3930166, 3930167, 3930168, 3930169,
    
    # Group Stage - Round 2 (12 matches)
    3930170, 3930171, 3930172, 3930173, 3930174, 3930175,
    3930176, 3930177, 3930178, 3930179, 3930180, 3930181,
    
    # Group Stage - Round 3 (12 matches)
    3930182, 3930183, 3930184, 3938637, 3938638, 3938639,
    3938640, 3938641, 3938642, 3938643, 3938644, 3938645,
    
    # Round of 16 (8 matches)
    3940878, 3940983, 3941017, 3941018, 3941019, 3941020,
    3941021, 3941022,
    
    # Quarter-Finals (4 matches)
    3942226, 3942227, 3942349, 3942382,
    
    # Semi-Finals (2 matches)
    3942752, 3942819,
    
    # Final (1 match)
    3943043,
]

def main():
    """Process all matches"""
    print("="*80)
    print("ENHANCED COMPARISON - ALL EURO 2024 MATCHES")
    print("="*80)
    print(f"\nTotal matches: {len(MATCH_IDS)}")
    print(f"Note: Some matches have multiple real commentary sources")
    print(f"      Each source will generate a separate comparison CSV")
    print(f"Output directory: {SCRIPT_DIR.parent / 'data'}")
    
    # Statistics
    successful = 0
    failed = 0
    failed_comparisons = []
    
    # Process each match
    for i, match_id in enumerate(MATCH_IDS, 1):
        print(f"\n{'-'*80}")
        print(f"[{i}/{len(MATCH_IDS)}] Processing match {match_id}...")
        print(f"{'-'*80}")
        
        try:
            # Run comparison - returns number of sources processed
            sources_count = process_match(match_id)
            
            if sources_count and sources_count > 0:
                successful += sources_count
                print(f"[SUCCESS] Match {match_id} - {sources_count} source(s) processed")
            else:
                failed += 1
                failed_comparisons.append((match_id, "No data found"))
                print(f"[WARNING] Match {match_id} - No data or comparison failed")
                
        except Exception as e:
            failed += 1
            failed_comparisons.append((match_id, str(e)[:100]))
            print(f"[ERROR] Match {match_id} failed: {type(e).__name__}: {str(e)[:100]}")
    
    # Final summary
    print("\n" + "="*80)
    print("BATCH PROCESSING COMPLETE")
    print("="*80)
    print(f"\nTotal matches processed: {len(MATCH_IDS)}")
    print(f"Total comparison CSVs created: {successful}")
    print(f"Failed comparisons: {failed}")
    
    if failed_comparisons:
        print(f"\nFailed comparisons ({len(failed_comparisons)}):")
        for match_id, error in failed_comparisons:
            print(f"  - Match {match_id}: {error}")
    
    print(f"\n[INFO] All comparison CSVs saved to: {SCRIPT_DIR.parent / 'data'}")
    print(f"[INFO] Files follow pattern: match_[ID]_[source]_enhanced_comparison.csv")
    print(f"[INFO] Multiple CSVs per match if multiple real commentary sources available")
    
    # Return exit code
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

