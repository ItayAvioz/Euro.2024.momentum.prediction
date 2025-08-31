#!/usr/bin/env python3
"""
3-Minute Momentum Calculator
============================

Production-ready implementation of the comprehensive momentum calculation system
for Euro 2024 football data, based on the Final Momentum Function Summary.

This module calculates team momentum in 3-minute windows using:
- All 25 kept event types with outcome-specific logic
- Team perspective (own vs opponent actions)
- Contextual multipliers (location, time, score, pressure)
- Hybrid weighted averaging for temporal windows

Author: Euro 2024 Momentum Prediction Project
Date: January 31, 2025
"""

import json
import ast
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')


class MomentumCalculator:
    """
    Main class for calculating momentum in 3-minute windows.
    
    Implements the complete methodology from Final_Momentum_Function_Summary.md
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize the momentum calculator.
        
        Args:
            verbose: Whether to print detailed calculation information
        """
        self.verbose = verbose
        self.eliminated_events = {
            'Bad Behaviour', 'Own Goal For', 'Injury Stoppage', 'Half Start', 
            'Half End', 'Referee Ball-Drop', 'Starting XI', 'Offside', 
            'Error', 'Ball Out', 'Camera Off'
        }
    
    def calculate_momentum_weight(self, event_data: Dict, target_team: str, game_context: Dict) -> float:
        """
        Main momentum calculation function for individual events.
        
        Args:
            event_data: Dict containing all event information
            target_team: String team name we're calculating momentum for
            game_context: Dict with score_diff, minute, etc.
        
        Returns:
            Float: Final momentum value (0-10)
        """
        # STEP 1: Determine team involvement
        primary_team = self.get_primary_team(event_data)
        
        if not primary_team:
            return 3.0  # No team identified = neutral momentum
        
        # STEP 2: Get base momentum by event type
        event_type = self.get_event_type_name(event_data.get('type', ''))
        base_momentum = self.get_base_momentum_by_event(event_data, event_type)
        
        if base_momentum == 0:
            return 0.0  # Eliminated event type
        
        # STEP 3: Apply team perspective
        if primary_team == target_team:
            # Own team action - direct impact
            team_momentum = base_momentum
            field_perspective = "attacking"  # Normal field orientation
        else:
            # Opponent action - convert to our momentum impact
            team_momentum = self.get_opponent_momentum_impact(event_data, event_type, base_momentum)
            field_perspective = "defending"  # Flipped field orientation
        
        # STEP 4: Apply context multipliers
        location_mult = self.get_location_multiplier(event_data, target_team, field_perspective)
        time_mult = self.get_time_multiplier(game_context.get('minute', 45))
        score_mult = self.get_score_multiplier(game_context, target_team)
        pressure_mult = self.get_pressure_multiplier(event_data)
        
        # STEP 4.5: Apply dampening for high multipliers
        combined_multiplier = location_mult * time_mult * score_mult * pressure_mult
        
        # Root dampening: If combined multiplier > 1.0, apply square root to reduce amplification
        if combined_multiplier > 1.0:
            dampened_multiplier = combined_multiplier ** 0.5  # Square root dampening
        else:
            dampened_multiplier = combined_multiplier  # No change for values <= 1.0
        
        # STEP 5: Final calculation with dampened multiplier
        final_momentum = team_momentum * dampened_multiplier
        
        # STEP 6: Clip to valid range
        result = np.clip(final_momentum, 0, 10)
        
        if self.verbose:
            print(f"Event: {event_type} | Team: {primary_team} | Target: {target_team}")
            print(f"Base: {base_momentum:.2f} | Team: {team_momentum:.2f} | Combined Mult: {combined_multiplier:.3f} | Dampened: {dampened_multiplier:.3f} | Final: {result:.2f}")
        
        return result
    
    def get_base_momentum_by_event(self, event_data: Dict, event_type: str) -> float:
        """
        Router function for all 25 kept event types.
        """
        if event_type in self.eliminated_events:
            return 0.0  # Eliminated event types
        
        # Route to specific event momentum calculators
        event_handlers = {
            'Shot': self.get_shot_momentum,
            'Pass': self.get_pass_momentum,
            'Carry': self.get_carry_momentum,
            'Pressure': self.get_pressure_momentum,
            'Ball Recovery': self.get_ball_recovery_momentum,
            'Clearance': self.get_clearance_momentum,
            'Duel': self.get_duel_momentum,
            'Foul Committed': self.get_foul_committed_momentum,
            'Dribble': self.get_dribble_momentum,
            'Foul Won': self.get_foul_won_momentum,
            'Miscontrol': self.get_miscontrol_momentum,
            'Dispossessed': self.get_dispossessed_momentum,
            'Interception': self.get_interception_momentum,
            'Block': self.get_block_momentum,
            'Counterpress': self.get_counterpress_momentum,
            '50/50': self.get_fifty_fifty_momentum,
            'Goal Keeper': self.get_goalkeeper_momentum,
            'Ball Receipt*': self.get_ball_receipt_momentum,
            'Substitution': self.get_substitution_momentum,
            'Tactical Shift': self.get_tactical_shift_momentum,
            'Shield': self.get_shield_momentum,
            'Player On': self.get_player_on_momentum,
            'Player Off': self.get_player_off_momentum,
            'Throw In': self.get_throw_in_momentum,
            'Penalty': self.get_penalty_momentum
        }
        
        handler = event_handlers.get(event_type, lambda x: 3.0)
        return handler(event_data)
    
    # =====================================
    # INDIVIDUAL EVENT MOMENTUM FUNCTIONS
    # =====================================
    
    def get_shot_momentum(self, event_data: Dict) -> float:
        """Shot with complete outcome analysis"""
        shot_data = self.get_event_detail(event_data, 'shot')
        outcome = self.get_shot_outcome(shot_data)
        
        outcome_values = {
            'Goal': 10.0,
            'Saved': 8.0,
            'Post': 7.5,
            'Saved to Post': 7.5,
            'Blocked': 5.5,
            'Off T': 4.0,
            'Wayward': 3.5
        }
        
        base_momentum = outcome_values.get(outcome, 6.0)
        
        # Context bonuses
        if self.has_boolean_flag(shot_data, 'one_on_one'):
            base_momentum += 1.0
        if self.has_boolean_flag(shot_data, 'open_goal'):
            base_momentum += 1.5
        if self.has_boolean_flag(shot_data, 'first_time'):
            base_momentum += 0.3
        
        return min(base_momentum, 10.0)
    
    def get_pass_momentum(self, event_data: Dict) -> float:
        """Pass with type and outcome hierarchy"""
        pass_data = self.get_event_detail(event_data, 'pass')
        
        # Check failure first
        if self.has_outcome(pass_data, 'Incomplete') or self.has_boolean_flag(pass_data, 'out'):
            return 2.0
        
        # Special pass types
        if self.has_boolean_flag(pass_data, 'goal_assist'):
            return 9.0
        elif self.has_boolean_flag(pass_data, 'shot_assist'):
            return 7.5
        elif self.has_boolean_flag(pass_data, 'through_ball'):
            return 7.0
        elif self.has_boolean_flag(pass_data, 'switch'):
            return 6.5
        elif self.has_boolean_flag(pass_data, 'cross'):
            return 6.0
        elif self.has_boolean_flag(pass_data, 'cut_back'):
            return 6.5
        
        # Pass type specific
        pass_type = self.get_pass_type(pass_data)
        if pass_type in ['Free Kick', 'Corner']:
            return 6.5
        elif pass_type == 'Penalty':
            return 8.0
        
        # Under pressure penalty
        pressure_penalty = -0.5 if self.has_boolean_flag(pass_data, 'under_pressure') else 0.0
        return 5.0 + pressure_penalty
    
    def get_carry_momentum(self, event_data: Dict) -> float:
        """Carry based on distance and direction"""
        carry_data = self.get_event_detail(event_data, 'carry')
        
        # Check if carry ended in dispossession
        if self.has_outcome(carry_data, 'Dispossessed'):
            return 2.5
        
        return 5.5  # Base carry momentum
    
    def get_dribble_momentum(self, event_data: Dict) -> float:
        """Dribble success/failure analysis"""
        dribble_data = self.get_event_detail(event_data, 'dribble')
        
        if self.has_outcome(dribble_data, 'Complete'):
            base_momentum = 7.0
            if self.has_boolean_flag(dribble_data, 'nutmeg'):
                base_momentum += 1.0
            if self.has_boolean_flag(dribble_data, 'under_pressure'):
                base_momentum += 0.5
            return base_momentum
        elif self.has_outcome(dribble_data, 'Incomplete'):
            return 2.5
        else:
            return 5.0
    
    def get_goalkeeper_momentum(self, event_data: Dict) -> float:
        """Comprehensive goalkeeper action momentum"""
        gk_data = self.get_event_detail(event_data, 'goalkeeper')
        gk_type = self.get_goalkeeper_type(gk_data)
        
        gk_values = {
            'Penalty Saved': 9.5,
            'Shot Saved': 7.5,
            'Save': 7.0,
            'Smother': 6.5,
            'Claim': 5.5,
            'Collected': 5.0,
            'Punch': 4.5,
            'Keeper Sweeper': 6.8,
            'Goal Conceded': 1.0,
            'Penalty Conceded': 0.5
        }
        
        return gk_values.get(gk_type, 5.0)
    
    def get_duel_momentum(self, event_data: Dict) -> float:
        """Duel win/loss outcome"""
        duel_data = self.get_event_detail(event_data, 'duel')
        
        if self.has_outcome(duel_data, 'Won'):
            if self.has_boolean_flag(duel_data, 'aerial_won'):
                return 6.5  # Won aerial duel
            else:
                return 6.0  # Won ground duel
        elif self.has_outcome(duel_data, 'Lost'):
            return 2.5  # Lost duel
        else:
            return 4.5  # Neutral duel
    
    def get_foul_committed_momentum(self, event_data: Dict) -> float:
        """Foul committed with card severity"""
        foul_data = self.get_event_detail(event_data, 'foul_committed')
        
        if self.has_boolean_flag(foul_data, 'red_card') or self.has_boolean_flag(foul_data, 'second_yellow'):
            return 1.0  # Very negative - sent off
        elif self.has_boolean_flag(foul_data, 'yellow_card'):
            return 2.5  # Negative - yellow card
        else:
            return 3.5  # Standard foul
    
    def get_foul_won_momentum(self, event_data: Dict) -> float:
        """Foul won - advantage gained"""
        foul_data = self.get_event_detail(event_data, 'foul_won')
        
        if self.has_boolean_flag(foul_data, 'penalty'):
            return 8.5  # Penalty won
        else:
            return 5.5  # Standard foul won
    
    # Simple momentum functions for other event types
    def get_pressure_momentum(self, event_data: Dict) -> float:
        return 4.5
    
    def get_ball_recovery_momentum(self, event_data: Dict) -> float:
        return 6.0
    
    def get_clearance_momentum(self, event_data: Dict) -> float:
        clearance_data = self.get_event_detail(event_data, 'clearance')
        return 5.5 if self.has_boolean_flag(clearance_data, 'aerial_won') else 4.5
    
    def get_miscontrol_momentum(self, event_data: Dict) -> float:
        return 2.0
    
    def get_dispossessed_momentum(self, event_data: Dict) -> float:
        return 2.0
    
    def get_interception_momentum(self, event_data: Dict) -> float:
        return 6.5
    
    def get_block_momentum(self, event_data: Dict) -> float:
        return 5.5
    
    def get_counterpress_momentum(self, event_data: Dict) -> float:
        return 5.0
    
    def get_fifty_fifty_momentum(self, event_data: Dict) -> float:
        fifty_data = self.get_event_detail(event_data, '50_50')
        if self.has_outcome(fifty_data, 'Won'):
            return 5.5
        elif self.has_outcome(fifty_data, 'Lost'):
            return 3.0
        else:
            return 4.0
    
    def get_ball_receipt_momentum(self, event_data: Dict) -> float:
        receipt_data = self.get_event_detail(event_data, 'ball_receipt')
        return 2.0 if self.has_outcome(receipt_data, 'Incomplete') else 4.5
    
    def get_substitution_momentum(self, event_data: Dict) -> float:
        return 4.0
    
    def get_tactical_shift_momentum(self, event_data: Dict) -> float:
        return 4.0
    
    def get_shield_momentum(self, event_data: Dict) -> float:
        return 5.0
    
    def get_player_on_momentum(self, event_data: Dict) -> float:
        return 4.2
    
    def get_player_off_momentum(self, event_data: Dict) -> float:
        return 3.8
    
    def get_throw_in_momentum(self, event_data: Dict) -> float:
        return 4.5
    
    def get_penalty_momentum(self, event_data: Dict) -> float:
        penalty_data = self.get_event_detail(event_data, 'penalty')
        outcome = self.get_penalty_outcome(penalty_data)
        
        outcome_values = {
            'Goal': 10.0,
            'Saved': 8.0,
            'Off Target': 4.0
        }
        
        return outcome_values.get(outcome, 8.5)
    
    # =====================================
    # TEAM PERSPECTIVE FUNCTIONS
    # =====================================
    
    def get_opponent_momentum_impact(self, event_data: Dict, event_type: str, base_momentum: float) -> float:
        """Convert opponent actions into target team momentum impact"""
        
        # HIGH THREAT: Opponent scoring/creating major danger
        if event_type in ['Shot'] and base_momentum >= 8.0:
            return 1.0  # Their great shot/goal = very bad for us
        elif event_type in ['Shot'] and base_momentum >= 5.0:
            return 2.0  # Their decent shot = bad for us
        elif event_type in ['Dribble', 'Foul Won'] and base_momentum >= 6.0:
            return 2.5  # Their skill/advantage = pressure on us
        elif event_type in ['Pass'] and base_momentum >= 7.0:
            return 2.0  # Their key pass = concerning for us
        
        # OPPONENT MISTAKES: Their errors = our opportunities
        elif event_type in ['Miscontrol', 'Dispossessed', 'Foul Committed']:
            return max(1.0, 6.0 - base_momentum)  # Inverse relationship
        
        # MEDIUM IMPACT: Standard opponent actions
        elif event_type in ['Interception', 'Ball Recovery', 'Clearance']:
            return 3.5  # Opponent defensive success = slight negative for us
        
        # NEUTRAL: Routine opponent actions
        else:
            return 3.0  # Standard neutral momentum
    
    # =====================================
    # CONTEXT MULTIPLIER FUNCTIONS
    # =====================================
    
    def get_location_multiplier(self, event_data: Dict, target_team: str, field_perspective: str) -> float:
        """Location multiplier based on team perspective"""
        if not self.has_valid_coordinates(event_data):
            return 1.0  # No location data = no bonus/penalty
        
        x_coord = self.get_x_coordinate(event_data.get('location'))
        
        if field_perspective == "attacking":
            # Target team is in attacking mode (normal orientation)
            if x_coord < 40:
                return 0.8   # Own defensive third
            elif x_coord <= 80:
                return 1.0   # Middle third
            else:
                return 1.4   # Final third (attacking bonus)
        
        elif field_perspective == "defending":
            # Target team is defending (flipped coordinates perspective)
            if x_coord > 80:
                return 0.8   # Own defensive area (under pressure)
            elif x_coord >= 40:
                return 1.0   # Middle third  
            else:
                return 1.4   # Counter-attack opportunity
        
        else:
            return 1.0  # Default neutral
    
    def get_time_multiplier(self, minute: float) -> float:
        """Game phase multiplier based on psychological pressure"""
        if 0 <= minute < 15:
            return 0.85    # Early game settling
        elif 15 <= minute < 30:
            return 1.0     # First half baseline
        elif 30 <= minute < 45:
            return 1.1     # Pre-halftime intensity
        elif 45 <= minute < 60:
            return 1.05    # Second half start
        elif 60 <= minute < 75:
            return 1.15    # Crucial middle period
        elif 75 <= minute < 90:
            return 1.25    # Final push
        else:  # 90+
            return 1.35    # Extra time desperation
    
    def get_score_multiplier(self, game_context: Dict, target_team: str) -> float:
        """
        Score situation multiplier based on EDA analysis.
        
        DYNAMIC SCORE COEFFICIENT: Score coefficient now changes dynamically within the window
        when goals are scored, providing more accurate psychological context for each event.
        - Events BEFORE a goal use the pre-goal score context
        - Events AFTER a goal use the post-goal score context
        - This captures the immediate momentum shift that goals create
        """
        score_diff = game_context.get('score_diff', 0)  # Score at WINDOW START
        minute = game_context.get('minute', 45)
        
        # Base amplifiers from EDA tournament analysis
        if score_diff == 0:
            score_mult = 1.25      # Draw - maximum urgency (Late Winner pattern)
        elif score_diff == -1:
            score_mult = 1.20      # Losing by 1 - comeback urgency  
        elif score_diff <= -2:
            score_mult = 1.18      # Losing by 2+ - desperation mode
        elif score_diff == 1:
            score_mult = 1.08      # Leading by 1 - careful control
        elif score_diff >= 2:
            score_mult = 1.02      # Leading by 2+ - game management
        else:
            score_mult = 1.0       # Other situations
        
        # EDA Insight: Second half 23.4% more efficient for losing/tied teams
        if minute >= 45 and score_diff <= 0:
            score_mult += 0.05     # Tactical urgency boost
        
        return max(0.95, min(score_mult, 1.30))  # Safety bounds
    
    def get_pressure_multiplier(self, event_data: Dict) -> float:
        """Under pressure situation multiplier"""
        if self.has_boolean_flag(event_data, 'under_pressure'):
            return 1.2  # 20% bonus for success under pressure
        else:
            return 1.0  # No bonus for normal conditions
    
    # =====================================
    # 3-MINUTE WINDOW CALCULATION
    # =====================================
    
    def calculate_3min_team_momentum(self, events_window: List[Dict], target_team: str, game_context: Dict) -> float:
        """
        Aggregate individual event momentum into window momentum using hybrid weighting.
        
        Args:
            events_window: List of events in the 3-minute window
            target_team: Team name we're calculating momentum for
            game_context: Game context (score_diff, minute, etc.)
        
        Returns:
            Float: Weighted average momentum for the window
        """
        # Filter events for target team using Team Involvement Hybrid
        team_events = self.filter_team_events(events_window, target_team)
        
        if not team_events:
            return 3.0  # Neutral momentum if no relevant events
        
        team_events_momentum = []
        
        # Calculate momentum for each team event with DYNAMIC score coefficients
        for event in team_events:
            # Create dynamic game context for this specific event
            dynamic_context = self.get_dynamic_game_context(events_window, event, target_team, game_context)
            event_momentum = self.calculate_momentum_weight(event, target_team, dynamic_context)
            if event_momentum > 0:  # Only include meaningful events
                team_events_momentum.append(event_momentum)
        
        if not team_events_momentum:
            return 3.0  # Neutral momentum if no meaningful events
        
        # Apply hybrid weighted average (0.7 base + 0.3 recency)
        total_weight = 0
        weighted_sum = 0
        
        for i, momentum in enumerate(team_events_momentum):
            base_weight = 0.7  # Base importance for all events
            recency_weight = 0.3 * (i + 1) / len(team_events_momentum)  # Recency bonus
            event_weight = base_weight + recency_weight
            
            weighted_sum += momentum * event_weight
            total_weight += event_weight
        
        result = weighted_sum / total_weight if total_weight > 0 else 3.0
        
        if self.verbose:
            print(f"Team: {target_team} | Events: {len(team_events_momentum)} | Momentum: {result:.2f}")
        
        return result
    
    def filter_team_events(self, events_window: List[Dict], target_team: str) -> List[Dict]:
        """
        Filter events for specific team using Team Involvement Hybrid.
        
        Returns events where: team_name == target_team OR possession_team == target_team
        """
        team_events = []
        
        for event in events_window:
            primary_team = self.get_primary_team(event)
            possession_team = self.get_possession_team_name(event)
            
            # Team Involvement Hybrid: Include if either matches
            if primary_team == target_team or possession_team == target_team:
                team_events.append(event)
        
        return team_events
    
    def process_full_match_3min_windows(self, match_events: pd.DataFrame, 
                                       home_team: str, away_team: str) -> pd.DataFrame:
        """
        Process a full match and calculate momentum for all 3-minute windows.
        
        Args:
            match_events: DataFrame with all match events
            home_team: Home team name
            away_team: Away team name
        
        Returns:
            DataFrame with momentum calculations for each 3-minute window
        """
        # Ensure events are sorted by time
        match_events = match_events.sort_values('minute').reset_index(drop=True)
        
        # Get match duration
        max_minute = match_events['minute'].max()
        
        # Initialize results list
        results = []
        
        # Process 3-minute windows starting from minute 3
        for window_start in range(3, int(max_minute) + 1, 3):
            window_end = window_start + 3
            
            # Get events in this window
            window_events = match_events[
                (match_events['minute'] >= window_start - 3) & 
                (match_events['minute'] < window_start)
            ].to_dict('records')
            
            # Calculate game context for this window
            minute = window_start
            
            # Calculate score difference at WINDOW START (beginning of 3-minute window)
            # Score is evaluated at window_start minute, NOT during the window
            window_start_time = window_start - 3
            score_at_window_start = self.calculate_score_at_minute(match_events, window_start_time)
            home_score = score_at_window_start['home_score']
            away_score = score_at_window_start['away_score']
            
            # Calculate momentum for both teams using score at window START
            home_context = {'score_diff': home_score - away_score, 'minute': minute}
            away_context = {'score_diff': away_score - home_score, 'minute': minute}
            
            home_momentum = self.calculate_3min_team_momentum(window_events, home_team, home_context)
            away_momentum = self.calculate_3min_team_momentum(window_events, away_team, away_context)
            
            # Store results
            results.append({
                'minute': minute,
                'window_start': window_start - 3,
                'window_end': window_start,
                'home_team': home_team,
                'away_team': away_team,
                'home_momentum': home_momentum,
                'away_momentum': away_momentum,
                'home_score': home_score,
                'away_score': away_score,
                'events_in_window': len(window_events)
            })
        
        return pd.DataFrame(results)
    
    def calculate_score_at_minute(self, match_events: pd.DataFrame, target_minute: float) -> Dict:
        """
        Calculate the cumulative score at a specific minute (beginning of window).
        
        Args:
            match_events: All match events
            target_minute: The minute to calculate score for
        
        Returns:
            Dict with home_score and away_score at target_minute
        """
        # Get all shot events up to (but not including) target_minute
        # Fix: Handle event type stored as dictionary string format
        shot_events = match_events[
            (match_events['type'].str.contains('Shot', na=False)) & 
            (match_events['minute'] < target_minute)
        ]
        
        home_score = 0
        away_score = 0
        
        # Count goals for each team up to target_minute
        for _, event in shot_events.iterrows():
            event_dict = event.to_dict()
            shot_data = self.get_event_detail(event_dict, 'shot')
            
            # Check if this shot was a goal
            if self.get_shot_outcome(shot_data) == 'Goal':
                team_name = self.get_team_name(event_dict.get('team', ''))
                home_team = self.get_team_name(event_dict.get('home_team_name', ''))
                
                if team_name == home_team:
                    home_score += 1
                else:
                    away_score += 1
        
        return {'home_score': home_score, 'away_score': away_score}
    
    def get_dynamic_game_context(self, events_window: List[Dict], current_event: Dict, target_team: str, base_context: Dict) -> Dict:
        """
        Calculate dynamic game context considering goals scored before the current event within the window.
        
        Args:
            events_window: All events in the 3-minute window
            current_event: The specific event we're calculating momentum for
            target_team: Team name we're calculating momentum for
            base_context: Original game context at window start
        
        Returns:
            Dict: Updated game context with dynamic score difference
        """
        current_minute = current_event.get('minute', 0)
        
        # Count goals that happened BEFORE this event in the same window
        goals_in_window = 0
        goals_against_in_window = 0
        
        for event in events_window:
            # Only consider events that happened before the current event
            if event.get('minute', 0) < current_minute:
                event_type = self.get_event_type_name(event.get('type', ''))
                
                # Check if this is a goal
                if event_type == 'Shot':
                    shot_data = self.get_event_detail(event, 'shot')
                    if self.get_shot_outcome(shot_data) == 'Goal':
                        scoring_team = self.get_team_name(event.get('team', ''))
                        
                        if scoring_team == target_team:
                            goals_in_window += 1  # Our goal
                        else:
                            goals_against_in_window += 1  # Opponent goal
        
        # Calculate new score difference
        original_score_diff = base_context.get('score_diff', 0)
        dynamic_score_diff = original_score_diff + goals_in_window - goals_against_in_window
        
        # Create dynamic context
        dynamic_context = base_context.copy()
        dynamic_context['score_diff'] = dynamic_score_diff
        dynamic_context['minute'] = current_minute  # Use event's actual minute
        
        return dynamic_context
    
    # =====================================
    # HELPER FUNCTIONS
    # =====================================
    
    def get_primary_team(self, event_data: Dict) -> str:
        """Team Involvement Hybrid: team_name OR possession_team"""
        team_name = self.get_team_name(event_data.get('team', ''))
        possession_team = self.get_possession_team_name(event_data)
        return team_name or possession_team
    
    def get_possession_team_name(self, event_data: Dict) -> str:
        """Extract possession team name from event data"""
        possession_team = event_data.get('possession_team', '')
        return self.get_team_name(possession_team)
    
    def get_team_name(self, team_data: Any) -> str:
        """Extract clean team name from team data"""
        if isinstance(team_data, dict):
            return team_data.get('name', '')
        elif isinstance(team_data, str):
            # Try to parse if it's a string representation of a dictionary
            try:
                # Handle Python dict string format like "{'id': 941, 'name': 'Netherlands'}"
                parsed = eval(team_data)
                if isinstance(parsed, dict):
                    return parsed.get('name', '')
            except:
                pass
            
            try:
                # Try JSON format
                parsed = json.loads(team_data)
                if isinstance(parsed, dict):
                    return parsed.get('name', '')
            except:
                pass
            
            # If it's already a simple string team name, return it
            return team_data
        else:
            return ''
    
    def get_event_type_name(self, event_type_data: Any) -> str:
        """Extract clean event type name from event type data"""
        if isinstance(event_type_data, dict):
            return event_type_data.get('name', '')
        elif isinstance(event_type_data, str):
            # Try to parse if it's a string representation of a dictionary
            try:
                # Handle Python dict string format like "{'id': 16, 'name': 'Shot'}"
                parsed = eval(event_type_data)
                if isinstance(parsed, dict):
                    return parsed.get('name', '')
            except:
                pass
            
            try:
                # Try JSON format
                parsed = json.loads(event_type_data)
                if isinstance(parsed, dict):
                    return parsed.get('name', '')
            except:
                pass
            
            # If it's already a simple string event type, return it
            return event_type_data
        else:
            return ''
    
    def get_event_detail(self, event_data: Dict, detail_key: str) -> Dict:
        """Safely extract and parse JSON event details"""
        detail = event_data.get(detail_key, {})
        
        if detail is None or detail == '':
            return {}
        
        if isinstance(detail, str):
            try:
                return json.loads(detail)  # Parse JSON string
            except:
                try:
                    return ast.literal_eval(detail)  # Parse Python literal
                except:
                    return {}
        
        return detail if isinstance(detail, dict) else {}
    
    def has_boolean_flag(self, event_data: Dict, flag_name: str) -> bool:
        """Check if boolean flag is True in event data"""
        if not isinstance(event_data, dict):
            return False
        return event_data.get(flag_name, False) is True
    
    def has_outcome(self, detail_data: Dict, outcome_name: str) -> bool:
        """Check specific outcome in event detail"""
        if not isinstance(detail_data, dict):
            return False
        
        outcome = detail_data.get('outcome', {})
        if isinstance(outcome, dict):
            return outcome.get('name', '') == outcome_name
        return False
    
    def has_valid_coordinates(self, event_data: Dict) -> bool:
        """Check if event has valid x,y coordinates"""
        location = event_data.get('location', None)
        if location is None:
            return False
        
        try:
            if isinstance(location, str):
                coords = json.loads(location)  # Parse "[x, y]" string
            else:
                coords = location
            
            return (isinstance(coords, list) and 
                    len(coords) >= 2 and 
                    coords[0] is not None and 
                    coords[1] is not None)
        except:
            return False
    
    def get_x_coordinate(self, location: Any) -> float:
        """Extract x coordinate with error handling"""
        try:
            if isinstance(location, str):
                coords = json.loads(location)
            else:
                coords = location
            
            return float(coords[0]) if coords[0] is not None else 60.0
        except:
            return 60.0  # Default to pitch center
    
    def get_shot_outcome(self, shot_data: Dict) -> str:
        """Get shot outcome from shot detail data"""
        if not isinstance(shot_data, dict):
            return 'Unknown'
        
        outcome = shot_data.get('outcome', {})
        if isinstance(outcome, dict):
            return outcome.get('name', 'Unknown')
        return 'Unknown'
    
    def get_pass_type(self, pass_data: Dict) -> str:
        """Get pass type from pass detail data"""
        if not isinstance(pass_data, dict):
            return 'Regular'
        
        pass_type = pass_data.get('type', {})
        if isinstance(pass_type, dict):
            return pass_type.get('name', 'Regular')
        return 'Regular'
    
    def get_goalkeeper_type(self, gk_data: Dict) -> str:
        """Get goalkeeper action type"""
        if not isinstance(gk_data, dict):
            return 'Unknown'
        
        gk_type = gk_data.get('type', {})
        if isinstance(gk_type, dict):
            return gk_type.get('name', 'Unknown')
        return 'Unknown'
    
    def get_penalty_outcome(self, penalty_data: Dict) -> str:
        """Get penalty outcome"""
        if not isinstance(penalty_data, dict):
            return 'Unknown'
        
        outcome = penalty_data.get('outcome', {})
        if isinstance(outcome, dict):
            return outcome.get('name', 'Unknown')
        return 'Unknown'


# =====================================
# CONVENIENCE FUNCTIONS
# =====================================

def calculate_match_momentum(match_events: pd.DataFrame, home_team: str, away_team: str, 
                           verbose: bool = False) -> pd.DataFrame:
    """
    Convenience function to calculate momentum for a full match.
    
    Args:
        match_events: DataFrame with match events
        home_team: Home team name
        away_team: Away team name
        verbose: Whether to print detailed information
    
    Returns:
        DataFrame with 3-minute momentum calculations
    """
    calculator = MomentumCalculator(verbose=verbose)
    return calculator.process_full_match_3min_windows(match_events, home_team, away_team)


def calculate_window_momentum(events: List[Dict], target_team: str, 
                            game_context: Dict, verbose: bool = False) -> float:
    """
    Convenience function to calculate momentum for a single 3-minute window.
    
    Args:
        events: List of events in the window
        target_team: Team name to calculate momentum for
        game_context: Dict with score_diff, minute, etc.
        verbose: Whether to print detailed information
    
    Returns:
        Float momentum value for the window
    """
    calculator = MomentumCalculator(verbose=verbose)
    return calculator.calculate_3min_team_momentum(events, target_team, game_context)


# =====================================
# EXAMPLE USAGE
# =====================================

if __name__ == "__main__":
    print("🎯 3-Minute Momentum Calculator")
    print("=" * 50)
    
    # Example usage with sample data
    sample_events = [
        {
            'type': 'Shot',
            'team': 'Spain',
            'possession_team': 'Spain',
            'location': '[95, 45]',
            'minute': 67,
            'shot': '{"outcome": {"name": "Saved"}}'
        },
        {
            'type': 'Pass',
            'team': 'Spain',
            'possession_team': 'Spain',
            'location': '[70, 30]',
            'minute': 68,
            'pass': '{"goal_assist": true}'
        }
    ]
    
    game_context = {'score_diff': 0, 'minute': 67}
    
    # Calculate momentum for Spain
    momentum = calculate_window_momentum(sample_events, 'Spain', game_context, verbose=True)
    print(f"\n🏆 Spain momentum for this window: {momentum:.2f}")
    
    print("\n✅ Momentum calculator ready for production use!")
