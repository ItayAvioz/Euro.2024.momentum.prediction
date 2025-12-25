"""
LLM vs Real Commentary Comparison
=================================
EXACTLY matches 08_enhanced_comparison methodology:
- Same minute mapping: Real minute N → LLM minute N-1
- Same models: SentenceTransformer (all-MiniLM-L6-v2), RoBERTa sentiment
- Same metrics: TF-IDF, BERT, content_overlap_ratio, sentiment
- Same average score: (TF-IDF + BERT + overlap + (1-sentiment_diff)) / 4
"""

import pandas as pd
import numpy as np
import os
import sys
import re
import warnings
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

warnings.filterwarnings('ignore')

# Paths
SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent
RESEARCH_DIR = BASE_DIR.parent
REAL_COMMENTARY_DIR = RESEARCH_DIR / "05_real_commentary_comparison" / "data"
LLM_COMMENTARY_FILE = RESEARCH_DIR / "10_llm_commentary" / "data" / "llm_commentary" / "all_matches_V3_20251209_193514.csv"
OUTPUT_DIR = BASE_DIR / "data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load models (same as 08)
print("Loading models...")
from sentence_transformers import SentenceTransformer
BERT_MODEL = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print("  [OK] BERT model loaded")

# Sentiment model (same as 08)
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
SENTIMENT_TOKENIZER = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment-latest")
SENTIMENT_MODEL = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment-latest")
print("  [OK] Sentiment model loaded")

# Linking words (same as 08)
LINKING_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be',
    'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
    'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
    'that', 'these', 'those', 'it', 'its', 'his', 'her', 'their', 'them',
    'he', 'she', 'we', 'they', 'i', 'you', 'my', 'your', 'our'
}

EVENT_TYPES = {
    'goal', 'shot', 'pass', 'tackle', 'dribble', 'foul', 'corner', 'free kick',
    'penalty', 'save', 'block', 'clearance', 'cross', 'header', 'volley',
    'assist', 'interception', 'offside', 'substitution', 'yellow card', 'red card',
    'kick-off', 'throw-in', 'goal kick', 'own goal', 'chance', 'attempt',
    'finish', 'strike', 'effort'
}


def normalize_text(text):
    """Normalize text (same as 08)"""
    if pd.isna(text):
        return ""
    text = str(text).lower()
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)
    return text.strip()


def get_content_words(text):
    """Get content words excluding linking words (same as 08)"""
    if pd.isna(text):
        return []
    text = normalize_text(text)
    text = re.sub(r'[^\w\s]', ' ', text)
    words = text.split()
    content = [w for w in words if len(w) > 2 and w not in LINKING_WORDS]
    return content


def extract_players(text, normalize=True):
    """Extract player names (same as 08)"""
    if pd.isna(text):
        return set()
    import unicodedata
    pattern = r'\b[A-Z][a-z\u00e0-\u00ff]{1,}(?:\s+[A-Z][a-z\u00e0-\u00ff]{1,})*\b'
    players = re.findall(pattern, str(text))
    excluded = {'Spain', 'France', 'England', 'Germany', 'Portugal', 'Italy', 'Netherlands',
                'Euro', 'UEFA', 'VAR', 'Good', 'Great', 'Brilliant', 'Crucial', 'Dangerous',
                'The', 'This', 'That', 'After', 'Before', 'During', 'Half', 'Start', 'End'}
    players = [p for p in players if p not in excluded]
    if normalize:
        def normalize_name(name):
            name = str(name).lower()
            name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
            parts = name.split()
            return parts[-1] if len(parts) > 1 else name
        return {normalize_name(p) for p in players}
    return set(players)


def extract_teams(text):
    """Extract team names (same as 08)"""
    if pd.isna(text):
        return set()
    teams = {
        'spain', 'france', 'england', 'germany', 'portugal', 'italy', 'netherlands',
        'belgium', 'croatia', 'switzerland', 'denmark', 'austria', 'turkey',
        'ukraine', 'poland', 'czech republic', 'scotland', 'serbia', 'romania',
        'slovakia', 'slovenia', 'hungary', 'albania', 'georgia'
    }
    text_lower = str(text).lower()
    return {team for team in teams if team in text_lower}


def extract_events(text):
    """Extract event types (same as 08)"""
    if pd.isna(text):
        return set()
    text_lower = str(text).lower()
    return {event for event in EVENT_TYPES if event in text_lower}


def calculate_sentiment(text):
    """Calculate sentiment using RoBERTa (same as 08)"""
    if pd.isna(text) or len(str(text).strip()) == 0:
        return None
    try:
        text_clean = str(text)[:512]
        inputs = SENTIMENT_TOKENIZER(text_clean, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = SENTIMENT_MODEL(**inputs)
            scores = outputs.logits.squeeze()
        probs = torch.nn.functional.softmax(scores, dim=0)
        sentiment_score = -1 * probs[0] + 0 * probs[1] + 1 * probs[2]
        return sentiment_score.item()
    except:
        return None


def compare_commentaries(real_text, llm_text):
    """Compare two commentaries (same metrics as 08)"""
    real_norm = normalize_text(real_text)
    llm_norm = normalize_text(llm_text)
    metrics = {}
    
    # TF-IDF
    if real_norm and llm_norm:
        try:
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([real_norm, llm_norm])
            metrics['TF-IDF'] = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except:
            metrics['TF-IDF'] = 0.0
    else:
        metrics['TF-IDF'] = 0.0
    
    # BERT embeddings
    if real_norm and llm_norm:
        try:
            embeddings = BERT_MODEL.encode([real_norm, llm_norm])
            metrics['Embeddings_BERT'] = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        except:
            metrics['Embeddings_BERT'] = 0.0
    else:
        metrics['Embeddings_BERT'] = 0.0
    
    # Sentiment
    real_sent = calculate_sentiment(real_text)
    llm_sent = calculate_sentiment(llm_text)
    metrics['real_sentiment'] = real_sent if real_sent is not None else 0.0
    metrics['our_sentiment'] = llm_sent if llm_sent is not None else 0.0
    metrics['sentiment_diff'] = abs(metrics['real_sentiment'] - metrics['our_sentiment'])
    
    # Word counts
    real_words = normalize_text(real_text).split()
    llm_words = normalize_text(llm_text).split()
    metrics['real_word_count'] = len(real_words)
    metrics['our_word_count'] = len(llm_words)
    
    # Content words
    real_content = get_content_words(real_text)
    llm_content = get_content_words(llm_text)
    metrics['real_content_words'] = len(real_content)
    metrics['our_content_words'] = len(llm_content)
    
    real_content_set = set(real_content)
    llm_content_set = set(llm_content)
    matching = real_content_set.intersection(llm_content_set)
    metrics['matching_content_words'] = len(matching)
    
    union = real_content_set.union(llm_content_set)
    metrics['content_overlap_ratio'] = len(matching) / len(union) if len(union) > 0 else 0.0
    
    # Entity extraction
    real_players = extract_players(real_text)
    llm_players = extract_players(llm_text)
    matching_players = real_players.intersection(llm_players)
    metrics['real_unique_players'] = len(real_players)
    metrics['our_unique_players'] = len(llm_players)
    metrics['matching_players'] = len(matching_players)
    metrics['entity_players_match'] = len(matching_players) / len(real_players) if len(real_players) > 0 else 0.0
    
    real_teams = extract_teams(real_text)
    llm_teams = extract_teams(llm_text)
    matching_teams = real_teams.intersection(llm_teams)
    metrics['real_unique_teams'] = len(real_teams)
    metrics['our_unique_teams'] = len(llm_teams)
    metrics['matching_teams'] = len(matching_teams)
    metrics['entity_teams_match'] = len(matching_teams) / len(real_teams) if len(real_teams) > 0 else 0.0
    
    real_events = extract_events(real_text)
    llm_events = extract_events(llm_text)
    matching_events = real_events.intersection(llm_events)
    metrics['real_unique_events'] = len(real_events)
    metrics['our_unique_events'] = len(llm_events)
    metrics['matching_events'] = len(matching_events)
    metrics['entity_events_match'] = len(matching_events) / len(real_events) if len(real_events) > 0 else 0.0
    
    # Entity repetitions
    real_all_players = extract_players(real_text, normalize=False)
    llm_all_players = extract_players(llm_text, normalize=False)
    metrics['real_player_mentions'] = len(real_all_players)
    metrics['our_player_mentions'] = len(llm_all_players)
    metrics['real_player_repetitions'] = max(0, len(real_all_players) - len(real_players))
    metrics['our_player_repetitions'] = max(0, len(llm_all_players) - len(llm_players))
    
    real_team_mentions = sum(str(real_text).lower().count(team) for team in real_teams)
    llm_team_mentions = sum(str(llm_text).lower().count(team) for team in llm_teams)
    metrics['real_team_mentions'] = real_team_mentions
    metrics['our_team_mentions'] = llm_team_mentions
    metrics['real_team_repetitions'] = max(0, real_team_mentions - len(real_teams))
    metrics['our_team_repetitions'] = max(0, llm_team_mentions - len(llm_teams))
    
    real_event_mentions = sum(str(real_text).lower().count(event) for event in real_events)
    llm_event_mentions = sum(str(llm_text).lower().count(event) for event in llm_events)
    metrics['real_event_mentions'] = real_event_mentions
    metrics['our_event_mentions'] = llm_event_mentions
    metrics['real_event_repetitions'] = max(0, real_event_mentions - len(real_events))
    metrics['our_event_repetitions'] = max(0, llm_event_mentions - len(llm_events))
    
    return metrics


def build_match_mapping():
    """Build match to real file mapping"""
    llm_df = pd.read_csv(LLM_COMMENTARY_FILE)
    matches = llm_df.groupby('match_id').agg({
        'home_team': 'first',
        'away_team': 'first'
    }).reset_index()
    
    real_files = list(REAL_COMMENTARY_DIR.glob("*.csv"))
    mapping = {}
    
    for _, row in matches.iterrows():
        match_id = row['match_id']
        home = row['home_team'].lower().replace(' ', '_')
        away = row['away_team'].lower().replace(' ', '_')
        
        sources = {}
        for real_file in real_files:
            file_name = real_file.name.lower()
            if (f"{home}_{away}" in file_name) or (f"{away}_{home}" in file_name):
                if 'flashscore' in file_name:
                    sources['flashscore'] = real_file.name
                elif 'espn' in file_name:
                    sources['espn'] = real_file.name
                elif 'bbc' in file_name:
                    sources['bbc'] = real_file.name
                elif 'fox' in file_name:
                    sources['fox'] = real_file.name
                elif 'sports_mole' in file_name:
                    sources['sports_mole'] = real_file.name
        
        if sources:
            mapping[match_id] = sources
    
    return mapping


def process_match(match_id, source_name, source_file, llm_df_full):
    """Process one match (same logic as 08)"""
    llm_df = llm_df_full[llm_df_full['match_id'] == match_id].copy()
    
    real_file_path = REAL_COMMENTARY_DIR / source_file
    if not real_file_path.exists():
        return None
    
    try:
        real_df = pd.read_csv(real_file_path, on_bad_lines='skip')
    except:
        return None
    
    home_team = llm_df['home_team'].iloc[0]
    away_team = llm_df['away_team'].iloc[0]
    
    print(f"  [OK] {home_team} vs {away_team}: LLM={len(llm_df)}, Real={len(real_df)}")
    
    commentary_col = 'commentary_text' if 'commentary_text' in real_df.columns else 'commentary'
    has_plus_time = 'plus_time' in real_df.columns
    
    results = []
    
    for _, real_row in real_df.iterrows():
        real_minute = int(real_row['minute'])
        real_text = real_row.get(commentary_col, '')
        real_type = real_row.get('event_type', 'General')
        
        if pd.isna(real_text) or len(str(real_text).strip()) == 0:
            continue
        
        # MINUTE MAPPING: Real minute N -> LLM minute N-1 (same as 08)
        if has_plus_time:
            plus_time = int(real_row.get('plus_time', 0))
            if plus_time > 0:
                target_minute = real_minute + plus_time - 1
                csv_minute = f"{real_minute}+{plus_time}"
                if real_minute == 45:
                    target_period = 1
                elif real_minute == 90:
                    target_period = 2
                elif real_minute == 105:
                    target_period = 3
                elif real_minute == 120:
                    target_period = 4
                else:
                    target_period = None
            else:
                target_minute = real_minute - 1
                csv_minute = real_minute
                if real_minute <= 45:
                    target_period = 1
                elif real_minute <= 90:
                    target_period = 2
                elif real_minute <= 105:
                    target_period = 3
                elif real_minute <= 120:
                    target_period = 4
                else:
                    target_period = None
        else:
            target_minute = real_minute - 1
            csv_minute = real_minute
            if real_minute <= 45:
                target_period = 1
            elif real_minute <= 90:
                target_period = 2
            elif real_minute <= 105:
                target_period = 3
            elif real_minute <= 120:
                target_period = 4
            else:
                target_period = None
        
        # Find matching LLM events
        if target_period is not None:
            llm_matches = llm_df[(llm_df['minute'] == target_minute) & (llm_df['period'] == target_period)]
        else:
            llm_matches = llm_df[llm_df['minute'] == target_minute]
        
        if len(llm_matches) == 0:
            # No LLM match - SKIP (only compare when both have commentary)
            continue
        
        # Compare with each LLM event at this minute
        for llm_idx, llm_row in llm_matches.iterrows():
            llm_text = llm_row.get('llm_commentary', '')
            if pd.isna(llm_text) or len(str(llm_text).strip()) == 0:
                continue
            
            metrics = compare_commentaries(real_text, llm_text)
            
            # Average score (same formula as 08)
            avg_score = (
                metrics['TF-IDF'] +
                metrics['Embeddings_BERT'] +
                metrics['content_overlap_ratio'] +
                (1 - metrics['sentiment_diff'])
            ) / 4
            
            avg_score_no_sentiment = (
                metrics['TF-IDF'] +
                metrics['Embeddings_BERT'] +
                metrics['content_overlap_ratio']
            ) / 3
            
            result = {
                'data_source': source_name.upper(),
                'minute': csv_minute,
                'sequence_rank': 1,  # Will be updated later
                'real_commentary': real_text,
                'real_type': real_type,
                'our_sequence_commentary': llm_text,
                'sequence_id': llm_idx,
                'average_score': avg_score,
                'average_score_no_sentiment': avg_score_no_sentiment,
                **metrics
            }
            results.append(result)
    
    if len(results) == 0:
        return None
    
    results_df = pd.DataFrame(results)
    
    # Rank within each minute (same as 08)
    results_df['sequence_rank'] = results_df.groupby('minute')['average_score'].rank(
        method='dense', ascending=False
    ).astype(int)
    
    # Sort chronologically
    def get_sort_key(minute_str):
        if '+' in str(minute_str):
            base, plus = str(minute_str).split('+')
            return float(base) + (float(plus) / 100)
        return float(minute_str)
    
    results_df['_sort_key'] = results_df['minute'].apply(get_sort_key)
    results_df = results_df.sort_values(['_sort_key', 'sequence_rank'])
    results_df = results_df.drop(columns=['_sort_key'])
    
    # Column order (same as 08)
    column_order = [
        'data_source', 'minute', 'sequence_rank', 'real_commentary', 'real_type', 'our_sequence_commentary', 'sequence_id',
        'average_score', 'average_score_no_sentiment',
        'TF-IDF', 'Embeddings_BERT', 'content_overlap_ratio',
        'real_sentiment', 'our_sentiment', 'sentiment_diff',
        'real_word_count', 'our_word_count',
        'real_content_words', 'our_content_words', 'matching_content_words',
        'real_unique_players', 'our_unique_players', 'matching_players', 'entity_players_match',
        'real_unique_teams', 'our_unique_teams', 'matching_teams', 'entity_teams_match',
        'real_unique_events', 'our_unique_events', 'matching_events', 'entity_events_match',
        'real_player_mentions', 'our_player_mentions', 'real_player_repetitions', 'our_player_repetitions',
        'real_team_mentions', 'our_team_mentions', 'real_team_repetitions', 'our_team_repetitions',
        'real_event_mentions', 'our_event_mentions', 'real_event_repetitions', 'our_event_repetitions'
    ]
    
    results_df = results_df[column_order]
    
    print(f"  [DONE] {len(results_df)} comparisons, avg score: {results_df['average_score'].mean():.3f}")
    
    return results_df


def main():
    print("=" * 70)
    print("LLM vs Real Commentary Comparison (08 methodology)")
    print("=" * 70)
    
    print("\n[INIT] Building match mapping...")
    match_mapping = build_match_mapping()
    print(f"[OK] Found {len(match_mapping)} matches")
    
    print("\n[INIT] Loading LLM commentary...")
    llm_df_full = pd.read_csv(LLM_COMMENTARY_FILE)
    print(f"[OK] Loaded {len(llm_df_full)} LLM events")
    
    total_files = 0
    
    for match_id, sources in match_mapping.items():
        print(f"\n[MATCH] {match_id}")
        
        for source_name, source_file in sources.items():
            print(f"  Processing {source_name}: {source_file}")
            
            result_df = process_match(match_id, source_name, source_file, llm_df_full)
            
            if result_df is not None and len(result_df) > 0:
                output_file = OUTPUT_DIR / f"match_{match_id}_{source_name}_llm_comparison.csv"
                result_df.to_csv(output_file, index=False)
                print(f"  [SAVED] {output_file.name} ({len(result_df)} rows)")
                total_files += 1
    
    print(f"\n{'=' * 70}")
    print(f"[DONE] Generated {total_files} comparison files")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
