# Prompt Engineering Documentation

## 🎯 Overview

This document describes the prompt engineering strategy for GPT-based football commentary generation.

---

## 📋 System Prompt

### **Base System Prompt**

```
You are a professional football (soccer) commentator providing live match commentary.

Your commentary style:
- Professional and engaging, like a real TV commentator
- Capture the excitement level appropriate to the event
- Be accurate with player names, teams, and actions
- Keep commentary concise but vivid
- Match the importance of the event (goals are exciting, routine passes are brief)

Guidelines:
- Goals: Maximum excitement, describe the moment vividly
- Shots: Describe the attempt and outcome
- Cards: Note the player and implications
- Substitutions: Brief tactical note
- General play: Concise description of the action

DO NOT include timestamps like [8:00] at the start.
DO NOT use generic phrases repeatedly.
DO generate natural, varied commentary each time.
```

### **Rationale**
- Sets clear expectations for role and style
- Provides specific guidelines per event type
- Negative instructions prevent common issues
- Encourages natural variation

---

## 🎯 Event-Specific Prompts

### **Goal Event**

```
Generate commentary for this football event:

Event Type: Goal
Player: {player_name}
Team: {team_name}
Minute: {minute}'
Current Score: {home_team} {home_score} - {away_score} {away_team}

Goal Details:
- Body Part: {body_part}
- Distance: {distance}
- Assist By: {assist_player}
- xG: {xg}

Generate EXCITING commentary for this goal! Capture the moment.

Excitement level for this event: 10/10
Generate the commentary now (1-3 sentences):
```

### **Shot Event**

```
Generate commentary for this football event:

Event Type: Shot
Player: {player_name}
Team: {team_name}
Minute: {minute}'

Shot Details:
- Outcome: {shot_outcome}
- Body Part: {body_part}
- Distance: {distance}
- xG: {xg}

Generate commentary describing this shot attempt.

Excitement level for this event: 6/10
Generate the commentary now (1-3 sentences):
```

### **Card Event**

```
Generate commentary for this football event:

Event Type: {Yellow/Red} Card
Player: {player_name}
Team: {team_name}
Minute: {minute}'

Card Details:
- Card Type: {card_type}
- Reason: {foul_reason}

Generate commentary about this {yellow/red} card.

Excitement level for this event: {5-9}/10
Generate the commentary now (1-3 sentences):
```

### **Substitution Event**

```
Generate commentary for this football event:

Event Type: Substitution
Player: {player_off} → {player_on}
Team: {team_name}
Minute: {minute}'

Generate brief tactical commentary about this substitution.

Excitement level for this event: 4/10
Generate the commentary now (1-2 sentences):
```

### **Save Event**

```
Generate commentary for this football event:

Event Type: Save
Player: {goalkeeper_name}
Team: {team_name}
Minute: {minute}'

Save Details:
- Shot By: {shot_player}
- Save Type: {save_type}

Generate commentary praising this save.

Excitement level for this event: 7/10
Generate the commentary now (1-3 sentences):
```

---

## ⚙️ Parameters

### **Temperature**
- **Default**: 0.7
- **Lower (0.3-0.5)**: More consistent, less varied
- **Higher (0.8-1.0)**: More creative, potentially less accurate

### **Max Tokens**
- **Default**: 200
- **Goals**: 200-250 (allow longer description)
- **Passes**: 100-150 (keep brief)

### **Top P**
- **Default**: 0.9
- Nucleus sampling for controlled variation

---

## 💡 Prompt Engineering Tips

### **1. Be Specific**
```
❌ "Generate commentary for this event"
✅ "Generate EXCITING commentary for this goal! Capture the moment."
```

### **2. Provide Context**
```
✅ Include:
- Current score
- Match minute
- Player/team names
- Event-specific details
```

### **3. Set Expectations**
```
✅ "1-3 sentences"
✅ "Excitement level: 10/10"
✅ "Keep it concise but vivid"
```

### **4. Use Negative Instructions**
```
✅ "DO NOT include timestamps"
✅ "DO NOT use generic phrases"
```

### **5. Match Event Importance**
```
Goal: 10/10 → Maximum excitement
Pass: 2/10 → Brief, factual
```

---

## 🔄 Prompt Variations

### **Style: Casual**
Add to system prompt:
```
Use a casual, friendly tone like you're explaining to a friend.
```

### **Style: Dramatic**
Add to system prompt:
```
Be dramatic and theatrical! Build tension and suspense.
```

### **Style: Technical**
Add to system prompt:
```
Focus on tactical aspects. Use technical football terminology.
```

---

## 📊 Quality Metrics

### **Accuracy**
- Player names correct?
- Event type correct?
- Score correct?

### **Naturalness**
- Reads like real commentary?
- Appropriate excitement level?
- No robotic phrases?

### **Variety**
- Different phrasings for same event type?
- Avoids repetition?
- Creative vocabulary?

### **Relevance**
- Matches event importance?
- Appropriate length?
- Contains key details?

---

## 🔍 Common Issues & Fixes

### **Issue: Generic Responses**
```
Problem: "Goal scored by the player"
Fix: Add specific details to prompt, increase temperature
```

### **Issue: Repetitive Patterns**
```
Problem: Same phrases repeated
Fix: Add "DO NOT use generic phrases repeatedly"
```

### **Issue: Timestamps Included**
```
Problem: "[8:00] Player scores"
Fix: Add "DO NOT include timestamps like [8:00] at the start"
```

### **Issue: Wrong Excitement Level**
```
Problem: Routine pass described excitedly
Fix: Include "Excitement level: X/10" in prompt
```

### **Issue: Too Long/Short**
```
Problem: 10-sentence commentary for a pass
Fix: Specify "1-3 sentences" or "2-4 sentences"
```

---

## 🎯 Best Practices

1. **Test prompts** with sample events before batch processing
2. **Iterate** on prompts based on output quality
3. **Log** prompts and outputs for analysis
4. **Version control** prompt changes
5. **A/B test** different prompt variations
6. **Monitor costs** - longer prompts = more tokens

---

## 📈 Future Improvements

1. **Few-shot examples**: Include real commentary samples
2. **Chain-of-thought**: Let model reason about event importance
3. **Context window**: Include match narrative so far
4. **Fine-tuning**: Train on sports commentary dataset
5. **Multi-turn**: Build conversation for sequence commentary

---

*Prompt Engineering Documentation - v1.0*  
*Phase 10: LLM Commentary Generation*  
*Created: November 24, 2025*

