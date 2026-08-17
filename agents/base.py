from abc import ABC, abstractmethod
from rich.console import Console

console = Console()


class BaseAgent(ABC):
    name: str = "BaseAgent"

    def __init__(self):
        self.console = console

    @abstractmethod
    def run(self) -> None:
        """Execute one cycle of the agent."""
        pass

    def log(self, message: str, level: str = "info") -> None:
        color = {
            "info": "cyan",
            "success": "green",
            "warning": "yellow",
            "error": "red",
        }.get(level, "white")
        self.console.print(f"[{color}][{self.name}] {message}[/{color}]")
