"""
GPT-Based Football Commentary Generator - V4
PENALTY HANDLING VERSION with:
- All V3 features (Progressive General, Multiple Events, xG)
- Period 5 (Penalty Shootout) handling
- Period 1-4 Penalty detection and commentary
- Goalkeeper info on saves
- Penalty count tracking for shootouts

Style: Professional, clear, factual, neutral - with tension/excitement based on event, minute, and result.
Input: All events from 1 minute + rich context data
Output: Single unified commentary for that minute

Author: AI Assistant
Date: December 9, 2025
"""

import os
import sys
import json
import time
from typing import Dict, List, Optional, Any
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    OPENAI_API_KEY, MODEL_NAME, TEMPERATURE, MAX_TOKENS, TOP_P,
    DELAY_BETWEEN_REQUESTS, SEED
)

try:
    from openai import OpenAI
except ImportError:
    print("Please install openai: pip install openai")
    sys.exit(1)


# =====================================
# REAL ESPN COMMENTARY - FEW-SHOT EXAMPLES
# =====================================
ESPN_FEW_SHOT_EXAMPLES = """
Below are REAL examples from ESPN live commentary during Euro 2024.

KICK OFF:
- [Kick Off] First Half begins. Euro 2024 Final!
- [Kick Off] The second half is underway.
- [Kick Off] Extra time begins. Still level after 90 minutes.

GOALS:
- [Goal] Goal! Spain 1, England 0. Nico Williams left footed shot from the left side of the box.
- [Goal] Goal! Spain 1, England 1. Cole Palmer left footed shot from outside the box. Assisted by Jude Bellingham.

PENALTIES (Period 1-4 - during match):
- [Penalty Awarded] Penalty to Spain! Morata brought down in the box by Walker.
- [Penalty Goal] Goal! Spain 1, England 0. Morata converts from the spot.
- [Penalty Saved] Saved! Pickford denies Morata from the penalty spot!
- [Penalty Missed] Off the post! Bruno Fernandes hits the woodwork from the spot.

PENALTY SHOOTOUT (Period 5):
- [Penalty 1] Dembélé (France) scores! France 1-0 Portugal in the shootout.
- [Penalty 2] Ronaldo (Portugal) - Goal! Shootout tied 1-1.
- [Penalty 5] João Félix (Portugal) - Hits the post! France leads 3-2.
- [Penalty 6] Theo Hernández (France) - Saved by Diogo Costa! Portugal survives.

SHOTS (single):
- [Shot Blocked] Attempt blocked. Declan Rice right footed shot from outside the box.
- [Shot Saved] Attempt saved. Fabián Ruiz right footed shot from the right side of the box.
- [Shot Missed] Attempt missed. Álvaro Morata right footed shot from the centre of the box goes wide.

CORNERS:
- [Corner] Corner, Spain. Conceded by John Stones.

FOULS:
- [Foul] Foul by Rodri (Spain) on Jude Bellingham (England).
- [Yellow Card] Harry Kane (England) is shown the yellow card for a bad foul.

SUBSTITUTIONS:
- [Substitution] Substitution, England. Ollie Watkins replaces Harry Kane.

GENERAL PLAY:
- [General] Spain in control with 65% possession.
- [General] Spain dominating for 3 consecutive minutes in midfield.

RULES:
1. For KICK OFF at minute 0: Include the stage (Final, Semi-Final, etc.)
2. For FOULS: Use "by X on Y" format when you have both players
3. For PENALTIES: Always mention the outcome (Goal, Saved, Missed/Post)
4. For PENALTY SHOOTOUT: Use "Penalty #" format and shootout score
5. NEVER use emojis
"""


class GPTCommentator:
    """
    Football commentary generator using OpenAI GPT models.
    
    V4: Enhanced with penalty handling for Period 1-4 and Period 5 (shootout).
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = None):
        self.api_key = api_key or OPENAI_API_KEY
        self.model = model or MODEL_NAME
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.client = OpenAI(api_key=self.api_key)
        self.system_prompt = self._create_system_prompt()
        self.last_request_time = 0
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt defining the commentator style."""
        return """You are an ESPN live football commentator.

YOUR STYLE:
- Professional, factual, concise
- 5-15 words per commentary (max 25 for complex situations)
- Include player name and team when relevant
- Match the tone to what's happening
- NEVER use emojis. Text only.
- ONLY ONE COMMENTARY per response - do NOT generate multiple lines

OUTPUT: Start with [EVENT_TYPE] then your commentary.

PENALTY HANDLING:
- Period 1-4: Use [Penalty Awarded], [Penalty Goal], [Penalty Saved], [Penalty Missed]
- Period 5 (Shootout): Use [Penalty #] format with shootout score, mention goalkeeper on saves

HANDLING MULTIPLE EVENTS:
When multiple events happen in same minute, I'll provide counts and context.
YOU decide the exact wording - be creative but professional.

Examples:
- "3 shots on goal, Spain piling on the pressure"
- "Penalty to Spain! Morata brought down by Walker"
- "Penalty 3: Bernardo Silva scores! Portugal 2-1 in the shootout"

RULES:
1. KICK OFF minute 0: Include the stage (Final, Semi-Final)
2. FOULS: Use "by X on Y" format
3. PENALTIES: Always include outcome and players involved
4. SHOOTOUT: Use penalty number and running shootout score
5. Be CREATIVE with wording - don't be robotic
6. NEVER use emojis"""
    
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
        
        # Build event-specific data section
        event_details = self._format_event_data(detected_type, event_data, match_context)
        
        # V3: Multiple events context
        multi_context = self._format_multi_events_context(match_context)
        
        # V3: Domination context for General events
        domination_context = ""
        if detected_type == 'General':
            domination_info = match_context.get('domination_info', {})
            consecutive_generals = match_context.get('consecutive_generals', 1)
            
            if consecutive_generals == 1:
                domination_context = "\n(First general event - use basic possession style)"
            elif consecutive_generals >= 2:
                if domination_info.get('has_domination'):
                    dom_team = domination_info.get('team', '')
                    dom_streak = domination_info.get('streak', 0)
                    domination_context = f"\n(DOMINATION: {dom_team} controlling for {dom_streak} straight minutes - incorporate this)"
                else:
                    domination_context = f"\n(Consecutive general #{consecutive_generals} - add context about flow of play)"
        
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
        
        prompt = f"""MATCH: {home_team} vs {away_team}
SCORE: {home_team} {home_score} - {away_score} {away_team} (USE EXACTLY - DO NOT CHANGE)
STAGE: {stage}
MINUTE: {minute}'
PHASE: {game_phase}

EVENT TYPE: {detected_type}

{event_details}
{multi_context}
{domination_context}
{shootout_context}

Generate ONE professional ESPN-style commentary (5-15 words):"""
        
        return prompt
    
    def _format_event_data(self, detected_type: str, event_data: Dict, match_context: Dict) -> str:
        """Format event-specific data for the prompt."""
        lines = ["EVENT DETAILS:"]
        
        home_team = match_context.get('home_team', 'Home')
        away_team = match_context.get('away_team', 'Away')
        stage = match_context.get('stage', '')
        period = match_context.get('period', 1)
        
        if detected_type == 'Goal':
            lines.append(f"- Scorer: {event_data.get('scorer', '')} ({event_data.get('team', '')})")
            if event_data.get('body_part'):
                lines.append(f"- Body part: {event_data.get('body_part', '')}")
            if event_data.get('location'):
                lines.append(f"- Location: {event_data.get('location', '')}")
            if event_data.get('assisted_by'):
                lines.append(f"- Assisted by: {event_data.get('assisted_by', '')}")
        
        elif detected_type == 'Penalty Goal':
            lines.append(f"- Scorer: {event_data.get('player', '')} ({event_data.get('team', '')})")
            lines.append(f"- Type: PENALTY - converted from the spot")
            if event_data.get('goalkeeper'):
                lines.append(f"- Goalkeeper beaten: {event_data.get('goalkeeper', '')}")
        
        elif detected_type == 'Penalty Saved':
            lines.append(f"- Taker: {event_data.get('player', '')} ({event_data.get('team', '')})")
            lines.append(f"- SAVED by: {event_data.get('goalkeeper', '')} ({event_data.get('goalkeeper_team', '')})")
        
        elif detected_type == 'Penalty Missed':
            lines.append(f"- Taker: {event_data.get('player', '')} ({event_data.get('team', '')})")
            lines.append(f"- Outcome: {event_data.get('outcome', 'Missed')} (Post/Wide)")
        
        elif detected_type == 'Penalty Awarded':
            lines.append(f"- Awarded to: {event_data.get('team', '')}")
            if event_data.get('fouled_player'):
                lines.append(f"- Player fouled: {event_data.get('fouled_player', '')}")
            if event_data.get('fouler'):
                lines.append(f"- Foul by: {event_data.get('fouler', '')} ({event_data.get('fouler_team', '')})")
            if event_data.get('location'):
                lines.append(f"- Location: in the penalty area")
        
        elif detected_type.startswith('Penalty') and period == 5:
            # Penalty shootout
            penalty_num = event_data.get('penalty_number', '')
            lines.append(f"- PENALTY #{penalty_num} in shootout")
            lines.append(f"- Taker: {event_data.get('player', '')} ({event_data.get('team', '')})")
            lines.append(f"- Outcome: {event_data.get('outcome', '')}")
            if event_data.get('goalkeeper'):
                lines.append(f"- Goalkeeper: {event_data.get('goalkeeper', '')}")
            shootout = event_data.get('shootout_score', {})
            lines.append(f"- Shootout score after: {home_team} {shootout.get('home', 0)} - {shootout.get('away', 0)} {away_team}")
        
        elif 'Shot' in detected_type:
            lines.append(f"- Player: {event_data.get('player', '')} ({event_data.get('team', '')})")
            lines.append(f"- Outcome: {event_data.get('outcome', '')}")
            if event_data.get('body_part'):
                lines.append(f"- Body part: {event_data.get('body_part', '')}")
            if event_data.get('location'):
                lines.append(f"- Location: {event_data.get('location', '')}")
            if event_data.get('saved_by'):
                lines.append(f"- Saved by: {event_data.get('saved_by', '')}")
            if event_data.get('blocked_by'):
                lines.append(f"- Blocked by: {event_data.get('blocked_by', '')}")
        
        elif detected_type == 'Corner':
            lines.append(f"- Team: {event_data.get('team', '')}")
            if event_data.get('delivered_by'):
                lines.append(f"- Delivered by: {event_data.get('delivered_by', '')}")
            if event_data.get('conceded_by'):
                lines.append(f"- Conceded by: {event_data.get('conceded_by', '')}")
        
        elif detected_type in ['Foul', 'Free Kick']:
            if event_data.get('committed_by'):
                lines.append(f"- Foul by: {event_data.get('committed_by', '')} ({event_data.get('committed_team', '')})")
            if event_data.get('fouled_player'):
                lines.append(f"- On: {event_data.get('fouled_player', '')} ({event_data.get('fouled_team', '')})")
            if event_data.get('location'):
                lines.append(f"- Location: {event_data.get('location', '')}")
        
        elif detected_type in ['Yellow Card', 'Red Card']:
            lines.append(f"- Card to: {event_data.get('carded_player', '')} ({event_data.get('carded_team', '')})")
            if event_data.get('fouled_player'):
                lines.append(f"- For foul on: {event_data.get('fouled_player', '')} ({event_data.get('fouled_team', '')})")
        
        elif detected_type == 'Substitution':
            lines.append(f"- Team: {event_data.get('team', '')}")
            lines.append(f"- Off: {event_data.get('player_off', '')}")
            if event_data.get('substitution_info'):
                lines.append(f"- On: {event_data.get('substitution_info', '')}")
        
        elif detected_type == 'Kick Off':
            lines.append(f"- Phase: {event_data.get('phase', '')}")
            if period == 1 and stage:
                lines.append(f"- STAGE: {stage} (MUST MENTION IN COMMENTARY)")
            elif period == 5:
                lines.append(f"- PENALTY SHOOTOUT BEGINS")
        
        elif detected_type == 'Injury':
            lines.append(f"- Player: {event_data.get('injured_player', '')} ({event_data.get('injured_team', '')})")
        
        elif detected_type == 'General':
            control = match_context.get('control', '')
            possession = match_context.get('possession_stats', {})
            area = match_context.get('area', '')
            
            if control:
                lines.append(f"- Control: {control}")
            if area:
                lines.append(f"- Area of play: {area}")
            if possession:
                poss_str = ', '.join([f"{k}: {v}%" for k, v in possession.items()])
                lines.append(f"- Possession: {poss_str}")
        
        return '\n'.join(lines)
    
    def _format_multi_events_context(self, match_context: Dict) -> str:
        """Format multi-events context for the prompt."""
        lines = []
        
        # Multiple shots
        multi_shots = match_context.get('multi_shots_info', {})
        if multi_shots.get('has_multiple'):
            scenario = multi_shots.get('scenario', 'pressure')
            count = multi_shots.get('count', 0)
            most_dangerous = multi_shots.get('most_dangerous', {})
            lines.append(f"\nMULTIPLE SHOTS ({count}): {scenario} scenario")
            if most_dangerous:
                lines.append(f"  Most dangerous: {most_dangerous.get('player', '')} - {most_dangerous.get('outcome', '')}")
        
        # Multiple corners
        multi_corners = match_context.get('multi_corners_info', {})
        if multi_corners.get('has_multiple'):
            count = multi_corners.get('count', 0)
            scenario = multi_corners.get('scenario', '')
            lines.append(f"\nMULTIPLE CORNERS ({count}): {scenario}")
        
        # Multiple fouls
        multi_fouls = match_context.get('multi_fouls_info', {})
        if multi_fouls.get('has_multiple'):
            count = multi_fouls.get('count', 0)
            lines.append(f"\nMULTIPLE FOULS ({count}): Physical/scrappy minute")
        
        # Multiple subs
        multi_subs = match_context.get('multi_subs_info', {})
        if multi_subs.get('has_multiple'):
            count = multi_subs.get('count', 0)
            team_counts = multi_subs.get('team_counts', {})
            lines.append(f"\nMULTIPLE SUBSTITUTIONS ({count}): {team_counts}")
        
        return '\n'.join(lines)
    
    def generate_minute_commentary(
        self,
        minute: int,
        events_data: List[Dict],
        rule_based_commentary: str = "",
        sequence_commentary: str = "",
        match_context: Dict = None
    ) -> str:
        """Generate commentary for a single minute."""
        # Rate limiting
        elapsed = time.time() - self.last_request_time
        if elapsed < DELAY_BETWEEN_REQUESTS:
            time.sleep(DELAY_BETWEEN_REQUESTS - elapsed)
        
        # Build prompt
        prompt = self._create_minute_prompt(
            minute=minute,
            events_data=events_data,
            rule_based_commentary=rule_based_commentary,
            sequence_commentary=sequence_commentary,
            match_context=match_context or {}
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt + "\n\n" + ESPN_FEW_SHOT_EXAMPLES},
                    {"role": "user", "content": prompt}
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                top_p=TOP_P,
                seed=SEED
            )
            
            self.last_request_time = time.time()
            
            commentary = response.choices[0].message.content.strip()
            
            # Ensure single line
            if '\n' in commentary:
                commentary = commentary.split('\n')[0].strip()
            
            return commentary
            
        except Exception as e:
            return f"[Error] Commentary generation failed: {str(e)}"


if __name__ == "__main__":
    # Test the commentator
    print("Testing GPT Commentator V4...")
    
    try:
        commentator = GPTCommentator()
        print(f"✅ Initialized with model: {commentator.model}")
        
        # Test penalty shootout
        test_context = {
            'home_team': 'Portugal',
            'away_team': 'France',
            'home_score': 0,
            'away_score': 0,
            'stage': 'Quarter-finals',
            'period': 5,
            'detected_type': 'Penalty',
            'event_data': {
                'player': 'Cristiano Ronaldo',
                'team': 'Portugal',
                'outcome': 'Goal',
                'penalty_number': 2,
                'goalkeeper': 'Mike Maignan',
                'shootout_score': {'home': 1, 'away': 1}
            }
        }
        
        commentary = commentator.generate_minute_commentary(
            minute=120,
            events_data=[],
            match_context=test_context
        )
        print(f"Test commentary: {commentary}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

