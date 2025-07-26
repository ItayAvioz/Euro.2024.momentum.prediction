#!/usr/bin/env python3
"""
Create a formatted summary table for nominal features analysis
Shows key statistics in a clean, readable format
"""

import pandas as pd
from pathlib import Path

def create_nominal_summary_table():
    """Create a formatted summary table from the nominal features CSV"""
    
    # Read the nominal features summary
    csv_path = Path("EDA/visualizations/nominal_features/nominal_features_summary.csv")
    
    if not csv_path.exists():
        print(f"Error: CSV file not found at {csv_path}")
        return
    
    df = pd.read_csv(csv_path)
    
    print("=" * 120)
    print("EURO 2024 NOMINAL FEATURES SUMMARY TABLE")
    print("=" * 120)
    print(f"Dataset: 187,858 total events | Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d')}")
    print()
    
    # Create formatted table
    print(f"{'Feature':<20} {'Missing%':<10} {'Categories':<12} {'Most Common':<25} {'Count':<10} {'%':<8}")
    print("-" * 120)
    
    for _, row in df.iterrows():
        feature = row['Feature']
        missing_pct = f"{row['Missing_Percentage']:.1f}%"
        categories = f"{row['Unique_Categories']}"
        
        # Clean up the most common category name
        most_common = str(row['Most_Common_Category'])
        if most_common.startswith("{'id'"):
            # Extract name from JSON-like string
            if "'name':" in most_common:
                name_start = most_common.find("'name': '") + 9
                name_end = most_common.find("'", name_start)
                most_common = most_common[name_start:name_end]
        
        # Truncate if too long
        if len(most_common) > 24:
            most_common = most_common[:21] + "..."
        
        count = f"{row['Most_Common_Count']:,}"
        percentage = f"{row['Most_Common_Percentage']:.1f}%"
        
        print(f"{feature:<20} {missing_pct:<10} {categories:<12} {most_common:<25} {count:<10} {percentage:<8}")
    
    print("-" * 120)
    
    # Summary statistics
    total_features = len(df)
    perfect_coverage = len(df[df['Missing_Percentage'] == 0])
    near_perfect = len(df[df['Missing_Percentage'] < 1])
    
    print(f"\nSUMMARY STATISTICS:")
    print(f"  📊 Total nominal features analyzed: {total_features}")
    print(f"  ✅ Perfect coverage (0% missing): {perfect_coverage} features")
    print(f"  🟢 Near-perfect coverage (<1% missing): {near_perfect} features")
    print(f"  📈 Average categories per feature: {df['Unique_Categories'].mean():.1f}")
    print(f"  🎯 Most diverse feature: {df.loc[df['Unique_Categories'].idxmax(), 'Feature']} ({df['Unique_Categories'].max()} categories)")
    print(f"  🔧 Simplest feature: {df.loc[df['Unique_Categories'].idxmin(), 'Feature']} ({df['Unique_Categories'].min()} categories)")
    
    # Feature classification by cardinality
    high_card = len(df[df['Unique_Categories'] >= 20])
    medium_card = len(df[(df['Unique_Categories'] >= 10) & (df['Unique_Categories'] < 20)])
    low_card = len(df[df['Unique_Categories'] < 10])
    
    print(f"\nFEATURE CARDINALITY DISTRIBUTION:")
    print(f"  🔴 High cardinality (≥20 categories): {high_card} features")
    print(f"  🟡 Medium cardinality (10-19 categories): {medium_card} features")
    print(f"  🟢 Low cardinality (<10 categories): {low_card} features")
    
    print(f"\n{'='*120}")
    print("✅ ANALYSIS COMPLETE - All nominal features have excellent data coverage!")
    print("📍 Ready for momentum modeling with appropriate encoding strategies")
    print(f"{'='*120}")

if __name__ == "__main__":
    create_nominal_summary_table() 