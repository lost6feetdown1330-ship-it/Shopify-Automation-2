"""
Shopify Autopilot 2 — main entry point
Runs the background agents + a lightweight webhook server for Shopify / Flow.
"""

import time
import threading
from fastapi import FastAPI, Request
from rich.console import Console
from rich.panel import Panel
from config import settings
from shopify.client import shopify
from workers.scheduler import start_scheduler
from services.notifier import send_message_sync
import uvicorn

console = Console()
app = FastAPI(title="Shopify Autopilot 2")


@app.get("/")
def health():
    return {"status": "online", "system": "Shopify Autopilot 2"}


@app.post("/webhooks/shopify")
async def shopify_webhook(request: Request):
    """Receive native Shopify webhooks."""
    try:
        body = await request.json()
        topic = request.headers.get("X-Shopify-Topic", "unknown")
        console.print(f"[cyan]Shopify webhook received: {topic}[/cyan]")
        # Future: route to specific agents based on topic
        return {"ok": True}
    except Exception as e:
        console.print(f"[red]Webhook error: {e}[/red]")
        return {"ok": False}


@app.post("/webhooks/flow")
async def flow_webhook(request: Request):
    """Receive HTTP requests sent from Shopify Flow."""
    try:
        body = await request.json()
        console.print("[magenta]Shopify Flow webhook received[/magenta]")
        console.print(body)
        send_message_sync(f"⚡ <b>Flow event received</b>\n<pre>{str(body)[:800]}</pre>")
        return {"ok": True, "received": True}
    except Exception as e:
        console.print(f"[red]Flow webhook error: {e}[/red]")
        return {"ok": False}


def banner():
    console.print(Panel.fit(
        "[bold magenta]Shopify Autopilot 2[/bold magenta]\n"
        "Do-Everything Edition + Flow Support\n"
        "Agents + Webhooks running...",
        border_style="magenta"
    ))


def health_check():
    console.print("[cyan]Running health check against Shopify...[/cyan]")
    data = shopify.get_shop_info()
    if "shop" in data:
        shop = data["shop"]
        console.print(f"[green]Connected to store: {shop.get('name')}[/green]")
        console.print(f"[dim]Plan: {shop.get('plan', {}).get('displayName', 'unknown')} | Currency: {shop.get('currencyCode')}[/dim]")
        return True
    else:
        console.print("[red]Failed to connect to Shopify. Check your .env credentials.[/red]")
        console.print(data)
        return False


def run_api():
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")


def main():
    banner()

    if not health_check():
        console.print("[bold red]Exiting — fix credentials and try again.[/bold red]")
        return

    send_message_sync("🚀 <b>Shopify Autopilot 2 is now online</b>\nAgents + Flow webhooks ready.")

    # Start background agents
    scheduler = start_scheduler()

    # Start webhook server in a separate thread
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    console.print("[green]Webhook server running on port 8000[/green]")
    console.print("[dim]POST /webhooks/shopify  and  POST /webhooks/flow[/dim]")

    console.print("[bold]System is live. Press Ctrl+C to stop.[/bold]")

    try:
        while True:
            time.sleep(30)
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down gracefully...[/yellow]")
        scheduler.shutdown()
        send_message_sync("🛑 Shopify Autopilot 2 stopped.")


if __name__ == "__main__":
    main()
