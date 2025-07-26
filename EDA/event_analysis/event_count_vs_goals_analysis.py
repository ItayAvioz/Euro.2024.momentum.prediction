import pandas as pd
import numpy as np

print("=== EVENT COUNT vs GOALS ANALYSIS ===")
print("Checking if event volume reflects goal scoring by period and stage")

# Load the data
matches = pd.read_csv('../Data/matches_complete.csv')
events = pd.read_csv('../Data/events_complete.csv')

print(f"Total matches: {len(matches)}")
print(f"Total events: {len(events)}")

# Create analysis for each team in each game
event_goal_analysis = []

for _, match in matches.iterrows():
    match_id = match['match_id']
    
    # Get match info
    team_a = match['home_team_name']
    team_b = match['away_team_name']
    stage = match['stage']
    
    # Get final scores
    team_a_score = int(match['home_score']) if pd.notna(match['home_score']) else 0
    team_b_score = int(match['away_score']) if pd.notna(match['away_score']) else 0
    
    # Get match events
    match_events = events[events['match_id'] == match_id].copy()
    
    if len(match_events) == 0:
        continue
    
    # Separate by period
    first_half_events = match_events[match_events['period'] == 1]
    second_half_events = match_events[match_events['period'] == 2]
    
    # Count goals by period for each team
    # Look for shot events that resulted in goals
    fh_team_a_goals = 0
    fh_team_b_goals = 0
    sh_team_a_goals = 0
    sh_team_b_goals = 0
    
    # First half goals
    fh_shots = first_half_events[first_half_events['shot'].notna()]
    for _, shot_event in fh_shots.iterrows():
        try:
            shot_data = eval(shot_event['shot']) if isinstance(shot_event['shot'], str) else shot_event['shot']
            if isinstance(shot_data, dict) and shot_data.get('outcome', {}).get('name') == 'Goal':
                if shot_event['team_name'] == team_a:
                    fh_team_a_goals += 1
                elif shot_event['team_name'] == team_b:
                    fh_team_b_goals += 1
        except:
            continue
    
    # Second half goals
    sh_shots = second_half_events[second_half_events['shot'].notna()]
    for _, shot_event in sh_shots.iterrows():
        try:
            shot_data = eval(shot_event['shot']) if isinstance(shot_event['shot'], str) else shot_event['shot']
            if isinstance(shot_data, dict) and shot_data.get('outcome', {}).get('name') == 'Goal':
                if shot_event['team_name'] == team_a:
                    sh_team_a_goals += 1
                elif shot_event['team_name'] == team_b:
                    sh_team_b_goals += 1
        except:
            continue
    
    # Count events by team and period
    fh_team_a_events = len(first_half_events[first_half_events['team_name'] == team_a])
    fh_team_b_events = len(first_half_events[first_half_events['team_name'] == team_b])
    sh_team_a_events = len(second_half_events[second_half_events['team_name'] == team_a])
    sh_team_b_events = len(second_half_events[second_half_events['team_name'] == team_b])
    
    # Add Team A data
    event_goal_analysis.append({
        'match_id': match_id,
        'team': team_a,
        'opponent': team_b,
        'stage': stage,
        'fh_events': fh_team_a_events,
        'fh_goals': fh_team_a_goals,
        'sh_events': sh_team_a_events,
        'sh_goals': sh_team_a_goals,
        'total_events': fh_team_a_events + sh_team_a_events,
        'total_goals': team_a_score,
        'fh_events_per_goal': fh_team_a_events / fh_team_a_goals if fh_team_a_goals > 0 else float('inf'),
        'sh_events_per_goal': sh_team_a_events / sh_team_a_goals if sh_team_a_goals > 0 else float('inf'),
        'total_events_per_goal': (fh_team_a_events + sh_team_a_events) / team_a_score if team_a_score > 0 else float('inf'),
        'match_date': match['match_date']
    })
    
    # Add Team B data
    event_goal_analysis.append({
        'match_id': match_id,
        'team': team_b,
        'opponent': team_a,
        'stage': stage,
        'fh_events': fh_team_b_events,
        'fh_goals': fh_team_b_goals,
        'sh_events': sh_team_b_events,
        'sh_goals': sh_team_b_goals,
        'total_events': fh_team_b_events + sh_team_b_events,
        'total_goals': team_b_score,
        'fh_events_per_goal': fh_team_b_events / fh_team_b_goals if fh_team_b_goals > 0 else float('inf'),
        'sh_events_per_goal': sh_team_b_events / sh_team_b_goals if sh_team_b_goals > 0 else float('inf'),
        'total_events_per_goal': (fh_team_b_events + sh_team_b_events) / team_b_score if team_b_score > 0 else float('inf'),
        'match_date': match['match_date']
    })

# Convert to DataFrame
analysis_df = pd.DataFrame(event_goal_analysis)

print(f"\nSuccessfully analyzed {len(analysis_df)} team performances across {len(analysis_df)//2} games")

# ===== OVERALL EVENT-GOAL RELATIONSHIP =====
print("\n" + "="*100)
print("OVERALL EVENT COUNT vs GOALS RELATIONSHIP")
print("="*100)

# Filter out teams that scored no goals for meaningful analysis
scoring_teams = analysis_df[analysis_df['total_goals'] > 0]
fh_scoring_teams = analysis_df[analysis_df['fh_goals'] > 0]
sh_scoring_teams = analysis_df[analysis_df['sh_goals'] > 0]

print(f"TOTAL GAME ANALYSIS ({len(scoring_teams)} scoring performances):")
print(f"Average events per goal: {scoring_teams['total_events_per_goal'].mean():.1f}")
print(f"Median events per goal: {scoring_teams['total_events_per_goal'].median():.1f}")
print(f"Min events per goal: {scoring_teams['total_events_per_goal'].min():.1f}")
print(f"Max events per goal: {scoring_teams['total_events_per_goal'].max():.1f}")

if len(fh_scoring_teams) > 0:
    print(f"\nFIRST HALF ANALYSIS ({len(fh_scoring_teams)} scoring performances):")
    print(f"Average events per goal: {fh_scoring_teams['fh_events_per_goal'].mean():.1f}")
    print(f"Median events per goal: {fh_scoring_teams['fh_events_per_goal'].median():.1f}")
    print(f"Min events per goal: {fh_scoring_teams['fh_events_per_goal'].min():.1f}")
    print(f"Max events per goal: {fh_scoring_teams['fh_events_per_goal'].max():.1f}")

if len(sh_scoring_teams) > 0:
    print(f"\nSECOND HALF ANALYSIS ({len(sh_scoring_teams)} scoring performances):")
    print(f"Average events per goal: {sh_scoring_teams['sh_events_per_goal'].mean():.1f}")
    print(f"Median events per goal: {sh_scoring_teams['sh_events_per_goal'].median():.1f}")
    print(f"Min events per goal: {sh_scoring_teams['sh_events_per_goal'].min():.1f}")
    print(f"Max events per goal: {sh_scoring_teams['sh_events_per_goal'].max():.1f}")

# ===== PERIOD COMPARISON =====
print("\n" + "="*100)
print("FIRST HALF vs SECOND HALF EFFICIENCY")
print("="*100)

# Calculate period efficiency
fh_total_events = analysis_df['fh_events'].sum()
fh_total_goals = analysis_df['fh_goals'].sum()
sh_total_events = analysis_df['sh_events'].sum()
sh_total_goals = analysis_df['sh_goals'].sum()

fh_efficiency = fh_total_events / fh_total_goals if fh_total_goals > 0 else float('inf')
sh_efficiency = sh_total_events / sh_total_goals if sh_total_goals > 0 else float('inf')

print(f"FIRST HALF TOURNAMENT TOTALS:")
print(f"Total events: {fh_total_events:,}")
print(f"Total goals: {fh_total_goals}")
print(f"Events per goal: {fh_efficiency:.1f}")

print(f"\nSECOND HALF TOURNAMENT TOTALS:")
print(f"Total events: {sh_total_events:,}")
print(f"Total goals: {sh_total_goals}")
print(f"Events per goal: {sh_efficiency:.1f}")

efficiency_difference = fh_efficiency - sh_efficiency
efficiency_percent = ((sh_efficiency - fh_efficiency) / fh_efficiency) * 100

print(f"\nEFFICIENCY COMPARISON:")
print(f"Difference: {efficiency_difference:.1f} events per goal")
print(f"Second half is {efficiency_percent:+.1f}% more/less efficient than first half")

# ===== STAGE ANALYSIS =====
print("\n" + "="*100)
print("EVENT-GOAL EFFICIENCY BY STAGE")
print("="*100)

stage_analysis = {}
for stage in analysis_df['stage'].unique():
    stage_data = analysis_df[analysis_df['stage'] == stage]
    stage_scoring = stage_data[stage_data['total_goals'] > 0]
    
    if len(stage_scoring) > 0:
        stage_analysis[stage] = {
            'performances': len(stage_scoring),
            'avg_events_per_goal': stage_scoring['total_events_per_goal'].mean(),
            'median_events_per_goal': stage_scoring['total_events_per_goal'].median(),
            'total_events': stage_data['total_events'].sum(),
            'total_goals': stage_data['total_goals'].sum(),
            'stage_efficiency': stage_data['total_events'].sum() / stage_data['total_goals'].sum() if stage_data['total_goals'].sum() > 0 else float('inf')
        }

# Display stage analysis
for stage, stats in stage_analysis.items():
    print(f"\n{stage.upper()}:")
    print(f"  Scoring performances: {stats['performances']}")
    print(f"  Average events per goal: {stats['avg_events_per_goal']:.1f}")
    print(f"  Median events per goal: {stats['median_events_per_goal']:.1f}")
    print(f"  Stage efficiency: {stats['stage_efficiency']:.1f} events per goal")

# ===== PERIOD BY STAGE ANALYSIS =====
print("\n" + "="*100)
print("PERIOD EFFICIENCY BY STAGE")
print("="*100)

for stage in analysis_df['stage'].unique():
    stage_data = analysis_df[analysis_df['stage'] == stage]
    
    stage_fh_events = stage_data['fh_events'].sum()
    stage_fh_goals = stage_data['fh_goals'].sum()
    stage_sh_events = stage_data['sh_events'].sum()
    stage_sh_goals = stage_data['sh_goals'].sum()
    
    stage_fh_efficiency = stage_fh_events / stage_fh_goals if stage_fh_goals > 0 else float('inf')
    stage_sh_efficiency = stage_sh_events / stage_sh_goals if stage_sh_goals > 0 else float('inf')
    
    print(f"\n{stage.upper()}:")
    print(f"  First Half: {stage_fh_events:,} events, {stage_fh_goals} goals, {stage_fh_efficiency:.1f} events/goal")
    print(f"  Second Half: {stage_sh_events:,} events, {stage_sh_goals} goals, {stage_sh_efficiency:.1f} events/goal")
    
    if stage_fh_goals > 0 and stage_sh_goals > 0:
        stage_efficiency_diff = ((stage_sh_efficiency - stage_fh_efficiency) / stage_fh_efficiency) * 100
        print(f"  Second half efficiency: {stage_efficiency_diff:+.1f}% vs first half")

# ===== EXTREME EFFICIENCY CASES =====
print("\n" + "="*100)
print("EXTREME EFFICIENCY CASES")
print("="*100)

print("MOST EFFICIENT SCORING (Fewest events per goal):")
most_efficient = scoring_teams.nsmallest(10, 'total_events_per_goal')
for _, team in most_efficient.iterrows():
    print(f"  {team['team']} vs {team['opponent']} ({team['stage']}): {team['total_events']:.0f} events, {team['total_goals']} goals = {team['total_events_per_goal']:.1f} events/goal")

print("\nLEAST EFFICIENT SCORING (Most events per goal):")
least_efficient = scoring_teams.nlargest(10, 'total_events_per_goal')
for _, team in least_efficient.iterrows():
    print(f"  {team['team']} vs {team['opponent']} ({team['stage']}): {team['total_events']:.0f} events, {team['total_goals']} goals = {team['total_events_per_goal']:.1f} events/goal")

# ===== CORRELATION ANALYSIS =====
print("\n" + "="*100)
print("EVENT-GOAL CORRELATION ANALYSIS")
print("="*100)

# Calculate correlations
total_correlation = analysis_df['total_events'].corr(analysis_df['total_goals'])
fh_correlation = analysis_df['fh_events'].corr(analysis_df['fh_goals'])
sh_correlation = analysis_df['sh_events'].corr(analysis_df['sh_goals'])

print(f"CORRELATION BETWEEN EVENTS AND GOALS:")
print(f"Total game: {total_correlation:.3f}")
print(f"First half: {fh_correlation:.3f}")
print(f"Second half: {sh_correlation:.3f}")

# Stage correlations
print(f"\nCORRELATION BY STAGE:")
for stage in analysis_df['stage'].unique():
    stage_data = analysis_df[analysis_df['stage'] == stage]
    stage_correlation = stage_data['total_events'].corr(stage_data['total_goals'])
    print(f"  {stage}: {stage_correlation:.3f}")

# ===== HIGH vs LOW EVENT VOLUME ANALYSIS =====
print("\n" + "="*100)
print("HIGH vs LOW EVENT VOLUME GOAL SCORING")
print("="*100)

# Define high/low event volume thresholds
event_median = analysis_df['total_events'].median()
high_volume = analysis_df[analysis_df['total_events'] > event_median]
low_volume = analysis_df[analysis_df['total_events'] <= event_median]

print(f"Event volume threshold: {event_median:.0f} events")
print(f"\nHIGH EVENT VOLUME TEAMS (>{event_median:.0f} events):")
print(f"  Performances: {len(high_volume)}")
print(f"  Average goals: {high_volume['total_goals'].mean():.2f}")
print(f"  Goals per performance: {high_volume['total_goals'].sum() / len(high_volume):.2f}")

print(f"\nLOW EVENT VOLUME TEAMS (<={event_median:.0f} events):")
print(f"  Performances: {len(low_volume)}")
print(f"  Average goals: {low_volume['total_goals'].mean():.2f}")
print(f"  Goals per performance: {low_volume['total_goals'].sum() / len(low_volume):.2f}")

# ===== SAVE RESULTS =====
print("\n" + "="*100)
print("SAVING RESULTS")
print("="*100)

analysis_df.to_csv('event_count_vs_goals_analysis.csv', index=False)
print("File saved: event_count_vs_goals_analysis.csv")

print(f"\n=== EVENT COUNT vs GOALS ANALYSIS COMPLETE ===")
print(f"Key Finding: Tournament average of {scoring_teams['total_events_per_goal'].mean():.1f} events needed per goal")
print(f"Period Finding: Second half {efficiency_percent:+.1f}% efficiency difference vs first half")
print(f"Correlation: {total_correlation:.3f} correlation between total events and goals") 