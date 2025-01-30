from pydantic import BaseModel


class AskAgent(BaseModel):
    prompt: str
    user_email: str | None = None
    user_id: str | None = None


class GoogleLogin(BaseModel):
    email: str