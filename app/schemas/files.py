from datetime import datetime
from pydantic import BaseModel

class FileResponse(BaseModel):
    id: int
    original_filename: str
    stored_filename: str
    size: int
    url: str
    content_type: str
    owner_id: int
    created_at: datetime