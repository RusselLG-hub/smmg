from pydantic import BaseModel


class UploadResponse(BaseModel):
    object_name: str
    url: str
