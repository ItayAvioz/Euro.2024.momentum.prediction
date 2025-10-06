# Top 11 Event Types - Commentary Guide

## Overview
This document provides detailed templates, data extraction fields, and real examples for the 11 most frequent event types in our Euro 2024 dataset.

**Event Distribution:**
1. Ball Receipt* (29 occurrences)
2. Carry (26 occurrences)
3. Pressure (26 occurrences)
4. Pass (19 occurrences)
5. Shot (12 occurrences)
6. Dribble (7 occurrences)
7. Block (6 occurrences)
8. Goal Keeper (6 occurrences)
9. Dribbled Past (5 occurrences)
10. Ball Recovery (3 occurrences)
11. Duel (2 occurrences)

---

## 1. BALL RECEIPT*

### Data to Extract:
- **Core Fields:**
  - `player_name`: Who received the ball
  - `team_name`: Player's team
  - `minute`, `second`: Timing
  - `location_x`, `location_y`: Position coordinates
  - `zone_combined`: Field zone (e.g., "central attacking third")
  - `under_pressure`: Boolean - is player pressured?
  
- **Context Fields:**
  - `possession_team`: Which team has possession
  - `play_pattern`: How play is developing (e.g., "From Kick Off", "Regular Play")
  - Previous event: Who passed the ball (from sequence)

### Template:
```
{player_name} receives [the ball]
```

### Real Examples:

**Example 1:** Simple Reception
```
Data:
- Player: Jordan Pickford
- Team: England
- Time: 0:02
- Zone: central defensive third
- Under Pressure: False
- Play Pattern: From Kick Off

Commentary: "Jordan Pickford receives"
```

**Example 2:** Reception Under Pressure
```
Data:
- Player: Daniel Olmo Carvajal
- Team: Spain
- Time: 0:40
- Zone: left midfield
- Under Pressure: True
- Play Pattern: From Goal Kick

Commentary: "Daniel Olmo Carvajal receives"
```

**Example 3:** Attacking Reception
```
Data:
- Player: Bukayo Saka
- Team: England
- Time: 0:09
- Zone: left attacking third
- Under Pressure: False
- Play Pattern: From Kick Off

Commentary: "Bukayo Saka receives"
```

---

## 2. CARRY

### Data to Extract:
- **Core Fields:**
  - `player_name`: Who is carrying
  - `team_name`: Player's team
  - `minute`, `second`: Timing
  - `location_x`, `location_y`: Starting position
  - `carry_end_x`, `carry_end_y`: Ending position
  - `carry_distance`: Distance covered
  - `zone_combined`: Starting zone
  - `under_pressure`: Boolean - is player pressured?
  - `duration`: How long the carry lasted

- **Derived Fields:**
  - Direction: Forward/backward/lateral (from coordinates)
  - End zone: Where the carry ended

### Template:
```
IF under_pressure:
    "{player_name} under pressure, carries forward"
ELSE:
    "{player_name} carries the ball"
```

### Real Examples:

**Example 1:** Simple Carry
```
Data:
- Player: Jordan Pickford
- Team: England
- Time: 0:02
- Start: (25.4, 38.8) - central defensive third
- End: (28.7, 31.6)
- Distance: 7.92 meters
- Under Pressure: False
- Duration: 1.87 seconds

Commentary: "Jordan Pickford carries the ball"
```

**Example 2:** Carry Under Pressure
```
Data:
- Player: Daniel Carvajal Ramos
- Team: Spain
- Time: 0:37
- Start: (20.6, 75.8) - left defensive third
- End: (28.6, 76.4)
- Distance: 8.02 meters
- Under Pressure: True
- Duration: 1.77 seconds

Commentary: "Daniel Carvajal Ramos under pressure, carries forward"
```

**Example 3:** Long Attacking Carry
```
Data:
- Player: Nicholas Williams Arthuer
- Team: Spain
- Time: 11:08
- Start: (99.4, 9.1) - right attacking third
- End: (115.6, 28.4)
- Distance: 25.20 meters
- Under Pressure: True
- Duration: 4.67 seconds

Commentary: "Nicholas Williams Arthuer under pressure, carries forward"
```

---

## 3. PRESSURE

### Data to Extract:
- **Core Fields:**
  - `player_name`: Who is pressing
  - `team_name`: Pressing player's team
  - `minute`, `second`: Timing
  - `location_x`, `location_y`: Position of presser
  - `zone_combined`: Field zone
  - `duration`: How long the pressure lasted
  - `possession_team`: Which team has the ball (opponent)

- **Context Fields:**
  - Previous event: Who is being pressed (from sequence)
  - Next event: Outcome of the pressure

### Template:
```
IF target_player_known:
    "{player_name} presses {target_player}"
ELSE:
    "{player_name} presses the ball carrier"
```

### Real Examples:

**Example 1:** Pressing Named Player
```
Data:
- Player: Jude Bellingham
- Team: England
- Time: 0:38
- Zone: right attacking third
- Duration: 0.54 seconds
- Target: Daniel Carvajal Ramos (from context)
- Play Pattern: From Goal Kick

Commentary: "Jude Bellingham presses Daniel Carvajal Ramos"
```

**Example 2:** Pressing Ball Carrier
```
Data:
- Player: Fabián Ruiz Peña
- Team: Spain
- Time: 7:14
- Zone: right attacking third
- Duration: 1.19 seconds
- Target: Unknown (generic)
- Play Pattern: Regular Play

Commentary: "Fabián Ruiz Peña presses the ball carrier"
```

**Example 3:** Defensive Pressure
```
Data:
- Player: Declan Rice
- Team: England
- Time: 0:40
- Zone: right midfield
- Duration: 0.29 seconds
- Target: Daniel Carvajal Ramos
- Play Pattern: From Goal Kick

Commentary: "Declan Rice presses Daniel Carvajal Ramos"
```

---

## 4. PASS

### Data to Extract:
- **Core Fields:**
  - `player_name`: Who is passing
  - `team_name`: Player's team
  - `minute`, `second`: Timing
  - `location_x`, `location_y`: Pass origin
  - `zone_combined`: Starting zone
  - `pass_recipient`: Who receives (if available)
  - `pass_length`: Distance of pass
  - `pass_height`: "Ground Pass", "Low Pass", "High Pass"
  - `pass_outcome`: Success/failure (None, "Incomplete", "Out", "Unknown")
  - `under_pressure`: Boolean
  - `duration`: Pass duration

- **Derived Fields:**
  - Pass type: Short (<15m), Medium (15-30m), Long (>30m)
  - Pass direction: "along the ground", "through the air"

### Template:
```
IF pass_length < 15:
    pass_distance = "short"
ELIF pass_length < 30:
    pass_distance = "medium"
ELSE:
    pass_distance = "long"

IF pass_height == "Ground Pass":
    pass_trajectory = "along the ground"
ELSE:
    pass_trajectory = "through the air"

"{player_name} plays {pass_distance} pass {pass_trajectory} to {pass_recipient}"

IF pass_height == "High Pass":
    "{player_name} plays {pass_distance} ball through the air to {pass_recipient}"
```

### Real Examples:

**Example 1:** Long High Pass
```
Data:
- Player: Jordan Pickford
- Team: England
- Time: 0:04
- Zone: central defensive third
- Recipient: Bukayo Saka
- Length: 98.18 meters
- Height: High Pass
- Outcome: Out
- Under Pressure: False
- Duration: 5.14 seconds

Commentary: "Jordan Pickford plays long ball through the air to Bukayo Saka"
```

**Example 2:** Medium Ground Pass
```
Data:
- Player: Robin Aime Robert Le Normand
- Team: Spain
- Time: 0:36
- Zone: left defensive third
- Recipient: Daniel Carvajal Ramos
- Length: 21.97 meters
- Height: Ground Pass
- Outcome: None (success)
- Under Pressure: False
- Duration: 1.39 seconds

Commentary: "Robin Aime Robert Le Normand plays medium pass along the ground to Daniel Carvajal Ramos"
```

**Example 3:** Short Ground Pass Under Pressure
```
Data:
- Player: Álvaro Borja Morata Martín
- Team: Spain
- Time: 0:51
- Zone: central attacking third
- Recipient: Pedro González López
- Length: 8.02 meters
- Height: Ground Pass
- Outcome: None (success)
- Under Pressure: True
- Duration: 1.20 seconds

Commentary: "Álvaro Borja Morata Martín plays short pass along the ground to Pedro González López"
```

**Example 4:** Long Pass Under Pressure
```
Data:
- Player: Bukayo Saka
- Team: England
- Time: 16:19
- Zone: left attacking third
- Recipient: Declan Rice
- Length: 19.52 meters
- Height: Ground Pass
- Outcome: None (success)
- Under Pressure: True
- Duration: 1.56 seconds

Commentary: "Bukayo Saka plays medium pass along the ground to Declan Rice"
```

---

## 5. SHOT

### Data to Extract:
- **Core Fields:**
  - `player_name`: Who is shooting
  - `team_name`: Player's team
  - `minute`, `second`: Timing
  - `location_x`, `location_y`: Shot origin
  - `zone_combined`: Shooting zone
  - `shot_xg`: Expected goals value
  - `shot_outcome`: "Goal", "Saved", "Blocked", "Off T" (off target), "Wayward"
  - `shot_body_part`: "Left Foot", "Right Foot", "Head"
  - `under_pressure`: Boolean
  - `duration`: Shot duration

- **Context Fields:**
  - Play pattern: "Regular Play", "From Free Kick", "From Corner"
  - Next event: What happened after (e.g., Block, Goal Keeper)

### Template:
```
IF shot_outcome == "Blocked":
    "{player_name} shoots - BLOCKED!"
ELIF shot_outcome == "Saved":
    "{player_name} shoots - saved by the goalkeeper!"
ELIF shot_outcome == "Off T" OR shot_outcome == "Wayward":
    "{player_name} shoots - just wide!"
ELIF shot_outcome == "Goal":
    "{player_name} shoots - GOAL!"
ELSE:
    "{player_name} shoots!"
```

### Real Examples:

**Example 1:** Blocked Shot
```
Data:
- Player: Nicholas Williams Arthuer
- Team: Spain
- Time: 11:13
- Zone: central attacking third
- Position: (115.6, 28.4)
- xG: 0.068
- Outcome: Blocked
- Body Part: Left Foot
- Under Pressure: True
- Duration: 0.05 seconds
- Play Pattern: From Free Kick

Commentary: "Nicholas Williams Arthuer shoots - BLOCKED!"
```

**Example 2:** Saved Shot
```
Data:
- Player: Pedro González López
- Team: Spain
- Time: 0:52
- Zone: central attacking third
- Position: (101.5, 39.7)
- xG: 0.117
- Outcome: Saved
- Body Part: Left Foot
- Under Pressure: True
- Duration: 0.55 seconds
- Play Pattern: Regular Play

Commentary: "Pedro González López shoots - saved by the goalkeeper!"
```

**Example 3:** Shot Off Target
```
Data:
- Player: Robin Aime Robert Le Normand
- Team: Spain
- Time: 12:21
- Zone: central attacking third
- Position: (112.9, 36.2)
- xG: 0.117
- Outcome: Off T
- Body Part: Right Foot
- Under Pressure: True
- Duration: 1.07 seconds
- Play Pattern: From Corner

Commentary: "Robin Aime Robert Le Normand shoots - just wide!"
```

**Example 4:** Simple Shot
```
Data:
- Player: David Strelec
- Team: Slovakia
- Time: 3:48
- Zone: central attacking third
- Position: (107.3, 35.8)
- xG: 0.092
- Outcome: Wayward
- Body Part: Right Foot
- Under Pressure: False
- Duration: 1.71 seconds
- Play Pattern: From Free Kick

Commentary: "David Strelec shoots!"
```

---

## 6. DRIBBLE

### Data to Extract:
- **Core Fields:**
  - `player_name`: Who is dribbling
  - `team_name`: Player's team
  - `minute`, `second`: Timing
  - `location_x`, `location_y`: Dribble position
  - `zone_combined`: Field zone
  - `dribble_outcome`: "Complete", "Incomplete"
  - `dribble_nutmeg`: Boolean - did they nutmeg?
  - `under_pressure`: Boolean
  - `duration`: Dribble duration

- **Context Fields:**
  - Previous/Next event: "Dribbled Past" event indicates defender beaten
  - Defender name (from context)

### Template:
```
IF dribble_nutmeg:
    IF defender_known:
        "{player_name} takes on {defender_name} - NUTMEG!"
    ELSE:
        "{player_name} takes on the defender - NUTMEG!"
ELIF dribble_outcome == "Complete":
    IF defender_known:
        "{player_name} beats {defender_name}"
    ELSE:
        "{player_name} beats the defender"
ELSE:
    IF defender_known:
        "{player_name} takes on {defender_name}"
    ELSE:
        "{player_name} takes on the defender"
```

### Real Examples:

**Example 1:** Nutmeg Dribble
```
Data:
- Player: Luke Shaw
- Team: England
- Time: 1:39
- Zone: right midfield
- Position: (51.1, 2.4)
- Outcome: Incomplete
- Nutmeg: True
- Under Pressure: True
- Duration: 0.0 seconds
- Defender: Daniel Carvajal Ramos (from context)

Commentary: "Luke Shaw takes on Daniel Carvajal Ramos - NUTMEG!"
```

**Example 2:** Successful Dribble
```
Data:
- Player: Declan Rice
- Team: England
- Time: 7:15
- Zone: left defensive third
- Position: (7.5, 56.7)
- Outcome: Complete
- Nutmeg: False
- Under Pressure: True
- Duration: 0.0 seconds
- Defender: Fabián Ruiz Peña (from context)

Commentary: "Declan Rice beats the defender"
```

**Example 3:** Nutmeg in Midfield
```
Data:
- Player: Nicholas Williams Arthuer
- Team: Spain
- Time: 5:03
- Zone: right midfield
- Position: (69.2, 5.2)
- Outcome: Complete
- Nutmeg: True
- Under Pressure: True
- Duration: 0.0 seconds
- Defender: Joshua Kimmich (from context)

Commentary: "Nicholas Williams Arthuer takes on the defender - NUTMEG!"
```

**Example 4:** Incomplete Dribble
```
Data:
- Player: Leroy Sané
- Team: Germany
- Time: 8:52
- Zone: left midfield
- Position: (49.2, 73.8)
- Outcome: Incomplete
- Nutmeg: False
- Under Pressure: True
- Duration: 0.0 seconds
- Defender: Marc Cucurella Saseta (from context)

Commentary: "Leroy Sané beats the defender"
```

---

## 7. BLOCK

### Data to Extract:
- **Core Fields:**
  - `player_name`: Who blocked
  - `team_name`: Player's team
  - `minute`, `second`: Timing
  - `location_x`, `location_y`: Block position
  - `zone_combined`: Field zone
  - `under_pressure`: Boolean
  - `duration`: Always 0.0 (instant)

- **Context Fields:**
  - Previous event: Shot details (who shot, from where)
  - Possession team: Attacking team

### Template:
```
"BLOCKED by {player_name}!"
```

### Real Examples:

**Example 1:** Defensive Block
```
Data:
- Player: John Stones
- Team: England
- Time: 11:13
- Zone: central defensive third
- Position: (4.1, 50.8)
- Under Pressure: False
- Duration: 0.0 seconds
- Previous Event: Shot by Nicholas Williams Arthuer (xG: 0.068)

Commentary: "BLOCKED by John Stones!"
```

**Example 2:** Midfield Block
```
Data:
- Player: Rodrigo Hernández Cascante
- Team: Spain
- Time: 16:20
- Zone: central defensive third
- Position: (21.6, 39.3)
- Under Pressure: False
- Duration: 0.0 seconds
- Previous Event: Shot by Declan Rice (xG: 0.049)

Commentary: "BLOCKED by Rodrigo Hernández Cascante!"
```

**Example 3:** Crucial Block
```
Data:
- Player: Marc Guehi
- Team: England
- Time: 27:27
- Zone: central defensive third
- Position: (15.8, 31.6)
- Under Pressure: False
- Duration: 0.0 seconds
- Previous Event: Shot by Fabián Ruiz Peña (xG: 0.048)

Commentary: "BLOCKED by Marc Guehi!"
```

---

## 8. GOAL KEEPER

### Data to Extract:
- **Core Fields:**
  - `player_name`: Goalkeeper name
  - `team_name`: Player's team
  - `minute`, `second`: Timing
  - `location_x`, `location_y`: Position (usually near goal)
  - `zone_combined`: Usually defensive third
  - `under_pressure`: Boolean
  - `duration`: Always 0.0

- **Context Fields:**
  - Previous event: Shot details
  - Type of save: From shot outcome

### Template:
```
"Goalkeeper deals with it"
```

### Real Examples:

**Example 1:** After Off-Target Shot
```
Data:
- Player: Jordan Pickford
- Team: England
- Time: 12:22
- Zone: central defensive third
- Position: (1.1, 37.6)
- Under Pressure: False
- Duration: 0.0 seconds
- Previous Event: Shot Off T by Robin Aime Robert Le Normand

Commentary: "Goalkeeper deals with it"
```

**Example 2:** After Save
```
Data:
- Player: Manuel Neuer
- Team: Germany
- Time: 0:53
- Zone: central defensive third
- Position: (1.5, 39.7)
- Under Pressure: False
- Duration: 0.0 seconds
- Previous Event: Shot Saved by Pedro González López (xG: 0.117)

Commentary: "Goalkeeper deals with it"
```

**Example 3:** Routine Collection
```
Data:
- Player: Jordan Pickford
- Team: England
- Time: 3:50
- Zone: central defensive third
- Position: (2.4, 41.8)
- Under Pressure: False
- Duration: 0.0 seconds
- Previous Event: Shot Wayward by David Strelec

Commentary: "Goalkeeper deals with it"
```

---

## 9. DRIBBLED PAST

### Data to Extract:
- **Core Fields:**
  - `player_name`: Defender who was beaten
  - `team_name`: Player's team
  - `minute`, `second`: Timing
  - `location_x`, `location_y`: Position
  - `zone_combined`: Field zone
  - `under_pressure`: Boolean
  - `duration`: Always 0.0

- **Context Fields:**
  - Next event: Dribble event (attacker who beat them)
  - Related to Pressure event

### Template:
```
"Dribbled Past"
```

### Real Examples:

**Example 1:** Midfielder Beaten
```
Data:
- Player: Fabián Ruiz Peña
- Team: Spain
- Time: 7:15
- Zone: right attacking third
- Position: (112.6, 23.4)
- Under Pressure: False
- Duration: 0.0 seconds
- Next Event: Dribble Complete by Declan Rice

Commentary: "Dribbled Past"
```

**Example 2:** Full-Back Beaten
```
Data:
- Player: Joshua Kimmich
- Team: Germany
- Time: 5:03
- Zone: left midfield
- Position: (50.9, 74.9)
- Under Pressure: False
- Duration: 0.0 seconds
- Next Event: Dribble Complete (Nutmeg) by Nicholas Williams Arthuer

Commentary: "Dribbled Past"
```

**Example 3:** Defender Beaten
```
Data:
- Player: Marc Cucurella Saseta
- Team: Spain
- Time: 8:52
- Zone: right midfield
- Position: (70.9, 6.3)
- Under Pressure: False
- Duration: 0.0 seconds
- Next Event: Dribble Incomplete by Leroy Sané

Commentary: "Dribbled Past"
```

---

## 10. BALL RECOVERY

### Data to Extract:
- **Core Fields:**
  - `player_name`: Who recovered the ball
  - `team_name`: Player's team
  - `minute`, `second`: Timing
  - `location_x`, `location_y`: Recovery position
  - `zone_combined`: Field zone
  - `under_pressure`: Boolean
  - `duration`: Always 0.0

- **Context Fields:**
  - Play pattern: Usually turnover situation
  - Next event: What happens after recovery

### Template:
```
"Ball Recovery"
```

### Real Examples:

**Example 1:** Attacking Recovery
```
Data:
- Player: Jamal Musiala
- Team: Germany
- Time: 0:06
- Zone: central attacking third
- Position: (81.8, 32.5)
- Under Pressure: False
- Duration: 0.0 seconds
- Play Pattern: From Kick Off
- Next Event: Carry under pressure

Commentary: "Ball Recovery"
```

**Example 2:** Midfield Recovery
```
Data:
- Player: Juraj Kucka
- Team: Slovakia
- Time: 1:05
- Zone: central midfield
- Position: (58.4, 42.6)
- Under Pressure: True
- Duration: 0.0 seconds
- Play Pattern: From Throw In
- Next Event: Carry and dribble

Commentary: "Ball Recovery"
```

---

## 11. DUEL

### Data to Extract:
- **Core Fields:**
  - `player_name`: Player involved in duel
  - `team_name`: Player's team
  - `minute`, `second`: Timing
  - `location_x`, `location_y`: Duel position
  - `zone_combined`: Field zone
  - `under_pressure`: Boolean
  - `duration`: Always 0.0

- **Context Fields:**
  - Related to Dribble event
  - Outcome: Who wins possession

### Template:
```
"Duel"
```

### Real Examples:

**Example 1:** Defensive Duel
```
Data:
- Player: Daniel Carvajal Ramos
- Team: Spain
- Time: 1:39
- Zone: left midfield
- Position: (69.0, 77.7)
- Under Pressure: True
- Duration: 0.0 seconds
- Previous Event: Dribble (Nutmeg) by Luke Shaw
- Outcome: Spain wins possession

Commentary: "Duel"
```

**Example 2:** Midfield Duel
```
Data:
- Player: Harry Kane
- Team: England
- Time: 1:05
- Zone: central midfield
- Position: (62.7, 39.3)
- Under Pressure: True
- Duration: 0.0 seconds
- Previous Event: Dribble by Juraj Kucka
- Outcome: Slovakia retains possession

Commentary: "Duel"
```

---

## Summary Table

| Event Type | Key Data Fields | Template Complexity | Context Needed |
|-----------|----------------|-------------------|----------------|
| Ball Receipt* | player, zone, pressure | Simple | Previous pass |
| Carry | player, distance, end position, pressure | Medium | Direction, speed |
| Pressure | player, target, zone | Simple | Ball carrier |
| Pass | player, recipient, length, height | Complex | Distance category |
| Shot | player, outcome, xG, body part | Complex | Result, blocker |
| Dribble | player, outcome, nutmeg, defender | Medium | Defender name |
| Block | player, zone | Simple | Shot details |
| Goal Keeper | player | Simple | Previous shot |
| Dribbled Past | player (defender) | Simple | Attacker |
| Ball Recovery | player, zone | Simple | Next action |
| Duel | player, zone | Simple | Outcome |

---

## Implementation Notes

### Data Extraction Priority:
1. **Always extract:** player_name, team_name, minute, second, event_type, zone_combined
2. **Event-specific:** outcome fields, distances, pressure status
3. **Context from sequence:** previous/next events, possession changes

### Template Selection Logic:
```python
def generate_commentary(event_type, event_data, sequence_context):
    if event_type == "Pass":
        return format_pass_commentary(event_data)
    elif event_type == "Shot":
        return format_shot_commentary(event_data, sequence_context)
    elif event_type == "Carry":
        return format_carry_commentary(event_data)
    # ... etc
```

### Context Integration:
- Use `sequence_id` to link related events
- Use `event_position` to understand event flow
- Use `is_key_event` to emphasize important moments
- Combine `event_commentary` with `sequence_commentary` for full context

