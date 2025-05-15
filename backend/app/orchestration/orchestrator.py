# Placeholder for orchestration logic
from typing import Dict, Any, Optional

from ..agents.personas import AgentPersona
from ..agents.base_agent import BaseAgent # Import BaseAgent
from .context_manager import context_manager # Import the global context_manager instance

# Placeholder for user/company data models - these would likely come from a database or another service
# These are already defined in the previous version, assuming they are sufficient for now.

# --- Context Collection, Persona Selection, Context Data Preparation --- #
# Functions collect_context, select_persona, prepare_context_data_for_agent 
# are assumed to be part of this module or context_manager as appropriate.
# For simplicity, let's assume context_manager.collect_full_context is the primary way to get all context.

async def select_persona_from_context(context: Dict[str, Any]) -> AgentPersona:
    """
    Selects an appropriate AgentPersona based on the collected context.
    This is a placeholder for a more sophisticated selection logic.
    """
    print(f"Orchestrator: Selecting persona based on context: {context.get('module_accessed')}, user role: {context.get('user_profile', {}).get('role')}")
    
    module = str(context.get("module_accessed", "")).lower()
    user_role = str(context.get("user_profile", {}).get("role", "")).lower()

    if "legal" in module or "compliance" in module or "juridico" in module:
        return AgentPersona.LEGAL_EXPERT
    elif "strategy" in module or "planning" in module or "estrategia" in module:
        return AgentPersona.STRATEGY_CONSULTANT
    elif "data" in module or "report" in module or "analytics" in module:
        return AgentPersona.DATA_ANALYST
    elif "content" in module or "marketing" in module or "redacao" in module:
        return AgentPersona.GROWTH_WRITER
    
    if "manager" in user_role or "director" in user_role:
        return AgentPersona.STRATEGY_CONSULTANT
        
    return AgentPersona.STRATEGY_CONSULTANT # Fallback default

async def prepare_context_for_agent(full_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formats the collected context into a dictionary suitable for the BaseAgent.
    """
    print("Orchestrator: Preparing context data for agent.")
    
    agent_context = {
        "user_role": full_context.get("user_profile", {}).get("role"),
        "user_department": full_context.get("user_profile", {}).get("department"),
        "company_sector": full_context.get("company_profile", {}).get("sector"),
        "company_stage": full_context.get("company_profile", {}).get("stage"),
        "company_strategic_goals": ", ".join(full_context.get("company_profile", {}).get("strategic_goals", [])),
        "module_accessed": full_context.get("module_accessed"),
    }
    return {k: v for k, v in agent_context.items() if v is not None}

# --- Main Orchestration Flow --- # 
async def handle_user_request(
    user_id: str, 
    company_id: str, 
    user_prompt: str, 
    module_accessed: str | None = None, 
    current_interaction_data: Dict[str, Any] | None = None
) -> str | None:
    """Orchestrates an agent response based on user request and context."""
    
    # 1. Collect full context using ContextManager
    full_context = await context_manager.collect_full_context(
        user_id=user_id, 
        company_id=company_id, 
        module_accessed=module_accessed, 
        current_interaction_data=current_interaction_data
    )
    
    # 2. Select Persona
    selected_persona_enum = await select_persona_from_context(full_context)
    
    # 3. Prepare context specifically for the agent
    agent_specific_context = await prepare_context_for_agent(full_context)
    
    # 4. Instantiate the agent
    # Here you could have a factory or registry if you have specialized agent classes
    # e.g., StrategicAgent(BaseAgent), LegalAgent(BaseAgent)
    # For now, BaseAgent is used directly with the selected persona.
    agent = BaseAgent(persona=selected_persona_enum)
    
    # 5. Get response from agent
    response = await agent.generate_response(
        user_prompt=user_prompt,
        conversation_history=full_context.get("interaction_history"),
        context_data=agent_specific_context
    )
    
    # 6. Post-process response, log interaction, update history, etc.
    if response:
        await context_manager.add_interaction_to_history(
            user_id=user_id, 
            company_id=company_id, 
            user_message=user_prompt, 
            assistant_message=response
        )
    
    return response

