# Starting Events with Team Statistics - Summary

## Dataset Overview

- **Total Events**: 40
- **Matches**: 10
- **Events per Match**: 4 (kick-off sequence)
- **Total Columns**: 49

## Selected Matches

- **3930158** (2024-06-14): Germany 5-1 Scotland (Group Stage)
- **3930171** (2024-06-20): Denmark 1-1 England (Group Stage)
- **3930180** (2024-06-25): Netherlands 2-3 Austria (Group Stage)
- **3941017** (2024-06-30): England 2-1 Slovakia (Round of 16)
- **3941021** (2024-07-02): Romania 0-3 Netherlands (Round of 16)
- **3942226** (2024-07-05): Spain 2-1 Germany (Quarter-finals)
- **3942382** (2024-07-06): Netherlands 2-1 Turkey (Quarter-finals)
- **3942752** (2024-07-09): Spain 2-1 France (Semi-finals)
- **3942819** (2024-07-10): Netherlands 1-2 England (Semi-finals)
- **3943043** (2024-07-14): Spain 2-1 England (Final)

## Column Categories

### Match Context (6 columns)
- match_id, match_date, stage, kick_off_time, stadium, referee

### Team Information (4 columns)
- team_a, team_b, team_a_score, team_b_score

### Team A Statistics (10 columns)
- matches_played, wins, draws, losses
- goals_scored, goals_conceded, goal_difference
- last_result, last_score, last_opponent

### Team B Statistics (10 columns)
- Same structure as Team A stats

### Lineups (2 columns)
- team_a_lineup, team_b_lineup

### Event Details (14 columns)
- event_number (1-4), event_id, timestamp, minute, second, period
- event_type, event_team, is_team_a_event
- player_name, player_position, location
- pass_details, carry_details, shot_details

