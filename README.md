# ghcn_wa_database

ghcn_wa_database is a Python library for creating and accessing a local
SQLite database.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install ghcn_wa_database.

```bash
pip install ghcn_wa_database
```

## Usage

```python
import ghcn_wa_database

ghcn_wa_database.make_db() # creates database in current directory. overwrites if currently exists
ghcn_wa_database.functions.display_table(database, table, rows) # see method help. returns Pandas dataframe from desired db
ghcn_wa_database.functions.station_query(database, stations, date, variable) # see method help. returns Pandas dataframe from desired database with control of station id, date or date range, and variable of interest.
ghcn_wa_database.functions.gdd(daily_max, daily_min) # see method help. returns NumPy array of calculated growing degree days based on max and min temperatures.
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[GNU GPL v3.0](https://choosealicense.com/licenses/gpl-3.0/)
