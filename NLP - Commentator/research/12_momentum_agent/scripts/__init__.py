"""
Momentum Agent Package
======================
Agent for integrating momentum data into GENERAL commentary.

IMPORTANT: Works ONLY for General commentary - integrates, doesn't replace!

Three agent options:
1. MomentumAgent - Pure rule-based (fast, free, deterministic)
2. HybridMomentumAgent - 3-layer system (hard rules + soft rules + LLM)
3. ExploratoryMomentumAgent - Full freedom LLM agent (RECOMMENDED)

Usage:
    # Exploratory (recommended) - full freedom to discover patterns
    from exploratory_momentum_agent import ExploratoryMomentumAgent
    agent = ExploratoryMomentumAgent(api_key="sk-...")
    
    # Pass recent events for context
    events = [
        {'minute': 39, 'team': 'Germany', 'event_type': 'Shot', 'detail': 'Saved'},
        {'minute': 38, 'team': 'Scotland', 'event_type': 'Foul', 'detail': ''},
    ]
    
    result = agent.explore(
        match_id=3930158, 
        minute=40, 
        period=1,
        score_home=3, 
        score_away=0,
        recent_events=events
    )
    
    if result['interesting']:
        # ADD this phrase to General commentary
        print(result['phrase'])

Author: Euro 2024 Momentum Project
Date: December 2024
"""

from .momentum_data_loader import MomentumDataLoader
from .momentum_agent import MomentumAgent
from .hybrid_momentum_agent import HybridMomentumAgent
from .exploratory_momentum_agent import ExploratoryMomentumAgent

__all__ = [
    'MomentumDataLoader', 
    'MomentumAgent', 
    'HybridMomentumAgent',
    'ExploratoryMomentumAgent'
]
__version__ = '1.1.0'

