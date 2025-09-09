"""Math Agent Plugin using Cadence SDK."""

from typing import Annotated, TypedDict

from cadence_sdk import BaseAgent, BasePlugin, PluginMetadata
from cadence_sdk.decorators import object_schema


@object_schema
class MatchResponseSchema(TypedDict):
    """Unified schema for representing heterogeneous search response entities"""

    used_operation: Annotated[
        list[str],
        ...,
        "Tracking all used operations",
    ]


class MathPlugin(BasePlugin):
    """Math Plugin Bundle using SDK interfaces."""

    @staticmethod
    def get_metadata() -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="mathematics",
            version="1.3.0",
            description="Mathematical calculations and arithmetic operations agent",
            agent_type="specialized",
            response_schema=MatchResponseSchema,
            capabilities=["addition", "subtraction", "multiplication", "division", "power", "modulo"],
            response_suggestion="When presenting mathematical results, always show the step-by-step calculation process, clearly state the operation performed and operands used, format numbers appropriately (with proper decimal places), and explain any assumptions or limitations. Use mathematical notation and clear formatting for better understanding.",
            llm_requirements={
                "provider": "openai",
                "model": "gpt-4.1",
                "temperature": 0.2,
                "max_tokens": 1024,
            },
            dependencies=["cadence-sdk>=1.3.0,<2.0.0"],
        )

    @staticmethod
    def create_agent() -> BaseAgent:
        """Create math agent instance."""
        from .agent import MathAgent

        return MathAgent(MathPlugin.get_metadata())

    @staticmethod
    def health_check() -> dict:
        """Perform health check."""
        try:
            from .tools import add, multiply, subtract

            add_func = getattr(add, "func", add)
            subtract_func = getattr(subtract, "func", subtract)
            multiply_func = getattr(multiply, "func", multiply)

            assert add_func(2, 3) == 5
            assert subtract_func(5, 3) == 2
            assert multiply_func(2, 4) == 8

            return {
                "healthy": True,
                "details": "Math plugin is operational",
                "checks": {"basic_operations": "OK", "tool_availability": "OK"},
            }
        except Exception as e:
            return {
                "healthy": False,
                "details": f"Math plugin health check failed: {e}",
                "error": str(e),
            }
