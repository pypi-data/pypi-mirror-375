from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, Literal


class CodeAiraRequest(BaseModel):
    model_name: Literal[
        "gemini-2.0-flash-lite-001",
        "gemini-2.0-flash-001",
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-2.5-flash-thinking",
        "gemini-2.5-pro-thinking",
        "azure-gpt-4o",
        "azure-gpt-4o-mini",
        "azure-o3-mini-low",
        "azure-o3-mini-medium",
        "azure-o3-mini-high",
        "claude-3-5-sonnet@20240620",
        "claude-3-5-sonnet-v2@20241022",
        "claude-3-7-sonnet@20250219",
        "claude-sonnet-4@20250514",
        "claude-3-7-sonnet@20250219-thinking",
        "claude-sonnet-4@20250514-thinking"

    ] = Field(..., description="The model used for completion")
    prompt: str = Field(..., description="The prompt for text completion")
    context: Optional[str] = Field(
        None, description="Optional context for the completion")
    app_id: Optional[str] = Field(None, description="Optional application ID")


class CodeAiraResponse(BaseModel):
    completion: str = Field(..., description="The generated text completion")
    model: str = Field(..., description="The model used for completion")

    usage: Dict[str, int] = Field(..., description="Token usage information")
    finish_reason: str = Field(..., description="Reason for completion finish")
    logprobs: Optional[Any] = Field(
        None, description="Log probabilities if requested")


class DataOnlyResponse(BaseModel):
    data: str = Field(..., description="The generated text completion")


class FullCompletionResponse(BaseModel):
    # the keys are sucess : boolean, data: str, log_id: str,
    # thread_id: str, location:str, error: http error codes or none
    success: bool = Field(...,
                          description="Whether the request was successful")
    data: str = Field(..., description="The generated text completion")
    log_id: str = Field(..., description="Unique identifier for the request")
    thread_id: str = Field(..., description="Unique identifier for the thread")
    location: str = Field(..., description="Location of the response")
    error: Optional[str] = Field(
        None, description="Error message if the request failed")
