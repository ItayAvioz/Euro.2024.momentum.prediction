# NLP Commentator - Euro 2024 Match Commentary Generation

## 🎯 Project Overview

This module aims to create an **AI-powered match commentator** that generates natural language commentary from Euro 2024 event data, integrated with momentum predictions.

## 📊 Training Dataset

### Dataset Composition
- **Total Events**: 144 events
- **Total Sequences**: 30 sequences  
- **Matches**: 3 exciting games
- **Sequence Length**: 2-5 events per sequence

### Selected Matches
1. **3943043**: Spain 2-1 England (Final) - Dramatic winner by Mikel Oyarzabal
2. **3942226**: Spain 2-1 Germany (Quarter-finals) - Extra time thriller with Mikel Merino's winner
3. **3941017**: England 2-1 Slovakia (Round of 16) - Bellingham's bicycle kick equalizer + extra time

### Sequence Types
- **Shot Sequences**: 15 (60 events) - Goals, saves, dangerous attempts
- **Dribble Sequences**: 7 (30 events) - Skill moves and take-ons
- **Pressure Sequences**: 7 (30 events) - High-pressure moments
- **Carry Sequences**: 6 (24 events) - Attacking runs with the ball

## 📋 Data Structure

### Key Columns for Commentary Generation

#### PRIMARY COLUMNS (Essential)
1. **minute, second, period** - Temporal context
   - Example: `minute: 67, second: 42, period: 2`
   - Usage: "In the 67th minute of the second half..."

2. **type** - Event type (JSON format)
   - Example: `{'id': 16, 'name': 'Shot'}`
   - Usage: Extract the 'name' field for event description

3. **player, team** - Actor identification (JSON format)
   - Example: `{'id': 5597, 'name': 'Lamine Yamal Nasraoui Ebana'}`
   - Usage: "Yamal drives forward for Spain..."

4. **location** - Field coordinates (JSON string)
   - Example: `[92.0, 38.0]`
   - Conversion: x=92, y=38 → "From the edge of the penalty area..."

5. **shot, pass, dribble, carry** - Event-specific details (JSON)
   - Contains: outcomes, body parts, distances, end locations
   - Example shot: `{'outcome': {'name': 'Goal'}, 'body_part': {'name': 'Right Foot'}}`

#### CONTEXTUAL COLUMNS (Add richness)
6. **under_pressure** - Boolean indicating pressure
7. **play_pattern** - Game phase context
8. **position** - Player position (JSON)
9. **duration** - Event duration in seconds
10. **related_events** - Chain of connected events

#### MATCH CONTEXT
11. **home_team_name, away_team_name** - Team names
12. **possession_team** - Current possession (JSON)
13. **timestamp** - Exact game timestamp

#### SEQUENCE METADATA (NLP Training)
14. **sequence_id** - Unique sequence identifier (1-30)
15. **sequence_type** - shot_sequence, dribble_sequence, pressure_sequence, carry_sequence
16. **sequence_key_event** - Main event in sequence (Shot, Dribble, Carry, Pressure)
17. **event_position** - Position in sequence (1, 2, 3, 4, 5)
18. **sequence_length** - Total events in sequence
19. **is_key_event** - True/False - identifies the climax

## 🎙️ Commentary Generation Strategy

### 1. **Context Building**
```
For each event at position N:
- Look at events 1 to N-1 in same sequence for build-up
- Use event_position to understand narrative flow
- Identify is_key_event=True as the climax for emphasis
```

### 2. **Location Parsing**
```python
def parse_location(location_str):
    """
    Convert [x, y] coordinates to natural language
    
    Field dimensions: 120x80 yards
    - x: 0 (own goal) → 120 (opponent goal)
    - y: 0 (left touchline) → 80 (right touchline)
    
    Zones:
    - x < 40: Defensive third
    - 40 ≤ x < 80: Middle third
    - x ≥ 80: Attacking third / final third
    - 102 ≤ x ≤ 120, 18 ≤ y ≤ 62: Penalty area
    """
    # Parse coordinates
    coords = eval(location_str)  # [x, y]
    x, y = coords[0], coords[1]
    
    # Determine zone
    if x >= 102 and 18 <= y <= 62:
        return "inside the penalty area"
    elif x >= 80:
        return "in the final third"
    elif x >= 40:
        return "in midfield"
    else:
        return "in the defensive third"
```

### 3. **Event Type Parsing**
```python
def parse_event_type(type_str):
    """Extract event name from JSON-like string"""
    type_dict = eval(type_str)  # {'id': 16, 'name': 'Shot'}
    return type_dict['name']  # 'Shot'
```

### 4. **Player/Team Parsing**
```python
def parse_player(player_str):
    """Extract player name from JSON"""
    player_dict = eval(player_str)  # {'id': 5597, 'name': 'Lamine Yamal...'}
    full_name = player_dict['name']
    # Optionally extract last name for brevity
    return full_name.split()[-1]  # 'Yamal'
```

### 5. **Shot Outcome Parsing**
```python
def parse_shot_outcome(shot_str):
    """Extract shot outcome details"""
    if pd.isna(shot_str):
        return None
    shot_dict = eval(shot_str)
    
    outcome = shot_dict.get('outcome', {}).get('name', 'Unknown')
    body_part = shot_dict.get('body_part', {}).get('name', 'Unknown')
    
    # Translate to commentary
    commentary_map = {
        'Goal': 'finds the back of the net',
        'Saved': 'is saved by the goalkeeper',
        'Post': 'hits the post',
        'Off T': 'goes just wide',
        'Blocked': 'is blocked by the defender'
    }
    
    return commentary_map.get(outcome, 'takes a shot')
```

## 💡 Example Commentary Generation

### Example Sequence: Shot Sequence (Finale - Spain's Goal)

```
Sequence ID: 15 (shot_sequence)
Events: 5 events, key_event at position 5

Event 1 (position 1/5): 
  - Type: Ball Receipt
  - Player: Dani Olmo
  - Location: [95.0, 40.0] → "receives in the final third"
  - Commentary: "Olmo collects the ball in dangerous territory..."

Event 2 (position 2/5):
  - Type: Carry  
  - Player: Dani Olmo
  - Duration: 1.2 seconds
  - Location: [95.0, 40.0] → [98.0, 42.0]
  - Commentary: "drives forward towards the penalty area..."

Event 3 (position 3/5):
  - Type: Pass
  - Player: Dani Olmo
  - Under_pressure: True
  - Commentary: "under pressure, threads a pass..."

Event 4 (position 4/5):
  - Type: Ball Receipt
  - Player: Mikel Oyarzabal
  - Location: [105.0, 44.0] → "inside the penalty area"
  - Commentary: "picked up by Oyarzabal in the box..."

Event 5 (position 5/5) ★ KEY EVENT ★:
  - Type: Shot
  - Player: Mikel Oyarzabal
  - Minute: 86
  - Shot outcome: Goal
  - Body part: Right Foot
  - Location: [105.0, 44.0]
  - Commentary: "**Oyarzabal... GOAL! Spain take the lead in the 86th minute!**"

Full Sequence Commentary:
"In the 86th minute, Olmo collects the ball in dangerous territory, drives forward towards the penalty area, and under pressure, threads a pass into the box. Picked up by Oyarzabal... **GOAL! Spain take the lead with just minutes remaining in the final!**"
```

## 🔧 Implementation Steps

### Phase 1: Data Preprocessing ✅
- [x] Extract 30 event sequences from 3 matches
- [x] Include 2-5 consecutive events per sequence
- [x] Balance sequence types (shots, dribbles, carries, pressure)
- [x] Preserve all relevant columns
- [x] Add sequence metadata

### Phase 2: Feature Engineering (In Progress)
- [ ] Parse JSON fields (type, player, team, location)
- [ ] Convert coordinates to natural language zones
- [ ] Extract shot/pass/dribble outcomes
- [ ] Build temporal context (previous events in sequence)
- [ ] Integrate momentum predictions for each event

### Phase 3: NLP Model Development (Planned)
- [ ] Choose architecture (T5, GPT-2, BART, or custom LSTM)
- [ ] Create training pairs: (events + context) → commentary
- [ ] Fine-tune on sports commentary style
- [ ] Integrate momentum as input feature ("Team X has momentum...")

### Phase 4: Integration with Momentum (Planned)
- [ ] Calculate momentum for each event in sequence
- [ ] Use momentum as additional context
- [ ] Example: "With momentum swinging in Spain's favor, Yamal drives forward..."

### Phase 5: Evaluation & Refinement (Planned)
- [ ] BLEU/ROUGE scores for generated text
- [ ] Human evaluation for naturalness
- [ ] Sports vocabulary coverage
- [ ] Real-time generation speed testing

## 📈 Next Steps

1. **Parse all JSON fields** in the dataset
2. **Create location zone mapping** (coordinates → natural language)
3. **Build event templates** for each event type
4. **Generate baseline commentary** using rule-based templates
5. **Collect reference commentaries** for these sequences (if available)
6. **Train initial NLP model** (start with simpler sequence-to-sequence)
7. **Integrate momentum data** from existing models
8. **Evaluate and iterate**

## 📊 Files in This Directory

```
NLP - Commentator/
├── README.md                          # This file
└── research/
    ├── extract_commentator_data_simple.py      # Data extraction script
    ├── commentator_training_data.csv           # Training dataset (144 events)
    └── data_extraction_summary.md              # Extraction summary
```

## 🎯 Success Criteria

### Minimum Viable Product (MVP)
- Generate grammatically correct commentary for shot sequences
- Incorporate player names, locations, and outcomes
- Maintain temporal flow (previous events as context)

### Enhanced Version
- Natural, engaging commentary style
- Integrate momentum context ("Team X building momentum...")
- Handle all sequence types (shots, dribbles, carries, pressure)
- Real-time generation speed (< 1 second per event)

### Production Version
- Professional commentary quality
- Multiple commentary styles (technical, casual, dramatic)
- Multi-language support
- Integration with live data feeds
- Momentum prediction integration

---

**Status**: Phase 1 Complete ✅ | Phase 2 In Progress 🔄  
**Dataset**: 144 events across 30 sequences from 3 matches  
**Next**: JSON parsing and template generation
