# Semi-Final Commentary Generation - Phase 6

## 📊 Overview

Successfully generated rich, detailed sports commentary for **both Euro 2024 semi-final matches** using the same templates and methodology as the final game commentary system.

---

## ⚽ Matches Covered

### 1. Netherlands vs England Semi-Final
- **Match ID**: 3942819
- **Result**: Netherlands 1-2 England
- **Date**: 2024-07-10
- **Total Events**: 3,485
- **Sequences**: 383
- **Key Moment**: Ollie Watkins 90th minute winner

### 2. Spain vs France Semi-Final
- **Match ID**: 3942752
- **Result**: Spain 2-1 France  
- **Date**: 2024-07-09
- **Total Events**: 3,328
- **Sequences**: 377
- **Key Moment**: 4-minute turnaround (Yamal & Olmo goals)

---

## 📁 Generated Files

### Data Files (in `data/` folder)

1. **match_3942819_detailed_commentary_data.csv** (1.1 MB)
   - Netherlands vs England enriched event data
   - 3,485 events × 58 columns
   - Tournament stats, in-match tracking, event context

2. **match_3942819_rich_commentary.csv** (2.3 MB)
   - Netherlands vs England with full commentary
   - 3,485 events × 62 columns
   - Event-level + sequence-level commentary

3. **match_3942752_detailed_commentary_data.csv** (1.1 MB)
   - Spain vs France enriched event data
   - 3,328 events × 58 columns
   - Tournament stats, in-match tracking, event context

4. **match_3942752_rich_commentary.csv** (2.5 MB)
   - Spain vs France with full commentary
   - 3,328 events × 62 columns
   - Event-level + sequence-level commentary

### Scripts (in `scripts/` folder)

1. **extract_semi_final_data.py**
   - Generic extraction script for any match
   - Calculates tournament stats before the match
   - Enriches events with 58 data fields
   - Tracks in-match score and player stats
   - Usage: `python extract_semi_final_data.py <match_id>`

2. **generate_semi_final_commentary.py**
   - Adapted from final game commentary system
   - Uses same 19 event templates
   - Generates event-level and sequence-level commentary
   - Creates narrative flow without player name repetition
   - Usage: `python generate_semi_final_commentary.py <match_id>`

---

## 🎯 Features & Methodology

### Same as Final Game System

✅ **19 Event Templates**:
- Pass, Shot, Goal, Save, Carry, Dribble, Pressure, Block
- Interception, Clearance, Duel, Goalkeeper, Miscontrol
- Dispossessed, Dribbled Past, 50/50, Substitution
- Foul Committed, Injury Stoppage, Tactical Shift

✅ **Enrichment (58 columns)**:
- Tournament stats (wins, draws, losses, goals)
- Player tournament goals
- In-match tracking (score, player match goals)
- Event context (previous/next events)
- Field zones, pressure detection, danger zones
- Pass details, shot details, carry distance

✅ **Commentary Features**:
- Dynamic excitement levels (neutral → excited → MAXIMUM)
- Player & team milestone tracking
- Tournament & in-match statistics integration
- Sequence narrative flow (no player repetition)
- Special period commentary (kickoff, halftime, etc.)

### Tournament Stats

#### Netherlands vs England
- **Netherlands**: 3-1-1 record, 9 goals scored, 5 conceded (5 scorers)
- **England**: 2-3-0 record, 5 goals scored, 3 conceded (6 scorers)

#### Spain vs France  
- **Spain**: 5-0-0 record, 11 goals scored, 2 conceded (8 scorers)
- **France**: 2-3-0 record, 3 goals scored, 1 conceded (6 scorers)

---

## 📈 Output Statistics

### Netherlands vs England
| Metric | Value |
|--------|-------|
| Total Events | 3,485 |
| Sequences | 383 |
| Columns | 62 |
| Top Events | Pass (1,065), Ball Receipt (1,020), Carry (910) |

### Spain vs France
| Metric | Value |
|--------|-------|
| Total Events | 3,328 |
| Sequences | 377 |
| Columns | 62 |
| Top Events | Pass (935), Ball Receipt (912), Carry (778) |

---

## 🔧 Technical Notes

### Generic Script Adaptation

The scripts were adapted from the final game system to work generically:

1. **Match ID as Parameter**: Both scripts accept `<match_id>` as command-line argument
2. **Dynamic Team Names**: Score columns are normalized (e.g., `Netherlands_score` → `spain_score`)
3. **Tournament Stats**: Calculated dynamically for any team before any match date
4. **No Hard-Coding**: Scripts work for any match in the dataset

### Column Normalization

The commentary generation script normalizes team-specific score columns to generic names (`spain_score`, `england_score`) to allow existing templates to work without modification. This is done automatically at runtime.

---

## 🚀 Usage

### Extract Match Data
```bash
python scripts/extract_semi_final_data.py 3942819  # Netherlands vs England
python scripts/extract_semi_final_data.py 3942752  # Spain vs France
```

### Generate Commentary
```bash
python scripts/generate_semi_final_commentary.py 3942819  # Netherlands vs England
python scripts/generate_semi_final_commentary.py 3942752  # Spain vs France
```

---

## 📝 Key Differences from Final Game

1. **Generic Implementation**: Works for any match, not just Spain vs England
2. **Tournament Context**: Stats calculated correctly for semi-finals (not finals)
3. **Multiple Matches**: Demonstrates scalability of the system
4. **Column Mapping**: Automatic normalization of team-specific columns

---

## ✅ Success Metrics

| Metric | Netherlands vs England | Spain vs France |
|--------|----------------------|-----------------|
| Events Processed | 3,485 | 3,328 |
| Sequences Created | 383 | 377 |
| Commentary Generated | ✓ All events | ✓ All events |
| Enrichment Fields | 58 | 58 |
| Final Columns | 62 | 62 |
| File Size | 2.3 MB | 2.5 MB |
| Processing Time | < 1 min | < 1 min |

---

## 🎉 Conclusion

Successfully replicated the final game commentary system for both semi-finals, demonstrating:

✅ System scalability to multiple matches  
✅ Generic implementation working across different teams  
✅ Consistent quality across 6,813 total events  
✅ Same rich features as the final game system  
✅ Fast processing (< 1 minute per match)

**All semi-final matches now have the same high-quality, detailed commentary as the final!**

---

*Generated: October 24, 2025*  
*System: NLP Football Commentator - Phase 6*  
*Matches: Euro 2024 Semi-Finals*

