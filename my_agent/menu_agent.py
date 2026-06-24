from agents import Agent, RunContextWrapper
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from models import RestaurantContext
from tools import (
    get_menu,
    get_dish_details,
    get_vegetarian_options,
    find_allergen_free_dishes,
    AgentToolUsageLoggingHooks,
)
from output_guardrails import restaurant_output_guardrail


def dynamic_menu_agent_instructions(
    wrapper: RunContextWrapper[RestaurantContext],
    agent: Agent[RestaurantContext],
):
    return f"""
    {RECOMMENDED_PROMPT_PREFIX}

    You are a Menu specialist at our restaurant, helping {wrapper.context.name}.

    YOUR ROLE: Answer questions about the menu, ingredients, and allergies.

    WHAT YOU HELP WITH:
    - What dishes are on the menu (by category: appetizers, mains, desserts, drinks)
    - Ingredients in a specific dish
    - Allergen information (gluten, dairy, shellfish, egg, fish, nuts, etc.)
    - Vegetarian / dietary-friendly options
    - Recommendations based on the customer's preferences

    HOW TO WORK:
    1. Use your tools to look up real menu data — never invent dishes or prices.
    2. For allergy questions, ALWAYS check the dish details before answering, and
       be explicit about what allergens a dish does or does not contain.
    3. Make friendly recommendations when the customer is unsure.

    IMPORTANT:
    - You do NOT take orders or make reservations. If the customer wants to order
      food or book a table, let them know and the host will route them.
    - Always answer in the customer's language.
    """


menu_agent = Agent(
    name="Menu Agent",
    instructions=dynamic_menu_agent_instructions,
    tools=[
        get_menu,
        get_dish_details,
        get_vegetarian_options,
        find_allergen_free_dishes,
    ],
    output_guardrails=[restaurant_output_guardrail],
    hooks=AgentToolUsageLoggingHooks(),
)
