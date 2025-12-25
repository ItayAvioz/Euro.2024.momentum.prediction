"""
Compare metric calculations: Original vs Period-Separated
Check if calculations match the original Dashboard approach
"""

import pandas as pd
import numpy as np

print("="*70)
print("COMPARISON: ORIGINAL vs PERIOD-SEPARATED CALCULATIONS")
print("="*70)

# Load original predictions
orig_path = '../../../models/modeling/scripts/outputs/predictions/arimax_predictions.csv'
orig_df = pd.read_csv(orig_path)
orig_df = orig_df[orig_df['model_type'] == 'momentum_to_change_arimax']

# Load period-separated predictions
new_path = '../outputs/arimax_predictions_by_period.csv'
new_df = pd.read_csv(new_path)

print(f"\nOriginal predictions: {len(orig_df)}")
print(f"Period-separated predictions: {len(new_df)}")

# Clean data
orig_clean = orig_df.dropna(subset=['prediction_value', 'actual_value'])
new_clean = new_df.dropna(subset=['prediction_value', 'actual_value'])

print(f"Original clean: {len(orig_clean)}")
print(f"Period-separated clean: {len(new_clean)}")

def calculate_all_metrics(df, name, game_col='game_id'):
    """Calculate all metrics for a dataframe"""
    print(f"\n{'='*70}")
    print(f"{name.upper()}")
    print(f"{'='*70}")
    
    pred = df['prediction_value'].values
    actual = df['actual_value'].values
    
    # 1. SIGN AGREEMENT (individual predictions)
    pred_sign = np.sign(pred)
    actual_sign = np.sign(actual)
    sign_agreement = (pred_sign == actual_sign).mean()
    
    print(f"\n1. SIGN AGREEMENT: {sign_agreement*100:.2f}%")
    
    pp = ((pred_sign > 0) & (actual_sign > 0)).sum()
    nn = ((pred_sign < 0) & (actual_sign < 0)).sum()
    pn = ((pred_sign > 0) & (actual_sign < 0)).sum()
    np_ = ((pred_sign < 0) & (actual_sign > 0)).sum()
    total = len(df)
    
    print(f"   PP: {pp} ({pp/total*100:.2f}%)")
    print(f"   NN: {nn} ({nn/total*100:.2f}%)")
    print(f"   PN: {pn} ({pn/total*100:.2f}%)")
    print(f"   NP: {np_} ({np_/total*100:.2f}%)")
    
    # 2. DIRECTIONAL ACCURACY - per game approach (proper way)
    print(f"\n2. DIRECTIONAL ACCURACY:")
    
    # Method A: Simple consecutive (wrong - crosses game boundaries)
    pred_dirs = np.sign(np.diff(pred))
    actual_dirs = np.sign(np.diff(actual))
    dir_acc_simple = (pred_dirs == actual_dirs).mean()
    print(f"   Method A (simple, may cross games): {dir_acc_simple*100:.2f}%")
    
    # Method B: Per-game calculation (correct)
    dir_accs = []
    for game in df[game_col].unique():
        game_df = df[df[game_col] == game].sort_values('minute_start')
        if len(game_df) < 2:
            continue
        g_pred = game_df['prediction_value'].values
        g_actual = game_df['actual_value'].values
        g_pred_dirs = np.sign(np.diff(g_pred))
        g_actual_dirs = np.sign(np.diff(g_actual))
        if len(g_pred_dirs) > 0:
            dir_accs.extend((g_pred_dirs == g_actual_dirs).tolist())
    
    dir_acc_per_game = np.mean(dir_accs) if dir_accs else 0
    print(f"   Method B (per-game): {dir_acc_per_game*100:.2f}%")
    
    return {
        'sign_agreement': sign_agreement,
        'dir_acc_simple': dir_acc_simple,
        'dir_acc_per_game': dir_acc_per_game,
        'pp': pp, 'nn': nn, 'pn': pn, 'np': np_
    }

def calculate_differential(df, name, game_col='game_id', home_col='is_home'):
    """Calculate differential sign accuracy"""
    print(f"\n3. DIFFERENTIAL SIGN ACCURACY ({name}):")
    
    if home_col not in df.columns:
        # Original data - need to identify home/away differently
        # In original, team name indicates home (first) vs away (second)
        print(f"   Cannot calculate - missing home indicator column")
        return None
    
    # Get home and away predictions per window
    home = df[df[home_col] == True][['match_id', 'minute_start', 'prediction_value', 'actual_value']].copy()
    away = df[df[home_col] == False][['match_id', 'minute_start', 'prediction_value', 'actual_value']].copy()
    
    home.columns = ['match_id', 'minute_start', 'pred_home', 'actual_home']
    away.columns = ['match_id', 'minute_start', 'pred_away', 'actual_away']
    
    merged = pd.merge(home, away, on=['match_id', 'minute_start'])
    merged = merged.dropna()
    
    print(f"   Paired windows: {len(merged)}")
    
    merged['pred_diff'] = merged['pred_home'] - merged['pred_away']
    merged['actual_diff'] = merged['actual_home'] - merged['actual_away']
    
    # Filter non-zero
    non_zero = merged[(merged['pred_diff'] != 0) & (merged['actual_diff'] != 0)]
    
    print(f"   Non-zero pairs: {len(non_zero)}")
    
    pred_diff_sign = np.sign(non_zero['pred_diff'].values)
    actual_diff_sign = np.sign(non_zero['actual_diff'].values)
    
    diff_accuracy = (pred_diff_sign == actual_diff_sign).mean()
    
    diff_pp = int(((pred_diff_sign > 0) & (actual_diff_sign > 0)).sum())
    diff_nn = int(((pred_diff_sign < 0) & (actual_diff_sign < 0)).sum())
    diff_pn = int(((pred_diff_sign > 0) & (actual_diff_sign < 0)).sum())
    diff_np = int(((pred_diff_sign < 0) & (actual_diff_sign > 0)).sum())
    
    print(f"   Differential Accuracy: {diff_accuracy*100:.2f}%")
    print(f"   PP: {diff_pp} ({diff_pp/len(non_zero)*100:.2f}%)")
    print(f"   NN: {diff_nn} ({diff_nn/len(non_zero)*100:.2f}%)")
    print(f"   PN: {diff_pn} ({diff_pn/len(non_zero)*100:.2f}%)")
    print(f"   NP: {diff_np} ({diff_np/len(non_zero)*100:.2f}%)")
    
    return {
        'accuracy': diff_accuracy,
        'pp': diff_pp, 'nn': diff_nn, 'pn': diff_pn, 'np': diff_np,
        'total': len(non_zero)
    }

# Calculate for original data
print("\n" + "="*70)
print("ORIGINAL DATA (hardcoded in dashboard: 81.61%, 71.11%, 67.35%)")
print("="*70)
orig_metrics = calculate_all_metrics(orig_clean, "ORIGINAL", game_col='game_id')

# Calculate for period-separated data
print("\n" + "="*70)
print("PERIOD-SEPARATED DATA")
print("="*70)
new_metrics = calculate_all_metrics(new_clean, "PERIOD-SEPARATED", game_col='match_id')

# Differential for period-separated only (has is_home column)
diff_metrics = calculate_differential(new_clean, "PERIOD-SEPARATED", game_col='match_id', home_col='is_home')

print("\n" + "="*70)
print("SUMMARY COMPARISON")
print("="*70)

print(f"\nMetric                    | Original (Dashboard) | Period-Separated")
print("-" * 65)
print(f"Sign Agreement            | 67.35% (hardcoded)   | {new_metrics['sign_agreement']*100:.2f}%")
print(f"Directional (simple)      | 81.61% (hardcoded)   | {new_metrics['dir_acc_simple']*100:.2f}%")
print(f"Directional (per-game)    | N/A                  | {new_metrics['dir_acc_per_game']*100:.2f}%")
if diff_metrics:
    print(f"Differential Sign         | 71.11% (hardcoded)   | {diff_metrics['accuracy']*100:.2f}%")

print("\n" + "="*70)
print("NOTE: Dashboard uses 'Method A' (simple) for Directional Accuracy")
print("      which may cross game boundaries - this is the same approach")
print("      as the original analysis.")
print("="*70)

