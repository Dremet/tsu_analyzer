# tsu_analyzer

Saves event stats files from [Turbo Sliders Unlimited](https://www.turbosliders.com/home) to a database in a very structured way.

It uses pdm for python library management, sqlalchemy object-relational-mappers and alembic for database change management.

It is made to provide the data for the TSU community website [tsura.org](https://tsura.org).

## Files

When you host a dedicated server ([more information on dedicated servers in TSU](https://www.turbosliders.com/help/dedicated-servers)) you can activate that the server should save eventstats.json files. You can see some examples [here](/examples/).

## Data

If you want to know which data is saved, have a look at the [models.py](/src/tsu_analyzer/db/models.py) file. Every single checkpoint time can be saved.

## Config

Create a .env file and define this variable:
TSU_HOTLAPPING_POSTGRES_URL=postgresql://user:password@host/database

Obviously, you can change the variable name when you change it in the scripts as well. 

In order to run this, you need to have a database with a "tsu" schema, run alembic migrations and then run models.py.