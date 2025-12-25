"""
Batch Commentary Generation with Full Output Tracking

Generates LLM commentary and saves all inputs/outputs for comparison.

Author: AI Assistant
Date: November 24, 2025
"""

import os
import sys
import argparse
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import LLM_COMMENTARY_DIR
from gpt_commentator import GPTCommentator


# =====================================
# DATA PATHS
# =====================================
SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent
PHASE7_DATA = BASE_DIR.parent / "07_all_games_commentary" / "data"
PHASE8_DATA = BASE_DIR.parent / "08_enhanced_comparison" / "data"


def load_match_data(match_id: int) -> Optional[pd.DataFrame]:
    """
    Load event data for a specific match from Phase 7.
    
    Args:
        match_id: Match ID to load
        
    Returns:
        DataFrame with match events or None if not found
    """
    # Try rich commentary file first
    rich_file = PHASE7_DATA / f"match_{match_id}_rich_commentary.csv"
    if rich_file.exists():
        print(f"✅ Loading from: {rich_file}")
        return pd.read_csv(rich_file)
    
    # Try detailed file
    detailed_file = PHASE7_DATA / f"match_{match_id}_detailed_commentary_data.csv"
    if detailed_file.exists():
        print(f"✅ Loading from: {detailed_file}")
        return pd.read_csv(detailed_file)
    
    print(f"❌ No data found for match {match_id}")
    return None


def load_real_commentary(match_id: int, source: str = 'espn') -> Optional[pd.DataFrame]:
    """
    Load real commentary for comparison from Phase 8.
    
    Args:
        match_id: Match ID
        source: Commentary source (espn, bbc, flashscore, etc.)
        
    Returns:
        DataFrame with real commentary or None
    """
    comparison_file = PHASE8_DATA / f"match_{match_id}_{source}_enhanced_comparison.csv"
    if comparison_file.exists():
        print(f"✅ Loading real commentary from: {comparison_file}")
        return pd.read_csv(comparison_file)
    
    # Try any available source
    for file in PHASE8_DATA.glob(f"match_{match_id}_*_enhanced_comparison.csv"):
        print(f"✅ Loading real commentary from: {file}")
        return pd.read_csv(file)
    
    print(f"⚠️ No real commentary found for match {match_id}")
    return None


def group_events_by_minute(df: pd.DataFrame) -> Dict[int, Dict]:
    """
    Group events by minute for processing.
    
    Args:
        df: DataFrame with event data
        
    Returns:
        Dict mapping minute -> {events, rule_based, sequence, scores}
    """
    minutes_data = {}
    
    for minute in df['minute'].unique():
        minute_df = df[df['minute'] == minute].copy()
        
        # Extract events
        events = []
        for _, row in minute_df.iterrows():
            event = {
                'event_type': row.get('event_type', 'Unknown'),
                'player_name': row.get('player_name', ''),
                'team_name': row.get('team_name', ''),
                'shot_outcome': row.get('shot_outcome', ''),
                'pass_recipient': row.get('pass_recipient', ''),
                'body_part': row.get('shot_body_part', row.get('body_part', '')),
                'location_x': row.get('location_x', ''),
                'location_y': row.get('location_y', ''),
                'under_pressure': row.get('under_pressure', False),
            }
            events.append(event)
        
        # Get commentary from last event in minute (usually has the full sequence)
        last_row = minute_df.iloc[-1]
        
        minutes_data[int(minute)] = {
            'events': events,
            'event_types': list(minute_df['event_type'].unique()),
            'rule_based': str(last_row.get('event_commentary', '')),
            'sequence': str(last_row.get('sequence_commentary', '')),
            'sequence_id': last_row.get('sequence_id', -1),
            'home_score': last_row.get('spain_score', last_row.get('home_score', 0)),
            'away_score': last_row.get('england_score', last_row.get('away_score', 0)),
            'period': last_row.get('period', 1),
        }
    
    return minutes_data


def generate_match_commentary(
    match_id: int,
    home_team: str = 'Home',
    away_team: str = 'Away',
    stage: str = 'Match',
    max_minutes: int = None,
    save_detailed: bool = True
) -> Optional[pd.DataFrame]:
    """
    Generate LLM commentary for a match and save full tracking data.
    
    Args:
        match_id: Match ID to process
        home_team: Home team name
        away_team: Away team name
        stage: Match stage (Group, Final, etc.)
        max_minutes: Optional limit on minutes to process
        save_detailed: Whether to save detailed tracking file
        
    Returns:
        DataFrame with results
    """
    print(f"\n{'='*60}")
    print(f"Generating LLM Commentary - Match {match_id}")
    print(f"{'='*60}")
    
    # Load match data
    df = load_match_data(match_id)
    if df is None:
        return None
    
    print(f"📊 Total events: {len(df)}")
    print(f"📊 Minutes covered: {df['minute'].min()} - {df['minute'].max()}")
    
    # Group by minute
    minutes_data = group_events_by_minute(df)
    print(f"📊 Unique minutes: {len(minutes_data)}")
    
    # Limit minutes if requested
    if max_minutes:
        minutes_data = dict(list(sorted(minutes_data.items()))[:max_minutes])
        print(f"📊 Limited to {max_minutes} minutes")
    
    # Initialize commentator
    try:
        commentator = GPTCommentator()
        print(f"✅ GPT Commentator initialized (model: {commentator.model})")
    except ValueError as e:
        print(f"❌ Error: {e}")
        return None
    
    # Generate commentary for each minute
    results = []
    total = len(minutes_data)
    
    print(f"\n📝 Generating commentary for {total} minutes...")
    
    for i, (minute, data) in enumerate(sorted(minutes_data.items())):
        # Match context
        context = {
            'home_team': home_team,
            'away_team': away_team,
            'home_score': data['home_score'],
            'away_score': data['away_score'],
            'stage': stage,
            'period': data['period'],
        }
        
        # Generate LLM commentary
        llm_commentary = commentator.generate_minute_commentary(
            minute=minute,
            events_data=data['events'],
            rule_based_commentary=data['rule_based'],
            sequence_commentary=data['sequence'],
            match_context=context
        )
        
        # Build result row with full tracking
        result = {
            # Identifiers
            'match_id': match_id,
            'minute': minute,
            'period': data['period'],
            'sequence_id': data['sequence_id'],
            
            # Match context
            'home_team': home_team,
            'away_team': away_team,
            'home_score': data['home_score'],
            'away_score': data['away_score'],
            'stage': stage,
            
            # Events info
            'event_count': len(data['events']),
            'event_types': ', '.join(data['event_types']),
            'main_event': _identify_main_event(data['event_types']),
            
            # Input commentaries
            'rule_based_commentary': data['rule_based'],
            'sequence_commentary': data['sequence'],
            
            # Output
            'llm_commentary': llm_commentary,
            
            # Metadata
            'model': commentator.model,
            'generated_at': datetime.now().isoformat(),
        }
        results.append(result)
        
        # Progress
        if (i + 1) % 10 == 0 or (i + 1) == total:
            print(f"  [{i+1}/{total}] Minute {minute}' - {data['event_types'][:3]}...")
    
    # Create DataFrame
    results_df = pd.DataFrame(results)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Main output file
    output_file = LLM_COMMENTARY_DIR / f"match_{match_id}_llm_commentary_{timestamp}.csv"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(output_file, index=False)
    print(f"\n✅ Saved to: {output_file}")
    
    # Detailed tracking file (for verification)
    if save_detailed:
        detailed_file = LLM_COMMENTARY_DIR / f"match_{match_id}_detailed_tracking_{timestamp}.csv"
        results_df.to_csv(detailed_file, index=False)
        print(f"✅ Detailed tracking: {detailed_file}")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"  • Total minutes processed: {len(results_df)}")
    print(f"  • Goals: {results_df[results_df['event_types'].str.contains('Goal', na=False)].shape[0]} minutes")
    print(f"  • Shots: {results_df[results_df['event_types'].str.contains('Shot', na=False)].shape[0]} minutes")
    print(f"  • Cards: {results_df[results_df['event_types'].str.contains('Card', na=False)].shape[0]} minutes")
    
    return results_df


def _identify_main_event(event_types: List[str]) -> str:
    """Identify the main event type from a list."""
    priority = ['Goal', 'Own Goal', 'Penalty', 'Red Card', 'Yellow Card', 
                'Shot', 'Save', 'Substitution', 'Corner', 'Free Kick', 'Foul']
    
    for event in priority:
        if event in event_types:
            return event
    
    return 'General Play'


def create_comparison_file(
    match_id: int,
    llm_results: pd.DataFrame,
    source: str = 'espn'
) -> Optional[pd.DataFrame]:
    """
    Create a comparison file merging LLM output with real commentary.
    
    Args:
        match_id: Match ID
        llm_results: DataFrame with LLM results
        source: Real commentary source
        
    Returns:
        Merged comparison DataFrame
    """
    # Load real commentary
    real_df = load_real_commentary(match_id, source)
    if real_df is None:
        return None
    
    # Merge on minute
    comparison = llm_results.merge(
        real_df[['minute', 'real_commentary', 'real_type', 'Embeddings_BERT', 
                 'real_sentiment', 'our_sentiment']].drop_duplicates('minute'),
        on='minute',
        how='left'
    )
    
    # Save comparison file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    comparison_file = LLM_COMMENTARY_DIR / f"match_{match_id}_comparison_{source}_{timestamp}.csv"
    comparison.to_csv(comparison_file, index=False)
    print(f"\n✅ Comparison file: {comparison_file}")
    
    return comparison


# =====================================
# OUTPUT FORMAT DOCUMENTATION
# =====================================
OUTPUT_FORMAT = """
OUTPUT FILE COLUMNS:
====================

IDENTIFIERS:
- match_id: Match identifier
- minute: Game minute (0-120+)
- period: Period number (1=first half, 2=second half, 3=ET1, 4=ET2)
- sequence_id: Original sequence ID from Phase 7

MATCH CONTEXT:
- home_team: Home team name
- away_team: Away team name
- home_score: Home team score at this minute
- away_score: Away team score at this minute
- stage: Match stage (Group, Final, etc.)

EVENTS INFO:
- event_count: Number of events in this minute
- event_types: Comma-separated list of event types
- main_event: Identified main event (Goal, Shot, Card, etc.)

COMMENTARIES (for comparison):
- rule_based_commentary: Generated commentary from Phase 7
- sequence_commentary: Sequence-level commentary from Phase 7
- llm_commentary: NEW - GPT generated commentary

METADATA:
- model: GPT model used
- generated_at: Timestamp of generation
"""


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate LLM commentary for a match")
    parser.add_argument('--match_id', type=int, required=True, help="Match ID")
    parser.add_argument('--home_team', type=str, default='Home', help="Home team name")
    parser.add_argument('--away_team', type=str, default='Away', help="Away team name")
    parser.add_argument('--stage', type=str, default='Match', help="Match stage")
    parser.add_argument('--max_minutes', type=int, help="Limit minutes to process")
    parser.add_argument('--compare', type=str, help="Create comparison with source (espn, bbc, etc.)")
    
    args = parser.parse_args()
    
    # Generate commentary
    results = generate_match_commentary(
        match_id=args.match_id,
        home_team=args.home_team,
        away_team=args.away_team,
        stage=args.stage,
        max_minutes=args.max_minutes
    )
    
    # Create comparison if requested
    if results is not None and args.compare:
        create_comparison_file(args.match_id, results, args.compare)


if __name__ == "__main__":
    # Print output format if run without args
    if len(sys.argv) == 1:
        print(OUTPUT_FORMAT)
        print("\nUsage:")
        print("  python batch_generate.py --match_id 3943043 --home_team Spain --away_team England --stage Final")
        print("  python batch_generate.py --match_id 3943043 --max_minutes 10")
        print("  python batch_generate.py --match_id 3943043 --compare espn")
    else:
        main()
