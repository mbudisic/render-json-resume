"""Base generator class."""

from abc import ABC, abstractmethod
from pathlib import Path

from ..schema import Resume


class BaseGenerator(ABC):
    """Abstract base class for document generators."""
    
    def __init__(self, resume: Resume, style: str = "professional"):
        self.resume = resume
        self.style = style
    
    @abstractmethod
    def generate(self, output_path: Path) -> None:
        """Generate the document and save to output_path."""
        pass
    
    def format_date_range(self, start: str | None, end: str | None) -> str:
        """Format a date range for display."""
        if not start and not end:
            return ""
        if start and not end:
            return f"{self._format_date(start)} - Present"
        if not start and end:
            return f"Until {self._format_date(end)}"
        return f"{self._format_date(start)} - {self._format_date(end)}"
    
    def _format_date(self, date_str: str) -> str:
        """Format a date string for display."""
        if not date_str:
            return ""
        parts = date_str.split("-")
        if len(parts) >= 2:
            year = parts[0]
            month = parts[1]
            months = [
                "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
            ]
            try:
                month_idx = int(month) - 1
                if 0 <= month_idx < 12:
                    return f"{months[month_idx]} {year}"
            except ValueError:
                pass
        return date_str
