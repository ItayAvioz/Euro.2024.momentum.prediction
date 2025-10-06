# Starting Game Commentary - Template & Examples Guide

## Overview

This guide demonstrates how to convert structured starting game data into natural language commentary. It covers 3 diverse match scenarios showing the complete pipeline from raw data to generated commentary.

---

## Example 1: Opening Match (No Previous Form)

### Match: Germany 5-1 Scotland

#### 1. METADATA
```
Match ID:      3930158
Date:          2024-06-14
Stage:         Group Stage (Opening Match)
Kick-off:      22:00:00
Stadium:       Allianz Arena
Referee:       Clément Turpin
Final Score:   Germany 5-1 Scotland
```

#### 2. EXTRACTED DATA

**GERMANY (Team A)**
- Matches Played: 0
- Status: Tournament opener
- Note: No previous form data available

**SCOTLAND (Team B)**
- Matches Played: 0
- Status: Tournament opener
- Note: No previous form data available

**Starting Lineups:**
- Germany: Manuel Neuer, Antonio Rüdiger, David Raum, Jonathan Tah, Pascal Groß...
- Scotland: Angus Gunn, Anthony Ralston, Andrew Robertson, Scott McTominay...

#### 3. TEMPLATE (Opening Match - No Form)

```
[OPENING]
"Welcome to {stadium} for this {stage} clash between {team_a} and {team_b}. 
{referee} will be taking charge of today's match."

[TEAM A - DEBUT]
"{team_a} are making their tournament debut in front of their home fans tonight."

[TEAM B - DEBUT]
"{team_b} are also starting their Euro 2024 journey this evening."

[LINEUPS]
"For {team_a}, we have {key_players_a} in the starting lineup. 
And {team_b} field {key_players_b} among others."

[KICK-OFF]
"We're all set for kick-off here at {stadium}. 
This {stage} encounter promises to be fascinating!"
```

#### 4. GENERATED COMMENTARY

> Welcome to Allianz Arena for this Group Stage clash between Germany and Scotland. Clément Turpin will be taking charge of today's match.
>
> Germany are making their tournament debut in front of their home fans tonight.
>
> Scotland are also starting their Euro 2024 journey this evening.
>
> For Germany, we have Manuel Neuer, Antonio Rüdiger, David Raum in the starting lineup. And Scotland field Angus Gunn, Anthony Ralston, Andrew Robertson among others.
>
> We're all set for kick-off here at Allianz Arena. This Group Stage encounter promises to be fascinating!

---

## Example 2: Mid-Tournament (Some Form Data)

### Match: Denmark 1-1 England

#### 1. METADATA
```
Match ID:      3930171
Date:          2024-06-20
Stage:         Group Stage (Matchday 2)
Kick-off:      19:00:00
Stadium:       Deutsche Bank Park
Referee:       Artur Manuel Ribeiro Soares Dias
Final Score:   Denmark 1-1 England
```

#### 2. EXTRACTED DATA

**DENMARK (Team A)**
- Tournament Record: 0W - 1D - 0L
- Goals: 1 scored, 1 conceded (GD: +0)
- Last Result: Draw (1-1 vs Slovenia)
- Form: Unbeaten

**ENGLAND (Team B)**
- Tournament Record: 1W - 0D - 0L
- Goals: 1 scored, 0 conceded (GD: +1)
- Last Result: Win (1-0 vs Serbia)
- Form: Perfect start

**Starting Lineups:**
- Denmark: Kasper Schmeichel, Joachim Andersen, Jannik Vestergaard...
- England: Jordan Pickford, Kyle Walker, Declan Rice, John Stones...

#### 3. TEMPLATE (Mid-Tournament - With Form)

```
[OPENING]
"Welcome to {stadium} for this {stage} clash between {team_a} and {team_b}. 
{referee} will be taking charge of today's match."

[TEAM A - FORM]
"{team_a} come into this match having recorded {W} wins, {D} draws, and {L} losses 
in the tournament so far. They've scored {GS} goal(s) while conceding {GC}. 
Their previous match ended in a {last_score} {last_result} against {last_opponent}."

[TEAM B - FORM]
"{team_b} have managed {W} wins, {D} draws, and {L} losses so far in Euro 2024. 
With {GS} goal(s) scored and {GC} conceded, they come in confident after 
{last_result_detail}."

[LINEUPS]
"For {team_a}, we have {key_players_a} in the starting lineup. 
And {team_b} field {key_players_b} among others."

[KICK-OFF]
"We're all set for kick-off here at {stadium}. 
This {stage} encounter promises to be fascinating!"
```

#### 4. GENERATED COMMENTARY

> Welcome to Deutsche Bank Park for this Group Stage clash between Denmark and England. Artur Manuel Ribeiro Soares Dias will be taking charge of today's match.
>
> Denmark come into this match having recorded 0 wins, 1 draw, and 0 losses in the tournament so far. They've scored 1 goal while conceding 1. Their previous match ended in a 1-1 draw against Slovenia.
>
> England have managed 1 win, 0 draws, and 0 losses so far in Euro 2024. With 1 goal scored and 0 conceded, they come in confident after beating Serbia 1-0.
>
> For Denmark, we have Kasper Schmeichel, Joachim Andersen, Jannik Vestergaard in the starting lineup. And England field Jordan Pickford, Kyle Walker, Declan Rice among others.
>
> We're all set for kick-off here at Deutsche Bank Park. This Group Stage encounter promises to be fascinating!

---

## Example 3: Final (Full Tournament History)

### Match: Spain 2-1 England

#### 1. METADATA
```
Match ID:      3943043
Date:          2024-07-14
Stage:         Final
Kick-off:      22:00:00
Stadium:       Olympiastadion Berlin
Referee:       François Letexier
Final Score:   Spain 2-1 England
```

#### 2. EXTRACTED DATA

**SPAIN (Team A)**
- Tournament Record: 6W - 0D - 0L (Perfect record!)
- Goals: 13 scored, 3 conceded (GD: +10)
- Last Result: Win (3-0 vs Croatia)
- Form: Dominant throughout tournament

**ENGLAND (Team B)**
- Tournament Record: 3W - 3D - 0L (Unbeaten)
- Goals: 7 scored, 4 conceded (GD: +3)
- Last Result: Win (1-0 vs Serbia)
- Form: Grinding results

**Starting Lineups:**
- Spain: David Raya Martin, Daniel Carvajal Ramos, Robin Aime Robert Le Normand...
- England: Jordan Pickford, Kyle Walker, Luke Shaw, Declan Rice, John Stones...

#### 3. TEMPLATE (Final - High Stakes)

```
[OPENING - ELEVATED]
"Welcome to {stadium} for this {stage} clash between {team_a} and {team_b}. 
{referee} will be taking charge of today's match."

[TEAM A - COMPLETE NARRATIVE]
"{team_a} come into this match having recorded {W} wins, {D} draws, and {L} losses 
in the tournament so far. They've scored {GS} goals while conceding {GC}. 
Last time out, they secured a {last_score} victory over {last_opponent}."

[TEAM B - COMPLETE NARRATIVE]
"{team_b} have managed {W} wins, {D} draws, and {L} losses so far in Euro 2024. 
With {GS} goals scored and {GC} conceded, they come in confident after 
beating {last_opponent} {last_score}."

[LINEUPS - KEY PLAYERS]
"For {team_a}, we have {key_players_a} in the starting lineup. 
And {team_b} field {key_players_b} among others."

[KICK-OFF - HIGH DRAMA]
"We're all set for kick-off here at {stadium}. 
This {stage} encounter promises to be fascinating!"
```

#### 4. GENERATED COMMENTARY

> Welcome to Olympiastadion Berlin for this Final clash between Spain and England. François Letexier will be taking charge of today's match.
>
> Spain come into this match having recorded 6 wins, 0 draws, and 0 losses in the tournament so far. They've scored 13 goals while conceding 3. Last time out, they secured a 3-0 victory over Croatia.
>
> England have managed 3 wins, 3 draws, and 0 losses so far in Euro 2024. With 7 goals scored and 4 conceded, they come in confident after beating Serbia 1-0.
>
> For Spain, we have David Raya Martin, Daniel Carvajal Ramos, Robin Aime Robert Le Normand in the starting lineup. And England field Jordan Pickford, Kyle Walker, Luke Shaw among others.
>
> We're all set for kick-off here at Olympiastadion Berlin. This Final encounter promises to be fascinating!

---

## Commentary Generation Framework

### 1. Data Fields Required

| Category | Field | Usage |
|----------|-------|-------|
| **Match Context** | stadium, stage, referee | Opening scene-setting |
| **Team Names** | team_a, team_b | Throughout commentary |
| **Team Stats** | wins, draws, losses | Form narrative |
| **Goals** | goals_scored, goals_conceded | Attacking/defensive profile |
| **Recent Form** | last_result, last_score, last_opponent | Momentum narrative |
| **Lineups** | team_a_lineup, team_b_lineup | Player introduction |

### 2. Conditional Logic Rules

```python
IF team_stats['matches_played'] == 0:
    USE debut_template()
    FOCUS ON: Anticipation, first appearance
    
ELIF team_stats['matches_played'] <= 2:
    USE early_tournament_template()
    FOCUS ON: Recent form, opening results
    
ELIF stage == 'Final':
    USE final_template()
    FOCUS ON: Complete tournament narrative, high stakes
    
ELSE:
    USE standard_template()
    FOCUS ON: Balanced form and context
```

### 3. Natural Language Techniques

#### Variation in Phrasing
- "come into this match" vs "arrive at this stage"
- "having recorded" vs "with" vs "boasting"
- "last time out" vs "their previous match" vs "in their last outing"

#### Result Descriptions
- **Win**: "secured a victory", "beat", "came through with a win"
- **Draw**: "drew", "shared the points", "played out a draw"
- **Loss**: "fell to", "were defeated by", "suffered a loss"

#### Tone Adaptation
- **Opening Match**: Excitement, fresh start, anticipation
- **Group Stage**: Form analysis, momentum building
- **Knockout**: Stakes raised, pressure mentioned
- **Final**: Epic narrative, complete story, high drama

### 4. Template Structure Components

```
[OPENING] (1-2 sentences)
├─ Welcome + Stadium
├─ Stage importance
├─ Teams introduced
└─ Referee mentioned

[TEAM A NARRATIVE] (2-3 sentences)
├─ Tournament record OR debut status
├─ Goal statistics (if applicable)
└─ Last match context

[TEAM B NARRATIVE] (2-3 sentences)
├─ Tournament record OR debut status
├─ Goal statistics (if applicable)
└─ Last match context

[LINEUPS] (1-2 sentences)
├─ Team A key players
└─ Team B key players

[KICK-OFF] (1 sentence)
└─ Anticipation + excitement
```

### 5. Key Variables for Template

```python
commentary_variables = {
    # Context
    'stadium': str,
    'stage': str,
    'referee': str,
    'team_a': str,
    'team_b': str,
    
    # Stats (Team A)
    'team_a_wins': int,
    'team_a_draws': int,
    'team_a_losses': int,
    'team_a_goals_scored': int,
    'team_a_goals_conceded': int,
    'team_a_last_result': str,  # 'Win', 'Draw', 'Loss'
    'team_a_last_score': str,   # e.g., '2-1'
    'team_a_last_opponent': str,
    
    # Stats (Team B) - same structure
    'team_b_wins': int,
    'team_b_draws': int,
    # ... etc
    
    # Lineups
    'team_a_key_players': list,
    'team_b_key_players': list,
}
```

---

## Summary: From Data to Commentary

### Pipeline Steps

1. **EXTRACT** → Load match data from CSV
2. **CLASSIFY** → Determine match type (debut/mid-tournament/final)
3. **SELECT TEMPLATE** → Choose appropriate commentary structure
4. **POPULATE** → Fill template with data
5. **GENERATE** → Apply natural language variations
6. **OUTPUT** → Natural commentary text

### Best Practices

✅ **DO:**
- Check for null/zero values (debut matches)
- Vary sentence structure and phrasing
- Adapt tone to match importance
- Use transitional phrases between sections
- Include specific statistics naturally

❌ **DON'T:**
- Use robotic, repetitive phrasing
- Ignore the stage/context of the match
- Overload with statistics (balance narrative)
- Use generic templates without context
- Forget to adapt for debuts vs experienced teams

---

## Next Steps for NLP Model

1. **Training Data**: Use these templates to generate diverse examples
2. **Feature Engineering**: Extract key variables from structured data
3. **Template Learning**: Model learns to select appropriate template based on context
4. **Natural Variation**: Train on varied phrasings of same information
5. **Evaluation**: Compare generated commentary with human-written versions

---

**Document Version:** 1.0  
**Created:** 2024  
**Purpose:** NLP Commentator Training - Starting Game Module
