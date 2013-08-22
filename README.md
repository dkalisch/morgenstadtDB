# morgenstadtDB #

morgenstadtDB is the database that is used in the Fraunhofer research project Morgenstadt.

## Software ##

The whole project is written in Python and uses the web framework Django. For the sake of simplicity, Twitter Bootstrap was used for styling.

## What does the project contain? ##

The project includes the complete Django web app, containing all of the models, views, settings and templates used in the morgenstadtDB. 

The project can be used as reference for the following problems:

- setting up a Django project and a database design for a research project
- working with the Django Forms API
- creating dynamic forms with Django, JavaScript and JQuery
- quick-styling with Twitter Bootstrap

## Changelog ##
Version 0.2

- Changed settings of Google API
- City data can be edited in the frontend, if the user is a "superuser"
- Improved organisation of Impact Factors in categories and the possibility to delete/connect Impact Factors dynamically to Best Practices
- Improved error-pages
- Improved usability, for example by adding extra "Save"-buttons, altering checkbox-widgets and sorting information in dropdowns
- Small bug-fixes