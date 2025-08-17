import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db import transaction
from django.core.exceptions import ValidationError
import re
from .filters import CustomerFilter, ProductFilter, OrderFilter
from decimal import Decimal
from .models import Customer, Product, Order

# GraphQL Types
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
    class Meta:
        model = Order
        fields = '__all__'
        interfaces = (graphene.relay.Node,)

# Input Types for Mutations
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)
    
    customer = graphene.Field(CustomerType)
    message = graphene.String()
    errors = graphene.List(graphene.String)
    success = graphene.Boolean()
    
    def mutate(self, info, input):
        errors = []
        
        # Validate email uniqueness
        if Customer.objects.filter(email=input.email).exists():
            errors.append("Email already exists")
        
        # Validate phone format if provided
        if input.phone:
            phone_pattern = r'^(\+\d{1,3}\d{10}|\d{3}-\d{3}-\d{4})$'
            if not re.match(phone_pattern, input.phone):
                errors.append("Invalid phone format. Use +1234567890 or 123-456-7890")
        
        if errors:
            return CreateCustomer(
                success=False,
                errors=errors,
                customer=None,
                message="Customer creation failed"
            )
        
        try:
            customer = Customer.objects.create(
                name=input.name,
                email=input.email,
                phone=input.phone or None
            )
            return CreateCustomer(
                success=True,
                customer=customer,
                message="Customer created successfully",
                errors=[]
            )
        except ValidationError as e:
            return CreateCustomer(
                success=False,
                errors=[str(e)],
                customer=None,
                message="Validation error"
            )
        except Exception as e:
            return CreateCustomer(
                success=False,
                errors=[f"Unexpected error: {str(e)}"],
                customer=None,
                message="Customer creation failed"
            )

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)
    
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)
    success_count = graphene.Int()
    total_count = graphene.Int()
    
    def mutate(self, info, input):
        customers = []
        errors = []
        
        # Use atomic transaction for consistency
        try:
            with transaction.atomic():
                for i, customer_data in enumerate(input):
                    try:
                        # Validate email uniqueness
                        if Customer.objects.filter(email=customer_data.email).exists():
                            errors.append(f"Customer {i+1} ({customer_data.name}): Email already exists")
                            continue
                        
                        # Validate phone format if provided
                        if customer_data.phone:
                            phone_pattern = r'^(\+\d{1,3}\d{10}|\d{3}-\d{3}-\d{4})$'
                            if not re.match(phone_pattern, customer_data.phone):
                                errors.append(f"Customer {i+1} ({customer_data.name}): Invalid phone format")
                                continue
                        
                        # Create customer
                        customer = Customer.objects.create(
                            name=customer_data.name,
                            email=customer_data.email,
                            phone=customer_data.phone or None
                        )
                        customers.append(customer)
                        
                    except ValidationError as e:
                        errors.append(f"Customer {i+1} ({customer_data.name}): {str(e)}")
                    except Exception as e:
                        errors.append(f"Customer {i+1} ({customer_data.name}): Unexpected error - {str(e)}")
        
        except Exception as e:
            errors.append(f"Transaction failed: {str(e)}")
        
        return BulkCreateCustomers(
            customers=customers,
            errors=errors,
            success_count=len(customers),
            total_count=len(input)
        )

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)
    
    product = graphene.Field(ProductType)
    message = graphene.String()
    errors = graphene.List(graphene.String)
    success = graphene.Boolean()
    
    def mutate(self, info, input):
        errors = []
        
        # Validate price is positive
        if input.price <= 0:
            errors.append("Price must be positive")
        
        # Validate stock is non-negative
        stock = input.stock if input.stock is not None else 0
        if stock < 0:
            errors.append("Stock cannot be negative")
        
        if errors:
            return CreateProduct(
                success=False,
                errors=errors,
                product=None,
                message="Product creation failed"
            )
        
        try:
            product = Product.objects.create(
                name=input.name,
                price=input.price,
                stock=stock
            )
            return CreateProduct(
                success=True,
                product=product,
                message="Product created successfully",
                errors=[]
            )
        except ValidationError as e:
            return CreateProduct(
                success=False,
                errors=[str(e)],
                product=None,
                message="Validation error"
            )
        except Exception as e:
            return CreateProduct(
                success=False,
                errors=[f"Unexpected error: {str(e)}"],
                product=None,
                message="Product creation failed"
            )

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)
    
    order = graphene.Field(OrderType)
    message = graphene.String()
    errors = graphene.List(graphene.String)
    success = graphene.Boolean()
    
    def mutate(self, info, input):
        errors = []
        
        # Validate customer exists
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            errors.append(f"Customer with ID {input.customer_id} does not exist")
            return CreateOrder(
                success=False,
                errors=errors,
                order=None,
                message="Order creation failed"
            )
        
        # Validate products exist and at least one is provided
        if not input.product_ids:
            errors.append("At least one product must be selected")
            return CreateOrder(
                success=False,
                errors=errors,
                order=None,
                message="Order creation failed"
            )
        
        # Get products and validate they exist
        products = Product.objects.filter(id__in=input.product_ids)
        found_product_ids = set(str(p.id) for p in products)
        requested_product_ids = set(input.product_ids)
        
        if found_product_ids != requested_product_ids:
            missing_ids = requested_product_ids - found_product_ids
            errors.append(f"Products with IDs {list(missing_ids)} do not exist")
            return CreateOrder(
                success=False,
                errors=errors,
                order=None,
                message="Order creation failed"
            )
        
        if errors:
            return CreateOrder(
                success=False,
                errors=errors,
                order=None,
                message="Order creation failed"
            )
        
        try:
            with transaction.atomic():
                # Calculate total amount
                total_amount = sum(product.price for product in products)
                
                # Create order
                order = Order.objects.create(
                    customer=customer,
                    total_amount=total_amount,
                    order_date=input.order_date
                )
                
                # Associate products
                order.products.set(products)
                
                return CreateOrder(
                    success=True,
                    order=order,
                    message=f"Order created successfully with total amount ${total_amount}",
                    errors=[]
                )
        except Exception as e:
            return CreateOrder(
                success=False,
                errors=[f"Order creation failed: {str(e)}"],
                order=None,
                message="Order creation failed"
            )

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")
    
    # Filtered connection fields (NEW - with advanced filtering)
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)
    
    # Simple list fields (for backward compatibility)
    customers_list = graphene.List(CustomerType)
    products_list = graphene.List(ProductType)
    orders_list = graphene.List(OrderType)
    
    # Individual item queries
    customer = graphene.Field(CustomerType, id=graphene.ID())
    product = graphene.Field(ProductType, id=graphene.ID())
    order = graphene.Field(OrderType, id=graphene.ID())
    
    # Custom aggregation queries
    customer_count = graphene.Int()
    product_count = graphene.Int()
    order_count = graphene.Int()
    total_revenue = graphene.Float()
    
    # Resolvers for simple lists
    def resolve_customers_list(self, info):
        return Customer.objects.all()
    
    def resolve_products_list(self, info):
        return Product.objects.all()
    
    def resolve_orders_list(self, info):
        return Order.objects.all()
    
    # Resolvers for individual items
    def resolve_customer(self, info, id):
        try:
            return Customer.objects.get(pk=id)
        except Customer.DoesNotExist:
            return None
    
    def resolve_product(self, info, id):
        try:
            return Product.objects.get(pk=id)
        except Product.DoesNotExist:
            return None
    
    def resolve_order(self, info, id):
        try:
            return Order.objects.get(pk=id)
        except Order.DoesNotExist:
            return None
    
    # Resolvers for aggregations
    def resolve_customer_count(self, info):
        return Customer.objects.count()
    
    def resolve_product_count(self, info):
        return Product.objects.count()
    
    def resolve_order_count(self, info):
        return Order.objects.count()
    
    def resolve_total_revenue(self, info):
        from django.db.models import Sum
        result = Order.objects.aggregate(total=Sum('total_amount'))
        return float(result['total'] or 0)

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
