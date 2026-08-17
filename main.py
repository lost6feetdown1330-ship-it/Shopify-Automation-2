"""
Shopify Autopilot 2 — main entry point
"""

import time
from rich.console import Console
from rich.panel import Panel
from config import settings
from shopify.client import shopify
from workers.scheduler import start_scheduler
from services.notifier import send_message_sync

console = Console()


def banner():
    console.print(Panel.fit(
        "[bold magenta]Shopify Autopilot 2[/bold magenta]\n"
        "Do-Everything Edition\n"
        "Running continuous agents...",
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


def main():
    banner()

    if not health_check():
        console.print("[bold red]Exiting — fix credentials and try again.[/bold red]")
        return

    send_message_sync("🚀 <b>Shopify Autopilot 2 is now online</b>\nAgents are watching your store.")

    scheduler = start_scheduler()

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
