# LLM Commentary Generation Process

## Overview

This document describes the complete process of generating ESPN-style football commentary using GPT-4o-mini. The system takes raw event data from StatsBomb and produces short, factual, classified commentary.

## BALANCED APPROACH

The key philosophy:
1. **Rich Data Extraction** - Extract ALL relevant data per event type
2. **ESPN Examples** - Show real examples for style learning
3. **LLM Freedom** - Model decides exact wording and what to include
4. **Pressure Only When Massive** - Only mention if >60% of events under pressure
5. **Event Chain Detection** - Link related events (Foul→Card, Shot→Corner, Pass→Goal)

## V3 ENHANCEMENTS

V3 adds intelligent handling of multiple events and progressive commentary:

| Feature | Logic | Example |
|---------|-------|---------|
| **Progressive General** | 1st general = basic, 2nd+ = domination streak | "Spain dominating for 3 minutes" |
| **Multiple Shots** | Same team = pressure, different = end-to-end | "Spain applying pressure! Two attempts" |
| **Multiple Corners** | Count + same/different teams | "Third corner for Spain" |
| **Multiple Fouls** | Count context (3+ = aggressive) | "Physical minute with 4 fouls" |
| **Multiple Substitutions** | Double/triple change detection | "Triple substitution for England" |
| **Multiple Offsides** | Same team = timing, different = open game | "Two offsides as both teams push forward" |
| **xG-based Shot Danger** | Prioritize most dangerous shot | Focus on highest xG shot |

## V4 ENHANCEMENTS: PENALTY HANDLING

V4 adds comprehensive penalty detection and commentary:

### Period 5 (Penalty Shootout)

| Feature | Logic | Example |
|---------|-------|---------|
| **Penalty Detection** | Shot events with `shot.type.name='Penalty'` | Detect each penalty kick |
| **Penalty Numbering** | Track penalty count (1, 2, 3...) | `[Penalty 3]` format |
| **Shootout Score** | Track running score separately from match | "Portugal 2-1 France in shootout" |
| **Goalkeeper on Save** | Extract from `goalkeeper` column | "Saved by Diogo Costa!" |
| **Skip Half Start** | Ignore Half Start events in Period 5 | No kick-off commentary |

### Period 1-4 (Penalties During Match)

| Feature | Logic | Example |
|---------|-------|---------|
| **Penalty Awarded** | Foul in box (location_x > 102) or play_pattern='From Penalty' | `[Penalty Awarded]` commentary |
| **Penalty Goal** | Shot with type='Penalty' and outcome='Goal' | `[Penalty Goal]` commentary |
| **Penalty Saved** | Shot with type='Penalty' and outcome='Saved' | `[Penalty Saved]` commentary |
| **Penalty Missed** | Shot with type='Penalty' and outcome='Post'/'Off T' | `[Penalty Missed]` commentary |
| **Card with Penalty** | Detect card in same minute | Separate `[Yellow Card]`/`[Red Card]` |

### Penalty Data Sources

| Column | Data | Used For |
|--------|------|----------|
| `shot` | `{'type': {'name': 'Penalty'}, 'outcome': {'name': 'Goal'}}` | Detect penalty shots |
| `goalkeeper` | `{'type': {'name': 'Save'}, 'outcome': {...}}` | Goalkeeper info on saves |
| `foul_committed` | Location, card info | Penalty awarded detection |
| `location_x` | X coordinate (>102 = penalty area) | Penalty foul detection |
| `play_pattern` | "From Penalty" | Penalty sequence detection |

### Penalty Commentary Examples

**Period 1-4:**
```
[Penalty Awarded] Penalty to Spain! Morata brought down by Walker in the box.
[Yellow Card] Kyle Walker (England) shown a yellow card for the challenge.
[Penalty Goal] Goal! Spain 1, England 0. Morata converts from the spot.
```

**Period 5 (Shootout):**
```
[Penalty 1] Dembélé (France) scores! France 1-0 Portugal in the shootout.
[Penalty 2] Ronaldo (Portugal) - Goal! Shootout tied 1-1.
[Penalty 5] João Félix (Portugal) - Hits the post! France leads 3-2.
[Penalty 6] Theo Hernández (France) - Saved by Diogo Costa!
```

## Target Output

ESPN-style commentary:
- Short: 5-15 words
- Factual: Player name, team, action
- Classified: `[Corner]`, `[Foul]`, `[Goal]`, etc.

### Examples
```
[Kick Off] First Half begins. Euro 2024 Final!
[Corner] Corner, Spain. Conceded by John Stones.
[Foul] Foul by Rodri (Spain) on Jude Bellingham (England).
[Goal] Goal! Spain 1, England 0. Nico Williams left footed shot from the left side of the box.
[General] Spain dominating possession, probing in midfield.
```

---

## Data Sources

### Primary: `euro_2024_complete_dataset.csv`

Contains the `related_events` column for linking events.

### Secondary: `match_XXXXXX_rich_commentary.csv`

Each match has ~2,500-4,000 event rows with 62 columns.

### Key Columns for Event Detection

| Column | Used For |
|--------|----------|
| `type` / `event_type` | Event detection (Shot, Foul, Pass) |
| `play_pattern` | Corner, Free Kick, Kick Off detection |
| `shot_outcome` | Goal, Saved, Blocked, Missed |
| `is_goal` | Goal detection (backup) |
| `pass_type` | Corner delivery detection |
| `pass_outcome` | Offside detection |
| `foul_committed` | Card info (embedded dict) |
| `bad_behaviour` | Card info (embedded dict) |
| `related_events` | Event linking (UUIDs) |
| `is_danger_zone` | Dangerous position flag |
| `under_pressure` | Pressure flag |

---

## Event Linking with `related_events`

### Data Structure

Each event has:
- `id` = unique UUID (e.g., `fb538032-230d-43b0-a57b-96d52747a583`)
- `related_events` = list of UUIDs pointing to connected events

### Example: Foul Connection

```
Event A (Foul Committed):
  id: fb538032-...
  type: Foul Committed
  player: Harry Kane (England)
  related_events: ['9b6209f1-...']  ← Points to Event B
  foul_committed: {'card': {'name': 'Yellow Card'}}

Event B (Foul Won):
  id: 9b6209f1-...
  type: Foul Won
  player: Fabián Ruiz (Spain)
  related_events: ['fb538032-...']  ← Points back to Event A
```

### Connection Types

| Connection | Method |
|------------|--------|
| **Foul Committed ↔ Foul Won** | `related_events` (exact match) |
| **Shot ↔ Assist Pass** | `related_events` (exact match) |
| **Shot ↔ Save/Block** | `related_events` (exact match) |
| **Foul ↔ Card** | Embedded in `foul_committed` column |
| **Foul → Free Kick** | `play_pattern` change (not linked) |
| **Shot Saved → Corner** | `play_pattern` change (not linked) |
| **Corner → Shot** | `play_pattern` = "From Corner" |

### Merging related_events (By Row Index)

Both files are ordered chronologically:
```python
# Both files have same order, merge by index
rich_df['related_events'] = match_complete['related_events'].values
rich_df['foul_committed_raw'] = match_complete['foul_committed'].values
rich_df['bad_behaviour_raw'] = match_complete['bad_behaviour'].values
rich_df['event_id'] = match_complete['id'].values
```

---

## Card Detection

Cards appear in **two columns**:

| Column | When Used | Example |
|--------|-----------|---------|
| `foul_committed` | Card for a foul | `{'card': {'name': 'Yellow Card'}}` |
| `bad_behaviour` | Card for non-foul (dissent, time wasting) | `{'card': {'name': 'Yellow Card'}}` |

### Extraction Logic

```python
def extract_card_info(row):
    card = None
    
    # Check foul_committed
    fc = row.get('foul_committed', '')
    if pd.notna(fc) and 'card' in str(fc).lower():
        data = ast.literal_eval(fc) if isinstance(fc, str) else fc
        if 'card' in data:
            card = data['card'].get('name')
    
    # Check bad_behaviour
    if card is None:
        bb = row.get('bad_behaviour', '')
        if pd.notna(bb) and 'card' in str(bb).lower():
            data = ast.literal_eval(bb) if isinstance(bb, str) else bb
            if 'card' in data:
                card = data['card'].get('name')
    
    return card
```

---

## Corner Detection

Corner is a **type of Pass** in StatsBomb data:

```
Event: Pass
  type: Pass
  pass_type: {'name': 'Corner'}
  play_pattern: From Corner
```

### Detection Methods

```python
# Method 1: Check pass_type (corner delivery)
corners = df[df['pass_type'].str.contains('Corner', na=False)]

# Method 2: Check play_pattern (events FROM a corner)
from_corner = df[df['play_pattern'].str.contains('Corner', na=False)]
```

### Corner Handling Rules

| Minute has... | Corner Action |
|---------------|---------------|
| Goal (from corner) | Goal commentary + corner context |
| Goal (not from corner) | Goal commentary only |
| Shot (from corner) | Shot commentary + corner context |
| Shot (not from corner) | Shot commentary only |
| Card | Card commentary only |
| Only Corner | **Present the corner!** |
| Multiple Corners | Present last corner + count |

### Corner Chain Detection

```python
def is_corner_related_to_event(major_event, minute_df):
    # Check if play_pattern indicates corner
    if major_event.get('play_pattern') == 'From Corner':
        return True
    
    # Check related_events
    related_ids = major_event.get('related_events', [])
    for rel_id in related_ids:
        related_event = minute_df[minute_df['id'] == rel_id]
        if 'Corner' in str(related_event.get('play_pattern', '')):
            return True
    
    return False
```

---

## Offside Detection

### Where to Find Offside

| Location | Column | Value |
|----------|--------|-------|
| Pass outcome | `pass_outcome` | `{'name': 'Offside'}` |
| Separate event | `type` | `Offside` |

### Offside Priority

| Context | Priority | Create Commentary? |
|---------|----------|-------------------|
| Cancels goal | #1 | ✅ Yes |
| Stops clear chance | #3 | ✅ Yes |
| Attacking third | #4 | ✅ Yes |
| Midfield | Skip | ❌ No |

### Detection Logic

```python
def detect_offside(minute_df):
    # Find offside in pass outcome
    offside_pass = minute_df[
        minute_df['pass_outcome'].str.contains('Offside', na=False)
    ]
    
    # Find offside event type
    offside_event = minute_df[
        minute_df['event_type'].str.contains('Offside', na=False)
    ]
    
    all_offside = pd.concat([offside_pass, offside_event])
    
    if len(all_offside) == 0:
        return None, False
    
    offside = all_offside.iloc[-1]
    
    # Check if dangerous (attacking third = x > 80)
    location_x = offside.get('location_x', 0)
    is_dangerous = location_x > 80
    
    return offside, is_dangerous
```

---

## Event Priority Order

```
1. Goal           → Present (with corner context if related)
2. Card           → Present (Yellow/Red)
3. Shot           → Present (with corner context if related)
4. Offside        → Present ONLY if dangerous (attacking third)
5. Substitution   → Present
6. Injury         → Present
7. Corner         → Present ONLY if nothing above exists
8. Foul           → Present
9. Free Kick      → Skip (foul already reported)
10. General       → Last resort
```

### Multiple Events in Same Minute

**Important Events (Always Report):**
- Goal
- Card
- Substitution
- Injury

**Foul Selection Priority (if multiple fouls):**
1. Foul with card
2. Foul in danger zone
3. Foul closest to goal
4. Last foul

---

## Event Chain Detection

### Chain Types

| Chain | Events | Commentary |
|-------|--------|------------|
| Pass → Shot → Goal | Assist detection | Goal + "Assisted by X" |
| Shot → Saved → Corner | Save + corner | "[Shot Saved] ... corner to follow" |
| Foul → Card → Free Kick | Full context | "[Foul + Card] ... free kick" |
| Injury → Substitution | Link events | "[Injury] ... replaced by X" |

### Detection Algorithm

```python
def detect_event_chain(minute_df, full_df):
    chain = {}
    
    # 1. Find the END of the chain (Goal or Shot)
    goal = minute_df[minute_df['shot_outcome'] == 'Goal']
    shot = minute_df[minute_df['type'] == 'Shot']
    
    if len(goal) > 0:
        chain['end'] = goal.iloc[-1]
        chain['end_type'] = 'Goal'
    elif len(shot) > 0:
        chain['end'] = shot.iloc[-1]
        chain['end_type'] = 'Shot'
    
    # 2. Trace BACK using related_events
    if 'end' in chain:
        current = chain['end']
        for rel_id in current.get('related_events', []):
            related = full_df[full_df['id'] == rel_id].iloc[0]
            if related['type'] == 'Pass':
                chain['assist'] = related
            elif related['type'] == 'Goal Keeper':
                chain['saved_by'] = related
    
    # 3. Check play_pattern for origin
    play_pattern = chain.get('end', {}).get('play_pattern', '')
    if 'Corner' in str(play_pattern):
        chain['from_corner'] = True
    elif 'Free Kick' in str(play_pattern):
        chain['from_free_kick'] = True
    
    return chain
```

---

## Process Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: LOAD DATA                                                   │
│ - Read euro_2024_complete_dataset.csv (for related_events)         │
│ - Read match_rich_commentary.csv                                    │
│ - Merge by row index                                                │
│ - Group by: (minute, period)                                        │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: EVENT DETECTION (Priority Order)                           │
│ 1. is_goal / shot_outcome='Goal' → Goal                            │
│ 2. foul_committed.card OR bad_behaviour.card → Card                │
│ 3. event_type='Shot' → Shot (Saved/Blocked/Missed)                 │
│ 4. pass_outcome='Offside' (attacking third) → Offside              │
│ 5. event_type='Substitution' → Substitution                        │
│ 6. event_type='Injury Stoppage' → Injury                           │
│ 7. play_pattern='From Corner' OR pass_type='Corner' → Corner       │
│ 8. event_type='Foul Committed/Won' → Foul                          │
│ 9. event_type='Half Start' → Kick Off                              │
│ 10. Otherwise → General                                             │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 3: EVENT CHAIN DETECTION                                       │
│ - Use related_events to find: Assist, Card, Corner origin          │
│ - Check play_pattern for: From Corner, From Free Kick              │
│ - Link: Foul Committed ↔ Foul Won                                  │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 4: COLUMN SELECTION (Based on Event Type)                      │
│                                                                     │
│ GOAL: scorer, team, body_part, location, assister, score           │
│ SHOT: player, team, outcome, body_part, location, saved/blocked_by │
│ CARD: player, team, card_type, reason (from foul)                  │
│ CORNER: team, delivered_by, conceded_by, count_this_minute         │
│ FOUL: committed_by, on (fouled_player), location, danger_context   │
│ OFFSIDE: player, team, location (only if dangerous)                │
│ SUBSTITUTION: team, player_off, player_on                          │
│ GENERAL: possession_%, turnovers, area, pressure_level             │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 5: BUILD LLM PROMPT                                            │
│ - System prompt: ESPN commentator style                             │
│ - Few-shot examples: 17 real ESPN examples                          │
│ - User prompt: Event data + chain info + reference commentary       │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 6: CALL OPENAI API                                             │
│ Model: gpt-4o-mini                                                  │
│ Parameters: temperature=0.7, max_tokens=40, top_p=0.9, seed=42     │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 7: OUTPUT                                                      │
│ [EVENT_TYPE] Short ESPN-style commentary (5-15 words)               │
│ Save to CSV with all metadata                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## System Prompt (from gpt_commentator.py)

```python
"""You are an ESPN live football commentator.

YOUR STYLE:
- Professional, factual, concise
- 5-15 words per commentary
- Include player name and team when relevant
- Match the tone to what's happening (goal = excited, foul = neutral)
- NEVER use emojis. Text only.

OUTPUT: Start with [EVENT_TYPE] then your commentary.

LEARN FROM THESE REAL ESPN EXAMPLES:

KICK OFF (IMPORTANT: Include stage for first kick off):
- [Kick Off] First Half begins. Euro 2024 Final!
- [Kick Off] The second half is underway.

GOALS:
- [Goal] Goal! Spain 1, England 0. Nico Williams left footed shot from the left side of the box.
- [Goal] Goal! Spain 1, England 1. Cole Palmer left footed shot from outside the box. Assisted by Jude Bellingham.

SHOTS:
- [Shot Blocked] Attempt blocked. Declan Rice right footed shot from outside the box.
- [Shot Saved] Attempt saved. Fabián Ruiz right footed shot from the right side of the box.
- [Shot Missed] Attempt missed. Álvaro Morata right footed shot misses to the left.

CORNERS & FREE KICKS:
- [Corner] Corner, Spain. Conceded by John Stones.
- [Free Kick] Jude Bellingham (England) wins a free kick on the left wing.

FOULS (USE "by X on Y" FORMAT):
- [Foul] Foul by Rodri (Spain) on Jude Bellingham (England).
- [Foul] Foul by Marc Cucurella (Spain) on Bukayo Saka (England).
- [Yellow Card] Harry Kane (England) is shown the yellow card for a bad foul.

SUBSTITUTIONS:
- [Substitution] Substitution, England. Ollie Watkins replaces Harry Kane.

GENERAL PLAY:
- [General] Spain maintaining possession in midfield.

RULES:
1. For KICK OFF at minute 0: ALWAYS include the stage (Final, Semi-Final, etc.)
2. For FOULS: Use "by X on Y" format when you have both players
3. For ASSISTS: Only mention if provided in data
4. NEVER use emojis"""
```

---

## Few-Shot Examples (17 Real ESPN Examples)

The `ESPN_FEW_SHOT_EXAMPLES` constant includes real commentary from Euro 2024:

| # | Event Type | ESPN Example |
|---|-----------|--------------|
| 1 | Goal | "Goal! Spain 1, England 0. Nico Williams left footed shot..." |
| 2 | Goal | "Goal! Spain 1, England 1. Cole Palmer left footed shot..." |
| 3 | Goal | "Goal! Spain 2, England 1. Mikel Oyarzabal right footed shot..." |
| 4 | Yellow Card | "Harry Kane is shown the yellow card for a bad foul." |
| 5 | Substitution | "Substitution, England. Ollie Watkins replaces Harry Kane." |
| 6 | Substitution | "Substitution, Spain. Mikel Oyarzabal replaces Álvaro Morata." |
| 7 | Corner | "Corner, Spain. Conceded by John Stones." |
| 8 | Free Kick | "Jude Bellingham wins a free kick on the left wing." |
| 9 | Foul | "Foul by Marc Cucurella (Spain)." |
| 10 | Shot Blocked | "Attempt blocked. Declan Rice right footed shot..." |
| 11 | Shot Saved | "Attempt saved. Fabián Ruiz right footed shot..." |
| 12 | General | "Delay over. They are ready to continue." |
| 13 | Offside | "Offside, Spain. Lamine Yamal is caught offside." |
| 14 | Kick Off | "First Half begins." |
| 15 | Shot Blocked | "Attempt blocked. Nico Williams left footed shot..." |
| 16 | Shot Missed | "Attempt missed. Dani Olmo left footed shot..." |
| 17 | Shot Missed | "Attempt missed. Álvaro Morata right footed shot..." |

---

## Game Phase Detection (from gpt_commentator.py)

The `_get_game_phase` function uses both `minute` AND `period` for accurate detection:

```python
def _get_game_phase(self, minute: int, period: int = None) -> str:
    if period == 1:
        if minute == 0:
            return "First Half - Kick-off"
        elif minute < 45:
            return "First Half"
        elif minute == 45:
            return "First Half"
        else:  # minute > 45, still period 1
            stoppage = minute - 45
            return f"First Half Stoppage time (45+{stoppage}')"
    
    elif period == 2:
        if minute == 45:
            return "Second Half - Kick-off"
        elif minute < 90:
            return "Second Half"
        elif minute == 90:
            return "Second Half"
        else:  # minute > 90, still period 2
            stoppage = minute - 90
            return f"Second Half Stoppage time (90+{stoppage}')"
    
    elif period == 3:
        # Extra Time - First Half
        ...
    
    elif period == 4:
        # Extra Time - Second Half
        ...
```

### Key Logic

| Minute | Period | Phase |
|--------|--------|-------|
| 0 | 1 | First Half - Kick-off |
| 1-44 | 1 | First Half |
| 45 | 1 | First Half |
| 46-47 | 1 | First Half Stoppage time (45+1', 45+2') |
| 45 | 2 | Second Half - Kick-off |
| 46-89 | 2 | Second Half |
| 90 | 2 | Second Half |
| 91+ | 2 | Second Half Stoppage time (90+1', etc.) |

---

## Event Data Formatting (from gpt_commentator.py)

The `_format_event_data` function formats data based on event type:

### Goal
```
- Scorer: Nico Williams (Spain)
- Body part: Left Foot
- Location: left side of the box
- Assisted by: Lamine Yamal
- Score now: Spain 1, England 0
```

### Shot
```
- Player: Declan Rice (England)
- Outcome: Blocked
- Body part: Right Foot
- Location: outside the box
- Blocked by: Marc Cucurella
```

### Foul
```
- Foul by: Rodri (Spain)
- On: Jude Bellingham (England)
- Location: right wing
```

### Free Kick
```
- Player fouled: Bukayo Saka (England)
- Foul committed by: Marc Cucurella (Spain)
- Location: left side of the box
- Position: good crossing position
```

### Corner
```
- Team: Spain
- Delivered by: Nico Williams
- Conceded by: John Stones
```

### Kick Off
```
- Phase: First Half - Kick-off
- STAGE: Final (MUST MENTION IN COMMENTARY)
```

### General
```
- Control: Spain in control
- Area of play: midfield
- Possession: Spain: 58.3%, England: 41.7%
```

---

## Model Parameters (from config.py)

```python
MODEL_NAME = "gpt-4o-mini"   # Cheapest GPT-4 quality model
TEMPERATURE = 0.7            # Balanced creativity and consistency
MAX_TOKENS = 40              # ESPN is 5-15 words (20-30 tokens)
TOP_P = 0.9                  # Nucleus sampling
SEED = 42                    # For reproducibility
```

### Cost Estimate

| Model | Input Cost | Output Cost | Per Match (~100 min) |
|-------|------------|-------------|----------------------|
| gpt-4 | $30/1M | $60/1M | ~$3.00 |
| gpt-4o-mini | $0.15/1M | $0.60/1M | ~$0.01 |

---

## V3: xG Extraction from Shot Column

### Data Source

The `shot` column in `euro_2024_complete_dataset.csv` contains a dictionary with StatsBomb xG:

```python
# Example shot column value:
{'statsbomb_xg': 0.123, 'end_location': [120.0, 36.0], 'type': {'name': 'Open Play'}, ...}
```

### Extraction Function

```python
def extract_xg_from_shot_column(shot_value):
    """
    Extract xG from the shot column.
    Shot column format: {'statsbomb_xg': 0.123, 'end_location': [...], ...}
    """
    if pd.isna(shot_value) or not shot_value:
        return None
    
    try:
        if isinstance(shot_value, str):
            data = ast.literal_eval(shot_value)
        else:
            data = shot_value
        
        if isinstance(data, dict):
            return data.get('statsbomb_xg', None)
    except (ValueError, SyntaxError):
        pass
    
    return None
```

---

## V3: Shot Danger Scoring

When multiple shots occur in the same minute, the system identifies the **most dangerous shot** using a scoring formula.

### Formula

```
danger_score = (xG × 100) + (120 - distance_to_goal) + outcome_bonus
```

### Components

| Component | Range | Description |
|-----------|-------|-------------|
| **xG × 100** | 0-100 pts | StatsBomb expected goals (primary factor) |
| **Distance** | 0-120 pts | Closer shots score higher (120 - distance) |
| **Outcome Bonus** | 5-30 pts | Based on shot result |

### Outcome Bonuses

| Outcome | Bonus | Reason |
|---------|-------|--------|
| Saved | +30 | Goalkeeper had to make save |
| Post | +25 | Nearly went in |
| Blocked | +20 | Defender blocked dangerous shot |
| Off T | +10 | Went close to target |
| Wayward | +5 | Far from goal |

### Implementation

```python
def calculate_shot_danger_score(shot_info):
    score = 0
    
    # xG component (0-100)
    xg = shot_info.get('xg', 0)
    if xg and not pd.isna(xg):
        score += float(xg) * 100
    
    # Distance component (closer = higher)
    distance = shot_info.get('distance', 30)
    if distance and not pd.isna(distance):
        score += max(0, 120 - float(distance))
    
    # Outcome bonus
    outcome = shot_info.get('outcome', '')
    outcome_bonuses = {
        'Saved': 30, 'Post': 25, 'Blocked': 20, 'Off T': 10, 'Wayward': 5
    }
    for key, bonus in outcome_bonuses.items():
        if key in str(outcome):
            score += bonus
            break
    
    return score
```

---

## V3: Multiple Events Detection

### Multiple Shots Analysis

```python
def analyze_multiple_shots(minute_df):
    """
    Analyze multiple shots in the same minute.
    Returns: has_multiple, count, scenario, shots_list, most_dangerous, team_counts
    """
    shot_rows = minute_df[minute_df['event_type'] == 'Shot']
    
    if len(shot_rows) < 2:
        return {'has_multiple': False, 'count': len(shot_rows)}
    
    # Build shots list with xG and danger score
    shots_list = []
    for idx, row in shot_rows.iterrows():
        xg = extract_xg_from_shot_column(row.get('shot'))
        shot_info = {
            'player': row.get('player_name', ''),
            'team': row.get('team_name', ''),
            'outcome': row.get('shot_outcome', ''),
            'distance': row.get('distance_to_goal', 30),
            'xg': xg
        }
        shot_info['danger_score'] = calculate_shot_danger_score(shot_info)
        shots_list.append(shot_info)
    
    # Determine scenario
    teams = shot_rows['team_name'].unique()
    scenario = 'pressure' if len(teams) == 1 else 'end_to_end'
    
    # Find most dangerous shot
    most_dangerous = max(shots_list, key=lambda x: x.get('danger_score', 0))
    
    return {
        'has_multiple': True,
        'count': len(shots_list),
        'scenario': scenario,
        'most_dangerous': most_dangerous
    }
```

### Scenario Types

| Scenario | Condition | Commentary Style |
|----------|-----------|------------------|
| **Pressure** | All shots from same team | "Spain applying pressure! Two attempts..." |
| **End-to-End** | Shots from both teams | "End-to-end action! Shot from Kane, Spain counter..." |

### Multiple Corners Analysis

```python
def analyze_multiple_corners(minute_df):
    corner_mask = minute_df['play_pattern'].str.contains('Corner', na=False)
    if 'pass_type' in minute_df.columns:
        corner_mask = corner_mask | minute_df['pass_type'].str.contains('Corner', na=False)
    
    corner_rows = minute_df[corner_mask]
    
    if len(corner_rows) < 2:
        return {'has_multiple': False, 'count': len(corner_rows)}
    
    teams = corner_rows['team_name'].unique()
    scenario = 'pressure' if len(teams) == 1 else 'open_game'
    
    return {'has_multiple': True, 'count': len(corner_rows), 'scenario': scenario}
```

### Multiple Fouls Analysis

```python
def analyze_multiple_fouls(minute_df):
    foul_committed = minute_df[minute_df['event_type'] == 'Foul Committed']
    foul_count = len(foul_committed)
    
    if foul_count < 3:
        return {'has_multiple': False, 'count': foul_count}
    
    return {'has_multiple': True, 'count': foul_count}
    # LLM decides: "aggressive play", "scrappy minute", etc.
```

### Multiple Substitutions Analysis

```python
def analyze_multiple_substitutions(minute_df):
    sub_rows = minute_df[minute_df['event_type'] == 'Substitution']
    
    if len(sub_rows) < 2:
        return {'has_multiple': False, 'count': len(sub_rows)}
    
    team_counts = sub_rows['team_name'].value_counts().to_dict()
    
    return {
        'has_multiple': True,
        'count': len(sub_rows),
        'team_counts': team_counts
        # LLM decides: "Double change for England", "Triple substitution"
    }
```

### Multiple Offsides Analysis

```python
def analyze_multiple_offsides(minute_df):
    offside_mask = minute_df['event_type'] == 'Offside'
    if 'pass_outcome' in minute_df.columns:
        offside_mask = offside_mask | (minute_df['pass_outcome'] == 'Offside')
    
    offside_rows = minute_df[offside_mask]
    
    if len(offside_rows) < 2:
        return {'has_multiple': False, 'count': len(offside_rows)}
    
    teams = offside_rows['team_name'].unique()
    scenario = 'timing_issues' if len(teams) == 1 else 'end_to_end'
    
    return {'has_multiple': True, 'count': len(offside_rows), 'scenario': scenario}
```

---

## V3: Progressive General Events with Domination Tracking

### Logic

| Consecutive Generals | Behavior |
|---------------------|----------|
| **1st General** | Basic possession: "Spain in control with 65% possession" |
| **2nd+ General** | Add domination streak: "Spain dominating for 3 minutes" |

### Key Rule

**Domination only counts if SAME team is in control for consecutive general events!**

### Implementation

```python
# Global trackers
possession_history = {}  # {(minute, period): {'dominant_team': 'Spain', 'pct': 65}}
last_event_type = None
consecutive_general_count = 0
general_control_history = []  # Track control for consecutive generals

# Inside main loop:
if detected_type == 'General':
    if last_event_type == 'General':
        consecutive_general_count += 1
    else:
        consecutive_general_count = 1
        general_control_history = []  # Reset on new streak
    
    general_control_history.append(current_control)
    domination_info = check_domination_for_consecutive_generals(
        consecutive_general_count, 
        current_control, 
        general_control_history
    )
else:
    consecutive_general_count = 0
    general_control_history = []  # Reset on non-General event
    domination_info = {'has_domination': False}

last_event_type = detected_type
```

### Domination Check Function

```python
def check_domination_for_consecutive_generals(consecutive_count, current_control, control_history):
    """
    Check domination for consecutive General events.
    Streak counts only if SAME team is in control.
    """
    if consecutive_count < 2 or not current_control:
        return {'has_domination': False}
    
    current_team = current_control.split()[0] if current_control else ''
    if not current_team:
        return {'has_domination': False}
    
    # Check if same team has been in control for all consecutive generals
    same_team_streak = 0
    for ctrl in reversed(control_history):
        if ctrl and ctrl.split()[0] == current_team:
            same_team_streak += 1
        else:
            break  # Different team, stop counting
    
    if same_team_streak >= 2:
        return {
            'has_domination': True,
            'team': current_team,
            'streak': same_team_streak
        }
    
    return {'has_domination': False}
```

### Dominant Team Detection

```python
def get_dominant_team_for_minute(minute_df):
    """Calculate which team dominated possession this minute."""
    if 'possession_team' not in minute_df.columns:
        return None
    
    possession_counts = minute_df['possession_team'].value_counts()
    total_events = len(minute_df)
    
    dominant_team = possession_counts.index[0]
    dominant_pct = (possession_counts.iloc[0] / total_events) * 100
    
    if dominant_pct > 55:
        return {'dominant_team': dominant_team, 'pct': round(dominant_pct, 1)}
    
    return None
```

### Most Active Player Detection

```python
def get_most_active_player(minute_df):
    """Find the player with most events this minute."""
    player_counts = minute_df['player_name'].dropna().value_counts()
    
    if len(player_counts) == 0:
        return None
    
    top_player = player_counts.index[0]
    count = player_counts.iloc[0]
    
    if count >= 5:  # Only report if player has 5+ events
        return {'player': top_player, 'team': team, 'count': int(count)}
    
    return None
```

---

## Pressure & Danger Zone Logic

### Pressure: Only When Massive (>60%)

```python
pressure_events = minute_df[minute_df['under_pressure'] == True]
pressure_pct = len(pressure_events) / len(minute_df)

if pressure_pct > 0.6:
    detection_info['pressure_level'] = 'MASSIVE'
    detection_info['show_pressure'] = True
else:
    detection_info['show_pressure'] = False
```

### Danger Zone Context

Only SPECIFIC tactical contexts are provided:

| Distance from Goal | Wide Position | Context |
|-------------------|---------------|---------|
| < 20m | Yes | "good crossing position" |
| < 20m | No (central) | "dangerous free kick position" |
| 20-30m | Yes | "free kick in a wide position" |
| 20-30m | No (central) | "free kick on the edge of the box" |
| > 30m | Any | None (use location like "right wing") |

---

## Location Helper Function

```python
def get_location_description(location_x, location_y):
    # Vertical position (left/center/right)
    if y < 26:
        side = "right"
    elif y > 54:
        side = "left"
    else:
        side = "centre"
    
    # Horizontal position
    if x < 40:
        area = "defensive half"
    elif x < 60:
        area = "midfield"
    elif x < 80:
        area = f"{side} wing" if side != "centre" else "attacking third"
    elif x < 102:
        area = f"{side} side of the box" if side != "centre" else "edge of the box"
    else:
        area = f"{side} side of the box" if side != "centre" else "centre of the box"
    
    return area
```

---

## Output Format

### CSV Columns

| Column | Description |
|--------|-------------|
| match_id | Match identifier |
| minute | Game minute |
| period | Period (1, 2, 3, 4) |
| home_team | Home team name |
| away_team | Away team name |
| home_score | Home team score |
| away_score | Away team score |
| stage | Match stage (Final, Semi-Final, etc.) |
| detected_type | Detected event classification |
| main_player | Player of main event |
| main_team | Team of main event |
| event_count | Total events in minute |
| event_chain | Related events detected |
| rule_based_commentary | Original rule-based text |
| sequence_commentary | Original sequence text |
| llm_commentary | **Generated ESPN-style commentary** |
| model | Model used |
| generated_at | Timestamp |

---

## Files Structure

```
10_llm_commentary/
├── scripts/
│   ├── Archive/                    # Previous versions
│   │   ├── gpt_commentator.py      # V1 - Basic
│   │   ├── run_final_test.py       # V1 - Basic
│   │   ├── gpt_commentator_v2.py   # V2 - Multi-events
│   │   └── run_final_test_v2.py    # V2 - Multi-events
│   ├── gpt_commentator_v3.py       # V3 - Progressive generals
│   ├── run_final_test_v3.py        # V3 - Full test script
│   ├── gpt_commentator_v4.py       # V4 - Penalty handling ← CURRENT
│   ├── run_final_test_v4.py        # V4 - Penalty test script ← CURRENT
│   ├── batch_generate_v3.py        # Batch processing (V3)
│   ├── config.py                   # Model parameters
│   └── check_data.py               # Data inspection
├── data/
│   ├── llm_commentary/             # Output CSVs (1 per version)
│   └── comparisons/                # Comparison analyses
├── docs/
│   └── LLM_COMMENTARY_PROCESS.md   # This file
├── README.md
├── SETUP.md
└── requirements.txt
```

### V3 Script Flow

```
run_final_test_v3.py
├── Load rich_commentary.csv
├── Load euro_2024_complete_dataset.csv (for xG, cards)
├── Merge shot, foul_committed, bad_behaviour columns
├── Initialize global trackers (possession_history, consecutive_general_count, etc.)
├── For each (minute, period):
│   ├── Track possession → possession_history
│   ├── Analyze multi-events (shots, corners, fouls, subs, offsides)
│   ├── detect_all_important_events()
│   │   ├── Half Start → Kick Off
│   │   ├── Goals
│   │   ├── Cards (from foul_committed/bad_behaviour)
│   │   ├── Substitutions
│   │   ├── Injuries
│   │   └── Else → detect_main_event()
│   ├── For each event:
│   │   ├── Track consecutive generals (if General)
│   │   ├── Calculate domination_info (same team check)
│   │   ├── extract_event_specific_data()
│   │   ├── Build context (with multi-event info)
│   │   └── Call GPT → generate_minute_commentary()
│   └── Save to results
└── Export CSV with V3 columns
```

---

## Summary: BALANCED APPROACH

### Core Features

1. **Data Sources**: euro_2024_complete_dataset.csv (related_events, shot xG) + rich_commentary.csv
2. **Detection**: Check event_type + play_pattern + shot_outcome + pass_type + foul_committed + bad_behaviour
3. **Event Linking**: Use `related_events` column to connect Foul↔Card, Shot↔Assist, etc.
4. **Row Selection**: Use the DETECTED main event's row (not last row)
5. **Corner Handling**: Only report if major event, or add context if related to Shot/Goal
6. **Offside Handling**: Only report if in attacking third (dangerous)
7. **Card Detection**: Check BOTH `foul_committed` AND `bad_behaviour` columns
8. **Rich Extraction**: Extract ALL relevant columns per event type
9. **Location Helper**: Convert x,y coordinates to natural descriptions
10. **Danger Context**: Only SPECIFIC tactical positions - no generic "dangerous area"
11. **Pressure Only If Massive**: Only mention if >60% of events under pressure
12. **No Emojis**: System prompt explicitly says "NEVER use emojis. Text only."
13. **LLM Freedom**: Provide data + ESPN examples, LLM decides exact wording
14. **Model**: gpt-4o-mini (cheap, fast, good quality)
15. **Parameters**: temperature=0.7, max_tokens=40, seed=42
16. **Output**: `[EVENT_TYPE] 5-15 word ESPN-style commentary`

### V3 Enhancements

17. **xG Extraction**: Parse `statsbomb_xg` from `shot` column dictionary
18. **Shot Danger Scoring**: Formula: `xG*100 + (120-distance) + outcome_bonus`
19. **Multiple Shots**: Detect pressure (same team) vs end-to-end (both teams), focus on most dangerous
20. **Multiple Corners**: Count + scenario (pressure/open game)
21. **Multiple Fouls**: Count context for 3+ fouls (LLM decides "aggressive play")
22. **Multiple Substitutions**: Detect double/triple changes per team
23. **Multiple Offsides**: Detect timing issues (same team) vs end-to-end play
24. **Progressive Generals**: 1st = basic possession, 2nd+ = domination streak
25. **Domination Tracking**: Only counts if SAME team in control for consecutive generals
26. **Most Active Player**: Identify player with 5+ events in a minute
27. **Area Detection**: Include defensive/midfield/attacking third in general commentary
28. **Single Line Output**: Enforce one-line commentary (post-processing)

### V4 Enhancements (Penalty Handling)

29. **Period 5 Detection**: Handle penalty shootout separately from regular play
30. **Penalty Shot Detection**: Check `shot.type.name='Penalty'` in shot column
31. **Penalty Awarded**: Detect foul in penalty area (location_x > 102)
32. **Penalty Outcome**: Goal, Saved, Missed (Post/Wide)
33. **Goalkeeper on Saves**: Extract from `goalkeeper` column
34. **Shootout Score Tracking**: Separate running score for shootout
35. **Penalty Numbering**: Track penalty count (Penalty 1, 2, 3...)
36. **Multiple Commentary per Minute**: Penalty Awarded + Card + Penalty Goal all separate

### V3 Output Columns

| Column | Description |
|--------|-------------|
| `v3_consecutive_generals` | Count of consecutive General events |
| `v3_domination_team` | Team dominating (if applicable) |
| `v3_domination_streak` | Number of minutes in domination |
| `v3_multi_shots_count` | Number of shots if ≥2 |
| `v3_multi_shots_scenario` | "pressure" or "end_to_end" |
| `v3_multi_corners_count` | Number of corners if ≥2 |
| `v3_multi_fouls_count` | Number of fouls if ≥3 |
| `v3_multi_subs_count` | Number of substitutions if ≥2 |
| `v3_multi_offsides_count` | Number of offsides if ≥2 |
