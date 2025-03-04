from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select

from digest.database.models.user import User


class UserRepository:
    """Repository for managing users in the database."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, user: User) -> User:
        """Create a new user."""
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get a user by ID."""
        return self.session.get(User, user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        statement = select(User).where(User.username == username)
        return self.session.exec(statement).first()

    def get_all(self) -> List[User]:
        """Get all users."""
        statement = select(User)
        return list(self.session.exec(statement))

    def update(self, user: User) -> User:
        """Update a user."""
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def delete(self, user_id: UUID) -> bool:
        """Delete a user."""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        self.session.delete(user)
        self.session.commit()
        return True 