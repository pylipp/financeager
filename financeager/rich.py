from rich import box
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
    """Create and return rich.Table from listings acc. to given options.
    :param stacked_layout: If True, listings are displayed one by one
    :param category_sort: Field governing category sorting (name, value)
    :param category_percentage: If True, display the share in the listing total of each
        category
    :param entry_sort: Field governing base entry sorting (name, value, date, ID)
    """
    if not listings:
        return "No entries found."

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

    def nr_rows(listing):
        if category_percentage:
            return len(listing.categories)
        return len(listing.categories) + sum(len(c.entries) for c in listing.categories)

    # Fill shorter table with empty rows
    if not stacked_layout:
        nr_earnings_rows = nr_rows(listings[0])
        nr_expenses_rows = nr_rows(listings[1])
        nr_rows_diff = nr_earnings_rows - nr_expenses_rows
        shorter_table = tables[1] if nr_rows_diff > 0 else tables[0]
        for _ in range(abs(nr_rows_diff)):
            shorter_table.add_row("")

    # Bottom rows for listing totals
    for table, total in zip(tables, totals):
        table.add_row("")
        table.add_row("Total", f"{total:.2f}", "", "", style="bold")

    grid = Table.grid(expand=False, pad_edge=True, padding=(0, 1, 0, 1))
    grid.add_column(min_width=50)

    if stacked_layout:
        # Single column
        grid.add_row(tables[0])
        grid.add_row(tables[1])
    else:
        # Two columns side-by-side
        grid.add_column(min_width=50)
        grid.add_row(*tables)

    diff = totals[0] - totals[1]
    grid.add_row(Panel(f"Difference: {diff:.2f}"), style="red" if diff < 0 else "green")
    return grid


def richify_recurrent_elements(elements, entry_sort=None):
    """Create and return rich.Table from recurrent elements acc. to given options.
    :param entry_sort: Field governing base entry sorting (name, value, ID, category,
        start, end, frequency)
    """
    fields = ["eid", "name", "value", "category", "start", "end", "frequency"]
    table = Table(
        show_edge=False, box=box.SIMPLE_HEAVY, expand=False, row_styles=["i", ""]
    )
    for field in fields:
        field = "id" if field == "eid" else field
        table.add_column(
            field.upper(), justify="right" if field in ["id", "value"] else "left"
        )

    entry_sort = entry_sort or "eid"
    for element in sorted(elements, key=lambda e: e[entry_sort]):
        element["category"] = element["category"] or "Unspecified"
        element["end"] = element["end"] or "-"
        table.add_row(
            *[
                str(element[f]).capitalize() if f != "value" else f"{element[f]:.2f}"
                for f in fields
            ]
        )
    return table
