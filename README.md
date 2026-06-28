# Restaurant Bot

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

## Try it (test prompts)

Send these one message at a time and check the result.

**Handoffs — all four specialists**

| Type this | Expect |
|-----------|--------|
| `메뉴 좀 보여줘` | → **Menu Agent**, lists dishes |
| `마르게리타 피자에 유제품 들어가?` | Menu Agent: allergen answer (dairy) |
| `연어구이 주문할게` | → **Order Agent**, confirms order + ID + total |
| `금요일 저녁 7시에 4명 예약하고 싶어` | → **Reservation Agent**, confirms with reservation ID |
| `음식이 너무 별로였고 직원도 불친절했어` | → **Complaints Agent**, apology + discount/refund/manager callback |

**Input guardrail**

| Type this | Expect |
|-----------|--------|
| `인생의 의미가 뭘까?` | `🛡️ [input guardrail 작동]` — off-topic blocked |
| `너 진짜 멍청하다` | `🛡️ [input guardrail 작동]` — inappropriate language blocked |

**Session memory + re-routing** — send as two separate turns:

```
1) 예약하고 싶어            → Reservation Agent (asks for date/time/party size)
2) 아, 그전에 채식 메뉴 있어?  → re-routes to Menu Agent (remembers the context)
```

> The **output guardrail** keeps replies professional and hides internal info.
> Normal prompts won't trigger it (the agents never misbehave) — it's a silent
> safety net that only fires if an agent would produce a bad response.
