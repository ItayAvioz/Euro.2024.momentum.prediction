# Quick Reference: Top 11 Event Types

## 📊 Event Distribution

| Rank | Event Type | Count | % of Total |
|------|-----------|-------|------------|
| 1 | Ball Receipt* | 29 | 20.1% |
| 2 | Carry | 26 | 18.1% |
| 3 | Pressure | 26 | 18.1% |
| 4 | Pass | 19 | 13.2% |
| 5 | Shot | 12 | 8.3% |
| 6 | Dribble | 7 | 4.9% |
| 7 | Block | 6 | 4.2% |
| 8 | Goal Keeper | 6 | 4.2% |
| 9 | Dribbled Past | 5 | 3.5% |
| 10 | Ball Recovery | 3 | 2.1% |
| 11 | Duel | 2 | 1.4% |

**Total: 141 events (97.9% of dataset)**

---

## 🎯 Quick Template Guide

### 1️⃣ Ball Receipt*
```
Template: "{player_name} receives"
Required: player_name
Optional: zone, under_pressure
```
**Example:** "Jordan Pickford receives"

---

### 2️⃣ Carry
```
Template: 
  IF under_pressure:
    "{player_name} under pressure, carries forward"
  ELSE:
    "{player_name} carries the ball"

Required: player_name, under_pressure
Optional: carry_distance, duration
```
**Examples:**
- "Jordan Pickford carries the ball"
- "Daniel Carvajal Ramos under pressure, carries forward"

---

### 3️⃣ Pressure
```
Template:
  IF target_known:
    "{player_name} presses {target_player}"
  ELSE:
    "{player_name} presses the ball carrier"

Required: player_name
Context: target_player (from previous event)
```
**Examples:**
- "Jude Bellingham presses Daniel Carvajal Ramos"
- "Fabián Ruiz Peña presses the ball carrier"

---

### 4️⃣ Pass
```
Template:
  distance = "short" (<15m) / "medium" (15-30m) / "long" (>30m)
  
  IF pass_height == "Ground Pass":
    "{player_name} plays {distance} pass along the ground to {recipient}"
  ELIF pass_height == "High Pass":
    "{player_name} plays {distance} ball through the air to {recipient}"
  ELSE:
    "{player_name} plays {distance} pass to {recipient}"

Required: player_name, pass_recipient, pass_length, pass_height
Optional: pass_outcome, under_pressure
```
**Examples:**
- "Jordan Pickford plays long ball through the air to Bukayo Saka"
- "Robin Aime Robert Le Normand plays medium pass along the ground to Daniel Carvajal Ramos"
- "Álvaro Borja Morata Martín plays short pass along the ground to Pedro González López"

---

### 5️⃣ Shot
```
Template:
  IF shot_outcome == "Blocked":
    "{player_name} shoots - BLOCKED!"
  ELIF shot_outcome == "Saved":
    "{player_name} shoots - saved by the goalkeeper!"
  ELIF shot_outcome in ["Off T", "Wayward"]:
    "{player_name} shoots - just wide!"
  ELIF shot_outcome == "Goal":
    "{player_name} shoots - GOAL!"
  ELSE:
    "{player_name} shoots!"

Required: player_name, shot_outcome
Optional: shot_xg, shot_body_part, under_pressure
```
**Examples:**
- "Nicholas Williams Arthuer shoots - BLOCKED!"
- "Pedro González López shoots - saved by the goalkeeper!"
- "Robin Aime Robert Le Normand shoots - just wide!"
- "David Strelec shoots!"

---

### 6️⃣ Dribble
```
Template:
  IF dribble_nutmeg:
    "{player_name} takes on {defender} - NUTMEG!"
  ELIF dribble_outcome == "Complete":
    "{player_name} beats {defender}"
  ELSE:
    "{player_name} takes on {defender}"

Required: player_name, dribble_outcome
Optional: dribble_nutmeg, under_pressure
Context: defender_name (from Dribbled Past event)
```
**Examples:**
- "Luke Shaw takes on Daniel Carvajal Ramos - NUTMEG!"
- "Declan Rice beats the defender"
- "Nicholas Williams Arthuer takes on the defender - NUTMEG!"

---

### 7️⃣ Block
```
Template: "BLOCKED by {player_name}!"

Required: player_name
Context: Previous shot details
```
**Examples:**
- "BLOCKED by John Stones!"
- "BLOCKED by Rodrigo Hernández Cascante!"
- "BLOCKED by Marc Guehi!"

---

### 8️⃣ Goal Keeper
```
Template: "Goalkeeper deals with it"

Required: player_name (optional in template)
Context: Previous shot details
```
**Example:** "Goalkeeper deals with it"

---

### 9️⃣ Dribbled Past
```
Template: "Dribbled Past"

Required: player_name (defender)
Context: Next dribble event
```
**Example:** "Dribbled Past"

---

### 🔟 Ball Recovery
```
Template: "Ball Recovery"

Required: player_name (optional in template)
Optional: zone, under_pressure
```
**Example:** "Ball Recovery"

---

### 1️⃣1️⃣ Duel
```
Template: "Duel"

Required: player_name (optional in template)
Context: Related dribble event
```
**Example:** "Duel"

---

## 🔑 Key Data Fields by Event Type

| Event Type | Core Fields | Special Fields | Context Needed |
|-----------|-------------|----------------|----------------|
| **Ball Receipt*** | player, zone | under_pressure | Previous pass |
| **Carry** | player, distance, end_location | under_pressure, duration | Direction |
| **Pressure** | player, zone | duration | Target player |
| **Pass** | player, recipient, length, height | outcome, under_pressure | - |
| **Shot** | player, outcome, xG | body_part, under_pressure | Next event (block/save) |
| **Dribble** | player, outcome | nutmeg, under_pressure | Defender name |
| **Block** | player, zone | - | Previous shot |
| **Goal Keeper** | player, zone | - | Previous shot |
| **Dribbled Past** | player (defender) | - | Next dribble |
| **Ball Recovery** | player, zone | under_pressure | - |
| **Duel** | player, zone | under_pressure | Outcome |

---

## 📋 Data Extraction Checklist

### Always Extract:
- ✅ `player_name`
- ✅ `team_name`
- ✅ `minute`, `second`
- ✅ `event_type`
- ✅ `zone_combined`
- ✅ `location_x`, `location_y`

### Event-Specific Fields:

**Pass:**
- `pass_recipient`
- `pass_length`
- `pass_height`
- `pass_outcome`

**Shot:**
- `shot_outcome`
- `shot_xg`
- `shot_body_part`

**Carry:**
- `carry_end_x`, `carry_end_y`
- `carry_distance`
- `duration`

**Dribble:**
- `dribble_outcome`
- `dribble_nutmeg`

**Pressure:**
- `duration`
- Target player (from context)

---

## 🔄 Context Integration

### Sequence-Level Context:
```python
# Use these fields to understand event flow
sequence_id         # Groups related events
event_position      # Order within sequence (1-5)
is_key_event        # Highlights important moments
sequence_type       # "shot_sequence", "dribble_sequence", etc.
```

### Finding Related Events:
```python
# Example: Find who is being pressed
sequence_events = df[df['sequence_id'] == current_sequence_id]
previous_event = sequence_events[sequence_events['event_position'] == current_pos - 1]
target_player = previous_event['player_name']
```

### Combining Event & Sequence Commentary:
```python
# Individual event
event_commentary = "Nicholas Williams Arthuer shoots - BLOCKED!"

# Full sequence context
sequence_commentary = "[11:08] Nicholas Williams Arthuer receives. " \
                     "Nicholas Williams Arthuer under pressure, carries forward. " \
                     "John Stones presses Nicholas Williams Arthuer. " \
                     "Nicholas Williams Arthuer shoots - BLOCKED!. " \
                     "BLOCKED by John Stones!"
```

---

## 💡 Implementation Tips

### 1. Template Selection
```python
def generate_commentary(event):
    event_type = event['event_type']
    
    templates = {
        'Ball Receipt*': lambda e: f"{e['player_name']} receives",
        'Carry': format_carry,
        'Pressure': format_pressure,
        'Pass': format_pass,
        'Shot': format_shot,
        'Dribble': format_dribble,
        'Block': lambda e: f"BLOCKED by {e['player_name']}!",
        'Goal Keeper': lambda e: "Goalkeeper deals with it",
        'Dribbled Past': lambda e: "Dribbled Past",
        'Ball Recovery': lambda e: "Ball Recovery",
        'Duel': lambda e: "Duel"
    }
    
    return templates[event_type](event)
```

### 2. Context Extraction
```python
def get_sequence_context(df, sequence_id, event_position):
    """Extract context from surrounding events"""
    sequence = df[df['sequence_id'] == sequence_id].sort_values('event_position')
    
    current = sequence[sequence['event_position'] == event_position].iloc[0]
    previous = sequence[sequence['event_position'] < event_position]
    next_events = sequence[sequence['event_position'] > event_position]
    
    return {
        'current': current,
        'previous': previous.to_dict('records'),
        'next': next_events.to_dict('records')
    }
```

### 3. Data Validation
```python
def validate_event_data(event, event_type):
    """Check if required fields are present"""
    required_fields = {
        'Pass': ['player_name', 'pass_recipient', 'pass_length', 'pass_height'],
        'Shot': ['player_name', 'shot_outcome'],
        'Carry': ['player_name', 'under_pressure'],
        # ... etc
    }
    
    for field in required_fields.get(event_type, ['player_name']):
        if pd.isna(event.get(field)):
            return False
    return True
```

---

## 📊 Usage Statistics

- **Complex Events** (need context): Pass, Pressure, Dribble (3 types)
- **Medium Events** (conditional logic): Carry, Shot (2 types)
- **Simple Events** (fixed template): Ball Receipt*, Block, Goal Keeper, Dribbled Past, Ball Recovery, Duel (6 types)

**Coverage:** These 11 event types cover **97.9%** of all events in the dataset.

---

## 🎓 Next Steps

1. **Train NLP Model** using `event_commentary_training_data.csv`
2. **Test Templates** with `generate_event_type_examples.py`
3. **Extend Coverage** to remaining 2.1% of events
4. **Add Variations** to templates for more natural language
5. **Integrate Context** from related_events columns
6. **Add Sentiment** based on match situation

---

For detailed examples and full implementation, see:
- `TOP_11_EVENTS_COMMENTARY_GUIDE.md` - Comprehensive guide
- `generate_event_type_examples.py` - Python implementation
- `event_commentary_training_data.csv` - Training data
