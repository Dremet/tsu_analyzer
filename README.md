# tsu_analyzer

Saves event stats files from [Turbo Sliders Unlimited](https://www.turbosliders.com/home) to a database in a very structured way.

It uses pdm for python library management, sqlalchemy object-relational-mappers and alembic for database change management.

It is made to provide the data for the TSU community website [tsura.org](https://tsura.org).

## Thanks!

Thanks to McVizn for the idea, thanks to Ande for replying quickly to all questions I had and thanks to the whole community for being awesome! :)

## Files

When you host a dedicated server ([more information on dedicated servers in TSU](https://www.turbosliders.com/help/dedicated-servers)) you can activate that the server should save eventstats.json files. You can see some examples [here](/examples/).

When the next event ends, the file will be overwritten though which is why I placed two files into the `config/Scripts/` directory:
1. eventend.src with `/cmd move_eventstats.sh` as a one line. When automaticScripts option is activated in the server, this will run automatically when an event ends.
2. `move_eventstats.sh` file that moves files into `~/eventstats` folder and renames them. You need to make sure that the folder exists and that you have `jq` installed cause the script also extracts the track name from the file content, see [move_eventstats.sh](/src/tsu_analyzer/move_eventstats.sh).

## Data

If you want to know which data is saved, have a look at the [models.py](/src/tsu_analyzer/db/models.py) file. Every single checkpoint time can be saved.

Check [Saver.py](/src/tsu_analyzer/db/Saver.py) for the main logic of reading the file and saving them to the database.

## Config / Setup

Create a .env file and define this variable:
TSU_HOTLAPPING_POSTGRES_URL=postgresql://user:password@host/database

Obviously, you can change the variable name when you change it in the scripts as well. 

In order to run this, you need to have a database with a "tsu" schema, run alembic migrations and then run models.py. 

Some commands to get you up and running quickly (assuming you have pdm and python installed):
- `pdm run alembic upgrade head` to apply db migrations
- `pdm run alembic revision --autogenerate -m "description what changed int he models"` to generate a alembic migration after you made changes to a model
- `pdm run python src/tsu_analyzer/db/Saver.py` to run the script
