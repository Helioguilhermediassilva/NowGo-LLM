import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock

# Adjust the import path based on your project structure
from app.orchestration.context_manager import ContextManager, context_manager as global_context_manager

@pytest_asyncio.fixture
def fresh_context_manager():
    """Provides a fresh instance of ContextManager for each test."""
    return ContextManager()

@pytest.mark.asyncio
async def test_context_manager_initialization(fresh_context_manager: ContextManager):
    assert fresh_context_manager.user_interaction_history == {}
    assert fresh_context_manager.user_profiles == {}
    assert fresh_context_manager.company_profiles == {}

@pytest.mark.asyncio
async def test_get_user_profile(fresh_context_manager: ContextManager):
    # Test with pre-populated data (as per current implementation)
    profile = await fresh_context_manager.get_user_profile("user123")
    assert profile is not None
    assert profile["role"] == "Manager"

    profile_non_existent = await fresh_context_manager.get_user_profile("non_existent_user")
    assert profile_non_existent is None

@pytest.mark.asyncio
async def test_get_company_profile(fresh_context_manager: ContextManager):
    # Test with pre-populated data
    profile = await fresh_context_manager.get_company_profile("comp456")
    assert profile is not None
    assert profile["sector"] == "Technology"

    profile_non_existent = await fresh_context_manager.get_company_profile("non_existent_comp")
    assert profile_non_existent is None

@pytest.mark.asyncio
async def test_interaction_history_empty(fresh_context_manager: ContextManager):
    history = await fresh_context_manager.get_interaction_history("user1", "comp1")
    assert history == []

@pytest.mark.asyncio
async def test_add_and_get_interaction_history(fresh_context_manager: ContextManager):
    user_id = "user_test_hist"
    company_id = "comp_test_hist"
    await fresh_context_manager.add_interaction_to_history(user_id, company_id, "Hello", "Hi there!") # Interaction 1 (2 messages)
    await fresh_context_manager.add_interaction_to_history(user_id, company_id, "How are you?", "I am fine.") # Interaction 2 (2 messages)
    # Total messages in history_key: 4

    # Test with default limit (limit=3 in implementation)
    history_default_limit = await fresh_context_manager.get_interaction_history(user_id, company_id)
    assert len(history_default_limit) == 3 
    # Expected: last 3 messages -> [assistant1, user2, assistant2]
    # assistant1: "Hi there!"
    # user2: "How are you?"
    # assistant2: "I am fine."
    assert history_default_limit[0] == {"role": "assistant", "content": "Hi there!"} # This was the second message added overall
    assert history_default_limit[1] == {"role": "user", "content": "How are you?"}
    assert history_default_limit[2] == {"role": "assistant", "content": "I am fine."}

    # Test with explicit limit=4 to get all messages
    history_all = await fresh_context_manager.get_interaction_history(user_id, company_id, limit=4)
    assert len(history_all) == 4
    assert history_all[0] == {"role": "user", "content": "Hello"}
    assert history_all[1] == {"role": "assistant", "content": "Hi there!"}
    assert history_all[2] == {"role": "user", "content": "How are you?"}
    assert history_all[3] == {"role": "assistant", "content": "I am fine."}

    # Test limit=1 (last 1 message)
    history_limited_1 = await fresh_context_manager.get_interaction_history(user_id, company_id, limit=1)
    assert len(history_limited_1) == 1
    assert history_limited_1[0] == {"role": "assistant", "content": "I am fine."} # The very last message
    
    # Test limit=2 (last 2 messages)
    history_limited_2 = await fresh_context_manager.get_interaction_history(user_id, company_id, limit=2)
    assert len(history_limited_2) == 2
    assert history_limited_2[0] == {"role": "user", "content": "How are you?"} # Second to last message
    assert history_limited_2[1] == {"role": "assistant", "content": "I am fine."} # Last message

    await fresh_context_manager.add_interaction_to_history(user_id, company_id, "Third q", "Third a")
    # Now history has 6 messages
    history_limit_3_after_add = await fresh_context_manager.get_interaction_history(user_id, company_id, limit=3)
    assert len(history_limit_3_after_add) == 3
    # Last 3 messages: [user2_msg, assistant2_msg, user3_msg, assistant3_msg] -> [assistant2, user3, assistant3]
    assert history_limit_3_after_add[0] == {"role": "assistant", "content": "I am fine."}
    assert history_limit_3_after_add[1] == {"role": "user", "content": "Third q"}
    assert history_limit_3_after_add[2] == {"role": "assistant", "content": "Third a"}

@pytest.mark.asyncio
async def test_collect_full_context_known_user_company(fresh_context_manager: ContextManager):
    user_id = "user123"
    company_id = "comp456"
    module = "test_module"

    # Add one interaction (Q1/A1) -> 2 messages
    await fresh_context_manager.add_interaction_to_history(user_id, company_id, "Q1", "A1")

    full_context = await fresh_context_manager.collect_full_context(user_id, company_id, module_accessed=module)

    assert full_context["user_profile"]["user_id"] == user_id
    assert full_context["user_profile"]["role"] == "Manager"
    assert full_context["company_profile"]["company_id"] == company_id
    assert full_context["company_profile"]["sector"] == "Technology"
    assert full_context["module_accessed"] == module
    # Default limit for get_interaction_history in collect_full_context is 3.
    # We added 2 messages. So it should return all 2.
    assert len(full_context["interaction_history"]) == 2 
    assert full_context["interaction_history"][0]["content"] == "Q1"
    assert full_context["interaction_history"][1]["content"] == "A1"

@pytest.mark.asyncio
async def test_collect_full_context_unknown_user_company(fresh_context_manager: ContextManager):
    user_id = "unknown_user"
    company_id = "unknown_comp"

    full_context = await fresh_context_manager.collect_full_context(user_id, company_id)

    assert full_context["user_profile"]["role"] == "Unknown"
    assert full_context["company_profile"]["sector"] == "Unknown"
    assert full_context["interaction_history"] == []

# Test the global instance if it's used elsewhere, though testing fresh instances is generally better.
@pytest.mark.asyncio
async def test_global_context_manager_instance():
    assert global_context_manager is not None
    # Simple check, assuming it's a ContextManager instance
    assert hasattr(global_context_manager, "collect_full_context")

