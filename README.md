# Shopify Autopilot 2 — The Do-Everything Edition

This is the full autonomous system for your Shopify store.

It watches orders, inventory, customers, products, and support.
It acts where it's safe.
It asks you (via phone notification) when it needs human approval for anything risky.

**Goal:** You do almost nothing after setup.

---

## What it actually does right now

- Continuously monitors new orders and flags issues
- Tracks inventory levels and alerts before you stock out
- Basic customer support drafting + order status replies (with approval gate)
- Daily summary report pushed to your phone
- Structured logging so you can see exactly what it did
- Human-in-the-loop for refunds, price changes, bulk edits, etc.
- Ready for you to drop in stronger AI models later

---

## Setup (seriously, try to keep it to 3 steps)

### 1. Create a private Shopify app + get credentials

1. Go to your Shopify admin → Settings → Apps and sales channels → Develop apps
2. Create a new app
3. Configure Admin API scopes (start with these):
   - `read_products`, `write_products`
   - `read_orders`, `write_orders`
   - `read_inventory`, `write_inventory`
   - `read_customers`
   - `read_fulfillments`, `write_fulfillments`
4. Install the app on your store
5. Copy the **Admin API access token** and your store name (`yourstore.myshopify.com`)

### 2. Fill the `.env` file

```bash
cp .env.example .env
```

Then edit `.env` with your real values:

```env
SHOPIFY_SHOP=yourstore.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SHOPIFY_API_VERSION=2025-10

# Optional but highly recommended for phone notifications
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Optional – for stronger AI later
OPENAI_API_KEY=
```

### 3. Run it

**Easiest way (Docker):**

```bash
docker compose up -d
```

**Or locally:**

```bash
pip install -r requirements.txt
python main.py
```

That's it. The system starts watching your store.

---

## How you control it from your iPhone

- Daily reports and alerts come through Telegram (set it up once)
- When the agent wants to do something risky (refund, big inventory change, etc.), it will send you a message with Approve / Reject buttons (or simple reply)
- You can also check the logs or hit the simple status endpoint

---

## Project Structure

```
main.py                 → starts everything
config.py               → loads settings
shopify/client.py       → smart GraphQL client with rate limiting
agents/                 → specialized agents (order, inventory, support...)
services/notifier.py    → phone notifications
workers/scheduler.py    → background jobs
```

---

## Important Safety Notes

- High-risk actions (refunds, price changes, deleting products, etc.) are **blocked by default** and require your explicit approval.
- All actions are logged.
- Start in a development store if you're nervous.
- You can turn individual agents on/off in `config.py`.

---

Built to be extended. Want me to add abandoned cart recovery, product description rewriting, competitor price watching, or full AI support agent next? Just say the word.
