"""Math Agent Implementation using Cadence SDK."""

from typing import List, Union

from cadence_sdk import BaseAgent
from cadence_sdk.base.metadata import PluginMetadata
from typing_extensions import Annotated, TypedDict


class MathResultSchema(TypedDict):
    """Schema for math operation results."""

    operation: Annotated[str, "The mathematical operation performed (e.g., addition, multiplication)"]
    operands: Annotated[list[Union[int, float]], "List of numbers used in the calculation"]
    result: Annotated[Union[int, float, str], "The result of the calculation or error message"]
    success: Annotated[bool, "Whether the calculation was successful"]


class MathAgent(BaseAgent):
    """Math operations and problem-solving agent using SDK."""

    def __init__(self, metadata: PluginMetadata):
        """Initialize the math agent."""
        super().__init__(metadata)

    def get_tools(self) -> List:
        """Get available math tools."""
        from .tools import math_tools

        return math_tools

    def get_system_prompt(self) -> str:
        """Get system prompt for the math agent."""
        return (
            "You are the Math Agent, specialized in mathematical operations and calculations. "
            "You have access to tools for: addition, subtraction, multiplication, division, "
            "exponentiation (power), and modulo operations. "
            "\n\n"
            "Always use the provided tools to perform calculations rather than doing math "
            "mentally. This ensures accuracy and allows the user to see your work."
            "Do not make up the answer if it's no tools suitable for calculation. \n"
        )

    def create_math_result(
        self, operation: str, operands: list[Union[int, float]], result: Union[int, float, str]
    ) -> MathResultSchema:
        """Create a structured math result according to the schema."""
        success = not isinstance(result, str) or not result.startswith("Error:")

        return MathResultSchema(operation=operation, operands=operands, result=result, success=success)
