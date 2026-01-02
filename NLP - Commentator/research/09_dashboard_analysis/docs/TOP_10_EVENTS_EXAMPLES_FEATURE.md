# Top 10 Event Types - Commentary Examples Feature

## 📋 Overview

This feature displays **2 random examples** for each of the **top 10 event types**, grouped by **3 BERT similarity ranges** (Low, Medium, High). It provides a direct comparison between real professional commentary and our AI-generated commentary.

---

## 🎯 Purpose

- **Visual Comparison**: See side-by-side real vs. generated commentary
- **Quality Assessment**: Evaluate how well we match professional commentary across different similarity levels
- **Pattern Discovery**: Identify what works well and what needs improvement for each event type
- **BERT Range Analysis**: Understand commentary quality at different semantic similarity levels

---

## 📊 Feature Structure

### **Top 10 Event Types**
Based on frequency in the dataset, typically includes:
1. General
2. Goal
3. Shot
4. Yellow Card
5. Substitution
6. Corner
7. Pass
8. Free Kick
9. Penalty
10. Save

### **BERT Similarity Groups**
- **Low (<0.45)**: Poor semantic similarity
- **Medium (0.45-0.55)**: Moderate semantic similarity
- **High (>0.55)**: Good semantic similarity

### **Examples Per Group**
- **2 random samples** from each BERT range
- Randomly selected using `random_state=42` for reproducibility
- Falls back to 1 sample if only 1 available
- Shows "No examples available" if none in that range

---

## 🖥️ User Interface

### **Section Header**
```
📝 Top 10 Event Types - Commentary Examples by BERT Groups
```

### **Event Type Accordion**
For each event type:
```
### Event Type Name (X total)
```

### **BERT Range Tabs**
Three tabs for each event:
- Low BERT (<0.45)
- Medium BERT (0.45-0.55)
- High BERT (>0.55)

### **Example Display**
For each example:

**Metrics Row** (4 columns):
- BERT Score (e.g., 0.637)
- TF-IDF (e.g., 0.245)
- Content Overlap (e.g., 0.089)
- Minute (e.g., 45+2)

**Commentary Comparison** (2 columns):
- **Left Column**: Real Commentary (with source attribution)
- **Right Column**: Generated Commentary

**Text Area Features**:
- Height: 150px (adjustable for long text)
- Read-only display
- Scroll if content exceeds height
- Unique keys prevent conflicts

---

## 🔧 Technical Implementation

### **Backend Method** (`data_loader.py`)

```python
def get_top_10_event_examples(self, score_type='average_score'):
    """
    Get top 10 event types with 2 random examples per BERT group.
    
    Process:
    1. Get best matches for scoring method
    2. Count event types, get top 10
    3. For each event type:
       - Filter by each BERT range
       - Sample 2 random examples (or less if not enough)
       - Store with metrics and commentary text
    
    Returns:
        dict: {
            'EventType1': {
                'total_count': int,
                'examples': {
                    'Low (<0.45)': {
                        'count_in_range': int,
                        'samples': [
                            {
                                'real_commentary': str,
                                'generated_commentary': str,
                                'bert_score': float,
                                'tfidf_score': float,
                                'content_overlap': float,
                                'minute': str,
                                'source': str
                            },
                            ...
                        ]
                    },
                    'Medium (0.45-0.55)': {...},
                    'High (>0.55)': {...}
                }
            },
            ...
        }
    """
```

### **Frontend Display** (`app.py`)

**Location**: Before footer section

**Features**:
- Uses `st.tabs()` for BERT range navigation
- `st.columns()` for side-by-side commentary display
- `st.metric()` for score visualization
- `st.text_area()` for commentary text (read-only)
- Dynamic key generation to prevent conflicts

**Key Generation Pattern**:
```python
key=f"real_{event_type}_{range_name}_{idx}"
key=f"gen_{event_type}_{range_name}_{idx}"
```

---

## 📈 Example Output

### **Goal Event - High BERT Range**

**Example 1**
```
Metrics:
BERT Score: 0.637    TF-IDF: 0.245    Content Overlap: 0.089    Minute: 8

Real Commentary (Source: FLASHSCORE):
"Goal! Randal Kolo Muani (France) makes the score 0:1 after burying 
a close-range header in the right side of the goal after a good run 
and cross by Kylian Mbappe."

Generated Commentary:
"[8:00] Kylian Mbappé Lottin under pressure, delivers the free kick 
a dangerous medium pass through the air to Randal Kolo Muani into 
the central attacking third, Randal Kolo Muani receives under pressure 
in the central attacking third ⚽ GOOOAL! Randal Kolo Muani scores! 
A brilliant header from close range (5m)! France now lead 1-0! 
His first goal of the tournament in the 8th minute!"
```

---

## 💡 Use Cases

### **1. Quality Assessment**
- Compare our best matches (high BERT) with professional commentary
- See what good semantic similarity looks like in practice
- Identify areas where we match well vs. poorly

### **2. Pattern Discovery**
- **High BERT examples**: Learn what makes good matches
- **Low BERT examples**: Understand where we diverge
- **Medium BERT examples**: See the transition zone

### **3. Event-Specific Insights**
- **Goals**: Do we capture the excitement?
- **Substitutions**: Do we provide tactical context?
- **Fouls**: Do we match the tone?
- **General**: Do we stay appropriately vague?

### **4. Improvement Guidance**
- **Vocabulary gaps**: Words real uses that we don't
- **Phrasing differences**: How professionals structure narratives
- **Tone mismatches**: Emotional alignment issues
- **Context inclusion**: What details matter most

---

## 🎯 Interpretation Guidelines

### **High BERT (>0.55)**
**What to look for**:
- ✅ Similar narrative structure
- ✅ Matching key details (player, outcome, location)
- ✅ Comparable emotional tone
- ⚠️ May still have vocabulary differences (low TF-IDF)
- ⚠️ May differ in specificity level

**Expected Quality**: These should feel like good matches

### **Medium BERT (0.45-0.55)**
**What to look for**:
- ⚠️ Describes same event but different emphasis
- ⚠️ May focus on different aspects (build-up vs. outcome)
- ⚠️ Tone might differ (excitement vs. description)
- ℹ️ Often where real stays vague, we get specific

**Expected Quality**: Recognizable as same event, but noticeably different

### **Low BERT (<0.45)**
**What to look for**:
- ❌ Fundamentally different narratives
- ❌ May describe different events in same minute
- ❌ Completely different vocabulary
- ❌ Mismatched focus or emphasis
- ℹ️ These are our weakest matches

**Expected Quality**: May not feel like the same event

---

## 🔍 Analysis Tips

### **Compare Across BERT Ranges**
For the same event type, compare:
- What changes from Low → Medium → High?
- Do high BERT examples share common patterns?
- What makes low BERT examples fail?

### **Compare Across Event Types**
- Which event types have more High BERT examples?
- Which struggle to get good matches?
- Are some events inherently harder to match?

### **Focus on Metrics**
- **High BERT + High TF-IDF**: Excellent match (similar words + meaning)
- **High BERT + Low TF-IDF**: Good meaning, different vocabulary
- **Low BERT + High Content**: Matching words, different meaning
- **All Low**: Poor match across all dimensions

---

## 📝 Notes

1. **Not Affected by Scoring Method Toggle**: Uses `average_score` by default, independent of user selection
2. **Random State Fixed**: Uses `random_state=42` for reproducible examples
3. **Best Matches Only**: Only shows the best-selected match for each minute
4. **Source Attribution**: Shows which data source provided the real commentary
5. **Minute Format**: Preserves original format (e.g., "45+2" for stoppage time)

---

## 🚀 Future Enhancements (Optional)

1. **Refresh Button**: Generate new random examples
2. **Filter by Source**: Show examples only from specific sources
3. **Export Functionality**: Download examples as CSV/PDF
4. **Highlight Differences**: Visual highlighting of word matches/mismatches
5. **Sentiment Indicators**: Color-code by sentiment match
6. **Example Count Selector**: Let users choose how many examples (2, 5, 10)
7. **Search Functionality**: Find examples containing specific words/players
8. **Worst Examples**: Option to show poorest matches instead of random

---

## ✅ Implementation Complete

**Files Modified**:
- `scripts/data_loader.py`: Added `get_top_10_event_examples()` method
- `app.py`: Added "Top 10 Event Types Examples" section before footer

**Lines Added**:
- Backend: ~90 lines
- Frontend: ~85 lines

**Testing**: Ready for testing with real data

---

*Feature created: November 24, 2025*  
*Part of: Euro 2024 NLP Commentator Dashboard Analysis*  
*Status: ✅ Implementation Complete*

