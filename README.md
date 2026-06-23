# 과제 1 — Restaurant Bot

A multi-agent restaurant bot using the **OpenAI Agents SDK** `handoff` feature.
A Triage agent routes each request to one of three specialists.

| Agent | Role |
|-------|------|
| **Triage** | Figures out what the guest wants and routes to a specialist |
| **Menu** | Menu, ingredients, allergens, vegetarian options |
| **Order** | Takes and confirms food orders |
| **Reservation** | Books / changes / cancels tables |

Specialists only receive handoffs (one-directional). Each turn re-enters Triage,
so switching topics mid-chat (e.g. Reservation → Menu) routes correctly. The
Streamlit UI shows a banner on each handoff and logs tools/results in the sidebar.

## Run

Requires Python 3.13+ and an OpenAI API key. Using [uv](https://docs.astral.sh/uv/):

```bash
cp .env.example .env          # paste your OPENAI_API_KEY
uv run streamlit run main.py
```

Set `tier="vip"` in `main.py` for VIP perks.

## Structure

```
main.py            # Streamlit UI, streaming, handoff display
models.py          # RestaurantContext, HandoffData, guardrail output
tools.py           # Menu / order / reservation tools + logging hooks
my_agent/          # triage_agent, menu_agent, order_agent, reservation_agent
```

## Example

```
User: 예약을 하고 싶어
[Reservation Agent로 handoff]
Reservation: 예약을 도와드리겠습니다! 인원수와 희망 날짜를 알려주세요.

User: 아, 그전에 채식 메뉴 있는지 알려줘
[Menu Agent로 handoff]
Menu: 네! 여러 가지 채식 메뉴가 있습니다...
```
