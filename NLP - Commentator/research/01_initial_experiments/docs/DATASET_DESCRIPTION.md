# 📊 NLP Commentator - Complete Datasets Description

## 🎯 Overview

Two complementary datasets have been created for NLP Commentator development:

---

## 📋 **Dataset 1: Action Event Sequences** 
**File**: `commentator_training_data.csv`

### Purpose
Training data for generating commentary during match action sequences.

### Specifications
- **144 events** across **30 sequences**
- **3 exciting matches** (Final, QF, R16)
- **2-5 consecutive events** per sequence
- Focus on: Goals, Shots, Dribbles, Pressure, Carries

### Key Features
- ✅ **Sequence Context**: event_position, sequence_length, is_key_event
- ✅ **Event Details**: type, player, location, outcomes
- ✅ **Match Context**: teams, possession, play_pattern
- ✅ **Event-specific data**: shot/pass/dribble/carry details

### Use Case
*"In the 67th minute, Yamal receives in the final third, drives forward, and threads a pass to Williams... GOAL!"*

### Columns (35 total)
1. Sequence metadata (6): sequence_id, sequence_type, sequence_key_event, event_position, sequence_length, is_key_event
2. Event identification (9): match_id, id, index, minute, second, period, timestamp, type, event_team
3. Player/Team (4): player, player_id, team, position
4. Location (1): location [x, y]
5. Event details (7): shot, pass, dribble, carry, duel, interception, clearance, goalkeeper
6. Context (5): under_pressure, counterpress, play_pattern, duration, possession_team
7. Match info (2): home_team_name, away_team_name
8. Related (1): related_events

---

## 📋 **Dataset 2: Starting Events with Team Statistics**
**File**: `starting_events_with_team_stats.csv`

### Purpose
Pre-match and kick-off commentary with comprehensive team form and context.

### Specifications
- **40 events** (4 events × 10 matches)
- **10 diverse matches** across all tournament stages
- **First 4 events** of each match (kick-off sequence)
- **Complete team statistics** before the match

### Key Features
- ✅ **Team Form**: Wins, Draws, Losses (before match)
- ✅ **Goals**: Scored, Conceded, Goal Difference
- ✅ **Last Result**: Result, Score, Opponent
- ✅ **Match Context**: Stadium, Referee, Stage, Lineups
- ✅ **Final Score**: How the match ended

### Use Case
*"Welcome to the Final at Olympiastadion Berlin! Spain, with a perfect 6 wins from 6 matches, coming off a 2-1 victory over France. They face England, who have 3 wins and 3 draws, and beat Netherlands 2-1 in the semi-final..."*

### Columns (49 total)

#### Match Context (6 columns)
1. `match_id` - Unique match identifier
2. `match_date` - Match date (YYYY-MM-DD)
3. `stage` - Tournament stage (Group Stage, R16, QF, SF, Final)
4. `kick_off_time` - Match kick-off time
5. `stadium` - Stadium name
6. `referee` - Referee name

#### Teams & Result (4 columns)
7. `home_team` - Home team name
8. `away_team` - Away team name
9. `home_score` - Final home score
10. `away_score` - Final away score

#### Home Team Statistics (10 columns) - **Before this match**
11. `home_matches_played` - Matches played in tournament
12. `home_wins` - Number of wins
13. `home_draws` - Number of draws
14. `home_losses` - Number of losses
15. `home_goals_scored` - Total goals scored
16. `home_goals_conceded` - Total goals conceded
17. `home_goal_difference` - Goal difference (+/-)
18. `home_last_result` - Last match result (Win/Draw/Loss)
19. `home_last_score` - Last match score (e.g., "2-1")
20. `home_last_opponent` - Last opponent name

#### Away Team Statistics (10 columns) - **Before this match**
21. `away_matches_played` - Matches played in tournament
22. `away_wins` - Number of wins
23. `away_draws` - Number of draws
24. `away_losses` - Number of losses
25. `away_goals_scored` - Total goals scored
26. `away_goals_conceded` - Total goals conceded
27. `away_goal_difference` - Goal difference (+/-)
28. `away_last_result` - Last match result (Win/Draw/Loss)
29. `away_last_score` - Last match score (e.g., "1-0")
30. `away_last_opponent` - Last opponent name

#### Lineups (2 columns)
31. `home_lineup` - Starting 11 (format: "1.Name | 2.Name | ...")
32. `away_lineup` - Starting 11 (format: "1.Name | 2.Name | ...")

#### Event Details (14 columns)
33. `event_number` - Event sequence number (1-4)
34. `event_id` - Unique event identifier
35. `minute` - Minute of event
36. `second` - Second of event
37. `period` - Period (1=First Half, 2=Second Half)
38. `timestamp` - Exact timestamp
39. `event_type` - Type of event (Pass, Carry, Shot, etc.)
40. `event_team` - Team performing event
41. `is_home_team_event` - Boolean (True if home team)
42. `player_name` - Player performing event
43. `player_position` - Player position
44. `location` - Field coordinates [x, y]
45. `under_pressure` - Boolean (True if under pressure)
46. `duration` - Event duration (seconds)

#### Event-Specific Details (3 columns) - JSON format
47. `pass_details` - Pass specifics (recipient, length, outcome)
48. `carry_details` - Carry specifics (end_location, distance)
49. `shot_details` - Shot specifics (outcome, body_part, xG)

---

## 📊 **10 Selected Matches Overview**

| Match | Date | Teams | Score | Stage | Key Feature |
|-------|------|-------|-------|-------|-------------|
| 3930158 | 2024-06-14 | Germany vs Scotland | 5-1 | Group Stage | Opening match, high scoring |
| 3930171 | 2024-06-20 | Denmark vs England | 1-1 | Group Stage | Competitive draw |
| 3930180 | 2024-06-25 | Netherlands vs Austria | 2-3 | Group Stage | Upset victory |
| 3941017 | 2024-06-30 | England vs Slovakia | 2-1 | Round of 16 | Dramatic comeback |
| 3941021 | 2024-07-02 | Romania vs Netherlands | 0-3 | Round of 16 | Dominant performance |
| 3942226 | 2024-07-05 | Spain vs Germany | 2-1 | Quarter-finals | Extra time thriller |
| 3942382 | 2024-07-06 | Netherlands vs Turkey | 2-1 | Quarter-finals | Exciting match |
| 3942752 | 2024-07-09 | Spain vs France | 2-1 | Semi-finals | High quality |
| 3942819 | 2024-07-10 | Netherlands vs England | 1-2 | Semi-finals | Late winner |
| 3943043 | 2024-07-14 | Spain vs England | 2-1 | Final | Tournament finale |

---

## 💡 **Usage Examples**

### Pre-Match Commentary (Dataset 2)
```python
# Load starting events dataset
df = pd.read_csv('starting_events_with_team_stats.csv')

# Get match 3943043 (Final) first event
final_match = df[df['match_id'] == 3943043].iloc[0]

commentary = f"""
Welcome to the {final_match['stage']} at {final_match['stadium']}!

{final_match['home_team']} comes into this match with an incredible record:
- {final_match['home_wins']} wins from {final_match['home_matches_played']} matches
- {final_match['home_goals_scored']} goals scored, only {final_match['home_goals_conceded']} conceded
- Last match: {final_match['home_last_result']} vs {final_match['home_last_opponent']} ({final_match['home_last_score']})

{final_match['away_team']} have battled through:
- {final_match['away_wins']} wins, {final_match['away_draws']} draws from {final_match['away_matches_played']} matches
- Last match: {final_match['away_last_result']} vs {final_match['away_last_opponent']} ({final_match['away_last_score']})

Referee: {final_match['referee']}
Final Score: {final_match['home_team']} {final_match['home_score']}-{final_match['away_score']} {final_match['away_team']}
"""
```

**Output**:
```
Welcome to the Final at Olympiastadion Berlin!

Spain comes into this match with an incredible record:
- 6 wins from 6 matches
- 13 goals scored, only 3 conceded
- Last match: Win vs France (2-1)

England have battled through:
- 3 wins, 3 draws from 6 matches
- Last match: Win vs Netherlands (2-1)

Referee: François Letexier
Final Score: Spain 2-1 England
```

### Action Commentary (Dataset 1)
```python
# Load action sequences dataset
df = pd.read_csv('commentator_training_data.csv')

# Get a goal sequence
goal_seq = df[df['sequence_type'] == 'shot_sequence']
goal_seq = goal_seq[goal_seq['sequence_id'] == 15]  # Example sequence

# Build commentary from sequence
events = []
for _, event in goal_seq.iterrows():
    player = eval(event['player'])['name'].split()[-1]
    event_type = eval(event['type'])['name']
    minute = event['minute']
    
    if event['is_key_event']:
        events.append(f"**{player} {event_type.upper()}! In the {minute}th minute!**")
    else:
        events.append(f"{player} {event_type.lower()}")

commentary = " → ".join(events)
```

---

## 🎯 **Next Steps for NLP Development**

### Phase 1: Data Preparation ✅
- [x] Extract action sequences (Dataset 1)
- [x] Extract starting events with stats (Dataset 2)
- [x] Include team form and context

### Phase 2: Feature Engineering (Current)
- [ ] Parse all JSON fields (type, player, team, location)
- [ ] Convert coordinates to natural language
- [ ] Create commentary templates
- [ ] Integrate momentum predictions

### Phase 3: Model Training (Planned)
- [ ] Build baseline rule-based system
- [ ] Train sequence-to-sequence model
- [ ] Fine-tune on football commentary style
- [ ] Evaluate with BLEU/ROUGE scores

### Phase 4: Integration (Planned)
- [ ] Combine pre-match + action commentary
- [ ] Add real-time momentum context
- [ ] Create commentary API
- [ ] Test with live data simulation

---

## 📁 **Files Summary**

```
NLP - Commentator/
├── README.md                                    # Main documentation
└── research/
    ├── commentator_training_data.csv            # Dataset 1: Action sequences (144 events)
    ├── starting_events_with_team_stats.csv      # Dataset 2: Starting events (40 events)
    ├── data_extraction_summary.md               # Dataset 1 summary
    ├── starting_events_summary.md               # Dataset 2 summary
    ├── DATASET_DESCRIPTION.md                   # This file
    ├── extract_commentator_data_simple.py       # Script for Dataset 1
    └── extract_starting_events_with_stats.py    # Script for Dataset 2
```

---

**Created**: October 2024  
**Status**: Phase 1 Complete ✅ | Ready for NLP Model Development  
**Total Data**: 184 events across 13 matches with comprehensive context
