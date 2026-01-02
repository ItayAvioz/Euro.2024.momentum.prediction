"""
Hybrid Momentum Agent
=====================
3-Layer decision system:
1. HARD RULES (Python) - Pre-filtering for efficiency
2. SOFT RULES (Prompt) - Guidelines for LLM
3. LLM JUDGMENT (API) - Contextual final decision

Author: Euro 2024 Momentum Project
Date: December 2024
"""

import os
from typing import Dict, Optional, List
from openai import OpenAI
from momentum_data_loader import MomentumDataLoader


class HybridMomentumAgent:
    """
    Hybrid agent combining hard rules with LLM judgment.
    
    Flow:
    1. Hard rules pre-filter (skip obvious cases, force include critical ones)
    2. Soft rules in prompt guide LLM behavior
    3. LLM makes contextual final decision
    """
    
    # =====================================================
    # LAYER 1: HARD RULES (Python)
    # Pre-filtering for efficiency - skip API calls when possible
    # =====================================================
    
    # SKIP conditions (don't waste API call)
    SKIP_IF_DIFF_BELOW = 0.3          # No significant difference
    SKIP_IF_BOTH_STABLE = 0.15        # Both teams barely moving
    
    # FORCE INCLUDE conditions (always mention, skip to LLM for phrasing)
    FORCE_IF_DIVERGENCE_ABOVE = 1.2   # Big divergence = always mention
    FORCE_IF_STREAK_ABOVE = 5         # 5+ minute streak = always mention
    FORCE_IF_DIFF_ABOVE = 2.0         # Complete dominance = always mention
    FORCE_IF_SWING_ABOVE = 1.5        # Major momentum swing = always mention
    
    # =====================================================
    # LAYER 2: SOFT RULES (Prompt Guidelines)
    # =====================================================
    
    SOFT_RULES_PROMPT = """
## Momentum Analysis Guidelines (Soft Rules)

You are analyzing momentum data for football commentary. Consider these guidelines:

### When to INCLUDE momentum:
- Streak of 3+ consecutive minutes of positive/negative change
- Divergence: one team rising while other falling
- Clear dominance shift happening
- Late game (75+) with prediction data available
- Momentum supports/contradicts the current score

### When to SKIP momentum:
- Both teams stable, nothing interesting
- Momentum data contradicts obvious game flow
- Too subtle to be meaningful to viewers

### Phrasing Guidelines:
- Be concise (max 15 words for momentum phrase)
- Use natural football language
- Don't say "momentum" directly - describe the effect
- Examples:
  - "Germany taking control of proceedings"
  - "The tide is turning in Spain's favor"
  - "Scotland struggling to get a foothold"

### Context to Consider:
- Game minute (early build-up vs late pressure)
- Current score (protecting lead vs chasing)
- Period (first half vs second half energy)
"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini", verbose: bool = False):
        self.loader = MomentumDataLoader(verbose=verbose)
        self.verbose = verbose
        self.model = model
        
        # Initialize OpenAI client
        api_key = api_key or os.getenv('OPENAI_API_KEY')
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None
            if verbose:
                print("[WARN] No OpenAI API key - LLM layer disabled")
    
    # =====================================================
    # MAIN ENTRY POINT
    # =====================================================
    
    def analyze(
        self,
        match_id: int,
        minute: int,
        period: int,
        score_home: int = 0,
        score_away: int = 0,
        home_team: str = None,
        away_team: str = None
    ) -> Dict:
        """
        Analyze momentum with 3-layer decision system.
        
        Args:
            match_id: Match identifier
            minute: Current game minute
            period: Game period (1, 2, 3, 4)
            score_home: Current home team score
            score_away: Current away team score
            home_team: Home team name (optional, loaded from data)
            away_team: Away team name (optional, loaded from data)
        
        Returns:
            {
                'include_momentum': bool,
                'decision_layer': 'hard_skip' | 'hard_include' | 'llm',
                'phrase': str or None,
                'reasoning': str,
                'raw_data': dict
            }
        """
        
        # Load momentum data
        context = self.loader.get_full_context(match_id, minute, period)
        
        if not context.get('has_momentum'):
            return {
                'include_momentum': False,
                'decision_layer': 'no_data',
                'phrase': None,
                'reasoning': 'No momentum data available',
                'raw_data': None
            }
        
        # Get team names
        home_team = home_team or context.get('home_team')
        away_team = away_team or context.get('away_team')
        
        # Analyze momentum features
        features = self._extract_features(context)
        features['score_home'] = score_home
        features['score_away'] = score_away
        features['minute'] = minute
        features['period'] = period
        
        # =====================================================
        # LAYER 1: HARD RULES - Pre-filtering
        # =====================================================
        
        hard_decision = self._apply_hard_rules(features)
        
        if hard_decision['action'] == 'SKIP':
            return {
                'include_momentum': False,
                'decision_layer': 'hard_skip',
                'phrase': None,
                'reasoning': hard_decision['reason'],
                'raw_data': features
            }
        
        if hard_decision['action'] == 'FORCE_INCLUDE':
            # Skip to LLM for phrasing (we know we want to include)
            if self.client:
                llm_result = self._call_llm(features, home_team, away_team, force_include=True)
                return {
                    'include_momentum': True,
                    'decision_layer': 'hard_include',
                    'phrase': llm_result['phrase'],
                    'reasoning': f"Hard rule: {hard_decision['reason']}. LLM phrasing.",
                    'raw_data': features
                }
            else:
                # No LLM available, use rule-based phrase
                phrase = self._generate_fallback_phrase(features, home_team, away_team)
                return {
                    'include_momentum': True,
                    'decision_layer': 'hard_include',
                    'phrase': phrase,
                    'reasoning': f"Hard rule: {hard_decision['reason']}. Fallback phrasing.",
                    'raw_data': features
                }
        
        # =====================================================
        # LAYER 2 & 3: SOFT RULES + LLM JUDGMENT
        # =====================================================
        
        if self.client:
            llm_result = self._call_llm(features, home_team, away_team, force_include=False)
            return {
                'include_momentum': llm_result['include'],
                'decision_layer': 'llm',
                'phrase': llm_result['phrase'],
                'reasoning': llm_result['reasoning'],
                'raw_data': features
            }
        else:
            # No LLM, fall back to rule-based decision
            return self._fallback_decision(features, home_team, away_team)
    
    # =====================================================
    # LAYER 1: HARD RULES IMPLEMENTATION
    # =====================================================
    
    def _apply_hard_rules(self, features: Dict) -> Dict:
        """
        Apply hard rules for pre-filtering.
        
        Returns:
            {'action': 'SKIP' | 'FORCE_INCLUDE' | 'ASK_LLM', 'reason': str}
        """
        
        diff = abs(features.get('momentum_diff', 0))
        home_change = abs(features.get('home_change', 0))
        away_change = abs(features.get('away_change', 0))
        divergence = features.get('divergence_swing', 0)
        streak_length = features.get('max_streak_length', 0)
        
        # SKIP RULES (save API call)
        if diff < self.SKIP_IF_DIFF_BELOW and home_change < self.SKIP_IF_BOTH_STABLE and away_change < self.SKIP_IF_BOTH_STABLE:
            return {'action': 'SKIP', 'reason': 'No significant momentum activity'}
        
        # FORCE INCLUDE RULES (definitely mention, just need phrasing)
        if divergence > self.FORCE_IF_DIVERGENCE_ABOVE:
            return {'action': 'FORCE_INCLUDE', 'reason': f'Strong divergence ({divergence:.1f})'}
        
        if streak_length >= self.FORCE_IF_STREAK_ABOVE:
            return {'action': 'FORCE_INCLUDE', 'reason': f'{streak_length}-minute streak detected'}
        
        if diff > self.FORCE_IF_DIFF_ABOVE:
            return {'action': 'FORCE_INCLUDE', 'reason': f'Complete dominance (diff: {diff:.1f})'}
        
        total_swing = home_change + away_change
        if total_swing > self.FORCE_IF_SWING_ABOVE:
            return {'action': 'FORCE_INCLUDE', 'reason': f'Major momentum swing ({total_swing:.1f})'}
        
        # Neither skip nor force - let LLM decide
        return {'action': 'ASK_LLM', 'reason': 'Borderline case - needs contextual judgment'}
    
    # =====================================================
    # FEATURE EXTRACTION
    # =====================================================
    
    def _extract_features(self, context: Dict) -> Dict:
        """Extract all momentum features for decision making."""
        
        home_change = context.get('home_change', 0) or 0
        away_change = context.get('away_change', 0) or 0
        
        # Detect divergence
        divergence_swing = 0
        if home_change > 0.3 and away_change < -0.3:
            divergence_swing = home_change - away_change
        elif away_change > 0.3 and home_change < -0.3:
            divergence_swing = away_change - home_change
        
        # Detect streaks from history
        max_streak_length = 0
        streak_team = None
        streak_direction = None
        
        if context.get('has_history') and context.get('history'):
            for team_type in ['home', 'away']:
                streak = self._calculate_streak(context['history'], f'{team_type}_change')
                if streak['positive'] > max_streak_length:
                    max_streak_length = streak['positive']
                    streak_team = context.get(f'{team_type}_team')
                    streak_direction = 'positive'
                if streak['negative'] > max_streak_length:
                    max_streak_length = streak['negative']
                    streak_team = context.get(f'{team_type}_team')
                    streak_direction = 'negative'
        
        # Determine dominant team
        diff = context.get('momentum_diff', 0)
        if abs(diff) < 0.5:
            dominant_team = 'Even'
            dominance_level = 'balanced'
        elif diff > 0:
            dominant_team = context.get('home_team')
            dominance_level = 'strong' if diff > 1.5 else 'slight'
        else:
            dominant_team = context.get('away_team')
            dominance_level = 'strong' if abs(diff) > 1.5 else 'slight'
        
        return {
            'home_team': context.get('home_team'),
            'away_team': context.get('away_team'),
            'home_momentum': context.get('home_momentum', 0),
            'away_momentum': context.get('away_momentum', 0),
            'home_change': home_change,
            'away_change': away_change,
            'momentum_diff': diff,
            'dominant_team': dominant_team,
            'dominance_level': dominance_level,
            'divergence_swing': divergence_swing,
            'max_streak_length': max_streak_length,
            'streak_team': streak_team,
            'streak_direction': streak_direction,
            'has_prediction': context.get('has_prediction', False),
            'predictions': context.get('predictions')
        }
    
    def _calculate_streak(self, history: List[Dict], change_key: str) -> Dict:
        """Calculate streak from history."""
        positive = 0
        negative = 0
        curr_pos = 0
        curr_neg = 0
        
        for entry in history:
            change = entry.get(change_key, 0) or 0
            if change > 0.1:
                curr_pos += 1
                curr_neg = 0
                positive = max(positive, curr_pos)
            elif change < -0.1:
                curr_neg += 1
                curr_pos = 0
                negative = max(negative, curr_neg)
            else:
                curr_pos = 0
                curr_neg = 0
        
        return {'positive': positive, 'negative': negative}
    
    # =====================================================
    # LAYER 2 & 3: LLM CALL WITH SOFT RULES
    # =====================================================
    
    def _call_llm(
        self, 
        features: Dict, 
        home_team: str, 
        away_team: str,
        force_include: bool = False
    ) -> Dict:
        """
        Call LLM with soft rules in prompt for contextual decision.
        
        Args:
            features: Extracted momentum features
            home_team: Home team name
            away_team: Away team name
            force_include: If True, only ask for phrasing (not whether to include)
        
        Returns:
            {'include': bool, 'phrase': str, 'reasoning': str}
        """
        
        # Build the prompt with soft rules
        system_prompt = self.SOFT_RULES_PROMPT
        
        # Build user prompt with current data
        user_prompt = self._build_user_prompt(features, home_team, away_team, force_include)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower for more consistent decisions
                max_tokens=100
            )
            
            return self._parse_llm_response(response.choices[0].message.content, force_include)
            
        except Exception as e:
            if self.verbose:
                print(f"[ERROR] LLM call failed: {e}")
            # Fallback to rule-based
            phrase = self._generate_fallback_phrase(features, home_team, away_team)
            return {
                'include': True if force_include else features.get('divergence_swing', 0) > 0.5,
                'phrase': phrase,
                'reasoning': f'LLM error, used fallback: {str(e)}'
            }
    
    def _build_user_prompt(
        self, 
        features: Dict, 
        home_team: str, 
        away_team: str,
        force_include: bool
    ) -> str:
        """Build the user prompt with current match data."""
        
        minute = features.get('minute', 0)
        period = features.get('period', 1)
        score_home = features.get('score_home', 0)
        score_away = features.get('score_away', 0)
        
        prompt = f"""
## Current Match Situation

**Match:** {home_team} vs {away_team}
**Score:** {home_team} {score_home} - {score_away} {away_team}
**Minute:** {minute}' (Period {period})

## Momentum Data

| Team | Momentum | Change (last 3 min) |
|------|----------|---------------------|
| {home_team} | {features.get('home_momentum', 0):.2f} | {features.get('home_change', 0):+.2f} |
| {away_team} | {features.get('away_momentum', 0):.2f} | {features.get('away_change', 0):+.2f} |

**Differential:** {features.get('momentum_diff', 0):+.2f}
**Dominant:** {features.get('dominant_team')} ({features.get('dominance_level')})
"""
        
        # Add streak info if present
        if features.get('max_streak_length', 0) >= 2:
            prompt += f"\n**Streak:** {features['streak_team']} has {features['max_streak_length']}-minute {features['streak_direction']} run"
        
        # Add divergence info if present
        if features.get('divergence_swing', 0) > 0:
            prompt += f"\n**Divergence:** Swing of {features['divergence_swing']:.2f} detected"
        
        # Add prediction if available
        if features.get('has_prediction') and features.get('predictions'):
            pred = features['predictions']
            prompt += f"\n**Prediction (next 3 min):** {pred.get('expected_dominant')} expected to improve"
        
        # Add the question
        if force_include:
            prompt += """

## Task
Generate a natural momentum phrase for commentary (max 15 words).
Don't say "momentum" directly.

**Response format:**
PHRASE: [your phrase here]
"""
        else:
            prompt += """

## Task
1. Should momentum be mentioned in commentary? (YES/NO)
2. If YES, provide a natural phrase (max 15 words)

**Response format:**
DECISION: [YES/NO]
REASON: [brief reason]
PHRASE: [phrase if YES, or "none" if NO]
"""
        
        return prompt
    
    def _parse_llm_response(self, response: str, force_include: bool) -> Dict:
        """Parse LLM response into structured format."""
        
        lines = response.strip().split('\n')
        result = {
            'include': force_include,
            'phrase': None,
            'reasoning': ''
        }
        
        for line in lines:
            line = line.strip()
            if line.upper().startswith('DECISION:'):
                decision = line.split(':', 1)[1].strip().upper()
                result['include'] = 'YES' in decision
            elif line.upper().startswith('REASON:'):
                result['reasoning'] = line.split(':', 1)[1].strip()
            elif line.upper().startswith('PHRASE:'):
                phrase = line.split(':', 1)[1].strip()
                if phrase.lower() != 'none':
                    result['phrase'] = phrase
        
        return result
    
    # =====================================================
    # FALLBACK (No LLM available)
    # =====================================================
    
    def _generate_fallback_phrase(self, features: Dict, home_team: str, away_team: str) -> str:
        """Generate phrase using rules when LLM not available."""
        
        dominant = features.get('dominant_team')
        
        # Priority 1: Divergence
        if features.get('divergence_swing', 0) > 0.5:
            if features.get('home_change', 0) > 0:
                return f"{home_team} taking control as {away_team} fade"
            else:
                return f"{away_team} seizing the initiative"
        
        # Priority 2: Strong streak
        if features.get('max_streak_length', 0) >= 3:
            team = features.get('streak_team')
            direction = features.get('streak_direction')
            if direction == 'positive':
                return f"{team} building pressure"
            else:
                return f"{team} struggling to get going"
        
        # Priority 3: Dominance
        if features.get('dominance_level') == 'strong':
            return f"{dominant} firmly in control"
        elif dominant != 'Even':
            return f"{dominant} edging proceedings"
        
        return "The game finely balanced"
    
    def _fallback_decision(self, features: Dict, home_team: str, away_team: str) -> Dict:
        """Make decision without LLM."""
        
        # Include if there's something interesting
        include = (
            features.get('divergence_swing', 0) > 0.5 or
            features.get('max_streak_length', 0) >= 3 or
            features.get('dominance_level') == 'strong'
        )
        
        phrase = self._generate_fallback_phrase(features, home_team, away_team) if include else None
        
        return {
            'include_momentum': include,
            'decision_layer': 'fallback',
            'phrase': phrase,
            'reasoning': 'No LLM available, used rule-based fallback',
            'raw_data': features
        }


# =====================================================
# TEST
# =====================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Testing Hybrid Momentum Agent")
    print("=" * 70)
    
    agent = HybridMomentumAgent(verbose=True)
    
    # Test cases
    test_cases = [
        {'match_id': 3930158, 'minute': 5, 'period': 1, 'score_home': 0, 'score_away': 0},
        {'match_id': 3930158, 'minute': 25, 'period': 1, 'score_home': 2, 'score_away': 0},
        {'match_id': 3930158, 'minute': 40, 'period': 1, 'score_home': 3, 'score_away': 0},
        {'match_id': 3930158, 'minute': 80, 'period': 2, 'score_home': 5, 'score_away': 1},
    ]
    
    for case in test_cases:
        print(f"\n{'='*70}")
        print(f"Minute {case['minute']}' - Score: {case['score_home']}-{case['score_away']}")
        print("=" * 70)
        
        result = agent.analyze(**case)
        
        print(f"Decision Layer: {result['decision_layer']}")
        print(f"Include: {result['include_momentum']}")
        print(f"Phrase: {result['phrase']}")
        print(f"Reasoning: {result['reasoning']}")
    
    print("\n[OK] Test completed!")

