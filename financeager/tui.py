"""
Module defining a TUI frontend of financeager data.
"""

import urwid
from urwidtrees.tree import SimpleTree
from urwidtrees.widgets import TreeBox
from urwidtrees.decoration import CollapsibleIndentedTree
from tinydb import where

from .model import Model


class FocusableText(urwid.WidgetWrap):
    """Class providing selectable text."""

    def __init__(self, txt):
        t = urwid.Text(txt)
        w = urwid.AttrMap(t, 'body', 'focus')
        super().__init__(w)

    def selectable(self):
        return True

    def keypress(self, size, key):
        return key


class VimColumns(urwid.Columns):
    """Columns subclass supporting horizontal navigation via h and l key as
    well as scrolling (page up/down) via Ctrl-u/Ctrl-d."""

    def keypress(self, size, key):
        # check for contents[self.focus_position]._tree parent/child position
        if key in ['left', 'h']:
            self.focus_position = 0 if self.focus_position == 1 else 1
            return
        elif key in ['right', 'l']:
            self.focus_position = 1 if self.focus_position == 0 else 0
            return
        elif key == "ctrl d":
            return super().keypress(size, "page down")
        elif key == "ctrl u":
            return super().keypress(size, "page up")
        return super().keypress(size, key)


class VimTreeBox(TreeBox):
    """TreeBox subclass supporting vertical navigation via k and l key."""

    def keypress(self, size, key):
        w, focuspos = self.get_focus()
        if key == 'j':
            return super().keypress(size, 'down')
        elif key == 'k':
            return super().keypress(size, 'up')
        return super().keypress(size, key)


def unhandled_input(key):
    """Function to handle input keys at the highest level (MainLoop). Used to
    quit the TUI."""
    if key.lower() == 'q':
        raise urwid.ExitMainLoop()


def build_tree_from_model(model):
    """Build a tree widget from a `financeager.model.Model` object."""
    categories = []

    for category in model.categories:
        entries = []
        for entry in category.entries:
            entries.append((FocusableText(str(entry)), None))
        category_subtree = (FocusableText(str(category)), entries)
        categories.append(category_subtree)

    root = (FocusableText(model.name), categories)

    return CollapsibleIndentedTree(
            SimpleTree([root]),
            icon_focussed_at='focus'
            )


def run(response):
    """The data from the response (dict with key 'elements' containing list of
    elements in the period database) is sorted into expenses and earnings.
    Models and corresponding tree widgets are built. The TUI is constructed and
    started."""

    if not "elements" in response:
        print("tui: Error while fetching database: {}".format(
            response.get("error", "unknown")))
        return

    query = where("value") > 0
    earnings = []
    expenses = []

    for element in response["elements"]:
        if query(element):
            earnings.append(element)
        else:
            expenses.append(element)

    model_earnings = Model.from_tinydb(earnings, "Earnings")
    model_expenses = Model.from_tinydb(expenses, "Expenses")

    columns = VimColumns([
            VimTreeBox(build_tree_from_model(model_earnings)),
            VimTreeBox(build_tree_from_model(model_expenses))
            ])
    root_widget = urwid.AttrMap(columns, 'body')
    footer = urwid.AttrMap(urwid.Text('Q to quit'), 'focus')
    palette = [
            ('focus', 'light gray', 'dark blue', 'standout')
            ]
    urwid.MainLoop(
            urwid.Frame(root_widget, footer=footer),
            palette,
            unhandled_input=unhandled_input
            ).run()
