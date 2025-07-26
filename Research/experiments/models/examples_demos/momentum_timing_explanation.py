#!/usr/bin/env python3
"""
Momentum Prediction Timing - 3-Minute Sliding Window Explained
Clear demonstration of input window vs output timing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def demonstrate_momentum_timing():
    """Show exactly how the 3-minute sliding window works"""
    
    print("⏰ MOMENTUM PREDICTION TIMING EXPLANATION")
    print("=" * 60)
    
    # Example timeline
    current_time = 1800  # 30:00 minutes into the match
    window_start = current_time - 180  # 27:00 (3 minutes ago)
    
    print(f"🎯 PREDICTION REQUEST: What's the momentum RIGHT NOW?")
    print(f"   Current Time: {current_time//60}:{current_time%60:02d} (30:00)")
    print()
    
    print(f"📥 INPUT DATA WINDOW: Last 3 minutes")
    print(f"   Window Start: {window_start//60}:{window_start%60:02d} (27:00)")
    print(f"   Window End:   {current_time//60}:{current_time%60:02d} (30:00)")
    print(f"   Window Size:  180 seconds (3 minutes)")
    print()
    
    # Sample events in the window
    sample_events = [
        {"time": "27:15", "event": "Pass", "team": "Netherlands"},
        {"time": "27:30", "event": "Shot", "team": "Netherlands"},
        {"time": "28:45", "event": "Carry", "team": "Netherlands"},
        {"time": "29:20", "event": "Pass", "team": "England"},
        {"time": "29:45", "event": "Dribble", "team": "Netherlands"},
        {"time": "30:00", "event": "Shot", "team": "Netherlands"}
    ]
    
    print("📊 SAMPLE EVENTS IN WINDOW:")
    for event in sample_events:
        print(f"   {event['time']} - {event['event']} by {event['team']}")
    print()
    
    # Feature extraction
    print("🔧 FEATURE EXTRACTION FROM 3-MINUTE WINDOW:")
    netherlands_events = [e for e in sample_events if e['team'] == 'Netherlands']
    england_events = [e for e in sample_events if e['team'] == 'England']
    
    features = {
        'total_events': len(netherlands_events),
        'shot_count': len([e for e in netherlands_events if e['event'] == 'Shot']),
        'possession_pct': len(netherlands_events) / len(sample_events) * 100,
        'attacking_actions': len([e for e in netherlands_events if e['event'] in ['Shot', 'Dribble', 'Carry']]),
        'events_per_minute': len(netherlands_events) / 3
    }
    
    for feature, value in features.items():
        print(f"   {feature:<20}: {value:.1f}")
    print()
    
    # Model prediction
    momentum_score = 7.2  # Example prediction
    
    print("🤖 MODEL PROCESSING:")
    print("   1. Analyze 3-minute feature patterns")
    print("   2. Random Forest makes prediction")
    print("   3. Apply 0-10 scale clipping")
    print()
    
    print("📤 OUTPUT - CURRENT MOMENTUM:")
    print(f"   Momentum Score: {momentum_score:.1f}/10")
    print(f"   Interpretation: HIGH MOMENTUM - Netherlands building pressure")
    print(f"   Timestamp: {current_time//60}:{current_time%60:02d} (RIGHT NOW)")
    print()
    
    print("🔄 SLIDING WINDOW BEHAVIOR:")
    print("=" * 40)
    
    time_examples = [
        (1800, "30:00", "Uses events from 27:00-30:00"),
        (1830, "30:30", "Uses events from 27:30-30:30"),
        (1860, "31:00", "Uses events from 28:00-31:00"),
        (1890, "31:30", "Uses events from 28:30-31:30")
    ]
    
    for time_sec, time_display, description in time_examples:
        window_start = time_sec - 180
        print(f"   At {time_display}: {description}")
        print(f"      Window: {window_start//60}:{window_start%60:02d} → {time_sec//60}:{time_sec%60:02d}")
    print()
    
    print("⚡ KEY INSIGHTS:")
    print("=" * 40)
    print("✅ INPUT: Historical data (last 3 minutes)")
    print("✅ OUTPUT: Current moment momentum (single point in time)")
    print("✅ WINDOW: Always moves forward with current time")
    print("✅ PREDICTION: 'How much momentum does team have RIGHT NOW?'")
    print("❌ NOT: 'What was the average momentum over 3 minutes?'")
    print()
    
    print("🎮 REAL-TIME APPLICATION:")
    print("=" * 40)
    print("• Live Commentary: 'Netherlands momentum surging (7.2/10)'")
    print("• Tactical Analysis: 'High pressure phase, expect goal attempt'")
    print("• Prediction Updates: Every few seconds with new events")
    print("• Context Awareness: Recent events weighted more heavily")

def compare_prediction_types():
    """Compare different types of predictions to clarify timing"""
    
    print("\n" + "=" * 60)
    print("🔍 PREDICTION TYPES COMPARISON")
    print("=" * 60)
    
    predictions = [
        {
            "type": "❌ WRONG INTERPRETATION",
            "question": "What will momentum be in next 3 minutes?",
            "input": "Current events",
            "output": "Future momentum (3-min period)",
            "note": "This is NOT what our model does!"
        },
        {
            "type": "❌ ALSO WRONG",
            "question": "What was average momentum over last 3 minutes?",
            "input": "Last 3 minutes events",
            "output": "Historical average momentum",
            "note": "This is also NOT what our model does!"
        },
        {
            "type": "✅ CORRECT - OUR MODEL",
            "question": "What is momentum RIGHT NOW?",
            "input": "Last 3 minutes events (context)",
            "output": "Current moment momentum score",
            "note": "Uses historical context to assess current state"
        }
    ]
    
    for pred in predictions:
        print(f"\n{pred['type']}:")
        print(f"   Question: {pred['question']}")
        print(f"   Input:    {pred['input']}")
        print(f"   Output:   {pred['output']}")
        print(f"   Note:     {pred['note']}")

def show_practical_example():
    """Show practical example with real timestamps"""
    
    print("\n" + "=" * 60)
    print("⚽ PRACTICAL EXAMPLE - Netherlands vs England")
    print("=" * 60)
    
    print("🕐 SCENARIO: 45th minute of match")
    print("   Current Time: 45:00")
    print("   Looking Back: 42:00 → 45:00 (3-minute window)")
    print()
    
    print("📊 EVENTS IN WINDOW (42:00-45:00):")
    events_data = {
        "42:15": "Netherlands - Pass",
        "42:30": "England - Pass", 
        "42:45": "Netherlands - Shot (MISS)",
        "43:20": "Netherlands - Carry",
        "43:35": "England - Pass",
        "44:10": "Netherlands - Dribble",
        "44:25": "Netherlands - Shot (SAVE)",
        "44:50": "Netherlands - Corner"
    }
    
    for timestamp, event in events_data.items():
        print(f"   {timestamp} - {event}")
    print()
    
    print("🎯 MODEL PREDICTION AT 45:00:")
    print("   Input:  All events from 42:00-45:00")
    print("   Output: Netherlands momentum = 8.1/10 RIGHT NOW")
    print("   Meaning: 'Netherlands has HIGH momentum at 45:00'")
    print("   NOT: 'Netherlands had high momentum for 3 minutes'")
    print("   NOT: 'Netherlands will have high momentum next 3 minutes'")

if __name__ == "__main__":
    demonstrate_momentum_timing()
    compare_prediction_types()
    show_practical_example() 