# Commentary Style Specification

## 🎯 Commentator Definition

> **A professional football commentator who describes events in a clear, factual, and neutral manner, while transferring the tension and excitement from the field to the commentary according to the event, minute, and result of the game.**

---

## 📊 Input/Output Specification

### **LLM Input**
| Component | Description |
|-----------|-------------|
| **Minute Events** | All raw event data from that 1-minute window |
| **Rule-Based Commentary** | The generated commentary from Phase 7 |
| **Sequence Commentary** | The sequence-level commentary grouping events |
| **Match Context** | Teams, score, stage, minute |

### **LLM Output**
| Component | Description |
|-----------|-------------|
| **Commentary** | Single unified commentary for that minute (1-3 sentences) |

---

## 🎨 Style Characteristics

### **1. Clear**
- Easy to understand
- No ambiguous language
- Direct description of events

### **2. Factual**
- Accurate player names
- Correct event description
- Real-time score reference

### **3. Neutral**
- No team bias
- Objective observation
- Professional tone

### **4. Tension/Excitement Transfer**
Dynamic based on:

| Factor | Low | Medium | High | Very High |
|--------|-----|--------|------|-----------|
| **Event Type** | Pass, Carry | Yellow Card, Corner | Shot, Save | Goal, Penalty, Red Card |
| **Minute** | 0-30' | 31-75' | 76-85' | 86-90+' |
| **Score Diff** | 2+ goals | 1 goal | Draw | Draw in knockout |

---

## 📝 Few-Shot Examples (ESPN Style)

### **Example 1: Goal (Very High Excitement)**
```
Minute: 86'
Score: Spain 0-0 England (Final)
Events: Pass Cucurella → Shot Oyarzabal (Goal)

Commentary:
"Oyarzabal! Spain have the lead! A crucial goal in the 86th minute 
as Cucurella's pass finds the substitute, who finishes calmly with 
his left foot. Spain lead 1-0 with just minutes remaining in the final."
```

**Why it works**:
- ✅ Clear description (who, what, how)
- ✅ Factual (minute, score, body part)
- ✅ High excitement (late goal in final)
- ✅ Context (substitute, time remaining)

---

### **Example 2: Shot Saved (Medium-High Excitement)**
```
Minute: 23'
Score: France 1-0 Poland
Events: Carry Mbappé → Shot Mbappé (Saved) → Save Szczęsny

Commentary:
"Mbappé tests Szczęsny from close range but the Polish goalkeeper 
is equal to it. France continuing to press for a second goal here."
```

**Why it works**:
- ✅ Clear (shot, save)
- ✅ Factual (close range, goalkeeper name)
- ✅ Neutral (credit to both players)
- ✅ Medium excitement (early game, already leading)

---

### **Example 3: Yellow Card (Low-Medium Excitement)**
```
Minute: 67'
Score: Germany 2-1 Denmark
Events: Foul Andersen → Yellow Card Andersen

Commentary:
"Andersen goes into the book for that foul on Musiala. Denmark will 
need to be careful now - they can't afford to go down to ten men 
with the score at 2-1."
```

**Why it works**:
- ✅ Clear (card, reason)
- ✅ Factual (player names)
- ✅ Context (tactical implication, score)
- ✅ Appropriate tension (not over-hyped)

---

### **Example 4: Substitution (Low Excitement)**
```
Minute: 72'
Score: Spain 1-1 Germany
Events: Substitution: Yamal off, Oyarzabal on

Commentary:
"Spain make a change. Oyarzabal comes on for Yamal as Luis de la Fuente 
looks to find a winner in this quarter-final."
```

**Why it works**:
- ✅ Brief (substitutions don't need drama)
- ✅ Factual (players, manager)
- ✅ Context (tactical intent, stage)

---

### **Example 5: General Play (Low Excitement)**
```
Minute: 34'
Score: Netherlands 0-0 England
Events: Pass Stones → Carry Rice → Pass Rice

Commentary:
"England patient in possession here. Rice picks it up from Stones 
and looks to set the tempo in midfield. Still goalless approaching half-time."
```

**Why it works**:
- ✅ Brief (routine play)
- ✅ No over-dramatization
- ✅ Context (score, time)

---

### **Example 6: Penalty Drama (Maximum Excitement)**
```
Minute: 90+3'
Score: Portugal 0-0 Slovenia
Events: Foul → Penalty → Shot Ronaldo (Saved) → Save Oblak

Commentary:
"Ronaldo from the spot... SAVED! Oblak denies him! Incredible drama 
in Ljubljana. Portugal had the chance to win it but Oblak guesses 
correctly. We're heading to extra time."
```

**Why it works**:
- ✅ Maximum drama (late penalty, miss)
- ✅ Captures the moment
- ✅ Context (implications)
- ✅ Natural exclamation

---

## ⚙️ Tension Calculation Logic

```python
def calculate_tension(minute, events, score_diff):
    
    # Base tension from event type
    if events contain ['Goal', 'Penalty', 'Red Card', 'Own Goal']:
        base = "VERY HIGH"
    elif events contain ['Shot', 'Yellow Card', 'Save']:
        base = "HIGH" if minute >= 75 else "MEDIUM"
    else:
        base = "LOW"
    
    # Minute adjustment
    if minute >= 85:
        base = increase_one_level(base)
    
    # Score adjustment
    if score_diff == 0 and minute >= 75:
        base = increase_one_level(base)
    
    return base
```

---

## 📋 Do's and Don'ts

### ✅ DO
- Sound like a real TV commentator
- Match excitement to the moment
- Include relevant context
- Vary language naturally
- Connect events to match narrative
- Keep routine events brief

### ❌ DON'T
- Use timestamps like `[23:00]`
- Repeat exact phrases
- Over-dramatize routine events
- Be robotic or list-like
- Show team bias
- Ignore match context

---

## 📊 Event Type Guidelines

| Event Type | Excitement | Length | Focus |
|------------|------------|--------|-------|
| **Goal** | VERY HIGH | 2-3 sentences | Scorer, assist, importance |
| **Own Goal** | VERY HIGH | 2-3 sentences | Unfortunate nature |
| **Penalty** | VERY HIGH | 2-3 sentences | Taker, outcome, drama |
| **Red Card** | VERY HIGH | 2 sentences | Player, implications |
| **Shot (Goal)** | VERY HIGH | 2-3 sentences | Quality of finish |
| **Shot (Saved)** | MEDIUM-HIGH | 1-2 sentences | Attempt and save |
| **Shot (Missed)** | MEDIUM | 1-2 sentences | Near miss or poor |
| **Yellow Card** | LOW-MEDIUM | 1-2 sentences | Player, warning |
| **Save** | MEDIUM-HIGH | 1-2 sentences | Goalkeeper credit |
| **Substitution** | LOW | 1 sentence | Tactical change |
| **Corner** | LOW-MEDIUM | 1 sentence | Set piece opportunity |
| **Free Kick** | LOW-MEDIUM | 1-2 sentences | Location, danger |
| **Pass/Carry** | LOW | Brief or skip | Only if significant |

---

## 🎯 Quality Metrics

### **Accuracy** (Must pass)
- [ ] Player names correct?
- [ ] Event description accurate?
- [ ] Score reference correct?

### **Style** (Should achieve)
- [ ] Sounds like real commentary?
- [ ] Excitement matches event?
- [ ] Natural language flow?
- [ ] Appropriate length?

### **Context** (Nice to have)
- [ ] Mentions tactical implications?
- [ ] References match situation?
- [ ] Connects to narrative?

---

## 🔄 Prompt Flow

```
┌─────────────────────────────────────┐
│           SYSTEM PROMPT             │
│  (Style definition, guidelines)     │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│         FEW-SHOT EXAMPLES           │
│   (6 ESPN-style examples)           │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│          USER PROMPT                │
│  - Minute + Score + Stage           │
│  - Events this minute               │
│  - Rule-based commentary            │
│  - Sequence commentary              │
│  - Tension level                    │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│        GPT RESPONSE                 │
│   (1-3 sentence commentary)         │
└─────────────────────────────────────┘
```

---

## 📈 Expected Output Quality

### **Goal Commentary Example**

**Input**:
```
Minute: 86'
Score: Spain 0-0 England (Final)
Events: [Pass Cucurella, Shot Oyarzabal (Goal)]
Rule-based: "[86:00] Cucurella to Oyarzabal. GOAL!"
Sequence: "Cucurella finds Oyarzabal who scores"
```

**Expected Output**:
```
"Oyarzabal! Spain have broken the deadlock with just four minutes 
remaining! Cucurella's ball across finds the substitute perfectly, 
and he makes no mistake. Spain lead 1-0 in the Euro 2024 final!"
```

**Quality Check**:
- ✅ Excitement matches late final goal
- ✅ Clear description of build-up
- ✅ Context (substitute, time, importance)
- ✅ Natural language flow
- ✅ Professional but excited tone

---

*Style Specification v1.0*  
*Phase 10: LLM Commentary Generation*  
*Created: November 24, 2025*

