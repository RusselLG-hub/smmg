from fastapi import APIRouter, Depends, File, UploadFile

from app.features.v1.auth.dependencies import get_current_user
from app.features.v1.uploads import schema as upload_schema
from app.features.v1.uploads import service as upload_service
from app.features.v1.users import model as user_model

router = APIRouter(prefix="/v1/uploads", tags=["uploads"])


@router.post("/image", response_model=upload_schema.UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    current_user: user_model.User = Depends(get_current_user),
):
    return await upload_service.upload_image(file)


@router.get("/{object_path:path}")
async def get_uploaded_file(object_path: str):
    return upload_service.get_uploaded_file(object_path)

