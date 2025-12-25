"""
Add NER (Named Entity Recognition) metric to existing comparison CSVs
Uses regex-based entity extraction optimized for football commentary
"""

import pandas as pd
import re
import unicodedata
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# Euro 2024 teams for entity recognition
EURO_TEAMS = {
    'germany', 'scotland', 'hungary', 'switzerland', 'spain', 'croatia', 
    'italy', 'albania', 'slovenia', 'denmark', 'serbia', 'england',
    'poland', 'netherlands', 'austria', 'france', 'belgium', 'slovakia',
    'romania', 'ukraine', 'turkey', 'georgia', 'portugal', 'czech republic',
    'czechia'
}

# Event keywords
EVENT_KEYWORDS = {
    'goal', 'shot', 'save', 'corner', 'free kick', 'penalty', 'foul',
    'yellow card', 'red card', 'substitution', 'offside', 'header',
    'cross', 'pass', 'tackle', 'block', 'clearance', 'assist'
}

print("Using regex-based NER for football commentary")


def normalize_name(name):
    """Normalize a name for comparison."""
    name = str(name).lower().strip()
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    return name


def extract_entities_ner(text):
    """Extract entities using regex patterns optimized for football."""
    if pd.isna(text) or len(str(text).strip()) == 0:
        return {'PERSON': set(), 'TEAM': set(), 'EVENT': set()}
    
    text_str = str(text)
    text_lower = text_str.lower()
    
    entities = {'PERSON': set(), 'TEAM': set(), 'EVENT': set()}
    
    # Extract player names (Capitalized words, often with nationality in parentheses)
    player_pattern = r'\b([A-Z][a-zÀ-ÿ]+(?:\s+[A-Z][a-zÀ-ÿ]+)*)\s*(?:\([A-Z][a-z]+\))?'
    potential_players = re.findall(player_pattern, text_str)
    
    # Filter out non-player names
    excluded = {
        'The', 'This', 'That', 'Good', 'Great', 'Brilliant', 'Perfect', 'Goal',
        'Shot', 'Save', 'Corner', 'Half', 'First', 'Second', 'Final', 'Group',
        'Stage', 'Match', 'Game', 'Time', 'Added', 'Extra', 'Penalty', 'VAR',
        'Attempt', 'Foul', 'Card', 'Yellow', 'Red', 'Substitution', 'Free',
        'Kick', 'Header', 'Cross', 'Pass', 'Tackle', 'Block', 'Euro'
    }
    
    for name in potential_players:
        name_clean = name.strip()
        if name_clean and name_clean not in excluded:
            if name_clean.lower() not in EURO_TEAMS:
                entities['PERSON'].add(normalize_name(name_clean))
    
    # Extract teams
    for team in EURO_TEAMS:
        if team in text_lower:
            entities['TEAM'].add(team)
    
    # Extract events
    for event in EVENT_KEYWORDS:
        if event in text_lower:
            entities['EVENT'].add(event)
    
    return entities


def calculate_ner_score(real_text, llm_text):
    """Calculate NER-based similarity between texts."""
    real_ents = extract_entities_ner(real_text)
    llm_ents = extract_entities_ner(llm_text)
    
    total_match = 0
    total_real = 0
    
    # Weight: PERSON most important, then TEAM, then EVENT
    weights = {'PERSON': 2.0, 'TEAM': 1.5, 'EVENT': 1.0}
    
    for ent_type in ['PERSON', 'TEAM', 'EVENT']:
        real_set = real_ents[ent_type]
        llm_set = llm_ents[ent_type]
        weight = weights[ent_type]
        
        if len(real_set) > 0:
            matching = 0
            for real_ent in real_set:
                for llm_ent in llm_set:
                    if real_ent == llm_ent:
                        matching += 1
                        break
                    elif real_ent in llm_ent or llm_ent in real_ent:
                        matching += 0.5
                        break
            
            total_match += matching * weight
            total_real += len(real_set) * weight
    
    if total_real > 0:
        return min(1.0, total_match / total_real)
    else:
        llm_total = sum(len(llm_ents[t]) for t in ['PERSON', 'TEAM', 'EVENT'])
        return 1.0 if llm_total == 0 else 0.5


def process_csv(csv_path):
    """Add NER score column to a CSV file."""
    print(f"Processing: {csv_path.name}")
    
    df = pd.read_csv(csv_path)
    
    # Check if NER column already exists
    if 'ner_score' in df.columns:
        print(f"  [SKIP] NER column already exists")
        return
    
    # Determine column names (08 uses different names)
    real_col = 'real_commentary' if 'real_commentary' in df.columns else None
    gen_col = 'our_sequence_commentary' if 'our_sequence_commentary' in df.columns else None
    
    if not real_col or not gen_col:
        print(f"  [ERROR] Could not find commentary columns")
        return
    
    # Calculate NER scores
    ner_scores = []
    total = len(df)
    
    for idx, row in df.iterrows():
        real_text = row.get(real_col, '')
        gen_text = row.get(gen_col, '')
        
        ner_score = calculate_ner_score(real_text, gen_text)
        ner_scores.append(ner_score)
        
        if (idx + 1) % 100 == 0:
            print(f"  Progress: {idx + 1}/{total} ({100*(idx+1)/total:.1f}%)")
    
    # Add NER column
    df['ner_score'] = ner_scores
    
    # Save updated CSV
    df.to_csv(csv_path, index=False)
    print(f"  [DONE] Added NER column, avg NER score: {df['ner_score'].mean():.3f}")


def main():
    """Process all comparison CSVs."""
    data_dir = Path(__file__).parent.parent / 'data'
    csv_files = list(data_dir.glob('match_*_enhanced_comparison.csv'))
    
    print(f"Found {len(csv_files)} CSV files to process")
    print("=" * 60)
    
    for csv_file in csv_files:
        process_csv(csv_file)
    
    print("=" * 60)
    print(f"[DONE] Processed {len(csv_files)} files")


if __name__ == "__main__":
    main()

