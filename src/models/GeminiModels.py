from pydantic import BaseModel


class GeminiPost(BaseModel):
    text: str
    hashtags: list[str]
    link: str
