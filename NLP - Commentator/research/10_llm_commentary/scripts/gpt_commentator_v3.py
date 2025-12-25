"""
GPT-Based Football Commentary Generator - V3
ENHANCED VERSION with:
- Progressive General events (1st basic, 2nd+ domination streak)
- Multiple Shots handling (same team vs different teams)
- Multiple Corners handling
- Multiple Fouls handling (count context)
- Multiple Substitutions (double/triple)
- Multiple Offsides (wide-to-wide context)
- LLM has freedom of action - we provide data, LLM decides wording

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

RULES:
1. For KICK OFF at minute 0: Include the stage (Final, Semi-Final, etc.)
2. For FOULS: Use "by X on Y" format when you have both players
3. Provide counts when multiple events happen
4. You have FREEDOM to choose exact wording - be creative but professional
5. NEVER use emojis
"""


class GPTCommentator:
    """
    Football commentary generator using OpenAI GPT models.
    
    V3: Enhanced with multiple events handling and LLM freedom.
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

DOMINATION CONTEXT:
For General events, I'll tell you if a team has dominated for X minutes.
Incorporate this naturally if relevant.

RULES:
1. KICK OFF minute 0: Include the stage (Final, Semi-Final)
2. FOULS: Use "by X on Y" format
3. MULTIPLE EVENTS: Mention count, you choose the description
4. Be CREATIVE with wording - don't be robotic
5. NEVER use emojis"""
    
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
                # First general - basic style
                domination_context = "\n(First general event - use basic possession style)"
            elif consecutive_generals >= 2:
                if domination_info.get('has_domination'):
                    dom_team = domination_info.get('team', '')
                    dom_streak = domination_info.get('streak', 0)
                    domination_context = f"\n(DOMINATION: {dom_team} controlling for {dom_streak} straight minutes - incorporate this)"
                else:
                    domination_context = f"\n(Consecutive general #{consecutive_generals} - add context about flow of play)"
        
        # Event chain context
        chain_section = ""
        event_chain = match_context.get('event_chain', {})
        if event_chain.get('has_chain'):
            chain_lines = []
            for related in event_chain.get('related_events', []):
                rel_type = related.get('type', '')
                if rel_type == 'Assist':
                    chain_lines.append(f"Assisted by: {related.get('player', '')}")
                elif rel_type in ['Yellow Card', 'Red Card']:
                    chain_lines.append(f"{rel_type} shown to: {related.get('player', '')}")
                elif rel_type == 'Free Kick':
                    chain_lines.append(f"Free kick: {related.get('position', '')}")
                elif rel_type == 'Corner':
                    chain_lines.append(f"Corner: {related.get('team', '')}")
            if chain_lines:
                chain_section = "\n\nRELATED:\n" + "\n".join(f"- {line}" for line in chain_lines)
        
        prompt = f"""Match: {home_team} {home_score} - {away_score} {away_team} ({stage})
Minute: {minute}' ({game_phase})

EVENT: {detected_type}
{event_details}{chain_section}{multi_context}{domination_context}

Generate ESPN-style commentary. You decide the exact wording."""

        return prompt
    
    def _format_multi_events_context(self, match_context: Dict) -> str:
        """Format context for multiple events in same minute."""
        lines = []
        
        # Multiple shots
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
        
        # Multiple corners
        multi_corners = match_context.get('multi_corners_info', {})
        if multi_corners.get('has_multiple'):
            count = multi_corners.get('count', 0)
            scenario = multi_corners.get('scenario', '')
            teams = multi_corners.get('team_counts', {})
            lines.append(f"\nMULTIPLE CORNERS ({count} total):")
            lines.append(f"  Scenario: {scenario.upper()}")
            lines.append(f"  Teams: {teams}")
        
        # Multiple fouls
        multi_fouls = match_context.get('multi_fouls_info', {})
        if multi_fouls.get('has_multiple'):
            count = multi_fouls.get('count', 0)
            lines.append(f"\nMULTIPLE FOULS ({count} total):")
            lines.append(f"  (You decide: scrappy, physical, busy referee, etc.)")
        
        # Multiple substitutions
        multi_subs = match_context.get('multi_subs_info', {})
        if multi_subs.get('has_multiple'):
            team_counts = multi_subs.get('team_counts', {})
            for team, count in team_counts.items():
                if count >= 2:
                    sub_type = "Triple" if count >= 3 else "Double"
                    players = multi_subs.get('players_by_team', {}).get(team, [])
                    lines.append(f"\n{sub_type.upper()} SUBSTITUTION ({team}):")
                    lines.append(f"  Players: {', '.join(players)}")
        
        # Multiple offsides
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
    
    def _format_event_data(self, detected_type: str, event_data: Dict, match_context: Dict) -> str:
        """Format event data based on event type."""
        lines = []
        
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
            home_team = match_context.get('home_team', 'Home')
            away_team = match_context.get('away_team', 'Away')
            home_score = match_context.get('home_score', 0)
            away_score = match_context.get('away_score', 0)
            # IMPORTANT: Make score explicit - LLM MUST use these exact numbers
            lines.append(f"SCORE AFTER GOAL: {home_team} {home_score}, {away_team} {away_score}")
            lines.append(f"(USE EXACTLY: {home_team} {home_score}, {away_team} {away_score} - DO NOT CHANGE)")
        
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
            # V3 FIX: Clarify this is a single corner, not multiple
            lines.append(f"(This is ONE corner kick - do not mention multiple corners unless MULTIPLE CORNERS section is provided)")
        
        elif detected_type == 'Free Kick':
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
            period = event_data.get('period', 1)
            stage = match_context.get('stage', '')
            
            lines.append(f"Phase: {phase}")
            if period == 1 and stage:
                lines.append(f"STAGE: {stage} (MUST MENTION IN COMMENTARY)")
        
        elif detected_type == 'Injury':
            injured_player = event_data.get('injured_player', player)
            injured_team = event_data.get('injured_team', team)
            
            lines.append(f"Injured: {injured_player} ({injured_team})")
        
        elif detected_type == 'Offside':
            offside_player = event_data.get('offside_player', player)
            offside_team = event_data.get('offside_team', team)
            
            lines.append(f"Player: {offside_player} ({offside_team})")
        
        elif detected_type == 'General':
            control = match_context.get('control', '')
            possession_stats = match_context.get('possession_stats', {})
            most_active = match_context.get('most_active_player', {})
            area = match_context.get('area', '')
            
            if control:
                # V3 FIX: Add area to control (e.g., "Spain in control in midfield")
                if area:
                    lines.append(f"Control: {control} in {area}")
                else:
                    lines.append(f"Control: {control}")
            if possession_stats:
                poss_str = ', '.join([f"{k}: {v}%" for k, v in possession_stats.items()])
                # Add area context to possession
                if area:
                    lines.append(f"Possession: {poss_str} (mostly in {area})")
                else:
                    lines.append(f"Possession: {poss_str}")
            if most_active.get('player'):
                lines.append(f"Most active: {most_active['player']} ({most_active.get('count', 0)} events)")
        
        else:
            if player:
                lines.append(f"Player: {player} ({team})")
            if location:
                lines.append(f"Location: {location}")
        
        return '\n'.join(f"- {line}" for line in lines) if lines else "- General play"
    
    def _rate_limit(self):
        """Apply rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < DELAY_BETWEEN_REQUESTS:
            time.sleep(DELAY_BETWEEN_REQUESTS - elapsed)
        self.last_request_time = time.time()
    
    def generate_minute_commentary(
        self,
        minute: int,
        events_data: List[Dict],
        rule_based_commentary: str,
        sequence_commentary: str,
        match_context: Dict,
        temperature: Optional[float] = None,
        use_few_shot: bool = True
    ) -> str:
        """Generate commentary for all events in a specific minute."""
        self._rate_limit()
        
        user_prompt = self._create_minute_prompt(
            minute, events_data, rule_based_commentary, 
            sequence_commentary, match_context
        )
        
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
            # Split by newlines and take the first non-empty line
            lines = [line.strip() for line in commentary.split('\n') if line.strip()]
            if lines:
                commentary = lines[0]
            
            return commentary
            
        except Exception as e:
            print(f"Error generating commentary: {e}")
            return f"[Error generating commentary for minute {minute}]"


# =====================================
# EXAMPLE USAGE
# =====================================
if __name__ == "__main__":
    print("=" * 60)
    print("GPT Commentary Generator V3 - Test")
    print("=" * 60)
    
    try:
        commentator = GPTCommentator()
        print(f"\n✅ Initialized with model: {commentator.model}")
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")

