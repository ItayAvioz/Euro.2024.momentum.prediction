#!/usr/bin/env python3
"""
360° Data Processing Examples
Comprehensive input-output examples for spatial data analysis
"""

import pandas as pd
import numpy as np
import json

def demonstrate_360_data_processing():
    print("🌐 360° DATA PROCESSING INPUT-OUTPUT EXAMPLES")
    print("=" * 60)
    
    # =================================================================
    # 1. RAW 360° DATA INPUT STRUCTURE
    # =================================================================
    print("\n1️⃣ RAW 360° DATA INPUT STRUCTURE")
    print("=" * 50)
    
    # Sample raw 360° data from StatsBomb
    raw_360_data = {
        'event_uuid': '12345678-1234-5678-9012-123456789abc',
        'visible_area': [0, 0, 120, 80],  # [x_min, y_min, x_max, y_max]
        'freeze_frame': [
            # England players (team_id: 1)
            {'player_id': 1001, 'position': [75.2, 42.1], 'teammate': True},
            {'player_id': 1002, 'position': [88.5, 35.7], 'teammate': True},
            {'player_id': 1003, 'position': [112.3, 39.4], 'teammate': True},
            {'player_id': 1004, 'position': [68.9, 55.2], 'teammate': True},
            {'player_id': 1005, 'position': [45.7, 28.3], 'teammate': True},
            {'player_id': 1006, 'position': [35.2, 45.8], 'teammate': True},
            {'player_id': 1007, 'position': [25.1, 60.2], 'teammate': True},
            {'player_id': 1008, 'position': [22.8, 20.1], 'teammate': True},
            {'player_id': 1009, 'position': [15.3, 40.5], 'teammate': True},
            {'player_id': 1010, 'position': [8.2, 35.7], 'teammate': True},
            {'player_id': 1011, 'position': [2.1, 40.0], 'teammate': True},  # Goalkeeper
            
            # Netherlands players (team_id: 2)
            {'player_id': 2001, 'position': [45.8, 38.2], 'teammate': False},
            {'player_id': 2002, 'position': [52.3, 45.1], 'teammate': False},
            {'player_id': 2003, 'position': [58.7, 32.4], 'teammate': False},
            {'player_id': 2004, 'position': [62.1, 55.9], 'teammate': False},
            {'player_id': 2005, 'position': [75.4, 48.3], 'teammate': False},
            {'player_id': 2006, 'position': [82.3, 42.7], 'teammate': False},
            {'player_id': 2007, 'position': [95.2, 35.1], 'teammate': False},
            {'player_id': 2008, 'position': [98.7, 48.6], 'teammate': False},
            {'player_id': 2009, 'position': [105.3, 41.2], 'teammate': False},
            {'player_id': 2010, 'position': [108.9, 38.7], 'teammate': False},
            {'player_id': 2011, 'position': [118.5, 40.0], 'teammate': False}  # Goalkeeper
        ]
    }
    
    print("📥 RAW 360° INPUT DATA:")
    print(f"Event UUID: {raw_360_data['event_uuid']}")
    print(f"Visible Area: {raw_360_data['visible_area']}")
    print(f"Total Players: {len(raw_360_data['freeze_frame'])}")
    print(f"Teammates: {sum(1 for p in raw_360_data['freeze_frame'] if p['teammate'])}")
    print(f"Opponents: {sum(1 for p in raw_360_data['freeze_frame'] if not p['teammate'])}")
    
    # =================================================================
    # 2. FREEZE FRAME PARSING
    # =================================================================
    print("\n2️⃣ FREEZE FRAME PARSING")
    print("=" * 50)
    
    def parse_freeze_frame(freeze_frame_data):
        """Parse freeze frame data into structured format"""
        teammates = []
        opponents = []
        
        for player in freeze_frame_data:
            player_info = {
                'player_id': player['player_id'],
                'x': player['position'][0],
                'y': player['position'][1],
                'position': player['position']
            }
            
            if player['teammate']:
                teammates.append(player_info)
            else:
                opponents.append(player_info)
        
        return {
            'teammates': teammates,
            'opponents': opponents,
            'total_players': len(freeze_frame_data)
        }
    
    parsed_data = parse_freeze_frame(raw_360_data['freeze_frame'])
    
    print("📤 PARSED OUTPUT:")
    print(f"Teammates ({len(parsed_data['teammates'])}):")
    for i, player in enumerate(parsed_data['teammates'][:3]):  # Show first 3
        print(f"  {i+1}. Player {player['player_id']}: ({player['x']:.1f}, {player['y']:.1f})")
    print(f"  ... and {len(parsed_data['teammates'])-3} more")
    
    print(f"\nOpponents ({len(parsed_data['opponents'])}):")
    for i, player in enumerate(parsed_data['opponents'][:3]):  # Show first 3
        print(f"  {i+1}. Player {player['player_id']}: ({player['x']:.1f}, {player['y']:.1f})")
    print(f"  ... and {len(parsed_data['opponents'])-3} more")
    
    # =================================================================
    # 3. PRESSURE CALCULATION
    # =================================================================
    print("\n3️⃣ PRESSURE CALCULATION")
    print("=" * 50)
    
    def calculate_pressure_score(event_location, opponents, pressure_radius=5.0):
        """Calculate pressure score based on opponent proximity"""
        event_x, event_y = event_location
        pressure_score = 0
        pressure_players = []
        
        for opponent in opponents:
            distance = np.sqrt((opponent['x'] - event_x)**2 + (opponent['y'] - event_y)**2)
            
            if distance <= pressure_radius:
                # Pressure decreases with distance
                pressure_contribution = max(0, (pressure_radius - distance) / pressure_radius)
                pressure_score += pressure_contribution
                pressure_players.append({
                    'player_id': opponent['player_id'],
                    'distance': round(distance, 1),
                    'pressure_contribution': round(pressure_contribution, 2)
                })
        
        return {
            'pressure_score': round(pressure_score, 2),
            'pressure_players': pressure_players,
            'total_pressure_players': len(pressure_players)
        }
    
    # Example: Calculate pressure for Harry Kane's shot
    event_location = [112.3, 39.4]  # Kane's position
    pressure_analysis = calculate_pressure_score(event_location, parsed_data['opponents'])
    
    print("📥 INPUT:")
    print(f"Event Location: {event_location}")
    print(f"Pressure Radius: 5.0m")
    print(f"Opponents to check: {len(parsed_data['opponents'])}")
    
    print("\n📤 PRESSURE ANALYSIS OUTPUT:")
    print(f"Pressure Score: {pressure_analysis['pressure_score']}/10")
    print(f"Players applying pressure: {pressure_analysis['total_pressure_players']}")
    for player in pressure_analysis['pressure_players']:
        print(f"  - Player {player['player_id']}: {player['distance']}m away, contributes {player['pressure_contribution']}")
    
    # =================================================================
    # 4. FIELD COVERAGE ANALYSIS
    # =================================================================
    print("\n4️⃣ FIELD COVERAGE ANALYSIS")
    print("=" * 50)
    
    def analyze_field_coverage(teammates, opponents, field_dimensions=(120, 80)):
        """Analyze field coverage by both teams"""
        field_width, field_height = field_dimensions
        
        # Divide field into zones
        zones = {
            'defensive_third': {'x_range': (0, 40), 'y_range': (0, 80)},
            'middle_third': {'x_range': (40, 80), 'y_range': (0, 80)},
            'attacking_third': {'x_range': (80, 120), 'y_range': (0, 80)}
        }
        
        # Count players in each zone
        coverage_analysis = {}
        for zone_name, zone_bounds in zones.items():
            x_min, x_max = zone_bounds['x_range']
            y_min, y_max = zone_bounds['y_range']
            
            teammates_in_zone = sum(1 for p in teammates if x_min <= p['x'] < x_max and y_min <= p['y'] < y_max)
            opponents_in_zone = sum(1 for p in opponents if x_min <= p['x'] < x_max and y_min <= p['y'] < y_max)
            
            coverage_analysis[zone_name] = {
                'teammates': teammates_in_zone,
                'opponents': opponents_in_zone,
                'total': teammates_in_zone + opponents_in_zone,
                'team_advantage': teammates_in_zone - opponents_in_zone
            }
        
        return coverage_analysis
    
    coverage = analyze_field_coverage(parsed_data['teammates'], parsed_data['opponents'])
    
    print("📥 INPUT:")
    print(f"Teammates: {len(parsed_data['teammates'])} players")
    print(f"Opponents: {len(parsed_data['opponents'])} players")
    print("Field divided into 3 zones")
    
    print("\n📤 FIELD COVERAGE OUTPUT:")
    for zone, data in coverage.items():
        print(f"{zone.replace('_', ' ').title()}:")
        print(f"  Teammates: {data['teammates']}, Opponents: {data['opponents']}")
        print(f"  Advantage: {data['team_advantage']:+d} ({'Teammates' if data['team_advantage'] > 0 else 'Opponents' if data['team_advantage'] < 0 else 'Balanced'})")
    
    # =================================================================
    # 5. SPACE ANALYSIS (VORONOI-LIKE)
    # =================================================================
    print("\n5️⃣ SPACE ANALYSIS")
    print("=" * 50)
    
    def analyze_space_control(teammates, opponents, sample_points=100):
        """Simplified space control analysis"""
        total_space = 0
        controlled_space = 0
        
        # Sample points across the field
        for i in range(sample_points):
            # Random point on field
            x = np.random.uniform(0, 120)
            y = np.random.uniform(0, 80)
            
            # Find closest teammate and opponent
            min_teammate_dist = min(np.sqrt((p['x'] - x)**2 + (p['y'] - y)**2) for p in teammates)
            min_opponent_dist = min(np.sqrt((p['x'] - x)**2 + (p['y'] - y)**2) for p in opponents)
            
            total_space += 1
            if min_teammate_dist < min_opponent_dist:
                controlled_space += 1
        
        control_percentage = (controlled_space / total_space) * 100
        
        return {
            'control_percentage': round(control_percentage, 1),
            'sample_points': sample_points,
            'controlled_points': controlled_space,
            'opponent_controlled': sample_points - controlled_space
        }
    
    # Set random seed for reproducible results
    np.random.seed(42)
    space_analysis = analyze_space_control(parsed_data['teammates'], parsed_data['opponents'])
    
    print("📥 INPUT:")
    print(f"Sample Points: {space_analysis['sample_points']}")
    print("Method: Closest player control")
    
    print("\n📤 SPACE CONTROL OUTPUT:")
    print(f"Team Control: {space_analysis['control_percentage']}%")
    print(f"Controlled Points: {space_analysis['controlled_points']}")
    print(f"Opponent Control: {100 - space_analysis['control_percentage']}%")
    
    # =================================================================
    # 6. TACTICAL FORMATION DETECTION
    # =================================================================
    print("\n6️⃣ TACTICAL FORMATION DETECTION")
    print("=" * 50)
    
    def detect_formation(teammates, field_dimensions=(120, 80)):
        """Detect tactical formation from player positions"""
        # Remove goalkeeper (closest to goal)
        outfield_players = [p for p in teammates if p['x'] > 15]  # Assume GK is behind x=15
        
        if len(outfield_players) < 10:
            return {'formation': 'Unknown', 'confidence': 0}
        
        # Analyze player distribution by thirds
        defensive_players = [p for p in outfield_players if p['x'] < 40]
        midfield_players = [p for p in outfield_players if 40 <= p['x'] < 80]
        attacking_players = [p for p in outfield_players if p['x'] >= 80]
        
        formation_string = f"{len(defensive_players)}-{len(midfield_players)}-{len(attacking_players)}"
        
        # Calculate formation confidence based on clustering
        formation_confidence = 0.8 if len(defensive_players) > 0 and len(midfield_players) > 0 else 0.6
        
        return {
            'formation': formation_string,
            'confidence': formation_confidence,
            'defensive_players': len(defensive_players),
            'midfield_players': len(midfield_players),
            'attacking_players': len(attacking_players),
            'total_outfield': len(outfield_players)
        }
    
    formation_analysis = detect_formation(parsed_data['teammates'])
    
    print("📥 INPUT:")
    print(f"Total teammates: {len(parsed_data['teammates'])}")
    print("Method: Positional clustering by thirds")
    
    print("\n📤 FORMATION DETECTION OUTPUT:")
    print(f"Detected Formation: {formation_analysis['formation']}")
    print(f"Confidence: {formation_analysis['confidence']:.1%}")
    print(f"Distribution: {formation_analysis['defensive_players']} defenders, {formation_analysis['midfield_players']} midfielders, {formation_analysis['attacking_players']} attackers")
    
    # =================================================================
    # 7. INTEGRATED 360° ANALYSIS
    # =================================================================
    print("\n7️⃣ INTEGRATED 360° ANALYSIS")
    print("=" * 50)
    
    def comprehensive_360_analysis(event_location, freeze_frame_data, event_type='Shot'):
        """Complete 360° analysis combining all techniques"""
        parsed = parse_freeze_frame(freeze_frame_data)
        pressure = calculate_pressure_score(event_location, parsed['opponents'])
        coverage = analyze_field_coverage(parsed['teammates'], parsed['opponents'])
        
        # Set seed for reproducible space analysis
        np.random.seed(42)
        space = analyze_space_control(parsed['teammates'], parsed['opponents'])
        formation = detect_formation(parsed['teammates'])
        
        # Determine tactical context
        if pressure['pressure_score'] > 2.0:
            tactical_context = 'High pressure situation'
        elif pressure['pressure_score'] > 1.0:
            tactical_context = 'Moderate pressure'
        else:
            tactical_context = 'Low pressure situation'
        
        # Calculate danger level
        x, y = event_location
        if x > 100 and 20 < y < 60:
            danger_level = 'Very High'
        elif x > 80:
            danger_level = 'High'
        elif x > 60:
            danger_level = 'Medium'
        else:
            danger_level = 'Low'
        
        return {
            'event_analysis': {
                'location': event_location,
                'pressure_score': pressure['pressure_score'],
                'tactical_context': tactical_context,
                'danger_level': danger_level
            },
            'team_analysis': {
                'formation': formation['formation'],
                'space_control': space['control_percentage'],
                'field_coverage': coverage
            },
            'spatial_insights': {
                'pressure_players': pressure['total_pressure_players'],
                'controlled_space': space['controlled_points'],
                'formation_confidence': formation['confidence']
            }
        }
    
    # Complete analysis for Kane's shot
    complete_analysis = comprehensive_360_analysis(
        event_location=[112.3, 39.4],
        freeze_frame_data=raw_360_data['freeze_frame'],
        event_type='Shot'
    )
    
    print("📥 COMPLETE INPUT:")
    print(f"Event: Shot at {complete_analysis['event_analysis']['location']}")
    print(f"Freeze Frame: {len(raw_360_data['freeze_frame'])} players")
    
    print("\n📤 COMPREHENSIVE 360° OUTPUT:")
    print(f"🎯 Event Analysis:")
    print(f"  Pressure Score: {complete_analysis['event_analysis']['pressure_score']}/10")
    print(f"  Tactical Context: {complete_analysis['event_analysis']['tactical_context']}")
    print(f"  Danger Level: {complete_analysis['event_analysis']['danger_level']}")
    
    print(f"\n⚽ Team Analysis:")
    print(f"  Formation: {complete_analysis['team_analysis']['formation']}")
    print(f"  Space Control: {complete_analysis['team_analysis']['space_control']}%")
    print(f"  Field Coverage: Attacking third advantage: {complete_analysis['team_analysis']['field_coverage']['attacking_third']['team_advantage']:+d}")
    
    print(f"\n📊 Spatial Insights:")
    print(f"  Players applying pressure: {complete_analysis['spatial_insights']['pressure_players']}")
    print(f"  Controlled space points: {complete_analysis['spatial_insights']['controlled_space']}/100")
    print(f"  Formation confidence: {complete_analysis['spatial_insights']['formation_confidence']:.1%}")
    
    # =================================================================
    # 8. COMMENTARY INTEGRATION
    # =================================================================
    print("\n8️⃣ COMMENTARY INTEGRATION")
    print("=" * 50)
    
    def generate_360_commentary(analysis_result):
        """Generate commentary based on 360° analysis"""
        event_data = analysis_result['event_analysis']
        team_data = analysis_result['team_analysis']
        
        # Base commentary
        commentary_parts = []
        
        # Pressure context
        if event_data['pressure_score'] > 2.0:
            commentary_parts.append("under intense pressure from multiple defenders")
        elif event_data['pressure_score'] > 1.0:
            commentary_parts.append("with defenders closing in")
        else:
            commentary_parts.append("with space to work")
        
        # Formation context
        formation = team_data['formation']
        if formation.startswith('4-3-3'):
            commentary_parts.append("The team is set up in an attacking 4-3-3 formation")
        elif formation.startswith('4-4-2'):
            commentary_parts.append("Playing a balanced 4-4-2 formation")
        else:
            commentary_parts.append(f"Operating in a {formation} formation")
        
        # Space control
        space_control = team_data['space_control']
        if space_control > 60:
            commentary_parts.append("dominating territorial control")
        elif space_control > 40:
            commentary_parts.append("in a balanced territorial battle")
        else:
            commentary_parts.append("under territorial pressure")
        
        # Combine into narrative
        commentary = f"The shot comes {commentary_parts[0]}. {commentary_parts[1]}, {commentary_parts[2]}."
        
        return commentary
    
    generated_commentary = generate_360_commentary(complete_analysis)
    
    print("📥 INPUT:")
    print("Complete 360° analysis results")
    
    print("\n📤 GENERATED COMMENTARY:")
    print(f'"{generated_commentary}"')
    
    print("\n🎯 SUMMARY")
    print("=" * 30)
    print("✅ 360° Data Processing Pipeline:")
    print("  1. Parse freeze frame data → Player positions")
    print("  2. Calculate pressure → Opponent proximity analysis")
    print("  3. Analyze field coverage → Zonal dominance")
    print("  4. Assess space control → Territorial advantage")
    print("  5. Detect formation → Tactical setup")
    print("  6. Generate insights → Contextual commentary")
    print()
    print("🔑 Key insight: 360° data provides rich spatial context")
    print("for tactical analysis and momentum prediction!")

if __name__ == "__main__":
    demonstrate_360_data_processing() 