import typing_extensions as typing


class GeminiPost(typing.TypedDict):
    Date: str | None
    PostText: str
    HashTags: list[str]
    Link: str
