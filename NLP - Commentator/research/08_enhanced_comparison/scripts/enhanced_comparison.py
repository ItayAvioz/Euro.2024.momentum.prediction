"""
Enhanced Commentary Comparison System
======================================
Compares generated commentary to real commentary with comprehensive metrics:
- Renamed metrics (TF-IDF, Embeddings-BERT)
- Sentiment analysis
- Word counts (total, content, matching)
- Entity counts (unique players, teams, events)
- Entity repetitions
- Proper normalization

Usage:
    python enhanced_comparison.py <match_id>
"""

import pandas as pd
import numpy as np
import os
import sys
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import warnings

warnings.filterwarnings('ignore')

# Setup paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENHANCED_ROOT = os.path.dirname(SCRIPT_DIR)  # 08_enhanced_comparison
RESEARCH_ROOT = os.path.dirname(ENHANCED_ROOT)  # research
NLP_ROOT = os.path.dirname(RESEARCH_ROOT)  # NLP - Commentator
PROJECT_ROOT = os.path.dirname(NLP_ROOT)  # Euro 2024 - momentum - DS-AI project

# Load models (will be loaded once)
print("Loading models...")
BERT_MODEL = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print("  [OK] BERT model loaded")

# Sentiment model
SENTIMENT_MODEL = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest", truncation=True, max_length=512)
print("  [OK] Sentiment model loaded")

# Linking words to exclude (common stop words)
LINKING_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be',
    'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
    'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
    'that', 'these', 'those', 'it', 'its', 'his', 'her', 'their', 'them',
    'he', 'she', 'we', 'they', 'i', 'you', 'my', 'your', 'our'
}

# Event types (common football events)
EVENT_TYPES = {
    'goal', 'shot', 'pass', 'tackle', 'dribble', 'foul', 'corner', 'free kick',
    'penalty', 'save', 'block', 'clearance', 'cross', 'header', 'volley',
    'assist', 'interception', 'offside', 'substitution', 'yellow card', 'red card',
    'kick-off', 'throw-in', 'goal kick', 'own goal', 'chance', 'attempt',
    'finish', 'strike', 'effort'
}


def normalize_text(text):
    """Normalize text for comparison"""
    if pd.isna(text):
        return ""
    
    # Convert to string and lowercase
    text = str(text).lower()
    
    # Remove emojis
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)
    
    return text.strip()


def normalize_name(name):
    """Normalize player/team name for matching"""
    if pd.isna(name):
        return ""
    
    name = str(name).lower()
    
    # Remove accents and special characters
    import unicodedata
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    
    # Get last name (usually the most important)
    parts = name.split()
    if len(parts) > 1:
        return parts[-1]  # Last name
    return name


def extract_players(text, normalize=True):
    """Extract player names from text (capitalized words)"""
    if pd.isna(text):
        return set()
    
    # Pattern: Capitalized words (2+ chars) that could be names
    pattern = r'\b[A-Z][a-záéíóúàèìòùâêîôûäëïöüñç]{1,}(?:\s+[A-Z][a-záéíóúàèìòùâêîôûäëïöüñç]{1,})*\b'
    players = re.findall(pattern, str(text))
    
    # Filter out common non-names
    excluded = {'Spain', 'France', 'England', 'Germany', 'Portugal', 'Italy', 'Netherlands', 
                'Euro', 'UEFA', 'VAR', 'Good', 'Great', 'Brilliant', 'Crucial', 'Dangerous',
                'The', 'This', 'That', 'After', 'Before', 'During', 'Half', 'Start', 'End'}
    players = [p for p in players if p not in excluded]
    
    if normalize:
        return {normalize_name(p) for p in players}
    return set(players)


def extract_teams(text, normalize=True):
    """Extract team names from text"""
    if pd.isna(text):
        return set()
    
    # Common team names in Euro 2024
    teams = {
        'spain', 'france', 'england', 'germany', 'portugal', 'italy', 'netherlands',
        'belgium', 'croatia', 'switzerland', 'denmark', 'austria', 'turkey',
        'ukraine', 'poland', 'czech republic', 'scotland', 'serbia', 'romania',
        'slovakia', 'slovenia', 'hungary', 'albania', 'georgia'
    }
    
    text_lower = str(text).lower()
    found = set()
    
    for team in teams:
        if team in text_lower:
            found.add(team)
    
    return found


def extract_events(text):
    """Extract event types from text"""
    if pd.isna(text):
        return set()
    
    text_lower = str(text).lower()
    found = set()
    
    for event in EVENT_TYPES:
        if event in text_lower:
            found.add(event)
    
    return found


def get_content_words(text):
    """Get content words (excluding linking words)"""
    if pd.isna(text):
        return []
    
    # Normalize and tokenize
    text = normalize_text(text)
    text = re.sub(r'[^\w\s]', ' ', text)  # Remove punctuation
    words = text.split()
    
    # Filter out linking words and short words
    content = [w for w in words if len(w) > 2 and w not in LINKING_WORDS]
    
    return content


def calculate_sentiment(text, debug=False):
    """Calculate sentiment score using RoBERTa model (-1 to 1 scale)
    
    Uses weighted average across all 3 probabilities (negative, neutral, positive)
    instead of just the highest class, to capture nuanced sentiment.
    """
    if pd.isna(text) or len(str(text).strip()) == 0:
        return None  # Return None for empty text (not 0)
    
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        
        # Truncate text to avoid issues
        text_clean = str(text)[:512]
        if len(text_clean.strip()) == 0:
            return None
        
        # Load model and tokenizer directly (not pipeline)
        model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        
        # Use cached model if available
        if not hasattr(calculate_sentiment, 'tokenizer'):
            calculate_sentiment.tokenizer = AutoTokenizer.from_pretrained(model_name)
            calculate_sentiment.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        
        tokenizer = calculate_sentiment.tokenizer
        model = calculate_sentiment.model
        
        # Tokenize
        inputs = tokenizer(text_clean, return_tensors="pt", truncation=True, max_length=512)
        
        # Get predictions
        with torch.no_grad():
            outputs = model(**inputs)
            scores = outputs.logits.squeeze()
        
        # Apply softmax to get probabilities
        probs = torch.nn.functional.softmax(scores, dim=0)
        
        # Calculate weighted average: -1 (negative) to +1 (positive)
        # Index 0 = negative, Index 1 = neutral, Index 2 = positive
        sentiment_score = -1 * probs[0] + 0 * probs[1] + 1 * probs[2]
        
        return sentiment_score.item()
        
    except Exception as e:
        # Log error without Unicode text
        is_goal_text = 'goooal' in str(text)[:100].lower() if text else False
        if is_goal_text:
            print(f"[ERROR] Sentiment failed for GOOOAL text: {type(e).__name__}")
        return None


def compare_commentaries(real_commentary, our_commentary):
    """Compare two commentaries with all metrics"""
    
    # Normalize texts
    real_norm = normalize_text(real_commentary)
    our_norm = normalize_text(our_commentary)
    
    metrics = {}
    
    # ===== 1. TF-IDF (Cosine Similarity) =====
    if real_norm and our_norm:
        try:
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([real_norm, our_norm])
            metrics['TF-IDF'] = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except:
            metrics['TF-IDF'] = 0.0
    else:
        metrics['TF-IDF'] = 0.0
    
    # ===== 2. Embeddings - BERT =====
    if real_norm and our_norm:
        try:
            embeddings = BERT_MODEL.encode([real_norm, our_norm])
            metrics['Embeddings_BERT'] = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        except:
            metrics['Embeddings_BERT'] = 0.0
    else:
        metrics['Embeddings_BERT'] = 0.0
    
    # ===== 3. Sentiment Analysis =====
    real_sent = calculate_sentiment(real_commentary)
    our_sent = calculate_sentiment(our_commentary)
    
    metrics['real_sentiment'] = real_sent if real_sent is not None else 0.0
    metrics['our_sentiment'] = our_sent if our_sent is not None else 0.0
    
    # Calculate diff (if both have valid sentiment)
    if real_sent is not None and our_sent is not None:
        metrics['sentiment_diff'] = abs(real_sent - our_sent)
    else:
        metrics['sentiment_diff'] = 0.0
    
    # ===== 4. Word Counts =====
    real_words = normalize_text(real_commentary).split()
    our_words = normalize_text(our_commentary).split()
    
    metrics['real_word_count'] = len(real_words)
    metrics['our_word_count'] = len(our_words)
    
    # Content words (without linking words)
    real_content = get_content_words(real_commentary)
    our_content = get_content_words(our_commentary)
    
    metrics['real_content_words'] = len(real_content)
    metrics['our_content_words'] = len(our_content)
    
    # Matching content words
    real_content_set = set(real_content)
    our_content_set = set(our_content)
    matching = real_content_set.intersection(our_content_set)
    
    metrics['matching_content_words'] = len(matching)
    
    # Content overlap ratio (Jaccard)
    union = real_content_set.union(our_content_set)
    metrics['content_overlap_ratio'] = len(matching) / len(union) if len(union) > 0 else 0.0
    
    # ===== 5. Entity Counts (Unique) =====
    real_players = extract_players(real_commentary)
    our_players = extract_players(our_commentary)
    matching_players = real_players.intersection(our_players)
    
    metrics['real_unique_players'] = len(real_players)
    metrics['our_unique_players'] = len(our_players)
    metrics['matching_players'] = len(matching_players)
    # NER match ratio for players
    metrics['entity_players_match'] = len(matching_players) / len(real_players) if len(real_players) > 0 else 0.0
    
    real_teams = extract_teams(real_commentary)
    our_teams = extract_teams(our_commentary)
    matching_teams = real_teams.intersection(our_teams)
    
    metrics['real_unique_teams'] = len(real_teams)
    metrics['our_unique_teams'] = len(our_teams)
    metrics['matching_teams'] = len(matching_teams)
    # NER match ratio for teams
    metrics['entity_teams_match'] = len(matching_teams) / len(real_teams) if len(real_teams) > 0 else 0.0
    
    real_events = extract_events(real_commentary)
    our_events = extract_events(our_commentary)
    matching_events = real_events.intersection(our_events)
    
    metrics['real_unique_events'] = len(real_events)
    metrics['our_unique_events'] = len(our_events)
    metrics['matching_events'] = len(matching_events)
    # NER match ratio for events
    metrics['entity_events_match'] = len(matching_events) / len(real_events) if len(real_events) > 0 else 0.0
    
    # ===== 6. Entity Repetitions =====
    # For players: count all mentions vs unique
    real_all_players = extract_players(real_commentary, normalize=False)
    our_all_players = extract_players(our_commentary, normalize=False)
    
    metrics['real_player_mentions'] = len(real_all_players)
    metrics['our_player_mentions'] = len(our_all_players)
    metrics['real_player_repetitions'] = max(0, len(real_all_players) - len(real_players))
    metrics['our_player_repetitions'] = max(0, len(our_all_players) - len(our_players))
    
    # For teams: count all mentions vs unique
    # Simple count of team mentions
    real_team_mentions = sum(str(real_commentary).lower().count(team) for team in real_teams)
    our_team_mentions = sum(str(our_commentary).lower().count(team) for team in our_teams)
    
    metrics['real_team_mentions'] = real_team_mentions
    metrics['our_team_mentions'] = our_team_mentions
    metrics['real_team_repetitions'] = max(0, real_team_mentions - len(real_teams))
    metrics['our_team_repetitions'] = max(0, our_team_mentions - len(our_teams))
    
    # For events: count all mentions vs unique
    real_event_mentions = sum(str(real_commentary).lower().count(event) for event in real_events)
    our_event_mentions = sum(str(our_commentary).lower().count(event) for event in our_events)
    
    metrics['real_event_mentions'] = real_event_mentions
    metrics['our_event_mentions'] = our_event_mentions
    metrics['real_event_repetitions'] = max(0, real_event_mentions - len(real_events))
    metrics['our_event_repetitions'] = max(0, our_event_mentions - len(our_events))
    
    return metrics


def get_match_teams(match_id):
    """Get team names for a match from matches data"""
    matches_file = os.path.join(PROJECT_ROOT, 'Data', 'matches_complete.csv')
    matches_df = pd.read_csv(matches_file)
    
    match = matches_df[matches_df['match_id'] == int(match_id)]
    if len(match) == 0:
        return None, None
    
    home = match.iloc[0]['home_team_name'].lower().replace(' ', '_')
    away = match.iloc[0]['away_team_name'].lower().replace(' ', '_')
    
    return home, away


def process_match(match_id):
    """Process one match comparison - processes ALL available real commentary sources"""
    
    print(f"\n{'='*80}")
    print(f"PROCESSING MATCH {match_id}")
    print(f"{'='*80}\n")
    
    # Get team names
    home, away = get_match_teams(match_id)
    if not home or not away:
        print(f"[ERROR] Could not find teams for match {match_id}")
        return 0
    
    print(f"Teams: {home} vs {away}")
    
    # Load our generated commentary
    our_file = os.path.join(RESEARCH_ROOT, '07_all_games_commentary', 'data', f'match_{match_id}_rich_commentary.csv')
    if not os.path.exists(our_file):
        print(f"[ERROR] Generated commentary not found: {our_file}")
        return 0
    
    our_df = pd.read_csv(our_file)
    print(f"[OK] Loaded generated commentary: {len(our_df)} events")
    
    # Find ALL available real commentary sources for this match
    team_combos = [
        f"{home}_{away}",
        f"{away}_{home}"
    ]
    
    sources_prefixes = ['flashscore', 'sports_mole', 'bbc', 'fox', 'espn']
    data_dir = os.path.join(RESEARCH_ROOT, '05_real_commentary_comparison', 'data')
    
    # Find all available sources
    available_sources = []
    for combo in team_combos:
        for prefix in sources_prefixes:
            potential_file = os.path.join(data_dir, f'{prefix}_{combo}_commentary.csv')
            if os.path.exists(potential_file):
                available_sources.append((prefix, potential_file))
    
    if not available_sources:
        print(f"[ERROR] No real commentary found for {home} vs {away}")
        print(f"   Tried: {team_combos}")
        return 0
    
    print(f"[OK] Found {len(available_sources)} real commentary source(s): {', '.join([s[0].upper() for s in available_sources])}")
    
    # Process each source
    sources_processed = 0
    
    for source_prefix, real_file in available_sources:
        print(f"\n{'-'*60}")
        print(f"Processing source: {source_prefix.upper()}")
        print(f"{'-'*60}")
        
        try:
            success = process_match_source(match_id, home, away, our_df, real_file, source_prefix)
            if success:
                sources_processed += 1
                print(f"[SUCCESS] {source_prefix.upper()} completed")
            else:
                print(f"[WARNING] {source_prefix.upper()} failed")
        except Exception as e:
            print(f"[ERROR] {source_prefix.upper()} error: {type(e).__name__}: {str(e)[:100]}")
    
    return sources_processed


def process_match_source(match_id, home, away, our_df, real_file, source_prefix):
    """Process one match with one specific real commentary source"""
    
    real_source = source_prefix.upper()    
    
    # SportsMole files have CSV formatting issues - skip bad lines
    if source_prefix == 'sports_mole':
        real_df = pd.read_csv(real_file, on_bad_lines='skip')
    else:
        real_df = pd.read_csv(real_file)
    print(f"[OK] Loaded real commentary: {len(real_df)} entries")
    
    # Create sequences from our commentary
    sequences = our_df.groupby('sequence_id').agg({
        'minute': 'first',
        'period': 'first',  # Include period for stoppage time filtering
        'sequence_commentary': 'first',
        'event_commentary': lambda x: ' '.join(x.dropna().astype(str))
    }).reset_index()
    
    print(f"[OK] Created {len(sequences)} sequences")
    
    # Detect commentary column name
    commentary_col = 'commentary_text' if 'commentary_text' in real_df.columns else 'commentary'
    
    # Compare row by row (each real commentary entry)
    results = []
    total_real_rows = len(real_df)
    
    print(f"\n[COMPARING] Processing {total_real_rows} real commentary rows...")
    
    # Check if real data has stoppage time column
    has_plus_time = 'plus_time' in real_df.columns
    
    for idx, real_row in real_df.iterrows():
        minute = real_row['minute']
        real_commentary = real_row[commentary_col]
        real_type = real_row.get('event_type', 'general')
        
        if pd.isna(real_commentary) or len(str(real_commentary).strip()) == 0:
            continue
        
        minute_int = int(minute)
        
        # Handle stoppage time using plus_time and period columns
        if has_plus_time:
            plus_time = int(real_row.get('plus_time', 0))
            
            if plus_time > 0:
                # STOPPAGE TIME: FlashScore N+P
                # For MATCHING: target_minute = N + P - 1
                # For PERIOD: determined by BASE minute (N)
                # For CSV: display FlashScore format with plus sign (e.g. "45+2", "90+4")
                target_minute = minute_int + plus_time - 1
                csv_minute = f"{minute_int}+{plus_time}"  # Display as "45+2", "90+4", etc.
                
                # Determine period based on BASE minute:
                if minute_int == 45:
                    target_period = 1  # First half stoppage
                elif minute_int == 90:
                    target_period = 2  # Second half stoppage
                elif minute_int == 105:
                    target_period = 3  # First extra time stoppage
                elif minute_int == 120:
                    target_period = 4  # Second extra time stoppage
                else:
                    # Shouldn't happen, but default to no period filter
                    target_period = None
                
                # Filter by BOTH minute AND period
                if target_period is not None:
                    our_sequences = sequences[
                        (sequences['minute'] == target_minute) & 
                        (sequences['period'] == target_period)
                    ]
                else:
                    our_sequences = sequences[sequences['minute'] == target_minute]
            else:
                # REGULAR TIME: FlashScore minute N → Our minute N-1
                target_minute = minute_int - 1
                csv_minute = minute_int  # Display original minute
                
                # Determine target period based on FlashScore minute
                if minute_int <= 45:
                    target_period = 1  # First half
                elif minute_int <= 90:
                    target_period = 2  # Second half
                elif minute_int <= 105:
                    target_period = 3  # First extra time
                elif minute_int <= 120:
                    target_period = 4  # Second extra time
                else:
                    target_period = None  # Shouldn't happen
                
                # Filter by BOTH minute AND period
                if target_period is not None:
                    our_sequences = sequences[
                        (sequences['minute'] == target_minute) & 
                        (sequences['period'] == target_period)
                    ]
                else:
                    our_sequences = sequences[sequences['minute'] == target_minute]
        else:
            # No plus_time column (Sports Mole, BBC, etc.): Simple conversion
            target_minute = minute_int - 1
            csv_minute = minute_int  # Display original minute
            
            # Determine target period based on FlashScore minute
            if minute_int <= 45:
                target_period = 1  # First half
            elif minute_int <= 90:
                target_period = 2  # Second half
            elif minute_int <= 105:
                target_period = 3  # First extra time
            elif minute_int <= 120:
                target_period = 4  # Second extra time
            else:
                target_period = None  # Shouldn't happen
            
            # Filter by BOTH minute AND period
            if target_period is not None:
                our_sequences = sequences[
                    (sequences['minute'] == target_minute) & 
                    (sequences['period'] == target_period)
                ]
            else:
                our_sequences = sequences[sequences['minute'] == target_minute]
        
        
        if len(our_sequences) == 0:
            # No generated commentary for this minute - still record it with empty metrics
            real_sent = calculate_sentiment(real_commentary)
            real_sent_val = real_sent if real_sent is not None else 0.0
            
            result = {
                'data_source': real_source,
                'minute': csv_minute,
                'real_commentary': real_commentary,
                'real_type': real_type,
                'our_sequence_commentary': '',
                'sequence_id': -1,
                'average_score': 0.0,
                'average_score_no_sentiment': 0.0,
                'TF-IDF': 0.0,
                'Embeddings_BERT': 0.0,
                'content_overlap_ratio': 0.0,
                'real_sentiment': real_sent_val,
                'our_sentiment': 0.0,
                'sentiment_diff': abs(real_sent_val),
                'real_word_count': len(normalize_text(real_commentary).split()),
                'our_word_count': 0,
                'real_content_words': len(get_content_words(real_commentary)),
                'our_content_words': 0,
                'matching_content_words': 0,
                'real_unique_players': len(extract_players(real_commentary)),
                'our_unique_players': 0,
                'matching_players': 0,
                'entity_players_match': 0.0,
                'real_unique_teams': len(extract_teams(real_commentary)),
                'our_unique_teams': 0,
                'matching_teams': 0,
                'entity_teams_match': 0.0,
                'real_unique_events': len(extract_events(real_commentary)),
                'our_unique_events': 0,
                'matching_events': 0,
                'entity_events_match': 0.0,
                'real_player_mentions': 0,
                'our_player_mentions': 0,
                'real_player_repetitions': 0,
                'our_player_repetitions': 0,
                'real_team_mentions': 0,
                'our_team_mentions': 0,
                'real_team_repetitions': 0,
                'our_team_repetitions': 0,
                'real_event_mentions': 0,
                'our_event_mentions': 0,
                'real_event_repetitions': 0,
                'our_event_repetitions': 0
            }
            results.append(result)
            continue
        
        # Calculate scores for each sequence in this minute
        for seq_idx, seq in our_sequences.iterrows():
            our_commentary = seq['sequence_commentary']
            
            if pd.isna(our_commentary) or len(str(our_commentary).strip()) == 0:
                continue
            
            # Calculate all metrics
            metrics = compare_commentaries(real_commentary, our_commentary)
            
            # Calculate average score (normalize main metrics to 0-1)
            avg_score = (
                metrics['TF-IDF'] +
                metrics['Embeddings_BERT'] +
                metrics['content_overlap_ratio'] +
                (1 - metrics['sentiment_diff'])  # Lower diff is better
            ) / 4
            
            # Calculate average score without sentiment
            avg_score_no_sentiment = (
                metrics['TF-IDF'] +
                metrics['Embeddings_BERT'] +
                metrics['content_overlap_ratio']
            ) / 3
            
            result = {
                'data_source': real_source,
                'minute': csv_minute,
                'real_commentary': real_commentary,
                'real_type': real_type,
                'our_sequence_commentary': our_commentary,
                'sequence_id': seq['sequence_id'],
                'average_score': avg_score,
                'average_score_no_sentiment': avg_score_no_sentiment,
                **metrics
            }
            
            results.append(result)
    
    # Create DataFrame
    results_df = pd.DataFrame(results)
    
    # Rank sequences within each minute
    results_df['sequence_rank'] = results_df.groupby('minute')['average_score'].rank(method='dense', ascending=False).astype(int)
    
    # Create sorting key for chronological order (handles stoppage time)
    def get_sort_key(minute_str):
        """Convert minute string to sortable value (e.g., '45+2' -> 45.2, '90' -> 90.0)"""
        if '+' in str(minute_str):
            base, plus = str(minute_str).split('+')
            return float(base) + (float(plus) / 100)  # 45+2 becomes 45.02
        else:
            return float(minute_str)
    
    results_df['_sort_key'] = results_df['minute'].apply(get_sort_key)
    
    # Sort chronologically by minute, then by rank within each minute
    results_df = results_df.sort_values(['_sort_key', 'sequence_rank'])
    results_df = results_df.drop(columns=['_sort_key'])  # Remove helper column
    
    # Reorder columns
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
    
    # Save results with source-specific filename
    output_file = os.path.join(SCRIPT_DIR, '..', 'data', f'match_{match_id}_{source_prefix}_enhanced_comparison.csv')
    results_df.to_csv(output_file, index=False)
    
    print(f"[SUCCESS] SAVED: match_{match_id}_{source_prefix}_enhanced_comparison.csv")
    print(f"   Total comparisons: {len(results_df)}")
    print(f"   Minutes covered: {results_df['minute'].nunique()}")
    print(f"   Average score: {results_df['average_score'].mean():.3f}")
    
    return True


def main():
    """Main execution"""
    if len(sys.argv) < 2:
        print("Usage: python enhanced_comparison.py <match_id>")
        sys.exit(1)
    
    match_id = sys.argv[1]
    sources_count = process_match(match_id)
    
    if sources_count > 0:
        print(f"\n{'='*80}")
        print(f"[SUCCESS] COMPARISON COMPLETE! - {sources_count} source(s) processed")
        print(f"{'='*80}\n")
    else:
        print(f"\n{'='*80}")
        print("[FAILED] COMPARISON FAILED - No sources processed")
        print(f"{'='*80}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

