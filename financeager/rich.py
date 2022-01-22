from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import DEFAULT_BASE_ENTRY_SORT_KEY, DEFAULT_CATEGORY_ENTRY_SORT_KEY


def richify_listings(
    listings,
    stacked_layout=False,
    category_sort=None,
    category_percentage=False,
    entry_sort=None,
):
    tables = []
    category_sort = category_sort or DEFAULT_CATEGORY_ENTRY_SORT_KEY
    entry_sort = entry_sort or DEFAULT_BASE_ENTRY_SORT_KEY

    totals = [ls.total_value() for ls in listings]
    # Build tables for listings
    for listing, total in zip(listings, totals):
        table = Table(
            title=listing.name, show_edge=False, box=box.SIMPLE_HEAVY, expand=True
        )
        table.add_column("Name")
        table.add_column("Value", justify="right")
        table.add_column("%" if category_percentage else "Date", justify="right")
        table.add_column("" if category_percentage else "ID", justify="right")
        tables.append(table)

        for category in sorted(
            listing.categories, key=lambda e: getattr(e, category_sort)
        ):
            percent = ""
            if category_percentage:
                percent = f"{100 * category.value / total:.1f}"
            table.add_row(
                category.name.title(),
                f"{category.value:0.2f}",
                percent,
                "",
                style="bold",
            )
            if category_percentage:
                continue

            for entry in sorted(category.entries, key=lambda e: getattr(e, entry_sort)):
                # Add two spaces for indent
                table.add_row(
                    f"  {entry.name.title()}",
                    f"{entry.value:.2f}",
                    entry.date,
                    str(entry.eid),
                )

    # Bottom panels for listing totals
    panels = [
        Panel(f"Total: {total:.2f}", style="bold", box=box.HORIZONTALS)
        for total in totals
    ]

    grid = Table.grid(expand=False, pad_edge=True, padding=(0, 1, 0, 1))
    grid.add_column(min_width=50)

    if stacked_layout:
        # Single column
        grid.add_row(tables[0])
        grid.add_row(panels[0])
        grid.add_row(tables[1])
        grid.add_row(panels[1])
    else:
        # Two columns side-by-side
        grid.add_column(min_width=50)
        grid.add_row(*tables)
        grid.add_row(*panels)

    diff = totals[0] - totals[1]
    grid.add_row(Panel(f"Difference: {diff:.2f}"), style="red" if diff < 0 else "green")

    Console().print(grid)
    return ""
