"""
GPT-Based Football Commentary Generator - V6
ENHANCED VARIETY VERSION with:
- All V5 features (Momentum Agent, Penalties, Shootouts, Multi-events)
- NEW: More variety in commentary (higher temperature, varied phrasing)
- NEW: Lower agent threshold (0.70) for more momentum insights
- NEW: Clearer momentum vs momentum change distinction
- NEW: Event sequence detection (Corner→Shot, Shot→Corner, Dribble→Shot, Free Kick→Goal)

Author: Euro 2024 Momentum Project
Date: December 2024
"""

import os
import sys
import json
import time
from typing import Dict, List, Optional, Any
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to import from config, with fallbacks
try:
    from config import (
        OPENAI_API_KEY, MODEL_NAME, TOP_P,
        DELAY_BETWEEN_REQUESTS, SEED
    )
    # V6: Override temperature and max_tokens
    TEMPERATURE = 0.75  # V6: Higher for more variety (was 0.7)
    MAX_TOKENS = 45     # V6: Slightly longer (was 40)
except Exception as e:
    print(f"[WARN] Could not load config: {e}")
    # Fallback values
    import os
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    MODEL_NAME = "gpt-4o-mini"
    TEMPERATURE = 0.75  # V6: Higher for more variety
    MAX_TOKENS = 45     # V6: Slightly longer
    TOP_P = 0.9
    DELAY_BETWEEN_REQUESTS = 1.0
    SEED = 42

try:
    from openai import OpenAI
except ImportError:
    print("Please install openai: pip install openai")
    sys.exit(1)

# Import momentum agent (optional - graceful fallback if not available)
try:
    momentum_agent_path = Path(__file__).parent.parent.parent / "12_momentum_agent" / "scripts"
    sys.path.insert(0, str(momentum_agent_path))
    from exploratory_momentum_agent import ExploratoryMomentumAgent
    MOMENTUM_AGENT_AVAILABLE = True
except ImportError:
    MOMENTUM_AGENT_AVAILABLE = False
    print("[INFO] Momentum agent not available - General commentary without momentum")


# =====================================
# REAL ESPN COMMENTARY - FEW-SHOT EXAMPLES
# V3 BASE (100% same) + V4 PENALTY ADDITIONS ONLY
# =====================================
ESPN_FEW_SHOT_EXAMPLES = """
Below are REAL examples from ESPN live commentary during Euro 2024.

KICK OFF:
- [Kick Off] The Final is underway! Spain versus England, both teams eager to claim glory.
- [Kick Off] First Half begins. Euro 2024 Final!
- [Kick Off] The second half is underway.

GOALS:
- [Goal] Goal! Spain 1, England 0. Nico Williams left footed shot from the left side of the box.
- [Goal] Goal! Spain 1, England 1. Cole Palmer left footed shot from outside the box. Assisted by Jude Bellingham.

SHOTS (single):
- [Shot Blocked] Attempt blocked. Declan Rice right footed shot from outside the box.
- [Shot Saved] Attempt saved. Fabián Ruiz right footed shot from the right side of the box.
- [Shot Missed] Attempt missed. Álvaro Morata right footed shot from the centre of the box goes wide.

SHOTS (multiple - you decide the wording):
- Multiple shots in same minute: mention count, outcomes, key players
- Same team = pressure scenario
- Different teams = end-to-end scenario

CORNERS (single):
- [Corner] Corner, Spain. Conceded by John Stones.

CORNERS (multiple - you decide the wording):
- Multiple corners: mention count, which team(s)
- Same team = sustained pressure
- Different teams = open game

FOULS (single):
- [Foul] Foul by Rodri (Spain) on Jude Bellingham (England).
- [Yellow Card] Harry Kane (England) is shown the yellow card for a bad foul.

FOULS (multiple - you decide the wording):
- Multiple fouls: mention count, context
- You decide: "busy referee", "scrappy", "physical battle", etc.

SUBSTITUTIONS (single):
- [Substitution] Substitution, England. Ollie Watkins replaces Harry Kane.

SUBSTITUTIONS (multiple - you decide the wording):
- 2 same team: double change
- 3 same team: triple change
- Different teams: mention both

OFFSIDES (you decide the wording):
- Single: [Offside] Yamal caught offside.
- Multiple same team: timing issues
- Multiple different teams: end-to-end, wide-to-wide play

GENERAL PLAY:
- First general: [General] Spain in control with 65% possession.
- Consecutive: Add domination streak context (2, 3, 4 minutes...)

OWN GOALS (player scores in HIS OWN net, OTHER team benefits):
- [Own Goal] Own goal! An unfortunate deflection off Mert Müldür gives the Netherlands the lead. Netherlands 2, Turkey 1.
- [Own Goal] Disaster for Austria! Wöber's attempted clearance ends up in his own net, giving France the lead.
- [Own Goal] Germany benefits from an own goal! A Scottish defender's clearance goes into his own net. Germany 4, Scotland 1.

PENALTIES (Period 1-4 - during match) [V4 EXTENSION]:
- [Penalty Awarded] Penalty to Spain! Morata brought down in the box by Walker.
- [Penalty Goal] Goal! Spain 1, England 0. Morata converts from the spot.
- [Penalty Saved] Saved! Pickford denies Morata from the penalty spot!
- [Penalty Missed] Off the post! Bruno Fernandes hits the woodwork from the spot.

PENALTY SHOOTOUT (Period 5) [V4 EXTENSION]:
- [Penalty 1] Dembélé (France) scores! France 1-0 Portugal in the shootout.
- [Penalty 2] Ronaldo (Portugal) - Goal! Shootout tied 1-1.
- [Penalty 5] João Félix (Portugal) - Hits the post! France leads 3-2.
- [Penalty 6] Theo Hernández (France) - Saved by Diogo Costa! Portugal survives.

⛔ WRONG EXAMPLES - NEVER DO THIS:
- ❌ "Shot saved! Germany with 4 corners so far." (corner count NOT provided)
- ❌ "Spain piling on pressure with 8 shots in this half." (shot count NOT provided)
- ❌ "Third corner in quick succession for England." (sequence count NOT provided)
- ❌ "Attempt blocked! Heavy pressure with four corners." (invented statistic)

✅ CORRECT EXAMPLES - DO THIS:
- ✅ "Shot saved! Havertz denied by Schmeichel from close range."
- ✅ "Attempt blocked! Depay's left-footed shot stopped by Akaydin."
- ✅ "Corner for Spain. Delivered by Nico Williams, conceded by Stones."

RULES:
1. For KICK OFF at minute 0: Include the stage (Final, Semi-Final, etc.)
2. For FOULS: Use "by X on Y" format when you have both players
3. Provide counts when multiple events happen
4. You have FREEDOM to choose exact wording - be creative but professional
5. For PENALTIES: Always mention the outcome (Goal, Saved, Missed/Post)
6. For PENALTY SHOOTOUT: Use "Penalty #" format and shootout score
7. NEVER use emojis
"""


class GPTCommentatorV6:
    """
    Football commentary generator with momentum agent integration.
    
    V6 Features:
    - More variety in phrasing (higher temperature)
    - Lower momentum threshold (0.70)
    - Clearer momentum vs momentum change
    - Event sequence detection
    - All V5 features (momentum agent, penalties, shootouts)
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        model: str = None,
        agent_model: str = "gpt-4o",  # Better model for agent reasoning
        enable_momentum: bool = True
    ):
        self.api_key = api_key or OPENAI_API_KEY
        self.model = model or MODEL_NAME  # gpt-4o-mini for commentary
        self.agent_model = agent_model    # gpt-4o for momentum agent
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.client = OpenAI(api_key=self.api_key)
        self.system_prompt = self._create_system_prompt()
        self.last_request_time = 0
        
        # Initialize momentum agent if available and enabled
        self.momentum_agent = None
        if enable_momentum and MOMENTUM_AGENT_AVAILABLE:
            try:
                self.momentum_agent = ExploratoryMomentumAgent(
                    api_key=self.api_key,
                    model=self.agent_model,  # Use GPT-4o for agent
                    verbose=False
                )
                print(f"[OK] Momentum agent initialized with {self.agent_model}")
            except Exception as e:
                print(f"[WARN] Momentum agent initialization failed: {e}")
                self.momentum_agent = None
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt defining the commentator style.
        
        V6: Added variety instructions.
        """
        return """You are an ESPN live football commentator.

YOUR STYLE:
- Professional, factual, concise
- 5-15 words per commentary (max 25 for complex situations)
- Include player name and team when relevant
- Match the tone to what's happening
- VARY your sentence structure - don't repeat same patterns
- Use different phrasings for similar events
- NEVER use emojis. Text only.
- ONLY ONE COMMENTARY per response - do NOT generate multiple lines

OUTPUT: Start with [EVENT_TYPE] then your commentary.

HANDLING MULTIPLE EVENTS:
When multiple events happen in same minute, I'll provide counts and context.
YOU decide the exact wording - be creative but professional.

IMPORTANT: The "play_patterns" data shows how events started (e.g., "From Corner(6)" means 6 events started from a corner situation) - this is NOT the number of corners! Only use corner counts if explicitly provided.

Examples of what you might say:
- "3 shots on goal, Spain piling on the pressure"
- "Busy minute for the referee, 4 fouls"
- "End to end stuff, both teams caught offside"
- "Triple change for England"
- "Scrappy play in midfield"

GENERAL EVENTS - VARIETY IS KEY:
You receive: possession stats, most active player, momentum data, domination info.
- VARY your commentary - don't repeat same elements every minute!
- Pick ONE or TWO interesting things to mention, not all
- If DOMINATION info says "X controlling for Y minutes" → mention it! (e.g., "Switzerland dominating midfield for the last 2 minutes")
- Rotate focus: possession → hot player → area → domination → momentum

CRITICAL - ONLY USE PROVIDED DATA:
You may ONLY mention statistics that are EXPLICITLY provided in the prompt below.
If a statistic is not listed, DO NOT mention it or make up numbers.

ALLOWED to mention (only if provided):
- Player names, team names
- Event outcomes (saved, blocked, missed, goal)
- Body part (left foot, right foot, header)
- Location (center of box, edge of box, etc.)
- Possession % (if provided in GENERAL events)
- Domination minutes (if provided: "controlling for X minutes")
- Multiple event counts (if provided: "3 shots in this minute")

FORBIDDEN (never mention unless explicitly provided):
- Corner counts ("X corners so far")
- Shot totals ("Y shots this half")
- Attempt sequences ("third corner in succession")
- Match statistics not in prompt

Example WRONG: "Shot saved! Germany applying heavy pressure with four corners."
Example RIGHT: "Shot saved! Havertz denied by Schmeichel from close range."

PENALTY HANDLING:
- Period 1-4: Use [Penalty Awarded], [Penalty Goal], [Penalty Saved], [Penalty Missed]
- Period 5 (Shootout): Use [Penalty #] format with shootout score

RULES:
1. KICK OFF minute 0: Include stage AND add excitement (e.g., "both teams eager to claim glory")
2. FOULS: Use "by X on Y" format
3. MULTIPLE EVENTS: Mention count, you choose the description
4. PENALTIES: Always include outcome and players involved
5. SHOOTOUT: Use penalty number and running shootout score
6. Be CREATIVE with wording - don't be robotic
7. NEVER use emojis"""
    
    def _get_game_phase(self, minute: int, period: int = None) -> str:
        """Determine the game phase based on minute AND period."""
        if period == 1:
            if minute == 0:
                return "First Half - Kick-off"
            elif minute < 45:
                return "First Half"
            elif minute == 45:
                return "First Half"
            else:
                stoppage = minute - 45
                return f"First Half Stoppage time (45+{stoppage}')"
        
        elif period == 2:
            if minute == 45:
                return "Second Half - Kick-off"
            elif minute < 90:
                return "Second Half"
            elif minute == 90:
                return "Second Half"
            else:
                stoppage = minute - 90
                return f"Second Half Stoppage time (90+{stoppage}')"
        
        elif period == 3:
            if minute <= 91:
                return "Extra Time First Half - Kick-off"
            elif minute <= 105:
                return "Extra Time - First Half"
            else:
                stoppage = minute - 105
                return f"Extra Time First Half Stoppage time (105+{stoppage}')"
        
        elif period == 4:
            if minute <= 106:
                return "Extra Time Second Half - Kick-off"
            elif minute <= 120:
                return "Extra Time - Second Half"
            else:
                stoppage = minute - 120
                return f"Extra Time Second Half Stoppage time (120+{stoppage}')"
        
        elif period == 5:
            return "Penalty Shootout"
        
        else:
            if minute <= 45:
                return "First Half"
            elif minute <= 90:
                return "Second Half"
            else:
                return "Extra Time"
    
    def _calculate_correct_score(
        self,
        detected_type: str,
        event_data: Dict,
        home_score: int,
        away_score: int,
        home_team: str,
        away_team: str
    ) -> tuple:
        """
        Calculate the correct score for the commentary.
        
        FIX V5.1: Score is now calculated from goal counting (build_running_score).
        The running score ALREADY includes goals as they happen.
        No adjustment needed - just return the score as-is.
        
        For Period 5 (shootout): shootout_score is tracked separately.
        """
        # Score is already correctly calculated from goal counting
        # No need to adjust
        return (home_score, away_score)
    
    def _get_momentum_context(
        self,
        match_id: int,
        minute: int,
        period: int,
        home_score: int,
        away_score: int,
        home_team: str,
        away_team: str,
        recent_events: List[Dict] = None
    ) -> Optional[Dict]:
        """
        Get momentum context from the agent.
        
        Only called for General commentary.
        Returns None if agent not available or not interesting.
        """
        if not self.momentum_agent:
            return None
        
        try:
            result = self.momentum_agent.explore(
                match_id=match_id,
                minute=minute,
                period=period,
                score_home=home_score,
                score_away=away_score,
                home_team=home_team,
                away_team=away_team,
                recent_events=recent_events,
                history_lookback=10
            )
            
            if result.get('interesting'):
                return result
            return None
            
        except Exception as e:
            print(f"[WARN] Momentum agent error: {e}")
            return None
    
    def _create_minute_prompt(
        self, 
        minute: int,
        events_data: List[Dict],
        rule_based_commentary: str,
        sequence_commentary: str,
        match_context: Dict
    ) -> str:
        """Create the prompt for generating commentary."""
        period = match_context.get('period', 1)
        game_phase = self._get_game_phase(minute, period)
        
        detected_type = match_context.get('detected_type', 'General')
        event_data = match_context.get('event_data', {})
        
        home_team = match_context.get('home_team', 'Home')
        away_team = match_context.get('away_team', 'Away')
        home_score = match_context.get('home_score', 0)
        away_score = match_context.get('away_score', 0)
        stage = match_context.get('stage', 'Match')
        
        # V5 FIX: Calculate correct score for Goals
        display_home_score, display_away_score = self._calculate_correct_score(
            detected_type, event_data, home_score, away_score, home_team, away_team
        )
        
        # Build event-specific data section (score is now in compact header)
        event_details = self._format_event_data(detected_type, event_data, match_context)
        
        # V3: Multiple events context
        multi_context = self._format_multi_events_context(match_context)
        
        # V6: Domination context for General events - MUST MENTION when present
        domination_context = ""
        if detected_type == 'General':
            domination_info = match_context.get('domination_info', {})
            consecutive_generals = match_context.get('consecutive_generals', 1)
            
            if consecutive_generals == 1:
                domination_context = "\n(First general - vary what you mention)"
            elif consecutive_generals >= 2:
                if domination_info.get('has_domination'):
                    dom_team = domination_info.get('team', '')
                    dom_streak = domination_info.get('streak', 0)
                    domination_context = f"""
⚠️ DOMINATION - MUST MENTION:
  {dom_team} controlling for {dom_streak} straight minutes!
  Example: "{dom_team} in control, dominating midfield for the last {dom_streak} minutes.\""""
                else:
                    domination_context = f"\n(General #{consecutive_generals} - vary your focus)"
        
        # V6.1: Event chain context (DIRECT chains only - action started within 7 events)
        chain_section = ""
        event_chain = match_context.get('event_chain', {})
        if event_chain.get('has_chain'):
            chain_lines = []
            chain_lines.append("(DIRECT chain - action started within last 7 events)")
            
            # Origin with pattern-specific instructions
            origin = event_chain.get('origin', '')
            if origin:
                chain_lines.append(f"Origin: {origin}")
                
                # Add usage instructions based on origin type
                if 'Corner (direct)' in origin:
                    # Direct = header or shot directly from corner delivery (0-1 passes)
                    chain_lines.append("→ DIRECT goal from corner delivery")
                    chain_lines.append("→ USE: 'from the corner', 'header from the delivery', 'heads in from the corner'")
                    chain_lines.append("⛔ NO corner counts ('X corners so far' is FORBIDDEN)")
                elif 'Corner (indirect)' in origin:
                    # Indirect = several passes after corner, mention subtly
                    chain_lines.append("→ Goal built up from corner (several passes in between)")
                    chain_lines.append("→ USE: 'The play started from a corner', 'Following the corner, they work it to...'")
                    chain_lines.append("→ Focus on the goal itself, corner is background context")
                    chain_lines.append("⛔ NO 'from the corner' (not direct), NO corner counts")
                elif 'Free Kick (direct)' in origin:
                    # Direct = shot directly from free kick
                    chain_lines.append("→ DIRECT goal from free kick")
                    chain_lines.append("→ USE: 'from the free kick', 'curls it in from the set piece'")
                    chain_lines.append("⛔ NO free kick counts")
                elif 'Free Kick (indirect)' in origin:
                    # Indirect = several passes after free kick, mention subtly
                    chain_lines.append("→ Goal built up from free kick (several passes in between)")
                    chain_lines.append("→ USE: 'The play originated from a free kick', 'Following the set piece...'")
                    chain_lines.append("→ Focus on the goal itself, free kick is background context")
                    chain_lines.append("⛔ NO 'from the free kick' (not direct), NO counts")
                elif 'Dribble' in origin:
                    chain_lines.append("→ USE: 'beats his man', 'after the run', 'dribbles past'")
                elif 'Blocked' in origin or 'Saved' in origin:
                    chain_lines.append("→ USE: 'second chance', 'follows up'")
            
            # Related events (Assist, Blocked By, etc.)
            for related in event_chain.get('related_events', []):
                rel_type = related.get('type', '')
                if rel_type == 'Assist':
                    chain_lines.append(f"Assisted by: {related.get('player', '')}")
                elif rel_type == 'Blocked By':
                    chain_lines.append(f"Blocked by: {related.get('player', '')}")
                elif rel_type in ['Yellow Card', 'Red Card']:
                    chain_lines.append(f"{rel_type} shown to: {related.get('player', '')}")
            
            if chain_lines:
                chain_section = "\n\nCHAIN:\n" + "\n".join(f"- {line}" for line in chain_lines)
        
        # V6: Event sequence removed - now handled by chain detection above
        sequence_section = ""
        
        # V6 UPDATED: Momentum context for General events ONLY
        # Agent selects data, LLM decides how to use it
        # V6: Lower threshold (0.70) and clearer momentum type
        momentum_context = ""
        momentum_data = match_context.get('momentum_context')
        if detected_type == 'General' and momentum_data and momentum_data.get('interesting'):
            forward_data = momentum_data.get('forward_data', [])
            reason = momentum_data.get('reason', '')
            confidence = momentum_data.get('confidence', 0.5)
            
            # V6: Threshold lowered to 0.70 (was 0.75)
            if confidence >= 0.70 and forward_data:
                # V6: Determine if it's about change or absolute value
                is_change = any('change' in str(d).lower() or 'shift' in str(d).lower() or 'swing' in str(d).lower() for d in forward_data)
                
                if is_change:
                    momentum_label = "⚡ MOMENTUM CHANGE"
                    momentum_instruction = "USE: 'gaining momentum', 'momentum shifting', 'building pressure'"
                else:
                    momentum_label = "📊 MOMENTUM STATE"
                    momentum_instruction = "USE: 'in control', 'dominating', 'on top'"
                
                # Format the selected data points
                data_lines = '\n'.join([f"- {d}" for d in forward_data])
                note_line = f"\nAgent note: {reason}" if reason else ""
                momentum_context = f"""

{momentum_label}:
{data_lines}{note_line}
→ {momentum_instruction}"""
        
        # V4: Penalty shootout context
        shootout_context = ""
        if period == 5:
            shootout_score = event_data.get('shootout_score', {})
            penalty_num = event_data.get('penalty_number', '')
            shootout_context = f"""
PENALTY SHOOTOUT:
- Penalty #{penalty_num}
- Shootout Score: {home_team} {shootout_score.get('home', 0)} - {shootout_score.get('away', 0)} {away_team}
- Use format: [Penalty {penalty_num}] Player (Team) - outcome. Shootout score.
"""
        
        # V6 FORMAT: Added sequence_section
        prompt = f"""Match: {home_team} {display_home_score} - {display_away_score} {away_team} ({stage})
Minute: {minute}' ({game_phase})

EVENT: {detected_type}
{event_details}{chain_section}{sequence_section}{multi_context}{domination_context}{momentum_context}{shootout_context}

Generate ESPN-style commentary. You decide the exact wording."""
        
        return prompt
    
    def _format_event_data(self, detected_type: str, event_data: Dict, match_context: Dict) -> str:
        """Format event-specific data for the prompt. V3 FORMAT."""
        lines = []  # V3: No header
        
        home_team = match_context.get('home_team', 'Home')
        away_team = match_context.get('away_team', 'Away')
        stage = match_context.get('stage', '')
        period = match_context.get('period', 1)
        player = event_data.get('player', '')
        team = event_data.get('team', '')
        location = event_data.get('location', '')
        
        if detected_type == 'Goal':
            scorer = event_data.get('scorer', player)
            body_part = event_data.get('body_part', '')
            assisted_by = event_data.get('assisted_by', '')
            
            lines.append(f"Scorer: {scorer} ({team})")
            if body_part:
                lines.append(f"Body part: {body_part}")
            if location:
                lines.append(f"Location: {location}")
            if assisted_by:
                lines.append(f"Assisted by: {assisted_by}")
            # V3: Explicit score emphasis
            home_score = match_context.get('home_score', 0)
            away_score = match_context.get('away_score', 0)
            lines.append(f"SCORE AFTER GOAL: {home_team} {home_score}, {away_team} {away_score}")
            lines.append(f"(USE EXACTLY: {home_team} {home_score}, {away_team} {away_score} - DO NOT CHANGE)")
        
        elif detected_type == 'Penalty Goal':
            lines.append(f"Scorer: {event_data.get('player', '')} ({event_data.get('team', '')})")
            lines.append(f"Type: PENALTY - converted from the spot")
            if event_data.get('goalkeeper'):
                lines.append(f"Goalkeeper beaten: {event_data.get('goalkeeper', '')}")
        
        elif detected_type == 'Penalty Saved':
            lines.append(f"Taker: {event_data.get('player', '')} ({event_data.get('team', '')})")
            lines.append(f"SAVED by: {event_data.get('goalkeeper', '')} ({event_data.get('goalkeeper_team', '')})")
        
        elif detected_type == 'Penalty Missed':
            lines.append(f"Taker: {event_data.get('player', '')} ({event_data.get('team', '')})")
            lines.append(f"Outcome: {event_data.get('outcome', 'Missed')} (Post/Wide)")
        
        elif detected_type == 'Penalty Awarded':
            lines.append(f"Awarded to: {event_data.get('team', '')}")
            if event_data.get('fouled_player'):
                lines.append(f"Player fouled: {event_data.get('fouled_player', '')}")
            if event_data.get('fouler'):
                lines.append(f"Foul by: {event_data.get('fouler', '')} ({event_data.get('fouler_team', '')})")
            if event_data.get('location'):
                lines.append(f"Location: in the penalty area")
        
        elif detected_type == 'Own Goal':
            # V6.2.1 FIX: Correct data + creative freedom
            scorer = event_data.get('scorer', event_data.get('player', ''))
            scorer_team = event_data.get('scoring_team', event_data.get('team', ''))
            # The OTHER team benefits from the own goal
            benefiting_team = away_team if scorer_team == home_team else home_team
            home_score = match_context.get('home_score', 0)
            away_score = match_context.get('away_score', 0)
            
            # Provide correct facts
            lines.append(f"OWN GOAL by: {scorer} ({scorer_team}) → {benefiting_team} benefits")
            lines.append(f"Score now: {home_team} {home_score}, {away_team} {away_score}")
            
            # Creative style options - LLM picks
            lines.append("STYLE OPTIONS (pick one):")
            lines.append(f"- Dramatic: 'Disaster for {scorer_team}! {scorer}'s deflection hands {benefiting_team} the lead'")
            lines.append(f"- Neutral: 'Own goal by {scorer} gives {benefiting_team} a goal'")
            lines.append(f"- Sympathetic: 'Unfortunate for {scorer}, own goal puts {benefiting_team} ahead'")
        
        elif detected_type.startswith('Penalty') and period == 5:
            # Penalty shootout
            penalty_num = event_data.get('penalty_number', '')
            lines.append(f"PENALTY #{penalty_num} in shootout")
            lines.append(f"Taker: {event_data.get('player', '')} ({event_data.get('team', '')})")
            lines.append(f"Outcome: {event_data.get('outcome', '')}")
            if event_data.get('goalkeeper'):
                lines.append(f"Goalkeeper: {event_data.get('goalkeeper', '')}")
            shootout = event_data.get('shootout_score', {})
            lines.append(f"Shootout score after: {home_team} {shootout.get('home', 0)} - {shootout.get('away', 0)} {away_team}")
        
        elif 'Shot' in detected_type:
            outcome = event_data.get('outcome', '')
            body_part = event_data.get('body_part', '')
            saved_by = event_data.get('saved_by', '')
            blocked_by = event_data.get('blocked_by', '')
            xg = event_data.get('xg', '')
            
            lines.append(f"Player: {player} ({team})")
            if outcome:
                lines.append(f"Outcome: {outcome}")
            if body_part:
                lines.append(f"Body part: {body_part}")
            if location:
                lines.append(f"Location: {location}")
            if xg:
                lines.append(f"xG: {xg}")
            if saved_by:
                lines.append(f"Saved by: {saved_by}")
            if blocked_by:
                lines.append(f"Blocked by: {blocked_by}")
        
        elif detected_type == 'Corner':
            delivered_by = event_data.get('delivered_by', player)
            conceded_by = event_data.get('conceded_by', '')
            
            lines.append(f"Team: {team}")
            if delivered_by:
                lines.append(f"Delivered by: {delivered_by}")
            if conceded_by:
                lines.append(f"Conceded by: {conceded_by}")
            # V3: Clarify single corner
            lines.append(f"(This is ONE corner kick - do not mention multiple corners unless MULTIPLE CORNERS section is provided)")
        
        elif detected_type == 'Free Kick':
            # V3 uses foul_committed_by for Free Kick events
            fouled_player = event_data.get('fouled_player', player)
            fouled_team = event_data.get('fouled_team', team)
            foul_committed_by = event_data.get('foul_committed_by', '')
            foul_committed_team = event_data.get('foul_committed_team', '')
            
            lines.append(f"Player fouled: {fouled_player} ({fouled_team})")
            if foul_committed_by:
                lines.append(f"Foul by: {foul_committed_by} ({foul_committed_team})")
            if location:
                lines.append(f"Location: {location}")
        
        elif detected_type == 'Foul':
            # V3 uses committed_by for Foul events
            committed_by = event_data.get('committed_by', '')
            committed_team = event_data.get('committed_team', '')
            fouled_player = event_data.get('fouled_player', '')
            fouled_team = event_data.get('fouled_team', '')
            
            if committed_by:
                lines.append(f"Foul by: {committed_by} ({committed_team})")
            if fouled_player:
                lines.append(f"On: {fouled_player} ({fouled_team})")
            if location:
                lines.append(f"Location: {location}")
        
        elif detected_type in ['Yellow Card', 'Red Card']:
            # V3 FORMAT: Card type + Player
            carded_player = event_data.get('carded_player', player)
            carded_team = event_data.get('carded_team', team)
            fouled_player = event_data.get('fouled_player', '')
            fouled_team = event_data.get('fouled_team', '')
            
            lines.append(f"Card: {detected_type}")
            lines.append(f"Player: {carded_player} ({carded_team})")
            if fouled_player:
                lines.append(f"For foul on: {fouled_player} ({fouled_team})")
        
        elif detected_type == 'Substitution':
            player_off = event_data.get('player_off', '')
            sub_info = event_data.get('substitution_info', '')
            
            lines.append(f"Team: {team}")
            if player_off:
                lines.append(f"Off: {player_off}")
            if sub_info:
                lines.append(f"Info: {sub_info}")
        
        elif detected_type == 'Kick Off':
            phase = event_data.get('phase', 'Match begins')
            
            lines.append(f"Phase: {phase}")
            if period == 1 and stage:
                lines.append(f"STAGE: {stage} (MUST MENTION IN COMMENTARY)")
            elif period == 5:
                lines.append(f"PENALTY SHOOTOUT BEGINS")
        
        elif detected_type == 'Injury':
            injured_player = event_data.get('injured_player', player)
            injured_team = event_data.get('injured_team', team)
            
            lines.append(f"Injured: {injured_player} ({injured_team})")
        
        elif detected_type == 'Offside':
            # V3: Specific Offside formatting
            offside_player = event_data.get('offside_player', player)
            offside_team = event_data.get('offside_team', team)
            
            lines.append(f"Player: {offside_player} ({offside_team})")
        
        elif detected_type == 'General':
            # V3 FORMAT: Control combined with area, possession with area suffix
            control = match_context.get('control', '')
            possession_stats = match_context.get('possession_stats', {})
            area = match_context.get('area', '')
            most_active = match_context.get('most_active_player', {})
            
            if control:
                # V3: Combine control with area in same line
                if area:
                    lines.append(f"Control: {control} in {area}")
                else:
                    lines.append(f"Control: {control}")
            if possession_stats:
                poss_str = ', '.join([f"{k}: {v}%" for k, v in possession_stats.items()])
                # V3: Add area context to possession
                if area:
                    lines.append(f"Possession: {poss_str} (mostly in {area})")
                else:
                    lines.append(f"Possession: {poss_str}")
            # V3: Most active player - V6.2 FIX: Include team name to prevent mismatch
            if most_active and most_active.get('player'):
                team_name = most_active.get('team', '')
                if team_name:
                    lines.append(f"Most active: {most_active['player']} ({team_name}) ({most_active.get('count', 0)} events)")
                else:
                    lines.append(f"Most active: {most_active['player']} ({most_active.get('count', 0)} events)")
        
        else:
            # V3: Default for unknown types
            if player:
                lines.append(f"Player: {player} ({team})")
            if location:
                lines.append(f"Location: {location}")
        
        # V3: Add dash prefix at return, with fallback
        return '\n'.join(f"- {line}" for line in lines) if lines else "- General play"
    
    def _rate_limit(self):
        """Apply rate limiting between requests. V3 method."""
        elapsed = time.time() - self.last_request_time
        if elapsed < DELAY_BETWEEN_REQUESTS:
            time.sleep(DELAY_BETWEEN_REQUESTS - elapsed)
        self.last_request_time = time.time()
    
    def _format_multi_events_context(self, match_context: Dict) -> str:
        """Format context for multiple events in same minute. V3 FORMAT."""
        lines = []
        
        # Multiple shots - V3 full format
        multi_shots = match_context.get('multi_shots_info', {})
        if multi_shots.get('has_multiple'):
            count = multi_shots.get('count', 0)
            scenario = multi_shots.get('scenario', '')
            teams = multi_shots.get('team_counts', {})
            shots_list = multi_shots.get('shots_list', [])
            most_dangerous = multi_shots.get('most_dangerous', {})
            
            lines.append(f"\nMULTIPLE SHOTS ({count} total):")
            lines.append(f"  Scenario: {scenario.upper()}")
            lines.append(f"  Teams: {teams}")
            for i, shot in enumerate(shots_list, 1):
                lines.append(f"  Shot {i}: {shot.get('player', '')} ({shot.get('team', '')}) - {shot.get('outcome', '')}")
            if most_dangerous:
                lines.append(f"  MOST DANGEROUS: {most_dangerous.get('player', '')} - xG: {most_dangerous.get('xg', 'N/A')}, Distance: {most_dangerous.get('distance', 'N/A')}m")
        
        # Multiple corners - V3 format
        multi_corners = match_context.get('multi_corners_info', {})
        if multi_corners.get('has_multiple'):
            count = multi_corners.get('count', 0)
            scenario = multi_corners.get('scenario', '')
            teams = multi_corners.get('team_counts', {})
            lines.append(f"\nMULTIPLE CORNERS ({count} total):")
            lines.append(f"  Scenario: {scenario.upper()}")
            lines.append(f"  Teams: {teams}")
        
        # Multiple fouls - V3 format
        multi_fouls = match_context.get('multi_fouls_info', {})
        if multi_fouls.get('has_multiple'):
            count = multi_fouls.get('count', 0)
            lines.append(f"\nMULTIPLE FOULS ({count} total):")
            lines.append(f"  (You decide: scrappy, physical, busy referee, etc.)")
        
        # Multiple substitutions - V3 format with Double/Triple
        # FIX ISSUE 2: Show both players OFF and players ON
        # FIX: Filter by current_sub_team to generate SEPARATE commentary per team
        multi_subs = match_context.get('multi_subs_info', {})
        current_sub_team = match_context.get('current_sub_team')  # Which team's subs to show
        
        if multi_subs.get('has_multiple'):
            team_counts = multi_subs.get('team_counts', {})
            for team, count in team_counts.items():
                # Only show this team's subs if current_sub_team is set
                if current_sub_team and team != current_sub_team:
                    continue
                    
                if count >= 2:
                    sub_type = "Triple" if count >= 3 else "Double"
                    players_off = multi_subs.get('players_off_by_team', multi_subs.get('players_by_team', {})).get(team, [])
                    players_on = multi_subs.get('players_on_by_team', {}).get(team, [])
                    lines.append(f"\n{sub_type.upper()} SUBSTITUTION ({team}):")
                    lines.append(f"  Players OFF: {', '.join(players_off)}")
                    if players_on:
                        lines.append(f"  Players ON: {', '.join(players_on)}")
        
        # Multiple offsides - V3 format (was missing entirely!)
        multi_offsides = match_context.get('multi_offsides_info', {})
        if multi_offsides.get('has_multiple'):
            count = multi_offsides.get('count', 0)
            scenario = multi_offsides.get('scenario', '')
            teams = multi_offsides.get('team_counts', {})
            lines.append(f"\nMULTIPLE OFFSIDES ({count} total):")
            lines.append(f"  Scenario: {scenario.upper()}")
            lines.append(f"  Teams: {teams}")
            if scenario == 'end_to_end':
                lines.append(f"  (Both teams pushing forward, wide-to-wide play)")
        
        return '\n'.join(lines) if lines else ""
    
    def generate_minute_commentary(
        self,
        minute: int,
        events_data: List[Dict],
        rule_based_commentary: str = "",
        sequence_commentary: str = "",
        match_context: Dict = None,
        temperature: Optional[float] = None,  # V3: temperature parameter
        use_few_shot: bool = True,  # V3: few-shot parameter
        recent_events: List[Dict] = None  # V5: For momentum agent
    ) -> str:
        """
        Generate commentary for a single minute.
        
        V6: Added event sequence support.
        """
        match_context = match_context or {}
        
        # V3: Rate limiting
        self._rate_limit()
        
        # V5: Get momentum context for General events
        detected_type = match_context.get('detected_type', 'General')
        if detected_type == 'General' and self.momentum_agent:
            match_id = match_context.get('match_id', 0)
            period = match_context.get('period', 1)
            home_score = match_context.get('home_score', 0)
            away_score = match_context.get('away_score', 0)
            home_team = match_context.get('home_team', '')
            away_team = match_context.get('away_team', '')
            
            momentum_result = self._get_momentum_context(
                match_id=match_id,
                minute=minute,
                period=period,
                home_score=home_score,
                away_score=away_score,
                home_team=home_team,
                away_team=away_team,
                recent_events=recent_events
            )
            
            if momentum_result:
                match_context['momentum_context'] = momentum_result
        
        # Build prompt
        user_prompt = self._create_minute_prompt(
            minute=minute,
            events_data=events_data,
            rule_based_commentary=rule_based_commentary,
            sequence_commentary=sequence_commentary,
            match_context=match_context
        )
        
        # V3: Proper message structure with separate few-shot turns
        messages = [{"role": "system", "content": self.system_prompt}]
        
        if use_few_shot:
            messages.append({
                "role": "user", 
                "content": "Here are examples of the commentary style I want:\n\n" + ESPN_FEW_SHOT_EXAMPLES
            })
            messages.append({
                "role": "assistant",
                "content": "Understood. I'll generate professional, ESPN-style commentary. I have freedom to choose exact wording while being factual and concise."
            })
        
        messages.append({"role": "user", "content": user_prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or TEMPERATURE,
                max_tokens=MAX_TOKENS,
                top_p=TOP_P,
                seed=SEED
            )
            
            commentary = response.choices[0].message.content.strip()
            
            # V3 FIX: Only take the first line if multiple generated
            lines = [line.strip() for line in commentary.split('\n') if line.strip()]
            if lines:
                commentary = lines[0]
            
            return commentary
            
        except Exception as e:
            print(f"Error generating commentary: {e}")
            return f"[Error generating commentary for minute {minute}]"


if __name__ == "__main__":
    # Test the commentator
    print("=" * 70)
    print("Testing GPT Commentator V6")
    print("=" * 70)
    
    try:
        commentator = GPTCommentatorV6()
        print(f"[OK] Initialized with model: {commentator.model}")
        print(f"[OK] Agent model: {commentator.agent_model}")
        print(f"[OK] Momentum agent: {'Available' if commentator.momentum_agent else 'Not available'}")
        print(f"[OK] Temperature: {TEMPERATURE}")
        print(f"[OK] Max tokens: {MAX_TOKENS}")
        
        # Test 1: Goal with score fix
        print("\n--- Test 1: Goal Score Fix ---")
        test_context = {
            'home_team': 'Germany',
            'away_team': 'Scotland',
            'home_score': 1,
            'away_score': 0,
            'stage': 'Group Stage',
            'period': 1,
            'detected_type': 'Goal',
            'event_data': {
                'scorer': 'Florian Wirtz',
                'team': 'Germany',
                'body_part': 'right foot',
                'location': 'centre of the box',
            }
        }
        
        commentary = commentator.generate_minute_commentary(
            minute=10,
            events_data=[],
            match_context=test_context
        )
        print(f"Goal commentary: {commentary}")
        
        # Test 2: Event sequence (Corner → Shot)
        print("\n--- Test 2: Event Sequence ---")
        test_context_seq = {
            'home_team': 'Spain',
            'away_team': 'England',
            'home_score': 0,
            'away_score': 0,
            'stage': 'Final',
            'period': 1,
            'detected_type': 'Corner',
            'event_data': {
                'team': 'Spain',
                'delivered_by': 'Olmo',
            },
            'event_sequence_info': {
                'has_sequence': True,
                'sequence_text': 'Corner → Shot (Morata, Header Saved)',
                'sequence_type': 'Corner Attack'
            }
        }
        
        commentary = commentator.generate_minute_commentary(
            minute=25,
            events_data=[],
            match_context=test_context_seq
        )
        print(f"Sequence commentary: {commentary}")
        
        print("\n[OK] V6 tests completed!")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

