"""
Base Service Class

This module provides an abstract base class for all service classes.
It encapsulates common functionality and enforces consistent patterns
across the service layer.

Key Features:
- Database session management
- Common CRUD operations
- Error handling patterns
- Logging integration
- Transaction management

Design Pattern:
This follows the Service Layer pattern, where business logic is
separated from controllers and data access. Services coordinate
between API endpoints and database models.

Usage:
    from app.services.base_service import BaseService
    
    class MyService(BaseService):
        def __init__(self, db: AsyncSession):
            super().__init__(db)
            self.logger = get_logger("my_service")
        
        async def my_business_operation(self):
            # Implement business logic here
            pass
"""

from typing import TypeVar, Generic, Type, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.exc import SQLAlchemyError

from app.core.logger import get_logger

# Type variable for generic model type
ModelType = TypeVar("ModelType")

logger = get_logger(service="base_service")


class BaseService(Generic[ModelType]):
    """
    Abstract base class for all service classes.
    
    This class provides common database operations and patterns
    that can be reused across all services. It uses generics to
    provide type-safe CRUD operations.
    
    Attributes:
        db: AsyncSession instance for database operations
        model_class: SQLAlchemy model class (set in subclasses)
    
    Example:
        class UserService(BaseService[User]):
            def __init__(self, db: AsyncSession):
                super().__init__(db, User)
    """
    
    def __init__(self, db: AsyncSession, model_class: Optional[Type[ModelType]] = None):
        """
        Initialize the base service.
        
        Args:
            db: Database session for this service instance
            model_class: SQLAlchemy model class for CRUD operations
        """
        self.db = db
        self.model_class = model_class
    
    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """
        Retrieve a single record by its ID.
        
        Args:
            id: Primary key value
            
        Returns:
            Optional[ModelType]: Model instance if found, None otherwise
            
        Example:
            user = await service.get_by_id(123)
            if user:
                print(f"Found user: {user.email}")
        """
        if not self.model_class:
            raise NotImplementedError("model_class must be set")
        
        try:
            stmt = select(self.model_class).where(self.model_class.id == id)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model_class.__name__} by id {id}: {e}")
            raise
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Retrieve all records with pagination.
        
        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            List[ModelType]: List of model instances
            
        Example:
            # Get first 10 users
            users = await service.get_all(skip=0, limit=10)
            
            # Get next 10 users
            users = await service.get_all(skip=10, limit=10)
        """
        if not self.model_class:
            raise NotImplementedError("model_class must be set")
        
        try:
            stmt = select(self.model_class).offset(skip).limit(limit)
            result = await self.db.execute(stmt)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting all {self.model_class.__name__}: {e}")
            raise
    
    async def create(self, obj: ModelType) -> ModelType:
        """
        Create a new record in the database.
        
        Args:
            obj: Model instance to create
            
        Returns:
            ModelType: Created model instance with ID populated
            
        Example:
            user = User(email="user@example.com", username="user")
            created_user = await service.create(user)
            print(f"Created user with ID: {created_user.id}")
        """
        try:
            self.db.add(obj)
            await self.db.commit()
            await self.db.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error creating {type(obj).__name__}: {e}")
            raise
    
    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """
        Update a record by its ID.
        
        Args:
            id: Primary key value
            **kwargs: Fields to update with their new values
            
        Returns:
            Optional[ModelType]: Updated model instance if found, None otherwise
            
        Example:
            updated_user = await service.update(
                123,
                email="newemail@example.com",
                username="newusername"
            )
        """
        if not self.model_class:
            raise NotImplementedError("model_class must be set")
        
        try:
            stmt = (
                update(self.model_class)
                .where(self.model_class.id == id)
                .values(**kwargs)
                .returning(self.model_class)
            )
            result = await self.db.execute(stmt)
            await self.db.commit()
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error updating {self.model_class.__name__} {id}: {e}")
            raise
    
    async def delete(self, id: int) -> bool:
        """
        Delete a record by its ID.
        
        Args:
            id: Primary key value
            
        Returns:
            bool: True if record was deleted, False if not found
            
        Example:
            deleted = await service.delete(123)
            if deleted:
                print("User deleted successfully")
            else:
                print("User not found")
        """
        if not self.model_class:
            raise NotImplementedError("model_class must be set")
        
        try:
            stmt = delete(self.model_class).where(self.model_class.id == id)
            result = await self.db.execute(stmt)
            await self.db.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error deleting {self.model_class.__name__} {id}: {e}")
            raise
    
    async def exists(self, id: int) -> bool:
        """
        Check if a record exists by its ID.
        
        Args:
            id: Primary key value
            
        Returns:
            bool: True if record exists, False otherwise
            
        Example:
            if await service.exists(123):
                print("User exists")
            else:
                print("User not found")
        """
        obj = await self.get_by_id(id)
        return obj is not None
    
    async def count(self) -> int:
        """
        Count total number of records.
        
        Returns:
            int: Total count of records
            
        Example:
            total_users = await service.count()
            print(f"Total users: {total_users}")
        """
        if not self.model_class:
            raise NotImplementedError("model_class must be set")
        
        try:
            stmt = select(self.model_class)
            result = await self.db.execute(stmt)
            return len(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model_class.__name__}: {e}")
            raise
