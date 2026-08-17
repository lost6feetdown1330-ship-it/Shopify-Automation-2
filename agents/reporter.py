from agents.base import BaseAgent
from shopify.client import shopify
from services.notifier import send_message_sync
from datetime import datetime


class ReporterAgent(BaseAgent):
    name = "Reporter"

    def run(self) -> None:
        self.log("Building daily report...")

        shop_data = shopify.get_shop_info()
        orders_data = shopify.get_recent_orders(first=20)

        shop_name = "Your Store"
        if "shop" in shop_data:
            shop_name = shop_data["shop"].get("name", shop_name)

        orders = orders_data.get("orders", {}).get("edges", []) if "orders" in orders_data else []

        paid_count = 0
        total_revenue = 0.0
        currency = "USD"

        for edge in orders:
            o = edge["node"]
            if o.get("displayFinancialStatus") == "PAID":
                paid_count += 1
                money = o.get("totalPriceSet", {}).get("shopMoney", {})
                try:
                    total_revenue += float(money.get("amount", 0))
                    currency = money.get("currencyCode", currency)
                except Exception:
                    pass

        report = (
            f"📊 <b>Daily Report — {shop_name}</b>\n"
            f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            f"Recent paid orders checked: <b>{paid_count}</b>\n"
            f"Approx revenue in sample: <b>{total_revenue:.2f} {currency}</b>\n\n"
            f"System is running. All agents active."
        )

        send_message_sync(report)
        self.log("Daily report sent.", "success")
