"""Simple entry point so the package is runnable."""

from src.core import db
from src.services.order_service import OrderService
from src.services.inventory import InventoryService
from src.services.pricing import PricingService


def seed():
    inv = InventoryService()
    pricing = PricingService()
    inv.set_stock("SKU-A", 100)
    inv.set_stock("SKU-B", 50)
    pricing.set_price("SKU-A", 10.0)
    pricing.set_price("SKU-B", 25.0)


def main():
    db.reset()
    seed()
    svc = OrderService()
    oid = svc.create_order("cust-1", [{"sku": "SKU-A", "quantity": 2}])
    print(f"Created order {oid}")
    print(svc.get_order(oid))


if __name__ == "__main__":
    main()
