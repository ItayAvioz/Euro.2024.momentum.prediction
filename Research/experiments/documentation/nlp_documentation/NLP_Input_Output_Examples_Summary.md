# NLP Input-Output Examples Summary

## Overview
This document provides concrete input-output examples for the **5 key NLP techniques** that were actually implemented in the Euro 2024 soccer momentum prediction project.

## The 5 NLP Techniques

### 1️⃣ Rule-Based Text Processing with Domain Vocabulary

**Purpose**: Convert raw event data into natural language using soccer-specific terminology.

**Input → Output Examples**:

```
📥 INPUT: {'player_name': 'Harry Kane', 'team_name': 'England', 'event_type': 'Pass', 'outcome': 'successful'}
📤 OUTPUT: "Harry Kane (England) completes a pass"

📥 INPUT: {'player_name': 'Jude Bellingham', 'team_name': 'England', 'event_type': 'Shot', 'outcome': 'on_target'}
📤 OUTPUT: "Jude Bellingham (England) forces a save"

📥 INPUT: {'player_name': 'Van Dijk', 'team_name': 'Netherlands', 'event_type': 'Pressure', 'outcome': 'successful'}
📤 OUTPUT: "Van Dijk (Netherlands) wins ball back"
```

**Key Features**:
- Domain-specific vocabulary mapping
- Consistent natural language output
- Player and team context integration

---

### 2️⃣ Template-Based Commentary Generation

**Purpose**: Create structured narratives using predefined templates with variable substitution.

**Input → Output Examples**:

```
📥 INPUT: Template='momentum_description' Data={'team': 'England', 'momentum_level': 'building momentum', 'score': 7.2}
📤 OUTPUT: "England are building momentum with momentum at 7.2/10"

📥 INPUT: Template='prediction' Data={'team': 'Netherlands', 'trend': 'increase', 'future_score': 6.8}
📤 OUTPUT: "Model predicts Netherlands momentum will increase to 6.8/10"

📥 INPUT: Template='player_action' Data={'player': 'Harry Kane', 'action': 'forces save', 'zone': 'attacking third'}
📤 OUTPUT: "Harry Kane forces save in the attacking third"
```

**Key Features**:
- Flexible template system
- Variable substitution
- Consistent commentary structure

---

### 3️⃣ Simple Sentiment Scoring

**Purpose**: Assign numerical sentiment values to events for momentum calculation.

**Input → Output Examples**:

```
📥 INPUT: England attacking sequence
  - Kane Pass (progressive)
  - Bellingham Carry (progressive)
  - Kane Shot (on_target)
📤 OUTPUT:
  Overall Sentiment: +0.50
  Individual Scores:
    - Kane Pass (progressive): +0.4
    - Bellingham Carry (progressive): +0.3
    - Kane Shot (on_target): +0.8

📥 INPUT: Netherlands struggling
  - Gakpo Pass (failed)
  - Depay Shot (off_target)
📤 OUTPUT:
  Overall Sentiment: -0.20
  Individual Scores:
    - Gakpo Pass (failed): -0.3
    - Depay Shot (off_target): -0.1
```

**Key Features**:
- Rule-based sentiment weights
- Event outcome-specific scoring
- Aggregate sentiment calculation

---

### 4️⃣ Context Pattern Detection

**Purpose**: Identify tactical patterns and game phases from event sequences.

**Input → Output Examples**:

```
📥 INPUT: England attacking surge
  - Kane (England) Shot
  - Foden (England) Shot
  - Saka (England) Shot
📤 OUTPUT:
  Detected Patterns: ['attacking_surge']
  Dominant Team: England (100.0%)
  Summary: 3 events, 1 teams

📥 INPUT: Netherlands defensive pressure
  - Van Dijk (Netherlands) Pressure
  - De Jong (Netherlands) Pressure
  - Ake (Netherlands) Pressure
📤 OUTPUT:
  Detected Patterns: ['defensive_pressure']
  Dominant Team: Netherlands (100.0%)
  Summary: 3 events, 1 teams
```

**Key Features**:
- Pattern recognition from event sequences
- Team dominance calculation
- Tactical phase identification

---

### 5️⃣ Spatial Data Integration

**Purpose**: Incorporate field position data to enhance event analysis.

**Input → Output Examples**:

```
📥 INPUT: Kane Shot at [112, 38]
📤 OUTPUT:
  Spatial Description: attacking third, central
  Coordinates: (112, 38)
  Goal Distance: 8.2m
  Danger Level: high

📥 INPUT: Bellingham Pass at [65, 45]
📤 OUTPUT:
  Spatial Description: midfield, central
  Coordinates: (65, 45)
  Goal Distance: 55.2m
  Danger Level: low

📥 INPUT: Saka Carry at [95, 15]
📤 OUTPUT:
  Spatial Description: attacking third, left flank
  Coordinates: (95, 15)
  Goal Distance: 35.4m
  Danger Level: medium
```

**Key Features**:
- Field zone determination
- Distance to goal calculation
- Danger level assessment

---

## 🎯 Integrated Example: All Techniques Together

**Complete Input Sequence**:
```
Event 1: Harry Kane Pass (progressive) at [75, 42]
Event 2: Jude Bellingham Carry (progressive) at [88, 35]
Event 3: Harry Kane Shot (on_target) at [112, 39]
Event 4: Van Dijk Pressure (successful) at [25, 40]
```

**Complete Output (All Techniques)**:

1. **Text Processing**:
   - Harry Kane (England) plays progressive pass
   - Jude Bellingham (England) drives forward
   - Harry Kane (England) forces a save
   - Van Dijk (Netherlands) wins ball back

2. **Sentiment Analysis**:
   - Overall Score: +0.45
   - Individual scores: Kane Pass (+0.4), Bellingham Carry (+0.3), Kane Shot (+0.8), Van Dijk Pressure (+0.3)

3. **Context Patterns**:
   - Detected: ['England_dominance', 'attacking_phase']
   - Dominant Team: England (75.0%)

4. **Spatial Integration**:
   - Kane: midfield, 45.0m from goal
   - Bellingham: attacking third, 32.4m from goal
   - Kane: attacking third, 8.1m from goal
   - Van Dijk: defensive third, 95.0m from goal

5. **Template Commentary**:
   - "England building momentum through progressive passing, forward runs, and clinical finishing"

**Generated Commentary**:
```
"England are building momentum with a clinical attacking sequence.
Harry Kane plays progressive pass in midfield, Jude Bellingham drives
forward into the attacking third, and Kane forces a save 8.2m from goal.
Overall sentiment: +0.45/1.0. Pattern detected: England dominance with
attacking phase. Van Dijk wins ball back in defensive third, but England
maintain territorial advantage. Momentum prediction: 7.2/10."
```

---

## 🔑 Key Insights

### What Was Actually Implemented:
✅ **Rule-based text processing** with domain vocabulary  
✅ **Template-based commentary generation** system  
✅ **Simple rule-based sentiment scoring**  
✅ **Context pattern detection** from event sequences  
✅ **Spatial data integration** (360° processing)  
✅ **Basic narrative structure** creation  
✅ **Integration with momentum prediction** models  

### What Was NOT Implemented:
❌ Advanced NLP models (BERT, GPT, Transformer)  
❌ Deep learning text generation  
❌ Sophisticated natural language understanding  
❌ Named entity recognition systems  
❌ Advanced sentiment analysis models  
❌ Natural language inference  
❌ Contextual word embeddings  
❌ Large language model integration  

### Why This Approach Was Chosen:
1. **Reliability**: Rule-based systems are predictable and consistent
2. **Domain Control**: Soccer-specific terminology and patterns
3. **Integration**: Easy to combine with existing ML models
4. **Transparency**: Clear, interpretable logic flow
5. **Maintenance**: Simple to update and modify rules
6. **Performance**: Fast execution suitable for real-time use
7. **Resource Efficiency**: No need for large model infrastructure

---

## 🎯 Final Summary

This project successfully demonstrated that **simple, well-designed rule-based systems** can be highly effective for domain-specific applications like soccer commentary and analysis. The 5 NLP techniques work together seamlessly to transform raw StatsBomb event data into rich, contextual commentary with momentum predictions.

The approach proves that you don't always need cutting-edge AI models to create practical, working solutions for real-world problems. Sometimes the best solution is the simplest one that works reliably!

### Processing Flow:
```
📝 INPUT: Raw StatsBomb event data
🔄 PROCESSING: 5 parallel NLP techniques
📤 OUTPUT: Rich, contextual commentary with predictions
```

The techniques successfully integrate with the momentum prediction models to create a complete soccer analysis system suitable for automatic commentary generation and tactical insights. 