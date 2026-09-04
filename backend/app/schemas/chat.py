from pydantic import BaseModel

class ChatTestRequest(BaseModel):
    prompt: str

class ChatTestResponse(BaseModel):
    response: str