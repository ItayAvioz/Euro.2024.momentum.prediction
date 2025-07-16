import pandas as pd

df = pd.read_csv('specs/Euro_2024_Enhanced_Data_Documentation.csv')
print(f'✅ Enhanced Documentation Complete!')
print(f'📊 Total columns documented: {len(df)}')
print(f'📁 Files analyzed: {list(df["source"].unique())}')
print(f'📈 Breakdown by file:')
for source in df["source"].unique():
    count = len(df[df["source"] == source])
    print(f'   - {source}: {count} columns')

print(f'\n🔍 Data Quality Summary:')
print(f'   - Files with 0% nulls: {len(df[df["null_percentage"] == "0.00%"])} columns')
print(f'   - Files with some nulls: {len(df[df["null_percentage"] != "0.00%"])} columns')

print(f'\n📋 New Enhanced Columns Added:')
print(f'   ✓ null_percentage - Shows % of missing values')
print(f'   ✓ data_examples - Real examples from each column')
print(f'   ✓ common_values_top5 - Top 5 values with percentages')
print(f'   ✓ key_connections - How files connect together')
print(f'   ✓ unit_measure - Proper StatsBomb units')
print(f'   ✓ notes - Additional StatsBomb context')

print(f'\n📄 Output: specs/Euro_2024_Enhanced_Data_Documentation.csv') 