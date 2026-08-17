# Shopify Autopilot 2 — The Do-Everything Edition

Full autonomous system for your Shopify store + **Shopify Flow** integration.

**Goal:** You do almost nothing after setup.

---

## What this system does

### Custom Agents (this repo)
- Continuously monitors paid but unfulfilled orders → alerts your phone
- Tracks inventory and screams before you stock out
- Daily summary report to your phone
- Structured logging + human-in-the-loop safety
- Ready for stronger AI later

### Shopify Flow (native)
We recommend running **both**. Flow handles simple reliable native triggers. Our agents handle continuous monitoring + phone alerts + more complex logic.

---

## Setup (3 steps max)

### 1. Create a private Shopify app

1. Shopify admin → Settings → Apps and sales channels → Develop apps
2. Create app
3. Admin API scopes (minimum):
   - `read_products`, `write_products`
   - `read_orders`, `write_orders`
   - `read_inventory`, `write_inventory`
   - `read_customers`
   - `read_fulfillments`, `write_fulfillments`
4. Install → copy Admin API access token + your `yourstore.myshopify.com`

### 2. Configure `.env`

```bash
cp .env.example .env
```

Fill in:

```env
SHOPIFY_SHOP=yourstore.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_xxxxxxxx
SHOPIFY_API_VERSION=2025-10

# Strongly recommended for iPhone alerts
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

### 3. Run it

```bash
docker compose up -d
```

or

```bash
pip install -r requirements.txt
python main.py
```

---

## Shopify Flow Recommended Workflows

Set these up in **Shopify Admin → Apps → Flow**. They complement the agents perfectly.

### 1. High-Value Order Alert
- **Trigger:** Order created
- **Condition:** Order total > $150 (or whatever number you want)
- **Action:** Send internal email / Slack / Telegram notification  
  (or use “Send HTTP request” to hit our webhook if you want the agents to also react)

### 2. Low Inventory Tagging
- **Trigger:** Inventory quantity changed
- **Condition:** Inventory quantity ≤ 5
- **Action:** Add product tag `low-stock` + send internal notification

### 3. Unfulfilled Order Escalation
- **Trigger:** Scheduled (every day)
- **Get data:** Orders that are paid + unfulfilled + created > 48 hours ago
- **Action:** Tag the order `needs-attention` + notify you

### 4. New Customer Welcome + Tag
- **Trigger:** Customer created
- **Action:** Add tag `new-customer` + send welcome email (via Shopify Email or Klaviyo connector)

### 5. Cancelled Order Cleanup
- **Trigger:** Order cancelled
- **Action:** Remove any “vip” or special tags, add `cancelled`, notify if it was a high-value order

### 6. Flow → Our Agents (optional power move)
You can make Flow call our system:
- In any Flow workflow, add action **Send HTTP request**
- Point it at: `https://your-server.com/webhooks/flow`
- Body can include whatever data you want
- Our system will log it and can react (we can expand this later)

---

## Webhook Support (already built)

The system now has a basic webhook endpoint so Shopify or Flow can push events instead of pure polling.

Once the server is running, endpoints available:
- `POST /webhooks/shopify` — for native Shopify webhooks
- `POST /webhooks/flow` — for Shopify Flow HTTP requests

---

## Project Structure

```
main.py                 → starts agents + webhook server
config.py
shopify/client.py       → GraphQL client
agents/                 → Order, Inventory, Reporter
services/notifier.py    → Telegram / phone alerts
workers/scheduler.py
```

---

## Safety

- High-risk actions stay behind approval
- Everything is logged
- Start on a development store if you’re nervous
- Agents can be toggled in `config.py`

---

Want me to add abandoned cart recovery, AI product description rewriting, or a full support reply agent next? Just say it.
