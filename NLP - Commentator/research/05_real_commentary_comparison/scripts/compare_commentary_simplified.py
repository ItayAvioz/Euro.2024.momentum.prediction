"""
Simplified Commentary Comparison Script (No spaCy dependency)

Compares AI-generated commentary with real Sports Mole commentary using three metrics:
1. Cosine Similarity (TF-IDF)
2. Entity Overlap (Regex-based)
3. Semantic Similarity (Sentence Transformers)

Ranks all sequences within each minute against real commentary.
"""

import pandas as pd
import numpy as np
import re
import os
import sys
import warnings
warnings.filterwarnings('ignore')

# Disable TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TRANSFORMERS_NO_TF'] = '1'

# Text processing
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Semantic similarity
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine

# ============================================================================
# NORMALIZATION DICTIONARIES
# ============================================================================

TEAM_VARIATIONS = {
    'spain': ['spain', 'spanish', 'la roja', 'spaniards', "spain's"],
    'england': ['england', 'english', 'three lions', 'the three lions', "england's", "three lions'"],
    'france': ['france', 'french', 'les bleus', "france's"],
    'netherlands': ['netherlands', 'dutch', 'holland', 'oranje', "netherlands'"]
}

PLAYER_VARIATIONS = {
    # Spain
    'yamal': ['lamine yamal nasraoui ebana', 'lamine yamal', 'yamal', 'lamine'],
    'williams': ['nico williams', 'williams', 'nico'],
    'olmo': ['dani olmo', 'olmo', 'dani'],
    'morata': ['alvaro morata', 'morata', 'alvaro'],
    'rodri': ['rodri', 'rodrigo hernandez'],
    'ruiz': ['fabian ruiz', 'ruiz', 'fabian'],
    'carvajal': ['dani carvajal', 'carvajal'],
    'cucurella': ['marc cucurella', 'cucurella', 'marc'],
    'laporte': ['aymeric laporte', 'laporte'],
    'simon': ['unai simon', 'simon', 'unai'],
    'oyarzabal': ['mikel oyarzabal', 'oyarzabal'],
    'merino': ['mikel merino', 'merino'],
    
    # England
    'palmer': ['cole palmer', 'palmer', 'cole'],
    'bellingham': ['jude bellingham', 'bellingham', 'jude'],
    'kane': ['harry kane', 'kane', 'harry'],
    'saka': ['bukayo saka', 'saka', 'bukayo'],
    'foden': ['phil foden', 'foden', 'phil'],
    'pickford': ['jordan pickford', 'pickford', 'jordan'],
    'walker': ['kyle walker', 'walker', 'kyle'],
    'stones': ['john stones', 'stones', 'john'],
    'rice': ['declan rice', 'rice', 'declan'],
    'shaw': ['luke shaw', 'shaw', 'luke'],
    'trippier': ['kieran trippier', 'trippier', 'kieran'],
    'watkins': ['ollie watkins', 'watkins', 'ollie'],
    'mainoo': ['kobbie mainoo', 'mainoo', 'kobbie'],
    'guehi': ['marc guehi', 'guehi'],
    
    # Netherlands
    'simons': ['xavi simons', 'simons', 'xavi'],
    'gakpo': ['cody gakpo', 'gakpo', 'cody'],
    'depay': ['memphis depay', 'depay', 'memphis'],
    'dumfries': ['denzel dumfries', 'dumfries', 'denzel'],
    'van dijk': ['virgil van dijk', 'van dijk', 'virgil'],
    'ake': ['nathan ake', 'ake', 'nathan'],
    'malen': ['donyell malen', 'malen', 'donyell'],
    'weghorst': ['wout weghorst', 'weghorst', 'wout'],
    'verbruggen': ['bart verbruggen', 'verbruggen', 'bart'],
    
    # France
    'mbappe': ['kylian mbappe', 'mbappe', 'kylian'],
    'griezmann': ['antoine griezmann', 'griezmann', 'antoine'],
    'kolo muani': ['randal kolo muani', 'kolo muani', 'randal'],
    'rabiot': ['adrien rabiot', 'rabiot', 'adrien'],
    'tchouameni': ['aurelien tchouameni', 'tchouameni'],
    'maignan': ['mike maignan', 'maignan', 'mike'],
    'hernandez': ['theo hernandez', 'hernandez', 'theo'],
    'kounde': ['jules kounde', 'kounde', 'jules'],
    'dembele': ['ousmane dembele', 'dembele', 'ousmane'],
}

# ============================================================================
# TEXT NORMALIZATION
# ============================================================================

def normalize_text(text):
    """Normalize text for comparison"""
    if pd.isna(text) or not text:
        return ""
    
    text = str(text).lower()
    
    # Remove emojis and special characters
    text = re.sub(r'[⚽🎯🔥💥👏🏆⏱️🟡🟥📍🎉]', '', text)
    
    # Normalize team names
    for canonical, variations in TEAM_VARIATIONS.items():
        for variation in sorted(variations, key=len, reverse=True):
            text = re.sub(r'\b' + re.escape(variation) + r'\b', canonical, text)
    
    # Normalize player names (longest first to avoid partial matches)
    for canonical, variations in PLAYER_VARIATIONS.items():
        for variation in sorted(variations, key=len, reverse=True):
            text = re.sub(r'\b' + re.escape(variation) + r'\b', canonical, text)
    
    # Clean extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def clean_for_display(text):
    """Clean text for display (remove emojis but keep original case)"""
    if pd.isna(text) or not text:
        return ""
    text = str(text)
    text = re.sub(r'[⚽🎯🔥💥👏🏆⏱️🟡🟥📍🎉]', '', text)
    return text.strip()

# ============================================================================
# METHOD 1: COSINE SIMILARITY (TF-IDF)
# ============================================================================

def calculate_cosine_similarity(text1, text2):
    """Calculate TF-IDF cosine similarity between two texts"""
    try:
        if not text1 or not text2:
            return 0.0
        
        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2),  # 1-word and 2-word phrases
            max_features=1000
        )
        
        vectors = vectorizer.fit_transform([text1, text2])
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        
        return round(float(similarity), 4)
    
    except Exception as e:
        return 0.0

# ============================================================================
# METHOD 2: ENTITY OVERLAP (REGEX-BASED)
# ============================================================================

def extract_entities_simple(text, normalized_text):
    """Extract entities using simple regex patterns"""
    entities = {
        'players': [],
        'actions': [],
        'locations': [],
        'outcome': None,
        'score': None
    }
    
    try:
        # Players (from normalized text)
        for canonical in PLAYER_VARIATIONS.keys():
            if canonical in normalized_text:
                entities['players'].append(canonical)
        
        # Actions (common football verbs)
        action_patterns = [
            'shoot', 'shot', 'score', 'goal', 'pass', 'dribble', 'tackle',
            'save', 'block', 'clear', 'cross', 'receive', 'deliver', 'fire',
            'strike', 'header', 'volley', 'chip', 'lob', 'curl', 'smash',
            'intercept', 'foul', 'challenge', 'press', 'pressure'
        ]
        for action in action_patterns:
            if re.search(r'\b' + action + r'(?:s|ed|ing)?\b', text, re.IGNORECASE):
                entities['actions'].append(action)
        
        # Locations
        location_keywords = ['box', 'area', 'corner', 'wing', 'third', 'midfield',
                            'left', 'right', 'central', 'penalty', 'attacking', 'defensive']
        for keyword in location_keywords:
            if re.search(r'\b' + keyword + r'\b', text, re.IGNORECASE):
                entities['locations'].append(keyword)
        
        # Outcome
        text_upper = text.upper()
        if 'GOAL' in text_upper or 'SCORES' in text_upper or 'BREAKTHROUGH' in text_upper:
            entities['outcome'] = 'GOAL'
        elif 'SAVED' in text_upper or 'SAVE' in text_upper:
            entities['outcome'] = 'SAVED'
        elif 'MISS' in text_upper or 'OVER' in text_upper or 'WIDE' in text_upper:
            entities['outcome'] = 'MISS'
        elif 'BLOCK' in text_upper:
            entities['outcome'] = 'BLOCK'
        elif 'PENALTY' in text_upper:
            entities['outcome'] = 'PENALTY'
        else:
            entities['outcome'] = 'PLAY'
        
        # Score
        score_pattern = r'\b(\d+)[:-](\d+)\b'
        match = re.search(score_pattern, text)
        if match:
            entities['score'] = f"{match.group(1)}-{match.group(2)}"
        elif 'level' in text.lower() or 'square' in text.lower() or 'all square' in text.lower():
            entities['score'] = 'LEVEL'
    
    except Exception as e:
        pass
    
    return entities

def calculate_entity_overlap(entities1, entities2):
    """Calculate entity overlap score"""
    try:
        overlaps = {}
        
        # Player overlap (Jaccard similarity)
        players1 = set(entities1['players'])
        players2 = set(entities2['players'])
        if players1 or players2:
            overlaps['players'] = len(players1 & players2) / len(players1 | players2)
        else:
            overlaps['players'] = 0.0
        
        # Action overlap (Jaccard similarity)
        actions1 = set(entities1['actions'])
        actions2 = set(entities2['actions'])
        if actions1 or actions2:
            overlaps['actions'] = len(actions1 & actions2) / len(actions1 | actions2)
        else:
            overlaps['actions'] = 0.0
        
        # Location overlap (any match)
        if entities1['locations'] and entities2['locations']:
            location_match = bool(set(entities1['locations']) & set(entities2['locations']))
            overlaps['locations'] = 1.0 if location_match else 0.0
        else:
            overlaps['locations'] = 0.0
        
        # Outcome match
        if entities1['outcome'] and entities2['outcome']:
            overlaps['outcome'] = 1.0 if entities1['outcome'] == entities2['outcome'] else 0.0
        else:
            overlaps['outcome'] = 0.0
        
        # Score match
        if entities1['score'] and entities2['score']:
            overlaps['score'] = 1.0 if entities1['score'] == entities2['score'] else 0.0
        else:
            overlaps['score'] = 0.0
        
        # Weighted average
        weights = {
            'players': 0.30,
            'actions': 0.25,
            'locations': 0.15,
            'outcome': 0.20,
            'score': 0.10
        }
        
        total_score = sum(overlaps[key] * weights[key] for key in weights.keys())
        
        return round(total_score, 4), overlaps
    
    except Exception as e:
        return 0.0, {}

# ============================================================================
# METHOD 3: SEMANTIC SIMILARITY (SENTENCE TRANSFORMERS)
# ============================================================================

print("Loading Sentence Transformer model...")
semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
print("OK Model loaded successfully")

def calculate_semantic_similarity(text1, text2):
    """Calculate semantic similarity using sentence transformers"""
    try:
        if not text1 or not text2:
            return 0.0
        
        # Generate embeddings
        embedding1 = semantic_model.encode(text1)
        embedding2 = semantic_model.encode(text2)
        
        # Calculate cosine similarity in embedding space
        similarity = 1 - cosine(embedding1, embedding2)
        
        return round(float(similarity), 4)
    
    except Exception as e:
        return 0.0

# ============================================================================
# COMPARISON PIPELINE
# ============================================================================

def compare_minute(minute, our_sequences, real_commentary):
    """Compare all sequences in a minute to real commentary"""
    results = []
    
    # Normalize real commentary once
    real_normalized = normalize_text(real_commentary)
    real_entities = extract_entities_simple(real_commentary, real_normalized)
    
    for seq_id, seq_text, seq_score in our_sequences:
        # Normalize our sequence
        our_normalized = normalize_text(seq_text)
        our_entities = extract_entities_simple(seq_text, our_normalized)
        
        # Calculate all three metrics
        cosine_sim = calculate_cosine_similarity(our_normalized, real_normalized)
        entity_overlap_score, entity_details = calculate_entity_overlap(our_entities, real_entities)
        semantic_sim = calculate_semantic_similarity(our_normalized, real_normalized)
        
        # Average score
        avg_score = (cosine_sim + entity_overlap_score + semantic_sim) / 3
        
        results.append({
            'minute': minute,
            'sequence_id': seq_id,
            'our_sequence_commentary': seq_text,
            'score_before': seq_score,
            'cosine_similarity': cosine_sim,
            'entity_overlap': entity_overlap_score,
            'semantic_similarity': semantic_sim,
            'average_score': round(avg_score, 4),
            'entity_players_match': entity_details.get('players', 0.0),
            'entity_actions_match': entity_details.get('actions', 0.0),
            'entity_outcome_match': entity_details.get('outcome', 0.0)
        })
    
    # Sort by average score (descending)
    results.sort(key=lambda x: x['average_score'], reverse=True)
    
    # Assign ranks
    for i, result in enumerate(results):
        result['sequence_rank'] = i + 1
    
    return results

def process_match(match_name, match_id, our_commentary_path, real_commentary_path):
    """Process a single match comparison"""
    print(f"\n{'='*70}")
    print(f"Processing: {match_name}")
    print(f"{'='*70}")
    
    # Load data
    print("Loading data...")
    our_df = pd.read_csv(our_commentary_path)
    real_df = pd.read_csv(real_commentary_path)
    
    print(f"OK Our commentary: {len(our_df)} events")
    print(f"OK Real commentary: {len(real_df)} entries")
    
    # Get sequences with commentary - GROUP BY UNIQUE SEQUENCE ID
    our_sequences = our_df[our_df['sequence_commentary'].notna()].copy()
    print(f"OK Found {len(our_sequences)} event rows with commentary")
    
    # Group by sequence_id to get unique sequences only
    # Use LAST event in each sequence (typically the key event like a goal or shot)
    unique_sequences = our_sequences.groupby('sequence_id').last().reset_index()
    print(f"OK Found {len(unique_sequences)} unique sequences")
    
    # ADJUST MINUTE: Our data uses 0-indexed minutes, real commentary uses 1-indexed
    # E.g., our minute 8 (8:01 elapsed) = real commentary "in the 9th minute"
    unique_sequences['minute_adjusted'] = unique_sequences['minute'] + 1
    print(f"OK Adjusted minutes to match real commentary format (our minute N -> real minute N+1)")
    
    # Group by minute
    all_results = []
    
    for minute in sorted(real_df['minute'].unique()):
        real_entries = real_df[real_df['minute'] == minute]
        
        # Combine all real commentary for this minute
        real_commentary_list = real_entries['commentary_text'].tolist()
        real_commentary = " ".join([str(c) for c in real_commentary_list if pd.notna(c)])
        real_type = real_entries['line_type'].mode()[0] if len(real_entries) > 0 else 'black'
        
        # Get UNIQUE sequences for this minute (using adjusted minute)
        our_minute_seqs = unique_sequences[unique_sequences['minute_adjusted'] == minute]
        
        if len(our_minute_seqs) == 0:
            continue
        
        # Prepare sequences (id, text, score) - ONE PER UNIQUE SEQUENCE
        sequences_to_compare = []
        for _, row in our_minute_seqs.iterrows():
            seq_id = row['sequence_id']
            seq_text = clean_for_display(row['sequence_commentary'])
            seq_score = row.get('score_before', 'N/A')
            sequences_to_compare.append((seq_id, seq_text, seq_score))
        
        # Compare all sequences in this minute
        minute_results = compare_minute(minute, sequences_to_compare, real_commentary)
        
        # Add real commentary to each result
        for result in minute_results:
            result['real_commentary'] = clean_for_display(real_commentary)
            result['real_commentary_type'] = real_type
        
        all_results.extend(minute_results)
        
        print(f"  Minute {minute:3d}: {len(minute_results):2d} sequences ranked")
    
    # Create results DataFrame
    results_df = pd.DataFrame(all_results)
    
    # Reorder columns
    column_order = [
        'minute',
        'sequence_rank',
        'real_commentary',
        'real_commentary_type',
        'our_sequence_commentary',
        'sequence_id',
        'score_before',
        'average_score',
        'cosine_similarity',
        'entity_overlap',
        'semantic_similarity',
        'entity_players_match',
        'entity_actions_match',
        'entity_outcome_match'
    ]
    
    results_df = results_df[column_order]
    
    # Save results
    output_path = f"../data/match_{match_id}_comparison_results.csv"
    results_df.to_csv(output_path, index=False)
    print(f"\nOK Results saved to: {output_path}")
    print(f"  Total comparisons: {len(results_df)}")
    print(f"  Avg score: {results_df['average_score'].mean():.3f}")
    print(f"  Rank 1 sequences: {len(results_df[results_df['sequence_rank'] == 1])}")
    
    return results_df

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main comparison pipeline"""
    print("\n" + "="*70)
    print("COMMENTARY COMPARISON ANALYSIS")
    print("="*70)
    
    # Match configurations
    matches = [
        {
            'name': 'Spain vs England (Final)',
            'match_id': '3943043',
            'our_commentary': '../../04_final_game_production/data/final_game_rich_commentary.csv',
            'real_commentary': '../data/sports_mole_final_commentary_COMPLETE.csv'
        },
        {
            'name': 'Netherlands vs England (Semi-Final)',
            'match_id': '3942819',
            'our_commentary': '../../06_semi_finals_commentary/data/match_3942819_rich_commentary.csv',
            'real_commentary': '../data/sports_mole_netherlands_england_commentary.csv'
        },
        {
            'name': 'Spain vs France (Semi-Final)',
            'match_id': '3942752',
            'our_commentary': '../../06_semi_finals_commentary/data/match_3942752_rich_commentary.csv',
            'real_commentary': '../data/sports_mole_spain_france_commentary.csv'
        }
    ]
    
    all_results = {}
    
    for match in matches:
        try:
            results_df = process_match(
                match['name'],
                match['match_id'],
                match['our_commentary'],
                match['real_commentary']
            )
            all_results[match['match_id']] = results_df
        except Exception as e:
            print(f"\nERROR Error processing {match['name']}: {e}")
            import traceback
            traceback.print_exc()
    
    # Generate summary statistics
    print("\n" + "="*70)
    print("GENERATING SUMMARY STATISTICS")
    print("="*70)
    
    summary_stats = []
    
    for match_id, results_df in all_results.items():
        match_name = [m['name'] for m in matches if m['match_id'] == match_id][0]
        
        stats = {
            'match': match_name,
            'match_id': match_id,
            'total_comparisons': len(results_df),
            'unique_minutes': results_df['minute'].nunique(),
            'rank_1_sequences': len(results_df[results_df['sequence_rank'] == 1]),
            'avg_cosine_similarity': results_df['cosine_similarity'].mean(),
            'avg_entity_overlap': results_df['entity_overlap'].mean(),
            'avg_semantic_similarity': results_df['semantic_similarity'].mean(),
            'avg_overall_score': results_df['average_score'].mean(),
            'max_score': results_df['average_score'].max(),
            'min_score': results_df['average_score'].min()
        }
        
        summary_stats.append(stats)
    
    summary_df = pd.DataFrame(summary_stats)
    summary_path = "../data/comparison_summary_statistics.csv"
    summary_df.to_csv(summary_path, index=False)
    print(f"\nOK Summary statistics saved to: {summary_path}")
    
    # Display summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    for _, row in summary_df.iterrows():
        print(f"\n{row['match']}")
        print(f"  Total Comparisons: {row['total_comparisons']}")
        print(f"  Rank 1 Sequences: {row['rank_1_sequences']}")
        print(f"  Avg Scores:")
        print(f"    • Cosine Similarity:   {row['avg_cosine_similarity']:.3f}")
        print(f"    • Entity Overlap:      {row['avg_entity_overlap']:.3f}")
        print(f"    • Semantic Similarity: {row['avg_semantic_similarity']:.3f}")
        print(f"    • Overall Average:     {row['avg_overall_score']:.3f}")
    
    print("\n" + "="*70)
    print("OK COMPARISON COMPLETE!")
    print("="*70)

if __name__ == "__main__":
    main()

