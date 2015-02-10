###############
# FINANCEAGER #
###############

A PyQt application that helps you administering your daily expenses and receipts. 

DISCLAIMER: Defs not BUG-FREE!

GENERAL USAGE
- Start
    Clone this repo, change directory to financeager/ and run
        python main.py [file]
    If you specify an appropriate xml file, Financeager will load it and start, otherwise it will display an empty view. 
- Set a new year
    Click the "New year" button (the yellow star) in the toolbar or type CTRL-Y. A popup will ask you to give an integer between 1 and 9999. Choose an appropriate value and click OK. The view now displays the current month with expenditures on the left and receipts on the right. It is populated with default categories. You can switch between the months by clicking a tab below the toolbar. 
- Add a new entry
    Click the "New entry" button (the pen) in the toolbar or type CTRL-N. A popup will ask you to give a name (arbitrary string), a value (floating point number, use '.' for cent fractions), a date and a category. If all fields are valid, click OK. The entry appears in the appropriate category of the current month. 
