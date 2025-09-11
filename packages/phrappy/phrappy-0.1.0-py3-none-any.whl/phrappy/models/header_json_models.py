from typing import List, Optional

from pydantic import BaseModel, Field

from .phrase_tms_api_models import UidReference, IdReference


class RateLimitsBaseModel(BaseModel):
    ratelimit_limit: Optional[int] = Field(alias="Ratelimit-Limit", default=None)
    ratelimit_remaining: Optional[int] = Field(
        alias="Ratelimit-Remaining", default=None
    )


class JobUpdateSourceMeta(BaseModel):
    jobs: List["UidReference"]
    preTranslate: bool = False
    allowAutomaticPostAnalysis: Optional[bool] = None
    callbackUrl: Optional[str] = None


class UploadHandoverFileMeta(BaseModel):
    jobs: List["UidReference"]


class JobUpdateTargetMeta(BaseModel):
    jobs: List["UidReference"] = Field(max_length=1)
    propagateConfirmedToTm: bool = False
    targetSegmentationRule: Optional["IdReference"] = None
    callbackUrl: Optional[str] = None
    unconfirmChangedSegments: Optional[bool] = True


class CreateSegmentationRuleMeta(BaseModel):
    name: str
    locale: str
    primary: bool = False
    filename: str


class UploadFileV2Meta(BaseModel):
    commitMessage: str
    subfolderName: str
    callbackUrl: Optional[str] = None
