import pandas as pd
import json

# Load pre-calculated metrics analysis
df = pd.read_csv('../outputs/metrics_vs_result_analysis.csv')

# Load existing JSON
with open('../outputs/dashboard_metrics.json', 'r') as f:
    json_data = json.load(f)

# ============================================================
# 1. ABSOLUTE MOMENTUM MARGINS (extended to 60%)
# ============================================================
momentum_margins = {}
for threshold in [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60]:
    valid = df[(df['momentum_outcome'] != 'TIE') & (df['momentum_margin_pct'] >= threshold)]
    total = len(valid)
    if total > 0:
        wins = (valid['momentum_outcome'] == 'WIN').sum()
        loses = (valid['momentum_outcome'] == 'LOSE').sum()
        draws = (valid['momentum_outcome'] == 'DRAW').sum()
        momentum_margins[str(threshold)] = {
            'games': total,
            'win_pct': round(wins/total*100, 1),
            'lose_pct': round(loses/total*100, 1),
            'draw_pct': round(draws/total*100, 1)
        }

json_data['momentum_margins'] = momentum_margins

# ============================================================
# 2. NUMBER OF SEQUENCES MARGINS (extended to 6)
# ============================================================
df['seq_margin'] = abs(df['home_num_seq'] - df['away_num_seq'])
num_seq_margins = {}
for threshold in [0, 1, 2, 3, 4, 5, 6]:
    valid = df[(df['num_seq_outcome'] != 'TIE') & (df['seq_margin'] >= threshold)]
    total = len(valid)
    if total > 0:
        wins = (valid['num_seq_outcome'] == 'WIN').sum()
        loses = (valid['num_seq_outcome'] == 'LOSE').sum()
        draws = (valid['num_seq_outcome'] == 'DRAW').sum()
        num_seq_margins[str(threshold)] = {
            'games': total,
            'win_pct': round(wins/total*100, 1),
            'lose_pct': round(loses/total*100, 1),
            'draw_pct': round(draws/total*100, 1)
        }

json_data['num_seq_margins'] = num_seq_margins

# ============================================================
# 3. POSITIVE CHANGES MARGINS
# ============================================================
df['change_margin_pct_calc'] = abs(df['home_positive_changes'] - df['away_positive_changes']) / df['total_windows'] * 100
positive_changes_margins = {}
for threshold in [0, 5, 10, 15]:
    valid = df[(df['change_outcome'] != 'TIE') & (df['change_margin_pct_calc'] >= threshold)]
    total = len(valid)
    if total > 0:
        wins = (valid['change_outcome'] == 'WIN').sum()
        loses = (valid['change_outcome'] == 'LOSE').sum()
        draws = (valid['change_outcome'] == 'DRAW').sum()
        positive_changes_margins[str(threshold)] = {
            'games': total,
            'win_pct': round(wins/total*100, 1),
            'lose_pct': round(loses/total*100, 1),
            'draw_pct': round(draws/total*100, 1)
        }

json_data['positive_changes_margins'] = positive_changes_margins

# ============================================================
# 4. LONGEST SEQUENCE MARGINS (extended to 6)
# ============================================================
df['longest_margin_calc'] = abs(df['home_longest'] - df['away_longest'])
longest_margins = {}
for threshold in [0, 1, 2, 3, 4, 5, 6]:
    valid = df[(df['longest_outcome'] != 'TIE') & (df['longest_margin_calc'] >= threshold)]
    total = len(valid)
    if total > 0:
        wins = (valid['longest_outcome'] == 'WIN').sum()
        loses = (valid['longest_outcome'] == 'LOSE').sum()
        draws = (valid['longest_outcome'] == 'DRAW').sum()
        longest_margins[str(threshold)] = {
            'games': total,
            'win_pct': round(wins/total*100, 1),
            'lose_pct': round(loses/total*100, 1),
            'draw_pct': round(draws/total*100, 1)
        }

json_data['longest_margins'] = longest_margins

# Save updated JSON
with open('../outputs/dashboard_metrics.json', 'w') as f:
    json.dump(json_data, f, indent=2)

print("JSON updated successfully!")
print("\n--- ABSOLUTE MOMENTUM MARGINS ---")
for k, v in momentum_margins.items():
    print(f"{k}%+: Games={v['games']}, WIN={v['win_pct']}%, LOSE={v['lose_pct']}%")

print("\n--- NUMBER OF SEQUENCES MARGINS ---")
for k, v in num_seq_margins.items():
    print(f"{k}+: Games={v['games']}, WIN={v['win_pct']}%, LOSE={v['lose_pct']}%")

print("\n--- POSITIVE CHANGES MARGINS ---")
for k, v in positive_changes_margins.items():
    print(f"{k}%+: Games={v['games']}, WIN={v['win_pct']}%, LOSE={v['lose_pct']}%")

print("\n--- LONGEST SEQUENCE MARGINS ---")
for k, v in longest_margins.items():
    print(f"{k}+: Games={v['games']}, WIN={v['win_pct']}%, LOSE={v['lose_pct']}%")

