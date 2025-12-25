"""
Batch Commentary Generation - V3
Generates ESPN-style LLM commentary for ALL 51 Euro 2024 matches.

Uses V3 logic:
- Progressive General events (domination streak)
- Multiple shots/corners/fouls analysis with xG
- LLM freedom of action

Author: AI Assistant
Date: December 9, 2025
"""

import os
import sys
import ast
import time
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gpt_commentator_v3 import GPTCommentator

# =====================================
# PATHS
# =====================================
SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent
PHASE7_DATA = BASE_DIR.parent / "07_all_games_commentary" / "data"
COMPLETE_DATA = Path("C:/Users/yonatanam/Desktop/Euro 2024 - momentum - DS-AI project/Data/euro_2024_complete_dataset.csv")
MATCHES_DATA = Path("C:/Users/yonatanam/Desktop/Euro 2024 - momentum - DS-AI project/Data/matches_complete.csv")
OUTPUT_DIR = BASE_DIR / "data" / "llm_commentary"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =====================================
# IMPORT V3 FUNCTIONS FROM run_final_test_v3.py
# =====================================
from run_final_test_v3 import (
    get_location_description,
    get_distance_description,
    extract_xg_from_shot_column,
    get_foul_danger_context,
    extract_card_from_row,
    validate_player_team,
    calculate_shot_danger_score,
    analyze_multiple_shots,
    analyze_multiple_corners,
    analyze_multiple_fouls,
    analyze_multiple_substitutions,
    analyze_multiple_offsides,
    get_dominant_team_for_minute,
    check_domination_for_consecutive_generals,
    get_most_active_player,
    detect_all_important_events,
    detect_main_event,
    extract_event_specific_data,
    detect_event_chain,
)


def load_all_matches():
    """Load match information for all 51 Euro 2024 games."""
    matches_df = pd.read_csv(MATCHES_DATA)
    
    # Extract relevant columns
    matches = []
    for _, row in matches_df.iterrows():
        matches.append({
            'match_id': row['match_id'],
            'home_team': row['home_team_name'],
            'away_team': row['away_team_name'],
            'stage': row['stage'],
            'home_score': row['home_score'],
            'away_score': row['away_score'],
            'match_date': row['match_date']
        })
    
    return matches


def load_match_data(match_id):
    """Load event data for a specific match."""
    # Try rich commentary file first
    rich_file = PHASE7_DATA / f"match_{match_id}_rich_commentary.csv"
    if rich_file.exists():
        return pd.read_csv(rich_file)
    
    # Try detailed file
    detailed_file = PHASE7_DATA / f"match_{match_id}_detailed_commentary_data.csv"
    if detailed_file.exists():
        return pd.read_csv(detailed_file)
    
    return None


def load_complete_dataset():
    """Load the complete dataset for xG and card columns."""
    try:
        return pd.read_csv(COMPLETE_DATA, low_memory=False)
    except Exception as e:
        print(f"[WARN] Could not load complete dataset: {e}")
        return None


def generate_match_commentary(match_info, df, complete_df, commentator):
    """Generate V3 commentary for a single match."""
    match_id = match_info['match_id']
    home_team = match_info['home_team']
    away_team = match_info['away_team']
    stage = match_info['stage']
    
    # Reset global trackers
    possession_history = {}
    last_event_type = None
    consecutive_general_count = 0
    general_control_history = []
    
    # Merge columns from complete dataset
    if complete_df is not None:
        match_complete = complete_df[complete_df['match_id'] == match_id].copy().reset_index(drop=True)
        if len(df) == len(match_complete):
            df['foul_committed'] = match_complete['foul_committed'].values
            df['bad_behaviour'] = match_complete['bad_behaviour'].values
            df['shot'] = match_complete['shot'].values
    
    # Determine score column names
    home_score_col = None
    away_score_col = None
    
    for col in df.columns:
        if 'score' in col.lower():
            if home_team.lower().split()[0] in col.lower():
                home_score_col = col
            elif away_team.lower().split()[0] in col.lower():
                away_score_col = col
    
    # Fallback to generic names
    if home_score_col is None:
        home_score_col = 'home_score' if 'home_score' in df.columns else None
    if away_score_col is None:
        away_score_col = 'away_score' if 'away_score' in df.columns else None
    
    # Group by (minute, period)
    df['minute_period'] = df['minute'].astype(str) + '_' + df['period'].astype(str)
    all_minute_periods = df.groupby(['minute', 'period']).size().reset_index()[['minute', 'period']]
    all_minute_periods = all_minute_periods.sort_values(['period', 'minute']).reset_index(drop=True)
    
    results = []
    
    for idx, row in all_minute_periods.iterrows():
        minute = row['minute']
        period = row['period']
        
        minute_df = df[(df['minute'] == minute) & (df['period'] == period)].copy()
        
        # Track possession for domination
        dom_info = get_dominant_team_for_minute(minute_df)
        possession_history[(minute, period)] = dom_info
        
        # Get most active player
        most_active = get_most_active_player(minute_df)
        
        # V3: Analyze multiple events in SAME minute
        multi_shots_info = analyze_multiple_shots(minute_df)
        multi_corners_info = analyze_multiple_corners(minute_df)
        multi_fouls_info = analyze_multiple_fouls(minute_df)
        multi_subs_info = analyze_multiple_substitutions(minute_df)
        multi_offsides_info = analyze_multiple_offsides(minute_df)
        
        # Base detection info
        base_detection_info = {
            'stage': stage,
            'full_df': df,
            'period': period
        }
        
        # Detect all important events
        all_events = detect_all_important_events(minute_df, base_detection_info)
        
        # V3: If multiple shots detected and main event is a shot, override to multi-shot
        if multi_shots_info.get('has_multiple') and len(all_events) == 1:
            detected_type, main_row, extra_info = all_events[0]
            if 'Shot' in detected_type and detected_type != 'Goal':
                scenario = multi_shots_info.get('scenario', 'pressure')
                new_type = f"Shots ({scenario.title()})"
                all_events = [(new_type, main_row, extra_info)]
        
        # Summaries
        event_counts = minute_df['event_type'].value_counts().head(5).to_dict()
        event_summary = ', '.join([f"{k}({v})" for k, v in event_counts.items()])
        pattern_counts = minute_df['play_pattern'].value_counts().to_dict()
        pattern_summary = ', '.join([f"{k}({v})" for k, v in pattern_counts.items() if pd.notna(k)])
        
        score_row = minute_df.iloc[-1]
        
        # Get scores
        home_score = 0
        away_score = 0
        if home_score_col and home_score_col in score_row:
            home_score = score_row.get(home_score_col, 0)
        if away_score_col and away_score_col in score_row:
            away_score = score_row.get(away_score_col, 0)
        
        for event_idx, (detected_type, main_row, extra_info) in enumerate(all_events):
            # Get current control for this minute
            current_control = ''
            if 'possession_team' in minute_df.columns:
                possession_counts = minute_df['possession_team'].value_counts()
                if len(possession_counts) > 0:
                    dominant_team = possession_counts.index[0]
                    dominant_pct = (possession_counts.iloc[0] / len(minute_df)) * 100
                    if dominant_pct > 55:
                        current_control = f"{dominant_team} in control"
            
            # V3: Track consecutive generals with control history
            if detected_type == 'General':
                if last_event_type == 'General':
                    consecutive_general_count += 1
                else:
                    consecutive_general_count = 1
                    general_control_history = []
                general_control_history.append(current_control)
                domination_info = check_domination_for_consecutive_generals(
                    consecutive_general_count, 
                    current_control, 
                    general_control_history
                )
            else:
                consecutive_general_count = 0
                general_control_history = []
                domination_info = {'has_domination': False}
            
            last_event_type = detected_type
            
            # Merge detection info
            detection_info = base_detection_info.copy()
            detection_info.update(extra_info)
            
            # Extract event data
            event_data = extract_event_specific_data(detected_type, main_row, minute_df, detection_info)
            
            # For Card events
            if detected_type in ['Yellow Card', 'Red Card']:
                event_data['carded_player'] = extra_info.get('carded_player', event_data.get('player', ''))
                event_data['carded_team'] = extra_info.get('carded_team', event_data.get('team', ''))
                event_data['fouled_player'] = extra_info.get('fouled_player', '')
                event_data['fouled_team'] = extra_info.get('fouled_team', '')
            
            # Detect event chains
            event_chain = detect_event_chain(minute_df, detected_type, main_row, detection_info)
            
            # Get commentary
            rule_based = str(main_row.get('event_commentary', '')) if pd.notna(main_row.get('event_commentary')) else ''
            sequence = str(main_row.get('sequence_commentary', '')) if pd.notna(main_row.get('sequence_commentary')) else ''
            
            # Calculate area for this minute
            area = ''
            if 'location_x' in minute_df.columns:
                avg_x = minute_df['location_x'].mean()
                if pd.notna(avg_x):
                    if avg_x < 40:
                        area = 'defensive third'
                    elif avg_x < 80:
                        area = 'midfield'
                    else:
                        area = 'attacking third'
            
            # Build context
            context = {
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_score,
                'away_score': away_score,
                'stage': stage,
                'period': detection_info.get('period', 1),
                'detected_type': detected_type,
                'event_data': event_data,
                'event_chain': event_chain,
                'total_events': len(minute_df),
                'pattern_summary': pattern_summary,
                'control': detection_info.get('control', ''),
                'possession_stats': detection_info.get('possession_stats', {}),
                'area': area,
                'domination_info': domination_info,
                'consecutive_generals': consecutive_general_count,
                'most_active_player': most_active if most_active else {},
                'multi_shots_info': multi_shots_info,
                'multi_corners_info': multi_corners_info,
                'multi_fouls_info': multi_fouls_info,
                'multi_subs_info': multi_subs_info,
                'multi_offsides_info': multi_offsides_info,
            }
            
            # Generate LLM commentary
            llm_commentary = commentator.generate_minute_commentary(
                minute=int(minute),
                events_data=[],
                rule_based_commentary=rule_based,
                sequence_commentary=sequence,
                match_context=context
            )
            
            # Save result
            result = {
                'match_id': match_id,
                'minute': minute,
                'period': period,
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_score,
                'away_score': away_score,
                'stage': stage,
                'detected_type': detected_type,
                'player': event_data.get('player', event_data.get('carded_player', '')),
                'team': event_data.get('team', event_data.get('carded_team', '')),
                'llm_commentary': llm_commentary,
                'model': commentator.model,
                'generated_at': datetime.now().isoformat(),
            }
            
            results.append(result)
    
    return results


def main():
    """Main entry point for batch processing."""
    print("=" * 70)
    print("BATCH COMMENTARY GENERATION - V3")
    print("All 51 Euro 2024 Matches - One CSV per game")
    print("=" * 70)
    
    # Load all matches info
    print("\n[1/4] Loading match information...")
    matches = load_all_matches()
    print(f"      Found {len(matches)} matches")
    
    # Load complete dataset once
    print("\n[2/4] Loading complete dataset for xG and cards...")
    complete_df = load_complete_dataset()
    if complete_df is not None:
        print(f"      Loaded {len(complete_df)} events")
    
    # Initialize commentator once
    print("\n[3/4] Initializing GPT Commentator V3...")
    commentator = GPTCommentator()
    print(f"      Model: {commentator.model}")
    
    # Process each match
    print("\n[4/4] Processing matches...")
    print("-" * 70)
    
    total_commentaries = 0
    successful_matches = 0
    failed_matches = []
    total_matches = len(matches)
    start_time = time.time()
    
    for i, match_info in enumerate(matches):
        match_id = match_info['match_id']
        match_start = time.time()
        
        print(f"\n[{i+1}/{total_matches}] {match_info['home_team']} vs {match_info['away_team']}")
        print(f"         Stage: {match_info['stage']} | Match ID: {match_id}")
        
        # Load match data
        df = load_match_data(match_id)
        if df is None:
            print(f"         ⚠️ No data found, skipping...")
            failed_matches.append(match_id)
            continue
        
        print(f"         Events: {len(df)}")
        
        # Generate commentary
        try:
            results = generate_match_commentary(match_info, df, complete_df, commentator)
            
            # Save this match's CSV immediately
            if results:
                results_df = pd.DataFrame(results)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = OUTPUT_DIR / f"match_{match_id}_V3_{timestamp}.csv"
                results_df.to_csv(output_file, index=False)
                
                match_time = time.time() - match_start
                print(f"         ✅ Generated {len(results)} commentaries ({match_time:.1f}s)")
                print(f"         💾 Saved: {output_file.name}")
                
                total_commentaries += len(results)
                successful_matches += 1
            
        except Exception as e:
            print(f"         ❌ Error: {e}")
            failed_matches.append(match_id)
            continue
        
        # Progress estimate
        elapsed = time.time() - start_time
        avg_time = elapsed / (i + 1)
        remaining = avg_time * (total_matches - i - 1)
        print(f"         ⏱️ Est. remaining: {remaining/60:.1f} min")
    
    # Final summary
    print("\n" + "=" * 70)
    print("BATCH COMPLETE!")
    print("=" * 70)
    
    total_time = time.time() - start_time
    
    print(f"\n✅ SUMMARY:")
    print(f"   Matches processed: {successful_matches}/{total_matches}")
    print(f"   Total commentaries: {total_commentaries}")
    print(f"   Total time: {total_time/60:.1f} minutes")
    print(f"   Output folder: {OUTPUT_DIR}")
    
    if failed_matches:
        print(f"\n⚠️ Failed matches ({len(failed_matches)}):")
        for mid in failed_matches:
            print(f"   - {mid}")
    
    print(f"\n📁 Generated files:")
    print(f"   match_[ID]_V3_[timestamp].csv × {successful_matches}")


if __name__ == "__main__":
    main()

