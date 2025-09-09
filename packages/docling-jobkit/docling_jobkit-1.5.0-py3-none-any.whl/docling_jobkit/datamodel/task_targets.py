from typing import Annotated, Literal

from pydantic import AnyHttpUrl, BaseModel, Field

from docling_jobkit.datamodel.s3_coords import S3Coordinates


class InBodyTarget(BaseModel):
    kind: Literal["inbody"] = "inbody"


class ZipTarget(BaseModel):
    kind: Literal["zip"] = "zip"


class S3Target(S3Coordinates):
    kind: Literal["s3"] = "s3"


class PutTarget(BaseModel):
    kind: Literal["put"] = "put"
    url: AnyHttpUrl


TaskTarget = Annotated[
    InBodyTarget | ZipTarget | S3Target | PutTarget, Field(discriminator="kind")
]
