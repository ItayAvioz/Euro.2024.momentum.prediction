# Event Type Keyword Presence Analysis

## 📝 Overview

This analysis checks whether the **event type keyword** itself appears in the commentary text for both real and generated commentaries.

## 🎯 What It Does

For each event type (Goal, Shot, Pass, etc.), it checks if the keyword appears in:

1. **Real commentary only** - Real uses the keyword, but we don't
2. **Generated commentary only** - We use the keyword, but real doesn't  
3. **Both commentaries** ✅ - BEST CASE: Both use the same keyword
4. **Neither commentary** - Neither mentions the keyword

## 🔍 Example

For a **Goal** event:
- **Keywords checked**: "goal", "goals", "scores", "scored"
- **Real commentary**: "AMAZING! Williams **scores** for Spain! 1-0!"
- **Generated commentary**: "Williams **SCORES**! Spain takes the lead 1-0 ⚽"
- **Result**: ✅ **In Both** (both commentaries mention the keyword)

## 📊 Event Type Keywords Mapping

```python
event_keywords = {
    'Pass': ['pass', 'passes', 'passed'],
    'Shot': ['shot', 'shots', 'shoots'],
    'Goal': ['goal', 'goals', 'scores', 'scored'],
    'Dribble': ['dribble', 'dribbles', 'dribbled'],
    'Pressure': ['pressure', 'pressures', 'pressed', 'pressing'],
    'Carry': ['carry', 'carries', 'carried', 'carrying'],
    'Clearance': ['clearance', 'cleared', 'clears'],
    'Interception': ['interception', 'intercepts', 'intercepted'],
    'Tackle': ['tackle', 'tackles', 'tackled'],
    'Block': ['block', 'blocks', 'blocked'],
    'Foul Committed': ['foul', 'fouls', 'fouled'],
    'Yellow Card': ['yellow', 'booked', 'card'],
    'Red Card': ['red', 'sent off', 'dismissed'],
    'Substitution': ['substitution', 'sub', 'subs', 'replaced', 'replaces'],
    'Offside': ['offside', 'offsides'],
    'Corner': ['corner', 'corners'],
    'Free Kick': ['free kick', 'free-kick'],
    'Throw-in': ['throw', 'throw-in'],
    'Goal Kick': ['goal kick'],
    'Penalty': ['penalty', 'penalties'],
    'Save': ['save', 'saves', 'saved'],
    'Own Goal': ['own goal'],
    'Injury': ['injury', 'injured'],
    'Tactical Shift': ['tactical', 'formation'],
    'Out': ['out']
}
```

## 📈 Dashboard Visualization

### 1. **Stacked Bar Chart**
- Shows the distribution of keyword presence for each event type
- Color-coded:
  - 🟢 **Green** = In Both (BEST)
  - 🔵 **Blue** = In Real Only
  - 🟠 **Orange** = In Generated Only
  - 🔴 **Red** = In Neither

### 2. **Detailed Table**
Shows counts and percentages for each category:
```
Event Type | Total | In Both | In Real Only | In Generated Only | In Neither
-----------|-------|---------|--------------|-------------------|------------
Goal       | 100   | 85 (85%)| 10 (10%)     | 3 (3%)           | 2 (2%)
Pass       | 500   | 420(84%)| 50 (10%)     | 20 (4%)          | 10 (2%)
```

## 💡 Why This Matters

### ✅ **High "In Both" Percentage is Good**
- Means we're using the **same vocabulary** as real commentators
- Shows our commentary is **consistent** with professional standards
- Indicates we're **not missing important keywords**

### ⚠️ **High "In Real Only" Means:**
- We're using **different terminology** for the same event
- Example: Real says "goal" but we say "nets it" or "finds the back of the net"
- May indicate we need to adjust our templates to include the keyword

### 📝 **High "In Generated Only" Means:**
- Real commentators use **varied vocabulary**
- Example: Real says "finds Kane" instead of "passes to Kane"
- This is OKAY - shows real commentary is more creative

### 🚫 **High "In Neither" Means:**
- Both commentaries describe the event **without using the keyword**
- Example: For a Pass event, real says "finds Kane" and we say "delivers to Kane"
- This can be acceptable for some events (like Pass), but concerning for others (like Goal)

## 🎯 Target Goals

### Event Types That SHOULD Have High "In Both":
1. **Goal** - Should be >80% (almost always mentioned)
2. **Yellow Card** - Should be >70% (usually mentioned)
3. **Red Card** - Should be >90% (critical events)
4. **Substitution** - Should be >60% (important tactical changes)
5. **Penalty** - Should be >80% (high-stakes moments)
6. **Own Goal** - Should be >90% (dramatic events)

### Event Types That Can Have Lower "In Both":
1. **Pass** - Can be 40-60% (many alternative phrases: "finds", "delivers", "plays")
2. **Carry** - Can be 30-50% (often described as "drives forward", "advances")
3. **Pressure** - Can be 40-60% (varied descriptions: "closes down", "harasses")
4. **Out** - Can be 20-40% (often just implied or not mentioned)

## 📊 Data Source

The analysis uses the **best matches** from each scoring method:
- **With Sentiment**: Based on `average_score` column
- **Without Sentiment**: Based on `average_score_no_sentiment` column

Each row in the comparison CSV is analyzed for keyword presence in both `real_commentary` and `our_sequence_commentary` columns.

## 🔄 How to Use

1. **Select Scoring Method** (With/Without Sentiment) at the top of the dashboard
2. **Scroll to "Event Type Keyword Presence in Commentary"** section
3. **Look at the stacked bar chart** - longer green bars are better
4. **Check the detailed table** for exact percentages
5. **Compare between scoring methods** by switching the radio button

## 🚀 Insights to Look For

### Good Signs:
- ✅ Goal events have >80% "In Both"
- ✅ Critical events (Red Card, Penalty, Own Goal) have >75% "In Both"
- ✅ Most event types have <10% "In Neither"

### Warning Signs:
- ⚠️ Goal events have <60% "In Both" → We're not using "goal" enough
- ⚠️ Any event type has >20% "In Neither" → Both commentaries avoiding the keyword
- ⚠️ Substitution has <40% "In Both" → We might be using vague language

### Action Items:
- If "In Real Only" is high → Add keyword to our templates
- If "In Generated Only" is high → Consider if real commentary is more creative
- If "In Neither" is high → Check if the event type classification is accurate

## 🔧 Technical Details

### Backend Method
```python
def get_event_type_keyword_presence(self, score_type='average_score'):
    """
    Check if event type keyword appears in commentary text.
    Returns: dict with counts and percentages for each category
    """
```

### Data Processing
1. Get best matches for selected scoring method
2. For each unique event type:
   - Get associated keywords from mapping
   - Check each commentary row for keyword presence
   - Categorize as: In Both, In Real Only, In Generated Only, In Neither
3. Calculate counts and percentages
4. Return sorted by "In Both" percentage (descending)

### Case-Insensitive Matching
All text is converted to lowercase before keyword matching to ensure accurate results regardless of capitalization.

## 📝 Example Interpretation

```
Event Type: Goal
Total: 100 commentaries
In Both: 85 (85%) ✅
In Real Only: 10 (10%)
In Generated Only: 3 (3%)
In Neither: 2 (2%)
```

**Interpretation:**
- **Excellent!** 85% of goal commentaries use "goal"/"scores"/"scored" in both real and generated
- 10% of the time, real mentions "goal" but we use alternative phrases ("nets it", "finds the target")
- 3% of the time, we mention "goal" but real uses alternatives ("finds the net")
- 2% of the time, neither commentary explicitly mentions "goal" (both use creative alternatives)

**Recommendation:** This is very good performance! Minor improvement: add "goal" keyword to templates where we're currently using alternatives.

---

*Created: 2025-11-14*
*Part of: Euro 2024 NLP Commentator Dashboard Analysis*

