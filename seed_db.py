import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')
django.setup()

from crm.models import Customer, Product, Order
from decimal import Decimal
from django.utils import timezone

def seed_database():
    print("🌱 Starting database seeding...")
    
    # Clear existing data
    Order.objects.all().delete()
    Customer.objects.all().delete()
    Product.objects.all().delete()
    
    # Create Customers
    print("👥 Creating customers...")
    customers_data = [
        {"name": "Alice Johnson", "email": "alice@example.com", "phone": "+1234567890"},
        {"name": "Bob Smith", "email": "bob@example.com", "phone": "123-456-7890"},
        {"name": "Carol Davis", "email": "carol@example.com", "phone": "+1987654321"},
        {"name": "David Wilson", "email": "david@example.com"},
        {"name": "Eva Brown", "email": "eva@example.com", "phone": "987-654-3210"},
    ]
    
    customers = []
    for data in customers_data:
        customer = Customer.objects.create(**data)
        customers.append(customer)
        print(f"  ✅ Created: {customer.name}")
    
    # Create Products
    print("📦 Creating products...")
    products_data = [
        {"name": "Laptop", "price": Decimal("999.99"), "stock": 50},
        {"name": "Wireless Mouse", "price": Decimal("29.99"), "stock": 100},
        {"name": "Mechanical Keyboard", "price": Decimal("79.99"), "stock": 75},
        {"name": "4K Monitor", "price": Decimal("299.99"), "stock": 30},
        {"name": "Noise-Cancelling Headphones", "price": Decimal("149.99"), "stock": 60},
    ]
    
    products = []
    for data in products_data:
        product = Product.objects.create(**data)
        products.append(product)
        print(f"  ✅ Created: {product.name} - ${product.price}")
    
    # Create Sample Orders
    print("🛍️  Creating sample orders...")
    orders_data = [
        {"customer": customers[0], "products": [products[0], products[1]]},  # Laptop + Mouse
        {"customer": customers[1], "products": [products[2], products[3]]},  # Keyboard + Monitor
        {"customer": customers[2], "products": [products[4]]},               # Headphones
        {"customer": customers[3], "products": [products[0], products[2], products[4]]},  # Laptop + Keyboard + Headphones
        {"customer": customers[4], "products": [products[1], products[3]]},  # Mouse + Monitor
    ]
    
    for i, data in enumerate(orders_data):
        # Calculate total
        total_amount = sum(product.price for product in data["products"])
        
        # Create order
        order = Order.objects.create(
            customer=data["customer"],
            total_amount=total_amount
        )
        
        # Add products
        order.products.set(data["products"])
        
        product_names = ", ".join([p.name for p in data["products"]])
        print(f"  ✅ Order #{order.id}: {order.customer.name} - {product_names} - ${order.total_amount}")
    
    print("🎉 Database seeding completed!")
    print(f"📊 Summary:")
    print(f"   - {Customer.objects.count()} customers")
    print(f"   - {Product.objects.count()} products")
    print(f"   - {Order.objects.count()} orders")

if __name__ == "__main__":
    seed_database()

