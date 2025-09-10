from rich.panel import Panel
from rich.text import Text
from rich.align import Align

# Project title styling
def get_banner():
    # Title styling
    title = Text("BibleMate AI", style="bold magenta", justify="center")
    title.stylize("bold magenta underline", 0, len("BibleMate AI"))
    # Tagline styling
    tagline = Text("Automate Your Bible Study", style="bold cyan", justify="center")
    # Combine into a panel
    banner_content = Align.center(
        Text("\n") + title + Text("\n") + tagline + Text("\n"),
        vertical="middle"
    )
    banner = Panel(
        banner_content,
        border_style="bright_blue",
        title="🚀 Praise the Lord!",
        title_align="left",
        subtitle="Eliran Wong",
        subtitle_align="right",
        padding=(1, 4)
    )
    return banner