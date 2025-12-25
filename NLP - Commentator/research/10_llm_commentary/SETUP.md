# Setup Instructions - Phase 10: LLM Commentary

## 🚀 Quick Start

### **Step 1: Install Dependencies**

```bash
cd "NLP - Commentator/research/10_llm_commentary"
pip install -r requirements.txt
```

### **Step 2: Configure API Key**

Create a `.env` file in the `10_llm_commentary` directory:

```bash
# Create .env file
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

Or manually create the file with this content:
```
OPENAI_API_KEY=your-api-key-here
```

### **Step 3: Test Configuration**

```bash
python scripts/config.py
```

Expected output:
```
✅ Configuration valid!
  Model: gpt-4
  Temperature: 0.7
  Max Tokens: 200
  API Key: Set
```

### **Step 4: Test Single Event**

```bash
python scripts/gpt_commentator.py
```

This will generate commentary for a sample goal event.

---

## 📝 Usage Examples

### **Generate Commentary for a Match**

```bash
python scripts/batch_generate.py --match_id 3943043
```

**Options:**
- `--match_id`: Required. The match ID to process
- `--max_events`: Optional. Max events to process (default: 50)
- `--output`: Optional. Custom output file path

### **Example: Final Match**
```bash
# Spain vs England Final
python scripts/batch_generate.py --match_id 3943043 --max_events 100
```

### **Python Usage**

```python
from scripts.gpt_commentator import GPTCommentator

# Initialize
commentator = GPTCommentator()

# Single event
event = {
    'event_type': 'Goal',
    'player_name': 'Oyarzabal',
    'team_name': 'Spain',
    'minute': 86,
    'body_part': 'Left Foot',
    'assist_player': 'Cucurella'
}

commentary = commentator.generate_commentary(event)
print(commentary)
```

---

## ⚙️ Configuration Options

### **Model Selection**

Edit `scripts/config.py`:

```python
# Options:
MODEL_NAME = "gpt-4"           # Best quality, slower
MODEL_NAME = "gpt-4-turbo"     # Fast, good quality
MODEL_NAME = "gpt-4o"          # Newest, balanced
MODEL_NAME = "gpt-4o-mini"     # Cheapest, fast
MODEL_NAME = "gpt-3.5-turbo"   # Budget option
```

### **Temperature**

```python
TEMPERATURE = 0.7  # Default - balanced

TEMPERATURE = 0.3  # More consistent
TEMPERATURE = 1.0  # More creative
```

### **Max Tokens**

```python
MAX_TOKENS = 200  # Default

MAX_TOKENS = 100  # Shorter commentary
MAX_TOKENS = 300  # Longer, more detailed
```

---

## 💰 Cost Estimation

### **GPT-4 Pricing (approximate)**
- Input: ~$0.03 / 1K tokens
- Output: ~$0.06 / 1K tokens

### **Per Event (estimated)**
- Prompt: ~300 tokens
- Output: ~100 tokens
- Cost: ~$0.015 per event

### **Per Match (50 events)**
- Total: ~$0.75 per match

### **All 51 Matches**
- Estimated total: ~$40

### **Cost-Saving Tips**
1. Use `gpt-4o-mini` for testing (~10x cheaper)
2. Reduce `max_events` for initial tests
3. Cache results to avoid regeneration

---

## 🔧 Troubleshooting

### **Error: API Key Not Set**
```
OPENAI_API_KEY not set. Create a .env file with your API key.
```

**Fix**: Create `.env` file with your API key

### **Error: Rate Limited**
```
RateLimitError: Rate limit exceeded
```

**Fix**: Increase `DELAY_BETWEEN_REQUESTS` in config.py

### **Error: Model Not Found**
```
InvalidRequestError: The model does not exist
```

**Fix**: Check model name in config.py

### **Error: Data Not Found**
```
❌ No data found for match 123456
```

**Fix**: Verify match ID exists in Phase 7 data

---

## 📁 Output Files

### **Location**
```
10_llm_commentary/data/llm_commentary/
```

### **File Format**
```
match_{match_id}_llm_commentary_{timestamp}.csv
```

### **Columns**
- `match_id`: Match identifier
- `event_index`: Original event index
- `minute`: Game minute
- `event_type`: Type of event
- `player_name`: Player involved
- `team_name`: Team name
- `rule_based_commentary`: Commentary from Phase 7
- `llm_commentary`: GPT-generated commentary

---

## 🎯 Next Steps

After generating commentary:

1. **Compare with Real Commentary**
   - Use metrics from Phase 8
   - Calculate BERT similarity
   - Compare sentiment

2. **Analyze Results**
   - Which approach is better?
   - For which event types?
   - Quality patterns?

3. **Iterate**
   - Adjust prompts
   - Try different temperatures
   - Fine-tune for specific events

---

## 📚 Related Documentation

- `docs/PROMPTS.md` - Prompt engineering guide
- `README.md` - Phase overview
- `../08_enhanced_comparison/` - Comparison metrics
- `../07_all_games_commentary/` - Rule-based source data

---

*Setup Guide - Phase 10: LLM Commentary*  
*Created: November 24, 2025*

