from agents.base import BaseAgent
from shopify.client import shopify
from services.notifier import send_message_sync


class InventoryAgent(BaseAgent):
    name = "InventoryAgent"
    LOW_STOCK_THRESHOLD = 5

    def run(self) -> None:
        self.log("Checking inventory levels...")
        data = shopify.get_inventory_levels(first=100)

        if "errors" in data:
            self.log(f"Failed to fetch inventory: {data['errors']}", "error")
            return

        variants = data.get("productVariants", {}).get("edges", [])
        low_stock = []

        for edge in variants:
            v = edge["node"]
            qty = v.get("inventoryQuantity")
            if qty is not None and qty <= self.LOW_STOCK_THRESHOLD:
                low_stock.append(v)

        if low_stock:
            msg_lines = [f"⚠️ <b>Low stock alert ({len(low_stock)} items):</b>"]
            for v in low_stock[:8]:
                product_title = v.get("product", {}).get("title", "Unknown")
                msg_lines.append(
                    f"• {product_title} — {v.get('title')} (SKU: {v.get('sku') or 'n/a'}) → <b>{v.get('inventoryQuantity')}</b> left"
                )
            send_message_sync("\n".join(msg_lines))
            self.log(f"Alerted about {len(low_stock)} low-stock variants.", "warning")
        else:
            self.log("Inventory levels look healthy.", "success")
