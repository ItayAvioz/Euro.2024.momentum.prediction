# 🔍 **Complete Column Values Explanation**

## 📊 **Based on Real Data Examples from Euro 2024**

This document explains exactly what each column means and what the values represent, using actual examples from your dataset.

---

## ⚽ **EVENTS DATA - Column by Column Explanation**

### **Example Row from Netherlands vs England Semi-final:**
```
match_id: 3942819
minute: 0
second: 0
event_type: Pass
player_name: Kobbie Mainoo
team_name: England
home_team: Netherlands
away_team: England
```

### **📋 Column Meanings:**

#### **1. `match_id`** 
- **Value Example**: `3942819`
- **Meaning**: Unique identifier for each match
- **Use**: Links events to specific matches
- **Real Context**: This is Netherlands vs England Semi-final match

#### **2. `minute`**
- **Value Examples**: `0`, `1`, `45`, `90`
- **Meaning**: Match minute when event occurred
- **Range**: 0-90+ (regular time), 90+ (extra time)
- **Real Context**: `0` = match start, `45` = end of first half

#### **3. `second`**
- **Value Examples**: `0`, `2`, `4`, `5`, `8`
- **Meaning**: Second within the minute (0-59)
- **Use**: Precise timing of events
- **Real Context**: `00:00` = kickoff, `00:02` = 2 seconds after kickoff

#### **4. `event_type`**
- **Value Examples**: `Pass`, `Ball Receipt*`, `Carry`, `Pressure`, `Dribble`
- **Meaning**: What action happened on the field
- **Categories**:
  - `Pass` = Player passed ball to teammate
  - `Ball Receipt*` = Player successfully received the ball
  - `Carry` = Player moved forward with ball at feet
  - `Pressure` = Player applied pressure to opponent
  - `Shot` = Player attempted to score
  - `Dribble` = Player dribbled past opponent

#### **5. `player_name`**
- **Value Examples**: `Kobbie Mainoo`, `Jordan Pickford`, `Memphis Depay`, `Kyle Walker`
- **Meaning**: Name of player who performed the action
- **Special**: `nan` for team-level events (Starting XI, Half Start)

#### **6. `team_name`**
- **Value Examples**: `England`, `Netherlands`
- **Meaning**: Full team name of the player
- **Use**: Identifies which team performed the action

#### **7. `home_team`**
- **Value**: `Netherlands`
- **Meaning**: Team playing at home venue
- **Constant**: Same for all events in this match

#### **8. `away_team`**
- **Value**: `England`
- **Meaning**: Team playing away from home
- **Constant**: Same for all events in this match

---

## 🎯 **360° DATA - Column by Column Explanation**

### **Example Row:**
```
event_uuid: 25dfc952-7a85-464f-b884-982064d46cc9
match_id: 3942819
home_team: Netherlands
away_team: England
stage: Semi-finals
visible_area: [82.05880352279489, 80.0, 37.469993200629204, 80.0, ...]
freeze_frame: [{'teammate': True, 'actor': False, 'keeper': True, 'location': [22.7, 41.0]}, ...]
```

### **📋 Column Meanings:**

#### **1. `event_uuid`**
- **Value Example**: `25dfc952-7a85-464f-b884-982064d46cc9`
- **Meaning**: Unique identifier linking to specific event
- **Use**: Connects 360° data to events data
- **Format**: UUID string (universally unique identifier)

#### **2. `match_id`**
- **Value**: `3942819`
- **Meaning**: Same match identifier as in events data
- **Use**: Ensures 360° data belongs to correct match

#### **3. `home_team` & `away_team`**
- **Values**: `Netherlands`, `England`
- **Meaning**: Same as events data
- **Use**: Match context consistency

#### **4. `stage`**
- **Value**: `Semi-finals`
- **Meaning**: Tournament stage
- **Other Examples**: `Group Stage`, `Round of 16`, `Quarter-finals`, `Final`

#### **5. `visible_area`**
- **Value Example**: `[82.05880352279489, 80.0, 37.469993200629204, 80.0, ...]`
- **Meaning**: Camera field of view coordinates
- **Format**: Array of coordinates defining visible field area
- **Use**: Defines what area of field is being tracked

#### **6. `freeze_frame`** (Most Important)
- **Value**: Array of player position objects
- **Length**: 21-22 players per frame
- **Structure**: Each player has:
  - `location`: [x, y] coordinates
  - `teammate`: True/False
  - `actor`: True/False (who performed the event)
  - `keeper`: True/False

---

## 👥 **FREEZE FRAME PLAYER OBJECT - Detailed Breakdown**

### **Example Player Objects:**
```json
{
  "teammate": true,
  "actor": false,
  "keeper": true,
  "location": [22.7, 41.0]
}
```

### **📋 Player Object Fields:**

#### **1. `location`**
- **Value Example**: `[22.7, 41.0]`
- **Meaning**: Player's X,Y position on field
- **Format**: [x_coordinate, y_coordinate]
- **Real Context**: `[22.7, 41.0]` = Near left goal, center of field

#### **2. `teammate`**
- **Values**: `True` or `False`
- **Meaning**: Is this player on same team as event actor?
- **Use**: Distinguish between team and opponents

#### **3. `actor`**
- **Values**: `True` or `False`
- **Meaning**: Is this player performing the event?
- **Use**: Identify who is doing the action (only 1 per frame)

#### **4. `keeper`**
- **Values**: `True` or `False`
- **Meaning**: Is this player a goalkeeper?
- **Use**: Special role identification

---

## 📐 **COORDINATE SYSTEM EXPLANATION**

### **Field Dimensions:**
- **Length**: 120 meters (X-axis)
- **Width**: 80 meters (Y-axis)

### **Key Positions:**
- **Left Goal**: X = 0, Y = 36-44
- **Right Goal**: X = 120, Y = 36-44
- **Center Circle**: X = 60, Y = 40
- **Left Penalty Area**: X = 0-18, Y = 18-62
- **Right Penalty Area**: X = 102-120, Y = 18-62

### **Real Player Position Examples:**
```
Player 1: [22.7, 41.0] = Near left goal, center (Goalkeeper)
Player 2: [46.5, 46.7] = Middle of field, slightly right
Player 3: [47.4, 64.5] = Middle of field, near top touchline
Player 4: [59.8, 29.1] = Center circle, bottom half
```

### **Field Zones:**
- **Defensive Third**: X < 40
- **Middle Third**: 40 ≤ X < 80
- **Attacking Third**: X ≥ 80

---

## ⏰ **TIME PROGRESSION EXAMPLE**

### **Actual Match Timeline:**
```
00:00 | Starting XI     | N/A              | Netherlands
00:00 | Starting XI     | N/A              | England
00:00 | Half Start      | N/A              | Netherlands
00:00 | Pass            | Kobbie Mainoo    | England
00:02 | Ball Receipt*   | Jordan Pickford  | England
00:02 | Carry           | Jordan Pickford  | England
00:04 | Pressure        | Memphis Depay    | Netherlands
00:05 | Pass            | Jordan Pickford  | England
```

### **What This Shows:**
- **Match Setup**: Starting XI and Half Start events
- **First Action**: Kobbie Mainoo passes at kickoff
- **Ball Movement**: Jordan Pickford receives and carries
- **Pressure**: Memphis Depay applies pressure
- **Response**: Jordan Pickford passes under pressure

---

## 🔗 **Data Connection Examples**

### **How Events Link to 360° Data:**
1. **Event occurs**: `Pass` by `Kobbie Mainoo` at `00:00`
2. **360° captures**: Positions of all 21 players at that moment
3. **Connection**: `event_uuid` links the pass to the player positions
4. **Analysis**: Can see where everyone was when pass happened

### **Practical Use:**
- **Commentary**: "Kobbie Mainoo passes with 3 opponents nearby"
- **Analysis**: "Pass was made under moderate pressure"
- **Quality**: "Pass had 60% success probability based on positions"

---

## ✅ **Summary of Key Insights**

### **Your Data Contains:**
- **Match**: Netherlands vs England (Semi-final)
- **Events**: 100+ actions with precise timing
- **Positions**: 21-22 players tracked per event
- **Precision**: Second-by-second timing
- **Coverage**: Complete tactical picture

### **Perfect For:**
- **🎙️ Commentary Generation**: "Player X passes under pressure"
- **🔮 Move Quality Prediction**: Success probability based on positions
- **⚔️ Tactical Analysis**: Team shape and pressing patterns
- **📊 Performance Analysis**: Individual player effectiveness

Your Euro 2024 dataset provides the complete foundation for advanced soccer analytics and commentary generation! 🏆 