import numpy as np

def calculate_basic_momentum(team_shots, team_possession, team_attacks):
    """Old approach - only team data"""
    return (team_shots * 1.5 + team_attacks * 0.15 + team_possession * 0.03)

def calculate_enhanced_momentum(team_data, opponent_data):
    """New approach - team vs opponent"""
    # Team performance
    team_score = (team_data['shots'] * 1.2 + 
                  team_data['attacks'] * 0.1 + 
                  team_data['possession'] * 0.02)
    
    # Opponent pressure (reduces momentum)
    opponent_pressure = (opponent_data['shots'] * 0.8 + 
                        opponent_data['attacks'] * 0.08)
    
    # Relative advantages (KEY!)
    shot_advantage = (team_data['shots'] - opponent_data['shots']) * 0.8
    possession_advantage = (team_data['possession'] - opponent_data['possession']) * 0.01
    attack_advantage = (team_data['attacks'] - opponent_data['attacks']) * 0.06
    
    # Final momentum
    momentum = team_score - opponent_pressure * 0.3 + shot_advantage + possession_advantage + attack_advantage
    return max(0, min(10, momentum))

def main():
    print("🎯 WHY OPPONENT DATA MATTERS: MOMENTUM IS RELATIVE!")
    print("=" * 70)
    
    print("\n💡 THE PROBLEM WITH OLD APPROACH:")
    print("   Team has 3 shots, 60% possession, 12 attacks")
    print("   → Always same momentum score")
    print("   ❌ But context matters! 3 shots vs weak/strong opponent = different!")
    
    print("\n🔥 THE SOLUTION: COMPARE WITH OPPONENT")
    print("=" * 70)
    
    # Same team performance, different opponents
    team_stats = {'shots': 3, 'possession': 60, 'attacks': 12}
    
    scenarios = [
        {
            'name': 'vs Weak Opponent',
            'opponent': {'shots': 0, 'possession': 40, 'attacks': 4},
            'context': 'Team dominating, opponent struggling'
        },
        {
            'name': 'vs Balanced Opponent', 
            'opponent': {'shots': 2, 'possession': 40, 'attacks': 8},
            'context': 'Even match, slight team advantage'
        },
        {
            'name': 'vs Strong Opponent',
            'opponent': {'shots': 5, 'possession': 40, 'attacks': 15},
            'context': 'Team under pressure, opponent attacking'
        }
    ]
    
    print(f"\n📊 TEAM PERFORMANCE (CONSTANT):")
    print(f"   Shots: {team_stats['shots']}")
    print(f"   Possession: {team_stats['possession']}%")
    print(f"   Attacks: {team_stats['attacks']}")
    
    # Calculate old approach (same for all)
    old_momentum = calculate_basic_momentum(
        team_stats['shots'], 
        team_stats['possession'], 
        team_stats['attacks']
    )
    
    print(f"\n❌ OLD APPROACH (ignores opponent):")
    print(f"   Momentum: {old_momentum:.2f}/10 (same in all scenarios)")
    
    print(f"\n✅ NEW APPROACH (includes opponent):")
    print("=" * 70)
    
    for i, scenario in enumerate(scenarios, 1):
        opponent = scenario['opponent']
        
        print(f"\n🎮 SCENARIO {i}: {scenario['name']}")
        print(f"💭 Context: {scenario['context']}")
        
        print(f"\n📊 HEAD-TO-HEAD:")
        print(f"                TEAM    OPPONENT   ADVANTAGE")
        print(f"   Shots      :   {team_stats['shots']:2d}   vs   {opponent['shots']:2d}      ({team_stats['shots'] - opponent['shots']:+2d})")
        print(f"   Possession : {team_stats['possession']:4.0f}%  vs {opponent['possession']:4.0f}%     ({team_stats['possession'] - opponent['possession']:+4.0f}%)")
        print(f"   Attacks    :   {team_stats['attacks']:2d}   vs   {opponent['attacks']:2d}      ({team_stats['attacks'] - opponent['attacks']:+2d})")
        
        # Calculate enhanced momentum
        enhanced_momentum = calculate_enhanced_momentum(team_stats, opponent)
        
        # Interpretation
        if enhanced_momentum >= 7.5:
            interpretation = "🔥 HIGH MOMENTUM - Clear dominance"
        elif enhanced_momentum >= 5.5:
            interpretation = "📈 MODERATE MOMENTUM - Slight advantage"
        elif enhanced_momentum >= 3.5:
            interpretation = "⚖️ BALANCED MOMENTUM - Even contest"
        else:
            interpretation = "📉 LOW MOMENTUM - Under pressure"
        
        print(f"\n🎯 ENHANCED MOMENTUM:")
        print(f"   Score: {enhanced_momentum:.2f}/10")
        print(f"   Analysis: {interpretation}")
        
        # Show key factors
        shot_adv = team_stats['shots'] - opponent['shots']
        if shot_adv >= 2:
            print(f"   ✅ Shot advantage (+{shot_adv}) boosts momentum")
        elif shot_adv <= -1:
            print(f"   ⚠️ Shot disadvantage ({shot_adv}) reduces momentum")
        
        attack_adv = team_stats['attacks'] - opponent['attacks']
        if attack_adv >= 3:
            print(f"   ✅ Attack superiority (+{attack_adv}) adds momentum")
        elif attack_adv <= -3:
            print(f"   ⚠️ Attack deficit ({attack_adv}) hurts momentum")
    
    print(f"\n" + "=" * 70)
    print("🧠 KEY INSIGHTS FROM OPPONENT DATA")
    print("=" * 70)
    
    print(f"\n🎯 SAME TEAM STATS, DIFFERENT MOMENTUM:")
    enhanced_scores = []
    for scenario in scenarios:
        score = calculate_enhanced_momentum(team_stats, scenario['opponent'])
        enhanced_scores.append(score)
        print(f"   {scenario['name']:<20}: {score:.2f}/10")
    
    momentum_range = max(enhanced_scores) - min(enhanced_scores)
    print(f"\n📊 MOMENTUM RANGE: {momentum_range:.1f} points difference!")
    print(f"   💡 Same team performance → Different momentum based on opponent")
    
    print(f"\n🔥 WHY THIS IS CRUCIAL:")
    print(f"   ✅ Captures game context and relative performance")
    print(f"   ✅ Distinguishes 'stat-padding vs weak teams' from real dominance")
    print(f"   ✅ Better reflects how analysts actually assess teams")
    print(f"   ✅ More realistic for automated commentary")
    print(f"   ✅ Handles counter-attacking scenarios correctly")
    
    print(f"\n📋 REAL EXAMPLES:")
    print(f"   🟢 'Team A has high momentum (7.8/10) - dominating possession'")
    print(f"   🟡 'Team A momentum dropping (4.2/10) - opponent creating chances'") 
    print(f"   🔴 'Team A struggling (2.1/10) - outshot 5-1 by opponent'")
    
    print(f"\n💭 COMMENTARY IMPROVEMENTS:")
    print(f"   OLD: 'Spain has 65% possession' (static)")
    print(f"   NEW: 'Spain building momentum (7.4/10) with possession dominance'")
    print(f"   NEW: 'Spain momentum falling (3.8/10) despite possession - Germany clinical'")
    
    print(f"\n✅ CONCLUSION:")
    print(f"   Your suggestion to include opponent data is brilliant!")
    print(f"   It transforms momentum from absolute metric to relative assessment.")
    print(f"   This makes it much more realistic and useful for analysis.")

if __name__ == "__main__":
    main() 