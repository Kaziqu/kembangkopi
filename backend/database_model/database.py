# database.py
from typing import List
from datetime import datetime, timezone

# database model
class OrderItem:
    def __init__(self, name: str, price: int, quantity: int, milk: str = "-", sugar: str= "-"):
        self.name = name
        self.price = price
        self.quantity = quantity
        self.total = price * quantity
        self.milk = milk
        self.sugar = sugar
        
class Order:
    def __init__(self, customer_name: str, items: List[OrderItem]):
        self.order_id = datetime.now().strftime("%Y%m%d%H%M%S")
        self.customer_name = customer_name
        self.items = items
        self.total = sum(item.total for item in items)
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.status = "pending"