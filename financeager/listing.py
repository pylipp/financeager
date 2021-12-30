"""Tabular, frontend-representation of financeager pocket."""
from . import DEFAULT_CATEGORY_ENTRY_SORT_KEY, DEFAULT_TABLE, RECURRENT_TABLE
from .entries import BaseEntry, CategoryEntry


class Listing:
    """Holds Entries in hierarchical order. First-level children are
    CategoryEntries, second-level children are BaseEntries. Generator methods
    are provided to iterate over these."""

    def __init__(self, name=None, categories=None):
        self.name = name or "Listing"
        self.categories = categories or []

    @classmethod
    def from_elements(cls, elements, default_category=None, name=None):
        """Create listing from list of element dictionaries"""
        listing = cls(name=name)
        for element in elements:
            category = element.pop("category", None) or default_category
            listing.add_entry(BaseEntry(**element), category_name=category)
        return listing

    def prettify(
        self, *, category_sort=None, category_percentage=False, **entry_options
    ):
        """Format listing (incl. name and header).
        Category entries are sorted acc. to the given 'category_sort'.
        'entry_options' are passed to CategoryEntry.string().
        The header lists the relevant item types of BaseEntry, or, if
        'category_percentage' is set, an indicator for a column that displays
        the share in the listing total of each category.

        :return: str
        """
        result = ["{1:^{0}}".format(CategoryEntry.TOTAL_LENGTH, self.name)]

        if category_percentage:
            entry_options["total_listing_value"] = self.total_value()

            # yapf: disable
            header_line = "{3:{0}} {4:{1}} {5:>{2}} {6}".format(
                CategoryEntry.NAME_LENGTH, BaseEntry.VALUE_LENGTH,
                BaseEntry.DATE_LENGTH,
                *[k.capitalize() for k in BaseEntry.ITEM_TYPES[:2]], "%",
                BaseEntry.EID_LENGTH * " ")
            # yapf: enable

        else:
            header_line = "{3:{0}} {4:{1}} {5:{2}}".format(
                CategoryEntry.NAME_LENGTH,
                BaseEntry.VALUE_LENGTH,
                BaseEntry.DATE_LENGTH,
                *[k.capitalize() for k in BaseEntry.ITEM_TYPES],
            )
            if BaseEntry.SHOW_EID:
                header_line += " " + "ID".ljust(BaseEntry.EID_LENGTH)

        result.append(header_line)

        category_sort = category_sort or DEFAULT_CATEGORY_ENTRY_SORT_KEY
        sort_key = lambda e: getattr(e, category_sort)
        for category in sorted(self.categories, key=sort_key):
            result.append(category.string(**entry_options))

        return "\n".join(result)

    def add_entry(self, entry, category_name=None):
        """Add a Category- or BaseEntry to the listing.
        Category names are unique, i.e. a CategoryEntry is discarded if one
        with identical name (case INsensitive) already exists.
        When adding a BaseEntry, the parent CategoryEntry is created if it does
        not exist. If no category is specified, the BaseEntry is added to the
        default category.

        :raises: TypeError if neither CategoryEntry nor BaseEntry given
        """
        if isinstance(entry, CategoryEntry):
            if entry.name not in self.category_entry_names:
                self.categories.append(entry)
        elif isinstance(entry, BaseEntry):
            category_entry = self._get_category_entry(category_name)
            category_entry.append(entry)
        else:
            raise TypeError(f"Invalid entry type: {entry}")

    def category_fields(self, field_type):
        """Generator iterating over the field specified by `field_type` of the
        first-level children (CategoryEntries) of the listing.

        :param field_type: 'name' or 'value'

        raises: KeyError if `field_type` not found.
        yields: str or float
        """
        for category_entry in self.categories:
            yield getattr(category_entry, field_type)

    @property
    def category_entry_names(self):
        """Convenience generator method yielding category names."""
        for category_name in self.category_fields("name"):
            yield category_name

    def _get_category_entry(self, category_name):
        """Fetch CategoryEntry searching for given `category_name` or return a
        new instance that is automatically added to the Listing's categories.
        The search is case insensitive.

        :return: CategoryEntry
        """
        category_name = category_name.lower()

        for category_entry in self.categories:
            if category_entry.name == category_name:
                return category_entry
        else:
            # Nothing found in existing categories
            category_entry = CategoryEntry(name=category_name)
            self.add_entry(category_entry)
            return category_entry

    def total_value(self):
        """Return total value of the listing."""
        return sum(v for v in self.category_fields("value"))


def prettify(elements, stacked_layout=False, recurrent_only=False, **listing_options):
    """Sort the given elements (type acc. to Pocket._search_all_tables) by
    positive and negative value and return pretty string build from the
    corresponding Listings.

    :param stacked_layout: If True, listings are displayed one by one
    :param recurrent_only: If True, assume that given elements are purely
        recurrent ones, and return them formatted as table
    :param listing_options: Options passed to Listing.prettify(), and
        Listing.from_elements()
    """

    if recurrent_only:
        fields = ["id", "name", "value", "category", "start", "end", "frequency"]
        field_lengths = {f: len(f) for f in fields}
        # Determine max. field length and convert some field types
        for element in elements:
            element["category"] = element["category"] or "Unspecified"
            element["end"] = element["end"] or "-"
            for field, length in field_lengths.items():
                field_lengths[field] = max(length, len(str(element[field])))

        sep = " | "
        # Add all-uppercase header row
        lines = [sep.join(f.upper().ljust(l) for f, l in field_lengths.items())]

        def _format(element, field):
            # Numeric values shall be right-aligned, others left-aligned
            if field in ["id", "value"]:
                return str(element[field]).rjust(field_lengths[field])
            return element[field].capitalize().ljust(field_lengths[field])

        # Sort elements acc. to 'entry_sort' option, and format them
        entry_sort = listing_options.get("entry_sort") or "id"
        entry_sort = "id" if entry_sort == "eid" else entry_sort
        for element in sorted(elements, key=lambda e: e[entry_sort]):
            lines.append(sep.join(_format(element, f) for f in fields))

        return "\n".join(lines)

    earnings = []
    expenses = []

    def _sort(eid, element):
        # Copying avoids modifying the original element. Flattening is in order
        # to distinguish recurrent entries (they have the same element ID which
        # thus can't be used as dict key)
        flat_element = element.copy()
        flat_element["eid"] = eid
        if flat_element["value"] > 0:
            earnings.append(flat_element)
        else:
            expenses.append(flat_element)

    # process standard elements
    for eid, element in elements[DEFAULT_TABLE].items():
        _sort(eid, element)

    # process recurrent elements, i.e. for each eid iterate list
    for eid, recurrent_elements in elements[RECURRENT_TABLE].items():
        for element in recurrent_elements:
            _sort(eid, element)

    if not earnings and not expenses:
        return ""

    default_category = listing_options.pop("default_category", None)
    listing_earnings = Listing.from_elements(
        earnings, default_category=default_category, name="Earnings"
    )
    listing_expenses = Listing.from_elements(
        expenses, default_category=default_category, name="Expenses"
    )
    listings = [listing_earnings, listing_expenses]

    total_values = []
    total_entries = []
    for listing in listings:
        total_entry = CategoryEntry(name="TOTAL")
        total_entry.value = listing.total_value()
        total_values.append(total_entry.value)
        total_entries.append(total_entry.string())

    # Compute difference of total earnings and expenses
    diff_entry = CategoryEntry(name="Difference")
    diff_entry.value = total_values[0] - total_values[1]
    diff_entry = diff_entry.string()

    if stacked_layout:
        line = CategoryEntry.TOTAL_LENGTH * "="
        return "{}\n{}\n{}\n\n{}\n{}\n{}\n{}".format(
            listing_earnings.prettify(**listing_options),
            line,
            total_entries[0],
            listing_expenses.prettify(**listing_options),
            line,
            total_entries[1],
            diff_entry,
        )
    else:
        result = []
        listings_str = [ls.prettify(**listing_options).splitlines() for ls in listings]
        for row in zip(*listings_str):
            result.append(" | ".join(row))
        earnings_size = len(listings_str[0])
        expenses_size = len(listings_str[1])
        diff = earnings_size - expenses_size
        if diff > 0:
            for row in listings_str[0][expenses_size:]:
                result.append(row + " | ")
        else:
            for row in listings_str[1][earnings_size:]:
                result.append(CategoryEntry.TOTAL_LENGTH * " " + " | " + row)
        # add 3 to take central separator " | " into account
        result.append((2 * CategoryEntry.TOTAL_LENGTH + 3) * "=")

        # add total value of earnings and expenses, and difference thereof
        result.append(" | ".join(total_entries))
        result.append(diff_entry)

        return "\n".join(result)
