"""
Generate Training Pairs for NLP Commentary Model
================================================
Create CSV with [INPUT FEATURES] -> [OUTPUT COMMENTARY] pairs
for training the starting game commentary model.
"""

import pandas as pd
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_starting_events():
    """Load the starting events dataset"""
    csv_path = os.path.join(SCRIPT_DIR, 'starting_events_with_team_stats.csv')
    df = pd.read_csv(csv_path)
    return df

def generate_commentary(row):
    """Generate commentary from row data"""
    team_a = row['team_a']
    team_b = row['team_b']
    stadium = row['stadium']
    referee = row['referee']
    stage = row['stage']
    
    # Opening
    commentary = f"Welcome to {stadium} for this {stage} clash between {team_a} and {team_b}. {referee} will be taking charge of today's match. "
    
    # Team A Form
    if row['team_a_matches_played'] > 0:
        w, d, l = int(row['team_a_wins']), int(row['team_a_draws']), int(row['team_a_losses'])
        gs, gc = int(row['team_a_goals_scored']), int(row['team_a_goals_conceded'])
        
        commentary += f"{team_a} come into this match having recorded {w} win{'s' if w != 1 else ''}, {d} draw{'s' if d != 1 else ''}, and {l} loss{'es' if l != 1 else ''} in the tournament so far. "
        commentary += f"They've scored {gs} goal{'s' if gs != 1 else ''} while conceding {gc}. "
        
        last_result = row['team_a_last_result']
        last_score = row['team_a_last_score']
        last_opp = row['team_a_last_opponent']
        
        if last_result == 'Win':
            commentary += f"Last time out, they secured a {last_score} victory over {last_opp}. "
        elif last_result == 'Draw':
            commentary += f"Their previous match ended in a {last_score} draw against {last_opp}. "
        else:
            commentary += f"They'll be looking to bounce back from a {last_score} defeat to {last_opp}. "
    else:
        commentary += f"{team_a} are making their tournament debut. "
    
    # Team B Form
    if row['team_b_matches_played'] > 0:
        w, d, l = int(row['team_b_wins']), int(row['team_b_draws']), int(row['team_b_losses'])
        gs, gc = int(row['team_b_goals_scored']), int(row['team_b_goals_conceded'])
        
        commentary += f"{team_b} have managed {w} win{'s' if w != 1 else ''}, {d} draw{'s' if d != 1 else ''}, and {l} loss{'es' if l != 1 else ''} so far in Euro 2024. "
        commentary += f"With {gs} goal{'s' if gs != 1 else ''} scored and {gc} conceded, "
        
        last_result = row['team_b_last_result']
        last_score = row['team_b_last_score']
        last_opp = row['team_b_last_opponent']
        
        if last_result == 'Win':
            commentary += f"they come in confident after beating {last_opp} {last_score}. "
        elif last_result == 'Draw':
            commentary += f"they drew {last_score} with {last_opp} last time. "
        else:
            commentary += f"they'll want to recover from that {last_score} loss to {last_opp}. "
    else:
        commentary += f"{team_b} are also starting their tournament campaign. "
    
    # Kick-off
    commentary += f"We're all set for kick-off here at {stadium}."
    
    return commentary

def create_training_pairs():
    """Create training pairs CSV"""
    
    # Load data
    df = load_starting_events()
    
    # Get unique matches (one row per match)
    matches = df.drop_duplicates(subset='match_id').copy()
    
    # Create training pairs
    training_data = []
    
    for idx, row in matches.iterrows():
        
        # Input features
        input_features = {
            'match_id': row['match_id'],
            'stage': row['stage'],
            'stadium': row['stadium'],
            'referee': row['referee'],
            'team_a': row['team_a'],
            'team_b': row['team_b'],
            'team_a_matches_played': row['team_a_matches_played'],
            'team_a_wins': row['team_a_wins'],
            'team_a_draws': row['team_a_draws'],
            'team_a_losses': row['team_a_losses'],
            'team_a_goals_scored': row['team_a_goals_scored'],
            'team_a_goals_conceded': row['team_a_goals_conceded'],
            'team_a_goal_difference': row['team_a_goal_difference'],
            'team_a_last_result': row['team_a_last_result'],
            'team_a_last_score': row['team_a_last_score'],
            'team_a_last_opponent': row['team_a_last_opponent'],
            'team_b_matches_played': row['team_b_matches_played'],
            'team_b_wins': row['team_b_wins'],
            'team_b_draws': row['team_b_draws'],
            'team_b_losses': row['team_b_losses'],
            'team_b_goals_scored': row['team_b_goals_scored'],
            'team_b_goals_conceded': row['team_b_goals_conceded'],
            'team_b_goal_difference': row['team_b_goal_difference'],
            'team_b_last_result': row['team_b_last_result'],
            'team_b_last_score': row['team_b_last_score'],
            'team_b_last_opponent': row['team_b_last_opponent'],
        }
        
        # Generate commentary
        commentary = generate_commentary(row)
        
        # Add to training data
        input_features['commentary'] = commentary
        training_data.append(input_features)
    
    # Create DataFrame
    training_df = pd.DataFrame(training_data)
    
    return training_df

def main():
    """Main execution"""
    print("\n" + "="*80)
    print("GENERATING NLP TRAINING PAIRS")
    print("="*80)
    
    print("\nCreating [INPUT FEATURES] -> [OUTPUT COMMENTARY] pairs...")
    
    training_df = create_training_pairs()
    
    # Save to CSV
    output_file = os.path.join(SCRIPT_DIR, 'starting_game_training_pairs.csv')
    training_df.to_csv(output_file, index=False)
    
    print(f"\n✅ Training pairs created successfully!")
    print(f"   File: {output_file}")
    print(f"   Total examples: {len(training_df)}")
    print(f"   Input features: {len(training_df.columns) - 1}")  # -1 for commentary column
    
    print("\n📊 Dataset Breakdown:")
    print(f"   Matches: {len(training_df)}")
    print(f"   Stages: {training_df['stage'].unique().tolist()}")
    
    print("\n📋 Column Structure:")
    print(f"   Input Features: {', '.join(training_df.columns[:-1].tolist()[:10])}...")
    print(f"   Output: commentary")
    
    # Show example
    print("\n" + "="*80)
    print("EXAMPLE TRAINING PAIR")
    print("="*80)
    
    example = training_df.iloc[2]  # Final match
    
    print("\n[INPUT FEATURES]")
    print(f"  Match ID: {example['match_id']}")
    print(f"  Stage: {example['stage']}")
    print(f"  Stadium: {example['stadium']}")
    print(f"  Referee: {example['referee']}")
    print(f"  Teams: {example['team_a']} vs {example['team_b']}")
    print(f"\n  Team A ({example['team_a']}) Stats:")
    print(f"    - Record: {int(example['team_a_wins'])}W-{int(example['team_a_draws'])}D-{int(example['team_a_losses'])}L")
    print(f"    - Goals: {int(example['team_a_goals_scored'])} scored, {int(example['team_a_goals_conceded'])} conceded")
    print(f"    - Last: {example['team_a_last_result']} ({example['team_a_last_score']} vs {example['team_a_last_opponent']})")
    print(f"\n  Team B ({example['team_b']}) Stats:")
    print(f"    - Record: {int(example['team_b_wins'])}W-{int(example['team_b_draws'])}D-{int(example['team_b_losses'])}L")
    print(f"    - Goals: {int(example['team_b_goals_scored'])} scored, {int(example['team_b_goals_conceded'])} conceded")
    print(f"    - Last: {example['team_b_last_result']} ({example['team_b_last_score']} vs {example['team_b_last_opponent']})")
    
    print("\n[OUTPUT COMMENTARY]")
    print(f"  {example['commentary']}")
    
    print("\n" + "="*80)
    print("USAGE FOR NLP MODEL TRAINING")
    print("="*80)
    print("""
    This CSV can be used for:
    
    1. SUPERVISED LEARNING
       - Input: All columns except 'commentary'
       - Output: 'commentary' column
       - Model learns to generate natural language from structured data
    
    2. TEMPLATE-BASED GENERATION
       - Extract patterns from commentary
       - Learn conditional rules (debut vs experienced teams)
       - Apply to new data
    
    3. FEATURE IMPORTANCE
       - Identify which stats are most mentioned
       - Determine narrative priorities
       - Optimize data extraction
    
    4. EVALUATION METRICS
       - BLEU score (n-gram overlap)
       - ROUGE score (summary quality)
       - Human evaluation (fluency, accuracy)
    """)
    
    print("="*80)
    
if __name__ == "__main__":
    main()
