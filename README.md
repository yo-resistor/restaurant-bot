# 과제 1 — Restaurant Bot

A multi-agent restaurant bot built with the **OpenAI Agents SDK** `handoff` feature,
following the same structure as the customer-support project.

## Agents

| Agent | Role |
|-------|------|
| **Triage Agent** | Greets the guest, figures out what they want, routes to one specialist |
| **Menu Agent** | Menu, ingredients, allergens, vegetarian options |
| **Order Agent** | Takes and confirms food orders |
| **Reservation Agent** | Books / changes / cancels tables |

The Triage agent uses `handoff()` to route requests. When a handoff happens the UI
shows a banner ("🔄 Connecting you to the **Menu Agent**...") and the sidebar logs
the transfer, tool calls, and results.

## Structure

```
restaurant-bot/
├── main.py                 # Streamlit chat UI + streaming + handoff display
├── models.py               # RestaurantContext, HandoffData, guardrail output
├── tools.py                # Menu / order / reservation tools + logging hooks
└── my_agent/
    ├── triage_agent.py     # Routing + handoffs + off-topic guardrail
    ├── menu_agent.py
    ├── order_agent.py
    └── reservation_agent.py
```

## Setup & Run

Requires Python 3.13+ and an OpenAI API key. Using [uv](https://docs.astral.sh/uv/):

```bash
# 1. add your API key
cp .env.example .env        # then edit .env and paste your OPENAI_API_KEY

# 2. run (uv installs the dependencies automatically)
uv run streamlit run main.py
```

Set `tier="vip"` in `main.py` to see VIP perks (priority kitchen, VIP seating).

## Example flow

```
User: 예약을 하고 싶어
Triage: 예약 담당에게 연결해 드릴게요...
[Reservation Agent로 handoff]
Reservation: 예약을 도와드리겠습니다! 인원수와 희망 날짜를 알려주세요.

User: 아, 그전에 채식 메뉴 있는지 알려줘
[Menu Agent로 handoff]
Menu: 네! 여러 가지 채식 메뉴가 있습니다...
```
