#!/usr/bin/env python3
"""
Practical Examples: Parsing 360° Data and Events
Step-by-step examples of decoding complex data structures
"""

import pandas as pd
import numpy as np
import json
import ast
import math

def parse_freeze_frame_detailed():
    """Detailed example of parsing freeze frame data"""
    print("🔍 DETAILED FREEZE FRAME PARSING EXAMPLES")
    print("=" * 55)
    
    # Load actual freeze frame data
    try:
        df_360 = pd.read_csv('euro_2024_complete/data_360_complete.csv', nrows=3)
        print(f"✅ Loaded {len(df_360)} real freeze frames")
        
        for i, row in df_360.iterrows():
            print(f"\n📊 FREEZE FRAME {i+1}:")
            print(f"   Match ID: {row['match_id']}")
            print(f"   Teams: {row['home_team']} vs {row['away_team']}")
            
            # Parse freeze frame
            freeze_frame = row['freeze_frame']
            print(f"   Raw data type: {type(freeze_frame)}")
            
            # Convert string to list of dictionaries
            if isinstance(freeze_frame, str):
                try:
                    players_data = ast.literal_eval(freeze_frame)
                    print(f"   ✅ Parsed {len(players_data)} players")
                    
                    # Analyze each player
                    teammates = []
                    opponents = []
                    keepers = []
                    actor = None
                    
                    for j, player in enumerate(players_data):
                        player_info = {
                            'index': j,
                            'x': player['location'][0],
                            'y': player['location'][1],
                            'is_teammate': player['teammate'],
                            'is_actor': player['actor'],
                            'is_keeper': player['keeper']
                        }
                        
                        if player['actor']:
                            actor = player_info
                        elif player['keeper']:
                            keepers.append(player_info)
                        elif player['teammate']:
                            teammates.append(player_info)
                        else:
                            opponents.append(player_info)
                    
                    print(f"   👤 Actor: {actor['x']:.1f}, {actor['y']:.1f}" if actor else "   👤 No actor found")
                    print(f"   🥅 Keepers: {len(keepers)}")
                    print(f"   🔵 Teammates: {len(teammates)}")
                    print(f"   🔴 Opponents: {len(opponents)}")
                    
                    # Show spatial analysis
                    if actor:
                        print(f"   📐 SPATIAL ANALYSIS:")
                        
                        # Find nearest opponents
                        if opponents:
                            distances = []
                            for opp in opponents:
                                dist = math.sqrt((actor['x'] - opp['x'])**2 + (actor['y'] - opp['y'])**2)
                                distances.append(dist)
                            
                            nearest_dist = min(distances)
                            print(f"      🔴 Nearest opponent: {nearest_dist:.1f}m away")
                            
                            if nearest_dist < 3:
                                print(f"      ⚠️ Under pressure!")
                            elif nearest_dist > 10:
                                print(f"      ✅ Lots of space!")
                            else:
                                print(f"      ⚖️ Moderate pressure")
                        
                        # Calculate field position
                        field_third = "Defensive" if actor['x'] < 40 else "Middle" if actor['x'] < 80 else "Attacking"
                        print(f"      📍 Field position: {field_third} third")
                        
                        # Distance to goal
                        goal_dist = math.sqrt((120 - actor['x'])**2 + (40 - actor['y'])**2)
                        print(f"      🥅 Distance to goal: {goal_dist:.1f}m")
                    
                except Exception as e:
                    print(f"   ❌ Error parsing: {e}")
        
    except Exception as e:
        print(f"❌ Could not load 360° data: {e}")
        demonstrate_parsing_with_example()

def demonstrate_parsing_with_example():
    """Demonstrate parsing with example data"""
    print("\n📝 EXAMPLE FREEZE FRAME PARSING:")
    
    # Example freeze frame data
    example_frame = """[
        {'teammate': True, 'actor': True, 'keeper': False, 'location': [45.2, 35.8]},
        {'teammate': True, 'actor': False, 'keeper': True, 'location': [12.1, 40.0]},
        {'teammate': True, 'actor': False, 'keeper': False, 'location': [35.7, 25.4]},
        {'teammate': False, 'actor': False, 'keeper': False, 'location': [48.9, 39.6]},
        {'teammate': False, 'actor': False, 'keeper': False, 'location': [52.3, 42.1]}
    ]"""
    
    print(f"Raw freeze frame:")
    print(example_frame)
    
    # Parse the data
    players = ast.literal_eval(example_frame)
    print(f"\n✅ Parsed {len(players)} players:")
    
    for i, player in enumerate(players):
        role = "⚽ ACTOR" if player['actor'] else "🥅 KEEPER" if player['keeper'] else "👤 PLAYER"
        team = "🔵 TEAM" if player['teammate'] else "🔴 OPPONENT"
        x, y = player['location']
        print(f"   {i+1}. {role} {team} at ({x:.1f}, {y:.1f})")

def create_spatial_analysis_functions():
    """Create functions for spatial analysis"""
    print("\n🧮 SPATIAL ANALYSIS FUNCTIONS")
    print("=" * 40)
    
    def calculate_pressure(actor_pos, opponent_positions):
        """Calculate pressure on a player"""
        if not opponent_positions:
            return 0
        
        distances = []
        for opp_pos in opponent_positions:
            dist = math.sqrt((actor_pos[0] - opp_pos[0])**2 + (actor_pos[1] - opp_pos[1])**2)
            distances.append(dist)
        
        # Pressure inversely related to distance
        nearest_dist = min(distances)
        pressure_score = max(0, 10 - nearest_dist)  # Scale 0-10
        return pressure_score
    
    def calculate_space_available(actor_pos, all_positions):
        """Calculate available space around player"""
        if not all_positions:
            return 10  # Maximum space if no other players
        
        distances = []
        for pos in all_positions:
            if pos != actor_pos:  # Don't include self
                dist = math.sqrt((actor_pos[0] - pos[0])**2 + (actor_pos[1] - pos[1])**2)
                distances.append(dist)
        
        # Space based on nearest player
        if distances:
            nearest_dist = min(distances)
            return min(10, nearest_dist)  # Cap at 10m
        return 10
    
    def get_field_zone(x, y):
        """Get field zone for position"""
        # Divide field into zones
        zone_x = "Defensive" if x < 40 else "Middle" if x < 80 else "Attacking"
        zone_y = "Left" if y < 26.7 else "Center" if y < 53.3 else "Right"
        return f"{zone_x} {zone_y}"
    
    def calculate_goal_angle(x, y):
        """Calculate angle to goal"""
        # Goal posts at (120, 36) and (120, 44)
        goal_left = (120, 36)
        goal_right = (120, 44)
        
        # Calculate angle using vectors
        vec_left = (goal_left[0] - x, goal_left[1] - y)
        vec_right = (goal_right[0] - x, goal_right[1] - y)
        
        # Calculate angle between vectors
        dot_product = vec_left[0] * vec_right[0] + vec_left[1] * vec_right[1]
        mag_left = math.sqrt(vec_left[0]**2 + vec_left[1]**2)
        mag_right = math.sqrt(vec_right[0]**2 + vec_right[1]**2)
        
        cos_angle = dot_product / (mag_left * mag_right)
        angle_rad = math.acos(max(-1, min(1, cos_angle)))
        angle_deg = math.degrees(angle_rad)
        
        return angle_deg
    
    # Demonstrate functions
    print("📊 EXAMPLE CALCULATIONS:")
    
    # Example positions
    actor_pos = (45.2, 35.8)
    opponent_positions = [(48.9, 39.6), (52.3, 42.1), (41.7, 33.2)]
    all_positions = [actor_pos] + opponent_positions + [(35.7, 25.4), (12.1, 40.0)]
    
    pressure = calculate_pressure(actor_pos, opponent_positions)
    space = calculate_space_available(actor_pos, all_positions)
    zone = get_field_zone(actor_pos[0], actor_pos[1])
    goal_angle = calculate_goal_angle(actor_pos[0], actor_pos[1])
    
    print(f"   Position: ({actor_pos[0]}, {actor_pos[1]})")
    print(f"   Pressure: {pressure:.1f}/10")
    print(f"   Space: {space:.1f}m")
    print(f"   Zone: {zone}")
    print(f"   Goal angle: {goal_angle:.1f}°")

def demonstrate_commentary_generation():
    """Demonstrate commentary generation with spatial context"""
    print("\n🎙️ COMMENTARY GENERATION WITH SPATIAL CONTEXT")
    print("=" * 50)
    
    # Load sample events
    try:
        events_df = pd.read_csv('euro_2024_sample_100_rows.csv')
        print(f"✅ Loaded {len(events_df)} events")
        
        # Generate commentary for different scenarios
        print("\n📝 COMMENTARY EXAMPLES:")
        
        scenarios = [
            {
                'event_type': 'Pass',
                'player': 'Jude Bellingham',
                'position': (45.2, 35.8),
                'pressure': 2.1,
                'space': 8.5,
                'minute': 23,
                'second': 15
            },
            {
                'event_type': 'Shot',
                'player': 'Harry Kane',
                'position': (105.3, 38.2),
                'pressure': 8.7,
                'space': 2.1,
                'minute': 67,
                'second': 43
            },
            {
                'event_type': 'Carry',
                'player': 'Pedri',
                'position': (67.8, 45.2),
                'pressure': 1.5,
                'space': 12.3,
                'minute': 34,
                'second': 27
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n   {i}. {scenario['event_type'].upper()} SCENARIO:")
            print(f"      Player: {scenario['player']}")
            print(f"      Position: ({scenario['position'][0]:.1f}, {scenario['position'][1]:.1f})")
            print(f"      Time: {scenario['minute']}:{scenario['second']:02d}")
            
            # Generate contextual commentary
            if scenario['pressure'] < 3:
                pressure_desc = "with plenty of time"
            elif scenario['pressure'] < 7:
                pressure_desc = "under moderate pressure"
            else:
                pressure_desc = "under intense pressure"
            
            if scenario['space'] > 10:
                space_desc = "in acres of space"
            elif scenario['space'] > 5:
                space_desc = "with some room to work"
            else:
                space_desc = "in tight quarters"
            
            # Event-specific commentary
            if scenario['event_type'] == 'Pass':
                commentary = f"⚽ {scenario['player']} {pressure_desc}, looks to distribute the ball {space_desc} in minute {scenario['minute']}"
            elif scenario['event_type'] == 'Shot':
                commentary = f"🎯 {scenario['player']} shoots {pressure_desc} from {space_desc} - minute {scenario['minute']}!"
            elif scenario['event_type'] == 'Carry':
                commentary = f"🏃 {scenario['player']} drives forward {pressure_desc} {space_desc} in minute {scenario['minute']}"
            
            print(f"      💬 Commentary: {commentary}")
        
    except Exception as e:
        print(f"❌ Error loading events: {e}")

def demonstrate_move_quality_prediction():
    """Demonstrate move quality prediction using spatial data"""
    print("\n🔮 MOVE QUALITY PREDICTION EXAMPLES")
    print("=" * 40)
    
    print("📊 PASS QUALITY PREDICTION:")
    
    # Example pass scenarios
    pass_scenarios = [
        {
            'passer_pos': (45.2, 35.8),
            'receiver_pos': (65.3, 42.1),
            'opponent_positions': [(48.9, 39.6), (52.3, 42.1), (58.7, 40.2)],
            'description': 'Medium pass through midfield'
        },
        {
            'passer_pos': (85.7, 25.4),
            'receiver_pos': (102.1, 38.9),
            'opponent_positions': [(88.2, 28.7), (95.4, 35.1), (98.7, 41.2)],
            'description': 'Final third through ball'
        },
        {
            'passer_pos': (25.8, 15.2),
            'receiver_pos': (75.3, 65.7),
            'opponent_positions': [(28.4, 18.9), (35.7, 25.4), (42.1, 35.8)],
            'description': 'Long diagonal switch'
        }
    ]
    
    for i, scenario in enumerate(pass_scenarios, 1):
        print(f"\n   {i}. {scenario['description'].upper()}:")
        
        passer_pos = scenario['passer_pos']
        receiver_pos = scenario['receiver_pos']
        opponents = scenario['opponent_positions']
        
        # Calculate pass features
        pass_distance = math.sqrt((receiver_pos[0] - passer_pos[0])**2 + (receiver_pos[1] - passer_pos[1])**2)
        
        # Pressure on passer
        passer_pressure = min([math.sqrt((passer_pos[0] - opp[0])**2 + (passer_pos[1] - opp[1])**2) for opp in opponents])
        
        # Space for receiver
        receiver_space = min([math.sqrt((receiver_pos[0] - opp[0])**2 + (receiver_pos[1] - opp[1])**2) for opp in opponents])
        
        # Defenders in passing lane
        defenders_in_lane = 0
        for opp in opponents:
            # Simple check if opponent is roughly in the passing lane
            if (min(passer_pos[0], receiver_pos[0]) <= opp[0] <= max(passer_pos[0], receiver_pos[0]) and
                min(passer_pos[1], receiver_pos[1]) <= opp[1] <= max(passer_pos[1], receiver_pos[1])):
                defenders_in_lane += 1
        
        # Simple quality score (0-10)
        distance_factor = max(0, 10 - pass_distance/10)  # Shorter passes generally easier
        pressure_factor = min(10, passer_pressure)  # More pressure = harder
        space_factor = min(10, receiver_space)  # More space = easier
        lane_factor = max(0, 10 - defenders_in_lane * 3)  # Fewer defenders = easier
        
        quality_score = (distance_factor + pressure_factor + space_factor + lane_factor) / 4
        
        print(f"      📏 Pass distance: {pass_distance:.1f}m")
        print(f"      ⚠️ Passer pressure: {passer_pressure:.1f}m to nearest opponent")
        print(f"      🎯 Receiver space: {receiver_space:.1f}m to nearest opponent")
        print(f"      🛡️ Defenders in lane: {defenders_in_lane}")
        print(f"      🎲 Quality score: {quality_score:.1f}/10")
        
        if quality_score > 7:
            print(f"      ✅ High probability pass")
        elif quality_score > 4:
            print(f"      ⚖️ Moderate difficulty pass")
        else:
            print(f"      ❌ High risk pass")

def main():
    """Main demonstration function"""
    print("🔍 PRACTICAL PARSING AND ANALYSIS EXAMPLES")
    print("=" * 60)
    print("📊 Step-by-step examples of working with 360° data and events")
    print()
    
    # Run all demonstrations
    parse_freeze_frame_detailed()
    create_spatial_analysis_functions()
    demonstrate_commentary_generation()
    demonstrate_move_quality_prediction()
    
    print("\n✅ PRACTICAL EXAMPLES COMPLETE!")
    print("🎯 You now have:")
    print("   1. Detailed freeze frame parsing methods")
    print("   2. Spatial analysis functions")
    print("   3. Commentary generation with context")
    print("   4. Move quality prediction examples")
    print("   5. Real-world application patterns")

if __name__ == "__main__":
    main() 