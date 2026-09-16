from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class LineItem:
    sku: str
    quantity: int
    unit_price: float = 0.0


@dataclass
class Order:
    order_id: str
    customer_id: str
    items: List[LineItem] = field(default_factory=list)
    status: str = "pending"  # pending, confirmed, cancelled, shipped
    total: float = 0.0
    created_at: Optional[datetime] = None
    # legacy field still used by some paths
    discount_code: Optional[str] = None

    def to_dict(self):
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "items": [{"sku": i.sku, "quantity": i.quantity, "unit_price": i.unit_price} for i in self.items],
            "status": self.status,
            "total": self.total,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "discount_code": self.discount_code,
            "quantity": sum(i.quantity for i in self.items),  # denormalized for the buggy updater
        }
