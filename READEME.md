# ALX Backend GraphQL CRM

A comprehensive GraphQL-based Customer Relationship Management (CRM) system built with Django and graphene-django.

## Project Structure

```
backend/
├── alx_backend_graphql_crm/     # Django project configuration
│   ├── settings.py              # Project settings with GraphQL config
│   ├── urls.py                  # URL routing and GraphQL endpoint
│   └── schema.py                # Main GraphQL schema
├── crm/                         # Main CRM app
│   ├── models.py                # Customer, Product, Order models
│   ├── schema.py                # GraphQL types, queries, mutations
│   ├── filters.py               # Django filters for GraphQL filtering
│   └── migrations/              # Database migrations
├── manage.py                    # Django management script
├── db.sqlite3                   # SQLite database
├── seed_db.py                   # Database seeding script
├── GRAPHQL_TESTS.md            # GraphQL query examples
└── README.md                    # This file
```

## Installation

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install Django graphene-django django-filter
```

3. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. (Optional) Seed database with sample data:
```bash
python seed_db.py
```

## Running the Server

Start the development server:
```bash
python manage.py runserver 8001
```

Access GraphQL interface at: `http://localhost:8001/graphql/`

## Features

### Database Models

**Customer**
- name (string, required)
- email (string, unique, required)
- phone (string, optional, validated format)
- created_at (auto-generated timestamp)
- updated_at (auto-updated timestamp)

**Product**
- name (string, required)
- price (decimal, positive, required)
- stock (integer, non-negative, default 0)
- created_at (auto-generated timestamp)
- updated_at (auto-updated timestamp)

**Order**
- customer (foreign key to Customer)
- products (many-to-many relationship to Product)
- total_amount (auto-calculated sum of product prices)
- order_date (auto-generated timestamp)
- created_at (auto-generated timestamp)
- updated_at (auto-updated timestamp)

### GraphQL Operations

#### Queries
- `hello` - Test query returning "Hello, GraphQL!"
- `allCustomers` - List all customers with filtering support
- `allProducts` - List all products with filtering support
- `allOrders` - List all orders with filtering support
- `customer(id)` - Get single customer by ID
- `product(id)` - Get single product by ID
- `order(id)` - Get single order by ID

#### Mutations
- `createCustomer` - Create a single customer with validation
- `bulkCreateCustomers` - Create multiple customers with partial success support
- `createProduct` - Create a product with validation
- `createOrder` - Create an order with product association and total calculation

### Filtering Capabilities

**Customer Filters**
- `nameIcontains` - Case-insensitive name search
- `emailIcontains` - Case-insensitive email search
- `createdAtGte` / `createdAtLte` - Date range filtering
- `phonePattern` - Filter by phone number prefix

**Product Filters**
- `nameIcontains` - Case-insensitive name search
- `priceGte` / `priceLte` - Price range filtering
- `stockGte` / `stockLte` - Stock level filtering
- `lowStock` - Boolean filter for products with stock < 10

**Order Filters**
- `totalAmountGte` / `totalAmountLte` - Total amount range
- `orderDateGte` / `orderDateLte` - Date range filtering
- `customerName` - Filter by customer name (related field lookup)
- `productName` - Filter by product name (related field lookup)
- `productId` - Filter by specific product ID

### Validation

**Customer**
- Email must be unique
- Phone format: `+1234567890` or `123-456-7890` (if provided)

**Product**
- Price must be positive
- Stock must be non-negative

**Order**
- Customer ID must exist
- At least one product must be selected
- All product IDs must exist
- Total amount is auto-calculated

## Testing

See `GRAPHQL_TESTS.md` for comprehensive examples of all queries and mutations.

Quick test:
```graphql
query {
  hello
}
```

Expected response:
```json
{
  "data": {
    "hello": "Hello, GraphQL!"
  }
}
```

## Admin Interface

Access Django admin at: `http://localhost:8001/admin/`

Default admin credentials can be created with:
```bash
python manage.py createsuperuser
```

## Architecture

### GraphQL Schema Design

The project follows a clean separation of concerns:

1. **Models Layer** - Django ORM models defining database structure
2. **GraphQL Types Layer** - GraphQL representations of models (CustomerType, ProductType, OrderType)
3. **Input Types Layer** - Input objects for mutations (CreateCustomerInput, etc.)
4. **Mutation Layer** - Business logic for create/update operations with validation
5. **Query Layer** - Read operations with filtering support
6. **Filters Layer** - Django filter definitions for GraphQL filtering

### Error Handling

All mutations include comprehensive error handling:
- Validation errors from Django model validation
- Database constraint violations (e.g., duplicate email)
- Related object existence checks
- User-friendly error messages in GraphQL responses

### Partial Success in Bulk Operations

The `bulkCreateCustomers` mutation supports partial success:
- Valid customers are created even if some fail validation
- Errors are returned with row information
- Success flag indicates if all operations succeeded

## Best Practices Implemented

1. **Transaction Safety** - Order creation uses database transactions
2. **Validation** - Input validation at model and mutation levels
3. **Error Messages** - Clear, user-friendly error messages
4. **Efficient Queries** - Uses Django ORM efficiently with related object fetching
5. **Scalable Filtering** - Django filters with support for complex lookups
6. **Type Safety** - Full GraphQL type definitions with required fields
7. **Documentation** - Comprehensive docstrings and examples

## Future Enhancements

- Authentication and authorization with JWT
- Rate limiting
- Caching with Redis
- File uploads
- Subscriptions for real-time updates
- Advanced reporting queries
- Audit logging
- API versioning

## Database Diagram

```
Customer
├── id (PK)
├── name
├── email (UNIQUE)
├── phone
├── created_at
└── updated_at

Product
├── id (PK)
├── name
├── price
├── stock
├── created_at
└── updated_at

Order
├── id (PK)
├── customer_id (FK → Customer)
├── total_amount
├── order_date
├── created_at
└── updated_at

Order_Product (Many-to-Many)
├── order_id (FK → Order)
└── product_id (FK → Product)
```

## Troubleshooting

**Port already in use**
```bash
python manage.py runserver 8002
```

**Database locked**
```bash
rm db.sqlite3
python manage.py migrate
python seed_db.py
```

**Module not found**
Ensure virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## License

Educational project for ALX Backend Course

## Support

For issues or questions, refer to:
- Django Documentation: https://docs.djangoproject.com/
- Graphene Documentation: https://docs.graphene-python.org/
- GraphQL Documentation: https://graphql.org/learn/
