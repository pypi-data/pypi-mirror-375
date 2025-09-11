"""joepie_tools - collection of harmless prank GUI tools."""

__version__ = "0.2.0"

from .hackerprank import fake_hack_screen, fake_matrix, fake_terminal, fake_file_dump, fake_warning_popup
from .cli import main

__all__ = ["fake_hack_screen", "fake_matrix", "fake_terminal", "fake_file_dump", "fake_warning_popup", "main"]
