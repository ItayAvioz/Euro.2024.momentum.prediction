"""
Momentum Agent for General Commentary
=====================================
Decides IF and WHAT momentum information to include in General commentary.

Features:
- Dominance detection (which team has higher momentum)
- Trend analysis (rising/falling/stable)
- Streak detection (2, 3, 4+ consecutive positive/negative changes)
- Divergence tracking (one rising while other falling)
- Max differential tracking (biggest gap between teams)
- ARIMAX predictions for minutes 75+

Author: Euro 2024 Momentum Project
Date: December 2024
"""

from typing import Dict, Tuple, Optional, List
from momentum_data_loader import MomentumDataLoader


class MomentumAgent:
    """
    Agent that analyzes momentum for General commentary.
    
    Only processes General commentary type.
    Uses actual momentum data (0-74 min) and predictions (75+ min).
    
    Decision Framework:
    1. WHO is dominant? (Higher momentum)
    2. WHAT is the trend? (Momentum change direction)
    3. Is there a STREAK? (2, 3, 4+ consecutive same-direction changes)
    4. Is there DIVERGENCE? (One team rising while other falling)
    5. How does current compare to MAX differential?
    6. What does the PREDICTION say? (75+ only)
    """
    
    # =====================================================
    # THRESHOLDS (Configurable)
    # =====================================================
    
    # Dominance thresholds
    DOMINANCE_THRESHOLD = 0.5       # Momentum diff for "slight advantage"
    STRONG_DOMINANCE = 1.5          # Momentum diff for "strong dominance"
    VERY_STRONG_DOMINANCE = 2.5     # Momentum diff for "complete control"
    
    # Change thresholds
    SIGNIFICANT_CHANGE = 0.3        # Momentum change to be "significant"
    STRONG_CHANGE = 0.6             # Momentum change for "strong trend"
    MOMENTUM_SWING = 1.0            # Big momentum swing
    
    # Streak thresholds
    MIN_STREAK = 2                  # Minimum consecutive minutes for streak
    STRONG_STREAK = 3               # Strong streak
    DOMINANT_STREAK = 4             # Dominant streak
    
    # Divergence threshold
    DIVERGENCE_THRESHOLD = 0.4      # Combined change for divergence detection
    
    def __init__(self, verbose: bool = False):
        self.loader = MomentumDataLoader(verbose=verbose)
        self.verbose = verbose
    
    # =====================================================
    # MAIN ENTRY POINT
    # =====================================================
    
    def analyze_for_general(
        self,
        match_id: int,
        minute: int,
        period: int
    ) -> Dict:
        """
        Analyze momentum situation for General commentary.
        
        This is the main entry point for the agent.
        
        Args:
            match_id: Match identifier
            minute: Current game minute
            period: Game period (1, 2, 3, 4)
        
        Returns:
            Complete agent decision with:
            - situation_type: Type of momentum situation
            - dominant_team: Who's in control
            - trend_description: What's happening with momentum
            - streak_info: Consecutive positive/negative changes
            - divergence_info: One team rising, other falling
            - max_diff_info: Comparison to biggest gap
            - prediction_note: Future expectation (75+ only)
            - phrase_suggestion: Suggested phrase for commentary
            - detailed_summary: Full agent analysis
        """
        
        # Get full momentum context with history
        context = self.loader.get_full_context(
            match_id, minute, period, 
            include_history=True, 
            lookback=5
        )
        
        if not context.get('has_momentum'):
            return {
                'include_momentum': False,
                'reason': 'no_data',
                'detailed_summary': "No momentum data available for this minute."
            }
        
        # =====================================================
        # ANALYSIS STEPS
        # =====================================================
        
        # Step 1: Determine dominant team
        dominance = self._analyze_dominance(context)
        
        # Step 2: Analyze trend (rising/falling/stable)
        trend = self._analyze_trend(context)
        
        # Step 3: Detect streaks (consecutive positive/negative)
        streak = self._detect_streak(context)
        
        # Step 4: Detect divergence (one rising, other falling)
        divergence = self._detect_divergence(context)
        
        # Step 5: Compare to max differential
        max_diff = self._analyze_max_differential(match_id, minute, period, context)
        
        # Step 6: Check predictions (75+ only)
        prediction = None
        if context.get('has_prediction'):
            prediction = self._analyze_prediction(context)
        
        # Step 7: Generate phrase suggestion
        phrase = self._generate_phrase(context, dominance, trend, streak, divergence, prediction)
        
        # Step 8: Create detailed summary
        summary = self._create_detailed_summary(
            context, dominance, trend, streak, divergence, max_diff, prediction
        )
        
        return {
            'include_momentum': True,
            'minute': minute,
            'period': period,
            
            # Dominance info
            'dominant_team': context.get('dominant_team'),
            'dominant_momentum': self._get_dominant_momentum(context),
            'dominance_type': dominance['type'],
            'dominance_strength': dominance['strength'],
            
            # Trend info
            'trend_description': trend['description'],
            'trend_direction': trend['direction'],
            
            # Streak info
            'has_streak': streak['has_streak'],
            'streak_team': streak.get('team'),
            'streak_length': streak.get('length', 0),
            'streak_direction': streak.get('direction'),
            'streak_description': streak.get('description'),
            
            # Divergence info
            'has_divergence': divergence['has_divergence'],
            'divergence_description': divergence.get('description'),
            'rising_team': divergence.get('rising_team'),
            'falling_team': divergence.get('falling_team'),
            
            # Max differential info
            'max_diff_info': max_diff,
            
            # Prediction info (75+ only)
            'has_prediction': prediction is not None,
            'prediction_note': prediction.get('note') if prediction else None,
            
            # Output
            'phrase_suggestion': phrase,
            'detailed_summary': summary,
            
            # Raw data for reference
            'raw_data': {
                'home_team': context.get('home_team'),
                'away_team': context.get('away_team'),
                'home_momentum': context.get('home_momentum'),
                'away_momentum': context.get('away_momentum'),
                'home_change': context.get('home_change'),
                'away_change': context.get('away_change'),
                'diff': context.get('momentum_diff')
            }
        }
    
    # =====================================================
    # ANALYSIS METHODS
    # =====================================================
    
    def _analyze_dominance(self, context: Dict) -> Dict:
        """Determine the current dominance situation."""
        diff = abs(context.get('momentum_diff', 0))
        
        if diff < self.DOMINANCE_THRESHOLD:
            return {'type': 'balanced', 'strength': 'even'}
        elif diff < self.STRONG_DOMINANCE:
            return {'type': 'slight_advantage', 'strength': 'moderate'}
        elif diff < self.VERY_STRONG_DOMINANCE:
            return {'type': 'dominant', 'strength': 'strong'}
        else:
            return {'type': 'complete_control', 'strength': 'overwhelming'}
    
    def _analyze_trend(self, context: Dict) -> Dict:
        """
        Analyze the momentum trend for the dominant team.
        
        Compares dominant team's change to opponent's change.
        """
        dominant = context.get('dominant_team')
        home = context.get('home_team')
        away = context.get('away_team')
        
        home_change = context.get('home_change', 0) or 0
        away_change = context.get('away_change', 0) or 0
        
        # Get dominant team's change
        if dominant == home:
            dom_change = home_change
            opp_change = away_change
            opp_team = away
        elif dominant == away:
            dom_change = away_change
            opp_change = home_change
            opp_team = home
        else:  # Even
            # Compare both teams
            if abs(home_change) > abs(away_change):
                return {
                    'description': 'home_building' if home_change > 0 else 'home_fading',
                    'direction': 'home_changing',
                    'changing_team': home,
                    'change_value': home_change
                }
            elif abs(away_change) > abs(home_change):
                return {
                    'description': 'away_building' if away_change > 0 else 'away_fading',
                    'direction': 'away_changing',
                    'changing_team': away,
                    'change_value': away_change
                }
            else:
                return {'description': 'stable', 'direction': 'steady'}
        
        # Classify dominant team's trend
        if dom_change > self.STRONG_CHANGE:
            if opp_change < -self.SIGNIFICANT_CHANGE:
                return {
                    'description': 'extending_control',
                    'direction': 'widening',
                    'dom_change': dom_change,
                    'opp_change': opp_change
                }
            else:
                return {
                    'description': 'surging',
                    'direction': 'rising_fast',
                    'dom_change': dom_change
                }
        elif dom_change > self.SIGNIFICANT_CHANGE:
            return {
                'description': 'improving',
                'direction': 'rising',
                'dom_change': dom_change
            }
        elif dom_change < -self.STRONG_CHANGE:
            if opp_change > self.SIGNIFICANT_CHANGE:
                return {
                    'description': 'momentum_shifting',
                    'direction': 'reversing',
                    'dom_change': dom_change,
                    'opp_change': opp_change,
                    'shifting_to': opp_team
                }
            else:
                return {
                    'description': 'fading_fast',
                    'direction': 'falling_fast',
                    'dom_change': dom_change
                }
        elif dom_change < -self.SIGNIFICANT_CHANGE:
            return {
                'description': 'losing_grip',
                'direction': 'falling',
                'dom_change': dom_change
            }
        else:
            return {
                'description': 'stable',
                'direction': 'steady',
                'dom_change': dom_change
            }
    
    def _detect_streak(self, context: Dict) -> Dict:
        """
        Detect consecutive positive or negative momentum changes.
        
        Looks at history to find streaks like:
        - 3 consecutive minutes of positive change → "Building momentum"
        - 4 consecutive minutes of negative change → "Sustained decline"
        """
        if not context.get('has_history') or not context.get('history'):
            return {'has_streak': False}
        
        history = context['history']
        if len(history) < 2:
            return {'has_streak': False}
        
        # Check streaks for both teams
        home_streaks = self._calculate_team_streak(history, 'home_change')
        away_streaks = self._calculate_team_streak(history, 'away_change')
        
        # Find the most significant streak
        best_streak = {'has_streak': False, 'length': 0}
        
        for team_type, streaks in [('home', home_streaks), ('away', away_streaks)]:
            team_name = context.get(f'{team_type}_team')
            
            if streaks['positive_streak'] >= self.MIN_STREAK:
                if streaks['positive_streak'] > best_streak['length']:
                    strength = self._get_streak_strength(streaks['positive_streak'])
                    best_streak = {
                        'has_streak': True,
                        'team': team_name,
                        'length': streaks['positive_streak'],
                        'direction': 'positive',
                        'strength': strength,
                        'description': f"{team_name} on a {streaks['positive_streak']}-minute positive run"
                    }
            
            if streaks['negative_streak'] >= self.MIN_STREAK:
                if streaks['negative_streak'] > best_streak['length']:
                    strength = self._get_streak_strength(streaks['negative_streak'])
                    best_streak = {
                        'has_streak': True,
                        'team': team_name,
                        'length': streaks['negative_streak'],
                        'direction': 'negative',
                        'strength': strength,
                        'description': f"{team_name} momentum declining for {streaks['negative_streak']} minutes"
                    }
        
        return best_streak
    
    def _calculate_team_streak(self, history: List[Dict], change_key: str) -> Dict:
        """Calculate streak length for a team's momentum changes."""
        positive_streak = 0
        negative_streak = 0
        current_positive = 0
        current_negative = 0
        
        for i, entry in enumerate(history):
            change = entry.get(change_key, 0) or 0
            
            if change > 0.1:  # Small positive threshold
                current_positive += 1
                current_negative = 0
                positive_streak = max(positive_streak, current_positive)
            elif change < -0.1:  # Small negative threshold
                current_negative += 1
                current_positive = 0
                negative_streak = max(negative_streak, current_negative)
            else:
                current_positive = 0
                current_negative = 0
        
        return {
            'positive_streak': positive_streak,
            'negative_streak': negative_streak
        }
    
    def _get_streak_strength(self, length: int) -> str:
        """Get streak strength based on length."""
        if length >= self.DOMINANT_STREAK:
            return 'dominant'
        elif length >= self.STRONG_STREAK:
            return 'strong'
        else:
            return 'building'
    
    def _detect_divergence(self, context: Dict) -> Dict:
        """
        Detect divergence: one team rising while other falling.
        
        This is a significant momentum shift indicator.
        """
        home_change = context.get('home_change', 0) or 0
        away_change = context.get('away_change', 0) or 0
        home_team = context.get('home_team')
        away_team = context.get('away_team')
        
        # Check for divergence (opposite directions)
        if home_change > self.DIVERGENCE_THRESHOLD and away_change < -self.DIVERGENCE_THRESHOLD:
            total_swing = home_change - away_change
            return {
                'has_divergence': True,
                'rising_team': home_team,
                'falling_team': away_team,
                'rising_change': home_change,
                'falling_change': away_change,
                'total_swing': total_swing,
                'description': f"{home_team} surging (+{home_change:.1f}) while {away_team} fades ({away_change:.1f})"
            }
        
        elif away_change > self.DIVERGENCE_THRESHOLD and home_change < -self.DIVERGENCE_THRESHOLD:
            total_swing = away_change - home_change
            return {
                'has_divergence': True,
                'rising_team': away_team,
                'falling_team': home_team,
                'rising_change': away_change,
                'falling_change': home_change,
                'total_swing': total_swing,
                'description': f"{away_team} surging (+{away_change:.1f}) while {home_team} fades ({home_change:.1f})"
            }
        
        return {'has_divergence': False}
    
    def _analyze_max_differential(
        self, 
        match_id: int, 
        minute: int, 
        period: int,
        context: Dict
    ) -> Dict:
        """Compare current differential to max differential in the match."""
        max_diff_data = self.loader.get_match_max_differential(match_id, minute, period)
        
        if not max_diff_data:
            return {}
        
        current_diff = abs(context.get('momentum_diff', 0))
        max_diff = max_diff_data.get('max_diff', 0)
        
        # Compare current to max
        if max_diff > 0:
            ratio = current_diff / max_diff
        else:
            ratio = 0
        
        if ratio >= 0.95:
            comparison = 'at_peak'
            note = f"Biggest momentum gap in the match so far ({current_diff:.1f})"
        elif ratio >= 0.8:
            comparison = 'near_peak'
            note = f"Near the biggest gap seen (peak was {max_diff:.1f} at min {max_diff_data['max_diff_minute']})"
        elif ratio >= 0.5:
            comparison = 'moderate'
            note = None
        else:
            comparison = 'below_peak'
            note = None
        
        return {
            'max_diff': max_diff,
            'max_minute': max_diff_data.get('max_diff_minute'),
            'max_team': max_diff_data.get('max_diff_team'),
            'current_diff': current_diff,
            'comparison': comparison,
            'note': note
        }
    
    def _analyze_prediction(self, context: Dict) -> Dict:
        """Analyze ARIMAX prediction for 75+ minutes."""
        pred = context.get('predictions')
        if not pred:
            return {}
        
        home_pred = pred.get('home_predicted_change', 0)
        away_pred = pred.get('away_predicted_change', 0)
        expected = pred.get('expected_dominant')
        home_team = pred.get('home_team')
        away_team = pred.get('away_team')
        
        # Build prediction note
        if expected == "Neither/Both":
            if home_pred > 0.3 and away_pred > 0.3:
                note = "Model predicts both teams will push - tense finish ahead"
            elif home_pred < -0.3 and away_pred < -0.3:
                note = "Model suggests game winding down"
            else:
                note = "No clear momentum shift predicted"
        else:
            change = home_pred if home_team == expected else away_pred
            if change > 0.6:
                note = f"Model predicts {expected} momentum surge (+{change:.1f})"
            elif change > 0.3:
                note = f"Model suggests {expected} will maintain pressure"
            elif change > 0:
                note = f"{expected} expected to hold momentum"
            else:
                note = f"Momentum could shift away from {expected}"
        
        return {
            'home_predicted': home_pred,
            'away_predicted': away_pred,
            'expected_dominant': expected,
            'note': note
        }
    
    def _get_dominant_momentum(self, context: Dict) -> float:
        """Get the momentum value of the dominant team."""
        dominant = context.get('dominant_team')
        if dominant == context.get('home_team'):
            return context.get('home_momentum', 0)
        elif dominant == context.get('away_team'):
            return context.get('away_momentum', 0)
        else:
            return (context.get('home_momentum', 0) + context.get('away_momentum', 0)) / 2
    
    # =====================================================
    # PHRASE GENERATION
    # =====================================================
    
    def _generate_phrase(
        self, 
        context: Dict, 
        dominance: Dict, 
        trend: Dict, 
        streak: Dict,
        divergence: Dict,
        prediction: Optional[Dict]
    ) -> str:
        """Generate a suggested phrase for the commentary."""
        dominant = context.get('dominant_team')
        home = context.get('home_team')
        away = context.get('away_team')
        dom_momentum = self._get_dominant_momentum(context)
        
        phrases = []
        
        # Priority 1: Divergence (most dramatic)
        if divergence.get('has_divergence'):
            return divergence['description']
        
        # Priority 2: Strong streak
        if streak.get('has_streak') and streak.get('strength') in ['strong', 'dominant']:
            return streak['description']
        
        # Priority 3: Based on dominance + trend
        if dominance['type'] == 'balanced':
            if trend['description'] in ['home_building', 'away_building']:
                changing = trend.get('changing_team')
                return f"{changing} beginning to assert themselves"
            else:
                return "Evenly matched with neither side able to dominate"
        
        elif dominance['type'] == 'complete_control':
            if trend['direction'] == 'widening':
                return f"{dominant} completely dominating, momentum at {dom_momentum:.1f} and rising"
            else:
                return f"{dominant} in complete control with {dom_momentum:.1f} momentum"
        
        elif dominance['type'] == 'dominant':
            if trend['description'] == 'extending_control':
                return f"{dominant} firmly in control and pulling further ahead"
            elif trend['description'] == 'momentum_shifting':
                opp = away if dominant == home else home
                return f"Tide turning! {opp} building momentum against {dominant}"
            elif trend['description'] == 'losing_grip':
                opp = away if dominant == home else home
                return f"{dominant} still ahead but {opp} sensing an opportunity"
            else:
                return f"{dominant} dominating proceedings with momentum at {dom_momentum:.1f}"
        
        else:  # slight_advantage
            if trend['description'] == 'surging':
                return f"{dominant} gaining the upper hand, momentum rising"
            elif trend['description'] == 'fading_fast':
                return f"{dominant} with slim advantage but momentum fading fast"
            elif streak.get('has_streak'):
                return streak['description']
            else:
                return f"{dominant} edging the contest"
        
        return f"Momentum with {dominant}"
    
    # =====================================================
    # DETAILED SUMMARY
    # =====================================================
    
    def _create_detailed_summary(
        self,
        context: Dict,
        dominance: Dict,
        trend: Dict,
        streak: Dict,
        divergence: Dict,
        max_diff: Dict,
        prediction: Optional[Dict]
    ) -> str:
        """Create a detailed summary of the agent's analysis."""
        lines = []
        
        home = context.get('home_team')
        away = context.get('away_team')
        home_mom = context.get('home_momentum', 0)
        away_mom = context.get('away_momentum', 0)
        home_change = context.get('home_change', 0)
        away_change = context.get('away_change', 0)
        minute = context.get('minute')
        
        lines.append("=" * 60)
        lines.append(f"MOMENTUM AGENT ANALYSIS - Minute {minute}'")
        lines.append("=" * 60)
        
        # Current state
        lines.append(f"\n[DATA] CURRENT MOMENTUM:")
        lines.append(f"   {home}: {home_mom:.2f} (change: {home_change:+.2f})")
        lines.append(f"   {away}: {away_mom:.2f} (change: {away_change:+.2f})")
        lines.append(f"   Differential: {context.get('momentum_diff', 0):+.2f}")
        
        # Dominance
        lines.append(f"\n[DOMINANCE]:")
        dominant = context.get('dominant_team')
        lines.append(f"   Status: {dominance['type'].replace('_', ' ').title()}")
        lines.append(f"   Dominant team: {dominant}")
        lines.append(f"   Strength: {dominance['strength']}")
        
        # Trend
        lines.append(f"\n[TREND]:")
        lines.append(f"   Description: {trend['description'].replace('_', ' ').title()}")
        lines.append(f"   Direction: {trend['direction']}")
        
        # Streak
        lines.append(f"\n[STREAK ANALYSIS]:")
        if streak.get('has_streak'):
            lines.append(f"   Detected: YES")
            lines.append(f"   Team: {streak['team']}")
            lines.append(f"   Length: {streak['length']} consecutive minutes")
            lines.append(f"   Type: {streak['direction']} momentum")
            lines.append(f"   Strength: {streak['strength']}")
        else:
            lines.append(f"   Detected: No significant streak")
        
        # Divergence
        lines.append(f"\n[DIVERGENCE]:")
        if divergence.get('has_divergence'):
            lines.append(f"   Detected: YES - SIGNIFICANT!")
            lines.append(f"   Rising: {divergence['rising_team']} ({divergence['rising_change']:+.2f})")
            lines.append(f"   Falling: {divergence['falling_team']} ({divergence['falling_change']:+.2f})")
            lines.append(f"   Total swing: {divergence['total_swing']:.2f}")
        else:
            lines.append(f"   Detected: No (both teams moving similarly)")
        
        # Max differential
        lines.append(f"\n[MAX DIFFERENTIAL]:")
        if max_diff:
            lines.append(f"   Max in match: {max_diff.get('max_diff', 0):.2f} at minute {max_diff.get('max_minute', 0)}")
            lines.append(f"   Max team: {max_diff.get('max_team', 'N/A')}")
            lines.append(f"   Current vs max: {max_diff.get('comparison', 'N/A')}")
            if max_diff.get('note'):
                lines.append(f"   Note: {max_diff['note']}")
        else:
            lines.append(f"   Not available")
        
        # Prediction
        lines.append(f"\n[PREDICTION (ARIMAX)]:")
        if prediction:
            lines.append(f"   {home} predicted: {prediction.get('home_predicted', 0):+.2f}")
            lines.append(f"   {away} predicted: {prediction.get('away_predicted', 0):+.2f}")
            lines.append(f"   Note: {prediction.get('note', 'N/A')}")
        else:
            lines.append(f"   Not available (only for minute 75+)")
        
        lines.append("\n" + "=" * 60)
        
        return '\n'.join(lines)


# Test if run directly
if __name__ == "__main__":
    print("=" * 60)
    print("Testing Momentum Agent")
    print("=" * 60)
    
    agent = MomentumAgent(verbose=True)
    
    # Test with Germany vs Scotland (match_id: 3930158)
    test_cases = [
        (3930158, 25, 1),   # Early game
        (3930158, 38, 1),   # Late first half
        (3930158, 60, 2),   # Mid second half
        (3930158, 80, 2),   # With predictions
    ]
    
    for match_id, minute, period in test_cases:
        print(f"\n{'='*60}")
        print(f"Testing: Match {match_id}, Minute {minute}, Period {period}")
        print("=" * 60)
        
        result = agent.analyze_for_general(match_id, minute, period)
        
        if result.get('include_momentum'):
            print(f"\n[INCLUDE] Agent Decision: INCLUDE MOMENTUM")
            print(f"\n[PHRASE] Phrase Suggestion:")
            print(f"   \"{result['phrase_suggestion']}\"")
            print(f"\n{result['detailed_summary']}")
        else:
            print(f"\n[SKIP] Agent Decision: NO DATA")
            print(f"   Reason: {result.get('reason')}")
    
    print("\n[OK] All tests completed!")

