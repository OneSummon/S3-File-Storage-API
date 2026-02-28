from datetime import datetime
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(15), unique=True, index=True)
    hashed_password: Mapped[str]
    role: Mapped[str]
    created_at: Mapped[datetime]
    
    files: Mapped[list["File"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
    )
    

class File(Base):
    __tablename__ = "files"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    original_filename: Mapped[str]
    stored_filename: Mapped[str]
    url: Mapped[str]
    bucket: Mapped[str]
    size: Mapped[int]
    content_type: Mapped[str]
    created_at: Mapped[datetime]
    
    author: Mapped["User"] = relationship(
        back_populates="files",
    )