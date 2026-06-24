# 과제 1 — Restaurant Bot

A multi-agent restaurant bot using the **OpenAI Agents SDK** `handoff` feature,
with input/output **guardrails**. A Triage agent routes each request to one of
four specialists.

| Agent | Role |
|-------|------|
| **Triage** | Figures out what the guest wants and routes to a specialist |
| **Menu** | Menu, ingredients, allergens, vegetarian options |
| **Order** | Takes and confirms food orders |
| **Reservation** | Books / changes / cancels tables |
| **Complaints** | Handles unhappy guests: empathize, offer discount/refund/manager callback, escalate serious issues |

Specialists only receive handoffs (one-directional). Each turn re-enters Triage,
so switching topics mid-chat (e.g. Reservation → Menu) routes correctly. The
Streamlit UI shows a banner on each handoff and logs tools/results in the sidebar.

## Guardrails

- **Input guardrail** (on Triage) rejects off-topic messages (not about the
  restaurant) and inappropriate / abusive language.
- **Output guardrail** (on every specialist) ensures replies stay professional
  and never expose internal info (agent names, tools, internal policies).

## Run

Requires Python 3.13+ and an OpenAI API key. Using [uv](https://docs.astral.sh/uv/):

```bash
cp .env.example .env          # paste your OPENAI_API_KEY
uv run streamlit run main.py
```

Set `tier="vip"` in `main.py` for VIP perks.

## Structure

```
main.py              # Streamlit UI, streaming, handoff + guardrail handling
models.py            # RestaurantContext, HandoffData, guardrail output models
tools.py             # Menu / order / reservation / complaints tools + hooks
output_guardrails.py # Output guardrail (professional, no internal info)
my_agent/            # triage + menu / order / reservation / complaints agents
```

## Examples

Routing / handoff (Reservation → Menu):

```
User: 예약을 하고 싶어
[Reservation Agent로 handoff]
Reservation: 예약을 도와드리겠습니다! 인원수와 희망 날짜를 알려주세요.

User: 아, 그전에 채식 메뉴 있는지 알려줘
[Menu Agent로 handoff]
Menu: 네! 여러 가지 채식 메뉴가 있습니다...
```

Complaints + input guardrail:

```
User: 음식이 너무 별로였고 직원도 불친절했어..
[Complaints Agent로 handoff]
Complaints: 불쾌한 경험을 드려 진심으로 사과드립니다. 다음 방문 시 할인을
            드리거나 매니저가 직접 연락드리도록 하겠습니다...

User: 인생의 의미가 뭘까?
[input guardrail 작동]
Bot: 저는 레스토랑 관련 질문(메뉴, 주문, 예약)에 대해서만 도와드릴 수 있어요.
```
