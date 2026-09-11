from pydantic import BaseModel, Field, field_validator

class ChatTestRequest(BaseModel):
    prompt: str = Field(description="The user's analytics question.")

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, value: str) -> str:
        prompt = value.strip()
        if not prompt:
            raise ValueError("Prompt must not be empty.")
        if len(prompt) > 4_000:
            raise ValueError("Prompt must be 4,000 characters or fewer.")
        return prompt

class ChatTestResponse(BaseModel):
    response: str
