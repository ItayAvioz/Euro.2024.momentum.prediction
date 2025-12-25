#!/usr/bin/env python3
"""
Euro 2024 Goal Timing Analysis
Extracts real goal timing data from the complete dataset
Focuses on periods 1+2 only, avoids double-counting own goals
"""

import pandas as pd
import ast
import numpy as np
from collections import defaultdict, Counter

def safe_eval_dict(val):
    """Safely evaluate dictionary strings"""
    if pd.isna(val) or val == '':
        return {}
    try:
        if isinstance(val, str):
            return ast.literal_eval(val)
        return val if isinstance(val, dict) else {}
    except:
        return {}

def main():
    print('🔍 ANALYZING EURO 2024 GOAL TIMING DATA...')
    print('=' * 60)
    
    # Load the dataset
    try:
        df = pd.read_csv('../Data/euro_2024_complete_dataset.csv', encoding='utf-8', low_memory=False)
        print(f'✅ Dataset loaded: {len(df):,} total events')
    except:
        try:
            df = pd.read_csv('../Data/euro_2024_complete_dataset.csv', encoding='latin-1', low_memory=False)
            print(f'✅ Dataset loaded: {len(df):,} total events')
        except Exception as e:
            print(f'❌ Error loading dataset: {e}')
            return
    
    # Parse type column to extract event types
    print('\n📊 PARSING EVENT TYPES...')
    df['type_parsed'] = df['type'].apply(safe_eval_dict)
    df['event_name'] = df['type_parsed'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else '')
    
    # Filter for periods 1 and 2 only
    df_periods = df[df['period'].isin([1, 2])].copy()
    print(f'📅 Events in periods 1+2: {len(df_periods):,}')
    
    # Find shot goals (avoid double counting)
    shot_goals = df_periods[
        (df_periods['event_name'] == 'Shot') & 
        (df_periods['shot'].notna())
    ].copy()
    
    print(f'🎯 Shot events in periods 1+2: {len(shot_goals)}')
    
    # Parse shot data to find goals
    shot_goals['shot_parsed'] = shot_goals['shot'].apply(safe_eval_dict)
    shot_goals['shot_outcome'] = shot_goals['shot_parsed'].apply(
        lambda x: x.get('outcome', {}).get('name', '') if isinstance(x, dict) else ''
    )
    
    # Filter for actual goals
    actual_shot_goals = shot_goals[shot_goals['shot_outcome'] == 'Goal'].copy()
    print(f'⚽ Shot goals in periods 1+2: {len(actual_shot_goals)}')
    
    # Find own goals (only "Own Goal Against" to avoid double counting)
    own_goals = df_periods[df_periods['event_name'] == 'Own Goal Against'].copy()
    print(f'🥅 Own goals in periods 1+2: {len(own_goals)}')
    
    # Combine all goals
    all_goals = []
    
    # Add shot goals
    for _, row in actual_shot_goals.iterrows():
        all_goals.append({
            'match_id': row['match_id'],
            'period': row['period'],
            'minute': row['minute'],
            'second': row.get('second', 0),
            'type': 'Shot Goal',
            'team': row['team'],
            'home_team': row['home_team_name'],
            'away_team': row['away_team_name'],
            'match_date': row.get('match_date', ''),
            'stage': row.get('stage', '')
        })
    
    # Add own goals
    for _, row in own_goals.iterrows():
        all_goals.append({
            'match_id': row['match_id'],
            'period': row['period'],
            'minute': row['minute'],
            'second': row.get('second', 0),
            'type': 'Own Goal',
            'team': row['team'],
            'home_team': row['home_team_name'],
            'away_team': row['away_team_name'],
            'match_date': row.get('match_date', ''),
            'stage': row.get('stage', '')
        })
    
    # Convert to DataFrame
    goals_df = pd.DataFrame(all_goals)
    
    print(f'\n🎯 TOTAL GOALS ANALYSIS:')
    print(f'Total goals in periods 1+2: {len(goals_df)}')
    print(f'Period 1 goals: {len(goals_df[goals_df["period"] == 1])}')
    print(f'Period 2 goals: {len(goals_df[goals_df["period"] == 2])}')
    print(f'Shot goals: {len(goals_df[goals_df["type"] == "Shot Goal"])}')
    print(f'Own goals: {len(goals_df[goals_df["type"] == "Own Goal"])}')
    
    # Create 5-minute intervals with stoppage time handling
    def get_5min_interval(period, minute):
        """Get 5-minute interval, adding stoppage time to last interval of each half"""
        if period == 1:
            if minute <= 5:
                return '1-5'
            elif minute <= 10:
                return '6-10'
            elif minute <= 15:
                return '11-15'
            elif minute <= 20:
                return '16-20'
            elif minute <= 25:
                return '21-25'
            elif minute <= 30:
                return '26-30'
            elif minute <= 35:
                return '31-35'
            elif minute <= 40:
                return '36-40'
            else:  # 41+ includes stoppage time
                return '41-45+'
        else:  # period == 2
            if minute <= 50:
                return '46-50'
            elif minute <= 55:
                return '51-55'
            elif minute <= 60:
                return '56-60'
            elif minute <= 65:
                return '61-65'
            elif minute <= 70:
                return '66-70'
            elif minute <= 75:
                return '71-75'
            elif minute <= 80:
                return '76-80'
            elif minute <= 85:
                return '81-85'
            else:  # 86+ includes stoppage time
                return '86-90+'
    
    # Apply interval calculation
    goals_df['interval_5min'] = goals_df.apply(
        lambda row: get_5min_interval(row['period'], row['minute']), axis=1
    )
    
    # Count goals per 5-minute interval
    interval_counts = goals_df['interval_5min'].value_counts()
    
    # Define the correct order for intervals
    interval_order = ['1-5', '6-10', '11-15', '16-20', '21-25', '26-30', '31-35', '36-40', '41-45+',
                     '46-50', '51-55', '56-60', '61-65', '66-70', '71-75', '76-80', '81-85', '86-90+']
    
    print(f'\n📊 GOALS BY 5-MINUTE INTERVALS:')
    print('=' * 40)
    
    total_goals = 0
    first_half_goals = 0
    second_half_goals = 0
    
    for interval in interval_order:
        count = interval_counts.get(interval, 0)
        total_goals += count
        
        if interval.startswith(('1-', '6-', '11-', '16-', '21-', '26-', '31-', '36-', '41-')):
            first_half_goals += count
            half_marker = '(1st Half)'
        else:
            second_half_goals += count
            half_marker = '(2nd Half)'
        
        print(f'{interval:>8}: {count:2d} goals {half_marker}')
    
    print('=' * 40)
    print(f'First Half Total: {first_half_goals} goals')
    print(f'Second Half Total: {second_half_goals} goals')
    print(f'Grand Total: {total_goals} goals')
    
    # Save detailed CSV
    goals_csv = goals_df[['match_id', 'home_team', 'away_team', 'match_date', 'stage', 
                         'period', 'minute', 'second', 'type', 'team', 'interval_5min']].copy()
    goals_csv = goals_csv.sort_values(['match_date', 'match_id', 'period', 'minute', 'second'])
    
    csv_filename = 'euro_2024_goal_timing_analysis.csv'
    goals_csv.to_csv(csv_filename, index=False)
    print(f'\n💾 SAVED: {csv_filename}')
    print(f'📄 Contains {len(goals_csv)} goals with detailed timing information')
    
    # Create summary for dashboard update
    goals_5min_list = [interval_counts.get(interval, 0) for interval in interval_order]
    
    print(f'\n🎯 DASHBOARD UPDATE DATA:')
    print('=' * 40)
    print('goals_5 = [' + ', '.join(map(str, goals_5min_list)) + ']')
    print(f'# Total: {sum(goals_5min_list)} goals ({first_half_goals} + {second_half_goals})')
    
    # Show matches with most goals per interval
    print(f'\n📈 INTERVAL ANALYSIS:')
    print('=' * 40)
    
    for interval in interval_order:
        interval_goals = goals_df[goals_df['interval_5min'] == interval]
        if len(interval_goals) > 0:
            matches_with_goals = interval_goals.groupby('match_id').size()
            max_goals_in_match = matches_with_goals.max() if len(matches_with_goals) > 0 else 0
            print(f'{interval:>8}: {len(interval_goals):2d} goals total, max {max_goals_in_match} in single match')

if __name__ == '__main__':
    main()
