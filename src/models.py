from typing import Literal

from pydantic import BaseModel, Field

class Customer(BaseModel):
    id: int = Field(description="The customer identifier")
    name: str = Field(description="The customer name")
    email: str = Field(description="The customer email")
    gender: Literal["M", "F", "O"] = Field(description="The customer's gender. M is 'Male', F is 'Female', O is 'Other/Unspecified'")

    def __str__(self) -> str:
        return f"Customer(id={self.id}, name={self.name}, email={self.email}, gender={self.gender})"


class Order(BaseModel):
    id: int = Field(description="The order identifier")
    customer_id: int = Field(description="The associated customer identifier")
    product_id: int = Field(description="The associated product identifier")
    quantity: int = Field(description="The number of products ordered")
    amount: int = Field(description="The order amount")

    def __str__(self) -> str:
        return f"Order(id={self.id}, customer_id={self.customer_id}, product_id={self.product_id}, quantity={self.quantity}, amount={self.amount})"


class GetCustomersTool(BaseModel):
    """
    Returns a list of customers filtered by the non-None input parameters
    If an input parameter is None, it is not used as a filter, allowing all values for that field.
    """
    id: int | None = Field(description="The customer identifier")
    name: str | None = Field(description="The customer name")
    email: str | None = Field(description="The customer email")
    gender: Literal["M", "F", "O"] | None = Field( description="The customer's gender. M is 'Male', F is 'Female', O is 'Other/Unspecified'")

    def __str__(self) -> str:
        return f"GetCustomersInput(id={self.id}, name={self.name}, email={self.email}, gender={self.gender})"

class GetCustomerOrdersTool(BaseModel):
    """
    Returns a list of orders for the specified customer ID.
    """
    customer_id: int = Field(description="The customer identifier")

    def __str__(self) -> str:
        return f"GetCustomerOrdersInput(customer_id={self.customer_id})"