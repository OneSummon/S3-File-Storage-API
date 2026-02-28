from typing import AsyncIterator
import uuid
from pathlib import Path
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from aiobotocore.session import get_session
from fastapi import HTTPException, UploadFile

from app.core.session_dep import SessionDep
from app.crud.files import delete_file, set_file

load_dotenv()

class S3client:
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        endpoint_url: str,
        bucket_name: str,
    ):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
        }
        self.bucket_name = bucket_name
        self.session = get_session()
    
    @asynccontextmanager    
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client
            
    
    async def upload_file(
        self,
        file: UploadFile,
        owner_id: int,
        session: SessionDep,
    ):
        object_name = file.filename
        ext = Path(object_name).suffix.lower()
        unique_name = f"{uuid.uuid4()}{ext}"
        
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        async with self.get_client() as client:
            await client.put_object(
                Bucket=self.bucket_name,
                Key=unique_name,
                Body=file.file,
            )
        
        data = {
            "filename": object_name,
            "unique_filename": unique_name,
            "url": f"{os.getenv('S3_DOMEN_URL')}/{unique_name}",
            "bucket": self.bucket_name,
            "size": file_size,
            "content_type": file.content_type,
        }
        
        if data:
            result_file = await set_file(
                filename=data["filename"],
                unique_filename=data["unique_filename"],
                url=data["url"],
                bucket=data["bucket"],
                size=data["size"],
                content_type=data["content_type"],
                owner_id=owner_id,
                session=session,
            )
            
        return result_file
    
    
    async def delete_file(
        self,
        file_id: int,
        stored_filename: str,
        session: SessionDep,
    ):
        async with self.get_client() as client:
            await client.delete_object(
                Bucket=self.bucket_name,
                Key=stored_filename,
            )
        
        await delete_file(file_id, session)
    
    
    async def download_file(
        self,
        stored_filename: str,
    ) -> AsyncIterator[bytes]:
        async with self.get_client() as client:
            response = await client.get_object(
                Bucket=self.bucket_name,
                Key=stored_filename,
            )
            async for chunk in response["Body"].iter_chunks(5 * 1024 * 1024):
                yield chunk
                

s3_client = S3client(
    access_key=os.getenv("S3_ACCESS_KEY"),
    secret_key=os.getenv("S3_SECRET_KEY"),
    endpoint_url=os.getenv("S3_ENDPOINT_URL"),
    bucket_name=os.getenv("S3_BUCKET_NAME"),
)