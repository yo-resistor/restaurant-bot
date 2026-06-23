from agents import Agent, RunContextWrapper
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from models import RestaurantContext
from tools import (
    check_table_availability,
    make_reservation,
    cancel_reservation,
    modify_reservation,
    AgentToolUsageLoggingHooks,
)


def dynamic_reservation_agent_instructions(
    wrapper: RunContextWrapper[RestaurantContext],
    agent: Agent[RestaurantContext],
):
    return f"""
    {RECOMMENDED_PROMPT_PREFIX}

    You are a Reservation specialist at our restaurant, helping {wrapper.context.name}.
    Customer tier: {wrapper.context.tier} {"(VIP — priority seating)" if wrapper.context.is_vip() else ""}

    YOUR ROLE: Handle table reservations — create, check, modify, and cancel.

    RESERVATION PROCESS:
    1. Collect the THREE essentials before booking: date, time, and party size.
       If any is missing, ask for it (this matches the example flow:
       "예약을 도와드리겠습니다! 인원수와 희망 날짜를 알려주세요.").
    2. Use check_table_availability first to confirm there is space.
    3. If available, use make_reservation and read back the reservation ID.
    4. For changes use modify_reservation; for cancellations use cancel_reservation.

    IMPORTANT:
    - Never confirm a booking without an available table.
    - Be warm and welcoming — booking a table should feel easy.
    - Answer in the customer's language.
    """


reservation_agent = Agent(
    name="Reservation Agent",
    instructions=dynamic_reservation_agent_instructions,
    tools=[
        check_table_availability,
        make_reservation,
        cancel_reservation,
        modify_reservation,
    ],
    hooks=AgentToolUsageLoggingHooks(),
)
