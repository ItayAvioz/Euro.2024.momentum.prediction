# StatsBomb Open Data: Complete Navigation Guide

## 📁 Data Folder Structure & Connection Map

```
statsbomb/open-data/
├── data/
│   ├── competitions.json          # START HERE - Master index of all competitions
│   ├── matches/                   # Match listings by competition
│   │   ├── {competition_id}/      # One folder per competition
│   │   │   └── {season_id}.json   # Match list for specific season
│   ├── events/                    # Match events (the main data)
│   │   └── {match_id}.json        # Event data for each match
│   ├── lineups/                   # Starting lineups
│   │   └── {match_id}.json        # Lineup data for each match
│   └── three-sixty/               # StatsBomb 360 data (limited matches)
│       └── {match_id}.json        # 360° data for selected matches
├── doc/                           # Documentation
└── img/                           # Images and media
```

## 🔗 How Data Files Connect

### Data Flow Navigation:
1. **competitions.json** → Lists all available competitions and seasons
2. **matches/{competition_id}/{season_id}.json** → Lists all matches for that competition/season
3. **events/{match_id}.json** → Contains ~3,400 events per match
4. **lineups/{match_id}.json** → Starting lineups for the match
5. **three-sixty/{match_id}.json** → 360° data (if available)

### Key Identifiers:
- **competition_id** + **season_id** → Find matches
- **match_id** → Find events, lineups, and 360° data
- **player_id** → Connect across events and lineups
- **team_id** → Connect across all data types

## 🏆 Competition & Season Guidelines

### Major Competitions Available:

#### International Tournaments:
| Competition | Competition ID | Season ID | Description |
|-------------|---------------|-----------|-------------|
| **FIFA World Cup** | 43 | 3 | 2018 Russia (Complete) |
| **FIFA World Cup** | 43 | 106 | 2022 Qatar (Complete) |
| **UEFA Euro** | 55 | 282 | 2024 Germany (Complete) |
| **UEFA Euro** | 55 | 43 | 2020 (Complete) |
| **Copa América** | 223 | 282 | 2024 USA |
| **FIFA Women's World Cup** | 72 | 30 | 2019 France |

#### Premier League:
| Competition | Competition ID | Season ID | Years |
|-------------|---------------|-----------|--------|
| **Premier League** | 2 | 27 | 2015/16 |
| **Premier League** | 2 | 44 | 2003/04 (Arsenal Invincibles) |

#### La Liga:
| Competition | Competition ID | Season ID | Years |
|-------------|---------------|-----------|--------|
| **La Liga** | 11 | 90 | 2020/21 |
| **La Liga** | 11 | 42 | 2015/16 |

#### Other Major Leagues:
| Competition | Competition ID | Season ID | League | Years |
|-------------|---------------|-----------|---------|--------|
| **Serie A** | 12 | 25 | Italy | 2015/16 |
| **Bundesliga** | 9 | 27 | Germany | 2015/16 |
| **Ligue 1** | 7 | 27 | France | 2015/16 |
| **FA Women's Super League** | 37 | Multiple | England | 2018-2022 |

### European Competitions:
| Competition | Competition ID | Season ID | Description |
|-------------|---------------|-----------|-------------|
| **UEFA Champions League** | 16 | Multiple | Various seasons |
| **UEFA Europa League** | 15 | Multiple | Various seasons |

## 🔍 Data Access Methods

### 1. Direct GitHub Download
```bash
# Clone the repository
git clone https://github.com/statsbomb/open-data.git

# Or download specific files
curl -O https://raw.githubusercontent.com/statsbomb/open-data/master/data/competitions.json
```

### 2. Using StatsBombPy (Python)
```python
import statsbombpy as sb

# Get all competitions
competitions = sb.competitions()

# Get matches for Euro 2024
matches = sb.matches(competition_id=55, season_id=282)

# Get events for a specific match
events = sb.events(match_id=3943043)
```

### 3. Using StatsBombR (R)
```r
library(StatsBombR)

# Get competitions
comp <- FreeCompetitions()

# Get matches
matches <- FreeMatches(comp)

# Get events
events <- get.matchFreeKicks(matches)
```

## 📊 Data Content Guidelines

### Events Data (~3,400 events per match):
- **Passing**: Every pass with location, outcome, technique
- **Shooting**: Shots with xG, location, body part
- **Defending**: Tackles, interceptions, clearances
- **Goalkeeping**: Saves, distributions, sweeping
- **Set Pieces**: Corners, free kicks, throw-ins
- **Disciplinary**: Cards, fouls, offside
- **Substitutions**: Player changes with timing

### Lineups Data:
- Starting XI for both teams
- Player positions and jersey numbers
- Substitution information
- Formation data

### 360° Data (Selected Matches):
- Player positions for key events
- Defensive line tracking
- Passing angles and options
- Pressure situations

## 🚀 Quick Start Workflow

### Step 1: Explore Available Data
```python
# Load competitions to see what's available
competitions = sb.competitions()
print(competitions[['competition_name', 'season_name', 'competition_id', 'season_id']])
```

### Step 2: Choose Your Focus
**For Tactical Analysis**: Use events data + 360° data
**For Player Performance**: Use events data + lineups
**For Match Prediction**: Use historical matches + events
**For Commentary/NLP**: Use events data (detailed descriptions)

### Step 3: Load Match Data
```python
# Get all matches for chosen competition
matches = sb.matches(competition_id=55, season_id=282)  # Euro 2024

# Load events for analysis
match_events = sb.events(match_id=matches.iloc[0]['match_id'])
```

## 📈 Best Practices for Your Project

### For Automatic Commentary:
1. **Focus on Events Data**: Rich descriptions of every action
2. **Use Text Fields**: `type`, `play_pattern`, `technique`, `outcome`
3. **Location Data**: XY coordinates for spatial descriptions
4. **Timing**: Minute and second precision for play-by-play

### For Move Quality Prediction:
1. **Events + 360° Data**: Complete tactical picture
2. **Sequence Analysis**: Track possession chains
3. **Pressure Data**: Understand defensive context
4. **Expected Threat (xT)**: Pre-built pitch control models

### For Multi-Competition Analysis:
1. **Start with World Cup/Euro**: Most complete datasets
2. **Use Big 5 Leagues**: Consistent data quality
3. **Consider Women's Data**: Excellent for longitudinal studies

## 🔧 Technical Notes

### File Formats:
- All data in **JSON format**
- UTF-8 encoding for international characters
- Consistent schema across all files

### Data Updates:
- Repository updated regularly
- New tournaments added post-event
- Historical data occasionally backfilled

### Rate Limits:
- No rate limits on GitHub downloads
- StatsBombPy handles API calls automatically
- Consider local caching for large datasets

## 📚 Advanced Usage

### Combining Data Sources:
```python
# Get match events and lineups together
events = sb.events(match_id=3943043)
lineups = sb.lineups(match_id=3943043)

# Merge for player-specific analysis
player_events = events.merge(lineups, on='player_id')
```

### Text Analysis Pipeline:
1. **Extract Action Descriptions**: From events data
2. **Add Context**: Location, time, score situation
3. **Generate Commentary**: Template-based or ML-generated
4. **Quality Assessment**: Based on outcome and xG/xT values

This guide provides the foundation for navigating StatsBomb's data structure and implementing your soccer prediction and commentary project. The key is understanding the relationship between competition_id, season_id, and match_id to access the data you need. 