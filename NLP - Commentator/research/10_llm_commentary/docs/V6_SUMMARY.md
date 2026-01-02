# GPT Commentator V6 - Summary

## Overview

V6 is an enhanced version with focus on:
1. **More Variety** - Different phrasings, varied sentence structure
2. **Event Chains** - Detects Corner→Shot, Dribble→Shot, etc.
3. **Clear Momentum Language** - Distinct "momentum" vs "momentum change"
4. **Lower Agent Threshold** - More momentum insights (0.70 vs 0.75)

---

## Parameters

| Parameter | V5 | V6 | Reason |
|-----------|----|----|--------|
| `TEMPERATURE` | 0.7 | **0.75** | More variety |
| `MAX_TOKENS` | 40 | **45** | Slightly longer |
| `Agent Threshold` | 0.75 | **0.70** | More insights |

---

## New Feature: Event Chains (Direct Detection)

### What It Does

Detects **DIRECT chains** by looking back **7 events** and checking for `play_pattern` changes:

| Chain Type | Detection Logic | LLM Instruction |
|------------|-----------------|-----------------|
| **From Corner** | `play_pattern` changed to 'From Corner' in last 7 events | "from the corner", "header from the delivery" |
| **From Free Kick** | `play_pattern` changed to 'From Free Kick' in last 7 events | "from the free kick", "following the set piece" |
| **After Dribble** | Same player: Carry event in last 7 events | "beats his man", "dribbles past" |
| **After Blocked** | Shot (Blocked/Saved) outcome in last 7 events before Corner | "second chance", "follows up" |

### Direct vs Indirect Chain Logic

The `play_pattern` column shows how an action started (first move). To detect **direct** chains:

1. Look back **7 events** before the main event
2. Check if `play_pattern` **changed** (e.g., from 'Regular Play' to 'From Corner')
3. If event -8 has the same pattern → NOT a direct chain (action started earlier)

```
Example: Event -8 = "Regular Play", Event -7 to -1 = "From Corner"
         → Corner started in our 7-event window → DIRECT chain ✓
```

### Example Output

**Before V6 (Hallucination):**
```
Le Normand's shot goes off target. Spain has been lively with five corners.
                                                            ↑ INVENTED!
```

**After V6 (Correct):**
```
Le Normand heads over from the corner delivery.
                        ↑ Uses chain origin ✓
```

### Hallucination Prevention

The prompt explicitly forbids inventing statistics:

```
CHAIN:
- (DIRECT chain - action started within last 7 events)
- Origin: From Corner
- → USE: 'from the corner', 'header from the delivery'
- ⛔ ONLY describe THIS event - NO match totals ('X corners so far' is FORBIDDEN)
```

### Note on Assists

Assist detection is handled separately by `extract_event_specific_data()` with its own 7-event lookback, not by the chain function.

---

## Momentum Language

### Clear Distinction

| Concept | Description | Phrasing |
|---------|-------------|----------|
| **MOMENTUM** | Current state (who has it) | "in control", "dominating", "on top" |
| **MOMENTUM CHANGE** | Shift/trend (who is gaining) | "gaining momentum", "building pressure" |

### Prompt Labels

- `📊 MOMENTUM STATE` → "USE: 'in control', 'dominating'"
- `⚡ MOMENTUM CHANGE` → "USE: 'gaining momentum', 'momentum shifting'"

---

## Variety Instructions

Added to system prompt:
```
- VARY your sentence structure - don't repeat same patterns
- Use different phrasings for similar events
- DON'T mention possession every time - VARY what you highlight
```

---

## Test Results (5 Matches)

| Match | Chains Detected | Hallucinations |
|-------|-----------------|----------------|
| England vs Switzerland | 12 | 0 ✓ |
| Spain vs England | 8 | 0 ✓ |
| Netherlands vs Turkey | 12 | 0 ✓ |
| Portugal vs France | 17 | 0 ✓ |
| Germany vs Denmark | 12 | 1 (fixed) |

**Total: 1 hallucination in 5 matches** - Fixed with strengthened system prompt.

---

## Sample Commentary

### Chain: From Corner
```
[Shot Missed] Attempt missed. Robin Le Normand heads over from the corner delivery.
```

### Chain: After Dribble
```
[Shot Blocked] Bukayo Saka dribbles past his man but his left-footed shot is denied.
```

### Chain: From Free Kick
```
[Shot Saved] Phil Foden's left-footed shot denied by Unai Simón following the free kick.
```

---

## Files

| File | Description |
|------|-------------|
| `gpt_commentator_v6.py` | V6 commentator class with chain instructions |
| `batch_generate_v6.py` | V6 batch generator with chain detection |
| `run_final_test_v3.py` | Contains `detect_event_chain()` function |

---

## Usage

```bash
cd "NLP - Commentator/research/10_llm_commentary/scripts"

# Run for specific match
python batch_generate_v6.py --home Spain --away England

# With custom API key
python batch_generate_v6.py --home Germany --away Scotland --api-key sk-xxx
```

---

## Version History

| Version | Key Features |
|---------|--------------|
| V3 | Basic event commentary, multi-events |
| V4 | Context-aware (score, time), penalties |
| V5 | Momentum agent integration |
| **V6** | **Variety + Event chains + Momentum clarity + Hallucination prevention + Penalty/Own Goal fix** |

---

## V6.1 Fixes

### Penalty Detection (Period 1-4)
- Ported `check_for_penalty_in_minute()` from V4 to V3
- Now correctly detects: `Penalty Goal`, `Penalty Saved`, `Penalty Missed`
- Checks `shot.type.name == 'Penalty'` in the shot column

### Own Goal Detection
- Added `check_for_own_goal_in_minute()` function
- Detects `event_type == 'Own Goal Against'`
- Returns `Own Goal` type with scorer info

---

## V6.2 Fixes (Latest)

### Direct vs Indirect Chain Distinction
Now distinguishes between direct and indirect chains based on **pass count**:

| Chain Type | Detection | Commentary Guidance |
|------------|-----------|-------------------|
| **Corner (direct)** | ≤1 pass between corner and goal | "from the corner", "heads in from the delivery" |
| **Corner (indirect)** | >1 pass between corner and goal | "The play started from a corner", "Following the corner..." |
| **Free Kick (direct)** | ≤1 pass between FK and goal | "from the free kick", "curls it in from the set piece" |
| **Free Kick (indirect)** | >1 pass between FK and goal | "The play originated from a free kick" |

### Enhanced Hallucination Prevention

**Option 3: Explicit "ONLY" list**
```
ALLOWED to mention (only if provided):
- Player names, team names
- Event outcomes, body part, location
- Possession %, domination minutes, multiple event counts

FORBIDDEN (never mention unless explicitly provided):
- Corner counts, shot totals, attempt sequences
```

**Option 4: Negative Few-Shot Examples**
```
⛔ WRONG EXAMPLES - NEVER DO THIS:
- ❌ "Shot saved! Germany with 4 corners so far."
- ❌ "Spain piling on pressure with 8 shots this half."
- ❌ "Third corner in quick succession for England."

✅ CORRECT EXAMPLES - DO THIS:
- ✅ "Shot saved! Havertz denied by Schmeichel from close range."
```

### Own Goal Score Fix
- Fixed `build_running_score()` to only count `Own Goal Against` once
- Previously double-counted due to both `For` and `Against` events

### Own Goal Player Detection Fix (V6.2.1)
- **Issue:** `check_for_own_goal_in_minute()` used `.iloc[0]` which picked `Own Goal For` (no player) instead of `Own Goal Against` (has player name)
- **Result:** Commentary said "Scotland defender gives Germany goal" when it should be "Germany defender gives Scotland goal"
- **Fix:** Changed detection to specifically match `event_type == 'Own Goal Against'`

| Before Fix | After Fix |
|------------|-----------|
| "a Scotland defender gives Germany another goal" ❌ | "off Antonio Rüdiger gives Scotland a goal" ✓ |

### Most Active Player Team Fix
- **Issue:** "Most active" player could be from the non-dominant team, confusing LLM
- **Fix:** Added team name to player data: `"Most active: Xavi Simons (Netherlands) (5 events)"`

### Area Perspective Fix
- **Issue:** "defensive third" was generic, not team-specific
- **Fix:** Now uses `"{home_team}'s defensive third"` for clarity

### Possession Control Threshold
- Changed from 55% to **60%** for "team in control" designation

---

## Final Test Results (10 Matches)

| Match | Own Goals | Penalties | Hallucinations | Status |
|-------|-----------|-----------|----------------|--------|
| Germany vs Scotland | 1 ✓ | 1 ✓ | 0 | ✓ |
| Netherlands vs Turkey | 1 ✓ | 0 | 0 | ✓ |
| England vs Switzerland | 0 | 0 | 0 | ✓ |
| Spain vs England | 0 | 0 | 0 | ✓ |
| Portugal vs France | 0 | 0 | 0 | ✓ |

---

Euro 2024 Momentum Project  
December 2024

