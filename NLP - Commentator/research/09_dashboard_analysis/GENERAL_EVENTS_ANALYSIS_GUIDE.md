# "General" Events Deep Dive Analysis Guide

## 📝 Overview

This analysis specifically focuses on "General" event types to understand the fundamental challenge: **Real commentators stay vague during certain moments, but our generated commentary is built from specific events!**

---

## 🎯 The Core Problem

### Real Commentary
- Uses general/vague language: *"Spain building from the back"*
- No specific event types mentioned
- Focuses on overall play, tempo, possession

### Generated Commentary
- Built from actual event data: *"Rodri passes to Pedri, Pedri carries forward under pressure"*
- Mentions specific event types (Pass, Carry, Pressure)
- Cannot avoid being specific because it describes actual events

**Result**: Mismatch in specificity level!

---

## 🔍 Three Core Analyses

### **1️⃣ Event Type Detection in Generated Commentary**

**Question**: What event types do we reveal when real commentary stays general?

**Method**:
- For each "General" event row, analyze the generated commentary text
- Check for keywords of each event type (Pass, Carry, Shot, etc.)
- Count how many times each event type is mentioned
- Calculate percentage of General events containing each type

**Keywords Mapping**:
```python
{
    'Pass': ['pass', 'passes', 'passed', 'passing'],
    'Carry': ['carry', 'carries', 'carried', 'carrying'],
    'Pressure': ['pressure', 'pressures', 'pressed', 'pressing'],
    'Shot': ['shot', 'shots', 'shoots', 'shooting'],
    'Goal': ['goal', 'goals', 'scores', 'scored', 'scoring'],
    # ... and more
}
```

**Output**:
```
For 2,381 "General" events:
- Pass mentioned in: 1,200 events (50.4%)
- Carry mentioned in: 800 events (33.6%)
- Pressure mentioned in: 600 events (25.2%)
- Shot mentioned in: 100 events (4.2%)
```

**Visualization**: Bar chart showing event type frequency

**Insight**: Shows which events we're "revealing" most when real stays general

---

### **2️⃣ Specificity Level Comparison**

**Question**: How much more specific are we compared to real commentary?

**Method**:
1. Define two word categories:
   - **Specific action words**: pass, shot, carry, dribble, tackle, etc. (from event type keywords)
   - **Vague/general words**: building, play, possession, control, tempo, movement, etc.

2. For Real Commentary:
   - Count total words
   - Count specific action words
   - Count vague/general words
   - Calculate percentages

3. For Generated Commentary:
   - Same process

4. Compare percentages

**Vague Words List**:
```python
{'building', 'play', 'playing', 'movement', 'moving', 'tempo',
 'possession', 'control', 'controlling', 'looking', 'trying'}
```

**Output Example**:
```
Real Commentary:
- Specific words: 8.5% of total words
- Vague words: 15.2% of total words

Generated Commentary:
- Specific words: 42.3% of total words (+33.8% vs Real)
- Vague words: 3.1% of total words (-12.1% vs Real)
```

**Visualizations**:
1. Metric cards showing percentages with deltas
2. Grouped bar chart comparing Real vs. Generated

**Color-coded Interpretation**:
- 🔴 Significantly more specific (>10% difference) → Need improvement
- 🟠 Moderately more specific (5-10% difference) → Could improve
- 🟢 Similarly specific (<5% difference) → Good balance

**Insight**: Quantifies the "over-specification" problem

---

### **3️⃣ Vocabulary Comparison (Top Words)**

**Question**: What words do we use vs. real commentary, excluding event type bias?

**Method**:
1. Extract all words from Real and Generated commentary for General events
2. Remove:
   - Stop words (the, a, an, and, or, etc.)
   - Short words (<3 characters)
   - Punctuation

3. Create two analyses:
   - **Analysis A**: All words (including event types)
   - **Analysis B**: Excluding event type words (focus on descriptive vocabulary)

4. Get top 30 words for each
5. Calculate overlap

**Stop Words List**:
```python
{'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'it', 'its'}
```

**Output**:

**All Words**:
```
Real Top Words:
1. building (450)
2. play (380)
3. possession (320)
...

Generated Top Words:
1. passes (890)
2. carries (670)
3. forward (520)
...
```

**Excluding Event Types**:
```
Real Top Words:
1. building (450)
2. midfield (280)
3. forward (250)
...

Generated Top Words:
1. forward (520)
2. midfield (480)
3. under (420)
...
```

**Overlap Analysis**:
```
Shared words: 7 words → building, forward, midfield, back, spain, possession, wide
Only in Real: 8 words → tempo, control, looking, trying, movement, play, deep, high
Only in Generated: 8 words → pedro, rodri, right, left, side, area, receive, passing
```

**Visualizations**:
1. Radio button toggle: "All Words" vs. "Excluding Event Type Words"
2. Side-by-side horizontal bar charts (top 15 words)
3. Word overlap summary with percentages

**Insight**: 
- Shows vocabulary differences when event type bias is removed
- Identifies words we're missing from real commentary
- Identifies words we overuse that real doesn't

---

## 📊 Dashboard Features

### **Interactive Elements**:
1. **Scoring Method Toggle**: Switch between "With Sentiment" and "Without Sentiment"
2. **Word Filter Radio Button**: Toggle between "All Words" and "Excluding Event Type Words"
3. **Dynamic Metrics**: Show deltas comparing Real vs. Generated

### **Visualizations**:
1. **Event Type Detection**: Vertical bar chart with counts and percentages
2. **Specificity Comparison**: Grouped bar chart + metric cards with color-coded deltas
3. **Top Words**: Side-by-side horizontal bar charts

### **Interpretations & Recommendations**:
- Automatic color-coded assessment (🔴🟠🟢)
- Specific recommendations based on results
- Overlap percentages with insights

---

## 💡 Use Cases & Insights

### **Use Case 1: Identifying Over-Specification**
**Scenario**: Generated commentary uses specific events 35% more than real

**Action**: 
- Review templates for "General" moments
- Add more vague/general descriptions
- Reduce event-specific vocabulary during build-up play

---

### **Use Case 2: Vocabulary Gap Analysis**
**Scenario**: Real uses "tempo", "control", "building" - we don't

**Action**:
- Add these words to templates
- Create "general play" commentary patterns
- Balance specific events with overall descriptions

---

### **Use Case 3: Event Type Coverage**
**Scenario**: Pass appears in 50% of General events, but Shot only 4%

**Action**:
- Understand which events should be mentioned vs. generalized
- Maybe shots should always be specific, but passes can be generalized
- Adjust templates accordingly

---

## 🎯 Interpretation Guidelines

### **Event Type Detection**:
- **High percentage (>40%)**: This event type is commonly revealed
- **Medium (20-40%)**: Sometimes mentioned, sometimes generalized
- **Low (<20%)**: Rarely mentioned explicitly

**Example**: If "Pass" is 50%, it means half of General commentary mentions passing explicitly

---

### **Specificity Analysis**:

**Specific Words Percentage**:
- Real: ~5-15% is typical for general moments
- Generated: Should ideally be similar
- If Generated >20%: Too specific, need more vague language

**Vague Words Percentage**:
- Real: ~10-20% is typical
- Generated: Should be similar
- If Generated <5%: Not enough general language

**Delta Interpretation**:
- **+30% specific**: 🔴 Severe over-specification
- **+15% specific**: 🟠 Moderate over-specification
- **+5% specific**: 🟢 Acceptable range

---

### **Top Words Overlap**:
- **>40% overlap**: Good vocabulary alignment
- **20-40% overlap**: Moderate differences, room for improvement
- **<20% overlap**: Significant vocabulary gap

**When excluding event types**:
- Higher overlap is better - shows we use similar descriptive language
- Focus on words "Only in Real" - these are vocabulary gaps to fill

---

## 🔧 Technical Implementation

### **Backend Method**:
```python
def get_general_events_analysis(self, score_type='average_score'):
    """
    Returns:
    {
        'total_general_events': int,
        'event_type_detection': {
            'Pass': {'count': int, 'percentage': float},
            'Carry': {'count': int, 'percentage': float},
            ...
        },
        'specificity_analysis': {
            'real': {
                'specific_count': int,
                'vague_count': int,
                'total_words': int,
                'specific_percentage': float,
                'vague_percentage': float
            },
            'generated': {...}
        },
        'top_words_analysis': {
            'real_all': [{'word': str, 'count': int}, ...],
            'generated_all': [...],
            'real_no_event': [...],
            'generated_no_event': [...]
        }
    }
    ```
### **Frontend Components**:
- Section header with emoji icon 🔍
- Warning box for scoring method
- Info box explaining the challenge
- Three sub-sections with visualizations
- Automatic interpretations and recommendations

---

## 📈 Expected Results & Benchmarks

### **Typical Results for "General" Events**:

**Event Type Detection**:
- Pass: 40-60%
- Carry: 25-40%
- Pressure: 20-35%
- Shot: 5-15%
- Goal: 1-5%

**Specificity**:
- Real specific words: 5-12%
- Generated specific words: 25-50%
- Delta: Usually +20-40% (problematic)

**Top Words Overlap**:
- All words: 15-30% (low due to event types)
- No event types: 30-50% (better alignment)

---

## 🚀 Recommendations Based on Results

### **If Specificity Delta >30%**:
1. Create "general play" templates
2. Use phrases like:
   - "Building from the back"
   - "Possession in midfield"
   - "Looking to break forward"
   - "Controlling the tempo"
3. Reduce event-by-event narration during build-up

### **If Top Words Overlap <20% (no events)**:
1. Incorporate words from "Only in Real" list
2. Add general descriptive vocabulary
3. Balance specific events with overall descriptions

### **If Certain Events Over-Mentioned**:
1. Identify events that should stay general
2. Create event-specific vs. general rules
3. Maybe: Always mention goals/shots, generalize passes during build-up

---

## 📚 Related Documentation

- `EVENT_TYPE_KEYWORD_ANALYSIS.md` - Event type keyword presence analysis
- `COMPARISON_METHODOLOGY.md` - Overall comparison methodology
- `DASHBOARD_GUIDE.md` - Complete dashboard guide

---

## 🔍 Example Workflow

1. **Navigate** to "General Events Deep Dive Analysis" section
2. **Select** scoring method (With/Without Sentiment)
3. **Review** Event Type Detection chart:
   - See which events we reveal most
   - Identify patterns
4. **Check** Specificity Analysis:
   - Compare specific vs. vague word percentages
   - Note the delta
5. **Explore** Top Words:
   - Toggle "All Words" vs. "Excluding Event Types"
   - Compare side-by-side charts
   - Review overlap analysis
6. **Read** automated interpretations
7. **Take action** based on recommendations

---

## ⚠️ Important Notes

1. **"General" events are special**: They represent moments where real commentators choose to stay vague
2. **We can't avoid being specific**: Our commentary is event-based by nature
3. **The goal**: Find balance between specific events and general descriptions
4. **Context matters**: Some events should always be specific (goals), others can be generalized (passes during build-up)
5. **Vocabulary is key**: Even when being specific, using similar vocabulary helps

---

*Created: 2025-11-14*  
*Part of: Euro 2024 NLP Commentator Dashboard Analysis*  
*Focus: Understanding and improving "General" event commentary generation*

