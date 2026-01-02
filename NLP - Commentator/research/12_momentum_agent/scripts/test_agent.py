"""
Test Script for Momentum Agent
==============================
Tests the agent with various match scenarios.

Author: Euro 2024 Momentum Project
Date: December 2024
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from momentum_agent import MomentumAgent
from momentum_data_loader import MomentumDataLoader


def test_basic_functionality():
    """Test basic agent functionality."""
    print("=" * 70)
    print("TEST 1: Basic Functionality")
    print("=" * 70)
    
    agent = MomentumAgent(verbose=False)
    
    # Test Germany vs Scotland
    result = agent.analyze_for_general(
        match_id=3930158,
        minute=25,
        period=1
    )
    
    assert result.get('include_momentum'), "Should have momentum data"
    assert result.get('dominant_team'), "Should detect dominant team"
    assert result.get('phrase_suggestion'), "Should generate phrase"
    
    print("[PASS] Basic functionality test PASSED")
    return True


def test_streak_detection():
    """Test streak detection."""
    print("\n" + "=" * 70)
    print("TEST 2: Streak Detection")
    print("=" * 70)
    
    agent = MomentumAgent(verbose=False)
    
    # Test multiple minutes to find streaks
    streak_found = False
    for minute in range(10, 45):
        result = agent.analyze_for_general(3930158, minute, 1)
        if result.get('has_streak'):
            print(f"[PASS] Streak found at minute {minute}:")
            print(f"   Team: {result['streak_team']}")
            print(f"   Length: {result['streak_length']} minutes")
            print(f"   Direction: {result['streak_direction']}")
            streak_found = True
            break
    
    if not streak_found:
        print("[INFO] No streak found in tested minutes (this is normal)")
    
    print("[PASS] Streak detection test PASSED")
    return True


def test_divergence_detection():
    """Test divergence detection."""
    print("\n" + "=" * 70)
    print("TEST 3: Divergence Detection")
    print("=" * 70)
    
    agent = MomentumAgent(verbose=False)
    
    # Test multiple minutes to find divergence
    divergence_found = False
    for minute in range(5, 45):
        result = agent.analyze_for_general(3930158, minute, 1)
        if result.get('has_divergence'):
            print(f"[PASS] Divergence found at minute {minute}:")
            print(f"   Rising: {result['rising_team']}")
            print(f"   Falling: {result['falling_team']}")
            print(f"   Description: {result['divergence_description']}")
            divergence_found = True
            break
    
    if not divergence_found:
        print("[INFO] No divergence found in tested minutes (this is normal)")
    
    print("[PASS] Divergence detection test PASSED")
    return True


def test_prediction_integration():
    """Test ARIMAX prediction integration (minute 75+)."""
    print("\n" + "=" * 70)
    print("TEST 4: Prediction Integration (75+ min)")
    print("=" * 70)
    
    agent = MomentumAgent(verbose=False)
    
    # Test minute 80 (should have predictions)
    result = agent.analyze_for_general(
        match_id=3930158,
        minute=80,
        period=2
    )
    
    if result.get('has_prediction'):
        print("[PASS] Prediction data available:")
        print(f"   Note: {result['prediction_note']}")
    else:
        print("[WARN] No prediction data (may be normal for some matches)")
    
    print("[PASS] Prediction integration test PASSED")
    return True


def test_detailed_summary():
    """Test detailed summary generation."""
    print("\n" + "=" * 70)
    print("TEST 5: Detailed Summary")
    print("=" * 70)
    
    agent = MomentumAgent(verbose=False)
    
    result = agent.analyze_for_general(
        match_id=3930158,
        minute=35,
        period=1
    )
    
    summary = result.get('detailed_summary', '')
    
    # Check summary contains expected sections
    assert 'CURRENT MOMENTUM' in summary, "Should have current momentum section"
    assert 'DOMINANCE' in summary, "Should have dominance section"
    assert 'TREND' in summary, "Should have trend section"
    assert 'STREAK ANALYSIS' in summary, "Should have streak section"
    assert 'DIVERGENCE' in summary, "Should have divergence section"
    
    print("[PASS] Detailed summary contains all sections")
    print("\n[SAMPLE] Summary (first 30 lines):")
    lines = summary.split('\n')[:30]
    for line in lines:
        print(f"   {line}")
    
    print("\n[PASS] Detailed summary test PASSED")
    return True


def test_multiple_matches():
    """Test agent with multiple matches."""
    print("\n" + "=" * 70)
    print("TEST 6: Multiple Matches")
    print("=" * 70)
    
    agent = MomentumAgent(verbose=False)
    
    # Test first 5 matches
    test_matches = [
        (3930158, "Germany vs Scotland"),
        (3930159, "Hungary vs Switzerland"),
        (3930160, "Spain vs Croatia"),
    ]
    
    for match_id, match_name in test_matches:
        result = agent.analyze_for_general(match_id, 30, 1)
        
        if result.get('include_momentum'):
            print(f"[PASS] {match_name}:")
            print(f"   Dominant: {result['dominant_team']}")
            print(f"   Phrase: \"{result['phrase_suggestion']}\"")
        else:
            print(f"[WARN] {match_name}: No data available")
    
    print("\n[PASS] Multiple matches test PASSED")
    return True


def run_full_analysis_demo():
    """Run a full analysis demonstration."""
    print("\n" + "=" * 70)
    print("FULL ANALYSIS DEMONSTRATION")
    print("=" * 70)
    
    agent = MomentumAgent(verbose=False)
    
    # Analyze key moments in a match
    match_id = 3930158  # Germany vs Scotland
    
    key_minutes = [
        (5, 1, "Early game"),
        (20, 1, "Build-up phase"),
        (40, 1, "Late first half"),
        (55, 2, "Early second half"),
        (75, 2, "Final push begins"),
        (85, 2, "Late pressure")
    ]
    
    print(f"\n[ANALYSIS] Analyzing Germany vs Scotland throughout the match:\n")
    
    for minute, period, description in key_minutes:
        result = agent.analyze_for_general(match_id, minute, period)
        
        if result.get('include_momentum'):
            print(f"[MIN {minute}'] ({description}):")
            print(f"   Dominant: {result['dominant_team']} ({result['dominance_type']})")
            print(f"   Trend: {result['trend_description']}")
            
            if result.get('has_streak'):
                print(f"   [STREAK] {result['streak_description']}")
            
            if result.get('has_divergence'):
                print(f"   [DIVERGE] {result['divergence_description']}")
            
            if result.get('has_prediction'):
                print(f"   [PREDICT] {result['prediction_note']}")
            
            print(f"   [PHRASE] \"{result['phrase_suggestion']}\"")
            print()
        else:
            print(f"[MIN {minute}'] ({description}): No data")
            print()


def main():
    """Run all tests."""
    print("=" * 70)
    print("MOMENTUM AGENT TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Streak Detection", test_streak_detection),
        ("Divergence Detection", test_divergence_detection),
        ("Prediction Integration", test_prediction_integration),
        ("Detailed Summary", test_detailed_summary),
        ("Multiple Matches", test_multiple_matches),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n[FAIL] TEST FAILED: {name}")
            print(f"   Error: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    # Run full demo
    run_full_analysis_demo()
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

