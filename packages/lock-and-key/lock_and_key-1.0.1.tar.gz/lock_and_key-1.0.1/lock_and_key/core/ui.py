"""UI utilities for Lock & Key."""

from rich.console import Console
from rich.panel import Panel


def print_banner() -> None:
    """Print the Lock & Key banner."""
    console = Console()
    banner = r"""
[bold cyan]

( \      (  ___  )(  ____ \| \    /\    /__\    | \    /\(  ____ \|\     /|
| (      | (   ) || (    \/|  \  / /   ( \/ )   |  \  / /| (    \/( \   / )
| |      | |   | || |      |  (_/ /     \  /    |  (_/ / | (__     \ (_) /
| |      | |   | || |      |   _ (      /  \/\  |   _ (  |  __)     \   /
| |      | |   | || |      |  ( \ \    / /\  /  |  ( \ \ | (         ) (
| (____/\| (___) || (____/\|  /  \ \  (  \/  \  |  /  \ \| (____/\   | |
(_______/(_______)(_______/|_/    \/   \___/\/  |_/    \/(_______/   \_/

[/bold cyan]
    """
    console.print(
        Panel(
            banner,
            title="Lock & Key Cloud Scanner",
            subtitle="by The Winter Shadow",
            style="bold magenta",
        )
    )
