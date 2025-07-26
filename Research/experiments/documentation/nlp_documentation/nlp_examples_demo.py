#!/usr/bin/env python3
print("🔍 CONCRETE INPUT-OUTPUT EXAMPLES FOR NLP TECHNIQUES")
print("=" * 70)

# 1. RULE-BASED TEXT PROCESSING WITH DOMAIN VOCABULARY
print("\n1️⃣ RULE-BASED TEXT PROCESSING WITH DOMAIN VOCABULARY")
print("=" * 60)

domain_vocabulary = {
    'Pass': {'successful': 'completes a pass', 'failed': 'loses possession', 'progressive': 'plays progressive pass'},
    'Shot': {'on_target': 'forces a save', 'goal': 'finds the net', 'off_target': 'sends wide'},
    'Carry': {'progressive': 'drives forward', 'under_pressure': 'dribbles under pressure'},
    'Pressure': {'successful': 'wins ball back', 'failed': 'fails to regain'}
}

def process_with_vocabulary(event):
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

print("📥 INPUT → OUTPUT EXAMPLES:")
print()

examples = [
    {'player_name': 'Harry Kane', 'team_name': 'England', 'event_type': 'Pass', 'outcome': 'successful'},
    {'player_name': 'Jude Bellingham', 'team_name': 'England', 'event_type': 'Shot', 'outcome': 'on_target'},
    {'player_name': 'Van Dijk', 'team_name': 'Netherlands', 'event_type': 'Pressure', 'outcome': 'successful'}
]

for i, event in enumerate(examples, 1):
    print(f"Example {i}:")
    print(f"  📥 INPUT: {event}")
    output = process_with_vocabulary(event)
    print(f"  📤 OUTPUT: \"{output}\"")
    print()

# 2. TEMPLATE-BASED COMMENTARY GENERATION
print("2️⃣ TEMPLATE-BASED COMMENTARY GENERATION")
print("=" * 60)

templates = {
    'momentum_description': '{team} are {momentum_level} with momentum at {score:.1f}/10',
    'prediction': 'Model predicts {team} momentum will {trend} to {future_score:.1f}/10',
    'player_action': '{player} {action} in the {zone}'
}

momentum_levels = {
    (0, 2): 'struggling desperately',
    (2, 4): 'finding it difficult',
    (4, 6): 'in balanced contest',
    (6, 8): 'building momentum',
    (8, 10): 'completely dominating'
}

def get_momentum_level(score):
    for (min_val, max_val), description in momentum_levels.items():
        if min_val <= score < max_val:
            return description
    return 'maintaining level'

print("📥 INPUT → OUTPUT EXAMPLES:")
print()

template_examples = [
    {
        'template': 'momentum_description',
        'data': {'team': 'England', 'momentum_level': get_momentum_level(7.2), 'score': 7.2}
    },
    {
        'template': 'prediction', 
        'data': {'team': 'Netherlands', 'trend': 'increase', 'future_score': 6.8}
    },
    {
        'template': 'player_action',
        'data': {'player': 'Harry Kane', 'action': 'forces save', 'zone': 'attacking third'}
    }
]

for i, example in enumerate(template_examples, 1):
    print(f"Example {i}:")
    print(f"  📥 INPUT: Template='{example['template']}' Data={example['data']}")
    output = templates[example['template']].format(**example['data'])
    print(f"  📤 OUTPUT: \"{output}\"")
    print()

# 3. SIMPLE SENTIMENT SCORING
print("3️⃣ SIMPLE SENTIMENT SCORING")
print("=" * 60)

sentiment_weights = {
    'Pass': {'successful': 0.2, 'failed': -0.3, 'progressive': 0.4},
    'Shot': {'on_target': 0.8, 'goal': 1.0, 'off_target': -0.1},
    'Carry': {'progressive': 0.3, 'under_pressure': 0.1},
    'Pressure': {'successful': 0.3, 'failed': -0.2}
}

def calculate_sentiment(events):
    total = 0
    count = 0
    details = []
    
    for event in events:
        event_type = event['event_type']
        outcome = event['outcome']
        
        if event_type in sentiment_weights and outcome in sentiment_weights[event_type]:
            score = sentiment_weights[event_type][outcome]
            total += score
            count += 1
            details.append(f"{event['player_name']} {event_type} ({outcome}): {score:+.1f}")
    
    avg = total / count if count > 0 else 0
    return avg, details

print("📥 INPUT → OUTPUT EXAMPLES:")
print()

sentiment_examples = [
    {
        'name': 'England attacking sequence',
        'events': [
            {'player_name': 'Kane', 'event_type': 'Pass', 'outcome': 'progressive'},
            {'player_name': 'Bellingham', 'event_type': 'Carry', 'outcome': 'progressive'},
            {'player_name': 'Kane', 'event_type': 'Shot', 'outcome': 'on_target'}
        ]
    },
    {
        'name': 'Netherlands struggling',
        'events': [
            {'player_name': 'Gakpo', 'event_type': 'Pass', 'outcome': 'failed'},
            {'player_name': 'Depay', 'event_type': 'Shot', 'outcome': 'off_target'}
        ]
    }
]

for i, example in enumerate(sentiment_examples, 1):
    print(f"Example {i}: {example['name']}")
    print(f"  📥 INPUT: {len(example['events'])} events")
    for event in example['events']:
        print(f"    - {event['player_name']} {event['event_type']} ({event['outcome']})")
    
    avg_sentiment, details = calculate_sentiment(example['events'])
    print(f"  📤 OUTPUT:")
    print(f"    Overall Sentiment: {avg_sentiment:+.2f}")
    print(f"    Individual Scores:")
    for detail in details:
        print(f"      - {detail}")
    print()

# 4. CONTEXT PATTERN DETECTION
print("4️⃣ CONTEXT PATTERN DETECTION")
print("=" * 60)

def detect_patterns(events):
    event_types = [e['event_type'] for e in events]
    teams = [e['team_name'] for e in events]
    
    patterns = []
    
    if event_types.count('Shot') >= 2:
        patterns.append('attacking_surge')
    if event_types.count('Pressure') >= 2:
        patterns.append('defensive_pressure')
    if event_types.count('Pass') >= 3:
        patterns.append('possession_control')
    
    if teams:
        dominant_team = max(set(teams), key=teams.count)
        dominance = teams.count(dominant_team) / len(teams)
    else:
        dominant_team = 'Unknown'
        dominance = 0
    
    return {
        'patterns': patterns,
        'dominant_team': dominant_team,
        'dominance': dominance,
        'summary': f"{len(events)} events, {len(set(teams))} teams"
    }

print("📥 INPUT → OUTPUT EXAMPLES:")
print()

pattern_examples = [
    {
        'name': 'England attacking surge',
        'events': [
            {'player_name': 'Kane', 'team_name': 'England', 'event_type': 'Shot', 'outcome': 'on_target'},
            {'player_name': 'Foden', 'team_name': 'England', 'event_type': 'Shot', 'outcome': 'blocked'},
            {'player_name': 'Saka', 'team_name': 'England', 'event_type': 'Shot', 'outcome': 'off_target'}
        ]
    },
    {
        'name': 'Netherlands defensive pressure',
        'events': [
            {'player_name': 'Van Dijk', 'team_name': 'Netherlands', 'event_type': 'Pressure', 'outcome': 'successful'},
            {'player_name': 'De Jong', 'team_name': 'Netherlands', 'event_type': 'Pressure', 'outcome': 'intense'},
            {'player_name': 'Ake', 'team_name': 'Netherlands', 'event_type': 'Pressure', 'outcome': 'successful'}
        ]
    }
]

for i, example in enumerate(pattern_examples, 1):
    print(f"Example {i}: {example['name']}")
    print(f"  📥 INPUT: {len(example['events'])} events")
    for event in example['events']:
        print(f"    - {event['player_name']} ({event['team_name']}) {event['event_type']}")
    
    analysis = detect_patterns(example['events'])
    print(f"  📤 OUTPUT:")
    print(f"    Detected Patterns: {analysis['patterns']}")
    print(f"    Dominant Team: {analysis['dominant_team']} ({analysis['dominance']:.1%})")
    print(f"    Summary: {analysis['summary']}")
    print()

# 5. SPATIAL DATA INTEGRATION
print("5️⃣ SPATIAL DATA INTEGRATION")
print("=" * 60)

def integrate_spatial(event):
    x, y = event['location']
    
    # Field zones
    if x < 40:
        zone = 'defensive third'
    elif x < 80:
        zone = 'midfield'
    else:
        zone = 'attacking third'
    
    # Field sides
    if y < 20:
        side = 'left flank'
    elif y < 30:
        side = 'left channel'
    elif y < 50:
        side = 'central'
    elif y < 60:
        side = 'right channel'
    else:
        side = 'right flank'
    
    # Distance to goal (simplified)
    if event['team_name'] == 'England':
        goal_distance = round(((120 - x)**2 + (40 - y)**2)**0.5, 1)
    else:
        goal_distance = round(((0 - x)**2 + (40 - y)**2)**0.5, 1)
    
    # Danger level
    if zone == 'attacking third' and 30 <= y <= 50:
        danger = 'high'
    elif zone == 'attacking third':
        danger = 'medium'
    else:
        danger = 'low'
    
    return {
        'spatial_desc': f'{zone}, {side}',
        'coordinates': (x, y),
        'goal_distance': goal_distance,
        'danger_level': danger
    }

print("📥 INPUT → OUTPUT EXAMPLES:")
print()

spatial_examples = [
    {
        'name': 'Penalty area shot',
        'event': {'player_name': 'Kane', 'team_name': 'England', 'event_type': 'Shot', 'location': [112, 38]}
    },
    {
        'name': 'Midfield pass',
        'event': {'player_name': 'Bellingham', 'team_name': 'England', 'event_type': 'Pass', 'location': [65, 45]}
    },
    {
        'name': 'Wide attack',
        'event': {'player_name': 'Saka', 'team_name': 'England', 'event_type': 'Carry', 'location': [95, 15]}
    }
]

for i, example in enumerate(spatial_examples, 1):
    print(f"Example {i}: {example['name']}")
    event = example['event']
    print(f"  📥 INPUT: {event['player_name']} {event['event_type']} at {event['location']}")
    
    spatial = integrate_spatial(event)
    print(f"  �� OUTPUT:")
    print(f"    Spatial Description: {spatial['spatial_desc']}")
    print(f"    Coordinates: {spatial['coordinates']}")
    print(f"    Goal Distance: {spatial['goal_distance']}m")
    print(f"    Danger Level: {spatial['danger_level']}")
    print()

print("🎯 SUMMARY")
print("=" * 50)
print("✅ All 5 NLP techniques demonstrated with concrete examples:")
print("  1. Rule-based text processing → Natural language descriptions")
print("  2. Template-based commentary → Structured narratives")
print("  3. Simple sentiment scoring → Numerical momentum indicators")
print("  4. Context pattern detection → Tactical phase identification")
print("  5. Spatial data integration → Location-aware analysis")
print()
print("🔑 Key insight: Simple, domain-specific methods work effectively")
print("for soccer commentary and analysis applications!")