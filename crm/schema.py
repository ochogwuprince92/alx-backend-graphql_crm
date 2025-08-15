import graphene
from graphene import DjangoObjectType
from .models import Customer, Product, Order
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from decimal import Decimal

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"

class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            raise Exception("Invalid email format.")

        # Check for duplicate email
        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists.")

        # Optional phone validation (simple example)
        if phone and not (phone.startswith('+') or '-' in phone):
            raise Exception("Invalid phone format.")

        customer = Customer.objects.create(name=name, email=email, phone=phone)
        return CreateCustomer(customer=customer, message="Customer created successfully.")


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        customers = graphene.List(
            graphene.NonNull(
                graphene.InputObjectType(
                    "CustomerInput",
                    name=graphene.String(required=True),
                    email=graphene.String(required=True),
                    phone=graphene.String(required=False),
                )
            )
        )

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, customers):
        created_customers = []
        errors = []

        for cust in customers:
            try:
                validate_email(cust.email)
                if Customer.objects.filter(email=cust.email).exists():
                    errors.append(f"Email already exists: {cust.email}")
                    continue

                if cust.phone and not (cust.phone.startswith('+') or '-' in cust.phone):
                    errors.append(f"Invalid phone format: {cust.phone}")
                    continue

                c = Customer.objects.create(
                    name=cust.name, email=cust.email, phone=cust.phone
                )
                created_customers.append(c)
            except ValidationError:
                errors.append(f"Invalid email: {cust.email}")

        return BulkCreateCustomers(customers=created_customers, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        stock = graphene.Int(required=False, default_value=0)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock):
        if price <= 0:
            raise Exception("Price must be positive.")
        if stock < 0:
            raise Exception("Stock cannot be negative.")

        product = Product.objects.create(name=name, price=price, stock=stock)
        return CreateProduct(product=product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids):
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID.")

        if not product_ids:
            raise Exception("At least one product must be selected.")

        products = Product.objects.filter(id__in=product_ids)
        if products.count() != len(product_ids):
            raise Exception("One or more product IDs are invalid.")

        total_amount = sum([p.price for p in products])

        order = Order.objects.create(customer=customer, total_amount=Decimal(total_amount))
        order.products.set(products)
        return CreateOrder(order=order)

class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(root, info):
        return Customer.objects.all()

    def resolve_products(root, info):
        return Product.objects.all()

    def resolve_orders(root, info):
        return Order.objects.all()


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
