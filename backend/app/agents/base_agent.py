from typing import Dict, Any, Optional, List
from ..core.openai_client import get_chat_completion
from .personas import AgentPersona

class BaseAgent:
    def __init__(self, persona: AgentPersona):
        self.persona = persona

    async def generate_response(
        self,
        user_prompt: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        context_data: Optional[Dict[str, Any]] = None
    ) -> str | None:
        """
        Generates a response using the assigned persona, user prompt, history, and context.
        """
        system_message = {"role": "system", "content": self.persona.get_system_prompt()}
        
        messages_for_llm: List[Dict[str, str]] = [system_message]

        if conversation_history:
            messages_for_llm.extend(conversation_history)

        formatted_context_data_str = ""
        if context_data: # context_data is not None and not empty
            parts = []
            for k, v in context_data.items():
                if v is not None: # Ensure value is not None before formatting
                    parts.append(f"{k.replace('_', ' ').capitalize()}: {v}")
            if parts:
                 formatted_context_data_str = "\n" + "\n".join(parts) # Add leading newline only if there are parts

        # Consistent preamble for the user message, context_data_str might be empty
        user_message_with_context = f"Relevant context for this interaction:{formatted_context_data_str}\n\nUser query: {user_prompt}"
        
        messages_for_llm.append({
            "role": "user", 
            "content": user_message_with_context
        })

        # Call the (potentially mocked) get_chat_completion
        # The get_chat_completion function expects the full list of messages as its first argument (prompt)
        response_content = await get_chat_completion(
            prompt=messages_for_llm, 
            model=self.persona.get_llm_model_name() # Assuming persona has this method
        )
        
        return response_content

