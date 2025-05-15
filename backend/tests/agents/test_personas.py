import pytest

# Adjust the import path based on your project structure
from app.agents.personas import AgentPersona


def test_agent_persona_enum_values():
    assert AgentPersona.STRATEGY_CONSULTANT.value["name"] == "Strategy Consultant"
    assert "strategic advice" in AgentPersona.STRATEGY_CONSULTANT.value["description"]
    assert "You are an experienced Strategy Consultant." in AgentPersona.STRATEGY_CONSULTANT.value["system_prompt"]

    assert AgentPersona.LEGAL_EXPERT.value["name"] == "Legal Expert"
    assert "legal and regulatory queries" in AgentPersona.LEGAL_EXPERT.value["description"]
    assert "You are a knowledgeable Legal Expert." in AgentPersona.LEGAL_EXPERT.value["system_prompt"]

    assert AgentPersona.DATA_ANALYST.value["name"] == "Data Analyst"
    assert "data interpretation" in AgentPersona.DATA_ANALYST.value["description"]
    assert "You are a proficient Data Analyst." in AgentPersona.DATA_ANALYST.value["system_prompt"]

    assert AgentPersona.GROWTH_WRITER.value["name"] == "Growth Writer"
    assert "institutional content" in AgentPersona.GROWTH_WRITER.value["description"]
    assert "You are a creative Growth Writer." in AgentPersona.GROWTH_WRITER.value["system_prompt"]

def test_agent_persona_get_methods():
    persona = AgentPersona.STRATEGY_CONSULTANT
    assert persona.get_name() == "Strategy Consultant"
    assert persona.get_description() == "Provides strategic advice, market analysis, and business planning insights."
    assert persona.get_system_prompt() == "You are an experienced Strategy Consultant. Your goal is to help users make informed strategic decisions by analyzing their business context, market trends, and providing actionable recommendations. Focus on clarity, evidence-based reasoning, and long-term impact."

    persona = AgentPersona.LEGAL_EXPERT
    assert persona.get_name() == "Legal Expert"
    assert persona.get_description() == "Assists with legal and regulatory queries, document analysis, and compliance."
    assert persona.get_system_prompt() == "You are a knowledgeable Legal Expert. Your role is to provide information and analysis on legal and regulatory matters relevant to the user\'s company and industry. You do not provide legal advice, but rather information to help them understand legal concepts and compliance requirements. Always suggest consulting with a qualified legal professional for definitive advice."


@pytest.mark.parametrize("persona_member", list(AgentPersona))
def test_all_personas_have_required_fields(persona_member: AgentPersona):
    assert "name" in persona_member.value
    assert isinstance(persona_member.value["name"], str)
    assert "description" in persona_member.value
    assert isinstance(persona_member.value["description"], str)
    assert "system_prompt" in persona_member.value
    assert isinstance(persona_member.value["system_prompt"], str)

@pytest.mark.parametrize("persona_member", list(AgentPersona))
def test_all_personas_get_methods_work(persona_member: AgentPersona):
    assert persona_member.get_name() == persona_member.value["name"]
    assert persona_member.get_description() == persona_member.value["description"]
    assert persona_member.get_system_prompt() == persona_member.value["system_prompt"]

