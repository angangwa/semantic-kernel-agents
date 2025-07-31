"""
Contoso Agent Factory

This module provides a centralized way to create all Contoso agents.
"""

from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from .alex_orchestrator import AlexOrchestrator
from .billing_agent import BillingAgent
from .plan_agent import PlanAgent
from .support_agent import SupportAgent

def create_contoso_agents(service: AzureChatCompletion):
    """
    Create all Contoso agents with the given service.
    
    Args:
        service: Azure OpenAI chat completion service
        
    Returns:
        Tuple of (alex, billing_agent, plan_agent, support_agent)
    """
    alex = AlexOrchestrator(service).agent
    billing_agent = BillingAgent(service).agent
    plan_agent = PlanAgent(service).agent
    support_agent = SupportAgent(service).agent
    
    return alex, billing_agent, plan_agent, support_agent

__all__ = [
    'AlexOrchestrator',
    'BillingAgent', 
    'PlanAgent',
    'SupportAgent',
    'create_contoso_agents'
]