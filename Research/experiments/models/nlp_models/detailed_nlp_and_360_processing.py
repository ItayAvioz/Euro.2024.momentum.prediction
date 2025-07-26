#!/usr/bin/env python3
"""
Detailed NLP and 360° Data Processing Explanation
Step-by-step breakdown of text processing and spatial analysis methods
"""

import pandas as pd
import numpy as np
import json
import re
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class NLPAndSpatialProcessor:
    """
    Comprehensive processor for NLP and 360° spatial data analysis
    """
    
    def __init__(self):
        self.event_descriptions = {}
        self.tactical_vocabulary = {}
        self.momentum_descriptors = {}
        self.setup_language_models()
    
    def setup_language_models(self):
        """Step 1: Setup language processing components"""
        
        print("🔧 STEP 1: LANGUAGE MODEL SETUP")
        print("=" * 60)
        
        # Event type descriptions (domain-specific vocabulary)
        self.event_descriptions = {
            'Pass': {
                'base': 'passes the ball',
                'successful': 'completes a pass',
                'failed': 'loses possession with failed pass',
                'progressive': 'plays a progressive pass forward',
                'cross': 'delivers a cross into the box'
            },
            'Shot': {
                'base': 'takes a shot',
                'on_target': 'forces a save from the goalkeeper',
                'off_target': 'sends the shot wide',
                'blocked': 'has the shot blocked',
                'goal': 'finds the back of the net'
            },
            'Carry': {
                'base': 'carries the ball forward',
                'progressive': 'drives forward with the ball',
                'under_pressure': 'dribbles under pressure',
                'successful': 'advances with possession'
            },
            'Pressure': {
                'base': 'applies pressure',
                'successful': 'wins the ball back',
                'failed': 'fails to regain possession',
                'intense': 'puts intense pressure on'
            },
            'Dribble': {
                'base': 'attempts to dribble',
                'successful': 'beats the defender',
                'failed': 'is dispossessed',
                'skillful': 'shows great skill to beat'
            }
        }
        
        # Momentum descriptors
        self.momentum_descriptors = {
            'very_low': ['struggling', 'under pressure', 'defending desperately'],
            'low': ['on the back foot', 'finding it difficult', 'lacking rhythm'],
            'moderate': ['evenly matched', 'balanced contest', 'trading blows'],
            'high': ['building momentum', 'taking control', 'pressing forward'],
            'very_high': ['dominating', 'in complete control', 'overwhelming']
        }
        
        # Tactical vocabulary
        self.tactical_vocabulary = {
            'formations': ['4-3-3', '4-4-2', '3-5-2', '4-2-3-1'],
            'zones': ['final third', 'midfield', 'defensive third', 'penalty area'],
            'actions': ['counter-attack', 'build-up play', 'pressing', 'defending deep'],
            'qualities': ['pace', 'precision', 'intensity', 'creativity']
        }
        
        print("✅ Domain-specific vocabulary loaded")
        print(f"   - {len(self.event_descriptions)} event types")
        print(f"   - {len(self.momentum_descriptors)} momentum levels")
        print(f"   - {sum(len(v) for v in self.tactical_vocabulary.values())} tactical terms")
    
    def process_360_data_step_by_step(self, sample_360_data):
        """Step 2: Process 360° data with detailed explanations"""
        
        print("\n🌐 STEP 2: 360° SPATIAL DATA PROCESSING")
        print("=" * 60)
        
        # Sample 360° data structure
        print("📊 INPUT: 360° Data Structure")
        print("Raw 360° data contains:")
        print("- event_uuid: Links to main event")
        print("- freeze_frame: Array of player positions")
        print("- visible_area: Field visibility polygon")
        
        # Step 2a: Parse freeze frame data
        print("\n🔍 STEP 2A: FREEZE FRAME PARSING")
        print("-" * 40)
        
        freeze_frame_example = [
            {"location": [60.2, 40.1], "player": {"id": 123, "name": "Van Dijk"}, "teammate": True},
            {"location": [58.5, 35.8], "player": {"id": 456, "name": "Kane"}, "teammate": False},
            {"location": [65.3, 42.7], "player": {"id": 789, "name": "Bellingham"}, "teammate": False}
        ]
        
        print("Example freeze frame data:")
        for player in freeze_frame_example:
            team_status = "Teammate" if player["teammate"] else "Opponent"
            print(f"  {player['player']['name']} ({team_status}): {player['location']}")
        
        # Step 2b: Calculate spatial metrics
        print("\n📐 STEP 2B: SPATIAL CALCULATIONS")
        print("-" * 40)
        
        def calculate_pressure_score(player_pos, opponent_positions):
            """Calculate pressure based on nearby opponents"""
            pressure = 0
            for opp_pos in opponent_positions:
                distance = np.sqrt((player_pos[0] - opp_pos[0])**2 + (player_pos[1] - opp_pos[1])**2)
                if distance < 5:  # Within 5 meters
                    pressure += max(0, 5 - distance)  # Closer = more pressure
            return pressure
        
        # Extract positions
        player_pos = freeze_frame_example[0]["location"]  # Van Dijk
        opponent_positions = [p["location"] for p in freeze_frame_example if not p["teammate"]]
        
        pressure_score = calculate_pressure_score(player_pos, opponent_positions)
        
        print(f"Van Dijk position: {player_pos}")
        print(f"Opponent positions: {opponent_positions}")
        print(f"Calculated pressure score: {pressure_score:.2f}")
        
        # Step 2c: Zone analysis
        print("\n🗺️ STEP 2C: FIELD ZONE ANALYSIS")
        print("-" * 40)
        
        def determine_field_zone(x_coord, y_coord):
            """Determine which zone of the field the action occurs in"""
            # Field is 120m x 80m
            if x_coord < 40:
                zone = "Defensive Third"
            elif x_coord < 80:
                zone = "Midfield"
            else:
                zone = "Attacking Third"
            
            if y_coord < 18 or y_coord > 62:
                zone += " (Wide)"
            else:
                zone += " (Central)"
            
            return zone
        
        for player in freeze_frame_example:
            zone = determine_field_zone(player["location"][0], player["location"][1])
            print(f"  {player['player']['name']}: {zone}")
        
        return {
            'pressure_scores': [pressure_score],
            'zones': [determine_field_zone(p["location"][0], p["location"][1]) for p in freeze_frame_example],
            'player_positions': freeze_frame_example
        }
    
    def process_event_text_step_by_step(self, sample_events):
        """Step 3: Process event text data"""
        
        print("\n📝 STEP 3: EVENT TEXT PROCESSING")
        print("=" * 60)
        
        # Sample event data
        events_data = [
            {
                'minute': 23, 'second': 15, 'event_type': 'Pass',
                'player_name': 'Harry Kane', 'team_name': 'England',
                'outcome': 'successful', 'location': [75.2, 40.1]
            },
            {
                'minute': 23, 'second': 18, 'event_type': 'Shot',
                'player_name': 'Harry Kane', 'team_name': 'England',
                'outcome': 'on_target', 'location': [110.5, 38.2]
            },
            {
                'minute': 23, 'second': 22, 'event_type': 'Pressure',
                'player_name': 'Van Dijk', 'team_name': 'Netherlands',
                'outcome': 'successful', 'location': [110.8, 38.5]
            }
        ]
        
        print("📊 INPUT: Event Data Structure")
        print("Raw event data contains:")
        print("- Temporal: minute, second")
        print("- Spatial: x, y coordinates")
        print("- Contextual: player, team, outcome")
        print("- Semantic: event_type, result")
        
        # Step 3a: Text extraction and cleaning
        print("\n🧹 STEP 3A: TEXT EXTRACTION & CLEANING")
        print("-" * 40)
        
        def extract_event_text(event):
            """Extract meaningful text from event data"""
            base_text = f"{event['player_name']} ({event['team_name']})"
            
            # Add event description
            if event['event_type'] in self.event_descriptions:
                event_desc = self.event_descriptions[event['event_type']]
                if event['outcome'] in event_desc:
                    action = event_desc[event['outcome']]
                else:
                    action = event_desc['base']
            else:
                action = event['event_type'].lower()
            
            # Add location context
            zone = self.determine_field_zone(event['location'][0], event['location'][1])
            
            return f"{base_text} {action} in the {zone}"
        
        processed_events = []
        for event in events_data:
            event_text = extract_event_text(event)
            processed_events.append({
                'timestamp': f"{event['minute']:02d}:{event['second']:02d}",
                'raw_text': event_text,
                'event_type': event['event_type'],
                'team': event['team_name']
            })
            print(f"  {event_text}")
        
        # Step 3b: Semantic analysis
        print("\n🔍 STEP 3B: SEMANTIC ANALYSIS")
        print("-" * 40)
        
        def analyze_event_sentiment(events):
            """Analyze sentiment/momentum from events"""
            sentiment_scores = {
                'Pass': {'successful': 0.2, 'failed': -0.3},
                'Shot': {'on_target': 0.8, 'goal': 1.0, 'off_target': -0.1},
                'Pressure': {'successful': 0.3, 'failed': -0.2},
                'Dribble': {'successful': 0.4, 'failed': -0.2}
            }
            
            team_sentiment = {}
            for event in events_data:
                team = event['team_name']
                if team not in team_sentiment:
                    team_sentiment[team] = []
                
                event_type = event['event_type']
                outcome = event['outcome']
                
                if event_type in sentiment_scores and outcome in sentiment_scores[event_type]:
                    score = sentiment_scores[event_type][outcome]
                    team_sentiment[team].append(score)
            
            return team_sentiment
        
        sentiment_analysis = analyze_event_sentiment(events_data)
        for team, scores in sentiment_analysis.items():
            avg_sentiment = np.mean(scores)
            print(f"  {team}: Average sentiment = {avg_sentiment:.2f}")
        
        return processed_events, sentiment_analysis
    
    def generate_commentary_step_by_step(self, events, momentum_data):
        """Step 4: Generate commentary using NLP techniques"""
        
        print("\n🎙️ STEP 4: COMMENTARY GENERATION")
        print("=" * 60)
        
        # Step 4a: Template-based generation
        print("🔤 STEP 4A: TEMPLATE-BASED GENERATION")
        print("-" * 40)
        
        commentary_templates = {
            'momentum_shift': "{team} {momentum_descriptor} with {key_stats}",
            'action_sequence': "{player} {action} and {result}",
            'tactical_analysis': "{team} {tactical_approach} in the {field_zone}",
            'pressure_situation': "{team} {pressure_level} from {opponent}"
        }
        
        def select_momentum_descriptor(momentum_score):
            """Select appropriate descriptor based on momentum score"""
            if momentum_score < 2:
                return np.random.choice(self.momentum_descriptors['very_low'])
            elif momentum_score < 4:
                return np.random.choice(self.momentum_descriptors['low'])
            elif momentum_score < 6:
                return np.random.choice(self.momentum_descriptors['moderate'])
            elif momentum_score < 8:
                return np.random.choice(self.momentum_descriptors['high'])
            else:
                return np.random.choice(self.momentum_descriptors['very_high'])
        
        # Example commentary generation
        momentum_score = 7.2
        descriptor = select_momentum_descriptor(momentum_score)
        
        commentary = commentary_templates['momentum_shift'].format(
            team="England",
            momentum_descriptor=descriptor,
            key_stats=f"momentum at {momentum_score:.1f}/10"
        )
        
        print(f"Generated commentary: '{commentary}'")
        
        # Step 4b: Context-aware generation
        print("\n🧠 STEP 4B: CONTEXT-AWARE GENERATION")
        print("-" * 40)
        
        def generate_contextual_commentary(events, momentum_data):
            """Generate commentary based on context"""
            recent_events = events[-3:]  # Last 3 events
            
            # Analyze recent pattern
            event_types = [e['event_type'] for e in recent_events]
            teams = [e['team'] for e in recent_events]
            
            # Pattern detection
            if event_types.count('Shot') >= 2:
                pattern = "shooting_spree"
            elif event_types.count('Pass') >= 2:
                pattern = "possession_play"
            elif event_types.count('Pressure') >= 2:
                pattern = "high_pressure"
            else:
                pattern = "mixed_play"
            
            # Generate context-specific commentary
            context_templates = {
                'shooting_spree': "Plenty of shooting opportunities here for {team}",
                'possession_play': "{team} patiently building their attacks",
                'high_pressure': "Intense pressure from both teams",
                'mixed_play': "End-to-end action in this phase"
            }
            
            dominant_team = max(set(teams), key=teams.count)
            contextual_commentary = context_templates[pattern].format(team=dominant_team)
            
            return contextual_commentary
        
        # Generate contextual commentary
        sample_events = [
            {'event_type': 'Pass', 'team': 'England'},
            {'event_type': 'Shot', 'team': 'England'},
            {'event_type': 'Shot', 'team': 'England'}
        ]
        
        contextual_commentary = generate_contextual_commentary(sample_events, momentum_data)
        print(f"Contextual commentary: '{contextual_commentary}'")
        
        # Step 4c: Momentum-based narrative
        print("\n📈 STEP 4C: MOMENTUM-BASED NARRATIVE")
        print("-" * 40)
        
        def create_momentum_narrative(current_momentum, future_momentum, team):
            """Create narrative based on momentum trend"""
            
            momentum_change = future_momentum - current_momentum
            
            if momentum_change > 0.5:
                trend = "building"
                narrative = f"{team} are really building momentum now"
            elif momentum_change < -0.5:
                trend = "declining"
                narrative = f"{team} seem to be losing their grip on this game"
            else:
                trend = "stable"
                narrative = f"{team} maintaining their current level"
            
            # Add specific details
            detailed_narrative = f"""
            {narrative}. Current momentum sits at {current_momentum:.1f}/10, 
            and our model predicts this will {'increase' if momentum_change > 0 else 'decrease'} 
            to {future_momentum:.1f}/10 in the next three minutes.
            """
            
            return detailed_narrative.strip()
        
        # Generate momentum narrative
        momentum_narrative = create_momentum_narrative(6.8, 7.2, "Netherlands")
        print(f"Momentum narrative: {momentum_narrative}")
        
        return {
            'template_commentary': commentary,
            'contextual_commentary': contextual_commentary,
            'momentum_narrative': momentum_narrative
        }
    
    def determine_field_zone(self, x_coord, y_coord):
        """Helper function to determine field zone"""
        if x_coord < 40:
            return "defensive third"
        elif x_coord < 80:
            return "midfield"
        else:
            return "attacking third"
    
    def advanced_nlp_techniques(self):
        """Step 5: Advanced NLP techniques used"""
        
        print("\n🤖 STEP 5: ADVANCED NLP TECHNIQUES")
        print("=" * 60)
        
        print("🔍 TECHNIQUES ACTUALLY IMPLEMENTED:")
        print("-" * 40)
        
        techniques = {
            'Domain-Specific Vocabulary': {
                'description': 'Custom soccer terminology and event descriptions',
                'implementation': 'Dictionary-based lookup with context',
                'example': 'Pass -> "completes a pass" vs "loses possession"'
            },
            'Template-Based Generation': {
                'description': 'Structured templates with variable insertion',
                'implementation': 'String formatting with contextual variables',
                'example': '{team} {momentum_descriptor} with {key_stats}'
            },
            'Context-Aware Processing': {
                'description': 'Commentary based on recent event patterns',
                'implementation': 'Pattern detection in event sequences',
                'example': 'Multiple shots -> "shooting spree" commentary'
            },
            'Sentiment Analysis': {
                'description': 'Event outcome to momentum scoring',
                'implementation': 'Rule-based sentiment scoring',
                'example': 'Goal = +1.0, Miss = -0.1'
            },
            'Temporal Language Processing': {
                'description': 'Time-based narrative generation',
                'implementation': 'Trend analysis for future predictions',
                'example': 'Momentum increasing -> "building momentum"'
            }
        }
        
        for technique, details in techniques.items():
            print(f"\n✅ {technique}:")
            print(f"   Description: {details['description']}")
            print(f"   Implementation: {details['implementation']}")
            print(f"   Example: {details['example']}")
        
        print("\n🚫 TECHNIQUES NOT IMPLEMENTED:")
        print("-" * 40)
        not_implemented = [
            'Large Language Models (GPT, BERT)',
            'Deep Learning Text Generation',
            'Named Entity Recognition',
            'Advanced Sentiment Analysis Models',
            'Text Classification Models',
            'Word Embeddings (Word2Vec, GloVe)',
            'Transformer Models'
        ]
        
        for technique in not_implemented:
            print(f"❌ {technique}")
        
        print("\n💡 RATIONALE:")
        print("-" * 40)
        print("The project focused on:")
        print("1. Rule-based NLP for reliability and control")
        print("2. Domain-specific vocabulary for accuracy")
        print("3. Template-based generation for consistency")
        print("4. Context-aware processing for relevance")
        print("5. Integration with momentum prediction models")
    
    def complete_processing_pipeline(self):
        """Complete end-to-end processing pipeline"""
        
        print("\n🔄 COMPLETE PROCESSING PIPELINE")
        print("=" * 60)
        
        pipeline_steps = [
            "1. Raw Data Input (Events + 360° Data)",
            "2. Spatial Analysis (Pressure, Zones, Positions)",
            "3. Event Text Processing (Description, Context)",
            "4. Sentiment Analysis (Momentum Scoring)",
            "5. Feature Engineering (Temporal, Spatial, Contextual)",
            "6. Model Prediction (Current + Future Momentum)",
            "7. Commentary Generation (Template + Context)",
            "8. Output Integration (Predictions + Commentary)"
        ]
        
        for step in pipeline_steps:
            print(f"  {step}")
        
        print("\n📊 DATA FLOW:")
        print("-" * 20)
        print("StatsBomb Data → Event Parser → Spatial Analyzer → ")
        print("Text Processor → Sentiment Analyzer → Feature Engineer → ")
        print("ML Model → Commentary Generator → Final Output")

def main():
    """Run complete NLP and 360° processing demonstration"""
    
    processor = NLPAndSpatialProcessor()
    
    # Run all processing steps
    sample_360_data = {"freeze_frame": [], "visible_area": []}
    sample_events = []
    
    # Step 1: Language model setup (already done in __init__)
    
    # Step 2: 360° data processing
    spatial_results = processor.process_360_data_step_by_step(sample_360_data)
    
    # Step 3: Event text processing
    text_results, sentiment_results = processor.process_event_text_step_by_step(sample_events)
    
    # Step 4: Commentary generation
    momentum_data = {'current': 6.8, 'future': 7.2}
    commentary_results = processor.generate_commentary_step_by_step(text_results, momentum_data)
    
    # Step 5: Advanced NLP techniques
    processor.advanced_nlp_techniques()
    
    # Step 6: Complete pipeline
    processor.complete_processing_pipeline()
    
    print("\n🎯 SUMMARY")
    print("=" * 60)
    print("This demonstration shows the actual NLP and 360° processing")
    print("methods used in the soccer analytics project:")
    print("✅ Spatial analysis of player positions")
    print("✅ Rule-based text processing")
    print("✅ Template-based commentary generation")
    print("✅ Context-aware narrative creation")
    print("✅ Integration with momentum prediction models")

if __name__ == "__main__":
    main() 