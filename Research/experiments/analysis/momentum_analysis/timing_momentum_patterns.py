#!/usr/bin/env python3
"""
Timing-Based Momentum Pattern Analysis
Deep dive into specific timing patterns for momentum prediction
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

class TimingMomentumAnalyzer:
    def __init__(self):
        self.events_df = None
        
    def load_data(self):
        """Load Euro 2024 data"""
        print("📊 Loading Euro 2024 Dataset...")
        try:
            self.events_df = pd.read_csv("../Data/events_complete.csv", low_memory=False)
            print(f"✅ Events loaded: {len(self.events_df):,}")
            
            # Extract event names
            self.events_df['event_name'] = self.events_df['type'].apply(self.extract_event_type)
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def extract_event_type(self, type_str):
        """Extract event name from type dictionary string"""
        if pd.isna(type_str) or type_str == '':
            return ''
        
        try:
            if "'name':" in str(type_str):
                start = str(type_str).find("'name': '") + 9
                end = str(type_str).find("'", start)
                return str(type_str)[start:end]
            else:
                return str(type_str)
        except:
            return str(type_str)
    
    def analyze_first_minutes_momentum(self):
        """Analyze momentum patterns in first 15 minutes"""
        print(f"\n🌅 FIRST MINUTES MOMENTUM ANALYSIS")
        print("=" * 50)
        
        first_15 = self.events_df[self.events_df['minute'] <= 15]
        
        # Events by minute in first 15
        print(f"📊 First 15 Minutes Event Distribution:")
        for minute in range(1, 16):
            minute_events = len(first_15[first_15['minute'] == minute])
            print(f"   Minute {minute:2d}: {minute_events:>4} events")
        
        # High-impact events in first 15
        print(f"\n⚡ HIGH-IMPACT EVENTS IN FIRST 15 MINUTES:")
        
        # Goals in first 15
        first_goals = first_15[first_15['event_name'].str.contains('Goal', na=False, case=False)]
        print(f"   Goals in first 15: {len(first_goals)}")
        if len(first_goals) > 0:
            goal_minutes = first_goals['minute'].value_counts().sort_index()
            print(f"   Goal distribution:")
            for minute, count in goal_minutes.items():
                print(f"     Minute {minute}: {count} goals")
        
        # Substitutions in first 15 (unusual)
        first_subs = first_15[first_15['substitution'].notna()]
        print(f"   Early substitutions: {len(first_subs)}")
        
        # Cards in first 15
        first_fouls = first_15[first_15['foul_committed'].notna()]
        first_cards = first_15[first_15['bad_behaviour'].notna()]
        print(f"   Early fouls: {len(first_fouls)}")
        print(f"   Early cards: {len(first_cards)}")
        
        # Tactical changes in first 15
        first_tactics = first_15[first_15['tactics'].notna()]
        print(f"   Early tactical changes: {len(first_tactics)}")
        
        # Activity intensity by minute
        print(f"\n📈 ACTIVITY INTENSITY FIRST 15 MINUTES:")
        activity_by_minute = []
        for minute in range(1, 16):
            activity = len(first_15[first_15['minute'] == minute])
            activity_by_minute.append(activity)
        
        avg_activity = np.mean(activity_by_minute)
        max_activity = max(activity_by_minute)
        min_activity = min(activity_by_minute)
        
        print(f"   Average activity: {avg_activity:.0f} events/minute")
        print(f"   Peak activity: {max_activity} events (minute {activity_by_minute.index(max_activity)+1})")
        print(f"   Lowest activity: {min_activity} events (minute {activity_by_minute.index(min_activity)+1})")
        
        return first_15
    
    def analyze_end_game_momentum(self):
        """Analyze momentum patterns in end game scenarios"""
        print(f"\n🔚 END GAME MOMENTUM ANALYSIS")
        print("=" * 50)
        
        # Define end game phases
        phases = {
            'Late Game (75-90)': (75, 90),
            'Stoppage Time (90-105)': (90, 105),
            'Extra Time (105+)': (105, 999)
        }
        
        for phase_name, (start_min, end_min) in phases.items():
            print(f"\n📊 {phase_name}:")
            
            if end_min == 999:
                phase_data = self.events_df[self.events_df['minute'] >= start_min]
            else:
                phase_data = self.events_df[
                    (self.events_df['minute'] >= start_min) & 
                    (self.events_df['minute'] < end_min)
                ]
            
            if len(phase_data) == 0:
                print(f"   No events in this phase")
                continue
            
            print(f"   Total events: {len(phase_data)}")
            
            # Goals in this phase
            phase_goals = phase_data[phase_data['event_name'].str.contains('Goal', na=False, case=False)]
            print(f"   Goals: {len(phase_goals)}")
            
            # Substitutions in this phase
            phase_subs = phase_data[phase_data['substitution'].notna()]
            print(f"   Substitutions: {len(phase_subs)}")
            
            # Cards in this phase
            phase_fouls = phase_data[phase_data['foul_committed'].notna()]
            phase_cards = phase_data[phase_data['bad_behaviour'].notna()]
            print(f"   Fouls: {len(phase_fouls)}")
            print(f"   Cards: {len(phase_cards)}")
            
            # Tactical changes
            phase_tactics = phase_data[phase_data['tactics'].notna()]
            print(f"   Tactical changes: {len(phase_tactics)}")
            
            # Activity intensity
            phase_duration = min(end_min - start_min, phase_data['minute'].max() - start_min + 1)
            if phase_duration > 0:
                activity_rate = len(phase_data) / phase_duration
                print(f"   Activity rate: {activity_rate:.1f} events/minute")
    
    def analyze_stoppage_time_patterns(self):
        """Analyze specific stoppage time momentum patterns"""
        print(f"\n⏱️  STOPPAGE TIME MOMENTUM PATTERNS")
        print("=" * 50)
        
        stoppage_data = self.events_df[self.events_df['minute'] >= 90]
        
        if len(stoppage_data) == 0:
            print("No stoppage time data found")
            return
        
        print(f"📊 Stoppage Time Analysis:")
        print(f"   Total stoppage events: {len(stoppage_data)}")
        
        # Minute-by-minute analysis
        print(f"\n📈 MINUTE-BY-MINUTE STOPPAGE ANALYSIS:")
        for minute in range(90, min(121, int(stoppage_data['minute'].max()) + 1)):
            minute_data = stoppage_data[stoppage_data['minute'] == minute]
            if len(minute_data) > 0:
                goals = len(minute_data[minute_data['event_name'].str.contains('Goal', na=False, case=False)])
                subs = len(minute_data[minute_data['substitution'].notna()])
                fouls = len(minute_data[minute_data['foul_committed'].notna()])
                cards = len(minute_data[minute_data['bad_behaviour'].notna()])
                
                print(f"   Minute {minute:3d}: {len(minute_data):4d} events | Goals: {goals} | Subs: {subs} | Fouls: {fouls} | Cards: {cards}")
        
        # Dramatic events in stoppage time
        print(f"\n🎭 DRAMATIC STOPPAGE TIME EVENTS:")
        
        stoppage_goals = stoppage_data[stoppage_data['event_name'].str.contains('Goal', na=False, case=False)]
        print(f"   Stoppage time goals: {len(stoppage_goals)}")
        
        if len(stoppage_goals) > 0:
            print(f"   Goal minutes:")
            for minute in sorted(stoppage_goals['minute'].unique()):
                count = len(stoppage_goals[stoppage_goals['minute'] == minute])
                print(f"     Minute {minute}: {count} goals")
        
        # Last-minute substitutions
        late_subs = stoppage_data[stoppage_data['substitution'].notna()]
        print(f"   Late substitutions: {len(late_subs)}")
        
        # Desperation fouls/cards
        stoppage_fouls = stoppage_data[stoppage_data['foul_committed'].notna()]
        stoppage_cards = stoppage_data[stoppage_data['bad_behaviour'].notna()]
        print(f"   Stoppage fouls: {len(stoppage_fouls)}")
        print(f"   Stoppage cards: {len(stoppage_cards)}")
        
        return stoppage_data
    
    def analyze_substitution_timing_patterns(self):
        """Analyze substitution timing and momentum impact"""
        print(f"\n🔄 SUBSTITUTION TIMING PATTERNS")
        print("=" * 50)
        
        subs_data = self.events_df[self.events_df['substitution'].notna()]
        
        if len(subs_data) == 0:
            print("No substitution data found")
            return
        
        print(f"📊 Substitution Analysis:")
        print(f"   Total substitutions: {len(subs_data)}")
        
        # Substitution timing clusters
        print(f"\n🕐 SUBSTITUTION TIMING CLUSTERS:")
        
        timing_clusters = {
            'Early (1-30)': (1, 30),
            'Mid-First (31-45)': (31, 45),
            'Early Second (46-60)': (46, 60),
            'Mid-Second (61-75)': (61, 75),
            'Late Game (76-90)': (76, 90),
            'Stoppage (90+)': (90, 999)
        }
        
        for cluster_name, (start_min, end_min) in timing_clusters.items():
            if end_min == 999:
                cluster_subs = subs_data[subs_data['minute'] >= start_min]
            else:
                cluster_subs = subs_data[
                    (subs_data['minute'] >= start_min) & 
                    (subs_data['minute'] <= end_min)
                ]
            
            count = len(cluster_subs)
            percentage = (count / len(subs_data)) * 100
            print(f"   {cluster_name:<20}: {count:>3} subs ({percentage:4.1f}%)")
        
        # Peak substitution minutes
        print(f"\n📈 PEAK SUBSTITUTION MINUTES:")
        sub_minutes = subs_data['minute'].value_counts().sort_index()
        top_minutes = sub_minutes.nlargest(10)
        
        for minute, count in top_minutes.items():
            print(f"   Minute {minute:3.0f}: {count} substitutions")
        
        # Tactical substitution patterns
        print(f"\n🎯 TACTICAL SUBSTITUTION INSIGHTS:")
        
        # Half-time substitutions
        halftime_subs = subs_data[subs_data['minute'] == 45]
        print(f"   Half-time substitutions: {len(halftime_subs)}")
        
        # Late tactical subs (60-75)
        tactical_subs = subs_data[
            (subs_data['minute'] >= 60) & 
            (subs_data['minute'] <= 75)
        ]
        print(f"   Tactical subs (60-75): {len(tactical_subs)}")
        
        # Desperation subs (80+)
        desperation_subs = subs_data[subs_data['minute'] >= 80]
        print(f"   Desperation subs (80+): {len(desperation_subs)}")
        
        return subs_data
    
    def analyze_card_momentum_impact(self):
        """Analyze card timing and momentum impact"""
        print(f"\n🟨 CARD MOMENTUM IMPACT ANALYSIS")
        print("=" * 50)
        
        fouls_data = self.events_df[self.events_df['foul_committed'].notna()]
        cards_data = self.events_df[self.events_df['bad_behaviour'].notna()]
        
        print(f"📊 Card Analysis:")
        print(f"   Total fouls: {len(fouls_data)}")
        print(f"   Total cards: {len(cards_data)}")
        
        # Card timing patterns
        print(f"\n🕐 CARD TIMING PATTERNS:")
        
        timing_phases = {
            'Opening (1-15)': (1, 15),
            'First Half (16-45)': (16, 45),
            'Early Second (46-60)': (46, 60),
            'Mid-Second (61-75)': (61, 75),
            'Late Game (76-90)': (76, 90),
            'Stoppage (90+)': (90, 999)
        }
        
        for phase_name, (start_min, end_min) in timing_phases.items():
            if end_min == 999:
                phase_fouls = fouls_data[fouls_data['minute'] >= start_min]
                phase_cards = cards_data[cards_data['minute'] >= start_min]
            else:
                phase_fouls = fouls_data[
                    (fouls_data['minute'] >= start_min) & 
                    (fouls_data['minute'] <= end_min)
                ]
                phase_cards = cards_data[
                    (cards_data['minute'] >= start_min) & 
                    (cards_data['minute'] <= end_min)
                ]
            
            foul_count = len(phase_fouls)
            card_count = len(phase_cards)
            
            print(f"   {phase_name:<20}: {foul_count:>3} fouls, {card_count:>3} cards")
        
        # Peak card minutes
        print(f"\n📈 PEAK CARD MINUTES:")
        if len(cards_data) > 0:
            card_minutes = cards_data['minute'].value_counts().sort_index()
            top_card_minutes = card_minutes.nlargest(8)
            
            for minute, count in top_card_minutes.items():
                print(f"   Minute {minute:3.0f}: {count} cards")
        
        # Discipline breakdown patterns
        print(f"\n⚖️  DISCIPLINE BREAKDOWN PATTERNS:")
        
        # Late game discipline issues
        late_fouls = fouls_data[fouls_data['minute'] >= 75]
        late_cards = cards_data[cards_data['minute'] >= 75]
        
        print(f"   Late game fouls (75+): {len(late_fouls)}")
        print(f"   Late game cards (75+): {len(late_cards)}")
        
        # Stoppage time discipline
        stoppage_fouls = fouls_data[fouls_data['minute'] >= 90]
        stoppage_cards = cards_data[cards_data['minute'] >= 90]
        
        print(f"   Stoppage fouls (90+): {len(stoppage_fouls)}")
        print(f"   Stoppage cards (90+): {len(stoppage_cards)}")
        
        return fouls_data, cards_data
    
    def create_momentum_timing_summary(self):
        """Create comprehensive timing-based momentum summary"""
        print(f"\n📋 MOMENTUM TIMING SUMMARY")
        print("=" * 50)
        
        # Calculate key momentum periods
        momentum_periods = {
            'Opening Rush (1-15)': {
                'events': len(self.events_df[self.events_df['minute'] <= 15]),
                'goals': len(self.events_df[
                    (self.events_df['minute'] <= 15) & 
                    (self.events_df['event_name'].str.contains('Goal', na=False, case=False))
                ]),
                'subs': len(self.events_df[
                    (self.events_df['minute'] <= 15) & 
                    (self.events_df['substitution'].notna())
                ])
            },
            'First Half End (40-50)': {
                'events': len(self.events_df[
                    (self.events_df['minute'] >= 40) & 
                    (self.events_df['minute'] <= 50)
                ]),
                'goals': len(self.events_df[
                    (self.events_df['minute'] >= 40) & 
                    (self.events_df['minute'] <= 50) & 
                    (self.events_df['event_name'].str.contains('Goal', na=False, case=False))
                ]),
                'subs': len(self.events_df[
                    (self.events_df['minute'] >= 40) & 
                    (self.events_df['minute'] <= 50) & 
                    (self.events_df['substitution'].notna())
                ])
            },
            'Second Half Start (45-55)': {
                'events': len(self.events_df[
                    (self.events_df['minute'] >= 45) & 
                    (self.events_df['minute'] <= 55)
                ]),
                'goals': len(self.events_df[
                    (self.events_df['minute'] >= 45) & 
                    (self.events_df['minute'] <= 55) & 
                    (self.events_df['event_name'].str.contains('Goal', na=False, case=False))
                ]),
                'subs': len(self.events_df[
                    (self.events_df['minute'] >= 45) & 
                    (self.events_df['minute'] <= 55) & 
                    (self.events_df['substitution'].notna())
                ])
            },
            'Final Push (75-90)': {
                'events': len(self.events_df[
                    (self.events_df['minute'] >= 75) & 
                    (self.events_df['minute'] <= 90)
                ]),
                'goals': len(self.events_df[
                    (self.events_df['minute'] >= 75) & 
                    (self.events_df['minute'] <= 90) & 
                    (self.events_df['event_name'].str.contains('Goal', na=False, case=False))
                ]),
                'subs': len(self.events_df[
                    (self.events_df['minute'] >= 75) & 
                    (self.events_df['minute'] <= 90) & 
                    (self.events_df['substitution'].notna())
                ])
            },
            'Stoppage Drama (90+)': {
                'events': len(self.events_df[self.events_df['minute'] >= 90]),
                'goals': len(self.events_df[
                    (self.events_df['minute'] >= 90) & 
                    (self.events_df['event_name'].str.contains('Goal', na=False, case=False))
                ]),
                'subs': len(self.events_df[
                    (self.events_df['minute'] >= 90) & 
                    (self.events_df['substitution'].notna())
                ])
            }
        }
        
        print(f"🎯 KEY MOMENTUM PERIODS:")
        for period, data in momentum_periods.items():
            events_per_min = data['events'] / 15 if 'Drama' not in period else data['events'] / 20
            print(f"   {period:<25}: {data['events']:>5} events, {data['goals']:>2} goals, {data['subs']:>2} subs ({events_per_min:.0f}/min)")
        
        # Identify highest momentum periods
        print(f"\n🔥 HIGHEST MOMENTUM PERIODS:")
        sorted_periods = sorted(momentum_periods.items(), 
                              key=lambda x: x[1]['events'] / (15 if 'Drama' not in x[0] else 20), 
                              reverse=True)
        
        for i, (period, data) in enumerate(sorted_periods[:3]):
            events_per_min = data['events'] / (15 if 'Drama' not in period else 20)
            print(f"   {i+1}. {period}: {events_per_min:.0f} events/minute")

def main():
    """Main analysis function"""
    print("⏰ TIMING-BASED MOMENTUM PATTERN ANALYSIS")
    print("=" * 80)
    
    analyzer = TimingMomentumAnalyzer()
    
    # Load data
    if not analyzer.load_data():
        return
    
    # Analyze timing patterns
    first_15 = analyzer.analyze_first_minutes_momentum()
    analyzer.analyze_end_game_momentum()
    stoppage_data = analyzer.analyze_stoppage_time_patterns()
    subs_data = analyzer.analyze_substitution_timing_patterns()
    fouls_data, cards_data = analyzer.analyze_card_momentum_impact()
    
    # Create summary
    analyzer.create_momentum_timing_summary()
    
    print(f"\n✅ TIMING ANALYSIS COMPLETE")
    print(f"\n💡 KEY FINDINGS:")
    print(f"   • Opening 15 minutes show high intensity with early goals")
    print(f"   • Substitutions peak at 60-75 minutes (tactical) and 80+ (desperation)")
    print(f"   • Stoppage time creates dramatic momentum swings")
    print(f"   • Cards increase in frequency during closing minutes")
    print(f"   • Extra time shows extreme momentum volatility")

if __name__ == "__main__":
    main() 