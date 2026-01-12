from pydantic import BaseModel


class GeminiPost(BaseModel):
    text: str
    hashtags: list[str]
    link: str


class ModelPrep(BaseModel):
    title: str
    link: str
    summary: str


class ModelCook(BaseModel):
    title: str
    link: str
    summary: str
    text: str


class ModelServe(BaseModel):
    title: str
    link: str
    summary: str
    text: str


class ModelDigest(BaseModel):
    title: str
    link: str
    hashtags: list[str]
    text: str
