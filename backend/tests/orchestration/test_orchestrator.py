import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock

# Adjust the import path based on your project structure
from app.orchestration.orchestrator import (
    select_persona_from_context,
    prepare_context_for_agent,
    handle_user_request
)
from app.agents.personas import AgentPersona
from app.agents.base_agent import BaseAgent # Needed for mocking its instantiation and methods

# Mock data for context
@pytest.fixture
def sample_user_profile_manager():
    return {"user_id": "user123", "role": "Manager", "department": "Sales"}

@pytest.fixture
def sample_company_profile_tech():
    return {"company_id": "comp456", "sector": "Technology", "stage": "Growth", "strategic_goals": ["Expand market share"]}

@pytest.fixture
def sample_full_context(sample_user_profile_manager, sample_company_profile_tech):
    return {
        "user_profile": sample_user_profile_manager,
        "company_profile": sample_company_profile_tech,
        "module_accessed": "strategy_dashboard",
        "current_interaction_data": {},
        "interaction_history": []
    }

@pytest.mark.asyncio
async def test_select_persona_from_context_strategy(sample_full_context):
    sample_full_context["module_accessed"] = "strategy_module"
    persona = await select_persona_from_context(sample_full_context)
    assert persona == AgentPersona.STRATEGY_CONSULTANT

@pytest.mark.asyncio
async def test_select_persona_from_context_legal(sample_full_context):
    sample_full_context["module_accessed"] = "legal_documents"
    persona = await select_persona_from_context(sample_full_context)
    assert persona == AgentPersona.LEGAL_EXPERT

@pytest.mark.asyncio
async def test_select_persona_from_context_data(sample_full_context):
    sample_full_context["module_accessed"] = "analytics_report"
    persona = await select_persona_from_context(sample_full_context)
    assert persona == AgentPersona.DATA_ANALYST

@pytest.mark.asyncio
async def test_select_persona_from_context_growth(sample_full_context):
    sample_full_context["module_accessed"] = "marketing_content_creation"
    persona = await select_persona_from_context(sample_full_context)
    assert persona == AgentPersona.GROWTH_WRITER

@pytest.mark.asyncio
async def test_select_persona_from_context_default_for_manager(sample_full_context):
    sample_full_context["module_accessed"] = "unknown_module"
    sample_full_context["user_profile"]["role"] = "Manager"
    persona = await select_persona_from_context(sample_full_context)
    assert persona == AgentPersona.STRATEGY_CONSULTANT

@pytest.mark.asyncio
async def test_select_persona_from_context_fallback_default(sample_full_context):
    sample_full_context["module_accessed"] = "unknown_module"
    sample_full_context["user_profile"]["role"] = "Intern"
    persona = await select_persona_from_context(sample_full_context)
    assert persona == AgentPersona.STRATEGY_CONSULTANT # Current fallback

@pytest.mark.asyncio
async def test_prepare_context_for_agent(sample_full_context):
    agent_context = await prepare_context_for_agent(sample_full_context)
    assert agent_context["user_role"] == "Manager"
    assert agent_context["company_sector"] == "Technology"
    assert agent_context["module_accessed"] == "strategy_dashboard"
    assert "Expand market share" in agent_context["company_strategic_goals"]
    assert agent_context.get("user_id") is None # Ensure only relevant fields are passed

@pytest.mark.asyncio
@patch("app.orchestration.orchestrator.context_manager.collect_full_context", new_callable=AsyncMock)
@patch("app.orchestration.orchestrator.select_persona_from_context", new_callable=AsyncMock)
@patch("app.orchestration.orchestrator.prepare_context_for_agent", new_callable=AsyncMock)
@patch("app.orchestration.orchestrator.BaseAgent", new_callable=MagicMock) # Mock the BaseAgent class
@patch("app.orchestration.orchestrator.context_manager.add_interaction_to_history", new_callable=AsyncMock)
async def test_handle_user_request_success(
    mock_add_history,
    MockBaseAgent,
    mock_prepare_context,
    mock_select_persona,
    mock_collect_context,
    sample_full_context
):
    user_id = "user123"
    company_id = "comp456"
    user_prompt = "Tell me about market expansion."
    module_accessed = "strategy"

    mock_collect_context.return_value = sample_full_context
    mock_select_persona.return_value = AgentPersona.STRATEGY_CONSULTANT
    mock_prepared_agent_context = {"user_role": "Manager", "company_sector": "Technology"}
    mock_prepare_context.return_value = mock_prepared_agent_context
    
    mock_agent_instance = AsyncMock(spec=BaseAgent) # Create an AsyncMock instance based on BaseAgent spec
    mock_agent_instance.generate_response = AsyncMock(return_value="Market expansion is key.")
    MockBaseAgent.return_value = mock_agent_instance # When BaseAgent is called, return our mock_agent_instance

    response = await handle_user_request(user_id, company_id, user_prompt, module_accessed)

    assert response == "Market expansion is key."
    mock_collect_context.assert_called_once_with(user_id=user_id, company_id=company_id, module_accessed=module_accessed, current_interaction_data=None)
    mock_select_persona.assert_called_once_with(sample_full_context)
    mock_prepare_context.assert_called_once_with(sample_full_context)
    MockBaseAgent.assert_called_once_with(persona=AgentPersona.STRATEGY_CONSULTANT)
    mock_agent_instance.generate_response.assert_called_once_with(
        user_prompt=user_prompt,
        conversation_history=sample_full_context.get("interaction_history"),
        context_data=mock_prepared_agent_context
    )
    mock_add_history.assert_called_once_with(user_id=user_id, company_id=company_id, user_message=user_prompt, assistant_message="Market expansion is key.")

@pytest.mark.asyncio
@patch("app.orchestration.orchestrator.context_manager.collect_full_context", new_callable=AsyncMock)
@patch("app.orchestration.orchestrator.BaseAgent", new_callable=MagicMock)
async def test_handle_user_request_agent_fails(
    MockBaseAgent, 
    mock_collect_context, 
    sample_full_context
):
    user_id = "user123"
    company_id = "comp456"
    user_prompt = "This will fail."

    mock_collect_context.return_value = sample_full_context # Assume context collection and persona selection work
    
    # Simulate agent failing to generate a response
    mock_agent_instance = AsyncMock(spec=BaseAgent)
    mock_agent_instance.generate_response = AsyncMock(return_value=None)
    MockBaseAgent.return_value = mock_agent_instance

    # We also need to mock select_persona and prepare_context for the flow to reach agent instantiation
    with patch("app.orchestration.orchestrator.select_persona_from_context", AsyncMock(return_value=AgentPersona.STRATEGY_CONSULTANT)), \
         patch("app.orchestration.orchestrator.prepare_context_for_agent", AsyncMock(return_value={})):
        response = await handle_user_request(user_id, company_id, user_prompt)
        assert response is None

