"""
Exploratory Momentum Agent
==========================
Agent with FREEDOM to explore and discover interesting momentum patterns.

IMPORTANT: This agent works ONLY for GENERAL commentary!
- It does NOT replace Goal, Shot, Card, etc. commentary
- It INTEGRATES with existing commentary flow
- It ADDS momentum context when interesting

Philosophy:
- Hard rules: ONLY for efficiency (skip truly empty data)
- Soft rules: VOCABULARY of patterns (not restrictions)
- LLM judgment: FULL FREEDOM to explore and find interesting insights

The agent receives:
- ALL momentum data
- Recent events (what happened, to which team)
- Match context

Author: Euro 2024 Momentum Project
Date: December 2024
"""

import os
import csv
from typing import Dict, Optional, List
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from momentum_data_loader import MomentumDataLoader


class ExploratoryMomentumAgent:
    """
    Agent with freedom to explore momentum data and find interesting patterns.
    
    The agent is NOT limited by rules - it receives all data and decides:
    - What patterns are interesting
    - What to highlight
    - How to phrase it
    """
    
    # Only ONE hard rule: skip if literally no data
    SKIP_IF_NO_DATA = True
    
    # =====================================================
    # SOFT RULES: Vocabulary of patterns (not restrictions!)
    # These are SUGGESTIONS, not limits
    # =====================================================
    
    EXPLORATION_PROMPT = """
## Your Role

You are a momentum ANALYST with GUIDED EXPLORATION.
- You decide WHAT is interesting
- You follow the OUTPUT FORMAT below
- Most minutes (60-70%) should NOT be interesting
- When in doubt, say NO

Full research tables are in APPENDIX at end. Use if needed, but focus on KEY PATTERNS below.

---

## YOUR FOCUS (Priority Order!)

**What to look for:**

1. **TENSION** - Score leader ≠ Momentum leader
   → ALWAYS interesting! Trailing team pushing = drama

2. **PREDICTIONS (min 76+)** - Your BEST data!
   → Count dominance, find crossovers, analyze full window

3. **Research threshold match** - Compare to QUICK REFERENCE
   → If margin matches "0% LOSE" pattern, cite it!

4. **HOT TIMES** - Current = MAX in match history
   → Biggest gap ever? Biggest change? Report it!

5. **Strong patterns** - 4+ min streaks, clear divergence
   → One team building, other fading for 4+ minutes

**What to SKIP:**
- Balanced situations (both teams similar)
- Small changes (< 0.2)
- Short streaks (2-3 min)
- Early game (< 15 min) unless extreme

---

## QUICK REFERENCE - Key Patterns

**0% LOSE Patterns (Always Report!):**
- 20%+ Mom margin + 3+ Longest seq → 100% WIN, 0% LOSE
- 5%+ Pos Change margin → 100% WIN, 0% LOSE
- 15%+ Mom margin → 62.5% WIN, 0% LOSE

**Goal Danger Signals:**
- POSITIVE change (+0.3+) = DANGEROUS (72.9% goals with positive change)
- NEGATIVE change (-0.3+) = VULNERABLE (65% goals conceded with negative)

**Tension Pattern:**
- Score leader ≠ Momentum leader → 66.7% WIN for momentum leader!

**Event Correlations:**
- Goal: Scoring team avg +0.603 change, conceding team avg -0.368
- Substitution: Both teams avg -0.12 change (temporary disruption)
- Yellow Card: Carded team avg +0.112 (was pressing hard!)

---

## OUTPUT FORMAT

INTERESTING: [YES/NO]
CONFIDENCE: [0.0-1.0]
MAIN_FINDING: [1 line - the pattern]
FORWARD_DATA: (Max 3-4 items)
- Current momentum VALUES for both teams
- The KEY pattern (streak, gap, tension)
- If min 76+: PREDICTION summary
- If research match: cite which (e.g., "matches 0% LOSE threshold")
REASON: [Why this matters]

**Confidence Guide:**
- 0.85+: Multiple patterns OR research threshold match
- 0.75-0.85: Single strong pattern (4+ streak, max gap, tension)
- < 0.75: NOT interesting - say NO

---

## EXAMPLES

**IMPORTANT: In a typical match, 60-70% of General minutes should be NOT interesting.**
**Only 30-40% have patterns strong enough to report. Be SELECTIVE!**

**Example 1 - Tension + Predictions (YES):**
INTERESTING: YES
CONFIDENCE: 0.88
MAIN_FINDING: Switzerland momentum takeover while trailing
FORWARD_DATA:
- Switzerland VALUE 5.8 vs England 4.2 (but England leads 1-0)
- Switzerland: 4-minute positive CHANGE streak
- PREDICTIONS: Switzerland dominates 8/10 remaining minutes
REASON: Tension pattern - trailing team building pressure, model predicts continuation

**Example 2 - Research Threshold Match (YES):**
INTERESTING: YES
CONFIDENCE: 0.90
MAIN_FINDING: England matches 0% LOSE research pattern
FORWARD_DATA:
- England total momentum: 52.5 vs Switzerland 43.0
- Margin calculation: (52.5 - 43.0) / 43.0 = 22.1% (above 20% threshold)
- England longest sequence: 5 (above 3+ threshold)
- Matches: "20%+ Mom + 3+ Longest = 0% LOSE" pattern
REASON: Historical pattern with 0% lose rate - strong win indicator

**Example 3 - Has Data but NOT Interesting (NO):**
INTERESTING: NO
CONFIDENCE: 0.65
MAIN_FINDING: Minor patterns, nothing significant
FORWARD_DATA: none
REASON: 3-minute streak and small gap (0.4) - below thresholds, not unusual

**Example 4 - Early Game Skip (NO):**
INTERESTING: NO
CONFIDENCE: 0.40
MAIN_FINDING: Too early for meaningful patterns
FORWARD_DATA: none
REASON: Minute 12, some movement but no extreme patterns - wait for game to develop

---

## UNDERSTANDING THE DATA

### Momentum VALUE (0-10 scale)
**Calculation:** Weighted sum of events in 3-minute window
- Events: shots, passes, carries, fouls, etc.
- Weights: shots/goals weighted higher than passes
- Formula: Momentum(X) = weighted_events(X-1, X-2, X-3)
- Higher = more positive team activity

### Momentum CHANGE
**Calculation:** Difference between current and previous momentum
- Formula: Change(X) = Momentum(X) - Momentum(X-3)
- Example: Change(65) = Momentum(65) - Momentum(62)
- Positive = team GAINING momentum (dangerous!)
- Negative = team LOSING momentum (vulnerable!)

### PREDICTIONS (minute 76+)
**What it is:** ARIMAX model predicts future CHANGE values
- Available from minute 76 to end of half
- You see the FULL prediction window
- Analyze: count positive/negative, find crossovers, identify trends

---

## DERIVED METRICS EXPLAINED

### Trajectory
**Calculation:** Compare momentum over last 3 minutes
- "rising" = increased by > 0.3 total
- "falling" = decreased by > 0.3 total
- "stable" = change within ±0.3

### Gap Trend
**Calculation:** Compare |home - away| over last 3 minutes
- "widening" = gap grew by > 0.2
- "narrowing" = gap shrunk by > 0.2
- "stable" = minimal change

### Volatility
**Calculation:** Average of |change| values in history
- "high" = avg |change| > 0.5 (wild swings)
- "medium" = avg |change| 0.2-0.5
- "low" = avg |change| < 0.2 (steady)

### Average Change (match_avg_change)
**Calculation:** Mean of all change values this match
- Use to compare: "current change is 2x match average!"
- Helps identify unusual spikes

### Window Dominance
**Calculation:** Count minutes where home_momentum > away_momentum
- Example: "70% home" = home led in 7 of 10 minutes
- High dominance (70%+) = sustained control

### Historical Crossovers
**What it is:** List of minutes where leadership changed
- Example: [45, 68] = lead changed at min 45 and 68
- Recent crossover = momentum shift just happened

### Number of Sequences
**Calculation:** Count separate groups of consecutive positive changes
- Example: +,+,-,-,+,+,+ → 2 sequences
- More sequences = controls game rhythm

### Longest Sequence
**Calculation:** Max length of consecutive positive changes
- Example: sequences [3, 2, 8, 4] → longest = 8
- Large margin (4+) = sustained dominance

### Prediction Summary (min 76+)
**Contains:**
- home/away_positive_predictions: count of positive predicted changes
- predicted_overall_dominant: which team dominates predictions
- dominance_ratio: e.g., "8/12" = dominant in 8 of 12
- prediction_crossovers: minutes where predicted leadership changes

---

## APPENDIX - Full Research Tables

(Use if you need exact numbers for specific margins)

### Winning Metrics
| Metric | Margin | WIN | LOSE |
|--------|--------|-----|------|
| Abs Momentum | 20%+ | 54.3% | 11.4% |
| Abs Momentum | 50%+ | 64.3% | 14.3% |
| Num Sequences | 3+ seq | 52.9% | 17.6% |
| Num Sequences | 4+ seq | 58.3% | 16.7% |

### Chasing Metrics (Higher = WORSE!)
| Metric | Margin | WIN | LOSE |
|--------|--------|-----|------|
| Pos Changes | 0%+ | 27.7% | 38.3% |
| Longest Seq | 0+ | 22.7% | 43.2% |

### Best Combinations
| Abs Mom | Other | WIN | LOSE |
|---------|-------|-----|------|
| 0%+ | 5%+ Pos Chg | 100% | 0% |
| 20%+ | 3+ Longest | 100% | 0% |
| 15%+ | 0+ Longest | 62.5% | 0% |

### Goal Correlation (96 goals)
| Team | Avg Change | % Positive |
|------|------------|------------|
| Scoring (B-1→A+1) | +0.603 | 72.9% |
| Conceding (B-1→A+1) | -0.368 | 35.4% |

### Event Correlations
| Event | Team | Avg Change |
|-------|------|------------|
| Substitution | Making sub | -0.126 |
| Yellow Card | Receiving | +0.112 |
| Yellow Card | Opponent A+2→A+3 | +0.157 |
"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini", verbose: bool = False, enable_logging: bool = True):
        self.loader = MomentumDataLoader(verbose=verbose)
        self.verbose = verbose
        self.model = model
        self.enable_logging = enable_logging
        
        # Logging setup
        self.log_dir = Path(__file__).parent.parent / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / f"agent_decisions_{datetime.now().strftime('%Y%m%d')}.csv"
        self._init_log_file()
        
        # Initialize OpenAI client
        api_key = api_key or os.getenv('OPENAI_API_KEY')
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None
            if verbose:
                print("[WARN] No OpenAI API key - agent disabled")
    
    def _init_log_file(self):
        """Initialize log file with headers if not exists."""
        if self.enable_logging and not self.log_file.exists():
            headers = [
                'timestamp', 'match_id', 'minute', 'period',
                'score_home', 'score_away', 'home_team', 'away_team',
                'interesting', 'confidence', 'main_finding', 'reason',
                'momentum_gap', 'home_momentum', 'away_momentum',
                'home_change', 'away_change', 'has_tension',
                'is_max_gap', 'home_streak', 'away_streak',
                'game_phase', 'has_predictions'
            ]
            with open(self.log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
    
    def _log_decision(self, match_id: int, minute: int, period: int,
                      game_context: Dict, result: Dict, exploration_data: Dict):
        """Log agent decision for future analysis."""
        if not self.enable_logging:
            return
        
        try:
            current = exploration_data.get('current_momentum', {})
            derived = exploration_data.get('derived', {})
            
            row = [
                datetime.now().isoformat(),
                match_id, minute, period,
                game_context.get('score_home', 0),
                game_context.get('score_away', 0),
                game_context.get('home_team', ''),
                game_context.get('away_team', ''),
                result.get('interesting', False),
                result.get('confidence', 0),
                result.get('main_finding', ''),
                result.get('reason', ''),
                current.get('momentum_diff', 0),
                current.get('home_momentum', 0),
                current.get('away_momentum', 0),
                current.get('home_change', 0),
                current.get('away_change', 0),
                game_context.get('has_tension', False),
                derived.get('is_max_gap', False),
                derived.get('home_streak', {}).get('current_streak', 0),
                derived.get('away_streak', {}).get('current_streak', 0),
                game_context.get('game_phase', ''),
                bool(exploration_data.get('prediction_window'))
            ]
            
            with open(self.log_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row)
        except Exception as e:
            if self.verbose:
                print(f"[WARN] Failed to log decision: {e}")
    
    # =====================================================
    # MAIN ENTRY POINT
    # =====================================================
    
    def explore(
        self,
        match_id: int,
        minute: int,
        period: int,
        score_home: int = 0,
        score_away: int = 0,
        home_team: str = None,
        away_team: str = None,
        recent_events: List[Dict] = None,  # Events from recent minutes
        history_lookback: int = 10  # Give agent more history to explore
    ) -> Dict:
        """
        Let the agent explore momentum data freely.
        
        IMPORTANT: This is for GENERAL commentary only!
        The phrase returned should INTEGRATE with existing commentary.
        
        Args:
            match_id: Match identifier
            minute: Current game minute
            period: Game period
            score_home: Current home score (ACCURATE - counted from goals!)
            score_away: Current away score (ACCURATE - counted from goals!)
            home_team: Home team name
            away_team: Away team name
            recent_events: List of recent events, each with:
                - minute: int
                - event_type: str (Shot, Foul, Pass, etc.)
                - team: str (team name)
                - player: str (optional)
                - detail: str (optional, e.g., "Saved", "Yellow Card")
            history_lookback: How many minutes of history to provide
        
        Returns:
            Agent's exploration results with phrase to ADD to commentary
        """
        
        # Load ALL available data for this minute
        context = self.loader.get_full_context(
            match_id, minute, period,
            include_history=True,
            lookback=history_lookback
        )
        
        # Only hard rule: skip if no data at all
        if not context.get('has_momentum'):
            return {
                'interesting': False,
                'reason': 'no_data',
                'phrase': None,
                'raw_data': None
            }
        
        home_team = home_team or context.get('home_team')
        away_team = away_team or context.get('away_team')
        
        # V6.2: Get running totals for the entire match up to this minute
        running_totals = self.loader.get_match_running_totals(match_id, minute, period)
        
        # Build game context (for agent decision and logging)
        game_context = self._build_game_context(
            minute, period, score_home, score_away,
            home_team, away_team, context
        )
        
        # Prepare rich data for agent exploration
        exploration_data = self._prepare_exploration_data(
            context, minute, period, 
            score_home, score_away,
            home_team, away_team,
            recent_events,  # Pass events to preparation
            game_context,  # Pass game context
            running_totals  # V6.2: Pass running totals
        )
        
        # Let the agent explore!
        if self.client:
            result = self._explore_with_llm(exploration_data)
            result['raw_data'] = exploration_data
            result['game_context'] = game_context
            
            # Log decision for future analysis
            self._log_decision(match_id, minute, period, game_context, result, exploration_data)
            
            return result
        else:
            return {
                'interesting': False,
                'reason': 'no_api_key',
                'phrase': None,
                'raw_data': exploration_data
            }
    
    def _build_game_context(self, minute: int, period: int, 
                            score_home: int, score_away: int,
                            home_team: str, away_team: str,
                            momentum_context: Dict) -> Dict:
        """Build game context for agent decision-making."""
        
        home_mom = momentum_context.get('home_momentum', 0) or 0
        away_mom = momentum_context.get('away_momentum', 0) or 0
        
        # Determine who leads what
        score_leader = 'home' if score_home > score_away else ('away' if score_away > score_home else 'tied')
        momentum_leader = 'home' if home_mom > away_mom + 0.2 else ('away' if away_mom > home_mom + 0.2 else 'even')
        
        # Tension: score and momentum leaders are DIFFERENT
        has_tension = (
            score_leader != 'tied' and 
            momentum_leader != 'even' and 
            score_leader != momentum_leader
        )
        
        return {
            'minute': minute,
            'period': period,
            'game_phase': self._get_game_phase(minute),
            'score_home': score_home,
            'score_away': score_away,
            'score_diff': abs(score_home - score_away),
            'is_close_game': abs(score_home - score_away) <= 1,
            'is_tied': score_home == score_away,
            'home_team': home_team,
            'away_team': away_team,
            'score_leader': score_leader,
            'score_leader_name': home_team if score_leader == 'home' else (away_team if score_leader == 'away' else 'Tied'),
            'momentum_leader': momentum_leader,
            'momentum_leader_name': home_team if momentum_leader == 'home' else (away_team if momentum_leader == 'away' else 'Even'),
            'has_tension': has_tension,  # Score leader != momentum leader
            'is_late_game': minute >= 75,
            'is_early_game': minute <= 15,
        }
    
    # =====================================================
    # DATA PREPARATION - Give agent EVERYTHING
    # =====================================================
    
    def _prepare_exploration_data(
        self,
        context: Dict,
        minute: int,
        period: int,
        score_home: int,
        score_away: int,
        home_team: str,
        away_team: str,
        recent_events: List[Dict] = None,
        game_context: Dict = None,
        running_totals: Dict = None  # V6.2: Running totals for research threshold comparison
    ) -> Dict:
        """
        Prepare ALL momentum data for agent exploration.
        No filtering - agent sees everything.
        Includes recent events for context.
        V6.2: Includes running totals for research threshold comparison.
        """
        
        # Use game context if provided, otherwise build basic context
        gc = game_context or {}
        rt = running_totals or {}
        
        data = {
            'match_context': {
                'minute': minute,
                'period': period,
                'period_name': self._get_period_name(period),
                'game_phase': gc.get('game_phase', self._get_game_phase(minute)),
                'home_team': home_team,
                'away_team': away_team,
                'score_home': score_home,
                'score_away': score_away,
                'score_diff': score_home - score_away,
                'is_tied': gc.get('is_tied', score_home == score_away),
                'home_winning': score_home > score_away,
                'away_winning': score_away > score_home,
                # NEW: Game context indicators
                'is_close_game': gc.get('is_close_game', abs(score_home - score_away) <= 1),
                'is_late_game': gc.get('is_late_game', minute >= 75),
                'is_early_game': gc.get('is_early_game', minute <= 15),
                'score_leader': gc.get('score_leader_name', ''),
                'momentum_leader': gc.get('momentum_leader_name', ''),
                'has_tension': gc.get('has_tension', False),
            },
            'current_momentum': {
                'home_momentum': context.get('home_momentum', 0),
                'away_momentum': context.get('away_momentum', 0),
                'momentum_diff': context.get('momentum_diff', 0),
                'home_change': context.get('home_change', 0),
                'away_change': context.get('away_change', 0),
                'dominant_team': context.get('dominant_team'),
                'events_count': context.get('events_count', 0)
            },
            'recent_events': recent_events or [],
            'history': [],
            'predictions': None,
            'prediction_window': [],  # NEW: Full prediction window from minute 76+
            # V6.2: Running totals from minute 0 to current (for research threshold comparison)
            'running_totals': {
                'home_total': rt.get('home_total_momentum', 0),
                'away_total': rt.get('away_total_momentum', 0),
                'home_seq': rt.get('home_num_sequences', 0),
                'away_seq': rt.get('away_num_sequences', 0),
                'home_long': rt.get('home_longest_sequence', 0),
                'away_long': rt.get('away_longest_sequence', 0),
                'home_pos': rt.get('home_positive_changes', 0),  # until minute-3 inclusive
                'away_pos': rt.get('away_positive_changes', 0),
                'home_pred_pos': rt.get('home_predicted_positive', 0),  # from min 76, same for all
                'away_pred_pos': rt.get('away_predicted_positive', 0),
            } if rt else {}
        }
        
        # Add full history for pattern discovery
        if context.get('has_history') and context.get('history'):
            for entry in context['history']:
                data['history'].append({
                    'minute': entry.get('minute'),
                    'home_momentum': entry.get('home_momentum'),
                    'away_momentum': entry.get('away_momentum'),
                    'home_change': entry.get('home_change'),
                    'away_change': entry.get('away_change'),
                    'momentum_diff': entry.get('momentum_diff')
                })
        
        # Add current minute prediction if available
        if context.get('has_prediction') and context.get('predictions'):
            pred = context['predictions']
            data['predictions'] = {
                'home_predicted_change': pred.get('home_predicted_change'),
                'away_predicted_change': pred.get('away_predicted_change'),
                'expected_dominant': pred.get('expected_dominant'),
                'home_accuracy': pred.get('home_accuracy'),
                'away_accuracy': pred.get('away_accuracy')
            }
        
        # NEW: Add FULL prediction window (minute 76+)
        # This gives the agent ALL predictions from current minute to end of half
        if context.get('has_prediction_window') and context.get('prediction_window'):
            for pred in context['prediction_window']:
                data['prediction_window'].append({
                    'minute': pred.get('minute'),
                    'home_predicted_change': pred.get('home_predicted_change'),
                    'away_predicted_change': pred.get('away_predicted_change'),
                    'expected_dominant': pred.get('expected_dominant')
                })
        
        # Calculate derived metrics for agent
        data['derived'] = self._calculate_derived_metrics(data)
        
        return data
    
    def _calculate_derived_metrics(self, data: Dict) -> Dict:
        """Calculate additional metrics to help agent exploration."""
        
        derived = {}
        history = data.get('history', [])
        current = data.get('current_momentum', {})
        prediction_window = data.get('prediction_window', [])
        
        if len(history) >= 2:
            # Home team streaks
            home_streak = self._calculate_streak_info(history, 'home_change')
            derived['home_streak'] = home_streak
            
            # Away team streaks
            away_streak = self._calculate_streak_info(history, 'away_change')
            derived['away_streak'] = away_streak
            
            # Momentum trajectory
            derived['home_trajectory'] = self._calculate_trajectory(history, 'home_momentum')
            derived['away_trajectory'] = self._calculate_trajectory(history, 'away_momentum')
            
            # Gap trend
            derived['gap_trend'] = self._calculate_gap_trend(history)
            
            # Volatility
            derived['home_volatility'] = self._calculate_volatility(history, 'home_change')
            derived['away_volatility'] = self._calculate_volatility(history, 'away_change')
            
            # NEW: Average change (actual number for comparison)
            home_changes = [h.get('home_change', 0) or 0 for h in history]
            away_changes = [h.get('away_change', 0) or 0 for h in history]
            derived['home_avg_change'] = round(sum(home_changes) / len(home_changes), 3) if home_changes else 0
            derived['away_avg_change'] = round(sum(away_changes) / len(away_changes), 3) if away_changes else 0
            derived['match_avg_change'] = round((sum(abs(c) for c in home_changes + away_changes)) / (len(home_changes) + len(away_changes)), 3) if home_changes else 0
            
            # NEW: Window dominance (how many minutes each team "won")
            derived['window_dominance'] = self._calculate_window_dominance(history)
            
            # NEW: Sequence metrics (for research thresholds comparison)
            derived['sequence_metrics'] = self._calculate_sequence_metrics(history)
            
            # NEW: Historical crossovers (where momentum leadership changed)
            derived['historical_crossovers'] = self._calculate_crossovers(history)
        
        # Max values in history
        if history:
            derived['max_home_momentum'] = max(h.get('home_momentum', 0) or 0 for h in history)
            derived['min_home_momentum'] = min(h.get('home_momentum', 0) or 0 for h in history)
            derived['max_away_momentum'] = max(h.get('away_momentum', 0) or 0 for h in history)
            derived['min_away_momentum'] = min(h.get('away_momentum', 0) or 0 for h in history)
            derived['max_gap'] = max(abs(h.get('momentum_diff', 0) or 0) for h in history)
            
            # NEW: Is current gap the MAXIMUM in match history? (Hot time indicator!)
            current_gap = abs(current.get('momentum_diff', 0) or 0)
            derived['is_max_gap'] = current_gap >= derived['max_gap'] * 0.95  # Allow 5% tolerance
            derived['current_gap'] = current_gap
            
            # NEW: Is current change the maximum?
            all_home_changes = [abs(h.get('home_change', 0) or 0) for h in history]
            all_away_changes = [abs(h.get('away_change', 0) or 0) for h in history]
            max_change = max(max(all_home_changes) if all_home_changes else 0, 
                           max(all_away_changes) if all_away_changes else 0)
            current_home_change = abs(current.get('home_change', 0) or 0)
            current_away_change = abs(current.get('away_change', 0) or 0)
            derived['is_max_change'] = max(current_home_change, current_away_change) >= max_change * 0.95
            derived['max_change_in_history'] = max_change
        
        # NEW: Prediction summary (minute 76+ only)
        if prediction_window:
            derived['prediction_summary'] = self._calculate_prediction_summary(prediction_window)
        
        return derived
    
    def _calculate_window_dominance(self, history: List[Dict]) -> Dict:
        """Calculate how many windows each team dominated."""
        home_wins = 0
        away_wins = 0
        ties = 0
        
        for h in history:
            home_mom = h.get('home_momentum', 0) or 0
            away_mom = h.get('away_momentum', 0) or 0
            diff = home_mom - away_mom
            
            if diff > 0.1:
                home_wins += 1
            elif diff < -0.1:
                away_wins += 1
            else:
                ties += 1
        
        total = home_wins + away_wins + ties
        return {
            'home_windows_won': home_wins,
            'away_windows_won': away_wins,
            'tied_windows': ties,
            'home_dominance_pct': round(home_wins / total * 100, 1) if total > 0 else 0,
            'away_dominance_pct': round(away_wins / total * 100, 1) if total > 0 else 0
        }
    
    def _calculate_sequence_metrics(self, history: List[Dict]) -> Dict:
        """Calculate sequence metrics matching research thresholds."""
        
        # Count positive sequences for each team
        home_sequences = self._count_sequences(history, 'home_change')
        away_sequences = self._count_sequences(history, 'away_change')
        
        # Calculate margins
        seq_count_margin = home_sequences['total_positive_sequences'] - away_sequences['total_positive_sequences']
        longest_margin = home_sequences['longest_positive'] - away_sequences['longest_positive']
        
        # Calculate momentum margin (absolute difference as percentage)
        total_home = sum(h.get('home_momentum', 0) or 0 for h in history)
        total_away = sum(h.get('away_momentum', 0) or 0 for h in history)
        total = total_home + total_away
        momentum_margin_pct = abs(total_home - total_away) / total * 100 if total > 0 else 0
        momentum_leader = 'home' if total_home > total_away else 'away'
        
        return {
            'home': home_sequences,
            'away': away_sequences,
            'seq_count_margin': abs(seq_count_margin),
            'seq_leader': 'home' if seq_count_margin > 0 else 'away' if seq_count_margin < 0 else 'tied',
            'longest_margin': abs(longest_margin),
            'longest_leader': 'home' if longest_margin > 0 else 'away' if longest_margin < 0 else 'tied',
            'momentum_margin_pct': round(momentum_margin_pct, 1),
            'momentum_leader': momentum_leader
        }
    
    def _count_sequences(self, history: List[Dict], change_key: str) -> Dict:
        """Count positive/negative sequences for a team."""
        total_positive_seq = 0
        total_negative_seq = 0
        longest_positive = 0
        longest_negative = 0
        current_streak = 0
        current_dir = None
        
        for h in history:
            change = h.get(change_key, 0) or 0
            
            if change > 0.05:  # Positive
                if current_dir == 'positive':
                    current_streak += 1
                else:
                    if current_dir == 'negative' and current_streak >= 2:
                        total_negative_seq += 1
                    current_streak = 1
                    current_dir = 'positive'
                longest_positive = max(longest_positive, current_streak)
                
            elif change < -0.05:  # Negative
                if current_dir == 'negative':
                    current_streak += 1
                else:
                    if current_dir == 'positive' and current_streak >= 2:
                        total_positive_seq += 1
                    current_streak = 1
                    current_dir = 'negative'
                longest_negative = max(longest_negative, current_streak)
            else:
                # End current sequence if it was 2+
                if current_dir == 'positive' and current_streak >= 2:
                    total_positive_seq += 1
                elif current_dir == 'negative' and current_streak >= 2:
                    total_negative_seq += 1
                current_streak = 0
                current_dir = None
        
        # Count final sequence if applicable
        if current_dir == 'positive' and current_streak >= 2:
            total_positive_seq += 1
        elif current_dir == 'negative' and current_streak >= 2:
            total_negative_seq += 1
        
        return {
            'total_positive_sequences': total_positive_seq,
            'total_negative_sequences': total_negative_seq,
            'longest_positive': longest_positive,
            'longest_negative': longest_negative
        }
    
    def _calculate_crossovers(self, history: List[Dict]) -> List[int]:
        """Find minutes where momentum leadership changed."""
        crossovers = []
        
        for i in range(1, len(history)):
            prev_diff = history[i-1].get('momentum_diff', 0) or 0
            curr_diff = history[i].get('momentum_diff', 0) or 0
            
            # Crossover if sign changed (and both are significant)
            if abs(prev_diff) > 0.1 and abs(curr_diff) > 0.1:
                if (prev_diff > 0 and curr_diff < 0) or (prev_diff < 0 and curr_diff > 0):
                    minute = history[i].get('minute', 0)
                    if minute:
                        crossovers.append(minute)
        
        return crossovers
    
    def _calculate_prediction_summary(self, prediction_window: List[Dict]) -> Dict:
        """
        Analyze full prediction window (minute 76+) and create summary.
        This is the "dotted line" analysis.
        """
        if not prediction_window:
            return {}
        
        # Extract prediction values
        home_preds = []
        away_preds = []
        
        for p in prediction_window:
            home_val = p.get('home_predicted_change')
            away_val = p.get('away_predicted_change')
            if home_val is not None:
                home_preds.append(home_val)
            if away_val is not None:
                away_preds.append(away_val)
        
        if not home_preds or not away_preds:
            return {}
        
        summary = {}
        
        # 1. Counts (positive/negative predictions)
        summary['home_positive_predictions'] = sum(1 for p in home_preds if p > 0.05)
        summary['home_negative_predictions'] = sum(1 for p in home_preds if p < -0.05)
        summary['home_neutral_predictions'] = len(home_preds) - summary['home_positive_predictions'] - summary['home_negative_predictions']
        
        summary['away_positive_predictions'] = sum(1 for p in away_preds if p > 0.05)
        summary['away_negative_predictions'] = sum(1 for p in away_preds if p < -0.05)
        summary['away_neutral_predictions'] = len(away_preds) - summary['away_positive_predictions'] - summary['away_negative_predictions']
        
        # 2. Averages
        summary['home_avg_predicted'] = round(sum(home_preds) / len(home_preds), 3)
        summary['away_avg_predicted'] = round(sum(away_preds) / len(away_preds), 3)
        
        # 3. Extremes
        summary['home_max_predicted'] = round(max(home_preds), 3)
        summary['home_min_predicted'] = round(min(home_preds), 3)
        summary['away_max_predicted'] = round(max(away_preds), 3)
        summary['away_min_predicted'] = round(min(away_preds), 3)
        
        # 4. Trends (first half vs second half of window)
        if len(home_preds) >= 4:
            mid = len(home_preds) // 2
            first_half_home = sum(home_preds[:mid]) / mid
            second_half_home = sum(home_preds[mid:]) / (len(home_preds) - mid)
            first_half_away = sum(away_preds[:mid]) / mid
            second_half_away = sum(away_preds[mid:]) / (len(away_preds) - mid)
            
            # Home trend
            if second_half_home > first_half_home + 0.1:
                summary['home_trend'] = 'improving'
            elif second_half_home < first_half_home - 0.1:
                summary['home_trend'] = 'declining'
            else:
                summary['home_trend'] = 'stable'
            
            # Away trend
            if second_half_away > first_half_away + 0.1:
                summary['away_trend'] = 'improving'
            elif second_half_away < first_half_away - 0.1:
                summary['away_trend'] = 'declining'
            else:
                summary['away_trend'] = 'stable'
        else:
            summary['home_trend'] = 'insufficient_data'
            summary['away_trend'] = 'insufficient_data'
        
        # 5. Prediction crossovers (where predicted dominance switches)
        pred_crossovers = []
        for i in range(1, len(prediction_window)):
            prev = prediction_window[i-1]
            curr = prediction_window[i]
            prev_diff = (prev.get('home_predicted_change') or 0) - (prev.get('away_predicted_change') or 0)
            curr_diff = (curr.get('home_predicted_change') or 0) - (curr.get('away_predicted_change') or 0)
            
            if (prev_diff > 0.05 and curr_diff < -0.05) or (prev_diff < -0.05 and curr_diff > 0.05):
                minute = curr.get('minute')
                if minute:
                    pred_crossovers.append(minute)
        
        summary['prediction_crossovers'] = pred_crossovers
        
        # 6. Overall prediction - who dominates more predictions?
        home_dominant_count = sum(1 for p in prediction_window 
                                  if (p.get('home_predicted_change') or 0) > (p.get('away_predicted_change') or 0) + 0.05)
        away_dominant_count = sum(1 for p in prediction_window 
                                  if (p.get('away_predicted_change') or 0) > (p.get('home_predicted_change') or 0) + 0.05)
        
        summary['home_dominant_predictions'] = home_dominant_count
        summary['away_dominant_predictions'] = away_dominant_count
        summary['predicted_overall_dominant'] = 'home' if home_dominant_count > away_dominant_count else 'away' if away_dominant_count > home_dominant_count else 'balanced'
        summary['dominance_ratio'] = f"{max(home_dominant_count, away_dominant_count)}/{len(prediction_window)}"
        summary['total_predictions'] = len(prediction_window)
        
        return summary
    
    def _calculate_streak_info(self, history: List[Dict], change_key: str) -> Dict:
        """Calculate streak information for a team."""
        
        positive_streak = 0
        negative_streak = 0
        current_streak = 0
        current_direction = None
        
        for entry in history:
            change = entry.get(change_key, 0) or 0
            
            if change > 0.1:
                if current_direction == 'positive':
                    current_streak += 1
                else:
                    current_streak = 1
                    current_direction = 'positive'
                positive_streak = max(positive_streak, current_streak)
                
            elif change < -0.1:
                if current_direction == 'negative':
                    current_streak += 1
                else:
                    current_streak = 1
                    current_direction = 'negative'
                negative_streak = max(negative_streak, current_streak)
            else:
                current_streak = 0
                current_direction = None
        
        return {
            'max_positive_streak': positive_streak,
            'max_negative_streak': negative_streak,
            'current_streak': current_streak,
            'current_direction': current_direction
        }
    
    def _calculate_trajectory(self, history: List[Dict], momentum_key: str) -> str:
        """Determine if momentum is rising, falling, or stable."""
        
        if len(history) < 3:
            return 'unknown'
        
        recent = [h.get(momentum_key, 0) or 0 for h in history[-3:]]
        
        if recent[-1] > recent[0] + 0.3:
            return 'rising'
        elif recent[-1] < recent[0] - 0.3:
            return 'falling'
        else:
            return 'stable'
    
    def _calculate_gap_trend(self, history: List[Dict]) -> str:
        """Determine if gap between teams is widening or narrowing."""
        
        if len(history) < 3:
            return 'unknown'
        
        gaps = [abs(h.get('momentum_diff', 0) or 0) for h in history[-3:]]
        
        if gaps[-1] > gaps[0] + 0.2:
            return 'widening'
        elif gaps[-1] < gaps[0] - 0.2:
            return 'narrowing'
        else:
            return 'stable'
    
    def _calculate_volatility(self, history: List[Dict], change_key: str) -> str:
        """Determine how volatile the momentum changes are."""
        
        if len(history) < 3:
            return 'unknown'
        
        changes = [abs(h.get(change_key, 0) or 0) for h in history]
        avg_change = sum(changes) / len(changes)
        
        if avg_change > 0.5:
            return 'high'
        elif avg_change > 0.2:
            return 'medium'
        else:
            return 'low'
    
    def _get_period_name(self, period: int) -> str:
        """Convert period number to name."""
        names = {1: 'First Half', 2: 'Second Half', 3: 'Extra Time 1st', 4: 'Extra Time 2nd'}
        return names.get(period, f'Period {period}')
    
    def _get_game_phase(self, minute: int) -> str:
        """Determine game phase from minute."""
        if minute <= 15:
            return 'early'
        elif minute <= 30:
            return 'build_up'
        elif minute <= 45:
            return 'first_half_end'
        elif minute <= 60:
            return 'second_half_start'
        elif minute <= 75:
            return 'mid_second_half'
        elif minute <= 85:
            return 'final_push'
        else:
            return 'closing_minutes'
    
    # =====================================================
    # LLM EXPLORATION
    # =====================================================
    
    def _explore_with_llm(self, data: Dict) -> Dict:
        """Let the LLM freely explore the data."""
        
        # Build rich prompt with all data
        prompt = self._build_exploration_prompt(data)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.EXPLORATION_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower for consistency (was 0.5)
                max_tokens=200,
                seed=42  # Fixed seed for reproducibility
            )
            
            return self._parse_exploration_response(response.choices[0].message.content)
            
        except Exception as e:
            if self.verbose:
                print(f"[ERROR] LLM exploration failed: {e}")
            return {
                'interesting': False,
                'reason': f'llm_error: {str(e)}',
                'phrase': None
            }
    
    def _build_exploration_prompt(self, data: Dict) -> str:
        """Build comprehensive prompt with all data for exploration."""
        
        ctx = data['match_context']
        mom = data['current_momentum']
        derived = data.get('derived', {})
        recent_events = data.get('recent_events', [])
        
        # Build tension indicator
        tension_note = ""
        if ctx.get('has_tension'):
            tension_note = f"\n**TENSION ALERT:** Score leader ({ctx['score_leader']}) != Momentum leader ({ctx['momentum_leader']})!"
        
        # Game importance indicator
        importance = "HIGH" if ctx.get('is_close_game') or ctx.get('is_late_game') else "Normal"
        if ctx.get('is_early_game') and not ctx.get('has_tension'):
            importance = "Low (early game)"
        
        prompt = f"""
## Match Situation

**{ctx['home_team']} vs {ctx['away_team']}**
- Score: {ctx['home_team']} {ctx['score_home']} - {ctx['score_away']} {ctx['away_team']}
- Minute: {ctx['minute']}' ({ctx['period_name']})
- Game Phase: {ctx['game_phase']}
- Pattern Importance: {importance}
- Close Game: {'YES' if ctx.get('is_close_game') else 'No'}
- Late Game: {'YES - every shift matters!' if ctx.get('is_late_game') else 'No'}
{tension_note}

## Recent Events (What just happened)

"""
        # Add recent events
        if recent_events:
            prompt += "| Minute | Team | Event | Detail |\n"
            prompt += "|--------|------|-------|--------|\n"
            for event in sorted(recent_events, key=lambda x: x.get('minute', 0)):
                evt_min = event.get('minute', '?')
                evt_team = event.get('team', '?')
                evt_type = event.get('event_type', '?')
                evt_detail = event.get('detail', '')
                player = event.get('player', '')
                detail_str = f"{evt_detail} - {player}" if player else evt_detail
                prompt += f"| {evt_min}' | {evt_team} | {evt_type} | {detail_str} |\n"
        else:
            prompt += "No specific events in recent minutes (quiet period)\n"
        
        prompt += f"""

## Current Momentum State (Minute {ctx['minute']}')

### Data Timing Explanation:
- Momentum({ctx['minute']}) = events from minutes {ctx['minute']-1}, {ctx['minute']-2}, {ctx['minute']-3}
- Change shown is for minute {ctx['minute']-3}: Change({ctx['minute']-3}) = Momentum({ctx['minute']}) - Momentum({ctx['minute']-3})
- Change({ctx['minute']-3}) = events({ctx['minute']-1},{ctx['minute']-2},{ctx['minute']-3}) - events({ctx['minute']-4},{ctx['minute']-5},{ctx['minute']-6})

| Metric | {ctx['home_team']} | {ctx['away_team']} | Based On |
|--------|---------|---------|---------|
| Momentum | {mom['home_momentum']:.2f} | {mom['away_momentum']:.2f} | events[{ctx['minute']-1},{ctx['minute']-2},{ctx['minute']-3}] |
| Change | {mom['home_change']:+.2f} | {mom['away_change']:+.2f} | mom({ctx['minute']}) - mom({ctx['minute']-3}) |

**Interpretation:**
- Momentum Difference: {mom['momentum_diff']:+.2f} ({'Home advantage' if mom['momentum_diff'] > 0.3 else 'Away advantage' if mom['momentum_diff'] < -0.3 else 'Even'})
- Dominant: {mom['dominant_team']}
- {ctx['home_team']} trend: {'RISING' if mom['home_change'] > 0.3 else 'FALLING' if mom['home_change'] < -0.3 else 'Stable'}
- {ctx['away_team']} trend: {'RISING' if mom['away_change'] > 0.3 else 'FALLING' if mom['away_change'] < -0.3 else 'Stable'}

"""
        
        # V6.2: Add running totals for research threshold comparison
        rt = data.get('running_totals', {})
        if rt and rt.get('home_total', 0) > 0:
            # Calculate margin for research threshold matching
            home_total = rt.get('home_total', 0)
            away_total = rt.get('away_total', 0)
            total_margin = abs(home_total - away_total) / max(away_total, home_total) * 100 if max(away_total, home_total) > 0 else 0
            total_leader = ctx['home_team'] if home_total > away_total else ctx['away_team']
            
            prompt += f"""
## MATCH TOTALS (minute 0 → {ctx['minute']}' inclusive) - USE FOR RESEARCH THRESHOLDS!

| Metric | {ctx['home_team']} | {ctx['away_team']} |
|--------|---------|---------|
| Total Momentum | {rt.get('home_total', 0):.1f} | {rt.get('away_total', 0):.1f} |
| Num Sequences | {rt.get('home_seq', 0)} | {rt.get('away_seq', 0)} |
| Longest Seq | {rt.get('home_long', 0)} | {rt.get('away_long', 0)} |
| Positive Changes (→ min {ctx['minute']-3}) | {rt.get('home_pos', 0)} | {rt.get('away_pos', 0)} |
"""
            # Add predicted totals if available (period 2, minute 76+)
            if rt.get('home_pred_pos', 0) > 0 or rt.get('away_pred_pos', 0) > 0:
                prompt += f"""| Predicted Pos (76→end) | {rt.get('home_pred_pos', 0)} | {rt.get('away_pred_pos', 0)} |
"""
            
            prompt += f"""
**Margin Analysis (for research patterns):**
- Total Momentum Margin: {total_margin:.1f}% ({total_leader} leads)
- Check QUICK REFERENCE: 20%+ margin + 3+ longest = 0% LOSE pattern!

"""
        
        prompt += f"""## Historical Data (Last {len(data['history'])} minutes)

"""
        # Add history table
        if data['history']:
            prompt += "| Minute | Home Mom | Away Mom | Home Chg | Away Chg | Diff |\n"
            prompt += "|--------|----------|----------|----------|----------|------|\n"
            for h in data['history']:
                prompt += f"| {h['minute']}' | {h['home_momentum']:.2f} | {h['away_momentum']:.2f} | {(h['home_change'] or 0):+.2f} | {(h['away_change'] or 0):+.2f} | {(h['momentum_diff'] or 0):+.2f} |\n"
        
        # Add derived metrics
        if derived:
            prompt += f"""

## Derived Insights

**{ctx['home_team']} Streaks:** 
- Max positive streak: {derived.get('home_streak', {}).get('max_positive_streak', 0)} min
- Max negative streak: {derived.get('home_streak', {}).get('max_negative_streak', 0)} min
- Current: {derived.get('home_streak', {}).get('current_streak', 0)} min {derived.get('home_streak', {}).get('current_direction', 'none')}

**{ctx['away_team']} Streaks:**
- Max positive streak: {derived.get('away_streak', {}).get('max_positive_streak', 0)} min
- Max negative streak: {derived.get('away_streak', {}).get('max_negative_streak', 0)} min
- Current: {derived.get('away_streak', {}).get('current_streak', 0)} min {derived.get('away_streak', {}).get('current_direction', 'none')}

**Trajectories:**
- {ctx['home_team']}: {derived.get('home_trajectory', 'unknown')}
- {ctx['away_team']}: {derived.get('away_trajectory', 'unknown')}

**Gap Trend:** {derived.get('gap_trend', 'unknown')}
**Volatility:** {ctx['home_team']}={derived.get('home_volatility', 'unknown')}, {ctx['away_team']}={derived.get('away_volatility', 'unknown')}

**Average Changes (for comparison):**
- {ctx['home_team']} avg change: {derived.get('home_avg_change', 0):+.3f}
- {ctx['away_team']} avg change: {derived.get('away_avg_change', 0):+.3f}
- Match avg |change|: {derived.get('match_avg_change', 0):.3f}

**Extremes in this window:**
- {ctx['home_team']} momentum range: {derived.get('min_home_momentum', 0):.2f} - {derived.get('max_home_momentum', 0):.2f}
- {ctx['away_team']} momentum range: {derived.get('min_away_momentum', 0):.2f} - {derived.get('max_away_momentum', 0):.2f}
- Max gap seen: {derived.get('max_gap', 0):.2f}

**HOT TIME INDICATORS:**
- Is current gap the LARGEST in match? {'YES - HOT TIME!' if derived.get('is_max_gap') else 'No'}
- Is current change the LARGEST in match? {'YES - MOMENTUM SHIFT!' if derived.get('is_max_change') else 'No'}
- Current gap: {derived.get('current_gap', 0):.2f} (max was {derived.get('max_gap', 0):.2f})
"""
        
        # Add predictions if available (only minute 76+)
        if data.get('predictions') or data.get('prediction_window'):
            pred = data.get('predictions', {})
            pred_window = data.get('prediction_window', [])
            
            prompt += f"""

## ARIMAX Predictions (PRIORITIZE THIS DATA!)

### Data Timing Reminder:
- Predictions START at minute 76 (not 75)
- At minute 75: we have ACTUAL momentum change (calculated from events 74,73,72)
- From minute 76: ARIMAX predicts future momentum CHANGE

### Current Minute ({ctx['minute']}') Prediction:
"""
            if pred:
                prompt += f"""- {ctx['home_team']} predicted change: {pred['home_predicted_change']:+.2f} {'(SURGE expected!)' if pred['home_predicted_change'] > 0.5 else '(decline expected)' if pred['home_predicted_change'] < -0.3 else ''}
- {ctx['away_team']} predicted change: {pred['away_predicted_change']:+.2f} {'(SURGE expected!)' if pred['away_predicted_change'] > 0.5 else '(decline expected)' if pred['away_predicted_change'] < -0.3 else ''}
- Expected to improve more: {pred['expected_dominant']}
"""
            else:
                prompt += "No prediction for current minute.\n"
            
            # FULL PREDICTION WINDOW - This is the key addition!
            if pred_window:
                prompt += f"""
### FULL PREDICTION WINDOW (Minutes {pred_window[0]['minute']}'-{pred_window[-1]['minute']}')

YOU CAN SEE ALL REMAINING PREDICTIONS TO END OF HALF!
Analyze trends, count consecutive positive/negative, find reversals!

| Minute | {ctx['home_team']} Pred | {ctx['away_team']} Pred | Expected |
|--------|------------|------------|----------|
"""
                for pw in pred_window:
                    home_pred = pw.get('home_predicted_change', 0)
                    away_pred = pw.get('away_predicted_change', 0)
                    expected = pw.get('expected_dominant', '?')
                    prompt += f"| {pw['minute']}' | {home_pred:+.2f} | {away_pred:+.2f} | {expected} |\n"
                
                # Add summary stats for the window
                home_preds = [pw.get('home_predicted_change', 0) for pw in pred_window]
                away_preds = [pw.get('away_predicted_change', 0) for pw in pred_window]
                home_positive = sum(1 for p in home_preds if p > 0.1)
                home_negative = sum(1 for p in home_preds if p < -0.1)
                away_positive = sum(1 for p in away_preds if p > 0.1)
                away_negative = sum(1 for p in away_preds if p < -0.1)
                
                prompt += f"""
### Prediction Window Summary:
- {ctx['home_team']}: {home_positive} positive predictions, {home_negative} negative predictions
- {ctx['away_team']}: {away_positive} positive predictions, {away_negative} negative predictions
- Total predictions available: {len(pred_window)} minutes
"""
        elif ctx['minute'] == 75:
            prompt += f"""

## ARIMAX Predictions
Minute 75: This is the LAST minute with ACTUAL data only.
- You have actual momentum change (calculated from events 74,73,72)
- Predictions will be available starting minute 76
"""
        elif ctx['minute'] < 75:
            prompt += f"""

## ARIMAX Predictions
Not available yet (predictions start from minute 76).
Until minute 75, you have ACTUAL momentum data only.
"""
        else:
            prompt += f"""

## ARIMAX Predictions
No prediction data available for this minute.
"""
        
        prompt += """

## Your Task

Explore this data freely. Find what's INTERESTING.
Don't limit yourself to the pattern vocabulary - discover your own insights!

What story does this momentum data tell?
"""
        
        return prompt
    
    def _parse_exploration_response(self, response: str) -> Dict:
        """Parse the agent's exploration response.
        
        New format focuses on data selection, not phrase writing:
        - INTERESTING: YES/NO
        - CONFIDENCE: 0.0-1.0
        - MAIN_FINDING: 1-line summary of pattern
        - FORWARD_DATA: list of data points to show
        - REASON: why this data matters
        """
        
        result = {
            'interesting': False,
            'confidence': 0.5,
            'main_finding': None,  # NEW: 1-line summary
            'forward_data': [],  # List of data lines to forward
            'reason': None,
            # Keep old fields for backwards compatibility
            'pattern': None,
            'phrase': None,
        }
        
        lines = response.strip().split('\n')
        in_forward_data = False
        
        for line in lines:
            line = line.strip()
            upper = line.upper()
            
            if upper.startswith('INTERESTING:'):
                value = line.split(':', 1)[1].strip().upper()
                result['interesting'] = 'YES' in value
                in_forward_data = False
                
            elif upper.startswith('CONFIDENCE:'):
                conf_str = line.split(':', 1)[1].strip()
                try:
                    conf_str = conf_str.replace('%', '').strip()
                    if conf_str.upper() == 'HIGH':
                        result['confidence'] = 0.9
                    elif conf_str.upper() == 'MEDIUM':
                        result['confidence'] = 0.6
                    elif conf_str.upper() == 'LOW':
                        result['confidence'] = 0.3
                    else:
                        conf_val = float(conf_str)
                        if conf_val > 1:
                            conf_val = conf_val / 100
                        result['confidence'] = max(0.0, min(1.0, conf_val))
                except:
                    result['confidence'] = 0.5
                in_forward_data = False
            
            elif upper.startswith('MAIN_FINDING:'):
                result['main_finding'] = line.split(':', 1)[1].strip()
                in_forward_data = False
                    
            elif upper.startswith('FORWARD_DATA:'):
                in_forward_data = True
                # Check if data is on same line
                rest = line.split(':', 1)[1].strip()
                if rest.lower() != 'none' and rest:
                    result['forward_data'].append(rest)
                    
            elif upper.startswith('REASON:'):
                result['reason'] = line.split(':', 1)[1].strip()
                in_forward_data = False
                
            elif in_forward_data and line.startswith('-'):
                # Data line within FORWARD_DATA section
                data_line = line[1:].strip()  # Remove leading dash
                if data_line.lower() != 'none' and data_line:
                    result['forward_data'].append(data_line)
                    
            # Legacy support for old format
            elif upper.startswith('PATTERN:'):
                result['pattern'] = line.split(':', 1)[1].strip()
                in_forward_data = False
                
            elif upper.startswith('PHRASE:'):
                phrase = line.split(':', 1)[1].strip()
                if phrase.lower() != 'none':
                    result['phrase'] = phrase
                in_forward_data = False
        
        return result


# =====================================================
# TEST
# =====================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Testing Exploratory Momentum Agent")
    print("(For GENERAL commentary - integrates with existing flow)")
    print("=" * 70)
    
    agent = ExploratoryMomentumAgent(verbose=True)
    
    # Example recent events (like you would get from event data)
    example_events_min40 = [
        {'minute': 39, 'team': 'Germany', 'event_type': 'Shot', 'detail': 'Saved', 'player': 'Musiala'},
        {'minute': 38, 'team': 'Scotland', 'event_type': 'Foul', 'detail': 'Free kick won', 'player': 'McTominay'},
        {'minute': 37, 'team': 'Germany', 'event_type': 'Pass', 'detail': 'Key pass', 'player': 'Kroos'},
        {'minute': 36, 'team': 'Germany', 'event_type': 'Carry', 'detail': 'Dribble', 'player': 'Sane'},
    ]
    
    example_events_min80 = [
        {'minute': 79, 'team': 'Germany', 'event_type': 'Substitution', 'detail': 'On', 'player': 'Fullkrug'},
        {'minute': 78, 'team': 'Scotland', 'event_type': 'Shot', 'detail': 'Off Target', 'player': 'Adams'},
        {'minute': 77, 'team': 'Scotland', 'event_type': 'Corner', 'detail': '', 'player': ''},
    ]
    
    if not agent.client:
        print("\n[INFO] No API key - showing data preparation only")
        
        # Show what data the agent would receive
        result = agent.explore(
            match_id=3930158,
            minute=40,
            period=1,
            score_home=3,
            score_away=0,
            recent_events=example_events_min40
        )
        
        print("\n[DATA] Raw data prepared for agent (including events):")
        import json
        
        # Show just the key parts
        raw = result.get('raw_data', {})
        print("\n--- RECENT EVENTS ---")
        for evt in raw.get('recent_events', []):
            print(f"  {evt['minute']}' - {evt['team']}: {evt['event_type']} ({evt.get('detail', '')})")
        
        print("\n--- CURRENT MOMENTUM ---")
        mom = raw.get('current_momentum', {})
        print(f"  Germany: {mom.get('home_momentum', 0):.2f} (change: {mom.get('home_change', 0):+.2f})")
        print(f"  Scotland: {mom.get('away_momentum', 0):.2f} (change: {mom.get('away_change', 0):+.2f})")
        
        print("\n--- DERIVED INSIGHTS ---")
        derived = raw.get('derived', {})
        print(f"  Home trajectory: {derived.get('home_trajectory', 'unknown')}")
        print(f"  Away trajectory: {derived.get('away_trajectory', 'unknown')}")
        print(f"  Gap trend: {derived.get('gap_trend', 'unknown')}")
        
    else:
        # Full test with API
        test_cases = [
            {
                'match_id': 3930158, 'minute': 40, 'period': 1, 
                'score_home': 3, 'score_away': 0,
                'recent_events': example_events_min40
            },
            {
                'match_id': 3930158, 'minute': 80, 'period': 2, 
                'score_home': 5, 'score_away': 1,
                'recent_events': example_events_min80
            },
        ]
        
        for case in test_cases:
            print(f"\n{'='*70}")
            print(f"Minute {case['minute']}' - Score: {case['score_home']}-{case['score_away']}")
            print(f"Recent events: {len(case.get('recent_events', []))}")
            print("=" * 70)
            
            result = agent.explore(**case)
            
            print(f"Interesting: {result.get('interesting')}")
            print(f"Pattern: {result.get('pattern')}")
            print(f"Insight: {result.get('insight')}")
            print(f"Phrase: {result.get('phrase')}")
            print(f"Confidence: {result.get('confidence')}")
    
    print("\n" + "=" * 70)
    print("REMINDER: This phrase is for GENERAL commentary only!")
    print("It should be ADDED to the commentary, not replace it.")
    print("=" * 70)
    print("\n[OK] Test completed!")

