#!/usr/bin/env python3
"""
Group Stage Substitution Analysis by Matchday
Analyzes substitution patterns for Matchdays 1, 2, and 3 of the Group Stage
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def load_data():
    """Load the required datasets"""
    print("Loading data...")
    
    # Load matches and events data
    matches = pd.read_csv('Data/matches_complete.csv')
    events = pd.read_csv('Data/events_complete.csv')
    
    print(f"Loaded {len(matches)} matches and {len(events)} events")
    return matches, events

def identify_group_stage_matches(matches):
    """Identify Group Stage matches and categorize by matchday"""
    print("\nIdentifying Group Stage matches...")
    
    # Filter for Group Stage
    group_matches = matches[matches['stage'] == 'Group Stage'].copy()
    
    # Convert match_date to datetime for sorting
    group_matches['match_date'] = pd.to_datetime(group_matches['match_date'])
    
    # Sort by date to identify matchdays
    group_matches = group_matches.sort_values('match_date')
    
    print(f"Found {len(group_matches)} Group Stage matches")
    print(f"Date range: {group_matches['match_date'].min().date()} to {group_matches['match_date'].max().date()}")
    
    # Group Stage structure: 6 groups × 3 matchdays = 18 matches per matchday, but only 12 unique dates
    # Each date has multiple matches, so we need to identify the 3 distinct matchday periods
    
    # Get unique dates and assign matchdays
    unique_dates = sorted(group_matches['match_date'].dt.date.unique())
    print(f"Unique match dates: {len(unique_dates)}")
    
    # Euro 2024 Group Stage structure:
    # Matchday 1: June 14-18
    # Matchday 2: June 19-23  
    # Matchday 3: June 24-26
    
    matchday_mapping = {}
    for i, date in enumerate(unique_dates):
        if date.day <= 18:  # June 14-18
            matchday_mapping[date] = 1
        elif date.day <= 23:  # June 19-23
            matchday_mapping[date] = 2
        else:  # June 24-26
            matchday_mapping[date] = 3
    
    # Add matchday column
    group_matches['matchday'] = group_matches['match_date'].dt.date.map(matchday_mapping)
    
    # Verify matchday distribution
    matchday_counts = group_matches['matchday'].value_counts().sort_index()
    print(f"\nMatchday distribution:")
    for md, count in matchday_counts.items():
        print(f"  Matchday {md}: {count} matches")
    
    return group_matches

def analyze_substitutions(events, group_matches):
    """Analyze substitution patterns by matchday"""
    print("\nAnalyzing substitutions...")
    
    # Get substitution events - type column contains dictionaries
    sub_events = events[events['type'].astype(str).str.contains('Substitution', na=False)].copy()
    print(f"Found {len(sub_events)} total substitution events")
    
    # Merge with match information
    sub_events = sub_events.merge(
        group_matches[['match_id', 'matchday', 'home_team_name', 'away_team_name']],
        on='match_id',
        how='inner'
    )
    
    print(f"Found {len(sub_events)} Group Stage substitution events")
    
    # Analyze by matchday
    results = {}
    
    for matchday in [1, 2, 3]:
        md_subs = sub_events[sub_events['matchday'] == matchday]
        md_matches = group_matches[group_matches['matchday'] == matchday]
        
        # Basic stats
        total_subs = len(md_subs)
        total_matches = len(md_matches)
        subs_per_match = total_subs / total_matches if total_matches > 0 else 0
        
        # Timing analysis
        timing_stats = {
            'mean_minute': md_subs['minute'].mean() if len(md_subs) > 0 else 0,
            'median_minute': md_subs['minute'].median() if len(md_subs) > 0 else 0,
            'earliest': md_subs['minute'].min() if len(md_subs) > 0 else 0,
            'latest': md_subs['minute'].max() if len(md_subs) > 0 else 0
        }
        
        # By period
        period_breakdown = md_subs['period'].value_counts().to_dict() if len(md_subs) > 0 else {}
        
        # By team activity (subs per team per match)
        team_subs = {}
        for _, match in md_matches.iterrows():
            match_subs = md_subs[md_subs['match_id'] == match['match_id']]
            home_subs = len(match_subs[match_subs['team'] == match['home_team_name']])
            away_subs = len(match_subs[match_subs['team'] == match['away_team_name']])
            
            team_subs[match['match_id']] = {
                'home': home_subs,
                'away': away_subs,
                'total': home_subs + away_subs
            }
        
        # Average subs per team per match
        if team_subs:
            avg_home_subs = np.mean([ts['home'] for ts in team_subs.values()])
            avg_away_subs = np.mean([ts['away'] for ts in team_subs.values()])
            max_team_subs = max([max(ts['home'], ts['away']) for ts in team_subs.values()])
            min_team_subs = min([min(ts['home'], ts['away']) for ts in team_subs.values()])
        else:
            avg_home_subs = avg_away_subs = max_team_subs = min_team_subs = 0
        
        results[matchday] = {
            'total_substitutions': total_subs,
            'total_matches': total_matches,
            'subs_per_match': subs_per_match,
            'timing': timing_stats,
            'period_breakdown': period_breakdown,
            'team_stats': {
                'avg_home_subs_per_match': avg_home_subs,
                'avg_away_subs_per_match': avg_away_subs,
                'max_team_subs_in_match': max_team_subs,
                'min_team_subs_in_match': min_team_subs
            },
            'match_details': team_subs
        }
    
    return results, sub_events

def create_visualizations(results, sub_events):
    """Create comprehensive visualizations"""
    print("\nCreating visualizations...")
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Figure 1: Overall substitution trends
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Group Stage Substitution Analysis by Matchday', fontsize=16, fontweight='bold')
    
    # 1. Substitutions per match
    matchdays = [1, 2, 3]
    subs_per_match = [results[md]['subs_per_match'] for md in matchdays]
    total_subs = [results[md]['total_substitutions'] for md in matchdays]
    
    bars1 = ax1.bar(matchdays, subs_per_match, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
    ax1.set_title('Substitutions per Match by Matchday', fontweight='bold')
    ax1.set_xlabel('Matchday')
    ax1.set_ylabel('Substitutions per Match')
    ax1.set_ylim(0, max(subs_per_match) * 1.1)
    
    # Add value labels on bars
    for i, (bar, value) in enumerate(zip(bars1, subs_per_match)):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                f'{value:.2f}', ha='center', va='bottom', fontweight='bold')
    
    # 2. Total substitutions
    bars2 = ax2.bar(matchdays, total_subs, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
    ax2.set_title('Total Substitutions by Matchday', fontweight='bold')
    ax2.set_xlabel('Matchday')
    ax2.set_ylabel('Total Substitutions')
    
    for i, (bar, value) in enumerate(zip(bars2, total_subs)):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                f'{value}', ha='center', va='bottom', fontweight='bold')
    
    # 3. Substitution timing (mean minute)
    mean_minutes = [results[md]['timing']['mean_minute'] for md in matchdays]
    bars3 = ax3.bar(matchdays, mean_minutes, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
    ax3.set_title('Average Substitution Timing by Matchday', fontweight='bold')
    ax3.set_xlabel('Matchday')
    ax3.set_ylabel('Average Minute')
    
    for i, (bar, value) in enumerate(zip(bars3, mean_minutes)):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'{value:.1f}\'', ha='center', va='bottom', fontweight='bold')
    
    # 4. Team substitution patterns
    home_subs = [results[md]['team_stats']['avg_home_subs_per_match'] for md in matchdays]
    away_subs = [results[md]['team_stats']['avg_away_subs_per_match'] for md in matchdays]
    
    x = np.arange(len(matchdays))
    width = 0.35
    
    bars4a = ax4.bar(x - width/2, home_subs, width, label='Home Teams', color='#FF6B6B', alpha=0.8)
    bars4b = ax4.bar(x + width/2, away_subs, width, label='Away Teams', color='#4ECDC4', alpha=0.8)
    
    ax4.set_title('Average Team Substitutions per Match', fontweight='bold')
    ax4.set_xlabel('Matchday')
    ax4.set_ylabel('Substitutions per Team per Match')
    ax4.set_xticks(x)
    ax4.set_xticklabels(matchdays)
    ax4.legend()
    
    # Add value labels
    for bars in [bars4a, bars4b]:
        for bar in bars:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f'{height:.2f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('EDA/group_stage_substitution_patterns.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Figure 2: Detailed timing analysis
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle('Substitution Timing Analysis', fontsize=16, fontweight='bold')
    
    # 1. Distribution of substitution minutes by matchday
    for matchday in [1, 2, 3]:
        md_subs = sub_events[sub_events['matchday'] == matchday]
        if len(md_subs) > 0:
            ax1.hist(md_subs['minute'], bins=15, alpha=0.6, 
                    label=f'Matchday {matchday}', density=True)
    
    ax1.set_title('Distribution of Substitution Minutes', fontweight='bold')
    ax1.set_xlabel('Minute')
    ax1.set_ylabel('Density')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Box plot of substitution timing
    timing_data = []
    timing_labels = []
    for matchday in [1, 2, 3]:
        md_subs = sub_events[sub_events['matchday'] == matchday]
        if len(md_subs) > 0:
            timing_data.append(md_subs['minute'].values)
            timing_labels.append(f'Matchday {matchday}')
    
    ax2.boxplot(timing_data, labels=timing_labels)
    ax2.set_title('Substitution Timing Distribution', fontweight='bold')
    ax2.set_ylabel('Minute')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('EDA/substitution_timing_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def print_detailed_results(results):
    """Print comprehensive substitution analysis results"""
    print("\n" + "="*80)
    print("GROUP STAGE SUBSTITUTION ANALYSIS BY MATCHDAY")
    print("="*80)
    
    for matchday in [1, 2, 3]:
        data = results[matchday]
        print(f"\nMATCHDAY {matchday}")
        print("-" * 40)
        print(f"Total Matches: {data['total_matches']}")
        print(f"Total Substitutions: {data['total_substitutions']}")
        print(f"Substitutions per Match: {data['subs_per_match']:.2f}")
        
        print(f"\nTiming Analysis:")
        print(f"  Average Minute: {data['timing']['mean_minute']:.1f}'")
        print(f"  Median Minute: {data['timing']['median_minute']:.1f}'")
        print(f"  Earliest: {data['timing']['earliest']:.0f}'")
        print(f"  Latest: {data['timing']['latest']:.0f}'")
        
        print(f"\nPeriod Breakdown:")
        for period, count in data['period_breakdown'].items():
            print(f"  Period {period}: {count} substitutions")
        
        print(f"\nTeam Statistics:")
        print(f"  Avg Home Team Subs per Match: {data['team_stats']['avg_home_subs_per_match']:.2f}")
        print(f"  Avg Away Team Subs per Match: {data['team_stats']['avg_away_subs_per_match']:.2f}")
        print(f"  Max Team Subs in a Match: {data['team_stats']['max_team_subs_in_match']}")
        print(f"  Min Team Subs in a Match: {data['team_stats']['min_team_subs_in_match']}")
    
    # Comparative analysis
    print(f"\n" + "="*40)
    print("COMPARATIVE ANALYSIS")
    print("="*40)
    
    md1_subs = results[1]['subs_per_match']
    md2_subs = results[2]['subs_per_match']
    md3_subs = results[3]['subs_per_match']
    
    print(f"\nSubstitution Trends:")
    if md1_subs > 0:
        print(f"  MD1 → MD2: {((md2_subs - md1_subs) / md1_subs * 100):+.1f}% change")
        print(f"  MD2 → MD3: {((md3_subs - md2_subs) / md2_subs * 100):+.1f}% change" if md2_subs > 0 else "  MD2 → MD3: No MD2 data for comparison")
        print(f"  MD1 → MD3: {((md3_subs - md1_subs) / md1_subs * 100):+.1f}% change")
    else:
        print(f"  MD1: {md1_subs:.2f} → MD2: {md2_subs:.2f} → MD3: {md3_subs:.2f} subs per match")
    
    md1_time = results[1]['timing']['mean_minute']
    md2_time = results[2]['timing']['mean_minute']
    md3_time = results[3]['timing']['mean_minute']
    
    print(f"\nTiming Trends:")
    print(f"  MD1 avg: {md1_time:.1f}' → MD2 avg: {md2_time:.1f}' → MD3 avg: {md3_time:.1f}'")
    
    if md1_time > 0:
        print(f"  MD1 → MD2: {((md2_time - md1_time) / md1_time * 100):+.1f}% change")
        print(f"  MD2 → MD3: {((md3_time - md2_time) / md2_time * 100):+.1f}% change")
        print(f"  MD1 → MD3: {((md3_time - md1_time) / md1_time * 100):+.1f}% change")

def save_summary_csv(results):
    """Save substitution analysis summary to CSV"""
    print("\nSaving summary to CSV...")
    
    # Create summary DataFrame
    summary_data = []
    
    for matchday in [1, 2, 3]:
        data = results[matchday]
        summary_data.append({
            'Matchday': matchday,
            'Total_Matches': data['total_matches'],
            'Total_Substitutions': data['total_substitutions'],
            'Subs_Per_Match': round(data['subs_per_match'], 2),
            'Avg_Minute': round(data['timing']['mean_minute'], 1),
            'Median_Minute': round(data['timing']['median_minute'], 1),
            'Earliest_Sub': int(data['timing']['earliest']),
            'Latest_Sub': int(data['timing']['latest']),
            'Avg_Home_Subs': round(data['team_stats']['avg_home_subs_per_match'], 2),
            'Avg_Away_Subs': round(data['team_stats']['avg_away_subs_per_match'], 2),
            'Max_Team_Subs': data['team_stats']['max_team_subs_in_match'],
            'Min_Team_Subs': data['team_stats']['min_team_subs_in_match']
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv('EDA/group_stage_substitution_summary.csv', index=False)
    
    # Also save detailed match-by-match data
    detailed_data = []
    for matchday in [1, 2, 3]:
        for match_id, match_subs in results[matchday]['match_details'].items():
            detailed_data.append({
                'Matchday': matchday,
                'Match_ID': match_id,
                'Home_Subs': match_subs['home'],
                'Away_Subs': match_subs['away'],
                'Total_Subs': match_subs['total']
            })
    
    detailed_df = pd.DataFrame(detailed_data)
    detailed_df.to_csv('EDA/group_stage_substitution_details.csv', index=False)
    
    print("Saved:")
    print("  - EDA/group_stage_substitution_summary.csv")
    print("  - EDA/group_stage_substitution_details.csv")

def main():
    """Main analysis function"""
    print("GROUP STAGE SUBSTITUTION ANALYSIS")
    print("=" * 50)
    
    # Load data
    matches, events = load_data()
    
    # Identify Group Stage matches by matchday
    group_matches = identify_group_stage_matches(matches)
    
    # Analyze substitutions
    results, sub_events = analyze_substitutions(events, group_matches)
    
    # Print results
    print_detailed_results(results)
    
    # Create visualizations
    create_visualizations(results, sub_events)
    
    # Save CSV summaries
    save_summary_csv(results)
    
    print("\n" + "="*50)
    print("ANALYSIS COMPLETE!")
    print("Check EDA/ directory for visualizations and CSV summaries")

if __name__ == "__main__":
    main() 