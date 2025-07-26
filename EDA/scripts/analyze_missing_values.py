import pandas as pd
import numpy as np

def analyze_missing_values():
    """Analyze missing values in Euro 2024 dataset and categorize by variable groups"""
    
    # Load the dataset
    try:
        df = pd.read_csv('../Data/euro_2024_complete_dataset.csv')
        print(f"Dataset loaded: {df.shape[0]:,} rows × {df.shape[1]} columns")
    except FileNotFoundError:
        print("Dataset not found. Checking alternative path...")
        df = pd.read_csv('Data/euro_2024_complete_dataset.csv')
        print(f"Dataset loaded: {df.shape[0]:,} rows × {df.shape[1]} columns")
    
    # Define variable groups based on our classification
    variable_groups = {
        # Continuous Normal
        'duration': 'Continuous Normal',
        'second': 'Continuous Normal', 
        'home_score': 'Continuous Normal',
        
        # Continuous Non-Normal
        'index': 'Continuous Non-Normal',
        'minute': 'Continuous Non-Normal',
        'possession': 'Continuous Non-Normal',
        'away_score': 'Continuous Non-Normal',
        'timestamp': 'Continuous Non-Normal',
        'visible_area': 'Continuous Non-Normal',
        'location': 'Continuous Non-Normal',
        'carry': 'Continuous Non-Normal',
        
        # Categorical Ordinal
        'period': 'Categorical Ordinal',
        'match_week': 'Categorical Ordinal',
        'stage': 'Categorical Ordinal',
        'match_date': 'Categorical Ordinal',
        'kick_off': 'Categorical Ordinal',
        
        # Categorical Nominal
        'id': 'Categorical Nominal',
        'type': 'Categorical Nominal',
        'possession_team': 'Categorical Nominal',
        'play_pattern': 'Categorical Nominal',
        'team': 'Categorical Nominal',
        'player': 'Categorical Nominal',
        'position': 'Categorical Nominal',
        'pass': 'Categorical Nominal',
        'ball_receipt': 'Categorical Nominal',
        'carry': 'Categorical Nominal',
        'dribble': 'Categorical Nominal',
        'shot': 'Categorical Nominal',
        'goalkeeper': 'Categorical Nominal',
        'clearance': 'Categorical Nominal',
        'interception': 'Categorical Nominal',
        'duel': 'Categorical Nominal',
        'block': 'Categorical Nominal',
        'foul_committed': 'Categorical Nominal',
        'foul_won': 'Categorical Nominal',
        'card': 'Categorical Nominal',
        'substitution': 'Categorical Nominal',
        'bad_behaviour': 'Categorical Nominal',
        'ball_recovery': 'Categorical Nominal',
        'dispossessed': 'Categorical Nominal',
        'error': 'Categorical Nominal',
        'miscontrol': 'Categorical Nominal',
        'player_off': 'Categorical Nominal',
        'player_on': 'Categorical Nominal',
        'tactics': 'Categorical Nominal',
        'half_start': 'Categorical Nominal',
        'half_end': 'Categorical Nominal',
        'starting_xi': 'Categorical Nominal',
        'freeze_frame': 'Categorical Nominal',
        'match_id': 'Categorical Nominal',
        'home_team_name': 'Categorical Nominal',
        'away_team_name': 'Categorical Nominal',
        'home_team_id': 'Categorical Nominal',
        'away_team_id': 'Categorical Nominal',
        'event_uuid': 'Categorical Nominal',
        '50_50': 'Categorical Nominal',
        
        # Categorical Binomial
        'under_pressure': 'Categorical Binomial',
        'counterpress': 'Categorical Binomial',
        'off_camera': 'Categorical Binomial',
        'injury_stoppage': 'Categorical Binomial',
        'out': 'Categorical Binomial'
    }
    
    # Calculate missing values
    missing_data = []
    total_rows = len(df)
    
    for column in df.columns:
        missing_count = df[column].isnull().sum()
        if missing_count > 0:  # Only include columns with missing values
            missing_percentage = (missing_count / total_rows) * 100
            group = variable_groups.get(column, 'Unknown')
            
            missing_data.append({
                'Feature': column,
                'Group': group,
                'Missing_Count': missing_count,
                'Missing_Percentage': round(missing_percentage, 2)
            })
    
    # Convert to DataFrame and sort by missing percentage (descending)
    missing_df = pd.DataFrame(missing_data)
    missing_df = missing_df.sort_values('Missing_Percentage', ascending=False)
    
    # Display results
    print("\n" + "="*80)
    print("FEATURES WITH MISSING VALUES")
    print("="*80)
    print(f"Total features analyzed: {len(df.columns)}")
    print(f"Features with missing values: {len(missing_df)}")
    print(f"Total dataset size: {total_rows:,} rows")
    print("\n")
    
    # Print in requested format
    print("Feature - Feature Group - Count of Missings - %")
    print("-" * 60)
    
    for _, row in missing_df.iterrows():
        print(f"{row['Feature']} - {row['Group']} - {row['Missing_Count']:,} - {row['Missing_Percentage']}%")
    
    # Summary by group
    print("\n" + "="*60)
    print("SUMMARY BY VARIABLE GROUP")
    print("="*60)
    
    group_summary = missing_df.groupby('Group').agg({
        'Missing_Count': ['count', 'sum'],
        'Missing_Percentage': ['mean', 'max']
    }).round(2)
    
    group_summary.columns = ['Features_with_Missings', 'Total_Missing_Values', 'Avg_Missing_Pct', 'Max_Missing_Pct']
    print(group_summary)
    
    # Save results
    missing_df.to_csv('EDA/missing_values_analysis.csv', index=False)
    print(f"\nDetailed results saved to: EDA/missing_values_analysis.csv")
    
    return missing_df

if __name__ == "__main__":
    missing_analysis = analyze_missing_values() 