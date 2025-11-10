# Batch Enhanced Comparison - Plan

## Overview

Process all 51 Euro 2024 matches with enhanced comparison, generating individual CSV files for each game.

---

## Input Data

### Generated Commentary
**Location:** `NLP - Commentator/research/07_all_games_commentary/data/`
**Files:** 51 × `match_[ID]_rich_commentary.csv`

### Real Commentary
**Location:** `NLP - Commentator/research/06_real_commentary_collection/data/`
**Sources:**
- FlashScore: 51 games (all Euro 2024)
- SportsMole: 6 games
- BBC: 4 games
- FOX: 4 games
- ESPN: 4 games

**Total unique games with real commentary:** 54 matches

---

## Match List (51 Total)

### Group Stage - Round 1 (12 matches)
```
3930158, 3930159, 3930160, 3930161, 3930162, 3930163,
3930164, 3930165, 3930166, 3930167, 3930168, 3930169
```

### Group Stage - Round 2 (12 matches)
```
3930170, 3930171, 3930172, 3930173, 3930174, 3930175,
3930176, 3930177, 3930178, 3930179, 3930180, 3930181
```

### Group Stage - Round 3 (12 matches)
```
3930182, 3930183, 3930184, 3938637, 3938638, 3938639,
3938640, 3938641, 3938642, 3938643, 3938644, 3938645
```

### Round of 16 (8 matches)
```
3940878, 3940983, 3941017, 3941018, 3941019, 3941020,
3941021, 3941022
```

### Quarter-Finals (4 matches)
```
3942226, 3942227, 3942349, 3942382
```

### Semi-Finals (2 matches)
```
3942752, 3942819
```

### Final (1 match)
```
3943043
```

---

## Processing Script

**Script:** `scripts/compare_all_matches.py`

**What it does:**
1. Loads each match's generated commentary (`match_[ID]_rich_commentary.csv`)
2. Finds corresponding real commentary (FlashScore, SportsMole, etc.)
3. Performs enhanced comparison with all metrics:
   - TF-IDF (lexical similarity)
   - Embeddings_BERT (semantic similarity)
   - Sentiment analysis (RoBERTa)
   - Word counts (total, content words, matching words)
   - Entity counts (players, teams, events - unique & repetition)
   - NER match ratios
4. Handles minute alignment (regular time, stoppage time, extra time, periods)
5. Ranks sequences by average similarity score
6. Saves results to `data/match_[ID]_enhanced_comparison.csv`

---

## Output Template

Each CSV will follow the same format as `match_3942752_enhanced_comparison.csv`:

### Columns (44 total):

1. **match_id** - Match identifier
2. **minute** - Minute (FlashScore format: "45+2", "90+4", etc.)
3. **real_commentary** - Original real commentary text
4. **our_sequence_commentary** - Our generated sequence commentary
5. **sequence_id** - Sequence identifier from our data
6. **sequence_rank** - Rank (1=best match for this minute)

**Similarity Metrics:**
7. **TF-IDF** - Word overlap similarity (0-1)
8. **Embeddings_BERT** - Semantic similarity (-1 to 1)
9. **average_score** - Average of similarity metrics

**Sentiment Analysis:**
10. **real_sentiment** - Real commentary sentiment (-1 to 1)
11. **our_sentiment** - Generated commentary sentiment (-1 to 1)
12. **sentiment_diff** - Absolute difference

**Word Counts:**
13. **real_word_count** - Total words in real commentary
14. **our_word_count** - Total words in generated commentary
15. **real_content_words** - Content words (no stop words) in real
16. **our_content_words** - Content words in generated
17. **matching_content_words** - Common content words
18. **content_overlap_ratio** - Matching / total unique content words

**Entity Counts - Unique:**
19. **real_players_unique** - Unique players in real commentary
20. **our_players_unique** - Unique players in generated commentary
21. **real_teams_unique** - Unique teams in real commentary
22. **our_teams_unique** - Unique teams in generated commentary
23. **real_events_unique** - Unique event types in real commentary
24. **our_events_unique** - Unique event types in generated commentary

**Entity Counts - Repetition:**
25. **real_players_repetition** - Total player mentions in real
26. **our_players_repetition** - Total player mentions in generated
27. **real_teams_repetition** - Total team mentions in real
28. **our_teams_repetition** - Total team mentions in generated
29. **real_events_repetition** - Total event mentions in real
30. **our_events_repetition** - Total event mentions in generated

**NER Match Ratios:**
31. **entity_players_match** - Player entity overlap ratio
32. **entity_teams_match** - Team entity overlap ratio
33. **entity_events_match** - Event entity overlap ratio

**Metadata:**
34-44. Additional context (team names, stage, data source, etc.)

---

## Expected Results

**Output:**
- **Multiple CSV files per match** (if multiple sources available)
- Files named: `match_[ID]_[source]_enhanced_comparison.csv`
- Each file contains minute-by-minute comparison with all metrics

**Examples:**
- `match_3942752_flashscore_enhanced_comparison.csv`
- `match_3942752_sports_mole_enhanced_comparison.csv`
- `match_3943043_flashscore_enhanced_comparison.csv`
- `match_3943043_bbc_enhanced_comparison.csv`

**Total CSV Count:**
- All 51 matches have FlashScore: 51 CSVs
- 6 matches also have SportsMole: +6 CSVs
- 4 matches also have BBC: +4 CSVs
- 4 matches also have FOX: +4 CSVs
- 4 matches also have ESPN: +4 CSVs
- **Total: ~65-70 comparison CSVs** (accounting for overlap)

**Estimated time:**
- ~2-3 minutes per source (sentiment model loading, BERT embeddings)
- Total: ~130-210 minutes for all comparisons

---

## Key Features

✅ **Minute Alignment:**
- Regular time: FlashScore minute N → Our minute N-1
- Stoppage time: FlashScore 45+2 → Our minute 46, period 1
- Extra time: FlashScore 105+1 → Our minute 105, period 3
- CSV displays FlashScore format (e.g., "45+2", "90+4")

✅ **Sequence Ranking:**
- Multiple sequences per minute ranked by `average_score`
- Best match = rank 1

✅ **Data Normalization:**
- Team names normalized (e.g., "Netherlands" / "Holland" / "The Netherlands")
- Player names cleaned (special characters, encoding issues)

✅ **Multiple Data Sources:**
- Prioritizes FlashScore (most complete)
- Falls back to SportsMole, BBC, FOX, ESPN
- Tracks data source in output

---

## Status

**Ready to execute:** ✅

All components tested and verified on match 3942752 (Spain vs France SF).

**Command to run:**
```bash
cd "C:\Users\yonatanam\Desktop\Euro 2024 - momentum - DS-AI project\NLP - Commentator\research\08_enhanced_comparison\scripts"
python compare_all_matches.py
```

---

## Next Steps After Completion

1. Verify all 51 CSVs generated successfully
2. Check for any failed matches
3. Aggregate statistics across all matches
4. Create dashboard for analysis (Phase 4)

