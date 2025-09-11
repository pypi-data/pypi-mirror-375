import logging
import msgspec
from rich import print


logger = logging.getLogger("wheel_getter")



class Reporter(msgspec.Struct):
    warnings: list[str] = []
    errors: list[str] = []
    
    def warning(self, message: str, *inserts: str) -> None:
        logger.warning(message, *inserts)
        self.warnings.append(message % inserts)
    
    def error(self, message: str, *inserts: str) -> None:
        logger.error(message, *inserts)
        self.errors.append(message % inserts)
    
    def report(self) -> int:
        weight = 0
        for m in self.warnings:
            print(f"[magenta]warning: {m}")
            weight = logging.WARNING
        for m in self.errors:
            print(f"[red]error: {m}")
            weight = logging.ERROR
        return weight
