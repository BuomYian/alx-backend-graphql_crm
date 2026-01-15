import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from django.db import transaction
from django.core.exceptions import ValidationError
from crm.models import Customer, Product, Order
from crm.filters import CustomerFilter, ProductFilter, OrderFilter
import re


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = '__all__'
        interfaces = (graphene.relay.Node,)


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = '__all__'
        interfaces = (graphene.relay.Node,)


class OrderType(DjangoObjectType):
    total_amount = graphene.Decimal()

    class Meta:
        model = Order
        fields = '__all__'
        interfaces = (graphene.relay.Node,)

    def resolve_total_amount(self, info):
        return self.calculate_total()


class CreateCustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class CreateCustomer(graphene.Mutation):
    customer = graphene.Field(CustomerType)
    message = graphene.String()
    success = graphene.Boolean()

    class Arguments:
        input = CreateCustomerInput(required=True)

    @staticmethod
    def mutate(root, info, input):
        try:
            customer = Customer(
                name=input.name,
                email=input.email,
                phone=input.phone
            )
            customer.full_clean()
            customer.save()
            return CreateCustomer(
                customer=customer,
                message=f"Customer {customer.name} created successfully",
                success=True
            )
        except ValidationError as e:
            raise GraphQLError(str(e))
        except Exception as e:
            raise GraphQLError(f"Error creating customer: {str(e)}")


class BulkCreateCustomersInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class BulkCreateCustomers(graphene.Mutation):
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)
    success = graphene.Boolean()

    class Arguments:
        input = graphene.List(BulkCreateCustomersInput, required=True)

    @staticmethod
    def mutate(root, info, input):
        created_customers = []
        errors = []

        for i, customer_data in enumerate(input):
            try:
                customer = Customer(
                    name=customer_data.name,
                    email=customer_data.email,
                    phone=customer_data.phone
                )
                customer.full_clean()
                customer.save()
                created_customers.append(customer)
            except ValidationError as e:
                errors.append(f"Row {i+1}: {str(e)}")
            except Exception as e:
                errors.append(f"Row {i+1}: {str(e)}")

        return BulkCreateCustomers(
            customers=created_customers,
            errors=errors,
            success=len(errors) == 0
        )


class CreateProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()


class CreateProduct(graphene.Mutation):
    product = graphene.Field(ProductType)
    message = graphene.String()
    success = graphene.Boolean()

    class Arguments:
        input = CreateProductInput(required=True)

    @staticmethod
    def mutate(root, info, input):
        try:
            product = Product(
                name=input.name,
                price=input.price,
                stock=input.stock or 0
            )
            product.full_clean()
            product.save()
            return CreateProduct(
                product=product,
                message=f"Product {product.name} created successfully",
                success=True
            )
        except ValidationError as e:
            raise GraphQLError(str(e))
        except Exception as e:
            raise GraphQLError(f"Error creating product: {str(e)}")


class CreateOrderInput(graphene.InputObjectType):
    customer_id = graphene.Int(required=True)
    product_ids = graphene.List(graphene.Int, required=True)
    order_date = graphene.DateTime()


class CreateOrder(graphene.Mutation):
    order = graphene.Field(OrderType)
    message = graphene.String()
    success = graphene.Boolean()

    class Arguments:
        input = CreateOrderInput(required=True)

    @staticmethod
    def mutate(root, info, input):
        try:
            if not input.product_ids:
                raise GraphQLError("At least one product must be selected")

            try:
                customer = Customer.objects.get(id=input.customer_id)
            except Customer.DoesNotExist:
                raise GraphQLError(
                    f"Customer with ID {input.customer_id} not found")

            products = Product.objects.filter(id__in=input.product_ids)
            if len(products) != len(input.product_ids):
                missing_ids = set(input.product_ids) - \
                    set(p.id for p in products)
                raise GraphQLError(f"Invalid product IDs: {missing_ids}")

            with transaction.atomic():
                order = Order.objects.create(
                    customer=customer,
                    total_amount=0
                )
                order.products.set(products)
                order.total_amount = order.calculate_total()
                order.save()

            return CreateOrder(
                order=order,
                message=f"Order created successfully with total: ${order.total_amount}",
                success=True
            )
        except GraphQLError:
            raise
        except Exception as e:
            raise GraphQLError(f"Error creating order: {str(e)}")


class Query(graphene.ObjectType):
    hello = graphene.String()
    all_customers = DjangoFilterConnectionField(
        CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(
        ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(
        OrderType, filterset_class=OrderFilter)
    customer = graphene.Field(CustomerType, id=graphene.Int(required=True))
    product = graphene.Field(ProductType, id=graphene.Int(required=True))
    order = graphene.Field(OrderType, id=graphene.Int(required=True))

    def resolve_hello(self, info):
        return "Hello, GraphQL!"

    def resolve_customer(self, info, id):
        try:
            return Customer.objects.get(id=id)
        except Customer.DoesNotExist:
            return None

    def resolve_product(self, info, id):
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            return None

    def resolve_order(self, info, id):
        try:
            return Order.objects.get(id=id)
        except Order.DoesNotExist:
            return None


class UpdateLowStockProducts(graphene.Mutation):
    updated_products = graphene.List(ProductType)
    updated_count = graphene.Int()
    message = graphene.String()
    success = graphene.Boolean()

    @staticmethod
    def mutate(root, info):
        try:
            low_stock_products = Product.objects.filter(stock__lt=10)
            updated_products = []

            for product in low_stock_products:
                product.stock += 10
                product.full_clean()
                product.save()
                updated_products.append(product)

            message = f"Successfully updated {len(updated_products)} products with low stock"

            return UpdateLowStockProducts(
                updated_products=updated_products,
                updated_count=len(updated_products),
                message=message,
                success=True
            )
        except Exception as e:
            raise GraphQLError(f"Error updating low stock products: {str(e)}")


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()
