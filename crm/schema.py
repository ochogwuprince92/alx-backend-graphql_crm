import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter


# --------------------
# GraphQL Types
# --------------------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        filterset_class = CustomerFilter
        interfaces = (graphene.relay.Node,)


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        filterset_class = ProductFilter
        interfaces = (graphene.relay.Node,)


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        filterset_class = OrderFilter
        interfaces = (graphene.relay.Node,)


# --------------------
# Input Types
# --------------------
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int(required=False, default_value=0)


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime(required=False)


# --------------------
# Mutations
# --------------------
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        try:
            validate_email(input.email)
        except ValidationError:
            raise Exception("Invalid email format.")

        if Customer.objects.filter(email=input.email).exists():
            raise Exception("Email already exists.")

        if input.phone and not (input.phone.startswith("+") or "-" in input.phone):
            raise Exception("Invalid phone format.")

        customer = Customer.objects.create(
            name=input.name,
            email=input.email,
            phone=input.phone,
        )
        return CreateCustomer(customer=customer, message="Customer created successfully.")


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        created_customers, errors = [], []

        for cust in input:
            try:
                validate_email(cust.email)
                if Customer.objects.filter(email=cust.email).exists():
                    errors.append(f"Email already exists: {cust.email}")
                    continue
                if cust.phone and not (cust.phone.startswith("+") or "-" in cust.phone):
                    errors.append(f"Invalid phone format: {cust.phone}")
                    continue
                c = Customer.objects.create(
                    name=cust.name, email=cust.email, phone=cust.phone
                )
                created_customers.append(c)
            except ValidationError:
                errors.append(f"Invalid email format: {cust.email}")

        return BulkCreateCustomers(customers=created_customers, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        if input.price <= 0:
            raise Exception("Price must be positive.")
        if input.stock < 0:
            raise Exception("Stock cannot be negative.")

        product = Product.objects.create(
            name=input.name,
            price=input.price,
            stock=input.stock or 0,
        )
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, input):
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID.")

        if not input.product_ids:
            raise Exception("At least one product must be selected.")

        products = Product.objects.filter(id__in=input.product_ids)
        if products.count() != len(input.product_ids):
            raise Exception("One or more product IDs are invalid.")

        total_amount = sum([p.price for p in products])

        order = Order.objects.create(
            customer=customer,
            total_amount=Decimal(total_amount),
            order_date=input.order_date or timezone.now(),
        )
        order.products.set(products)

        return CreateOrder(order=order)


class Query(graphene.ObjectType):
    # Relay single fetch
    customer = graphene.relay.Node.Field(CustomerType)
    product = graphene.relay.Node.Field(ProductType)
    order = graphene.relay.Node.Field(OrderType)

    # Collections with filter + order_by
    all_customers = DjangoFilterConnectionField(
        CustomerType, order_by=graphene.List(of_type=graphene.String)
    )
    all_products = DjangoFilterConnectionField(
        ProductType, order_by=graphene.List(of_type=graphene.String)
    )
    all_orders = DjangoFilterConnectionField(
        OrderType, order_by=graphene.List(of_type=graphene.String)
    )

    def resolve_all_customers(self, info, order_by=None, **kwargs):
        qs = Customer.objects.all()
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def resolve_all_products(self, info, order_by=None, **kwargs):
        qs = Product.objects.all()
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def resolve_all_orders(self, info, order_by=None, **kwargs):
        qs = Order.objects.all()
        if order_by:
            qs = qs.order_by(*order_by)
        return qs


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()


# --- Schema ---
schema = graphene.Schema(query=Query, mutation=Mutation)
