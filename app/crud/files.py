from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.session_dep import SessionDep
from app.database.models import File


async def set_file(
    filename: str,
    unique_filename: str,
    url: str,
    bucket: str,
    size: int,
    content_type: str,
    owner_id: int,
    session: SessionDep,
):
    new_file = File(
        original_filename=filename,
        stored_filename=unique_filename,
        url=url,
        bucket=bucket,
        size=size,
        content_type=content_type,
        owner_id=owner_id,
        created_at=datetime.now(),
    )
    
    session.add(new_file)
    await session.commit()
    await session.refresh(new_file)
    
    return new_file


async def get_file(file_id: int, session: SessionDep):
    return await session.scalar(select(File).where(File.id == file_id))

async def get_files_by_id(
    owner_id: int,
    session: SessionDep, 
    limit: int = 20, 
    offset: int = 0
    ):
    return await session.scalars(
        select(File)
        .options(selectinload(File.author))
        .where(File.owner_id == owner_id)
        .order_by(File.created_at.asc())
        .limit(limit)
        .offset(offset)
    )


async def delete_file(file_id: int, session: SessionDep):
    file = await get_file(file_id, session)
    
    await session.delete(file)
    await session.commit()