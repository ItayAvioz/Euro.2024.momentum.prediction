#!/usr/bin/env python3
"""
Create Complete Nominal Features Summary
Combines original nominal features with complex features analysis
"""

import pandas as pd
from pathlib import Path

def create_complete_nominal_summary():
    """Create comprehensive summary combining all nominal features"""
    
    output_dir = Path("EDA/visualizations/nominal_features")
    
    # Read original and updated summaries
    original_csv = output_dir / 'nominal_features_summary.csv'
    updated_csv = output_dir / 'nominal_features_summary_updated.csv'
    
    if not original_csv.exists():
        print(f"Error: Original CSV not found at {original_csv}")
        return
    
    # Load data
    original_df = pd.read_csv(original_csv)
    
    if updated_csv.exists():
        updated_df = pd.read_csv(updated_csv)
        # Combine dataframes
        complete_df = pd.concat([original_df, updated_df], ignore_index=True)
    else:
        complete_df = original_df
    
    # Sort by missing percentage (ascending)
    complete_df = complete_df.sort_values('Missing_Percentage')
    
    # Add Description column if not present
    if 'Description' not in complete_df.columns:
        complete_df['Description'] = ''
        
        # Add descriptions for original features
        descriptions = {
            'type': 'Event type classifications (JSON objects)',
            'event_type': 'Simplified event type strings',
            'possession_team': 'Team in possession (JSON objects)',
            'team': 'Team performing event (JSON objects)',
            'home_team_name': 'Home team name strings',
            'away_team_name': 'Away team name strings',
            'home_team_id': 'Home team numeric IDs',
            'away_team_id': 'Away team numeric IDs',
            'play_pattern': 'How possession started (JSON objects)',
            'position': 'Player positions (JSON objects)',
            'match_id': 'Unique match identifiers',
            'stadium': 'Venue information (JSON objects)',
            'referee': 'Match officials (JSON objects)'
        }
        
        for feature, desc in descriptions.items():
            mask = complete_df['Feature'] == feature
            complete_df.loc[mask, 'Description'] = desc
    
    # Save complete summary
    complete_csv_path = output_dir / 'nominal_features_complete_summary.csv'
    complete_df.to_csv(complete_csv_path, index=False)
    
    # Create detailed table display
    print("=" * 140)
    print("EURO 2024 COMPLETE NOMINAL FEATURES ANALYSIS")
    print("=" * 140)
    print(f"Dataset: 187,858 total events | Total Features: {len(complete_df)}")
    print()
    
    # Create formatted table with all features
    print(f"{'Feature':<22} {'Missing%':<10} {'Categories':<12} {'Most Common':<30} {'Count':<12} {'%':<8} {'Type':<15}")
    print("-" * 140)
    
    for _, row in complete_df.iterrows():
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
        if len(most_common) > 29:
            most_common = most_common[:26] + "..."
        
        count = f"{row['Most_Common_Count']:,}"
        percentage = f"{row['Most_Common_Percentage']:.1f}%"
        
        # Determine feature type
        if row['Missing_Percentage'] == 0:
            feature_type = "Perfect"
        elif row['Missing_Percentage'] < 1:
            feature_type = "Near-Perfect"
        elif row['Missing_Percentage'] < 20:
            feature_type = "Good"
        elif row['Missing_Percentage'] < 50:
            feature_type = "Medium"
        else:
            feature_type = "Poor"
        
        print(f"{feature:<22} {missing_pct:<10} {categories:<12} {most_common:<30} {count:<12} {percentage:<8} {feature_type:<15}")
    
    print("-" * 140)
    
    # Comprehensive statistics
    total_features = len(complete_df)
    perfect_coverage = len(complete_df[complete_df['Missing_Percentage'] == 0])
    near_perfect = len(complete_df[complete_df['Missing_Percentage'] < 1])
    good_coverage = len(complete_df[complete_df['Missing_Percentage'] < 20])
    medium_coverage = len(complete_df[(complete_df['Missing_Percentage'] >= 20) & (complete_df['Missing_Percentage'] < 50)])
    poor_coverage = len(complete_df[complete_df['Missing_Percentage'] >= 50])
    
    print(f"\nCOMPREHENSIVE STATISTICS:")
    print(f"  📊 Total nominal features analyzed: {total_features}")
    print(f"  ✅ Perfect coverage (0% missing): {perfect_coverage} features")
    print(f"  🟢 Near-perfect coverage (<1% missing): {near_perfect} features")
    print(f"  🔵 Good coverage (<20% missing): {good_coverage} features")
    print(f"  🟡 Medium coverage (20-50% missing): {medium_coverage} features")
    print(f"  🔴 Poor coverage (≥50% missing): {poor_coverage} features")
    
    # Feature classification by cardinality
    high_card = len(complete_df[complete_df['Unique_Categories'] >= 50])
    medium_high_card = len(complete_df[(complete_df['Unique_Categories'] >= 20) & (complete_df['Unique_Categories'] < 50)])
    medium_card = len(complete_df[(complete_df['Unique_Categories'] >= 10) & (complete_df['Unique_Categories'] < 20)])
    low_card = len(complete_df[complete_df['Unique_Categories'] < 10])
    
    print(f"\nFEATURE CARDINALITY DISTRIBUTION:")
    print(f"  🔴 Very high cardinality (≥50 categories): {high_card} features")
    print(f"  🟠 High cardinality (20-49 categories): {medium_high_card} features")
    print(f"  🟡 Medium cardinality (10-19 categories): {medium_card} features")
    print(f"  🟢 Low cardinality (<10 categories): {low_card} features")
    
    # Momentum modeling recommendations
    print(f"\nMOMENTUM MODELING RECOMMENDATIONS:")
    print(f"  🎯 High Priority (Direct Impact): event_type, type, play_pattern, position")
    print(f"  🎯 Medium Priority (Contextual): team, home/away_team_name, player, related_events")
    print(f"  🎯 Low Priority (Limited Impact): match_id, stadium, referee, pass, freeze_frame")
    
    # Data quality insights
    print(f"\nDATA QUALITY INSIGHTS:")
    excellent_features = complete_df[complete_df['Missing_Percentage'] < 5]['Feature'].tolist()
    problematic_features = complete_df[complete_df['Missing_Percentage'] >= 50]['Feature'].tolist()
    
    print(f"  ✅ Excellent quality ({len(excellent_features)} features): {', '.join(excellent_features[:5])}" + 
          (f" + {len(excellent_features)-5} more" if len(excellent_features) > 5 else ""))
    
    if problematic_features:
        print(f"  ⚠️  Needs attention ({len(problematic_features)} features): {', '.join(problematic_features)}")
    
    print(f"\n{'='*140}")
    print("✅ COMPLETE NOMINAL FEATURES ANALYSIS FINISHED")
    print(f"📁 Complete summary saved: {complete_csv_path}")
    print(f"📊 {len(complete_df)} features analyzed with comprehensive statistics")
    print(f"🚀 Ready for momentum prediction modeling with appropriate encoding strategies")
    print(f"{'='*140}")
    
    return complete_df

def create_feature_categorization():
    """Create categorization of features by momentum modeling priority"""
    
    output_dir = Path("EDA/visualizations/nominal_features")
    complete_csv = output_dir / 'nominal_features_complete_summary.csv'
    
    if not complete_csv.exists():
        print("Complete summary not found. Run main analysis first.")
        return
    
    df = pd.read_csv(complete_csv)
    
    # Categorize features by modeling priority
    high_priority = ['type', 'event_type', 'play_pattern', 'position']
    medium_priority = ['team', 'possession_team', 'home_team_name', 'away_team_name', 'player', 'related_events_count']
    low_priority = ['match_id', 'stadium', 'referee', 'home_team_id', 'away_team_id', 'pass', 'freeze_frame']
    
    # Add priority column
    df['Momentum_Priority'] = 'Unknown'
    for feature in high_priority:
        df.loc[df['Feature'] == feature, 'Momentum_Priority'] = 'High'
    for feature in medium_priority:
        df.loc[df['Feature'] == feature, 'Momentum_Priority'] = 'Medium'
    for feature in low_priority:
        df.loc[df['Feature'] == feature, 'Momentum_Priority'] = 'Low'
    
    # Save categorized version
    categorized_path = output_dir / 'nominal_features_categorized.csv'
    df.to_csv(categorized_path, index=False)
    
    print(f"\nFeature categorization saved: {categorized_path}")
    
    # Print priority summary
    print("\nFEATURE PRIORITY SUMMARY:")
    for priority in ['High', 'Medium', 'Low']:
        priority_features = df[df['Momentum_Priority'] == priority]['Feature'].tolist()
        print(f"  {priority} Priority ({len(priority_features)} features): {', '.join(priority_features)}")

if __name__ == "__main__":
    complete_df = create_complete_nominal_summary()
    create_feature_categorization() 