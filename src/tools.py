from config import ORDERS, CUSTOMERS, SIMULATE_ERROR
from models import GetCustomersTool, Customer, Order, GetCustomerOrdersTool

import random

TOOL_HANDLERS = {
    "GetCustomersTool": lambda args: [c.model_dump() for c in get_customers(GetCustomersTool(**args))],
    "GetCustomerOrdersTool": lambda args: [o.model_dump() for o in get_customer_orders(GetCustomerOrdersTool(**args))]
}

def get_customers(input: GetCustomersTool) -> list[Customer]:
    #print(f">> get_customers: input={input}")
    if SIMULATE_ERROR and input.name and not input.name.isupper():
        error = "The name must be in UPPERCASE"
        #print(f"get_customers: raising error={error}")
        raise RuntimeError(error)
    customers = [
        customer for customer in CUSTOMERS
        # Check ID: If input.id is None OR customer.id matches input.id
        if (input.id is None or customer.id == input.id)
           # Check Name: If input.name is None OR customer.name matches input.name
           and (input.name is None or customer.name.lower() == input.name.lower())
           # Check Email: If input.email is None OR customer.email matches input.email
           and (input.email is None or customer.email == input.email)
           # Check Gender: If input.gender is None OR customer.gender matches input.gender
           and (input.gender is None or customer.gender == input.gender)
    ]
    #print(f"<< get_customers: returning nb_results={len(customers)}")
    return customers


def get_customer_orders(input: GetCustomerOrdersTool) -> list[Order]:
    #print(f">> get_customer_orders: input={input}")
    if SIMULATE_ERROR and random.random() < 0.75:
        error = "Temporary database connection error, please try again"
        #print(f"<< get_customer_orders: raising error={error}")
        raise RuntimeError(error)
    orders = [
        order for order in ORDERS
        if order.customer_id == input.customer_id
    ]
    #print(f"<< get_customer_orders: returning nb_orders={len(orders)}")
    return orders
