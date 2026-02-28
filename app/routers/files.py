from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.core.session_dep import SessionDep
from app.crud.files import get_file, get_files_by_id
from app.dependencies.auth import CurrentUserDep
from app.dependencies.rate_limit import RateLimitDep
from app.schemas.files import FileResponse
from app.services.storage_s3_selectel import s3_client


router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/uploads", response_model=FileResponse)
async def upload_f(
    file: UploadFile, 
    currentUser: CurrentUserDep, 
    session: SessionDep, 
    _: RateLimitDep
    ):
    
    if file.size > 5 * 1024 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 5GB limit")
    
    result_file = await s3_client.upload_file(file, currentUser.id, session)
    
    return result_file


@router.get("/all", response_model=list[FileResponse])
async def get_all_user_files(
    currentUser: CurrentUserDep, 
    session: SessionDep, 
    _: RateLimitDep,
    limit: int = 20, 
    offset: int = 0,
    ):
    files = await get_files_by_id(
        currentUser.id,
        session,
        limit,
        offset
        )
    
    return files


@router.delete("/{file_id}")
async def delete_f(
    file_id: int, 
    currentUser: CurrentUserDep, 
    session: SessionDep,
    _: RateLimitDep
    ):
    
    del_file = await get_file(file_id, session)
    
    if not del_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if del_file.owner_id != currentUser.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    await s3_client.delete_file(file_id, del_file.stored_filename, session)
    
    return {"detail": "File deleted successfully"}


@router.get("/{file_id}")
async def get_meta_data(
    file_id: int, 
    currentUser: CurrentUserDep, 
    session: SessionDep,
    _: RateLimitDep
    ):
    
    file = await get_file(file_id, session)
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if file.owner_id != currentUser.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    meta_data = {
        "file_id": file.id,
        "owner_id": file.owner_id,
        "original_filename": file.original_filename,
        "stored_filename": file.stored_filename,
        "url": file.url,
        "bucket": file.bucket,
        "size": file.size,
        "content_type": file.content_type,
        "created_at": file.created_at
    }
    
    return meta_data


@router.get("/{file_id}/download")
async def download_file(
    file_id: int, 
    currentUser: CurrentUserDep, 
    session: SessionDep, 
    _: RateLimitDep
    ):
    
    file = await get_file(file_id, session)
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if file.owner_id != currentUser.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    stream = s3_client.download_file(file.stored_filename)
    
    headers = {
        "Content-Disposition": f"attachment; filename={file.original_filename}",
    }
    
    if file.size is not None:
        headers["Content-Length"] = str(file.size)
    
    return StreamingResponse(
        stream,
        media_type=file.content_type,
        headers=headers
    )