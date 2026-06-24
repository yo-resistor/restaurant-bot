from agents import Agent, RunContextWrapper
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from models import RestaurantContext
from tools import (
    place_order,
    get_order_status,
    add_special_request,
    AgentToolUsageLoggingHooks,
)
from output_guardrails import restaurant_output_guardrail


def dynamic_order_agent_instructions(
    wrapper: RunContextWrapper[RestaurantContext],
    agent: Agent[RestaurantContext],
):
    return f"""
    {RECOMMENDED_PROMPT_PREFIX}

    You are an Order specialist at our restaurant, helping {wrapper.context.name}.
    Customer tier: {wrapper.context.tier} {"(VIP — priority kitchen)" if wrapper.context.is_vip() else ""}

    YOUR ROLE: Take food orders and confirm them.

    ORDER PROCESS:
    1. Confirm exactly which dishes the customer wants.
    2. Use the place_order tool to register the order and get a total + order ID.
    3. Read back the order ID, the items, the total, and the estimated prep time.
    4. Offer to add any special requests (allergies, no onions, extra spicy, etc.)
       using the add_special_request tool.
    5. If they ask about an existing order, use get_order_status.

    IMPORTANT:
    - Only order dishes that exist on the menu. If the customer asks for something
      you can't find, tell them and suggest they ask the Menu specialist.
    - Always clearly CONFIRM the order back to the customer before finishing.
    - Answer in the customer's language.
    """


order_agent = Agent(
    name="Order Agent",
    instructions=dynamic_order_agent_instructions,
    tools=[
        place_order,
        get_order_status,
        add_special_request,
    ],
    output_guardrails=[restaurant_output_guardrail],
    hooks=AgentToolUsageLoggingHooks(),
)
