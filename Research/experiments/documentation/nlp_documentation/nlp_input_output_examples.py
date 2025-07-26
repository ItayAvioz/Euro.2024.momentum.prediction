#!/usr/bin/env python3
"""
Concrete Input-Output Examples for NLP Techniques
Demonstrating the 5 key methods actually implemented in the project
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any

def demonstrate_nlp_techniques():
    """Show concrete examples of each NLP technique with input-output pairs"""
    
    print("🔍 CONCRETE INPUT-OUTPUT EXAMPLES FOR NLP TECHNIQUES")
    print("=" * 70)
    
    # =================================================================
    # 1. RULE-BASED TEXT PROCESSING WITH DOMAIN VOCABULARY
    # =================================================================
    
    print("\n1️⃣ RULE-BASED TEXT PROCESSING WITH DOMAIN VOCABULARY")
    print("=" * 60)
    
    # Domain vocabulary mapping
    domain_vocabulary = {
        'Pass': {
            'successful': 'completes a pass',
            'failed': 'loses possession with failed pass',
            'progressive': 'plays a progressive pass forward',
            'cross': 'delivers a cross into the box'
        },
        'Shot': {
            'on_target': 'forces a save from the goalkeeper',
            'goal': 'finds the back of the net',
            'off_target': 'sends the shot wide',
            'blocked': 'has the shot blocked'
        },
        'Carry': {
            'progressive': 'drives forward with the ball',
            'under_pressure': 'dribbles under pressure',
            'successful': 'advances with possession'
        },
        'Pressure': {
            'successful': 'wins the ball back',
            'failed': 'fails to regain possession',
            'intense': 'puts intense pressure on'
        },
        'Dribble': {
            'successful': 'beats the defender',
            'failed': 'is dispossessed'
        }
    }
    
    def process_with_domain_vocabulary(event):
        """Apply domain vocabulary to convert event to natural language"""
        base_text = f"{event['player_name']} ({event['team_name']})"
        
        if event['event_type'] in domain_vocabulary:
            descriptions = domain_vocabulary[event['event_type']]
            if event['outcome'] in descriptions:
                action = descriptions[event['outcome']]
            else:
                action = f"performs {event['event_type'].lower()}"
        else:
            action = event['event_type'].lower()
        
        return f"{base_text} {action}"
    
    # INPUT-OUTPUT EXAMPLES
    print("📥 INPUT → OUTPUT EXAMPLES:")
    print()
    
    sample_inputs = [
        {
            'player_name': 'Harry Kane',
            'team_name': 'England', 
            'event_type': 'Pass',
            'outcome': 'successful'
        },
        {
            'player_name': 'Jude Bellingham',
            'team_name': 'England',
            'event_type': 'Shot', 
            'outcome': 'on_target'
        },
        {
            'player_name': 'Virgil van Dijk',
            'team_name': 'Netherlands',
            'event_type': 'Pressure',
            'outcome': 'successful'
        },
        {
            'player_name': 'Gakpo',
            'team_name': 'Netherlands',
            'event_type': 'Carry',
            'outcome': 'progressive'
        }
    ]
    
    for i, event in enumerate(sample_inputs, 1):
        print(f"Example {i}:")
        print(f"  📥 INPUT: {event}")
        output = process_with_domain_vocabulary(event)
        print(f"  📤 OUTPUT: '{output}'")
        print()
    
    # =================================================================
    # 2. TEMPLATE-BASED COMMENTARY GENERATION
    # =================================================================
    
    print("\n2️⃣ TEMPLATE-BASED COMMENTARY GENERATION")
    print("=" * 60)
    
    # Commentary templates
    commentary_templates = {
        'momentum_description': '{team} are {momentum_level} with momentum at {score:.1f}/10',
        'prediction': 'Model predicts {team} momentum will {trend} to {future_score:.1f}/10 in next 3 minutes',
        'player_action': '{player} {action_description} in the {field_zone}',
        'tactical_situation': '{team} {tactical_approach} against {opponent} who are {opponent_state}',
        'game_phase': 'In this {phase} of the match, {team} {approach} while {opponent} {counter_approach}'
    }
    
    # Momentum level mapping
    momentum_levels = {
        (0, 2): 'struggling desperately',
        (2, 4): 'finding it difficult',
        (4, 6): 'locked in a balanced contest',
        (6, 8): 'building momentum',
        (8, 10): 'completely dominating'
    }
    
    def get_momentum_level(score):
        for (min_val, max_val), description in momentum_levels.items():
            if min_val <= score < max_val:
                return description
        return 'maintaining their level'
    
    def generate_template_commentary(template_name, **kwargs):
        """Generate commentary using templates"""
        if template_name in commentary_templates:
            return commentary_templates[template_name].format(**kwargs)
        return f"Unknown template: {template_name}"
    
    # INPUT-OUTPUT EXAMPLES
    print("📥 INPUT → OUTPUT EXAMPLES:")
    print()
    
    template_inputs = [
        {
            'template': 'momentum_description',
            'data': {
                'team': 'England',
                'momentum_level': get_momentum_level(7.2),
                'score': 7.2
            }
        },
        {
            'template': 'prediction',
            'data': {
                'team': 'Netherlands',
                'trend': 'increase',
                'future_score': 6.8
            }
        },
        {
            'template': 'player_action',
            'data': {
                'player': 'Harry Kane',
                'action_description': 'forces a save from the goalkeeper',
                'field_zone': 'attacking third'
            }
        },
        {
            'template': 'tactical_situation',
            'data': {
                'team': 'England',
                'tactical_approach': 'applying high pressure',
                'opponent': 'Netherlands',
                'opponent_state': 'defending deep'
            }
        }
    ]
    
    for i, example in enumerate(template_inputs, 1):
        print(f"Example {i}:")
        print(f"  📥 INPUT:")
        print(f"    Template: '{example['template']}'")
        print(f"    Data: {example['data']}")
        output = generate_template_commentary(example['template'], **example['data'])
        print(f"  📤 OUTPUT: '{output}'")
        print()
    
    # =================================================================
    # 3. SIMPLE SENTIMENT SCORING
    # =================================================================
    
    print("\n3️⃣ SIMPLE SENTIMENT SCORING")
    print("=" * 60)
    
    # Sentiment weights
    sentiment_weights = {
        'Pass': {'successful': 0.2, 'failed': -0.3, 'progressive': 0.4, 'cross': 0.3},
        'Shot': {'on_target': 0.8, 'goal': 1.0, 'off_target': -0.1, 'blocked': -0.2},
        'Carry': {'progressive': 0.3, 'under_pressure': 0.1, 'successful': 0.2},
        'Pressure': {'successful': 0.3, 'failed': -0.2, 'intense': 0.4},
        'Dribble': {'successful': 0.4, 'failed': -0.2}
    }
    
    def calculate_sentiment_score(events):
        """Calculate sentiment score from events"""
        total_sentiment = 0
        scored_events = 0
        details = []
        
        for event in events:
            event_type = event['event_type']
            outcome = event['outcome']
            
            if event_type in sentiment_weights and outcome in sentiment_weights[event_type]:
                score = sentiment_weights[event_type][outcome]
                total_sentiment += score
                scored_events += 1
                details.append({
                    'event': f"{event['player_name']} {event_type} ({outcome})",
                    'score': score
                })
        
        avg_sentiment = total_sentiment / scored_events if scored_events > 0 else 0
        return avg_sentiment, details
    
    # INPUT-OUTPUT EXAMPLES
    print("📥 INPUT → OUTPUT EXAMPLES:")
    print()
    
    sentiment_inputs = [
        # Example 1: Positive sequence
        {
            'sequence': 'England attacking sequence',
            'events': [
                {'player_name': 'Harry Kane', 'event_type': 'Pass', 'outcome': 'progressive'},
                {'player_name': 'Jude Bellingham', 'event_type': 'Carry', 'outcome': 'progressive'},
                {'player_name': 'Harry Kane', 'event_type': 'Shot', 'outcome': 'on_target'}
            ]
        },
        # Example 2: Negative sequence
        {
            'sequence': 'Netherlands struggling sequence',
            'events': [
                {'player_name': 'Gakpo', 'event_type': 'Pass', 'outcome': 'failed'},
                {'player_name': 'Van Dijk', 'event_type': 'Pressure', 'outcome': 'failed'},
                {'player_name': 'Depay', 'event_type': 'Shot', 'outcome': 'off_target'}
            ]
        },
        # Example 3: Mixed sequence
        {
            'sequence': 'Mixed momentum sequence',
            'events': [
                {'player_name': 'Foden', 'event_type': 'Pass', 'outcome': 'successful'},
                {'player_name': 'Ake', 'event_type': 'Pressure', 'outcome': 'successful'},
                {'player_name': 'Saka', 'event_type': 'Shot', 'outcome': 'blocked'}
            ]
        }
    ]
    
    for i, example in enumerate(sentiment_inputs, 1):
        print(f"Example {i}: {example['sequence']}")
        print(f"  📥 INPUT: {len(example['events'])} events")
        for event in example['events']:
            print(f"    - {event['player_name']} {event['event_type']} ({event['outcome']})")
        
        avg_sentiment, details = calculate_sentiment_score(example['events'])
        print(f"  📤 OUTPUT:")
        print(f"    Overall Sentiment: {avg_sentiment:+.2f}")
        print(f"    Individual Scores:")
        for detail in details:
            print(f"      - {detail['event']}: {detail['score']:+.1f}")
        print()
    
    # =================================================================
    # 4. CONTEXT PATTERN DETECTION
    # =================================================================
    
    print("\n4️⃣ CONTEXT PATTERN DETECTION")
    print("=" * 60)
    
    def detect_context_patterns(events):
        """Detect patterns in event sequences"""
        event_types = [e['event_type'] for e in events]
        teams = [e['team_name'] for e in events]
        outcomes = [e['outcome'] for e in events]
        
        # Pattern detection logic
        patterns = []
        
        # Attacking pattern
        if event_types.count('Shot') >= 2:
            patterns.append('attacking_surge')
        
        # Pressure pattern
        if event_types.count('Pressure') >= 2:
            patterns.append('defensive_pressure')
        
        # Possession pattern
        if event_types.count('Pass') >= 3:
            patterns.append('possession_control')
        
        # Transition pattern
        if len(set(teams)) > 1 and len(events) >= 3:
            patterns.append('quick_transitions')
        
        # Unsuccessful pattern
        if outcomes.count('failed') >= 2:
            patterns.append('struggling_phase')
        
        # Determine dominant team
        if teams:
            dominant_team = max(set(teams), key=teams.count)
            team_dominance = teams.count(dominant_team) / len(teams)
        else:
            dominant_team = 'Unknown'
            team_dominance = 0
        
        return {
            'patterns': patterns,
            'dominant_team': dominant_team,
            'team_dominance': team_dominance,
            'event_summary': {
                'total_events': len(events),
                'unique_teams': len(set(teams)),
                'event_types': dict(pd.Series(event_types).value_counts())
            }
        }
    
    # INPUT-OUTPUT EXAMPLES
    print("📥 INPUT → OUTPUT EXAMPLES:")
    print()
    
    context_inputs = [
        # Example 1: Attacking surge
        {
            'scenario': 'England attacking surge',
            'events': [
                {'player_name': 'Kane', 'team_name': 'England', 'event_type': 'Pass', 'outcome': 'progressive'},
                {'player_name': 'Bellingham', 'team_name': 'England', 'event_type': 'Shot', 'outcome': 'on_target'},
                {'player_name': 'Foden', 'team_name': 'England', 'event_type': 'Shot', 'outcome': 'blocked'},
                {'player_name': 'Saka', 'team_name': 'England', 'event_type': 'Shot', 'outcome': 'off_target'}
            ]
        },
        # Example 2: Defensive pressure
        {
            'scenario': 'Netherlands defensive pressure',
            'events': [
                {'player_name': 'Van Dijk', 'team_name': 'Netherlands', 'event_type': 'Pressure', 'outcome': 'successful'},
                {'player_name': 'De Jong', 'team_name': 'Netherlands', 'event_type': 'Pressure', 'outcome': 'intense'},
                {'player_name': 'Ake', 'team_name': 'Netherlands', 'event_type': 'Pressure', 'outcome': 'successful'}
            ]
        },
        # Example 3: Quick transitions
        {
            'scenario': 'Quick transitions between teams',
            'events': [
                {'player_name': 'Kane', 'team_name': 'England', 'event_type': 'Pass', 'outcome': 'failed'},
                {'player_name': 'Gakpo', 'team_name': 'Netherlands', 'event_type': 'Carry', 'outcome': 'progressive'},
                {'player_name': 'Bellingham', 'team_name': 'England', 'event_type': 'Pressure', 'outcome': 'successful'},
                {'player_name': 'Depay', 'team_name': 'Netherlands', 'event_type': 'Shot', 'outcome': 'on_target'}
            ]
        }
    ]
    
    for i, example in enumerate(context_inputs, 1):
        print(f"Example {i}: {example['scenario']}")
        print(f"  📥 INPUT: {len(example['events'])} events")
        for event in example['events']:
            print(f"    - {event['player_name']} ({event['team_name']}) {event['event_type']} ({event['outcome']})")
        
        context_analysis = detect_context_patterns(example['events'])
        print(f"  📤 OUTPUT:")
        print(f"    Detected Patterns: {context_analysis['patterns']}")
        print(f"    Dominant Team: {context_analysis['dominant_team']} ({context_analysis['team_dominance']:.1%})")
        print(f"    Event Summary: {context_analysis['event_summary']}")
        print()
    
    # =================================================================
    # 5. SPATIAL DATA INTEGRATION
    # =================================================================
    
    print("\n5️⃣ SPATIAL DATA INTEGRATION")
    print("=" * 60)
    
    def integrate_spatial_data(event_with_location):
        """Integrate spatial information with event data"""
        # Field dimensions: 120m x 80m
        # Goals at (0, 36-44) and (120, 36-44)
        
        x, y = event_with_location['location']
        
        # Determine field zone
        if x < 40:
            zone = 'defensive third'
        elif x < 80:
            zone = 'midfield'
        else:
            zone = 'attacking third'
        
        # Determine field side
        if y < 20:
            side = 'left flank'
        elif y < 30:
            side = 'left channel'
        elif y < 50:
            side = 'central channel'
        elif y < 60:
            side = 'right channel'
        else:
            side = 'right flank'
        
        # Calculate distance to goal
        if event_with_location['team_name'] == 'England':
            # England attacking towards (120, 40)
            goal_distance = np.sqrt((120 - x)**2 + (40 - y)**2)
        else:
            # Netherlands attacking towards (0, 40)
            goal_distance = np.sqrt((0 - x)**2 + (40 - y)**2)
        
        # Determine danger level based on location
        if zone == 'attacking third' and 30 <= y <= 50:
            danger_level = 'high'
        elif zone == 'attacking third':
            danger_level = 'medium'
        elif zone == 'midfield' and 25 <= y <= 55:
            danger_level = 'medium'
        else:
            danger_level = 'low'
        
        # Calculate pressure context (simplified)
        pressure_score = max(0, 10 - goal_distance/10)  # Closer to goal = higher pressure
        
        return {
            'spatial_description': f"{zone}, {side}",
            'coordinates': (x, y),
            'goal_distance': round(goal_distance, 1),
            'danger_level': danger_level,
            'pressure_score': round(pressure_score, 1),
            'tactical_context': f"Position offers {danger_level} threat level"
        }
    
    # INPUT-OUTPUT EXAMPLES
    print("📥 INPUT → OUTPUT EXAMPLES:")
    print()
    
    spatial_inputs = [
        # Example 1: Goal area shot
        {
            'scenario': 'Shot from penalty area',
            'event': {
                'player_name': 'Harry Kane',
                'team_name': 'England',
                'event_type': 'Shot',
                'outcome': 'on_target',
                'location': [112, 38]  # Close to goal, central
            }
        },
        # Example 2: Midfield pass
        {
            'scenario': 'Midfield progressive pass',
            'event': {
                'player_name': 'Jude Bellingham',
                'team_name': 'England', 
                'event_type': 'Pass',
                'outcome': 'progressive',
                'location': [65, 45]  # Central midfield
            }
        },
        # Example 3: Wide attack
        {
            'scenario': 'Wide attacking carry',
            'event': {
                'player_name': 'Bukayo Saka',
                'team_name': 'England',
                'event_type': 'Carry',
                'outcome': 'progressive',
                'location': [95, 15]  # Wide attacking position
            }
        },
        # Example 4: Defensive action
        {
            'scenario': 'Defensive pressure',
            'event': {
                'player_name': 'Van Dijk',
                'team_name': 'Netherlands',
                'event_type': 'Pressure',
                'outcome': 'successful',
                'location': [25, 40]  # Defensive zone
            }
        }
    ]
    
    for i, example in enumerate(spatial_inputs, 1):
        print(f"Example {i}: {example['scenario']}")
        print(f"  📥 INPUT:")
        event = example['event']
        print(f"    Player: {event['player_name']} ({event['team_name']})")
        print(f"    Action: {event['event_type']} ({event['outcome']})")
        print(f"    Location: {event['location']}")
        
        spatial_analysis = integrate_spatial_data(event)
        print(f"  📤 OUTPUT:")
        print(f"    Spatial Description: {spatial_analysis['spatial_description']}")
        print(f"    Coordinates: {spatial_analysis['coordinates']}")
        print(f"    Goal Distance: {spatial_analysis['goal_distance']}m")
        print(f"    Danger Level: {spatial_analysis['danger_level']}")
        print(f"    Pressure Score: {spatial_analysis['pressure_score']}/10")
        print(f"    Tactical Context: {spatial_analysis['tactical_context']}")
        print()
    
    # =================================================================
    # INTEGRATED EXAMPLE: ALL TECHNIQUES TOGETHER
    # =================================================================
    
    print("\n🎯 INTEGRATED EXAMPLE: ALL TECHNIQUES TOGETHER")
    print("=" * 60)
    
    def process_complete_sequence(events_with_spatial):
        """Process a complete sequence using all NLP techniques"""
        results = {
            'text_processing': [],
            'template_commentary': [],
            'sentiment_analysis': {},
            'context_patterns': {},
            'spatial_integration': []
        }
        
        # 1. Text processing with domain vocabulary
        for event in events_with_spatial:
            text = process_with_domain_vocabulary(event)
            results['text_processing'].append(text)
        
        # 2. Sentiment scoring
        sentiment_score, sentiment_details = calculate_sentiment_score(events_with_spatial)
        results['sentiment_analysis'] = {
            'overall_score': sentiment_score,
            'details': sentiment_details
        }
        
        # 3. Context pattern detection
        results['context_patterns'] = detect_context_patterns(events_with_spatial)
        
        # 4. Spatial integration
        for event in events_with_spatial:
            spatial_info = integrate_spatial_data(event)
            results['spatial_integration'].append(spatial_info)
        
        # 5. Template-based commentary generation
        patterns = results['context_patterns']['patterns']
        dominant_team = results['context_patterns']['dominant_team']
        
        if 'attacking_surge' in patterns:
            commentary = generate_template_commentary(
                'tactical_situation',
                team=dominant_team,
                tactical_approach='mounting an attacking surge',
                opponent='their opponents',
                opponent_state='under pressure'
            )
        elif 'defensive_pressure' in patterns:
            commentary = generate_template_commentary(
                'tactical_situation',
                team=dominant_team,
                tactical_approach='applying defensive pressure',
                opponent='their opponents',
                opponent_state='struggling to maintain possession'
            )
        else:
            commentary = f"{dominant_team} controlling the tempo of the game"
        
        results['template_commentary'] = commentary
        
        return results
    
    # Complete integrated example
    print("📥 COMPLETE INPUT SEQUENCE:")
    integrated_example = [
        {
            'player_name': 'Harry Kane',
            'team_name': 'England',
            'event_type': 'Pass',
            'outcome': 'progressive',
            'location': [75, 42]
        },
        {
            'player_name': 'Jude Bellingham', 
            'team_name': 'England',
            'event_type': 'Carry',
            'outcome': 'progressive',
            'location': [88, 35]
        },
        {
            'player_name': 'Harry Kane',
            'team_name': 'England',
            'event_type': 'Shot',
            'outcome': 'on_target',
            'location': [112, 39]
        }
    ]
    
    for i, event in enumerate(integrated_example, 1):
        print(f"  Event {i}: {event['player_name']} {event['event_type']} ({event['outcome']}) at {event['location']}")
    
    complete_results = process_complete_sequence(integrated_example)
    
    print("\n📤 COMPLETE OUTPUT:")
    print(f"  1. Text Processing:")
    for i, text in enumerate(complete_results['text_processing'], 1):
        print(f"     {i}. {text}")
    
    print(f"\n  2. Sentiment Analysis:")
    print(f"     Overall Score: {complete_results['sentiment_analysis']['overall_score']:+.2f}")
    for detail in complete_results['sentiment_analysis']['details']:
        print(f"     - {detail['event']}: {detail['score']:+.1f}")
    
    print(f"\n  3. Context Patterns:")
    print(f"     Detected: {complete_results['context_patterns']['patterns']}")
    print(f"     Dominant Team: {complete_results['context_patterns']['dominant_team']}")
    
    print(f"\n  4. Spatial Integration:")
    for i, spatial in enumerate(complete_results['spatial_integration'], 1):
        print(f"     Event {i}: {spatial['spatial_description']}, {spatial['danger_level']} danger ({spatial['goal_distance']}m from goal)")
    
    print(f"\n  5. Template Commentary:")
    print(f"     '{complete_results['template_commentary']}'")
    
    print("\n🎯 FINAL SUMMARY")
    print("=" * 50)
    print("✅ All 5 NLP techniques successfully demonstrated with:")
    print("  • Clear input-output examples")
    print("  • Realistic soccer data")
    print("  • Practical integration approach")
    print("  • Domain-specific vocabulary and patterns")
    print("  • Spatial context integration")
    print("  • Template-based natural language generation")

if __name__ == "__main__":
    demonstrate_nlp_techniques() 