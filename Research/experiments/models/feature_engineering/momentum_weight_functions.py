#!/usr/bin/env python3
"""
Momentum Weight Functions for Euro 2024 Analysis
Detailed breakdown of weight functions for momentum calculation
"""

import numpy as np
import pandas as pd

class MomentumWeightSystem:
    """Complete weight system for momentum calculation"""
    
    def __init__(self):
        self.component_weights = self.define_component_weights()
        self.time_period_weights = self.define_time_period_weights()
        self.situational_modifiers = self.define_situational_modifiers()
    
    def define_component_weights(self):
        """Define weights for each momentum component"""
        return {
            # === CORE MOMENTUM COMPONENTS ===
            'attacking_momentum': {
                'weight': 0.25,
                'description': 'Attacking intent and frequency',
                'reasoning': 'Primary indicator of team aggression and goal-seeking behavior'
            },
            'goal_threat_level': {
                'weight': 0.40,
                'description': 'Direct scoring opportunities',
                'reasoning': 'Most important factor - actual chances to score'
            },
            'possession_dominance': {
                'weight': 0.015,
                'description': 'Possession advantage over 50/50',
                'reasoning': 'Moderate impact - possession doesn\'t always translate to momentum'
            },
            'execution_quality': {
                'weight': 2.0,
                'description': 'Success rate of team actions',
                'reasoning': 'High multiplier - quality execution amplifies all other actions'
            },
            'performance_index': {
                'weight': 0.15,
                'description': 'Combined execution × attacking',
                'reasoning': 'Composite metric for overall team performance'
            },
            'recent_attacking': {
                'weight': 0.20,
                'description': 'Attacking actions in last 60 seconds',
                'reasoning': 'Recent activity weighted higher for current momentum'
            },
            'under_pressure': {
                'weight': -0.05,
                'description': 'Opponent pressure (negative)',
                'reasoning': 'Reduces momentum when under opponent pressure'
            },
            'tempo_control': {
                'weight': 0.08,
                'description': 'Ball progression vs possession',
                'reasoning': 'Moderate impact - ability to advance play'
            },
            'pressure_resistance': {
                'weight': 0.10,
                'description': 'Actions maintained under pressure',
                'reasoning': 'Resilience factor - maintaining performance under stress'
            }
        }
    
    def define_time_period_weights(self):
        """Define time-based weight modifiers for different game periods"""
        return {
            # === GAME PHASES (90 minutes divided into periods) ===
            'early_game': {
                'time_range': (0, 900),  # 0-15 minutes
                'weight_modifier': 0.85,
                'reasoning': 'Lower weight - teams still settling into rhythm',
                'characteristics': 'Cautious play, feeling out opponent'
            },
            'first_phase': {
                'time_range': (900, 1800),  # 15-30 minutes
                'weight_modifier': 1.0,
                'reasoning': 'Standard weight - normal game flow established',
                'characteristics': 'Settled gameplay, tactical patterns emerging'
            },
            'late_first_half': {
                'time_range': (1800, 2700),  # 30-45 minutes
                'weight_modifier': 1.1,
                'reasoning': 'Slightly higher - teams push before halftime',
                'characteristics': 'Increased urgency before break'
            },
            'second_half_start': {
                'time_range': (2700, 3600),  # 45-60 minutes
                'weight_modifier': 1.05,
                'reasoning': 'Fresh energy after halftime adjustments',
                'characteristics': 'Tactical changes, renewed energy'
            },
            'crucial_phase': {
                'time_range': (3600, 4500),  # 60-75 minutes
                'weight_modifier': 1.15,
                'reasoning': 'Critical period - momentum shifts more impactful',
                'characteristics': 'Substitutions, tactical battles intensify'
            },
            'final_push': {
                'time_range': (4500, 5400),  # 75-90 minutes
                'weight_modifier': 1.25,
                'reasoning': 'Highest weight - every action crucial',
                'characteristics': 'Maximum urgency, result-determining moments'
            },
            'injury_time': {
                'time_range': (5400, 6000),  # 90+ minutes
                'weight_modifier': 1.35,
                'reasoning': 'Maximum impact - last chance situations',
                'characteristics': 'Desperate attempts, all-or-nothing mentality'
            }
        }
    
    def define_situational_modifiers(self):
        """Define additional situational weight modifiers"""
        return {
            # === SCORE DIFFERENTIAL MODIFIERS ===
            'losing_by_1': {
                'modifier': 1.15,
                'reasoning': 'Increased urgency when behind by 1 goal'
            },
            'losing_by_2_plus': {
                'modifier': 1.25,
                'reasoning': 'Desperate situation requires maximum effort'
            },
            'winning_by_1': {
                'modifier': 0.95,
                'reasoning': 'Slight reduction - may play more conservatively'
            },
            'winning_by_2_plus': {
                'modifier': 0.85,
                'reasoning': 'Lower urgency when comfortably ahead'
            },
            'tied_game': {
                'modifier': 1.0,
                'reasoning': 'Standard weight for balanced situations'
            },
            
            # === COMPETITION STAGE MODIFIERS ===
            'group_stage': {
                'modifier': 0.9,
                'reasoning': 'Lower stakes, more conservative approach'
            },
            'knockout_stage': {
                'modifier': 1.1,
                'reasoning': 'Higher stakes, elimination pressure'
            },
            'final': {
                'modifier': 1.2,
                'reasoning': 'Maximum stakes, every moment crucial'
            }
        }
    
    def calculate_weighted_momentum(self, features, time_seconds, score_diff=0, stage='group'):
        """Calculate momentum with all weight functions applied"""
        
        # === STEP 1: BASE MOMENTUM CALCULATION ===
        base_components = []
        
        for component_name, weight_info in self.component_weights.items():
            if component_name in features:
                weighted_value = features[component_name] * weight_info['weight']
                base_components.append(weighted_value)
        
        base_momentum = sum(base_components)
        
        # === STEP 2: TIME PERIOD MODIFIER ===
        time_modifier = self.get_time_period_modifier(time_seconds)
        
        # === STEP 3: SITUATIONAL MODIFIERS ===
        score_modifier = self.get_score_modifier(score_diff)
        stage_modifier = self.situational_modifiers[stage]['modifier']
        
        # === STEP 4: APPLY ALL MODIFIERS ===
        final_momentum = base_momentum * time_modifier * score_modifier * stage_modifier
        
        # === STEP 5: NORMALIZE TO 0-10 RANGE ===
        final_momentum = min(10, max(0, final_momentum))
        
        return {
            'base_momentum': base_momentum,
            'time_modifier': time_modifier,
            'score_modifier': score_modifier,
            'stage_modifier': stage_modifier,
            'final_momentum': final_momentum,
            'calculation_breakdown': self.get_calculation_breakdown(
                features, time_seconds, score_diff, stage
            )
        }
    
    def get_time_period_modifier(self, time_seconds):
        """Get time-based weight modifier"""
        for period_name, period_info in self.time_period_weights.items():
            time_min, time_max = period_info['time_range']
            if time_min <= time_seconds <= time_max:
                return period_info['weight_modifier']
        
        # Default to injury time if beyond 90 minutes
        return self.time_period_weights['injury_time']['weight_modifier']
    
    def get_score_modifier(self, score_diff):
        """Get score differential modifier"""
        if score_diff == 0:
            return self.situational_modifiers['tied_game']['modifier']
        elif score_diff == -1:
            return self.situational_modifiers['losing_by_1']['modifier']
        elif score_diff <= -2:
            return self.situational_modifiers['losing_by_2_plus']['modifier']
        elif score_diff == 1:
            return self.situational_modifiers['winning_by_1']['modifier']
        else:  # score_diff >= 2
            return self.situational_modifiers['winning_by_2_plus']['modifier']
    
    def get_calculation_breakdown(self, features, time_seconds, score_diff, stage):
        """Provide detailed breakdown of momentum calculation"""
        breakdown = {
            'components': {},
            'modifiers': {},
            'formula': {}
        }
        
        # Component breakdown
        total_component_weight = 0
        for component_name, weight_info in self.component_weights.items():
            if component_name in features:
                component_value = features[component_name]
                weighted_value = component_value * weight_info['weight']
                breakdown['components'][component_name] = {
                    'raw_value': component_value,
                    'weight': weight_info['weight'],
                    'weighted_value': weighted_value,
                    'description': weight_info['description']
                }
                total_component_weight += weighted_value
        
        # Modifier breakdown
        breakdown['modifiers'] = {
            'time_period': {
                'modifier': self.get_time_period_modifier(time_seconds),
                'period': self.get_current_period_name(time_seconds)
            },
            'score_differential': {
                'modifier': self.get_score_modifier(score_diff),
                'score_diff': score_diff
            },
            'competition_stage': {
                'modifier': self.situational_modifiers[stage]['modifier'],
                'stage': stage
            }
        }
        
        # Formula breakdown
        breakdown['formula'] = {
            'base_momentum': total_component_weight,
            'time_modifier': breakdown['modifiers']['time_period']['modifier'],
            'score_modifier': breakdown['modifiers']['score_differential']['modifier'],
            'stage_modifier': breakdown['modifiers']['competition_stage']['modifier'],
            'formula_text': 'final_momentum = base_momentum × time_modifier × score_modifier × stage_modifier'
        }
        
        return breakdown
    
    def get_current_period_name(self, time_seconds):
        """Get current game period name"""
        for period_name, period_info in self.time_period_weights.items():
            time_min, time_max = period_info['time_range']
            if time_min <= time_seconds <= time_max:
                return period_name
        return 'injury_time'
    
    def display_weight_system(self):
        """Display complete weight system documentation"""
        print("🎯 MOMENTUM WEIGHT SYSTEM DOCUMENTATION")
        print("=" * 80)
        
        # === COMPONENT WEIGHTS ===
        print("\n📊 COMPONENT WEIGHTS:")
        print("=" * 50)
        
        total_base_weight = 0
        for component, info in self.component_weights.items():
            print(f"{component:25} : {info['weight']:6.3f} | {info['description']}")
            if info['weight'] > 0:
                total_base_weight += info['weight']
        
        print(f"\nTotal positive weight: {total_base_weight:.3f}")
        
        # === TIME PERIOD WEIGHTS ===
        print("\n⏰ TIME PERIOD MODIFIERS:")
        print("=" * 50)
        
        for period, info in self.time_period_weights.items():
            time_range = f"{info['time_range'][0]//60}-{info['time_range'][1]//60} min"
            print(f"{period:20} : {info['weight_modifier']:5.2f} | {time_range:12} | {info['reasoning']}")
        
        # === SITUATIONAL MODIFIERS ===
        print("\n🎲 SITUATIONAL MODIFIERS:")
        print("=" * 50)
        
        print("Score Differential:")
        score_mods = ['losing_by_2_plus', 'losing_by_1', 'tied_game', 'winning_by_1', 'winning_by_2_plus']
        for mod in score_mods:
            if mod in self.situational_modifiers:
                info = self.situational_modifiers[mod]
                print(f"  {mod:20} : {info['modifier']:5.2f} | {info['reasoning']}")
        
        print("\nCompetition Stage:")
        stage_mods = ['group_stage', 'knockout_stage', 'final']
        for mod in stage_mods:
            if mod in self.situational_modifiers:
                info = self.situational_modifiers[mod]
                print(f"  {mod:20} : {info['modifier']:5.2f} | {info['reasoning']}")

def demonstrate_momentum_calculation():
    """Demonstrate momentum calculation with examples"""
    print("\n🧮 MOMENTUM CALCULATION EXAMPLES")
    print("=" * 80)
    
    weight_system = MomentumWeightSystem()
    
    # Example scenarios
    scenarios = [
        {
            'name': 'Early Game - Balanced Play',
            'features': {
                'attacking_momentum': 3.2,
                'goal_threat_level': 1.5,
                'possession_dominance': 5.0,
                'execution_quality': 0.75,
                'performance_index': 2.4,
                'recent_attacking': 2.0,
                'under_pressure': 3.0,
                'tempo_control': 1.8,
                'pressure_resistance': 2.1
            },
            'time_seconds': 600,  # 10 minutes
            'score_diff': 0,
            'stage': 'group_stage'
        },
        {
            'name': 'Late Game - Losing Team Push',
            'features': {
                'attacking_momentum': 6.8,
                'goal_threat_level': 4.2,
                'possession_dominance': -8.0,
                'execution_quality': 0.65,
                'performance_index': 4.4,
                'recent_attacking': 5.5,
                'under_pressure': 6.2,
                'tempo_control': 3.1,
                'pressure_resistance': 1.8
            },
            'time_seconds': 5100,  # 85 minutes
            'score_diff': -1,
            'stage': 'knockout_stage'
        },
        {
            'name': 'Final - Winning Team Control',
            'features': {
                'attacking_momentum': 4.1,
                'goal_threat_level': 2.8,
                'possession_dominance': 12.0,
                'execution_quality': 0.85,
                'performance_index': 3.5,
                'recent_attacking': 1.8,
                'under_pressure': 1.5,
                'tempo_control': 2.4,
                'pressure_resistance': 3.2
            },
            'time_seconds': 4800,  # 80 minutes
            'score_diff': 1,
            'stage': 'final'
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 SCENARIO {i}: {scenario['name']}")
        print("-" * 60)
        
        result = weight_system.calculate_weighted_momentum(
            scenario['features'],
            scenario['time_seconds'],
            scenario['score_diff'],
            scenario['stage']
        )
        
        print(f"Base Momentum: {result['base_momentum']:.3f}")
        print(f"Time Modifier: {result['time_modifier']:.3f} ({weight_system.get_current_period_name(scenario['time_seconds'])})")
        print(f"Score Modifier: {result['score_modifier']:.3f}")
        print(f"Stage Modifier: {result['stage_modifier']:.3f}")
        print(f"FINAL MOMENTUM: {result['final_momentum']:.3f}/10")
        
        # Show top contributing components
        components = result['calculation_breakdown']['components']
        sorted_components = sorted(components.items(), key=lambda x: abs(x[1]['weighted_value']), reverse=True)
        
        print(f"\nTop 3 Contributing Factors:")
        for j, (comp_name, comp_data) in enumerate(sorted_components[:3], 1):
            print(f"  {j}. {comp_name}: {comp_data['weighted_value']:+.3f}")

def main():
    """Main demonstration function"""
    weight_system = MomentumWeightSystem()
    
    # Display complete weight system
    weight_system.display_weight_system()
    
    # Demonstrate calculations
    demonstrate_momentum_calculation()
    
    print("\n✅ Weight system documentation complete!")

if __name__ == "__main__":
    main() 