import streamlit as st
from agents import (
    Agent,
    RunContextWrapper,
    input_guardrail,
    Runner,
    GuardrailFunctionOutput,
    handoff,
)
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from agents.extensions import handoff_filters
from models import RestaurantContext, InputGuardRailOutput, HandoffData
from my_agent.menu_agent import menu_agent
from my_agent.order_agent import order_agent
from my_agent.reservation_agent import reservation_agent


input_guardrail_agent = Agent(
    name="Input Guardrail Agent",
    instructions="""
    Ensure the user's request is about our restaurant — the menu, ingredients,
    allergies, placing a food order, or making a table reservation. Friendly small
    talk (greetings, thanks) is fine, especially at the start of the conversation.
    If the request is clearly off-topic (e.g. unrelated to dining at our
    restaurant), return a reason for the tripwire.
""",
    output_type=InputGuardRailOutput,
)


@input_guardrail
async def off_topic_guardrail(
    wrapper: RunContextWrapper[RestaurantContext],
    agent: Agent[RestaurantContext],
    input: str,
):
    result = await Runner.run(
        input_guardrail_agent,
        input,
        context=wrapper.context,
    )

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_off_topic,
    )


def dynamic_triage_agent_instructions(
    wrapper: RunContextWrapper[RestaurantContext],
    agent: Agent[RestaurantContext],
):
    return f"""
    {RECOMMENDED_PROMPT_PREFIX}


    You are the host (Triage agent) of our restaurant. You greet the guest and
    figure out WHAT they want, then connect them to the right specialist.
    You call guests by their name.

    The guest's name is {wrapper.context.name}.
    The guest's email is {wrapper.context.email}.
    The guest's tier is {wrapper.context.tier}.

    YOUR MAIN JOB: Understand the guest's request and route them to ONE specialist.

    ROUTING GUIDE:

    🍽️ MENU AGENT — route here for:
    - Questions about the menu, dishes, prices
    - Ingredients in a dish
    - Allergy / allergen questions
    - Vegetarian or dietary options
    - "What vegetarian dishes do you have?", "Does the pizza contain dairy?"

    🧾 ORDER AGENT — route here for:
    - Placing a food order
    - Checking or changing an existing order
    - "I'd like to order the salmon", "What's the status of my order?"

    📅 RESERVATION AGENT — route here for:
    - Booking, changing, or cancelling a table
    - "I want to make a reservation", "Can I move my booking to 8pm?"

    HOW TO HAND OFF:
    1. Understand the request. Ask ONE clarifying question only if it's unclear.
    2. Tell the guest you're connecting them, e.g.
       "메뉴 전문가에게 연결합니다..." or "Connecting you to our reservation specialist...".
    3. Then hand off to the matching specialist agent.

    IMPORTANT:
    - Route to exactly ONE specialist per request.
    - If the guest changes topic (e.g. was ordering, now asks about the menu),
      route them to the new matching specialist.
    - Always answer in the guest's language.
    """


def handle_handoff(
    wrapper: RunContextWrapper[RestaurantContext],
    input_data: HandoffData,
):

    with st.sidebar:
        st.write(
            f"""
            Handing off to {input_data.to_agent_name}
            Reason: {input_data.reason}
            Request Type: {input_data.request_type}
            Description: {input_data.request_description}
        """
        )


def make_handoff(agent):

    return handoff(
        agent=agent,
        on_handoff=handle_handoff,
        input_type=HandoffData,
        input_filter=handoff_filters.remove_all_tools,
    )


triage_agent = Agent(
    name="Triage Agent",
    instructions=dynamic_triage_agent_instructions,
    input_guardrails=[
        off_topic_guardrail,
    ],
    handoffs=[
        make_handoff(menu_agent),
        make_handoff(order_agent),
        make_handoff(reservation_agent),
    ],
)
