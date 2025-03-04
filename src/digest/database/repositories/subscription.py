from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select

from digest.database.models.relationships import TrustedSource


class SubscriptionRepository:
    """Repository for managing user source subscriptions in the database."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, user_id: UUID, source_id: str) -> TrustedSource:
        """Create a new subscription."""
        subscription = TrustedSource(user_id=user_id, source_id=source_id)
        self.session.add(subscription)
        self.session.commit()
        self.session.refresh(subscription)
        return subscription

    def get(self, user_id: UUID, source_id: UUID) -> Optional[TrustedSource]:
        """Get a specific subscription."""
        statement = select(TrustedSource).where(
            TrustedSource.user_id == user_id,
            TrustedSource.source_id == source_id
        )
        return self.session.exec(statement).first()

    def get_user_subscriptions(self, user_id: UUID) -> List[TrustedSource]:
        """Get all subscriptions for a user."""
        statement = select(TrustedSource).where(
            TrustedSource.user_id == user_id
        )
        return list(self.session.exec(statement))

    def get_source_subscribers(self, source_id: UUID) -> List[TrustedSource]:
        """Get all subscriptions for a source."""
        statement = select(TrustedSource).where(
            TrustedSource.source_id == source_id
        )
        return list(self.session.exec(statement))

    def update(self, subscription: TrustedSource) -> TrustedSource:
        """Update a subscription."""
        self.session.add(subscription)
        self.session.commit()
        self.session.refresh(subscription)
        return subscription

    def delete(self, user_id: UUID, source_id: UUID) -> bool:
        """Delete a subscription."""
        subscription = self.get(user_id, source_id)
        if not subscription:
            return False
        
        self.session.delete(subscription)
        self.session.commit()
        return True
