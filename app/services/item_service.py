from typing import List, Optional
from datetime import datetime
from app.models.item import Item, ItemCreate, ItemUpdate


class ItemService:
    """Service for managing items (in-memory storage for demonstration)"""
    
    def __init__(self):
        self.items: List[Item] = []
        self.next_id: int = 1
        
        # Add some sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample data"""
        sample_items = [
            ItemCreate(
                name="Sample Item 1",
                description="This is a sample item",
                price=19.99,
                is_available=True
            ),
            ItemCreate(
                name="Sample Item 2",
                description="Another sample item",
                price=29.99,
                is_available=True
            ),
        ]
        for item_data in sample_items:
            self.create_item(item_data)
    
    def get_all_items(self) -> List[Item]:
        """Get all items"""
        return self.items
    
    def get_item_by_id(self, item_id: int) -> Optional[Item]:
        """Get an item by ID"""
        for item in self.items:
            if item.id == item_id:
                return item
        return None
    
    def create_item(self, item_data: ItemCreate) -> Item:
        """Create a new item"""
        new_item = Item(
            id=self.next_id,
            **item_data.model_dump(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.items.append(new_item)
        self.next_id += 1
        return new_item
    
    def update_item(self, item_id: int, item_update: ItemUpdate) -> Optional[Item]:
        """Update an existing item"""
        item = self.get_item_by_id(item_id)
        if not item:
            return None
        
        update_data = item_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)
        
        item.updated_at = datetime.now()
        return item
    
    def delete_item(self, item_id: int) -> bool:
        """Delete an item"""
        item = self.get_item_by_id(item_id)
        if not item:
            return False
        
        self.items.remove(item)
        return True
