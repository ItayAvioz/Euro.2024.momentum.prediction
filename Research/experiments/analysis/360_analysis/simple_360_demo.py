#!/usr/bin/env python3
"""
Simple 360° Data Processing Demo
Clear input-output examples for spatial analysis
"""

import numpy as np

def main():
    print("🌐 360° DATA PROCESSING INPUT-OUTPUT EXAMPLES")
    print("=" * 60)
    
    # 1. RAW 360° DATA INPUT
    print("\n1️⃣ RAW 360° DATA INPUT STRUCTURE")
    print("=" * 50)
    
    # Sample freeze frame data - realistic positions
    freeze_frame = [
        # England players (teammates)
        {'player_id': 1003, 'position': [112.3, 39.4], 'teammate': True},   # Kane (shooter)
        {'player_id': 1002, 'position': [88.5, 35.7], 'teammate': True},    # Bellingham
        {'player_id': 1001, 'position': [75.2, 42.1], 'teammate': True},    # England midfielder
        
        # Netherlands players (opponents)
        {'player_id': 2003, 'position': [108.9, 38.7], 'teammate': False},  # Close defender
        {'player_id': 2004, 'position': [115.2, 35.1], 'teammate': False},  # Very close defender
        {'player_id': 2001, 'position': [95.4, 48.3], 'teammate': False}    # Distant player
    ]
    
    print("📥 RAW INPUT DATA:")
    print("Total players:", len(freeze_frame))
    teammates = sum(1 for p in freeze_frame if p['teammate'])
    opponents = sum(1 for p in freeze_frame if not p['teammate'])
    print("Teammates:", teammates)
    print("Opponents:", opponents)
    
    print("\nSample positions:")
    for i, player in enumerate(freeze_frame[:3]):
        team = "England" if player['teammate'] else "Netherlands"
        pos = player['position']
        print(f"  Player {player['player_id']} ({team}): [{pos[0]}, {pos[1]}]")
    
    # 2. PARSING
    print("\n2️⃣ FREEZE FRAME PARSING")
    print("=" * 50)
    
    teammates_list = []
    opponents_list = []
    
    for player in freeze_frame:
        player_data = {
            'id': player['player_id'],
            'x': player['position'][0],
            'y': player['position'][1]
        }
        
        if player['teammate']:
            teammates_list.append(player_data)
        else:
            opponents_list.append(player_data)
    
    print("📤 PARSED OUTPUT:")
    print(f"Teammates ({len(teammates_list)}):")
    for p in teammates_list:
        print(f"  ID {p['id']}: ({p['x']:.1f}, {p['y']:.1f})")
    
    print(f"Opponents ({len(opponents_list)}):")
    for p in opponents_list:
        print(f"  ID {p['id']}: ({p['x']:.1f}, {p['y']:.1f})")
    
    # 3. PRESSURE CALCULATION
    print("\n3️⃣ PRESSURE CALCULATION")
    print("=" * 50)
    
    # Kane's position for the shot
    kane_x, kane_y = 112.3, 39.4
    pressure_radius = 5.0
    total_pressure = 0
    pressure_players = []
    
    for opponent in opponents_list:
        distance = np.sqrt((opponent['x'] - kane_x)**2 + (opponent['y'] - kane_y)**2)
        
        if distance <= pressure_radius:
            pressure_contribution = (pressure_radius - distance) / pressure_radius
            total_pressure += pressure_contribution
            pressure_players.append({
                'id': opponent['id'],
                'distance': round(distance, 1),
                'pressure': round(pressure_contribution, 2)
            })
    
    print("📥 INPUT:")
    print(f"Event location: [{kane_x}, {kane_y}]")
    print(f"Pressure radius: {pressure_radius}m")
    print(f"Opponents to check: {len(opponents_list)}")
    
    print("\n📤 PRESSURE OUTPUT:")
    print(f"Total pressure score: {total_pressure:.2f}")
    print(f"Players applying pressure: {len(pressure_players)}")
    for p in pressure_players:
        print(f"  Player {p['id']}: {p['distance']}m away, pressure: {p['pressure']}")
    
    # 4. FIELD ZONE ANALYSIS
    print("\n4️⃣ FIELD ZONE ANALYSIS")
    print("=" * 50)
    
    zones = {
        'defensive': (0, 40),
        'midfield': (40, 80),
        'attacking': (80, 120)
    }
    
    zone_counts = {}
    for zone_name, zone_range in zones.items():
        x_min, x_max = zone_range
        team_in_zone = sum(1 for p in teammates_list if x_min <= p['x'] < x_max)
        opp_in_zone = sum(1 for p in opponents_list if x_min <= p['x'] < x_max)
        
        zone_counts[zone_name] = {
            'teammates': team_in_zone,
            'opponents': opp_in_zone,
            'advantage': team_in_zone - opp_in_zone
        }
    
    print("📥 INPUT:")
    print("Field zones: defensive (0-40), midfield (40-80), attacking (80-120)")
    
    print("\n📤 ZONE ANALYSIS OUTPUT:")
    for zone, data in zone_counts.items():
        print(f"{zone.title()} Third:")
        print(f"  Teammates: {data['teammates']}, Opponents: {data['opponents']}")
        advantage = data['advantage']
        if advantage > 0:
            print(f"  Advantage: Team +{advantage}")
        elif advantage < 0:
            print(f"  Advantage: Opponents +{abs(advantage)}")
        else:
            print("  Advantage: Balanced")
    
    # 5. SPATIAL INSIGHTS
    print("\n5️⃣ SPATIAL INSIGHTS GENERATION")
    print("=" * 50)
    
    insights = []
    
    # Pressure insight
    if total_pressure > 2.0:
        insights.append("High pressure situation - multiple defenders close")
    elif total_pressure > 1.0:
        insights.append("Moderate pressure - defenders nearby")
    else:
        insights.append("Low pressure - space available")
    
    # Location insight
    if kane_x > 100:
        insights.append("Shot from high-danger penalty area")
    elif kane_x > 80:
        insights.append("Shot from attacking third")
    
    # Zone insight
    attacking_adv = zone_counts['attacking']['advantage']
    if attacking_adv > 0:
        insights.append(f"Numerical advantage in attacking third (+{attacking_adv})")
    elif attacking_adv < 0:
        insights.append(f"Outnumbered in attacking third ({attacking_adv})")
    
    print("📥 INPUT:")
    print(f"Pressure score: {total_pressure:.2f}")
    print(f"Event location: [{kane_x}, {kane_y}]")
    print("Zone analysis data")
    
    print("\n📤 SPATIAL INSIGHTS:")
    for i, insight in enumerate(insights, 1):
        print(f"  {i}. {insight}")
    
    # 6. COMMENTARY GENERATION
    print("\n6️⃣ COMMENTARY GENERATION")
    print("=" * 50)
    
    # Generate commentary based on 360° data
    if total_pressure > 2.0:
        pressure_desc = "under intense pressure"
    elif total_pressure > 1.0:
        pressure_desc = "with defenders closing in"
    else:
        pressure_desc = "with space to work"
    
    location_desc = "in the penalty area" if kane_x > 100 else "in the attacking third"
    
    attacking_context = ""
    if attacking_adv > 0:
        attacking_context = f" England have a {attacking_adv}-player advantage in the final third."
    elif attacking_adv < 0:
        attacking_context = f" Netherlands have a {abs(attacking_adv)}-player advantage in the final third."
    
    commentary = f"Kane's shot comes from {location_desc}, {pressure_desc}. Spatial analysis shows {total_pressure:.1f} pressure points from nearby defenders.{attacking_context}"
    
    print("📥 INPUT:")
    print("All 360° analysis results combined")
    
    print("\n📤 GENERATED COMMENTARY:")
    print(f'"{commentary}"')
    
    # 7. COMPLETE SUMMARY
    print("\n🎯 COMPLETE 360° ANALYSIS SUMMARY")
    print("=" * 40)
    print("✅ Processing Pipeline:")
    print("  1. Raw freeze frame → Parse players")
    print("  2. Calculate pressure → Opponent proximity")
    print("  3. Analyze zones → Field dominance")
    print("  4. Generate insights → Tactical context")
    print("  5. Create commentary → Natural language")
    
    print("\n📊 Key Results:")
    print(f"  • Pressure Score: {total_pressure:.2f}/10")
    print(f"  • Pressure Players: {len(pressure_players)}")
    print(f"  • Attacking Advantage: {attacking_adv:+d}")
    print("  • Context: High-danger area shot")
    
    print("\n🔑 360° DATA BENEFITS:")
    print("• Quantifies defensive pressure objectively")
    print("• Identifies numerical advantages by field zone")
    print("• Provides spatial context for events")
    print("• Enhances commentary with tactical analysis")
    print("• Supports momentum prediction models")
    print("• Enables real-time spatial insights")

if __name__ == "__main__":
    main() 