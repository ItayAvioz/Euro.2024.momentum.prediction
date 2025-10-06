# Final Game Commentary Template Guide
## Euro 2024 Final: Spain vs England (Minute 75+)

---

## 📊 Dataset Overview

**Match:** Spain 2-1 England (Final)  
**Period Analyzed:** Minute 75-94 (Second half + Stoppage time)  
**Total Events:** 525  
**Total Sequences:** 60  
**Key Moments:** 1 Goal, 5 Shots, 6 Blocks

**Tournament Context (Before Final):**
- **Spain:** 6-0-0 record, 13 goals scored, 3 conceded
- **England:** 3-3-0 record, 7 goals scored, 4 conceded

---

## 🎯 Event Type Distribution

| Event Type | Count | % | Excitement Level |
|-----------|-------|---|------------------|
| Pass | 147 | 28.0% | Neutral → High (depends on context) |
| Ball Receipt* | 139 | 26.5% | Neutral |
| Carry | 123 | 23.4% | Neutral → Medium |
| Pressure | 39 | 7.4% | Medium |
| Ball Recovery | 12 | 2.3% | Medium |
| Clearance | 10 | 1.9% | Medium → High |
| Duel | 10 | 1.9% | Medium |
| Block | 6 | 1.1% | **HIGH** |
| Goal Keeper | 6 | 1.1% | Medium → High |
| Shot | 5 | 1.0% | **VERY HIGH** |
| Foul Won | 5 | 1.0% | Low → Medium |

---

## 1. PASS (147 occurrences)

### Data Extracted:
```python
{
    # Core data
    'player_name': str,
    'team_name': str,
    'minute': int,
    'second': float,
    'pass_recipient': str,
    'pass_length': float (meters),
    'pass_height': str ('Ground Pass', 'Low Pass', 'High Pass'),
    'pass_outcome': str (None=success, 'Incomplete', 'Out', 'Offside'),
    'pass_angle': float (radians),
    'under_pressure': bool,
    'play_pattern': str,
    
    # Location data
    'location_x': float,
    'location_y': float,
    'pass_end_x': float,
    'pass_end_y': float,
    
    # Context data
    'spain_score': int,
    'england_score': int,
    'possession_team': str
}
```

### Enrichment Data:
- **Distance category:** Short (<15m), Medium (15-30m), Long (>30m)
- **Trajectory:** "along the ground", "through the air"
- **Direction:** "forward", "back", "lateral" (calculated from x coordinates)
- **Zone progression:** Start zone → End zone
- **Play pattern context:** Free kick, corner, goal kick, etc.
- **Pressure context:** "under pressure" modifier

### Template Logic:
```python
IF under_pressure:
    pressure_text = "under pressure, "
ELSE:
    pressure_text = ""

distance = SHORT/MEDIUM/LONG (based on pass_length)
trajectory = "along the ground" / "through the air" (based on pass_height)

IF pass_recipient exists:
    base = "{player} {pressure}plays a {distance} {type} {trajectory} to {recipient}"
ELSE:
    base = "{player} {pressure}plays a {distance} {type} {trajectory}"

IF zone_progression (e.g., midfield → attacking third):
    base += " into the {end_zone}"

IF outcome:
    IF outcome == "Out":
        base += ", but it goes out of play"
    ELIF outcome == "Offside":
        base += ", but the flag is up for offside!"
    ELIF outcome == "Incomplete":
        base += ", but the pass doesn't find its target"

IF play_pattern == "Free Kick":
    Replace "plays" with "delivers the free kick"
ELIF play_pattern == "Corner":
    Replace "plays" with "delivers the corner"
ELIF play_pattern == "Goal Kick":
    Prepend "From the goal kick, "
```

### Real Examples:

**Example 1: Long Pass Under Pressure**
```
Data:
- Player: Kyle Walker (England)
- Recipient: John Stones
- Length: 37.0m (LONG)
- Height: Low Pass
- Under Pressure: True
- Outcome: Success
- Zone: central attacking third → central midfield

Commentary:
"Kyle Walker under pressure, plays a long pass back to John Stones"
```

**Example 2: Forward Pass with Zone Progression**
```
Data:
- Player: Jordan Pickford (England)
- Recipient: Kyle Walker
- Length: 67.5m (LONG)
- Height: High Pass
- Under Pressure: True
- Outcome: Out
- Zone: central defensive third → left attacking third

Commentary:
"Jordan Pickford under pressure, plays a long ball forward through the air to Kyle Walker into the left attacking third, but it goes out of play"
```

**Example 3: Short Ground Pass**
```
Data:
- Player: Marc Cucurella Saseta (Spain)
- Recipient: Rodrigo Hernández Cascante
- Length: 11.4m (SHORT)
- Height: Ground Pass
- Under Pressure: False
- Outcome: Success

Commentary:
"Marc Cucurella Saseta plays a short pass along the ground to Rodrigo Hernández Cascante"
```

---

## 2. SHOT (5 occurrences) ⚽

### Data Extracted:
```python
{
    # Core data
    'player_name': str,
    'team_name': str,
    'minute': int,
    'second': float,
    'shot_outcome': str ('Goal', 'Saved', 'Blocked', 'Off T', 'Wayward', 'Post'),
    'shot_xg': float (0.0-1.0),
    'shot_body_part': str ('Left Foot', 'Right Foot', 'Head'),
    'shot_technique': str,
    'is_goal': bool,
    'under_pressure': bool,
    
    # Location
    'location_x': float,
    'location_y': float,
    
    # Score context
    'spain_score': int,
    'england_score': int,
    'score_diff': int,
    
    # Player stats
    'player_tournament_goals': int,
    'player_match_goals': int,
    
    # Team stats
    'team_tournament_goals': int
}
```

### Enrichment Data:
- **Time context:** "late in the game", "in the dying moments", "in stoppage time"
- **Zone description:** Calculated from location
- **Player milestones:** First goal, brace, tournament total
- **Team milestones:** First time leading, two-goal lead, etc.
- **Assist tracking:** Previous pass event (if from same team within 3 seconds)
- **xG context:** Add xG value for big chances (>0.4)

### Template Logic:

#### For GOALS (is_goal == True):
```python
# Maximum excitement!
base = "⚽ GOOOAL! {player} scores"

# Check for assist
IF previous_event is Pass AND same_team AND time_diff < 3 seconds:
    base += ", assisted by {assist_player}"
base += "! "

# Add technique excitement
IF body_part == "Head":
    base += "A brilliant header from {player}! "
ELIF body_part == "Right Foot":
    base += "What a strike with the right foot! "
ELIF body_part == "Left Foot":
    base += "A superb left-footed finish! "

# Calculate new score
new_score = calculate_new_score()
base += "{team} now lead {new_score}! "

# Player milestones
IF player_match_goals + 1 >= 2:
    base += "That's {player}'s {ordinal} goal of the match! "

IF player_tournament_goals + 1 == 1:
    base += "His first goal of the tournament {time_context}! "
ELSE:
    base += "His {ordinal} goal of the tournament {time_context}! "

# Dramatic context
IF score_diff == 2:
    base += "A crucial two-goal lead in the final! "
IF "stoppage" in time_context:
    base += "What drama in stoppage time! "
```

#### For NON-GOALS:
```python
IF under_pressure:
    base = "{player} under pressure, shoots"
ELSE:
    base = "{player} shoots"

IF body_part:
    base += " with the {body_part}"
base += " from the {zone}"

# Outcome
IF outcome == "Blocked":
    base += " - BLOCKED!"
ELIF outcome == "Saved":
    base += " - SAVED by the goalkeeper!"
    IF xg > 0.3:
        base += " Great chance!"
ELIF outcome == "Off T":
    base += " - just wide!"
    IF xg > 0.25:
        base += " Should have scored!"
ELIF outcome == "Wayward":
    base += " - well wide!"
ELIF outcome == "Post":
    base += " - HITS THE POST! So close!"

# Add xG for big chances
IF xg > 0.4:
    base += " (xG: {xg:.2f})"
```

### Real Examples:

**Example 1: GOAL! (Maximum Excitement)**
```
Data:
- Player: Mikel Oyarzabal Ugarte (Spain)
- Minute: 85:56
- Body Part: Right Foot
- xG: 0.34
- Is Goal: TRUE
- Player Match Goals Before: 1 (now 2 = brace!)
- Player Tournament Goals Before: 0 (now 1 = first!)
- Score Before: 1-0
- Score After: 2-0

Commentary:
"⚽ GOOOAL! Mikel Oyarzabal Ugarte scores! What a strike with the right foot! Spain now lead 2-0! That's Mikel Oyarzabal Ugarte's second goal of the match! His first goal of the tournament late in the game! A crucial two-goal lead in the final!"
```

**Example 2: Shot Saved (High Excitement)**
```
Data:
- Player: Lamine Yamal Nasraoui Ebana (Spain)
- Minute: 81:14
- Body Part: Left Foot
- Outcome: Saved
- xG: 0.23
- Under Pressure: False
- Zone: central attacking third

Commentary:
"Lamine Yamal Nasraoui Ebana shoots with the left foot from the central attacking third - SAVED by the goalkeeper!"
```

**Example 3: Shot Off Target**
```
Data:
- Player: Declan Rice (England)
- Minute: 89:51
- Body Part: Right Foot
- Outcome: Off T
- xG: 0.15
- Under Pressure: True
- Zone: central attacking third

Commentary:
"Declan Rice under pressure, shoots with the right foot from the central attacking third - just wide!"
```

---

## 3. CARRY (123 occurrences)

### Data Extracted:
```python
{
    'player_name': str,
    'team_name': str,
    'minute': int,
    'under_pressure': bool,
    'duration': float (seconds),
    'location_x': float,
    'location_y': float,
    'carry_end_x': float,
    'carry_end_y': float,
    'carry_distance': float (calculated)
}
```

### Enrichment Data:
- **Distance traveled:** Calculated from start/end coordinates
- **Zone progression:** Start zone → End zone
- **Significant run:** Distance > 15m = "drives forward"
- **Pressure context:** "under pressure" modifier

### Template Logic:
```python
IF carry_distance > 15:
    action = "drives forward with the ball"
ELSE:
    action = "carries the ball"

IF under_pressure:
    base = "{player}, under pressure, {action}"
ELSE:
    base = "{player} {action}"

IF start_zone != end_zone:
    base += " from the {start_zone} into the {end_zone}"
```

### Real Examples:

**Example 1: Long Run Forward**
```
Data:
- Player: Bukayo Saka (England)
- Distance: 18.7m
- Under Pressure: False
- Zone: right midfield → right attacking third

Commentary:
"Bukayo Saka drives forward with the ball from the right midfield into the right attacking third"
```

**Example 2: Carry Under Pressure**
```
Data:
- Player: John Stones (England)
- Distance: 5.5m
- Under Pressure: True
- Zone: central midfield

Commentary:
"John Stones, under pressure, carries the ball"
```

---

## 4. BALL RECEIPT* (139 occurrences)

### Data Extracted:
```python
{
    'player_name': str,
    'team_name': str,
    'minute': int,
    'under_pressure': bool,
    'location_x': float,
    'location_y': float
}
```

### Enrichment Data:
- **Zone:** Calculated from location
- **Pressure context:** Important in attacking zones
- **Dangerous zone:** "attacking third", "penalty area"

### Template Logic:
```python
IF under_pressure AND in_attacking_zone:
    base = "{player} receives under pressure in the {zone}"
ELIF in_attacking_zone:
    base = "{player} receives in the {zone}"
ELSE:
    base = "{player} receives"
```

### Real Examples:

**Example 1: Dangerous Reception**
```
Data:
- Player: Kyle Walker (England)
- Under Pressure: True
- Zone: central attacking third

Commentary:
"Kyle Walker receives under pressure in the central attacking third"
```

**Example 2: Simple Reception**
```
Data:
- Player: John Stones (England)
- Under Pressure: False
- Zone: central midfield

Commentary:
"John Stones receives"
```

---

## 5. PRESSURE (39 occurrences)

### Data Extracted:
```python
{
    'player_name': str (presser),
    'team_name': str (pressing team),
    'minute': int,
    'duration': float,
    'location_x': float,
    'location_y': float
}
```

### Enrichment Data:
- **Target player:** Identified from previous/next event (opposite team)
- **Context:** Builds narrative of pressing intensity

### Template Logic:
```python
# Look for target in previous event (same possession, opposite team)
IF target_player_identified:
    base = "{player} closes down {target_player}"
ELSE:
    base = "{player} closes down the ball carrier"
```

### Real Examples:

**Example 1: Named Target**
```
Data:
- Player: Mikel Oyarzabal Ugarte (Spain)
- Previous Event: John Stones (England) carrying ball

Commentary:
"Mikel Oyarzabal Ugarte closes down John Stones"
```

**Example 2: Generic**
```
Data:
- Player: Declan Rice (England)
- Target: Unknown

Commentary:
"Declan Rice closes down the ball carrier"
```

---

## 6. BLOCK (6 occurrences) 🛡️

### Data Extracted:
```python
{
    'player_name': str (blocker),
    'team_name': str,
    'minute': int,
    'location_x': float,
    'location_y': float
}
```

### Enrichment Data:
- **Previous event:** Usually a shot
- **Defensive heroism:** High excitement level

### Template Logic:
```python
base = "Crucial block by {player}!"
# Simple but effective - blocks are always exciting
```

### Real Examples:

**Example 1:**
```
Data:
- Player: Luke Shaw (England)
- Minute: 84:20
- Previous: Shot by Lamine Yamal

Commentary:
"Crucial block by Luke Shaw!"
```

---

## 7. CLEARANCE (10 occurrences)

### Template:
```python
base = "{player} clears the danger"
```

**Example:** "Kyle Walker clears the danger"

---

## 8. GOAL KEEPER (6 occurrences)

### Template:
```python
base = "The goalkeeper deals with it"
```

**Example:** "The goalkeeper deals with it"

---

## 9. BALL RECOVERY (12 occurrences)

### Template:
```python
base = "{player} wins the ball back"
```

**Example:** "Rodrigo Hernández Cascante wins the ball back"

---

## 10. FOUL WON (5 occurrences)

### Template:
```python
base = "{player} is fouled"
```

**Example:** "Lamine Yamal Nasraoui Ebana is fouled"

---

## 📋 Sequence Commentary

### How Sequences Are Created:
```python
# Group events by possession team
# Max 10 events per sequence
# New sequence when possession changes

sequence_commentary = "[time] event1. event2. event3. event4. event5."
```

### Real Sequence Example:

**Sequence #43 (Leading to Oyarzabal's GOAL):**

```
[85:50] Sequence Commentary:
"Marc Cucurella Saseta plays a short pass along the ground to Rodrigo Hernández Cascante. Rodrigo Hernández Cascante receives. Rodrigo Hernández Cascante carries the ball. Rodrigo Hernández Cascante plays a short pass forward along the ground to Mikel Oyarzabal Ugarte. Mikel Oyarzabal Ugarte receives in the central attacking third."

[85:56] GOAL EVENT:
"⚽ GOOOAL! Mikel Oyarzabal Ugarte scores! What a strike with the right foot! Spain now lead 2-0! That's Mikel Oyarzabal Ugarte's second goal of the match! His first goal of the tournament late in the game! A crucial two-goal lead in the final!"
```

---

## 🎯 Commentary Style Guide

### Excitement Levels:

**NEUTRAL (Most Events):**
- Passes, Carries, Ball Receipts, Pressure
- Factual, descriptive tone
- Example: "John Stones plays a long pass to Kyle Walker"

**MEDIUM (Tactical Events):**
- Ball Recovery, Clearance, Duel
- Slightly more engaged
- Example: "Kyle Walker clears the danger"

**HIGH (Defensive Saves):**
- Blocks, Saves, Last-ditch tackles
- Excitement and praise
- Example: "Crucial block by Luke Shaw!"

**VERY HIGH (Attacking Moments):**
- Shots, Near misses
- Heightened excitement
- Example: "Declan Rice shoots - just wide! Should have scored!"

**MAXIMUM (Goals):**
- Goals
- Extreme excitement, milestones, context
- Example: "⚽ GOOOAL! Mikel Oyarzabal Ugarte scores! What a strike..."

---

## 📊 Summary Statistics

**Total Dataset:**
- **Events:** 525
- **Sequences:** 60
- **Columns:** 46
- **Period:** Minutes 75-94

**Enrichment Data Added:**
- Tournament stats for both teams (before final)
- Player tournament goals (before final)
- In-match player goals (dynamic)
- Dynamic score tracking
- Zone calculations
- Time context
- Pass trajectory/distance categories
- Player milestones

**Output Format:**
- **CSV:** One row per event
- **Columns include:**
  - All base event data (42 columns)
  - event_commentary (generated)
  - sequence_id
  - sequence_commentary
  - sequence_length

---

## 🚀 Usage

**Load Data:**
```python
import pandas as pd
df = pd.read_csv('final_game_rich_commentary.csv')
```

**Filter by Event Type:**
```python
goals = df[df['is_goal'] == True]
shots = df[df['event_type'] == 'Shot']
key_passes = df[(df['event_type'] == 'Pass') & (df['pass_length'] > 30)]
```

**Access Commentary:**
```python
for idx, row in df.iterrows():
    print(f"[{row['minute']}:{row['second']:.0f}] {row['event_commentary']}")
```

**Sequence Analysis:**
```python
sequences = df.groupby('sequence_id')
for seq_id, seq_events in sequences:
    print(f"\nSequence {seq_id}:")
    print(seq_events.iloc[0]['sequence_commentary'])
```

---

*Generated for Euro 2024 Final: Spain vs England (75+ minutes)*
*Dataset includes rich context, statistics, and realistic sports commentary*
