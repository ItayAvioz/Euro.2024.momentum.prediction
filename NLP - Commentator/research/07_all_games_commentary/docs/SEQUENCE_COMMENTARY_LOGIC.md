# Sequence Commentary Logic - OLD vs NEW

**Date**: November 2, 2025  
**Status**: ✅ Implemented across all scripts

---

## 📚 What is a Sequence?

A **sequence** = Group of consecutive events forming one "play" or "possession chain"

**Sequences END when:**
- Possession changes (different team gets ball)
- Key event occurs (Goal, Shot, Foul, Substitution)
- Too long (reaches 10 events)

---

## ❌ OLD LOGIC - The Problem

### Rule:
```python
for i, idx in enumerate(event_indices[:5]):  # First 5 events only!
    # Add to commentary
```
**Take the first 5 events from sequence**

### Problems:

**Problem 1: Goals Get Cut Off**
- If goal is event #6, #7, #8, #9, or #10 → **MISSING from commentary!**

**Problem 2: Too Many "Receives"**
- Every "Ball Receipt*" event included → Repetitive and unnatural

---

## ✅ NEW LOGIC - The Solution

### Rules:
```python
# 1. Prioritize GOALS - always include them
# 2. Skip "Ball Receipt*" unless significant (under pressure in danger zone)
# 3. Take first 4 regular events + ALL goals

if key_event_indices:
    selected = regular_event_indices[:4] + key_event_indices
else:
    selected = regular_event_indices[:5]
```

**Decision Tree:**
```
For each event:
├─ GOAL/Own Goal? → ✅ ALWAYS include (no matter position!)
├─ Ball Receipt*?
│  ├─ Under pressure in danger zone? → ✅ Include (significant)
│  └─ Normal receive? → ❌ Skip (implied from pass)
└─ Other (Pass/Carry/Dribble/etc.) → ✅ Include
```

---

## 🔍 REAL EXAMPLES - Before & After

### **Example 1: Spain Winning Goal (Final)**

**Match**: Spain 2-1 England (Euro 2024 Final)  
**Sequence 363**: 10 events, goal is event #9

**Events in Sequence:**
```
1. [85:52] Olmo passes to Oyarzabal
2. [85:53] Oyarzabal receives
3. [85:53] Oyarzabal passes to Cucurella
4. [85:55] Walker pressures Oyarzabal
5. [85:55] Cucurella receives
6. [85:55] Cucurella carries
7. [85:55] Cucurella passes to Oyarzabal
8. [85:56] Oyarzabal receives
9. [85:56] ⚽ OYARZABAL SCORES! 2-1    ← Event #9!
10. [85:57] Goalkeeper
```

#### ❌ OLD Commentary (Problem):
```
"[85:52] Olmo passes to Oyarzabal. Oyarzabal receives, passes to Cucurella. 
Walker pressures. Cucurella receives."
```
**Issues:**
- 🚨 **GOAL IS MISSING!** (only took first 5 events)
- Too many "receives" (cluttered)

#### ✅ NEW Commentary (Fixed):
```
"[85:52] Olmo passes to Oyarzabal passes to Cucurella. Walker pressures. 
Cucurella carries, passes to Oyarzabal. ⚽ GOOOAL! Oyarzabal scores! 
Spain now lead 2-1! His first goal of the tournament late in the game!"
```
**Improvements:**
- ✅ **GOAL INCLUDED** (even though it's event #9!)
- ✅ Skipped unnecessary "receives"
- ✅ Flows naturally like real commentary

---

### **Example 2: Germany First Goal**

**Match**: Germany 5-1 Scotland (Opening Match)  
**Sequence 52**: 5 events, goal is event #5

**Events in Sequence:**
```
1. [9:51] Kimmich receives (under pressure in attacking third)
2. [9:51] Kimmich carries
3. [9:54] Kimmich passes to Wirtz (dangerous pass)
4. [9:55] Wirtz receives (under pressure in danger zone)
5. [9:55] ⚽ WIRTZ SCORES! 1-0
```

#### ❌ OLD Commentary:
```
"[9:51] Kimmich receives under pressure. Kimmich carries. 
Kimmich passes to Wirtz. Wirtz receives. Wirtz shoots."
```
**Issues:**
- Goal included (within first 5) but cut off
- All receives included (repetitive)

#### ✅ NEW Commentary:
```
"[9:51] Kimmich under pressure, carries the ball, plays dangerous pass to Wirtz. 
Wirtz receives under pressure in attacking third. ⚽ GOOOAL! Wirtz scores! 
Germany lead 1-0! His first goal of the tournament!"
```
**Improvements:**
- ✅ Goal included with full excitement
- ✅ Only significant receive kept (under pressure in danger zone)
- ✅ Flows like real sports commentary

---

### **Example 3: Own Goal**

**Match**: Germany 5-1 Scotland  
**Sequence 384**: 1 event (own goal)

**Events in Sequence:**
```
1. [86:32] ⚽ Rüdiger Own Goal (Germany) → Scotland scores
```

#### ❌ OLD Commentary:
```
"Own Goal Against - Antonio Rüdiger"
```
**Issues:**
- Generic text, no excitement
- No score context

#### ✅ NEW Commentary:
```
"[86:32] 💥 OWN GOAL! Antonio Rüdiger puts the ball into his own net! 
Cruel for Germany, but Scotland won't mind! Germany now lead 4-1!"
```
**Improvements:**
- ✅ Full own goal template with drama
- ✅ Score update included
- ✅ Context for both teams

---

### **Example 4: Musiala Solo Goal**

**Match**: Germany 5-1 Scotland  
**Sequence 99**: 5 events, dribble sequence

**Events in Sequence:**
```
1. [18:42] Musiala carries (loses it)
2. [18:42] McGregor beaten (dribbled past)
3. [18:42] Musiala dribbles
4. [18:42] Musiala carries
5. [18:43] ⚽ MUSIALA SCORES! 2-0
```

#### ❌ OLD Commentary:
```
"Musiala carries. McGregor beaten. Musiala dribbles. Musiala carries. 
Musiala shoots."
```
**Issues:**
- Repetitive player names
- No excitement

#### ✅ NEW Commentary:
```
"[18:42] Musiala under pressure, carries the ball - BUT LOSES IT! 
McGregor is beaten by Musiala! Musiala takes on the defender, carries. 
⚽ GOOOAL! Musiala scores! Germany lead 2-0! His first goal of the tournament! 
A crucial two-goal lead!"
```
**Improvements:**
- ✅ Full narrative with drama
- ✅ Goal commentary complete
- ✅ Context (first goal, two-goal lead)

---

## 📊 Summary Table

| Aspect | OLD Logic | NEW Logic |
|--------|-----------|-----------|
| **Goal at event #3** | ✅ Included | ✅ Included |
| **Goal at event #9** | ❌ **MISSING** | ✅ **Included** |
| **Multiple goals** | ❌ Might miss | ✅ ALL included |
| **Ball Receipt (normal)** | ❌ Always included | ✅ Skipped (implied) |
| **Ball Receipt (danger)** | ✅ Included | ✅ Included (significant) |
| **Commentary flow** | ❌ Repetitive | ✅ Natural, like real commentary |
| **No goals in sequence** | First 5 events | First 5 events (same) |

---

## 🎯 Key Improvements

### 1. **Goals Always Included**
- **Before**: Goals beyond event #5 were cut off
- **After**: ALL goals included, no matter position (event #9, #10, etc.)

### 2. **Natural Flow**
- **Before**: "Player A passes. Player B receives, passes. Player C receives."
- **After**: "Player A passes to Player B passes to Player C. GOAL!"

### 3. **Smart Filtering**
- Skip: Normal receives (implied from pass)
- Keep: Receives under pressure in danger zones (significant)
- Always: Goals, own goals (critical events)

---

## 🎙️ Matches Real Commentary Style

**Real commentators:**
- ✅ "Messi to Suarez to Neymar... GOAL!"
- ✅ "Receives under pressure in the box, shoots!"

**Real commentators DON'T say:**
- ❌ "Messi passes. Suarez receives. Suarez passes. Neymar receives."

**Our NEW logic mimics real sports broadcasting!** 🎯⚽

---

## 📁 Files Updated

All three commentary generation scripts now use the NEW logic:

1. ✅ `07_all_games_commentary/scripts/generate_match_commentary.py`
2. ✅ `04_final_game_production/scripts/generate_rich_commentary.py`
3. ✅ `06_semi_finals_commentary/scripts/generate_semi_final_commentary.py`

---

## ✅ Verified With

- **Germany vs Scotland** (5-1) - All 6 goals in sequence commentary
- **Spain vs England** (2-1) - Winning goal now included (was event #9)
- **Semi-finals** - All goals properly included

**Status**: Ready for all 51 Euro 2024 matches! 🚀

