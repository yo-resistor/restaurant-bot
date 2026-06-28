import dotenv

dotenv.load_dotenv()
from openai import OpenAI
import asyncio
import streamlit as st
from agents import (
    Runner,
    SQLiteSession,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
)
from models import RestaurantContext
from my_agent.triage_agent import triage_agent

client = OpenAI()

st.title("🍝 Restaurant Bot")
st.caption("메뉴 문의 · 주문 · 예약 · 불만 접수를 도와드려요.")

with st.expander("ℹ️ 사용 방법"):
    st.markdown(
        """
        - **메뉴 / 재료 / 알레르기** → "채식 메뉴 있어?"
        - **주문** → "연어구이 주문할게"
        - **예약** → "금요일 저녁 7시에 4명 예약하고 싶어"
        - **불만** → "음식이 별로였어요"

        아래 버튼으로 바로 시작할 수도 있어요.
        레스토랑과 무관하거나 부적절한 말은 자동으로 차단돼요.
        """
    )

# Quick-start buttons — clicking one sends an example prompt for the user.
QUICK_PROMPTS = {
    "🍽️ 메뉴 보기": "채식 메뉴 있어?",
    "🧾 주문하기": "연어구이 주문할게",
    "📅 예약하기": "금요일 저녁 7시에 4명 예약하고 싶어",
    "😟 불만 접수": "음식이 너무 별로였어요",
}
quick_clicked = None
for col, (label, prompt) in zip(st.columns(len(QUICK_PROMPTS)), QUICK_PROMPTS.items()):
    if col.button(label, use_container_width=True):
        quick_clicked = prompt

guest_ctx = RestaurantContext(
    customer_id=1,
    name="yun",
    email="yun@email.com",
    phone="010-1234-5678",
    tier="regular",  # change to "vip" to see VIP perks
)


if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession(
        "chat-history",
        "restaurant-bot-memory.db",
    )
session = st.session_state["session"]

if "agent" not in st.session_state:
    st.session_state["agent"] = triage_agent


async def paint_history():
    messages = await session.get_items()
    for message in messages:
        if "role" in message:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    st.write(message["content"])
                else:
                    if message["type"] == "message":
                        st.write(message["content"][0]["text"].replace("$", r"\$"))


asyncio.run(paint_history())


async def run_agent(message):

    # Always start each turn from the Triage agent so it can (re)route the guest
    # to the right specialist — e.g. Reservation now, Menu on the next question.
    # The session memory still carries the full conversation history.
    st.session_state["agent"] = triage_agent

    with st.chat_message("ai"):
        text_placeholder = st.empty()
        response = ""

        st.session_state["text_placeholder"] = text_placeholder

        try:

            stream = Runner.run_streamed(
                st.session_state["agent"],
                message,
                session=session,
                context=guest_ctx,
            )

            async for event in stream.stream_events():
                if event.type == "raw_response_event":

                    if event.data.type == "response.output_text.delta":
                        response += event.data.delta
                        text_placeholder.write(response.replace("$", r"\$"))

                elif event.type == "agent_updated_stream_event":

                    if st.session_state["agent"].name != event.new_agent.name:

                        st.info(f"➡️ Handed off to the **{event.new_agent.name}**")

                        st.session_state["agent"] = event.new_agent

                        text_placeholder = st.empty()

                        st.session_state["text_placeholder"] = text_placeholder
                        response = ""

        except InputGuardrailTripwireTriggered as e:
            # The agent may have already streamed some text before the guardrail
            # tripped (they run concurrently), so erase it first.
            st.session_state["text_placeholder"].empty()
            st.warning("🛡️ [input guardrail 작동]")
            info = e.guardrail_result.output.output_info
            if getattr(info, "is_inappropriate", False):
                st.write(
                    "정중한 대화를 부탁드려요. 메뉴, 주문, 예약은 기꺼이 도와드릴게요. 🙂"
                )
            else:
                st.write(
                    "저는 레스토랑 관련 질문(메뉴, 주문, 예약)에 대해서만 도와드릴 수 있어요. 🙂"
                )

        except OutputGuardrailTripwireTriggered:
            st.session_state["text_placeholder"].empty()
            st.warning("🛡️ [output guardrail 작동]")
            st.write("죄송하지만 그 답변은 보여드릴 수 없어요. 다시 도와드릴게요. 🙏")


message = st.chat_input(
    "메뉴 문의, 주문, 예약 또는 불만을 입력하세요",
) or quick_clicked

if message:
    with st.chat_message("human"):
        st.write(message)
    asyncio.run(run_agent(message))


with st.sidebar:
    st.header("🔍 Behind the scenes")
    st.caption(f"Active agent: {st.session_state['agent'].name}")
    reset = st.button("Reset memory")
    if reset:
        asyncio.run(session.clear_session())
    st.write(asyncio.run(session.get_items()))
