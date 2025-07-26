import pandas as pd
import numpy as np
import ast

print("=== CONSECUTIVE EVENTS & TURNOVER ANALYSIS (FIXED) ===")
print("Using possession and possession_team columns to track ball control patterns")

# Load the data
matches = pd.read_csv('../Data/matches_complete.csv')
events = pd.read_csv('../Data/events_complete.csv')

print(f"Total matches: {len(matches)}")
print(f"Total events: {len(events)}")

# ===== METHODOLOGY EXPLANATION =====
print("\n" + "="*80)
print("CALCULATION METHODOLOGY")
print("="*80)

print("CONSECUTIVE EVENTS CALCULATION:")
print("• Using 'possession' column - groups events into possession sequences")
print("• Each possession number represents continuous control by one team")
print("• Consecutive events = count of events within same possession")
print("• When possession number changes = new possession sequence starts")

print("\nTURNOVER CALCULATION:")
print("• Using 'possession_team' column to identify which team has possession")
print("• Turnover = when possession_team changes from one team to another")
print("• Count turnovers per team per match/period")
print("• Parse team dictionary strings to extract team names")

# Function to extract team name from dictionary string
def extract_team_name(team_dict_str):
    try:
        if pd.isna(team_dict_str):
            return None
        team_dict = ast.literal_eval(team_dict_str)
        return team_dict.get('name', None)
    except:
        return None

# Extract team names
print("\n" + "="*80)
print("DATA PREPROCESSING")
print("="*80)

print("Extracting team names from dictionary strings...")
events['team_name'] = events['team'].apply(extract_team_name)
events['possession_team_name'] = events['possession_team'].apply(extract_team_name)

print("Sample extracted names:")
sample = events[['possession', 'possession_team_name', 'team_name']].head(10)
print(sample)

print(f"\nExtracted team names:")
print(f"• Unique teams in 'team_name': {events['team_name'].nunique()}")
print(f"• Unique teams in 'possession_team_name': {events['possession_team_name'].nunique()}")

# Create analysis for each match
consecutive_turnover_analysis = []

for _, match in matches.iterrows():
    match_id = match['match_id']
    home_team = match['home_team_name']
    away_team = match['away_team_name']
    stage = match['stage']
    
    # Get match events
    match_events = events[events['match_id'] == match_id].copy()
    match_events = match_events.dropna(subset=['possession'])  # Remove events without possession info
    
    if len(match_events) == 0:
        continue
    
    # Sort by period, minute, second to ensure proper order
    match_events = match_events.sort_values(['period', 'minute', 'second'])
    
    # Analyze by period
    for period in [1, 2]:
        period_events = match_events[match_events['period'] == period]
        
        if len(period_events) == 0:
            continue
        
        # ===== CONSECUTIVE EVENTS ANALYSIS =====
        # Group by possession to find consecutive events
        possession_groups = period_events.groupby('possession')
        
        home_consecutive_events = []
        away_consecutive_events = []
        
        for possession_id, possession_events in possession_groups:
            # Count events per team in this possession
            team_counts = possession_events['team_name'].value_counts()
            
            for team, count in team_counts.items():
                if team == home_team:
                    home_consecutive_events.append(count)
                elif team == away_team:
                    away_consecutive_events.append(count)
        
        # ===== TURNOVER ANALYSIS =====
        # Track possession changes using possession_team_name
        possession_team_events = period_events.dropna(subset=['possession_team_name'])
        
        if len(possession_team_events) == 0:
            home_turnovers = away_turnovers = 0
        else:
            # Find possession changes
            home_turnovers = 0
            away_turnovers = 0
            
            prev_team = None
            for _, event in possession_team_events.iterrows():
                current_team = event['possession_team_name']
                if prev_team is not None and prev_team != current_team:
                    # Turnover occurred - previous team lost possession
                    if prev_team == home_team:
                        home_turnovers += 1
                    elif prev_team == away_team:
                        away_turnovers += 1
                prev_team = current_team
        
        # Calculate statistics
        home_avg_consecutive = np.mean(home_consecutive_events) if home_consecutive_events else 0
        home_max_consecutive = max(home_consecutive_events) if home_consecutive_events else 0
        home_total_possessions = len(home_consecutive_events)
        
        away_avg_consecutive = np.mean(away_consecutive_events) if away_consecutive_events else 0
        away_max_consecutive = max(away_consecutive_events) if away_consecutive_events else 0
        away_total_possessions = len(away_consecutive_events)
        
        # Add home team data
        consecutive_turnover_analysis.append({
            'match_id': match_id,
            'team': home_team,
            'opponent': away_team,
            'stage': stage,
            'period': period,
            'avg_consecutive_events': home_avg_consecutive,
            'max_consecutive_events': home_max_consecutive,
            'total_possessions': home_total_possessions,
            'turnovers': home_turnovers,
            'turnover_rate': home_turnovers / home_total_possessions if home_total_possessions > 0 else 0,
            'match_date': match['match_date']
        })
        
        # Add away team data
        consecutive_turnover_analysis.append({
            'match_id': match_id,
            'team': away_team,
            'opponent': home_team,
            'stage': stage,
            'period': period,
            'avg_consecutive_events': away_avg_consecutive,
            'max_consecutive_events': away_max_consecutive,
            'total_possessions': away_total_possessions,
            'turnovers': away_turnovers,
            'turnover_rate': away_turnovers / away_total_possessions if away_total_possessions > 0 else 0,
            'match_date': match['match_date']
        })

# Convert to DataFrame
analysis_df = pd.DataFrame(consecutive_turnover_analysis)

print(f"\n" + "="*80)
print("ANALYSIS RESULTS")
print("="*80)
print(f"Successfully analyzed {len(analysis_df)} team-period performances")
print(f"From {len(analysis_df)//4} matches")

# ===== OVERALL SUMMARY STATISTICS =====
print("\n" + "="*80)
print("OVERALL SUMMARY STATISTICS")
print("="*80)

print("CONSECUTIVE EVENTS:")
print(f"Average consecutive events per possession: {analysis_df['avg_consecutive_events'].mean():.2f}")
print(f"Median consecutive events per possession: {analysis_df['avg_consecutive_events'].median():.2f}")
print(f"Max consecutive events in a possession: {analysis_df['max_consecutive_events'].max():.0f}")
print(f"Average max consecutive per team-period: {analysis_df['max_consecutive_events'].mean():.2f}")

print(f"\nPOSSESSIONS:")
print(f"Average possessions per team-period: {analysis_df['total_possessions'].mean():.1f}")
print(f"Median possessions per team-period: {analysis_df['total_possessions'].median():.1f}")
print(f"Max possessions in a period: {analysis_df['total_possessions'].max():.0f}")

print(f"\nTURNOVERS:")
print(f"Average turnovers per team-period: {analysis_df['turnovers'].mean():.2f}")
print(f"Median turnovers per team-period: {analysis_df['turnovers'].median():.2f}")
print(f"Max turnovers in a period: {analysis_df['turnovers'].max():.0f}")
print(f"Average turnover rate: {analysis_df['turnover_rate'].mean():.3f} (turnovers per possession)")

# ===== PERIOD COMPARISON =====
print("\n" + "="*80)
print("PERIOD COMPARISON")
print("="*80)

for period in [1, 2]:
    period_data = analysis_df[analysis_df['period'] == period]
    period_name = "First Half" if period == 1 else "Second Half"
    
    print(f"\n{period_name} ({len(period_data)} performances):")
    print(f"  Avg consecutive events: {period_data['avg_consecutive_events'].mean():.2f}")
    print(f"  Max consecutive events: {period_data['max_consecutive_events'].mean():.2f}")
    print(f"  Avg possessions: {period_data['total_possessions'].mean():.1f}")
    print(f"  Avg turnovers: {period_data['turnovers'].mean():.2f}")
    print(f"  Turnover rate: {period_data['turnover_rate'].mean():.3f}")

# Calculate period differences
fh_data = analysis_df[analysis_df['period'] == 1]
sh_data = analysis_df[analysis_df['period'] == 2]

print(f"\nPERIOD DIFFERENCES (Second Half vs First Half):")
print(f"  Consecutive events: {sh_data['avg_consecutive_events'].mean() - fh_data['avg_consecutive_events'].mean():+.2f}")
print(f"  Max consecutive: {sh_data['max_consecutive_events'].mean() - fh_data['max_consecutive_events'].mean():+.2f}")
print(f"  Possessions: {sh_data['total_possessions'].mean() - fh_data['total_possessions'].mean():+.1f}")
print(f"  Turnovers: {sh_data['turnovers'].mean() - fh_data['turnovers'].mean():+.2f}")
print(f"  Turnover rate: {sh_data['turnover_rate'].mean() - fh_data['turnover_rate'].mean():+.3f}")

# ===== STAGE ANALYSIS =====
print("\n" + "="*80)
print("ANALYSIS BY STAGE")
print("="*80)

for stage in analysis_df['stage'].unique():
    stage_data = analysis_df[analysis_df['stage'] == stage]
    
    print(f"\n{stage.upper()} ({len(stage_data)} performances):")
    print(f"  Avg consecutive events: {stage_data['avg_consecutive_events'].mean():.2f}")
    print(f"  Max consecutive events: {stage_data['max_consecutive_events'].mean():.2f}")
    print(f"  Avg possessions: {stage_data['total_possessions'].mean():.1f}")
    print(f"  Avg turnovers: {stage_data['turnovers'].mean():.2f}")
    print(f"  Turnover rate: {stage_data['turnover_rate'].mean():.3f}")

# ===== STAGE + PERIOD ANALYSIS =====
print("\n" + "="*80)
print("DETAILED STAGE + PERIOD ANALYSIS")
print("="*80)

for stage in analysis_df['stage'].unique():
    print(f"\n{stage.upper()}:")
    stage_data = analysis_df[analysis_df['stage'] == stage]
    
    for period in [1, 2]:
        period_data = stage_data[stage_data['period'] == period]
        period_name = "First Half" if period == 1 else "Second Half"
        
        if len(period_data) > 0:
            print(f"  {period_name}: {period_data['avg_consecutive_events'].mean():.2f} consecutive, " +
                  f"{period_data['total_possessions'].mean():.1f} possessions, " +
                  f"{period_data['turnovers'].mean():.2f} turnovers")

# ===== EXTREME VALUES ANALYSIS =====
print("\n" + "="*80)
print("EXTREME VALUES ANALYSIS")
print("="*80)

print("HIGHEST CONSECUTIVE EVENTS:")
top_consecutive = analysis_df.nlargest(10, 'max_consecutive_events')
for _, row in top_consecutive.iterrows():
    print(f"  {row['team']} vs {row['opponent']} ({row['stage']}, Period {row['period']}): {row['max_consecutive_events']:.0f} events")

print(f"\nMOST TURNOVERS:")
top_turnovers = analysis_df.nlargest(10, 'turnovers')
for _, row in top_turnovers.iterrows():
    print(f"  {row['team']} vs {row['opponent']} ({row['stage']}, Period {row['period']}): {row['turnovers']:.0f} turnovers")

print(f"\nHIGHEST TURNOVER RATES:")
top_turnover_rates = analysis_df.nlargest(10, 'turnover_rate')
for _, row in top_turnover_rates.iterrows():
    print(f"  {row['team']} vs {row['opponent']} ({row['stage']}, Period {row['period']}): {row['turnover_rate']:.3f} rate")

print(f"\nMOST POSSESSIONS:")
top_possessions = analysis_df.nlargest(10, 'total_possessions')
for _, row in top_possessions.iterrows():
    print(f"  {row['team']} vs {row['opponent']} ({row['stage']}, Period {row['period']}): {row['total_possessions']:.0f} possessions")

# ===== CORRELATION ANALYSIS =====
print("\n" + "="*80)
print("CORRELATION ANALYSIS")
print("="*80)

correlations = analysis_df[['avg_consecutive_events', 'max_consecutive_events', 'total_possessions', 'turnovers', 'turnover_rate']].corr()

print("CORRELATION MATRIX:")
print(correlations.round(3))

print(f"\nKEY CORRELATIONS:")
print(f"Consecutive events vs Possessions: {correlations.loc['avg_consecutive_events', 'total_possessions']:.3f}")
print(f"Consecutive events vs Turnovers: {correlations.loc['avg_consecutive_events', 'turnovers']:.3f}")
print(f"Possessions vs Turnovers: {correlations.loc['total_possessions', 'turnovers']:.3f}")
print(f"Possessions vs Turnover Rate: {correlations.loc['total_possessions', 'turnover_rate']:.3f}")

# ===== SAVE RESULTS =====
print("\n" + "="*80)
print("SAVING RESULTS")
print("="*80)

analysis_df.to_csv('consecutive_events_turnover_analysis_fixed.csv', index=False)
print("File saved: consecutive_events_turnover_analysis_fixed.csv")

print(f"\n=== CONSECUTIVE EVENTS & TURNOVER ANALYSIS COMPLETE ===")
print(f"Key Finding: Average {analysis_df['avg_consecutive_events'].mean():.2f} consecutive events per possession")
print(f"Turnover Impact: {analysis_df['turnovers'].mean():.2f} turnovers per team-period")
print(f"Ball Control: {analysis_df['total_possessions'].mean():.1f} possessions per team-period") 