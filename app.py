"""HTTP server wrapping the Smart Code Review Agent."""

import os
import asyncio
import requests as http_requests

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from code_review_agent.agent import code_review_agent

# Load environment variables
load_dotenv("code_review_agent/.env")

# --- FastAPI App ---
app = FastAPI(
    title="Smart Code Review Agent",
    description="An ADK-powered Python code review agent",
    version="1.0.0",
)

# --- ADK Runner Setup ---
session_service = InMemorySessionService()
runner = Runner(
    agent=code_review_agent,
    app_name="code_review_agent",
    session_service=session_service,
)

# --- Request / Response Models ---
class ReviewRequest(BaseModel):
    """Input model for code review requests."""
    code: Optional[str] = Field(None, description="Raw Python code to review")
    url: Optional[str] = Field(None, description="GitHub raw URL or Gist link to fetch code from")

class ReviewResponse(BaseModel):
    """Output model for code review results."""
    status: str
    review: Optional[str] = None
    error: Optional[str] = None


# --- Helper Functions ---
def fetch_code_from_url(url: str) -> str:
    """Fetch Python code from a GitHub raw URL or Gist link.

    Args:
        url: A URL pointing to raw Python code.

    Returns:
        The Python source code as a string.

    Raises:
        HTTPException: If the URL is unreachable or doesn't return valid content.
    """
    try:
        response = http_requests.get(url, timeout=10)
        response.raise_for_status()

        content_type = response.headers.get("content-type", "")
        if "html" in content_type and "raw" not in url:
            raise HTTPException(
                status_code=400,
                detail="URL appears to be an HTML page, not raw code. Use a raw GitHub URL (e.g., https://raw.githubusercontent.com/...).",
            )

        return response.text

    except http_requests.exceptions.Timeout:
        raise HTTPException(status_code=408, detail="Timeout fetching code from URL.")
    except http_requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch code from URL: {str(e)}")


def validate_input(request: ReviewRequest) -> str:
    """Validate the review request and extract the code.

    Args:
        request: The incoming review request.

    Returns:
        The Python code to review.

    Raises:
        HTTPException: If input is invalid.
    """
    if not request.code and not request.url:
        raise HTTPException(
            status_code=400,
            detail="Either 'code' or 'url' must be provided.",
        )

    if request.code and request.url:
        raise HTTPException(
            status_code=400,
            detail="Provide either 'code' or 'url', not both.",
        )

    if request.url:
        code = fetch_code_from_url(request.url)
    else:
        code = request.code

    # Basic validation
    if not code or not code.strip():
        raise HTTPException(status_code=400, detail="Code is empty.")

    if len(code.splitlines()) > 5000:
        raise HTTPException(
            status_code=400,
            detail="Code exceeds maximum length of 5000 lines.",
        )

    return code


async def run_agent(code: str) -> str:
    """Run the ADK agent on the provided code.

    Args:
        code: Python source code to review.

    Returns:
        The agent's review response as a string.
    """
    session = await session_service.create_session(
        app_name="code_review_agent",
        user_id="api_user",
    )

    from google.genai import types

    user_message = types.Content(
        role="user",
        parts=[types.Part.from_text(text=f"Review this Python code:\n\n{code}")],
    )

    final_response = ""
    async for event in runner.run_async(
        user_id="api_user",
        session_id=session.id,
        new_message=user_message,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_response = event.content.parts[0].text

    return final_response


# --- Endpoints ---
@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run."""
    return {"status": "healthy", "agent": "code_review_agent"}


@app.post("/review", response_model=ReviewResponse)
async def review_code(request: ReviewRequest):
    """Submit Python code for review.

    Accepts either raw code or a GitHub URL pointing to a Python file.
    Returns a structured code review with findings and a quality score.
    """
    try:
        code = validate_input(request)
        review = await run_agent(code)

        return ReviewResponse(status="success", review=review)

    except HTTPException:
        raise
    except Exception as e:
        return ReviewResponse(status="error", error=f"Agent error: {str(e)}")


# --- Entry Point ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)