"""Orchestrator service for LangGraph coordination.

Provides high-level wrapper around AgentCoordinator for application service integration,
handling LangGraph state management and response processing.
"""

import time
from typing import Any, Dict, List, Optional

from cadence_sdk.base.loggable import Loggable
from cadence_sdk.types.state import AgentState, PluginContextFields, StateHelpers
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from ...domain.models.conversation import Conversation
from ..orchestrator.coordinator import AgentCoordinator


class OrchestratorResponse(Loggable):
    """Response container for orchestrator processing results.

    Encapsulates information generated during multi-agent conversation processing,
    including response content, performance metrics, and routing information.
    """

    def __init__(
        self,
        response: str,
        input_tokens: int,
        output_tokens: int,
        agent_hops: int = 0,
        processing_time: float = 0.0,
        tools_used: Optional[List[str]] = None,
        routing_history: Optional[List[str]] = None,
        error: Optional[str] = None,
    ):
        super().__init__()
        self.response = response
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.agent_hops = agent_hops
        self.processing_time = processing_time
        self.tools_used = tools_used or []
        self.routing_history = routing_history or []
        self.error = error

    @property
    def total_tokens(self) -> int:
        """Total tokens used."""
        return self.input_tokens + self.output_tokens

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "response": self.response,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            AgentStateFields.AGENT_HOPS: self.agent_hops,
            "processing_time": self.processing_time,
            PluginContextFields.TOOLS_USED: self.tools_used,
            PluginContextFields.ROUTING_HISTORY: self.routing_history,
            "error": self.error,
        }


class OrchestratorService(Loggable):
    """Service wrapper for LangGraph orchestration.

    Provides clean interfaces for context preparation, orchestrator execution,
    response extraction, and error handling.
    """

    def __init__(self, orchestrator: AgentCoordinator):
        self.orchestrator = orchestrator

    async def process_with_context(
        self,
        thread_id: str,
        message: str,
        conversation_history: List[Conversation],
        user_id: str = "anonymous",
        org_id: str = "public",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> OrchestratorResponse:
        """Process message with conversation context."""
        start_time = time.time()

        try:
            langgraph_context = self._prepare_context(conversation_history, message)

            state: AgentState = {
                AgentStateFields.MESSAGES: langgraph_context,
                AgentStateFields.AGENT_HOPS: 0,
                AgentStateFields.THREAD_ID: thread_id,
                AgentStateFields.PLUGIN_CONTEXT: StateHelpers.get_plugin_context({}),
                "configurable": {
                    AgentStateFields.THREAD_ID: thread_id,
                    "user_id": user_id,
                    "organization_id": org_id,
                    "checkpoint_ns": f"org_{org_id}/user_{user_id}",
                    **(metadata or {}),
                },
            }

            context_message_count = len(langgraph_context)
            self.logger.debug(
                f"Processing message for thread {thread_id} with {context_message_count} context messages"
            )
            result = await self.orchestrator.ask(state)

            response_text = self._extract_response_text(result)
            processing_time = time.time() - start_time

            input_tokens = self._estimate_input_tokens(langgraph_context)
            output_tokens = self._estimate_output_tokens(response_text)

            routing_history = result.get(AgentStateFields.PLUGIN_CONTEXT, {}).get(
                PluginContextFields.ROUTING_HISTORY, []
            )
            tools_used = self._extract_tools_used(result)

            response_preview = response_text[:100]
            self.logger.info(f"Orchestrator completed for thread {thread_id}: {response_preview}...")

            return OrchestratorResponse(
                response=response_text,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                agent_hops=result.get(AgentStateFields.AGENT_HOPS, 0),
                processing_time=processing_time,
                tools_used=tools_used,
                routing_history=routing_history,
            )

        except Exception as e:
            processing_time = time.time() - start_time
            error_message = f"Orchestrator error: {str(e)}"

            self.logger.error(f"Orchestrator failed for thread {thread_id}: {error_message}")

            return OrchestratorResponse(
                response=f"I encountered an error processing your request: {str(e)}",
                input_tokens=self._estimate_tokens(message),
                output_tokens=50,
                processing_time=processing_time,
                error=error_message,
            )

    def _prepare_context(self, history: List[Conversation], current_message: str) -> List[BaseMessage]:
        """Prepare LangGraph message context from conversation history."""
        messages = []

        for turn in history:
            messages.extend(turn.to_langgraph_messages())

        messages.append(HumanMessage(content=current_message))

        stored_turns_count = len(history)
        message_count = len(messages)
        self.logger.debug(f"Prepared context: {message_count} messages from {stored_turns_count} stored turns")
        return messages

    @staticmethod
    def _extract_response_text(orchestrator_result: Dict[str, Any]) -> str:
        """Extract final response text from orchestrator result."""
        messages = orchestrator_result.get(AgentStateFields.MESSAGES, [])

        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and getattr(msg, "content", None):
                return msg.content

        return "No response generated"

    @staticmethod
    def _extract_tools_used(orchestrator_result: Dict[str, Any]) -> List[str]:
        """Extract list of tools used during processing."""
        routing_history = orchestrator_result.get(AgentStateFields.PLUGIN_CONTEXT, {}).get(
            PluginContextFields.ROUTING_HISTORY, []
        )
        return list(set(routing_history)) if routing_history else []

    @staticmethod
    def _estimate_input_tokens(messages: List[BaseMessage]) -> int:
        """Estimate input tokens from message context.

        Calculates token count by summing character lengths and dividing by four.
        """
        total_chars = sum(len(msg.content) for msg in messages if hasattr(msg, "content"))
        return max(1, total_chars // 4)

    @staticmethod
    def _estimate_output_tokens(response: str) -> int:
        """Estimate output tokens from response using character-length heuristic."""
        return max(1, len(response) // 4)

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Simple token estimation for fallback error paths."""
        return max(1, len(text) // 4)

    async def process_simple_message(
        self, message: str, thread_id: str = "temp_session", user_id: str = "anonymous", org_id: str = "public"
    ) -> OrchestratorResponse:
        """Process a simple message without conversation history.

        Useful for testing or stateless interactions.
        """
        return await self.process_with_context(
            thread_id=thread_id, message=message, conversation_history=[], user_id=user_id, org_id=org_id
        )

    def get_orchestrator_info(self) -> Dict[str, Any]:
        """Get information about the orchestrator configuration."""
        try:
            plugin_info = self.orchestrator.plugin_manager.get_plugin_routing_info()
            available_plugins = self.orchestrator.plugin_manager.get_available_plugins()

            return {
                "available_plugins": available_plugins,
                "plugin_info": plugin_info,
                "healthy_plugins": list(self.orchestrator.plugin_manager.healthy_plugins),
                "failed_plugins": list(self.orchestrator.plugin_manager.failed_plugins),
                "max_agent_hops": self.orchestrator.settings.max_agent_hops,
                "graph_recursion_limit": self.orchestrator.settings.graph_recursion_limit,
            }
        except Exception as e:
            self.logger.warning(f"Error getting orchestrator info: {e}")
            return {"error": str(e), "available_plugins": [], "healthy_plugins": [], "failed_plugins": []}

    async def health_check(self) -> Dict[str, Any]:
        """Perform orchestrator health check."""
        try:
            start_time = time.time()
            test_response = await self.process_simple_message("Health check test")
            response_time = time.time() - start_time

            return {
                "status": "healthy" if test_response.error is None else "unhealthy",
                "response_time": response_time,
                "error": test_response.error,
                "orchestrator_info": self.get_orchestrator_info(),
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e), "response_time": None}
