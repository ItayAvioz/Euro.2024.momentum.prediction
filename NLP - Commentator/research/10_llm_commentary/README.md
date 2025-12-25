# Phase 10: LLM Commentary Generation

## 🎯 Objective

Generate football match commentary using **Large Language Models (GPT)** based on event data, comparing with both:
1. **Real professional commentary** (from FlashScore, BBC, etc.)
2. **Rule-based generated commentary** (from previous phases)

---

## 📊 Overview

### **Approach**
- Use OpenAI GPT models to generate natural language commentary
- Input: Event data (player, action, location, context)
- Output: Natural, engaging commentary text
- Compare quality with rule-based approach

### **Goals**
1. Generate more natural, varied commentary
2. Capture professional commentator style and tone
3. Achieve higher similarity scores with real commentary
4. Maintain accuracy of event details

---

## 🏗️ Folder Structure

```
10_llm_commentary/
├── README.md                    # This file
├── scripts/
│   ├── gpt_commentator.py       # Main GPT commentary generator
│   ├── batch_generate.py        # Batch processing for all matches
│   ├── compare_approaches.py    # Compare LLM vs Rule-based vs Real
│   └── config.py                # API configuration
├── data/
│   ├── llm_commentary/          # Generated commentary output
│   └── comparisons/             # Comparison results
├── docs/
│   ├── PROMPTS.md               # Prompt engineering documentation
│   └── RESULTS.md               # Results analysis
└── prompts/
    ├── base_prompt.txt          # Base system prompt
    └── event_templates/         # Event-specific prompt templates
```

---

## 🔧 Setup

### **Prerequisites**
1. OpenAI API key
2. Python 3.8+
3. Required packages (see requirements.txt)

### **Installation**
```bash
cd "NLP - Commentator/research/10_llm_commentary"
pip install openai pandas python-dotenv
```

### **API Key Configuration**
Create a `.env` file in this directory:
```
OPENAI_API_KEY=your_api_key_here
```

---

## 🚀 Usage

### **Single Event Commentary**
```python
from scripts.gpt_commentator import GPTCommentator

commentator = GPTCommentator()
commentary = commentator.generate_commentary(event_data)
```

### **Batch Generation**
```bash
python scripts/batch_generate.py --match_id 3943043
```

### **Compare Approaches**
```bash
python scripts/compare_approaches.py --match_id 3943043
```

---

## 📈 Expected Improvements

### **Over Rule-Based**
- More natural language flow
- Greater vocabulary variety
- Better emotional tone matching
- Contextual awareness
- Professional style adaptation

### **Metrics to Track**
- BERT similarity score (vs real)
- Sentiment alignment
- Vocabulary diversity
- Naturalness rating
- Event accuracy

---

## 🔍 Comparison Framework

### **Three-Way Comparison**
```
Real Commentary (FlashScore/BBC)
         ↕
LLM Commentary (GPT-generated)
         ↕
Rule-Based Commentary (Phase 7)
```

### **Questions to Answer**
1. Does LLM achieve higher BERT scores than rule-based?
2. Does LLM match sentiment better?
3. Is LLM more varied in vocabulary?
4. Does LLM maintain event accuracy?
5. Which approach is more "natural"?

---

## 📋 Event Types to Support

Based on Phase 3 analysis, priority event types:
1. **Goal** - Most critical, highest stakes
2. **Shot** - Attacking action
3. **Yellow Card** - Disciplinary
4. **Substitution** - Tactical
5. **Corner** - Set piece
6. **Free Kick** - Set piece
7. **Penalty** - High stakes
8. **Save** - Goalkeeper action
9. **Pass** - Build-up play
10. **General** - Overall play description

---

## 💡 Prompt Engineering Strategy

### **Base System Prompt**
```
You are a professional football commentator providing live match commentary.
Your style is engaging, accurate, and captures the excitement of the moment.
Match key events to their importance - goals are exciting, routine plays are brief.
```

### **Event-Specific Context**
- Current score
- Match minute
- Team names
- Player details
- Location on pitch
- Previous events (context)

---

## 📊 Expected Output Format

### **Input (Event Data)**
```json
{
    "event_type": "Goal",
    "player": "Kolo Muani",
    "team": "France",
    "minute": 8,
    "score_before": "0-0",
    "score_after": "1-0",
    "body_part": "Header",
    "distance": "5m",
    "assist_player": "Mbappé"
}
```

### **Output (LLM Commentary)**
```
"GOOOAL! Randal Kolo Muani rises highest to meet Mbappé's cross and 
powers a header into the back of the net! France take the lead in 
the 8th minute - what a start for Les Bleus! The stadium erupts!"
```

---

## ⚙️ Configuration Options

### **Model Settings**
- Model: `gpt-4` or `gpt-3.5-turbo`
- Temperature: 0.7 (balance creativity/accuracy)
- Max tokens: 150 (commentary length limit)
- Top P: 0.9

### **Style Options**
- Formal vs Casual
- Excitement level (1-10)
- Detail level (brief/standard/detailed)
- Include emojis (yes/no)

---

## 🎯 Success Criteria

### **Phase Complete When**
1. ✅ LLM generates commentary for all event types
2. ✅ Achieves higher BERT scores than rule-based
3. ✅ Maintains 95%+ event accuracy
4. ✅ Comparison framework complete
5. ✅ Documentation finalized

---

## 📚 Related Phases

- **Phase 3**: Top 11 events analysis (event types reference)
- **Phase 7**: All games commentary (rule-based reference)
- **Phase 8**: Enhanced comparison (similarity metrics)
- **Phase 9**: Dashboard analysis (visualization)

---

## 🔄 Development Status

- [x] Folder structure created
- [ ] API configuration setup
- [ ] Base prompt engineering
- [ ] Single event generation
- [ ] Batch processing
- [ ] Comparison framework
- [ ] Results analysis
- [ ] Documentation complete

---

*Phase 10 created: November 24, 2025*  
*Status: 🚧 In Development*  
*Goal: LLM-based commentary generation with GPT*

