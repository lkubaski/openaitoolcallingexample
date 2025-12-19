from typing import cast

from openai import OpenAI, pydantic_function_tool
import json

from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionMessageFunctionToolCall, \
    ChatCompletionAssistantMessageParam, ChatCompletionMessageParam, ChatCompletionToolMessageParam, \
    ChatCompletionMessageToolCallParam, ChatCompletionSystemMessageParam

import config
from config import API_KEY, MODEL, SYSTEM_PROMPT
from models import GetCustomersTool, GetCustomerOrdersTool
from tools import TOOL_HANDLERS

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY
)


def answer(questions: list[str]) -> None:
    messages: list[ChatCompletionMessageParam] = [
        ChatCompletionSystemMessageParam(role="system", content=SYSTEM_PROMPT),
    ]

    for question in questions:
        print("\n---------------------------------------")
        print(f"New question='{question}'")
        print("---------------------------------------")
        messages.append(ChatCompletionUserMessageParam(role="user", content=question))

        current_loop = 0
        while current_loop <= config.MAX_LOOP:  # Prefixing with module name to avoid a mypy warning
            current_loop += 1
            print(f"\nCalling chat.completions.create() with nb messages={len(messages)}")
            tools = [
                pydantic_function_tool(GetCustomersTool),
                pydantic_function_tool(GetCustomerOrdersTool)]
            # https://platform.openai.com/docs/api-reference/chat/create
            chat_completion = client.chat.completions.create(
                model=MODEL,
                tools=tools,
                messages=messages)
            message = chat_completion.choices[0].message
            print(f"Got message={message}")

            if message.content:
                # When there are no more tools to call, the model has finished and we can print the final answer
                print("---------- BEGIN RESPONSE ---------- ")
                print(message.content)
                print("---------- END RESPONSE ---------- ")
                break
            elif message.tool_calls:
                print(f"Nb tools to call={len(message.tool_calls)}")
                # message.tool_calls is a "list[ChatCompletionMessageFunctionToolCall]"
                # But ChatCompletionAssistantMessageParam() expects a "Iterable[ChatCompletionMessageFunctionToolCallParam]" (which is an alias for ChatCompletionMessageToolCallParam)
                # However ChatCompletionMessageFunctionToolCall & ChatCompletionMessageToolCallParam are structurally identical
                # (they both have those 3 fields: id, function, type)
                # so we can just cast the list directly
                tool_calls = cast(list[ChatCompletionMessageToolCallParam], message.tool_calls)
                # The assistant "ChatCompletionMessage" output message is added to the list of messages as a "ChatCompletionAssistantMessageParam"
                messages.append(
                    ChatCompletionAssistantMessageParam(
                        role="assistant",
                        content=None,
                        tool_calls=tool_calls)
                )
                tool_message_params: list[ChatCompletionToolMessageParam] = []
                for tool_call in message.tool_calls:
                    tool_call = cast(ChatCompletionMessageFunctionToolCall, tool_call)
                    tool_output_json = None

                    try:
                        tool_arguments = json.loads(tool_call.function.arguments)
                        handler = TOOL_HANDLERS.get(tool_call.function.name)
                        if handler:
                            tool_output = handler(tool_arguments)
                            tool_output_json = json.dumps(tool_output)
                        else:
                            tool_output_json = json.dumps({"error": f"Unknown tool: {tool_call.function.name}"})
                    except Exception as e:
                        error_message = f"Error when calling tool {tool_call.function.name}: {str(e)}"
                        print(f"ERROR: {error_message}")
                        tool_output_json = json.dumps({"error": error_message})

                    """
                    try:
                        tool_arguments = json.loads(tool_call.function.arguments)
                        tool_output = None
                        print(f"calling tool={tool_call.function.name} with arguments={tool_arguments}")
                        if tool_call.function.name == "GetCustomersTool":
                            get_customers_input = GetCustomersTool(**tool_arguments)
                            customers = get_customers(get_customers_input)
                            tool_output = [customer.model_dump() for customer in customers]
                            tool_output_json = json.dumps(tool_output)
                        elif tool_call.function.name == "GetCustomerOrdersTool":
                            get_customer_orders_input = GetCustomerOrdersTool(**tool_arguments)
                            orders = get_customer_orders(get_customer_orders_input)
                            tool_output = [order.model_dump() for order in orders]
                            tool_output_json = json.dumps(tool_output)
                        else:
                            tool_output_json = json.dumps({"error": f"Unknown tool: {tool_call.function.name}"})
                    except Exception as e:
                        error_message = f"Error when calling tool {tool_call.function.name}: {str(e)}"
                        print(f"ERROR: {error_message}")
                        tool_output_json = json.dumps({"error": error_message})
                    """

                    print(f"Got tool_output_json={tool_output_json}")
                    tool_message = ChatCompletionToolMessageParam(
                        role="tool",
                        tool_call_id=tool_call.id,
                        content=tool_output_json,  # This will be the result OR the formatted error
                    )
                    tool_message_params.append(tool_message)

                messages.extend(tool_message_params)
            else:
                raise Exception(f"Model response had neither content nor tool calls")

        if current_loop == config.MAX_LOOP:
            raise Exception(f"could not get final response within {config.MAX_LOOP} iterations")


if __name__ == "__main__":
    questions = [
        "What are the orders for customer with email='alice@example.com' ?",
        "What are the orders for customer with name='Bob' ?",
        "What's the total amount of orders for customer with name='Bob' ?",
    ]
    answer(questions)
