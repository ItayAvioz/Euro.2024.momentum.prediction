# Event Commentary Generation - Complete Guide

## Overview

This guide demonstrates how to convert structured event sequence data into natural language commentary with full metadata extraction. Unlike starting game commentary, this focuses on **in-game action sequences** with complex event relationships.

---

## Complete Workflow

```
RAW EVENT DATA (commentator_training_data.csv)
    ↓
[METADATA EXTRACTION] Parse JSON fields, calculate zones
    ↓
[TEMPLATE APPLICATION] Apply event-specific templates
    ↓
[SEQUENCE ASSEMBLY] Connect events into flowing narrative
    ↓
NATURAL COMMENTARY (event_commentary_training_data.csv)
```

---

## Example 1: Shot Sequence

### RAW DATA (Sequence ID: 7)
```
Match: Spain vs England (Final)
Sequence Type: shot_sequence
Key Event: Shot (Event #4)
Length: 5 events
```

### EXTRACTED METADATA

#### Event 1: Ball Receipt
```
Time: 11:08 (Period 1)
Player: Nicholas Williams Arthuer
Position: Left Wing
Team: Spain
Location: (99.4, 9.1) → left attacking third
Context: Regular play
Related Events: 1 connection
```

#### Event 2: Carry
```
Time: 11:08 (Period 1)
Player: Nicholas Williams Arthuer
Position: Left Wing
Team: Spain
Location Start: (99.4, 9.1)
Location End: (115.6, 28.4)
Distance: ~19m
Zone: left attacking third → central attacking third
Under Pressure: YES ⚠️
Duration: 4.67 seconds
Related Events: 3 connections
```

#### Event 3: Pressure
```
Time: 11:12 (Period 1)
Player: John Stones
Position: Right Center Back
Team: England
Location: (10.1, 54.2) → left defensive third
Target: Nicholas Williams Arthuer (Spain)
Related Events: 2 connections
```

#### Event 4: Shot ⭐ KEY EVENT ⭐
```
Time: 11:13 (Period 1)
Player: Nicholas Williams Arthuer
Position: Left Wing
Team: Spain
Location: (115.6, 28.4) → central attacking third
Shot Details:
  - xG: 0.068 (6.8% chance)
  - Body Part: Left Foot
  - Technique: Normal
  - Outcome: Blocked
  - One-on-one: YES
Under Pressure: YES ⚠️
Related Events: 3 connections
```

#### Event 5: Block
```
Time: 11:13 (Period 1)
Player: John Stones
Position: Right Center Back
Team: England
Location: (4.1, 50.8) → central defensive third
Blocked Shot From: Nicholas Williams Arthuer
Related Events: 1 connection
```

### GENERATED COMMENTARY

**Event-Level:**
1. "Nicholas Williams Arthuer receives the ball"
2. "Williams under pressure, drives forward with the ball into the attacking third"
3. "John Stones closes down Williams"
4. "⭐ Williams shoots with the left from the central attacking third - BLOCKED! ⭐"
5. "BLOCKED by John Stones! Crucial defending"

**Sequence-Level (Flowing):**
> **[11:08]** Nicholas Williams Arthuer receives the ball. Williams under pressure, drives forward with the ball, pushing deep into the attacking third. John Stones closes down. Williams shoots with the left - BLOCKED! John Stones with crucial defending!

---

## Example 2: Dribble Sequence

### RAW DATA (Sequence ID: 5)
```
Match: Spain vs England (Final)
Sequence Type: dribble_sequence
Key Event: Dribble (Event #3)
Length: 5 events
```

### EXTRACTED METADATA

#### Event 1: Ball Receipt
```
Time: 1:38 (Period 1)
Player: Luke Shaw
Position: Left Back
Team: England
Location: (48.7, 3.7) → right midfield
Under Pressure: YES ⚠️
Related Events: 2 connections
```

#### Event 2: Carry
```
Time: 1:38 (Period 1)
Player: Luke Shaw
Position: Left Back
Team: England
Location Start: (48.7, 3.7)
Location End: (51.1, 2.4)
Distance: ~2.8m (short)
Under Pressure: YES ⚠️
Duration: 1.12 seconds
Related Events: 3 connections
```

#### Event 3: Dribble ⭐ KEY EVENT ⭐
```
Time: 1:39 (Period 1)
Player: Luke Shaw
Position: Left Back
Team: England
Location: (51.1, 2.4) → right midfield
Dribble Details:
  - Outcome: Incomplete
  - Special: NUTMEG! 🔥 (Through the legs)
Opponent: Daniel Carvajal Ramos (Spain, Right Back)
Under Pressure: YES ⚠️
Related Events: 1 connection
```

#### Event 4: Duel
```
Time: 1:39 (Period 1)
Player: Daniel Carvajal Ramos
Position: Right Back
Team: Spain
Location: (69.0, 77.7) → left defensive third
Duel Type: Tackle
Outcome: Won
Under Pressure: YES ⚠️
Counterpress: YES
Related Events: 1 connection
```

#### Event 5: Carry
```
Time: 1:39 (Period 1)
Player: Daniel Carvajal Ramos
Position: Right Back
Team: Spain
Location Start: (69.0, 77.7)
Location End: (35.8, 75.1)
Distance: ~33.6m (long)
Duration: 4.56 seconds
Related Events: 2 connections
```

### GENERATED COMMENTARY

**Event-Level:**
1. "Luke Shaw receives the ball"
2. "Shaw under pressure, carries forward"
3. "⭐ Shaw takes on Carvajal - NUTMEG! Through the legs ⭐"
4. "Carvajal wins the tackle"
5. "Carvajal drives forward with the ball"

**Sequence-Level (Flowing):**
> **[1:38]** Luke Shaw receives the ball under pressure. Shaw carries forward. Shaw takes on Carvajal - NUTMEG! Through the legs! But Carvajal recovers and wins the tackle. Carvajal drives forward with the ball.

---

## Example 3: Pressure Sequence

### RAW DATA (Sequence ID: 3)
```
Match: Spain vs England (Final)
Sequence Type: pressure_sequence
Key Event: Pressure (Event #3)
Length: 5 events
```

### EXTRACTED METADATA

#### Event 1: Ball Receipt
```
Time: 0:37 (Period 1)
Player: Daniel Carvajal Ramos
Position: Right Back
Team: Spain
Location: (20.6, 75.8) → left defensive third
Play Pattern: From Goal Kick
Related Events: 1 connection
```

#### Event 2: Carry
```
Time: 0:37 (Period 1)
Player: Daniel Carvajal Ramos
Position: Right Back
Team: Spain
Location Start: (20.6, 75.8)
Location End: (28.6, 76.4)
Distance: ~8.2m (short)
Under Pressure: YES ⚠️
Duration: 1.77 seconds
Related Events: 3 connections
```

#### Event 3: Pressure ⭐ KEY EVENT ⭐
```
Time: 0:38 (Period 1)
Player: Jude Bellingham
Position: Left Wing
Team: England
Location: (94.7, 4.1) → right attacking third
Target: Daniel Carvajal Ramos (Spain)
Duration: 0.54 seconds
Related Events: 1 connection
```

#### Event 4: Pass
```
Time: 0:39 (Period 1)
Player: Daniel Carvajal Ramos
Position: Right Back
Team: Spain
Location: (28.6, 76.4) → left defensive third
Pass Details:
  - Recipient: Daniel Olmo Carvajal
  - Length: 23.0m (medium)
  - Height: Ground Pass
  - Angle: -0.35 radians
  - Body Part: Right Foot
Duration: 1.08 seconds
Related Events: 1 connection
```

#### Event 5: Pressure
```
Time: 0:40 (Period 1)
Player: Declan Rice
Position: Left Defensive Midfield
Team: England
Location: (69.9, 11.6) → right midfield
Target: Daniel Olmo Carvajal (Spain)
Duration: 0.29 seconds
Related Events: 2 connections
```

### GENERATED COMMENTARY

**Event-Level:**
1. "Carvajal receives the ball"
2. "Carvajal under pressure, carries the ball"
3. "⭐ Bellingham presses Carvajal in the attacking third ⭐"
4. "Carvajal plays a medium pass along the ground to Olmo"
5. "Rice closes down Olmo"

**Sequence-Level (Flowing):**
> **[0:37]** Daniel Carvajal Ramos receives the ball from a goal kick. Carvajal under pressure, carries the ball forward. Jude Bellingham presses high in the attacking third. Carvajal plays a medium pass along the ground to Daniel Olmo Carvajal. Declan Rice immediately closes down Olmo.

---

## Metadata Extraction Framework

### 1. CORE METADATA (Always Present)

| Category | Fields | Purpose |
|----------|--------|---------|
| **Time** | minute, second, period, timestamp | When event occurred |
| **Player** | player_name, player_position, player_id | Who performed action |
| **Team** | team_name, possession_team | Which team has ball |
| **Event** | event_type, is_key_event | What action happened |
| **Sequence** | sequence_id, event_position, sequence_length | Context in sequence |

### 2. LOCATION METADATA

| Field | Value | Commentary Usage |
|-------|-------|------------------|
| **location_x** | 0-120 | "in the attacking third" |
| **location_y** | 0-80 | "on the left wing" |
| **zone_horizontal** | defensive/midfield/attacking third | Field progression |
| **zone_vertical** | left/central/right | Width position |
| **zone_combined** | e.g., "left attacking third" | Full spatial context |

### 3. EVENT-SPECIFIC METADATA

#### PASS EVENTS
```
pass_recipient: Who receives the ball
pass_length: Distance (0-100m)
  → short (0-10m), medium (10-25m), long (25m+)
pass_height: Ground Pass, Low Pass, High Pass
  → "along the ground", "through the air"
pass_outcome: Complete, Incomplete, Out
  → affects narrative flow
pass_body_part: Left Foot, Right Foot, Head
  → "heads it", "with the right"
```

#### SHOT EVENTS
```
shot_xg: Expected goals (0-1)
  → 0.3+ = "great chance"
shot_outcome: Goal, Saved, Blocked, Off Target
  → emotional response level
shot_body_part: Left Foot, Right Foot, Head
  → technique description
shot_technique: Normal, Volley, Overhead
  → action verb choice
```

#### DRIBBLE EVENTS
```
dribble_outcome: Complete, Incomplete
  → "beats him" vs "loses it"
dribble_nutmeg: Boolean
  → adds excitement "NUTMEG!"
opponent: Extracted from related events
  → "takes on [Opponent]"
```

#### CARRY EVENTS
```
carry_start: (x, y) from location
carry_end: (x, y) from carry details
carry_distance: Calculated
  → "drives forward" (>15m), "carries" (5-15m), "controls" (<5m)
```

#### PRESSURE EVENTS
```
target_player: Extracted from context
duration: How long pressure applied
effect: Check next event outcome
  → successful pass, turnover, etc.
```

### 4. CONTEXTUAL FLAGS

| Flag | Impact on Commentary |
|------|---------------------|
| **under_pressure** | Adds "under pressure," prefix |
| **counterpress** | "wins it back immediately" |
| **play_pattern** | "from a corner", "on the break" |
| **duration** | "quick pass" vs "takes time" |

---

## Commentary Templates

### TEMPLATE 1: Pass Event
```
STRUCTURE:
{Player} {body_part_verb} {distance} {delivery} to {Recipient} {location_context} {outcome_context}

VARIABLES:
- body_part_verb: "plays", "heads it", "chips"
- distance: "short", "medium", "long"
- delivery: "pass along the ground", "ball through the air", "low pass"
- location_context: "in the {zone}"
- outcome_context: "", "but it's intercepted", "but it goes out"

EXAMPLES:
✓ "Carvajal plays a medium pass along the ground to Olmo in the central midfield"
✓ "Kane heads it, long ball through the air to Saka, but it's intercepted"
✓ "Shaw chips a short pass to Bellingham in the left attacking third"
```

### TEMPLATE 2: Shot Event
```
STRUCTURE:
{Player} {shot_verb} {body_part} from the {zone} - {outcome}!

VARIABLES:
- shot_verb: "shoots", "volleys", "attempts an overhead kick"
- body_part: "with the left", "with the right", "with a header"
- outcome: 
  * Goal: "IT'S A GOAL! What a finish!"
  * Saved: "saved by the goalkeeper!"
  * Blocked: "BLOCKED! Crucial defending"
  * Off: "just wide of the post"

EXAMPLES:
✓ "Williams shoots with the left from the central attacking third - BLOCKED!"
✓ "Kane volleys from the right attacking third - IT'S A GOAL!"
✓ "Bellingham with a header from the central attacking third - saved!"
```

### TEMPLATE 3: Dribble Event
```
STRUCTURE:
{Player} takes on {Opponent} {special_context}, {outcome}

VARIABLES:
- special_context: "- NUTMEG!", "- through the legs", ""
- outcome:
  * Complete: "beats him and drives forward"
  * Incomplete: "but loses it", "but the defender stands firm"

EXAMPLES:
✓ "Shaw takes on Carvajal - NUTMEG! Through the legs"
✓ "Rice takes on Fabián, beats him and drives forward"
✓ "Saka takes on Cucurella, but loses possession"
```

### TEMPLATE 4: Carry Event
```
STRUCTURE:
{Player} {pressure_context} {action} {progression_context}

VARIABLES:
- pressure_context: "under pressure,", ""
- action:
  * Long (>15m): "drives forward with the ball"
  * Medium (5-15m): "carries the ball"
  * Short (<5m): "controls the ball"
- progression_context: ", pushing into the {end_zone}", ""

EXAMPLES:
✓ "Williams under pressure, drives forward with the ball"
✓ "Stones carries the ball, pushing into the central midfield"
✓ "Pickford controls the ball"
```

### TEMPLATE 5: Pressure Event
```
STRUCTURE:
{Player} {verb} {Target} in the {zone}

VARIABLES:
- verb: "presses", "closes down", "harries"
- Target: Player name or "the ball carrier"

EXAMPLES:
✓ "Bellingham presses Carvajal in the right attacking third"
✓ "Rice closes down in the central midfield"
✓ "Stones harries Williams"
```

### TEMPLATE 6: Sequence Flow
```
CONNECTION STRATEGIES:
1. Period separation: ". " (new sentence)
2. Continuation: ", " (same flow)
3. Dramatic pause: " - " (emphasis)
4. Cause-effect: "but", "then", "however"

EMOTIONAL LEVEL:
- Normal: Standard description
- Key Event: Add emphasis "⭐" or "!"
- Critical Outcome: ALL CAPS for goals, saves

EXAMPLE FULL SEQUENCE:
"[11:08] Williams receives the ball. Williams under pressure, 
drives forward with the ball. Stones closes down. Williams shoots 
with the left - BLOCKED! Stones with crucial defending!"
```

---

## Field Zone Reference

### Pitch Coordinates
```
0 ─────────────────── 120 (x-axis: length)
│    DEFENSIVE    MIDFIELD    ATTACKING
│      0-40        40-80        80-120
│
0─80 (y-axis: width)
     RIGHT    CENTRAL    LEFT
     0-27      27-53    53-80
```

### Zone Descriptions
| Coordinates | Horizontal Zone | Vertical Zone | Combined |
|-------------|----------------|---------------|----------|
| (15, 15) | Defensive third | Right | "right defensive third" |
| (60, 40) | Midfield | Central | "central midfield" |
| (100, 70) | Attacking third | Left | "left attacking third" |

---

## Related Events & Connections

### Purpose
Related events show the flow and causality between actions:
- **Pass** → Connected to **Ball Receipt** (recipient)
- **Shot** → Connected to **Block** or **Goal Keeper**
- **Dribble** → Connected to **Duel** or **Dribbled Past**
- **Pressure** → Connected to **Carry** or **Pass** (effect)

### Usage in Commentary
```
Event 1: Pass by Player A
  related_events: [event_2_id]
Event 2: Ball Receipt by Player B
  related_events: [event_1_id]

Commentary: "Player A passes to Player B"
```

---

## Training Data Structure

### Input Features (38 columns)
```python
# Sequence Context (6)
sequence_id, sequence_type, sequence_key_event, sequence_length, event_position, is_key_event

# Match Context (7)
match_id, home_team, away_team, minute, second, period, timestamp

# Event Details (8)
event_type, player_name, player_position, team_name, possession_team, under_pressure, duration, play_pattern

# Location (5)
location_x, location_y, zone_horizontal, zone_vertical, zone_combined

# Pass Details (4)
pass_recipient, pass_length, pass_height, pass_outcome

# Shot Details (3)
shot_xg, shot_outcome, shot_body_part

# Dribble Details (2)
dribble_outcome, dribble_nutmeg

# Carry Details (3)
carry_end_x, carry_end_y, carry_distance
```

### Output (2 columns)
```python
# Generated Commentary
event_commentary    # Single event description
sequence_commentary # Full sequence narrative
```

---

## Usage for NLP Models

### 1. Event-Level Model
```
TASK: Generate commentary for single event
INPUT: All metadata for one event
OUTPUT: event_commentary

EXAMPLE:
Input: {
  event_type: "Shot",
  player_name: "Williams",
  location_x: 115.6,
  zone_combined: "central attacking third",
  shot_xg: 0.068,
  shot_outcome: "Blocked",
  under_pressure: True
}
Output: "Williams shoots with the left from the central attacking third - BLOCKED!"
```

### 2. Sequence-Level Model
```
TASK: Generate flowing commentary for sequence
INPUT: All events in sequence (grouped by sequence_id)
OUTPUT: sequence_commentary

EXAMPLE:
Input: Sequence of 5 events (Pass → Carry → Pressure → Shot → Block)
Output: "[11:08] Carvajal receives. Carvajal under pressure, carries forward. 
         Bellingham presses. Carvajal plays to Olmo. Olmo shoots - BLOCKED!"
```

### 3. Template Learning
```
MODEL LEARNS:
- Event type → Template selection
- Context flags → Phrase modifiers
- Outcomes → Emotional level
- Sequences → Connection patterns
```

---

## Summary

This complete system provides:

✅ **Full Metadata Extraction** - 40 columns of structured data  
✅ **Event Templates** - Specific patterns for each event type  
✅ **Sequence Assembly** - Rules for connecting events  
✅ **Context-Aware** - Pressure, location, timing  
✅ **Natural Language** - Flowing, emotional, varied  
✅ **Training Ready** - 144 events, 30 sequences prepared  

**Ready for NLP model training to create an AI football commentator!** 🎙️⚽

---

*Document Version: 1.0*  
*Created: 2024*  
*Dataset: event_commentary_training_data.csv*
