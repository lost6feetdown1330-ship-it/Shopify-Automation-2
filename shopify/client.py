"""
Smart Shopify GraphQL client with basic rate limiting and retries.
"""

import time
import httpx
from typing import Any, Dict, Optional
from config import settings
from rich.console import Console

console = Console()


class ShopifyClient:
    def __init__(self):
        self.shop = settings.shopify_shop.replace("https://", "").replace("http://", "").rstrip("/")
        self.token = settings.shopify_access_token
        self.api_version = settings.shopify_api_version
        self.endpoint = f"https://{self.shop}/admin/api/{self.api_version}/graphql.json"
        self._last_request = 0.0
        self._min_interval = 0.5  # rough protection against hammering

    def _headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.token,
        }

    def execute(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Simple throttle
        elapsed = time.time() - self._last_request
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)

        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        for attempt in range(3):
            try:
                with httpx.Client(timeout=30.0) as client:
                    resp = client.post(self.endpoint, json=payload, headers=self._headers())
                    self._last_request = time.time()

                    if resp.status_code == 429:
                        # Rate limited – wait and retry
                        wait = float(resp.headers.get("Retry-After", 2))
                        console.print(f"[yellow]Rate limited. Waiting {wait}s...[/yellow]")
                        time.sleep(wait)
                        continue

                    resp.raise_for_status()
                    data = resp.json()

                    if "errors" in data:
                        console.print(f"[red]GraphQL errors: {data['errors']}[/red]")
                        return {"errors": data["errors"]}

                    return data.get("data", {})

            except Exception as e:
                console.print(f"[red]Shopify request failed (attempt {attempt+1}): {e}[/red]")
                time.sleep(1.5 * (attempt + 1))

        return {"errors": ["Max retries exceeded"]}

    # ---------- Convenience methods ----------

    def get_shop_info(self) -> Dict[str, Any]:
        query = """
        {
          shop {
            name
            email
            currencyCode
            primaryDomain { url }
            plan { displayName }
          }
        }
        """
        return self.execute(query)

    def get_recent_orders(self, first: int = 10) -> Dict[str, Any]:
        query = """
        query ($first: Int!) {
          orders(first: $first, sortKey: CREATED_AT, reverse: true) {
            edges {
              node {
                id
                name
                createdAt
                displayFinancialStatus
                displayFulfillmentStatus
                totalPriceSet { shopMoney { amount currencyCode } }
                customer { firstName lastName email }
                lineItems(first: 10) {
                  edges {
                    node {
                      title
                      quantity
                      sku
                    }
                  }
                }
              }
            }
          }
        }
        """
        return self.execute(query, {"first": first})

    def get_inventory_levels(self, first: int = 50) -> Dict[str, Any]:
        query = """
        query ($first: Int!) {
          productVariants(first: $first) {
            edges {
              node {
                id
                title
                sku
                inventoryQuantity
                product { title }
              }
            }
          }
        }
        """
        return self.execute(query, {"first": first})


# Singleton
shopify = ShopifyClient()
