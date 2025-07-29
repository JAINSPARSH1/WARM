# WARM/core/comparator.py
"""
Compare two analysis dictionaries and highlight differences.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

def compare_dicts(a: dict, b: dict, ignore_keys: list = None) -> dict:
    """
    Compare two flat dictionaries `a` and `b`.
    Returns a mapping: key -> (value_in_a, value_in_b, is_match: bool)
    """
    ignore = set(ignore_keys or [])
    diffs = {}
    for k in sorted(set(a) | set(b)):
        if k in ignore:
            continue
        va = a.get(k, "-")
        vb = b.get(k, "-")
        diffs[k] = (va, vb, va == vb)
    return diffs

def render_comparison(
    title_a: str, data_a: dict,
    title_b: str, data_b: dict,
    ignore_keys: list = None
) -> None:
    """
    Nicely print two panels and a diff table.
    """
    ignore = set(ignore_keys or [])
    diffs = compare_dicts(data_a, data_b, ignore_keys)

    # Unified, filtered key list
    all_keys = [k for k in sorted(set(data_a) | set(data_b)) if k not in ignore]

    # PANEL A
    tbl_a = Table(box=box.SIMPLE, show_header=False)
    for k in all_keys:
        tbl_a.add_row(f"[bold]{k}[/bold]", str(data_a.get(k, "-")))
    panel_a = Panel(tbl_a, title=f"[cyan]{title_a}[/cyan]", expand=True)

    # PANEL B
    tbl_b = Table(box=box.SIMPLE, show_header=False)
    for k in all_keys:
        tbl_b.add_row(f"[bold]{k}[/bold]", str(data_b.get(k, "-")))
    panel_b = Panel(tbl_b, title=f"[magenta]{title_b}[/magenta]", expand=True)

    console.print(panel_a, panel_b, sep="\n\n")

    # DIFF TABLE
    diff_tbl = Table(box=box.MINIMAL_HEAVY_HEAD)
    diff_tbl.add_column("Metric", style="bold")
    diff_tbl.add_column(title_a, overflow="fold")
    diff_tbl.add_column(title_b, overflow="fold")
    diff_tbl.add_column("Match?", justify="center")

    # Sort so mismatches appear first
    for k, (va, vb, match) in sorted(diffs.items(), key=lambda kv: kv[1][2]):
        style = None if match else "on red"
        diff_tbl.add_row(
            k,
            str(va),
            str(vb),
            "[green]✓[/]" if match else "[red]✗[/]",
            style=style
        )

    console.print(Panel(diff_tbl, title="[bold red]Cross-comparison[/bold red]"))

