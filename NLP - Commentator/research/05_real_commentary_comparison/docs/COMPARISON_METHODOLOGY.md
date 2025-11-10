# Commentary Comparison Methodology

**Project:** Euro 2024 NLP Commentator - Phase 5  
**Date:** October 2025  
**Purpose:** Detailed methodology for comparing generated vs real professional commentary

---

## 📋 Overview

This document defines the step-by-step approach for comparing our generated event-level commentary with Sports Mole's minute-level professional commentary.

**Key Challenge:** Our data is **play-by-play** (event-level), Sports Mole is **minute-by-minute** (minute-level)

**Solution:** **1-minute aggregation** strategy

---

## 🎯 Comparison Strategy

### **Core Principle: Sequence-to-Minute Alignment**

```
Our Data:         [Event 1] → [Event 2] → [Event 3] → ... → [Event N]
                  All in minute 47

Aggregation:      Sequence Commentary for minute 47

Sports Mole:      Single minute 47 entry

Comparison:       Sequence Commentary ↔ Sports Mole Entry
```

**Why this works:**
- ✅ Both are narrative summaries
- ✅ Similar text lengths
- ✅ Our sequences already group related events
- ✅ Fair comparison of storytelling ability

---

## 📊 Three Comparison Metrics

### **Metric 1: Cosine Similarity (Lexical Similarity)**

**What it measures:** How similar are the actual words used?

**Method:**
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Example
your_text = "Nicholas Williams shoots with left foot from close range - GOAL! Spain 1-0"
sm_text = "Williams bursts into the box before firing into the bottom corner - GOAL Spain 1-0"

vectorizer = TfidfVectorizer()
vectors = vectorizer.fit_transform([your_text, sm_text])
similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

# Result: 0.4-0.7 (moderate-high similarity)
```

**Expected Range:**
- 0.6-0.8: Excellent match (same words, same structure)
- 0.4-0.6: Good match (similar words, slight variations)
- 0.2-0.4: Moderate match (different words, same meaning)
- <0.2: Poor match (completely different)

**Why not 1.0?**
- Different writing styles (data-driven vs journalistic)
- Synonym usage (shoots vs fires, receives vs collects)
- Different detail levels

---

### **Metric 2: Entity Overlap (Information Completeness)**

**What it measures:** How much key information is shared?

**Entities to Extract:**
1. **Player names** (e.g., "Williams", "Palmer")
2. **Actions** (e.g., "shoots", "passes", "dribbles")
3. **Locations** (e.g., "box", "corner", "left wing")
4. **Outcomes** (e.g., "GOAL", "saved", "blocked")
5. **Scores** (e.g., "1-0", "1-1")
6. **Body parts** (e.g., "left foot", "header")
7. **Teams** (e.g., "Spain", "England")

**Method:**
```python
import spacy
nlp = spacy.load('en_core_web_sm')

def extract_entities(text):
    doc = nlp(text)
    entities = {
        'players': [ent.text for ent in doc.ents if ent.label_ == 'PERSON'],
        'actions': [token.lemma_ for token in doc if token.pos_ == 'VERB'],
        'locations': [chunk.text for chunk in doc.noun_chunks if 'box' in chunk.text or 'corner' in chunk.text],
        'outcome': 'GOAL' if 'GOAL' in text else 'attempt',
        'score': extract_score(text)  # Custom regex function
    }
    return entities

def calculate_overlap(your_entities, sm_entities):
    overlaps = {
        'player': any(p in str(sm_entities['players']) for p in your_entities['players']),
        'action': any(a in str(sm_entities['actions']) for a in your_entities['actions']),
        'location': any(l in str(sm_entities['locations']) for l in your_entities['locations']),
        'outcome': your_entities['outcome'] == sm_entities['outcome'],
        'score': your_entities['score'] == sm_entities['score']
    }
    
    overlap_score = sum(overlaps.values()) / len(overlaps)
    return overlap_score, overlaps

# Example
your_ent = {'players': ['Williams'], 'actions': ['shoot'], 'location': ['close range'], 'outcome': 'GOAL', 'score': '1-0'}
sm_ent = {'players': ['Williams'], 'actions': ['fire'], 'location': ['corner'], 'outcome': 'GOAL', 'score': '1-0'}

overlap, details = calculate_overlap(your_ent, sm_ent)
# Result: 4/5 = 0.80 (80% overlap)
```

**Expected Range:**
- 0.8-1.0: Excellent - All key information matches
- 0.6-0.8: Good - Most information matches
- 0.4-0.6: Moderate - Some key info missing
- <0.4: Poor - Major information gaps

---

### **Metric 3: Semantic Similarity (Meaning Similarity)**

**What it measures:** Do both describe the same meaning, regardless of words?

**Method:**
```python
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine

model = SentenceTransformer('all-MiniLM-L6-v2')

your_text = "Williams shoots with left foot from close range - GOAL! Spain 1-0"
sm_text = "Williams bursts into box before firing into bottom corner - GOAL Spain 1-0"

# Get embeddings (vector representations of meaning)
your_embedding = model.encode(your_text)
sm_embedding = model.encode(sm_text)

# Calculate semantic similarity
semantic_sim = 1 - cosine(your_embedding, sm_embedding)

# Result: 0.75-0.95 (high semantic similarity)
```

**Expected Range:**
- 0.85-1.0: Excellent - Nearly identical meaning
- 0.70-0.85: Good - Same core meaning, slight nuance differences
- 0.50-0.70: Moderate - Related meaning, different focus
- <0.50: Poor - Different meanings

**Why this matters:**
- "shoots" vs "fires" = Same semantic concept (0.95 similarity)
- "close range" vs "into the box" = Similar concepts (0.85 similarity)
- "left foot" vs "left-footed strike" = Same meaning (0.90 similarity)

---

## 🔄 Data Preparation Pipeline

### **Phase 1: Extract Sports Mole Data**

**Input:** Sports Mole HTML page

**Process:**
1. Navigate to match page
2. Find all commentary entries
3. Extract minute + text for each entry

**Output Format:**
```csv
match_id,minute,second,commentary_text,team_focus,players_mentioned
final,0,0,"KICKOFF: England kick us off here...",England,[]
final,3,0,"Shaw wins his first battle against Yamal, knocking the Barcelona teenager to the ground",England,"['Shaw','Yamal']"
final,47,0,"GOAL! Spain 1-0 England (Williams 47'): The ball is worked to Williams on the left, and the Athletic forward bursts into the box before firing into the bottom corner",Spain,['Williams']
final,73,0,"GOAL! Spain 1-1 England (Palmer 73'): England are level! Palmer collects a pass from Bellingham before curling one into the far corner",England,"['Palmer','Bellingham']"
final,86,0,"GOAL! Spain 2-1 England (Oyarzabal 86'): Spain are back ahead! Cucurella delivers a low cross into the box, and Oyarzabal slides in to convert",Spain,"['Oyarzabal','Cucurella']"
```

**File:** `05_real_commentary_comparison/data/sports_mole_[match]_commentary.csv`

---

### **Phase 2: Aggregate Our Data by Minute**

**Input:** `04_final_game_production/data/final_game_rich_commentary.csv`

**Process:**
```python
import pandas as pd

# Load our data
our_data = pd.read_csv('final_game_rich_commentary.csv')

# Group by minute
minute_aggregated = []

for minute in range(0, 95):  # 0-94 minutes
    minute_events = our_data[our_data['minute'] == minute]
    
    if len(minute_events) > 0:
        # Get sequence commentary (already aggregated)
        sequence_commentary = minute_events['sequence_commentary'].iloc[0]
        
        # Or concatenate individual event commentaries
        event_commentaries = minute_events['event_commentary'].tolist()
        
        # Get event count
        event_count = len(minute_events)
        
        # Identify key events
        has_goal = (minute_events['is_goal'] == True).any()
        has_shot = (minute_events['event_type'] == 'Shot').any()
        has_substitution = (minute_events['event_type'] == 'Substitution').any()
        
        minute_aggregated.append({
            'minute': minute,
            'event_count': event_count,
            'sequence_commentary': sequence_commentary,
            'event_commentaries': event_commentaries,
            'has_goal': has_goal,
            'has_shot': has_shot,
            'has_substitution': has_substitution,
            'key_players': minute_events['player_name'].unique().tolist()
        })

# Save
pd.DataFrame(minute_aggregated).to_csv('our_commentary_by_minute.csv', index=False)
```

**Output Format:**
```csv
minute,event_count,sequence_commentary,has_goal,has_shot,key_players
0,15,"[0:00-0:15] England kicks off, Bellingham receives...",False,False,"['Bellingham','Kane']"
47,23,"[47:21] Williams receives from Cucurella, carries forward, shoots - GOAL! Spain 1-0",True,True,['Williams','Cucurella','Pickford']
73,18,"[73:14] Palmer receives from Bellingham, shoots - GOAL! England equalizes 1-1",True,True,"['Palmer','Bellingham']"
```

**File:** `05_real_commentary_comparison/data/our_commentary_by_minute.csv`

---

### **Phase 3: Align Data for Comparison**

**Process:**
```python
# Load both datasets
sm_data = pd.read_csv('sports_mole_final_commentary.csv')
our_data = pd.read_csv('our_commentary_by_minute.csv')

# Merge on minute
aligned_data = pd.merge(
    our_data, 
    sm_data, 
    on='minute', 
    how='inner',  # Only minutes present in both
    suffixes=('_ours', '_sm')
)

# Result: Side-by-side comparison
aligned_data.to_csv('aligned_commentary_comparison.csv', index=False)
```

**Output Format:**
```csv
minute,sequence_commentary_ours,commentary_text_sm,has_goal,event_count
47,"Williams receives, carries, shoots - GOAL! Spain 1-0","Williams bursts into box, fires into corner - GOAL Spain 1-0",True,23
73,"Palmer receives from Bellingham, shoots - GOAL! 1-1","Palmer collects pass from Bellingham, curls into corner - GOAL 1-1",True,18
```

---

## 🎯 Comparison Levels

### **Level 1: Key Moments (Goals) - Priority 1**

**Why:** Most detailed commentary in both sources

**Events to Compare:**
1. Williams Goal (47') - Spain 1-0
2. Palmer Goal (73') - England 1-1
3. Oyarzabal Goal (86') - Spain 2-1

**Comparison:**
```python
goals = aligned_data[aligned_data['has_goal'] == True]

for _, goal in goals.iterrows():
    minute = goal['minute']
    your_text = goal['sequence_commentary_ours']
    sm_text = goal['commentary_text_sm']
    
    # Calculate metrics
    cosine_sim = calculate_cosine_similarity(your_text, sm_text)
    entity_overlap = calculate_entity_overlap(your_text, sm_text)
    semantic_sim = calculate_semantic_similarity(your_text, sm_text)
    
    print(f"Minute {minute} - Goal")
    print(f"  Cosine Similarity: {cosine_sim:.3f}")
    print(f"  Entity Overlap: {entity_overlap:.3f}")
    print(f"  Semantic Similarity: {semantic_sim:.3f}")
```

**Expected Results:**
```
Minute 47 - Williams Goal
  Cosine Similarity: 0.550
  Entity Overlap: 0.900
  Semantic Similarity: 0.850

Minute 73 - Palmer Goal
  Cosine Similarity: 0.620
  Entity Overlap: 0.950
  Semantic Similarity: 0.880

Minute 86 - Oyarzabal Goal
  Cosine Similarity: 0.580
  Entity Overlap: 0.850
  Semantic Similarity: 0.820

Average - Goals (n=3)
  Cosine Similarity: 0.583 ± 0.029
  Entity Overlap: 0.900 ± 0.041
  Semantic Similarity: 0.850 ± 0.025
```

---

### **Level 2: Shot Events - Priority 2**

**Why:** 25 shots in match, good sample size

**Events to Compare:**
- All 25 shot events where Sports Mole has commentary

**Process:**
```python
shots = aligned_data[aligned_data['has_shot'] == True]

shot_metrics = {
    'cosine_sims': [],
    'entity_overlaps': [],
    'semantic_sims': []
}

for _, shot in shots.iterrows():
    your_text = shot['sequence_commentary_ours']
    sm_text = shot['commentary_text_sm']
    
    shot_metrics['cosine_sims'].append(calculate_cosine_similarity(your_text, sm_text))
    shot_metrics['entity_overlaps'].append(calculate_entity_overlap(your_text, sm_text))
    shot_metrics['semantic_sims'].append(calculate_semantic_similarity(your_text, sm_text))

# Calculate averages
print(f"Shots (n={len(shots)})")
print(f"  Cosine Similarity: {np.mean(shot_metrics['cosine_sims']):.3f} ± {np.std(shot_metrics['cosine_sims']):.3f}")
print(f"  Entity Overlap: {np.mean(shot_metrics['entity_overlaps']):.3f} ± {np.std(shot_metrics['entity_overlaps']):.3f}")
print(f"  Semantic Similarity: {np.mean(shot_metrics['semantic_sims']):.3f} ± {np.std(shot_metrics['semantic_sims']):.3f}")
```

**Expected Results:**
```
Shots (n=25)
  Cosine Similarity: 0.420 ± 0.120
  Entity Overlap: 0.720 ± 0.150
  Semantic Similarity: 0.680 ± 0.180
```

---

### **Level 3: Full Match Sample - Priority 3**

**Why:** Overall commentary style comparison

**Events to Compare:**
- Every 10th minute: 0, 10, 20, 30, 40, 50, 60, 70, 80, 90
- Total: 10 comparison points

**Process:**
```python
sample_minutes = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
sample_data = aligned_data[aligned_data['minute'].isin(sample_minutes)]

# Calculate metrics for sample
# ... same as above
```

**Expected Results:**
```
Full Match Sample (n=10)
  Cosine Similarity: 0.380 ± 0.150
  Entity Overlap: 0.650 ± 0.200
  Semantic Similarity: 0.620 ± 0.220
```

---

## 📊 Results Analysis Framework

### **Comparison Table:**

```csv
comparison_id,minute,event_type,our_commentary,sm_commentary,cosine_sim,entity_overlap,semantic_sim,quality_rating
1,47,Goal,"Williams receives, carries, shoots - GOAL! Spain 1-0","Williams bursts into box, fires into corner - GOAL Spain 1-0",0.550,0.900,0.850,Excellent
2,73,Goal,"Palmer receives from Bellingham, shoots - GOAL! 1-1","Palmer collects pass from Bellingham, curls into corner - GOAL 1-1",0.620,0.950,0.880,Excellent
3,86,Goal,"Oyarzabal shoots - GOAL! Spain 2-1","Oyarzabal slides in to convert - GOAL Spain 2-1",0.580,0.850,0.820,Excellent
4,15,Pass,"Bellingham receives, plays to Kane","Bellingham finds Kane with a long ball",0.420,0.750,0.680,Good
5,62,Shot,"Saka shoots from distance - saved","Saka tries from range, Pickford saves",0.450,0.700,0.720,Good
```

### **Quality Rating Scale:**

| Score Range | Rating | Interpretation |
|-------------|--------|----------------|
| 0.80-1.00 | Excellent | Nearly identical, professional quality |
| 0.60-0.80 | Good | Strong match, minor differences |
| 0.40-0.60 | Moderate | Acceptable, noticeable differences |
| 0.20-0.40 | Fair | Significant gaps |
| 0.00-0.20 | Poor | Minimal similarity |

### **Overall Assessment:**

**Calculation:**
```python
# Weight the metrics
overall_score = (
    0.25 * cosine_similarity +
    0.35 * entity_overlap +
    0.40 * semantic_similarity
)

# Rationale:
# - Entity Overlap (35%): Most important - do we capture key info?
# - Semantic Similarity (40%): Very important - same meaning?
# - Cosine Similarity (25%): Less important - exact words matter less
```

**Example:**
```
Goal at 47':
  Cosine: 0.550 × 0.25 = 0.138
  Entity: 0.900 × 0.35 = 0.315
  Semantic: 0.850 × 0.40 = 0.340
  Overall: 0.793 (Good quality)
```

---

## 🎯 Why 1-Minute Aggregation Works

### **Problem Solved:**

**Before (Event-level comparison):**
```
Your Event 1: "Rodri passes to Olmo" (5 words)
Your Event 2: "Olmo receives" (2 words)
Your Event 3: "Olmo dribbles forward" (3 words)
Your Event 4: "Olmo shoots - saved!" (4 words)

Sports Mole: "Olmo collects pass from Rodri, drives forward and shoots but it's saved" (13 words)

Problem: Comparing 4 short texts vs 1 long text = unfair, low similarity
```

**After (Sequence-level comparison):**
```
Your Sequence: "Olmo receives from Rodri in midfield, drives forward with the ball into attacking third, shoots from distance - saved by goalkeeper" (23 words)

Sports Mole: "Olmo collects pass from Rodri, drives forward and shoots but it's saved" (13 words)

Solution: Both are narrative summaries = fair comparison, high similarity
```

### **Benefits:**

✅ **Fair Text Length:** Both ~10-30 words  
✅ **Same Narrative Level:** Both tell a story, not just label events  
✅ **Contextual:** Both include build-up and outcome  
✅ **Natural Granularity:** Matches how humans describe football  
✅ **Meaningful Metrics:** Similarity scores are interpretable

---

## 📝 Implementation Checklist

### **Phase 1: Data Collection** (Week 1)
- [ ] Extract Sports Mole commentary for Final
- [ ] Extract Sports Mole commentary for England-Netherlands
- [ ] Extract Sports Mole commentary for Spain-France
- [ ] Save as CSVs in `data/` folder

### **Phase 2: Data Preparation** (Week 1)
- [ ] Aggregate our data by minute
- [ ] Align both datasets on minute
- [ ] Identify key moments (goals, shots, substitutions)
- [ ] Save aligned data

### **Phase 3: Comparison** (Week 2)
- [ ] Implement cosine similarity calculation
- [ ] Implement entity overlap calculation
- [ ] Implement semantic similarity calculation
- [ ] Run on all key moments

### **Phase 4: Analysis** (Week 2)
- [ ] Generate comparison tables
- [ ] Calculate aggregate metrics
- [ ] Identify patterns (what works well, what needs improvement)
- [ ] Create visualizations

### **Phase 5: Documentation** (Week 3)
- [ ] Write comparison results report
- [ ] Document insights and learnings
- [ ] Update templates based on findings
- [ ] Create recommendations for improvement

---

## 🚀 Expected Outcomes

### **Quantitative Results:**
- Cosine Similarity: 0.4-0.7 (moderate-high)
- Entity Overlap: 0.7-0.9 (high)
- Semantic Similarity: 0.75-0.90 (high)
- Overall Quality Score: 0.65-0.80 (Good)

### **Qualitative Insights:**
- Which event types have highest similarity?
- Where do we excel vs struggle?
- What language patterns should we adopt?
- Which templates need refinement?

### **Actionable Improvements:**
- Template updates based on real examples
- Vocabulary enrichment
- Narrative flow improvements
- Detail level adjustments

---

## 📁 Output Files

All comparison results will be saved in:
```
05_real_commentary_comparison/
├── data/
│   ├── sports_mole_final_commentary.csv
│   ├── sports_mole_eng_ned_commentary.csv
│   ├── sports_mole_spa_fra_commentary.csv
│   ├── our_commentary_by_minute.csv
│   ├── aligned_commentary_final.csv
│   └── comparison_results.csv
├── docs/
│   ├── DATA_SOURCES_EVALUATION.md (this file's companion)
│   ├── COMPARISON_METHODOLOGY.md (this file)
│   └── COMPARISON_RESULTS.md (to be created)
└── scripts/
    ├── extract_sports_mole.py
    ├── aggregate_our_data.py
    ├── calculate_metrics.py
    └── generate_report.py
```

---

**Status:** ✅ Methodology defined, ready for implementation  
**Next Step:** Extract Sports Mole data for 3 matches

