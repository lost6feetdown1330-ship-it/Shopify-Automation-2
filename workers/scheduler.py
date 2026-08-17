from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from config import settings
from agents.order_agent import OrderAgent
from agents.inventory_agent import InventoryAgent
from agents.reporter import ReporterAgent
from rich.console import Console

console = Console()


def start_scheduler():
    scheduler = BackgroundScheduler()

    if settings.enable_order_agent:
        order_agent = OrderAgent()
        scheduler.add_job(
            order_agent.run,
            IntervalTrigger(seconds=settings.poll_interval * 2),
            id="order_agent",
            replace_existing=True,
        )
        console.print("[green]OrderAgent scheduled[/green]")

    if settings.enable_inventory_agent:
        inv_agent = InventoryAgent()
        scheduler.add_job(
            inv_agent.run,
            IntervalTrigger(seconds=settings.poll_interval * 5),
            id="inventory_agent",
            replace_existing=True,
        )
        console.print("[green]InventoryAgent scheduled[/green]")

    if settings.enable_reporter:
        reporter = ReporterAgent()
        scheduler.add_job(
            reporter.run,
            CronTrigger(hour=settings.daily_report_hour, minute=0),
            id="daily_reporter",
            replace_existing=True,
        )
        console.print(f"[green]Daily Reporter scheduled for {settings.daily_report_hour}:00[/green]")

    scheduler.start()
    console.print("[bold green]All scheduled jobs started[/bold green]")
    return scheduler
