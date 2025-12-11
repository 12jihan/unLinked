from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ShareCommentary(BaseModel):
    text: str = Field(default="")


class Media(BaseModel):
    status: str = "READY"
    originalUrl: str
    description: Optional[dict] = None
    title: Optional[dict] = None


class ShareContent(BaseModel):
    shareCommentary: ShareCommentary
    shareMediaCategory: str = "NONE"
    media: List[Media] = Field(default_factory=list)


class SpecificContent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    ugcShareContent: ShareContent = Field(alias="com.linkedin.ugc.ShareContent")


class Visibility(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    memberNetworkVisibility: str = Field(
        # default="CONNECTIONS", alias="com.linkedin.ugc.MemberNetworkVisibility"
        default="PUBLIC",
        alias="com.linkedin.ugc.MemberNetworkVisibility",
    )


class TextPostRequestBody(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    author: str
    lifecycleState: str = "PUBLISHED"
    specificContent: SpecificContent
    visibility: Visibility
