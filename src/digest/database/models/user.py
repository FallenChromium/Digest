from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    """Database model for users."""
    
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True
    )
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    trusted_sources: List["TrustedSource"] = Relationship( # type: ignore
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    ) 
    feed: List["Feed"] = Relationship( # type: ignore
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    ) 