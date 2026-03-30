"""Smart Code Review Agent - Agent Definition."""

from google.adk.agents import LlmAgent
from .prompt import AGENT_INSTRUCTIONS
from .tools import analyze_bugs, check_style, review_security, calculate_score

code_review_agent = LlmAgent(
    name="code_review_agent",
    model="gemini-2.5-flash",
    instruction=AGENT_INSTRUCTIONS,
    tools=[analyze_bugs, check_style, review_security, calculate_score],
    description="An AI agent that reviews Python code for bugs, style issues, security vulnerabilities, and provides a quality score.",
)