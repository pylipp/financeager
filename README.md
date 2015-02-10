FINANCEAGER
===========

A PyQt application that helps you administering your daily expenses and receipts. 

Who is this for?
----------------
You might be someone who wants to organize finances with a simple software
because you're tired of Excel and the like. 
Or you are interested in PyQt applications and like to see some example code. 

DISCLAIMER: Defs not BUG-FREE!

GENERAL USAGE
-------------
### Start
Clone this repo, change directory to `financeager/` and run

    python main.py [path/to/file]
    
If you specify an appropriate xml file, Financeager will load it and start, otherwise it will display an empty view. 
### Set a new year
Click the "New year" button (star icon) in the toolbar or type CTRL-Y. A popup will ask you to give an integer between 1 and 9999. Choose an appropriate value and click OK. The view now displays the current month with expenditures on the left and receipts on the right. It is populated with default categories. You can switch between the months by clicking a tab below the toolbar. 
### Add a new entry
Click the "New entry" button (pen icon) in the toolbar or type CTRL-N. A popup will ask you to give a name (arbitrary string), a value (floating point number, use '.' for cent fractions), a date and a category. If all fields are valid, click OK. The entry appears in the appropriate category of the current month. 
### Modify entry
Double-click on the value of the entry and type a new value. It is not
possible (yet) to modify the name or the date of an entry. 
### Remove entry
Select the entry you want to remove. Click the "Remove entry" button (red X icon) in the toolbar or press the "Delete" key. This action cannot be undone!
### Show statistics
Click the "Show statistics" button (table sheet icon) in the toolbar or type
CTRL-T. The popup gives an overview of all expenses and receipts of the
current year, listed by month. The difference (= your win/less) is
calculated, too. Pressing ESC or clicking the button again will hide the
window. 
### Show settings
Click the "Show settings" button (gear icon) in the toolbar or type CTRL-E.
In the popup you can modify category and file saving settings. 
Click the "Categories" tab: 
You can organize categories here. Remember to press "Apply" after you
made a change. Otherwise changes will be lost if you click OK.
Click the "File saving" tab:
You can specify a file name to save the current sheet to. You can also
set if you want Financeager to autosave at exit.
### Show about
Click the "About" button (question mark icon) in the toolbar or type
CTRL-A. A popup glorifying me will be displayed.
### Quit
Click the "Quit" button (door icon) in the toolbar or type CTRL-Q.
Financeager automatically saves and quits.


KNOWN BUGS
----------
- Category names can be ambiguous. That's an issue if you are about to remove a category. 
- Report. Them. 

FUTURE FEATURES
---------------
- enable modifying name and date of an entry
- implement search that displays all entries of the year matching a search pattern
- implement undo function (undo removing entries)
- apply changes in SettingsWindow when OK is clicked
