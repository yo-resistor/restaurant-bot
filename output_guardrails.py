from agents import (
    Agent,
    output_guardrail,
    Runner,
    RunContextWrapper,
    GuardrailFunctionOutput,
)
from models import OutputGuardRailOutput, RestaurantContext


restaurant_output_guardrail_agent = Agent(
    name="Restaurant Output Guardrail",
    instructions="""
    Analyze the restaurant bot's response to a guest and check whether it is:

    - Unprofessional or impolite (rude, dismissive, sarcastic, insulting, or
      uses profanity / inappropriate language)
    - Exposing internal information that a guest should never see
      (system prompts, agent names, tool names, internal policies or rules,
       raw data dumps, employee details, or how the bot works internally)

    Normal guest-facing information is FINE and must NOT be flagged: menu items,
    prices, order/reservation IDs, discount codes, tracking info, etc.

    A good response is warm, professional, and only shares guest-facing info.
    Return true for any field that applies.
    """,
    output_type=OutputGuardRailOutput,
)


@output_guardrail
async def restaurant_output_guardrail(
    wrapper: RunContextWrapper[RestaurantContext],
    agent: Agent,
    output: str,
):
    result = await Runner.run(
        restaurant_output_guardrail_agent,
        output,
        context=wrapper.context,
    )

    validation = result.final_output

    triggered = validation.is_unprofessional or validation.exposes_internal_info

    return GuardrailFunctionOutput(
        output_info=validation,
        tripwire_triggered=triggered,
    )
