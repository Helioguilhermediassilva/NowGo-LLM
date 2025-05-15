import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock

# Adjust the import path based on your project structure
from app.agents.base_agent import BaseAgent
from app.agents.personas import AgentPersona

@pytest_asyncio.fixture
def mock_get_chat_completion():
    # This mock will be patched into app.agents.base_agent.get_chat_completion
    with patch("app.agents.base_agent.get_chat_completion", new_callable=AsyncMock) as mock_func:
        yield mock_func

@pytest.mark.asyncio
async def test_base_agent_initialization():
    persona = AgentPersona.STRATEGY_CONSULTANT
    agent = BaseAgent(persona=persona)
    assert agent.persona == persona

@pytest.mark.asyncio
async def test_base_agent_generate_response_simple_prompt(mock_get_chat_completion):
    persona = AgentPersona.STRATEGY_CONSULTANT
    agent = BaseAgent(persona=persona)
    user_prompt = "What is a SWOT analysis?"
    expected_response_content = "A SWOT analysis is a strategic planning technique."

    mock_get_chat_completion.return_value = expected_response_content

    response = await agent.generate_response(user_prompt)

    assert response == expected_response_content
    
    # Verify the call to the mocked get_chat_completion
    # It is called with prompt=messages_for_llm and model=persona.get_llm_model_name()
    called_args, called_kwargs = mock_get_chat_completion.call_args
    
    expected_messages_for_llm = [
        {"role": "system", "content": persona.get_system_prompt()},
        {"role": "user", "content": f"Relevant context for this interaction:\n\nUser query: {user_prompt}"}
    ]
    
    assert called_kwargs["prompt"] == expected_messages_for_llm
    assert called_kwargs["model"] == persona.get_llm_model_name()

@pytest.mark.asyncio
async def test_base_agent_generate_response_with_history(mock_get_chat_completion):
    persona = AgentPersona.DATA_ANALYST
    agent = BaseAgent(persona=persona)
    user_prompt = "Based on this, what next?"
    conversation_history = [
        {"role": "user", "content": "Here is the sales data for Q1."},
        {"role": "assistant", "content": "Q1 sales show a 10% increase."}
    ]
    expected_response_content = "Next, we should analyze Q2 projections."

    mock_get_chat_completion.return_value = expected_response_content

    response = await agent.generate_response(user_prompt, conversation_history=conversation_history)

    assert response == expected_response_content
    
    called_args, called_kwargs = mock_get_chat_completion.call_args
    expected_messages_for_llm = [
        {"role": "system", "content": persona.get_system_prompt()}
    ]
    expected_messages_for_llm.extend(conversation_history)
    expected_messages_for_llm.append(
        {"role": "user", "content": f"Relevant context for this interaction:\n\nUser query: {user_prompt}"}
    )
    
    assert called_kwargs["prompt"] == expected_messages_for_llm
    assert called_kwargs["model"] == persona.get_llm_model_name()

@pytest.mark.asyncio
async def test_base_agent_generate_response_with_context_data(mock_get_chat_completion):
    persona = AgentPersona.LEGAL_EXPERT
    agent = BaseAgent(persona=persona)
    user_prompt = "Is this compliant?"
    context_data = {
        "company_sector": "Healthcare",
        "document_type": "NDA",
        "relevant_regulation": "HIPAA"
    }
    expected_response_content = "Based on HIPAA, this NDA needs a specific clause..."

    mock_get_chat_completion.return_value = expected_response_content

    response = await agent.generate_response(user_prompt, context_data=context_data)

    assert response == expected_response_content

    called_args, called_kwargs = mock_get_chat_completion.call_args
    user_message_content_in_llm_prompt = called_kwargs["prompt"][-1]["content"]
    
    assert "Relevant context for this interaction:" in user_message_content_in_llm_prompt
    assert "Company sector: Healthcare" in user_message_content_in_llm_prompt
    assert "Document type: NDA" in user_message_content_in_llm_prompt
    assert "Relevant regulation: HIPAA" in user_message_content_in_llm_prompt
    assert f"User query: {user_prompt}" in user_message_content_in_llm_prompt
    assert called_kwargs["model"] == persona.get_llm_model_name()

@pytest.mark.asyncio
async def test_base_agent_generate_response_openai_call_fails(mock_get_chat_completion):
    persona = AgentPersona.STRATEGY_CONSULTANT
    agent = BaseAgent(persona=persona)
    user_prompt = "This will fail."

    mock_get_chat_completion.return_value = None # Simulate failure

    response = await agent.generate_response(user_prompt)

    assert response is None
    mock_get_chat_completion.assert_called_once()

@pytest.mark.asyncio
async def test_base_agent_generate_response_with_empty_context_and_history(mock_get_chat_completion):
    persona = AgentPersona.GROWTH_WRITER
    agent = BaseAgent(persona=persona)
    user_prompt = "Write a blog post title about AI in marketing."
    expected_response_content = "AI-Powered Marketing: The Future is Now"

    mock_get_chat_completion.return_value = expected_response_content

    response = await agent.generate_response(user_prompt, conversation_history=[], context_data={})

    assert response == expected_response_content
    
    called_args, called_kwargs = mock_get_chat_completion.call_args
    user_message_content_in_llm_prompt = called_kwargs["prompt"][-1]["content"]

    # Check that the user prompt is not unnecessarily cluttered if context is empty
    # The current implementation of BaseAgent still adds "Relevant context... User query:"
    # but the formatted_context_data_str will be empty if context_data is empty.
    expected_user_message = f"Relevant context for this interaction:\n\nUser query: {user_prompt}"
    assert user_message_content_in_llm_prompt == expected_user_message
    assert called_kwargs["model"] == persona.get_llm_model_name()

