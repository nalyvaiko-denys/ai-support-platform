from pydantic import BaseModel, ConfigDict


class LLMResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    text: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    response_time_ms: int
