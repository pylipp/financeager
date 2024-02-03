"""Tabular, frontend-representation of financeager pocket."""

from json import dumps as jdumps

from . import DEFAULT_TABLE, RECURRENT_TABLE
from .entries import BaseEntry, CategoryEntry
from .rich import richify_listings, richify_recurrent_elements


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


def prettify(
    elements,
    recurrent_only=False,
    json=False,
    default_category=None,
    **listing_options,
):
    """Sort the given elements (type acc. to Pocket._search_all_tables) by
    positive and negative value and print tabular representation.

    :param json: If True, return elements as JSON-formatted string
    :param recurrent_only: If True, assume that given elements are purely
        recurrent ones
    :param listing_options: Options passed to rich.richify_listings()
    """
    if json:
        return jdumps(elements)

    if recurrent_only:
        entry_sort = listing_options.get("entry_sort")
        return richify_recurrent_elements(elements, entry_sort=entry_sort)

    listings = _derive_listings(elements, default_category=default_category)
    return richify_listings(listings, **listing_options)


def _derive_listings(elements, *, default_category):
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
        return

    listing_earnings = Listing.from_elements(
        earnings, default_category=default_category, name="Earnings"
    )
    listing_expenses = Listing.from_elements(
        expenses, default_category=default_category, name="Expenses"
    )
    return [listing_earnings, listing_expenses]
