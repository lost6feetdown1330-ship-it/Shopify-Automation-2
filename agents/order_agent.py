from agents.base import BaseAgent
from shopify.client import shopify
from services.notifier import send_message_sync


class OrderAgent(BaseAgent):
    name = "OrderAgent"

    def run(self) -> None:
        self.log("Checking recent orders...")
        data = shopify.get_recent_orders(first=15)

        if "errors" in data:
            self.log(f"Failed to fetch orders: {data['errors']}", "error")
            return

        orders = data.get("orders", {}).get("edges", [])
        if not orders:
            self.log("No recent orders found.")
            return

        unfulfilled = []
        for edge in orders:
            order = edge["node"]
            status = order.get("displayFulfillmentStatus", "")
            financial = order.get("displayFinancialStatus", "")

            if status in ("UNFULFILLED", "PARTIAL") and financial == "PAID":
                unfulfilled.append(order)

        if unfulfilled:
            msg_lines = [f"📦 <b>{len(unfulfilled)} paid order(s) still unfulfilled:</b>"]
            for o in unfulfilled[:5]:
                total = o.get("totalPriceSet", {}).get("shopMoney", {})
                customer = o.get("customer") or {}
                name = f"{customer.get('firstName', '')} {customer.get('lastName', '')}".strip() or "Guest"
                msg_lines.append(
                    f"• {o['name']} — {total.get('amount')} {total.get('currencyCode')} — {name}"
                )
            send_message_sync("\n".join(msg_lines))
            self.log(f"Alerted about {len(unfulfilled)} unfulfilled paid orders.", "warning")
        else:
            self.log("All recent paid orders look good.", "success")
