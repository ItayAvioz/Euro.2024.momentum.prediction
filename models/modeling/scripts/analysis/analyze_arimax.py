import pandas as pd

# Load ARIMAX results
df = pd.read_csv('../outputs/predictions/arimax_predictions.csv')

print("🚀 ARIMAX ANALYSIS SUMMARY")
print("=" * 50)

# Overall summary
print(f"Total predictions: {len(df):,}")
print(f"Model types: {df['model_type'].unique()}")
print(f"Games: {df['game_id'].nunique()}")
print(f"Teams: {df['team'].nunique()}")

print("\n📊 PERFORMANCE BY MODEL TYPE:")
print("-" * 40)

for model_type in df['model_type'].unique():
    subset = df[df['model_type'] == model_type]
    print(f"\n{model_type}:")
    print(f"  Predictions: {len(subset):,}")
    print(f"  Average MSE: {subset['mse'].mean():.4f}")
    print(f"  Average Adjusted R²: {subset['adjusted_r2'].mean():.4f}")
    print(f"  Average Directional Accuracy: {subset['directional_accuracy'].mean():.4f}")
    if 'has_exog' in subset.columns:
        exog_count = subset['has_exog'].sum()
        print(f"  With Exogenous Variables: {exog_count}/{len(subset)}")

print("\n🎯 ARIMAX SPECIFIC ANALYSIS:")
print("-" * 35)

arimax_results = df[df['model_type'] == 'momentum_to_change_arimax']
if len(arimax_results) > 0:
    print(f"ARIMAX Predictions: {len(arimax_results):,}")
    print(f"MSE: {arimax_results['mse'].mean():.4f}")
    print(f"Adjusted R²: {arimax_results['adjusted_r2'].mean():.4f}")
    print(f"Directional Accuracy: {arimax_results['directional_accuracy'].mean():.4f}")
    print(f"All use exogenous vars: {arimax_results['has_exog'].all()}")
    
    print("\nSample ARIMAX predictions:")
    sample = arimax_results[['team', 'minutes_prediction', 'prediction_value', 'actual_value']].head(10)
    print(sample.to_string(index=False))
    
    # Compare with regular change model
    regular_change = df[df['model_type'] == 'change_to_change']
    print(f"\n📈 COMPARISON: ARIMAX vs Regular Change Model")
    print(f"ARIMAX MSE: {arimax_results['mse'].mean():.4f}")
    print(f"Regular Change MSE: {regular_change['mse'].mean():.4f}")
    print(f"ARIMAX Dir. Acc.: {arimax_results['directional_accuracy'].mean():.4f}")
    print(f"Regular Change Dir. Acc.: {regular_change['directional_accuracy'].mean():.4f}")
    
    improvement_mse = ((regular_change['mse'].mean() - arimax_results['mse'].mean()) / regular_change['mse'].mean()) * 100
    improvement_dir = ((arimax_results['directional_accuracy'].mean() - regular_change['directional_accuracy'].mean()) / regular_change['directional_accuracy'].mean()) * 100
    
    print(f"\n💡 IMPROVEMENTS:")
    print(f"MSE improvement: {improvement_mse:.2f}%")
    print(f"Directional Accuracy improvement: {improvement_dir:.2f}%")
else:
    print("❌ No ARIMAX results found!")
