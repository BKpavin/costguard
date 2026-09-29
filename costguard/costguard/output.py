"""
Output formatting module for CostGuard.
Renders beautiful terminal tables and summaries using rich library.
"""

from typing import Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text


def render_cost_report(impact_data: Dict[str, Any], guardrail_limit: Optional[float] = None) -> None:
    """
    Render formatted cost prediction report to stdout using rich terminal components.

    Args:
        impact_data: Dictionary output from calculate_cost_impact.
        guardrail_limit: Optional threshold limit for display banner.
    """
    console = Console()
    currency = impact_data.get("currency", "USD")
    items = impact_data.get("itemized", [])
    net_delta = impact_data.get("net_monthly_delta", 0.0)

    # Build Rich Table
    table = Table(title="CostGuard - Monthly Azure Infrastructure Impact", title_style="bold blue")
    table.add_column("Resource Address", style="cyan", no_wrap=True)
    table.add_column("Type", style="magenta")
    table.add_column("Action", style="yellow", justify="center")
    table.add_column(f"Previous ({currency})", justify="right")
    table.add_column(f"New ({currency})", justify="right")
    table.add_column(f"Delta ({currency})", justify="right")

    for item in items:
        action = item["action"]

        # Action formatting
        if action == "create":
            action_str = f"[bold green]+ {action}[/bold green]"
        elif action == "delete":
            action_str = f"[bold red]- {action}[/bold red]"
        elif action == "update":
            action_str = f"[bold yellow]~ {action}[/bold yellow]"
        else:
            action_str = f"[dim]{action}[/dim]"

        delta = item["delta_monthly"]
        delta_str = f"+${delta:.2f}" if delta > 0 else (f"-${abs(delta):.2f}" if delta < 0 else "$0.00")
        if delta > 0:
            delta_str = f"[red]{delta_str}[/red]"
        elif delta < 0:
            delta_str = f"[green]{delta_str}[/green]"
        else:
            delta_str = f"[dim]{delta_str}[/dim]"

        table.add_row(
            item["address"],
            item["type"],
            action_str,
            f"${item['previous_monthly']:.2f}",
            f"${item['new_monthly']:.2f}",
            delta_str,
        )

    console.print()
    console.print(table)

    # Summary panel
    prev_total = impact_data.get("total_previous_monthly", 0.0)
    new_total = impact_data.get("total_new_monthly", 0.0)
    
    summary_text = Text()
    summary_text.append(f"Current Monthly Total:  ${prev_total:.2f} {currency}\n")
    summary_text.append(f"Proposed Monthly Total: ${new_total:.2f} {currency}\n")

    if net_delta > 0:
        summary_text.append(f"Net Monthly Delta:      +${net_delta:.2f} {currency}", style="bold red")
    elif net_delta < 0:
        summary_text.append(f"Net Monthly Delta:      -${abs(net_delta):.2f} {currency}", style="bold green")
    else:
        summary_text.append(f"Net Monthly Delta:       ${net_delta:.2f} {currency}", style="bold green")

    if guardrail_limit is not None:
        summary_text.append(f"\nGuardrail Threshold:    ${guardrail_limit:.2f} {currency}")
        if net_delta > guardrail_limit:
            summary_text.append(" (BREACHED)", style="bold red")
        else:
            summary_text.append(" (PASSED)", style="bold green")

    panel = Panel(
        summary_text,
        title="[bold]Monthly Cost Summary[/bold]",
        border_style="red" if (guardrail_limit and net_delta > guardrail_limit) else "green"
    )
    console.print(panel)
