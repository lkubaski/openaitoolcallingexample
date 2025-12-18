from models import Customer, Order

API_KEY = "[YOUR_API_KEY_HERE]"

MODEL = "openai/gpt-4o-mini"

CUSTOMERS = [
    Customer(id=1, name="Alice", email="alice@example.com", gender="F"),
    Customer(id=2, name="Bob", email="bob@example.com", gender="M"),
]

ORDERS = [
    Order(id=1, customer_id=1, product_id=1, quantity=2, amount=50),
    Order(id=2, customer_id=1, product_id=2, quantity=5, amount=100),
    Order(id=3, customer_id=2, product_id=1, quantity=5, amount=150),
    Order(id=3, customer_id=2, product_id=2, quantity=10, amount=200),
]

SYSTEM_PROMPT = """
You are a resilient assistant. 
If a tool call fails, analyze the error message. 
Your immediate next action must be to **retry the call at least once**, optionally adjusting the input parameters based on the error details, before generating any final answer for the user.
"""

SIMULATE_ERROR = False

# A limit on the number of retries to avoid spending too many tokens
MAX_LOOP = 10