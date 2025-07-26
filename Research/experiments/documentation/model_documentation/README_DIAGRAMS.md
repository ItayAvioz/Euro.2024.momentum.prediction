# StatsBomb Data Connection Diagrams

This folder contains visual diagrams showing how to connect StatsBomb data for your soccer prediction and commentary project.

## 📊 Available Diagrams

### 1. Data Connection Flow Diagram
**File:** `statsbomb_data_connection_diagram.html`

This interactive diagram shows the complete workflow for connecting StatsBomb data:
- Competition/Season selection
- Match listing
- Events, lineups, and 360° data connections
- Key connection fields (IDs)
- Practical examples for your project

## 🖼️ How to Save Diagrams as Images

### Method 1: Using the HTML File
1. **Open** `statsbomb_data_connection_diagram.html` in your web browser
2. **Wait** for the diagram to load (requires internet connection for Mermaid.js)
3. **Right-click** on the diagram
4. **Select** "Save image as..." or "Copy image"
5. **Save** as `statsbomb_data_connection_flow.png` in your project folder

### Method 2: Screenshot
1. Open the HTML file in your browser
2. Take a screenshot of the diagram area
3. Crop and save as needed

### Method 3: Browser Developer Tools
1. Open the HTML file in Chrome/Firefox
2. Press F12 to open Developer Tools
3. Find the SVG element containing the diagram
4. Right-click → Copy → Copy outerHTML
5. Use an online SVG to PNG converter

## 📋 Diagram Content Summary

The main diagram shows:

```
🏆 Competition/Season Selection (competition_id + season_id)
    ↓
📅 Match List (matches/{competition_id}/{season_id}.json)
    ↓
🔍 Specific Match Selection (match_id)
    ↓
⚽ Events Data (events/{match_id}.json)
👥 Lineups Data (lineups/{match_id}.json)  
🎯 360° Data (three-sixty/{match_id}.json)
    ↓
🔗 Data Connections via player_id, team_id
    ↓
🎯 Your Project Applications
   📺 Commentary Generation
   🤖 Move Quality Prediction
```

## 🎯 Key Connection Fields

| Field | Purpose | Example |
|-------|---------|---------|
| `competition_id` | Identifies the competition | 55 (UEFA Euro) |
| `season_id` | Identifies the season | 282 (2024) |
| `match_id` | Identifies specific match | 3943043 |
| `player_id` | Connects player across data | Links events to lineups |
| `team_id` | Connects team information | Links team data |

## 🚀 Using in Your Project

1. **Reference the diagram** when building your data pipeline
2. **Use the connection fields** to join different data sources
3. **Follow the step-by-step workflow** for consistent data access
4. **Save the image** for documentation and presentations

## 📁 File Structure Reference

```
statsbomb/open-data/data/
├── competitions.json                    # Master index
├── matches/{competition_id}/{season_id}.json  # Match lists
├── events/{match_id}.json              # Match events (~3,400 per match)
├── lineups/{match_id}.json             # Player lineups
└── three-sixty/{match_id}.json         # 360° data (selected matches)
```

## 🔧 Technical Notes

- The HTML diagram requires an internet connection to load Mermaid.js
- All diagrams are responsive and work on desktop/mobile
- Diagrams include color coding for different data types
- Interactive elements show the complete data flow

## 📞 Support

If you need help with the diagrams or data connections:
1. Check the main `StatsBomb_Data_Guide.md`
2. Run `python data_connection_guide.py` for a practical example
3. Use `python statsbomb_explorer.py` to explore the actual data 