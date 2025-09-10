# Time Series Storage Tools

This software can be used to store time series from manufacturing test beds. 
The design was derived with data analysis in mind, enabling FAIR principles and reproducibility.

The conceptualization is published in [*link will follow shortly*].
If you use this software in any of your works please cite [*DOI will follow shortly*].


# Setup storagetools

To use `storagetools` in your projects, you need the following:

-   `storagetools` installed
-   a `config.ini` (works without but is not useful, see [Getting Started](#getting-started))

A minimal `config.ini` may look like:

```
[environment]
analysis_name = my_first_analysis 

[property_columns]
# additional case-specific properties (metadata information) as dict of lists.
# Use SQLite datatype as key for the dict (e.g., "TEXT", "FLOAT", etc.)
experiment = {"INT": ["run", "material"], "FLOAT": ["feedrate"]}
sensor = {"TEXT": ["manufacturer", "model", "identifier", "description"]}
channel = {"TEXT": ["measurand", "unit"]}
```


A more complete `config.ini` may look like:

```
[environment]
analysis_name = ucb_mill
available_cores = 12

# upper size limit for the key-value store, for most cases just leave as is
max_kvsize = 1099511627776

[storagetools.locations]
# name of the working directory
workdir_root = work

# name of the data directory within the work directory
storage_dir = data

# name of the plots directory within the work directory
plot_dir = plots

# name of the SQLite database file
database_filename = database.db

[property_columns]
# additional case-specific properties (metadata information) as dict of lists.
# Use SQLite datatype as key for the dict (e.g., "TEXT", "FLOAT", etc.)
experiment = {"INT": ["run", "material"], "FLOAT": ["feedrate"]}
sensor = {"TEXT": ["manufacturer", "model", "identifier", "description"]}
channel = {"TEXT": ["measurand", "unit"]}
```

If you want to modify logging, you can add:

```
[loggers]
keys=root

[handlers]
keys=screen, file

[formatters]
keys=default

[logger_root]
level=DEBUG
handlers=screen,file

[handler_screen]
class=StreamHandler
level=INFO
formatter=default
args=(sys.stdout,)

[handler_file]
class=FileHandler
level=DEBUG
formatter=default
args=('debug.log', 'a')

[formatter_default]
format=%(asctime)s %(levelname)s %(filename)s:%(lineno)d (%(funcName)s): %(message)s
```


# Getting Started

For a demonstration of how to use storagetools refer to the jupyter-notebooks in `doc/tutorials`.
