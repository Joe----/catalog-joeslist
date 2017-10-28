# Catalog Project

Joeslist is a web application written in python to demonstrate CRUD.

## Features

All rubric requirements are met:

1. Implements JSON endpoints for list of categories, list of items in a category, and data for each item.
2. Reads category and item information from a database.
3. Includes a form allowing users to add new items and correctly processes submitted form.
4. Includes a form to edit/update a current record in the database table and correctly processes submitted form.
5. Includes a function to delete a current record.
6. Create, delete, and update operations consider authorization status prior to execution.
7. Implements Google+ authentication & authorization service.
8. 'Login' and 'Logout' links exist and are dynamic depending on current state.
9. Code is ready for personal review and neatly formatted and compliant with the Python PEP 8 style guide.
10. Comments are present to explain longer code procedures.
11. This README file includes details of all the steps required to successfully run the application.
12. Responsive design using bootstrap
13. When logged in, users can edit or delete their own posts directly from the list of all postings.
14. Home page displays most recent posts.
15. Leftside nav contains categories.
16. Includes a load file to populate the database.
17. Uses flash messages for database actions and includes messages in page titles for better accessibility.
18. Uses glyphicons with action links and a favicon for the site.
19. Uses int data type for miles and float for prices and formats prices to dollars on output.
20. EXTRA: Uses Bleach.

## Software Prerequisites

Python 2.7.9

## Install and Run the Web Application

1. Create the joeslist.db sqlite database:

    python database_setup.py

2. Populate the database with some data:

    python load_cars.py

3. Start the webserver and run the application:

    python application.py

4. Open http://localhost:8000/

## Author

* **Joe Burkhart** [email](mailto:jb822f@att.com)

## License

This project may be licensed by Udacity.

## Acknowledgments

* Udacity
