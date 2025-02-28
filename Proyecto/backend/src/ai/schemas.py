"""
Schemas module for the Naurat Importation Bot API.

This module defines Pydantic models used for request validation and data serialization.

Features:
- Defines input data structures for API endpoints.
- Ensures data integrity and validation using Pydantic.
"""

from pydantic import BaseModel


class AskAgent(BaseModel):
    """
    Schema for handling user queries to the AI agent.

    Attributes:
        prompt (str): The user's input message or question for the AI.
        user_email (str | None): Optional email of the user making the request.
        user_id (str | None): Optional unique identifier of the user.
    """

    prompt: str
    user_email: str | None = None
    user_id: str | None = None


class GoogleLogin(BaseModel):
    """
    Schema for handling Google login requests.

    Attributes:
        email (str): The user's Google account email address.
    """

    email: str
