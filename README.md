# ClusteredData Warehouse!
#### Video Demo:  <https://youtu.be/Cbkz9I-Ck64>
#### Description:


The app I made is to be used by the employees at progressSoft corporation to add fx deals and
check the details of deals from a databse.I used sqlite for the database.

A good thing is that its a single database that is shared with all employees
which makes it possible for an employee to check deals added by his/her colleagues.

deals.db consists of two tables first one is users to register employees and the
second is deals to register fx deal, and user_id in deals relates to which employee
added the fx deal.
In the navigation bar there is the following tabs check deal, add a deal, Deals database
and employee deals.

there is an error message displayed through apology.html when an employee tries to add a deal
in which there is a deal in the databse with the exact Deal Id.
Displaying a message : invalid deal id, deal id already exists.

in index.html when filling the inputs from_iso_code and to_iso_code by an employee there is a code in python to check the
the codes are valid , to do so I created an array called ISO and whatever is submitted in the forms by the employee
is checked with the ISO array to make sure its a valid code.

application.py contains the python code to register and login eployees.
add a new deal and check an existing deals details.

Done by: Waseem Hoshe



