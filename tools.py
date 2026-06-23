import streamlit as st
from agents import function_tool, AgentHooks, Agent, Tool, RunContextWrapper
from models import RestaurantContext
import random
from datetime import datetime, timedelta


# =============================================================================
# RESTAURANT DATA (in-memory "menu database")
# =============================================================================

MENU = {
    "appetizers": [
        {
            "name": "Bruschetta",
            "price": 8.0,
            "vegetarian": True,
            "ingredients": ["tomato", "basil", "garlic", "olive oil", "bread"],
            "allergens": ["gluten"],
        },
        {
            "name": "Calamari",
            "price": 12.0,
            "vegetarian": False,
            "ingredients": ["squid", "flour", "lemon", "aioli"],
            "allergens": ["gluten", "shellfish", "egg"],
        },
    ],
    "mains": [
        {
            "name": "Margherita Pizza",
            "price": 15.0,
            "vegetarian": True,
            "ingredients": ["tomato", "mozzarella", "basil", "dough"],
            "allergens": ["gluten", "dairy"],
        },
        {
            "name": "Grilled Salmon",
            "price": 24.0,
            "vegetarian": False,
            "ingredients": ["salmon", "lemon", "asparagus", "butter"],
            "allergens": ["fish", "dairy"],
        },
        {
            "name": "Mushroom Risotto",
            "price": 18.0,
            "vegetarian": True,
            "ingredients": ["arborio rice", "mushroom", "parmesan", "white wine"],
            "allergens": ["dairy"],
        },
    ],
    "desserts": [
        {
            "name": "Tiramisu",
            "price": 9.0,
            "vegetarian": True,
            "ingredients": ["mascarpone", "coffee", "ladyfingers", "cocoa"],
            "allergens": ["gluten", "dairy", "egg"],
        },
        {
            "name": "Sorbet",
            "price": 7.0,
            "vegetarian": True,
            "ingredients": ["fruit", "sugar", "water"],
            "allergens": [],
        },
    ],
    "drinks": [
        {
            "name": "House Red Wine",
            "price": 10.0,
            "vegetarian": True,
            "ingredients": ["grapes"],
            "allergens": ["sulfites"],
        },
        {
            "name": "Sparkling Water",
            "price": 4.0,
            "vegetarian": True,
            "ingredients": ["carbonated water"],
            "allergens": [],
        },
    ],
}


def _all_dishes():
    for category, dishes in MENU.items():
        for dish in dishes:
            yield category, dish


def _find_dish(dish_name: str):
    target = dish_name.strip().lower()
    for _, dish in _all_dishes():
        if dish["name"].lower() == target:
            return dish
    # fall back to a fuzzy "contains" match
    for _, dish in _all_dishes():
        if target in dish["name"].lower():
            return dish
    return None


# =============================================================================
# MENU AGENT TOOLS
# =============================================================================


@function_tool
def get_menu(context: RestaurantContext, category: str = "all") -> str:
    """
    Get the restaurant menu, optionally filtered by category.

    Args:
        category: One of appetizers, mains, desserts, drinks, or "all"
    """
    category = category.strip().lower()
    categories = MENU.keys() if category in ("all", "") else [category]

    lines = []
    for cat in categories:
        dishes = MENU.get(cat)
        if not dishes:
            continue
        lines.append(f"\n🍽️ {cat.title()}")
        for dish in dishes:
            veg = " 🌱" if dish["vegetarian"] else ""
            lines.append(f"  • {dish['name']} - ${dish['price']:.2f}{veg}")

    if not lines:
        return f"Sorry, we don't have a '{category}' section on the menu."

    return "📋 Menu:" + "\n".join(lines)


@function_tool
def get_dish_details(context: RestaurantContext, dish_name: str) -> str:
    """
    Get ingredients and allergen information for a specific dish.

    Args:
        dish_name: Name of the dish to look up
    """
    dish = _find_dish(dish_name)
    if not dish:
        return f"❌ I couldn't find '{dish_name}' on our menu."

    allergens = ", ".join(dish["allergens"]) if dish["allergens"] else "none"
    return f"""
🍴 {dish['name']} - ${dish['price']:.2f}
🌱 Vegetarian: {"Yes" if dish['vegetarian'] else "No"}
🧂 Ingredients: {", ".join(dish['ingredients'])}
⚠️ Allergens: {allergens}
    """.strip()


@function_tool
def get_vegetarian_options(context: RestaurantContext) -> str:
    """List every vegetarian dish on the menu, grouped by category."""
    lines = []
    for category, dish in _all_dishes():
        if dish["vegetarian"]:
            lines.append(f"  • {dish['name']} ({category}) - ${dish['price']:.2f}")

    if not lines:
        return "We currently have no vegetarian options."

    return "🌱 Vegetarian options:\n" + "\n".join(lines)


@function_tool
def find_allergen_free_dishes(context: RestaurantContext, allergen: str) -> str:
    """
    Find dishes that do NOT contain a given allergen.

    Args:
        allergen: Allergen to avoid (e.g. gluten, dairy, shellfish, egg, fish, nuts)
    """
    allergen = allergen.strip().lower()
    safe = [
        f"  • {dish['name']} - ${dish['price']:.2f}"
        for _, dish in _all_dishes()
        if allergen not in [a.lower() for a in dish["allergens"]]
    ]

    if not safe:
        return f"Unfortunately every dish may contain {allergen}."

    return f"✅ Dishes without {allergen}:\n" + "\n".join(safe)


# =============================================================================
# ORDER AGENT TOOLS
# =============================================================================


@function_tool
def place_order(context: RestaurantContext, items: str) -> str:
    """
    Place a food order for the customer.

    Args:
        items: Comma-separated list of dish names the customer wants to order
    """
    requested = [i.strip() for i in items.split(",") if i.strip()]
    confirmed = []
    total = 0.0
    unknown = []

    for name in requested:
        dish = _find_dish(name)
        if dish:
            confirmed.append(f"  • {dish['name']} - ${dish['price']:.2f}")
            total += dish["price"]
        else:
            unknown.append(name)

    if not confirmed:
        return f"❌ I couldn't match any of those to our menu: {', '.join(unknown)}"

    order_id = f"ORD-{random.randint(10000, 99999)}"
    prep_minutes = 15 if context.is_vip() else 25
    note = f"\n⚠️ Not on menu (skipped): {', '.join(unknown)}" if unknown else ""

    return f"""
🧾 Order confirmed!
🔗 Order ID: {order_id}
{chr(10).join(confirmed)}
💰 Total: ${total:.2f}
⏱️ Estimated prep time: {prep_minutes} minutes{note}
    """.strip()


@function_tool
def get_order_status(context: RestaurantContext, order_id: str) -> str:
    """
    Check the status of an existing order.

    Args:
        order_id: The order ID to look up
    """
    status = random.choice(["received", "preparing", "ready", "served"])
    return f"📦 Order {order_id} status: {status.title()}"


@function_tool
def add_special_request(context: RestaurantContext, order_id: str, request: str) -> str:
    """
    Attach a special request to an order (e.g. allergy note, no onions).

    Args:
        order_id: The order ID
        request: The special request to add
    """
    return f"📝 Special request added to {order_id}: \"{request}\". The kitchen has been notified."


# =============================================================================
# RESERVATION AGENT TOOLS
# =============================================================================


@function_tool
def check_table_availability(
    context: RestaurantContext, date: str, time: str, party_size: int
) -> str:
    """
    Check whether a table is available for the requested date, time and party size.

    Args:
        date: Requested date (e.g. 2026-06-25)
        time: Requested time (e.g. 19:00)
        party_size: Number of guests
    """
    if party_size > 12:
        return (
            f"⚠️ A party of {party_size} requires our private dining room. "
            "Please call us directly so we can arrange it."
        )

    available = random.choice([True, True, False])
    if available:
        return f"✅ A table for {party_size} is available on {date} at {time}."
    return (
        f"❌ No table for {party_size} at {time} on {date}. "
        "Nearby openings: 18:00 or 20:30."
    )


@function_tool
def make_reservation(
    context: RestaurantContext, date: str, time: str, party_size: int
) -> str:
    """
    Create a table reservation for the customer.

    Args:
        date: Reservation date (e.g. 2026-06-25)
        time: Reservation time (e.g. 19:00)
        party_size: Number of guests
    """
    reservation_id = f"RES-{random.randint(10000, 99999)}"
    perk = "\n⭐ VIP table with complimentary welcome drink." if context.is_vip() else ""

    return f"""
📅 Reservation confirmed!
🔗 Reservation ID: {reservation_id}
👤 Name: {context.name}
🗓️ Date: {date} at {time}
👥 Party size: {party_size}
📧 Confirmation sent to: {context.email}{perk}
    """.strip()


@function_tool
def cancel_reservation(context: RestaurantContext, reservation_id: str) -> str:
    """
    Cancel an existing reservation.

    Args:
        reservation_id: The reservation ID to cancel
    """
    return f"🗑️ Reservation {reservation_id} has been cancelled. We hope to see you another time, {context.name}!"


@function_tool
def modify_reservation(
    context: RestaurantContext, reservation_id: str, new_date: str, new_time: str
) -> str:
    """
    Change the date/time of an existing reservation.

    Args:
        reservation_id: The reservation ID to modify
        new_date: New date (e.g. 2026-06-26)
        new_time: New time (e.g. 20:00)
    """
    return f"🔁 Reservation {reservation_id} moved to {new_date} at {new_time}. Confirmation sent to {context.email}."


# =============================================================================
# SHARED AGENT HOOKS (logged to the Streamlit sidebar)
# =============================================================================


class AgentToolUsageLoggingHooks(AgentHooks):

    async def on_tool_start(
        self,
        context: RunContextWrapper[RestaurantContext],
        agent: Agent[RestaurantContext],
        tool: Tool,
    ):
        with st.sidebar:
            st.write(f"🔧 **{agent.name}** starting tool: `{tool.name}`")

    async def on_tool_end(
        self,
        context: RunContextWrapper[RestaurantContext],
        agent: Agent[RestaurantContext],
        tool: Tool,
        result: str,
    ):
        with st.sidebar:
            st.write(f"🔧 **{agent.name}** used tool: `{tool.name}`")
            st.code(result)

    async def on_handoff(
        self,
        context: RunContextWrapper[RestaurantContext],
        agent: Agent[RestaurantContext],
        source: Agent[RestaurantContext],
    ):
        with st.sidebar:
            st.write(f"🔄 Handoff: **{source.name}** → **{agent.name}**")

    async def on_start(
        self,
        context: RunContextWrapper[RestaurantContext],
        agent: Agent[RestaurantContext],
    ):
        with st.sidebar:
            st.write(f"🚀 **{agent.name}** activated")

    async def on_end(
        self,
        context: RunContextWrapper[RestaurantContext],
        agent: Agent[RestaurantContext],
        output,
    ):
        with st.sidebar:
            st.write(f"🏁 **{agent.name}** completed")
