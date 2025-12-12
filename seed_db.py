import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')
django.setup()

from crm.models import Customer, Product, Order

def seed_database():
    Customer.objects.all().delete()
    Product.objects.all().delete()
    Order.objects.all().delete()

    customers = [
        Customer(name='Alice Johnson', email='alice@example.com', phone='+1234567890'),
        Customer(name='Bob Smith', email='bob@example.com', phone='123-456-7890'),
        Customer(name='Carol White', email='carol@example.com', phone='+1987654321'),
    ]
    Customer.objects.bulk_create(customers)

    products = [
        Product(name='Laptop', price=999.99, stock=10),
        Product(name='Mouse', price=29.99, stock=50),
        Product(name='Keyboard', price=79.99, stock=5),
        Product(name='Monitor', price=299.99, stock=15),
    ]
    Product.objects.bulk_create(products)

    customers_list = Customer.objects.all()
    products_list = Product.objects.all()

    for customer in customers_list:
        order = Order.objects.create(customer=customer)
        selected_products = products_list[:2]
        order.products.set(selected_products)
        order.total_amount = order.calculate_total()
        order.save()

    print("Database seeded successfully!")
    print(f"Created {Customer.objects.count()} customers")
    print(f"Created {Product.objects.count()} products")
    print(f"Created {Order.objects.count()} orders")

if __name__ == '__main__':
    seed_database()
