# Real Example: From CSV to LLM Commentary

## 🎯 Match: Spain vs England - Euro 2024 Final
**Minute 85** - The Winning Goal (Oyarzabal)

---

## 📊 STEP 1: Raw CSV Data (Source)

**File**: `match_3943043_rich_commentary.csv`

### All Events in Minute 85 (seconds 50-56):

| Row | event_type | player_name | team_name | second | location_x | location_y | shot_outcome | score |
|-----|------------|-------------|-----------|--------|------------|------------|--------------|-------|
| 6694 | Ball Receipt* | Daniel Olmo Carvajal | Spain | 50 | 63.4 | 34.9 | | 1-1 |
| 6695 | Carry | Daniel Olmo Carvajal | Spain | 50 | 63.4 | 34.9 | | 1-1 |
| 6696 | Pass | Daniel Olmo Carvajal | Spain | 52 | 70.7 | 33.6 | | 1-1 |
| 6697 | Ball Receipt* | Mikel Oyarzabal Ugarte | Spain | 53 | 88.2 | 39.9 | | 1-1 |
| 6698 | Pass | Mikel Oyarzabal Ugarte | Spain | 53 | 88.9 | 37.8 | | 1-1 |
| 6699 | Pressure | Kyle Walker | England | 55 | 21.2 | 64.6 | | 1-1 |
| 6700 | Ball Receipt* | Marc Cucurella Saseta | Spain | 55 | 99.7 | 12.7 | | 1-1 |
| 6701 | Carry | Marc Cucurella Saseta | Spain | 55 | 99.7 | 12.7 | | 1-1 |
| 6702 | Pass | Marc Cucurella Saseta | Spain | 55 | 100.0 | 12.7 | | 1-1 |
| 6703 | Ball Receipt* | Mikel Oyarzabal Ugarte | Spain | 56 | 111.2 | 36.3 | | 1-1 |
| 6704 | **Shot** | **Mikel Oyarzabal Ugarte** | Spain | 56 | 111.2 | 36.3 | **Goal** | 1-1→2-1 |

### Raw CSV Row for the Goal (Row 6704):
```csv
6704,3943043,2,85,56,00:40:56.903,Shot,Mikel Oyarzabal Ugarte,Spain,Spain,111.2,36.3,,0.39391,From Throw In,,,,,,,,Goal,0.2833282,Right Foot,Normal,True,,,,,False,,"{'id': 23, 'name': 'Center Forward'}",,1,1,0,6,0,0,13,3,0,0,...
```

### Key Columns Extracted:
- `event_type`: Shot
- `player_name`: Mikel Oyarzabal Ugarte
- `team_name`: Spain
- `minute`: 85
- `second`: 56
- `shot_outcome`: Goal
- `shot_xg`: 0.2833282
- `shot_body_part`: Right Foot
- `spain_score` / `england_score`: 1-1 → 2-1

---

## 📊 STEP 2: Rule-Based Commentary (From Phase 7)

**Column**: `event_commentary`

```
⚽ GOOOAL! Mikel Oyarzabal Ugarte scores! What a strike with the right foot 
from close range (9m)! Spain now lead 2-1! His first goal of the tournament 
late in the game! A vital goal in the closing stages!
```

---

## 📊 STEP 3: Sequence Commentary (From Phase 7)

**Column**: `sequence_commentary`

```
[85:53] Mikel Oyarzabal Ugarte under pressure, plays a medium pass forward 
along the ground to Marc Cucurella Saseta into the right attacking third. 
Kyle Walker closes down Mikel Oyarzabal Ugarte. Marc Cucurella Saseta 
receives under pressure in the right attacking third under pressure, 
carries the ball, ⚽ GOOOAL! Mikel Oyarzabal Ugarte scores! What a strike 
with the right foot from close range (9m)! Spain now lead 2-1! His first 
goal of the tournament late in the game! A vital goal in the closing stages!
```

---

## 🔄 STEP 4: Data Processing (Python Code)

```python
import pandas as pd

# Load the CSV
df = pd.read_csv('match_3943043_rich_commentary.csv')

# Filter to minute 85
minute_85_events = df[df['minute'] == 85].copy()

# Group by minute for LLM input
events_data = []
for _, row in minute_85_events.iterrows():
    event = {
        'event_type': row['event_type'],
        'player_name': row['player_name'],
        'team_name': row['team_name'],
        'second': row['second'],
        'location_x': row['location_x'],
        'location_y': row['location_y'],
        'shot_outcome': row.get('shot_outcome', ''),
        'shot_body_part': row.get('shot_body_part', ''),
        'pass_recipient': row.get('pass_recipient', ''),
    }
    events_data.append(event)

# Get rule-based and sequence commentary (from last event in sequence)
goal_row = minute_85_events[minute_85_events['event_type'] == 'Shot'].iloc[0]
rule_based = goal_row['event_commentary']
sequence = goal_row['sequence_commentary']

# Match context
match_context = {
    'home_team': 'Spain',
    'away_team': 'England',
    'home_score': 1,  # Before goal
    'away_score': 1,  # Before goal
    'stage': 'Final'
}
```

**Output - `events_data` list**:
```python
[
    {'event_type': 'Ball Receipt*', 'player_name': 'Daniel Olmo Carvajal', 'team_name': 'Spain', 'second': 50},
    {'event_type': 'Carry', 'player_name': 'Daniel Olmo Carvajal', 'team_name': 'Spain', 'second': 50},
    {'event_type': 'Pass', 'player_name': 'Daniel Olmo Carvajal', 'team_name': 'Spain', 'second': 52, 'pass_recipient': 'Mikel Oyarzabal Ugarte'},
    {'event_type': 'Ball Receipt*', 'player_name': 'Mikel Oyarzabal Ugarte', 'team_name': 'Spain', 'second': 53},
    {'event_type': 'Pass', 'player_name': 'Mikel Oyarzabal Ugarte', 'team_name': 'Spain', 'second': 53, 'pass_recipient': 'Marc Cucurella Saseta'},
    {'event_type': 'Pressure', 'player_name': 'Kyle Walker', 'team_name': 'England', 'second': 55},
    {'event_type': 'Ball Receipt*', 'player_name': 'Marc Cucurella Saseta', 'team_name': 'Spain', 'second': 55},
    {'event_type': 'Carry', 'player_name': 'Marc Cucurella Saseta', 'team_name': 'Spain', 'second': 55},
    {'event_type': 'Pass', 'player_name': 'Marc Cucurella Saseta', 'team_name': 'Spain', 'second': 55, 'pass_recipient': 'Mikel Oyarzabal Ugarte'},
    {'event_type': 'Ball Receipt*', 'player_name': 'Mikel Oyarzabal Ugarte', 'team_name': 'Spain', 'second': 56},
    {'event_type': 'Shot', 'player_name': 'Mikel Oyarzabal Ugarte', 'team_name': 'Spain', 'second': 56, 'shot_outcome': 'Goal', 'shot_body_part': 'Right Foot'}
]
```

---

## 🤖 STEP 5: LLM Input (What GPT Receives)

### System Prompt:
```
You are a professional football (soccer) commentator.

YOUR STYLE:
- Clear, factual, and neutral in describing events
- Transfer tension and excitement from the field based on:
  * What happened (you decide the importance)
  * The minute (late game = more tension)
  * The result (close games = more tension)

YOUR TASK FOR EACH MINUTE:
1. Look at ALL events provided for that minute
2. Identify if there is a MAIN EVENT worth highlighting:
   - A goal, card, penalty, significant shot, save, etc.
   - If yes → Focus commentary on that main event
3. If NO main event (just routine passing, carries, positioning):
   - Generate brief GENERAL PLAY commentary describing the flow
4. Match your excitement level to what actually happened

[... rest of system prompt ...]
```

### Few-Shot Examples (sent first):
```
### Example 1: Clear Main Event - Goal (86', Final, 0-0)
**Events**: Pass Cucurella → Shot Oyarzabal (Goal)
**Rule-based**: "[86:00] Cucurella passes to Oyarzabal, Oyarzabal shoots - GOAL!"
**Sequence**: "Cucurella finds Oyarzabal who finishes with his left foot"

**Commentary**: 
"Oyarzabal! Spain have the lead! A crucial goal in the 86th minute..."

[... more examples ...]
```

### User Prompt (The Actual Request):
```
Generate professional commentary for this minute of play.

### Match Context
- **Minute**: 85'
- **Score**: Spain 1 - 1 England
- **Stage**: Final

### Events This Minute
1. Ball Receipt* - Daniel Olmo Carvajal (Spain)
2. Carry - Daniel Olmo Carvajal (Spain)
3. Pass - Daniel Olmo Carvajal (Spain)
   (To: Mikel Oyarzabal Ugarte)
4. Ball Receipt* - Mikel Oyarzabal Ugarte (Spain)
5. Pass - Mikel Oyarzabal Ugarte (Spain)
   (To: Marc Cucurella Saseta)
6. Pressure - Kyle Walker (England)
7. Ball Receipt* - Marc Cucurella Saseta (Spain)
8. Carry - Marc Cucurella Saseta (Spain)
9. Pass - Marc Cucurella Saseta (Spain)
   (To: Mikel Oyarzabal Ugarte)
10. Ball Receipt* - Mikel Oyarzabal Ugarte (Spain)
11. Shot - Mikel Oyarzabal Ugarte (Spain)
   (Outcome: Goal, Body part: Right Foot)

### Rule-Based Commentary (for reference)
⚽ GOOOAL! Mikel Oyarzabal Ugarte scores! What a strike with the right foot 
from close range (9m)! Spain now lead 2-1! His first goal of the tournament 
late in the game! A vital goal in the closing stages!

### Sequence Commentary (for reference)
[85:53] Mikel Oyarzabal Ugarte under pressure, plays a medium pass forward 
along the ground to Marc Cucurella Saseta into the right attacking third. 
Kyle Walker closes down Mikel Oyarzabal Ugarte. Marc Cucurella Saseta 
receives under pressure in the right attacking third, carries the ball, 
⚽ GOOOAL! Mikel Oyarzabal Ugarte scores!

### Your Task
1. First, identify: Is there a MAIN EVENT in this minute? (goal, shot, card, save, etc.)
   - If YES → Focus on that main event with appropriate excitement
   - If NO → Generate brief general play commentary describing the flow

2. Generate natural, professional commentary (1-3 sentences)

**Your Commentary:**
```

---

## 🎙️ STEP 6: LLM Output (What GPT Returns)

### Expected Output:
```
"Oyarzabal! Spain have done it in the 85th minute! Olmo finds Oyarzabal, 
who plays in Cucurella down the left. The cross comes back to Oyarzabal 
and he finishes with his right foot from close range! Spain lead 2-1 
in the dying minutes of the Euro 2024 final! What a moment!"
```

---

## 📊 STEP 7: Save Output

```python
# Add to results
output = {
    'match_id': 3943043,
    'minute': 85,
    'events_count': 11,
    'main_event': 'Goal',
    'rule_based_commentary': rule_based,
    'sequence_commentary': sequence,
    'llm_commentary': llm_output,
    'home_team': 'Spain',
    'away_team': 'England',
    'score_before': '1-1',
    'score_after': '2-1'
}

# Save to CSV
results_df = pd.DataFrame([output])
results_df.to_csv('match_3943043_llm_commentary.csv', index=False)
```

---

## 📈 Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    RAW CSV DATA                                 │
│  match_3943043_rich_commentary.csv                              │
│  ~3000+ rows of events                                          │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FILTER BY MINUTE                             │
│  minute == 85 → 11 events                                       │
│  (Ball Receipt, Carry, Pass, Shot, etc.)                        │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTRACT DATA                                 │
│  events_data: List of 11 event dictionaries                     │
│  rule_based: "⚽ GOOOAL! Mikel Oyarzabal..."                     │
│  sequence: "[85:53] Mikel Oyarzabal under pressure..."          │
│  match_context: {Spain 1-1 England, Final}                      │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BUILD LLM PROMPT                             │
│  System: Commentator style definition                           │
│  Few-shot: 6 ESPN-style examples                                │
│  User: Match context + Events + Rule-based + Sequence           │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GPT-4 PROCESSING                             │
│  1. Identifies MAIN EVENT: Goal by Oyarzabal                    │
│  2. Determines excitement: VERY HIGH (late goal, final, tie)    │
│  3. Generates natural commentary                                │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LLM OUTPUT                                   │
│  "Oyarzabal! Spain have done it in the 85th minute!..."         │
│  (1-3 sentences, professional, exciting)                        │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SAVE TO CSV                                  │
│  match_3943043_llm_commentary.csv                               │
│  minute | rule_based | sequence | llm_commentary                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Comparison: Three Commentary Sources

| Source | Commentary |
|--------|------------|
| **Rule-Based** | ⚽ GOOOAL! Mikel Oyarzabal Ugarte scores! What a strike with the right foot from close range (9m)! Spain now lead 2-1! His first goal of the tournament late in the game! A vital goal in the closing stages! |
| **Sequence** | [85:53] Mikel Oyarzabal under pressure, plays a medium pass forward... Marc Cucurella Saseta receives... carries the ball, ⚽ GOOOAL! Mikel Oyarzabal Ugarte scores! |
| **LLM (GPT)** | Oyarzabal! Spain have done it in the 85th minute! Olmo finds Oyarzabal, who plays in Cucurella down the left. The cross comes back to Oyarzabal and he finishes with his right foot! Spain lead 2-1 in the dying minutes of the final! |

### Analysis:
- **Rule-Based**: Detailed, includes stats (9m, xG), but template-driven
- **Sequence**: Shows build-up, includes timestamps, comprehensive
- **LLM**: More natural flow, captures the moment, sounds like TV commentary

---

## 📊 Another Example: General Play (No Main Event)

### Minute 34: Just Passing

**Events**:
```
1. Pass - Rodri (Spain)
2. Ball Receipt - Pedri (Spain)
3. Carry - Pedri (Spain)
4. Pass - Pedri (Spain)
5. Ball Receipt - Fabián Ruiz (Spain)
```

**Rule-Based**: "Rodri passes to Pedri, Pedri carries, passes to Fabián Ruiz"

**Sequence**: "[34:00] Rodri under pressure, plays a short pass..."

**LLM Prompt** would show:
- No Goal, Shot, Card, or significant event
- GPT identifies: NO MAIN EVENT

**LLM Output**:
```
"Spain keeping the ball well in midfield. Rodri to Pedri, who looks 
to build through the center. England sitting deep here as we approach 
half-time with the score still level."
```

**Why**: Brief, describes the flow, no over-dramatization, appropriate for routine play.

---

## ✅ Summary: Complete Pipeline

| Step | Input | Output |
|------|-------|--------|
| 1. Load CSV | File path | DataFrame (3000+ rows) |
| 2. Filter | minute=85 | 11 events |
| 3. Extract | Rows | events_data, rule_based, sequence |
| 4. Build Prompt | All data | System + Few-shot + User prompt |
| 5. Call GPT | Prompt | LLM commentary string |
| 6. Save | Commentary | Output CSV |

---

*Real Example Documentation - Spain vs England Final*  
*Phase 10: LLM Commentary Generation*  
*Created: November 24, 2025*

