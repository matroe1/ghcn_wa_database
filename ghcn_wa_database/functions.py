def display_table(database, table, rows):
    """

    database: name of SQLite database as str
    table: name of table, as str
    rows: how many rows to display as int, or 'all' as str.

    Returns a dataframe of the table of interest in a database with the first rows
    number of rows.
    If rows input as 'all', all rows of the table are returned.

    """
    import pandas as pd
    import sqlite3
    import sys

    #connect to database
    conn = sqlite3.connect(database)


    sql_placeholder = "SELECT * FROM "

    if isinstance(rows, str) == True:
        if rows.lower() == 'all':
            qry= sql_placeholder + table +';'
        else:
            raise ValueError('ERROR: Rows input incorrect. \'All\' or integer required.')


    else:
        qry= sql_placeholder + table + ' LIMIT ' + str(rows) + ';'

    df = pd.read_sql_query(qry, conn)

    conn.close()

    return df


def station_query(database, stations, date, variable):
    """

    database: name of SQLite database as str
    stations: station ids of desired stations as str in a list e.g. ['station_id1', 'station_id2']
                or input ['all'] if all stations meeting date & variable criteria are desired.
                Station Ids are per GHCN convention, the first two characters denote the FIPS country code,
                the third character is a network code that identifies the station numbering system
                used, and the remaining eight characters contain the actual station ID.
    date: desired date or date range, input as a 1 or 2 element list of strings.
                e.g. ['date'] or ['date_start','date_end']
    variable: variable(s) of interest input as a list of strings. e.g. ['TMAX', 'TMIN']

    Returns a dataframe from a query of SQLite database with desired stations, date(s) and variable data.

    """
    import pandas as pd
    import sqlite3

    df = pd.DataFrame()
    #connect to database
    conn = sqlite3.connect(database)

    water = ['PRCP','SNOW']
    temp = ['TMAX','TMIN']
    wind = ['WSF2', 'WDF2', 'WSFG', 'WDFG']

    columns = ', '.join(variable)

    select_stmt = """SELECT station_id, date, """ + columns

    if variable[0] in water:
        from_stmt = " FROM precip "
        notnull_stmt = " AND (PRCP NOT NULL OR SNOW NOT NULL) "

    elif variable[0] in temp:
        from_stmt = " FROM temp "
        notnull_stmt = " AND (TMAX NOT NULL OR TMIN NOT NULL) "

    elif variable[0] in wind:
        from_stmt = " FROM wind "
        notnull_stmt = " AND (WSF2 NOT NULL OR WSFG NOT NULL) "

    else:
        print('variable not in available data')


    if len(date) == 1:
        date_stmt = "WHERE date = '" + date[0] + "'"
    elif len(date) == 2:
        date_stmt = "WHERE date between '" + date[0] + "' AND '" + date[1] + "'"
    else:
        print('incorrect date format')

    if stations[0].lower() == 'all':
        stations_stmt =";"
    elif len(stations) == 1:
        stations_stmt ="AND station_id = '" + stations[0] +"';"
    elif len(stations) > 1:
        stations_stmt ="AND station_id IN ('" + "', '".join(stations) +"');"
    else:
        print('stations input error')

    qry = select_stmt + from_stmt + date_stmt + notnull_stmt + stations_stmt

    df = pd.read_sql_query(qry, conn)

    conn.close()

    return df

def gdd(daily_max, daily_min):
    """

    daily_max: Series of tmax values. Can be column in dataframe or NumPy array
    daily_min: Series of tmin values. Can be column in dataframe or NumPy array

    Corresponding daily_max and daily_min should align positionally in both series.

    Returns a NumPy array of same length as daily_max and daily_min.

    """
    import numpy as np
    import sys

    dmax = daily_max
    dmin = daily_min

    if(len(dmax) != len(dmin)):
        raise ValueError('Error: input series of two different lengths. daily_max and daily_min must be same length')

    base_temp = 50
    max_temp = 86

    dmax_mod = np.where(dmax < base_temp, base_temp, dmax)
    dmin_mod = np.where(dmin < base_temp, base_temp, dmin)
    dmax_mod = np.where(dmax_mod > max_temp, max_temp, dmax_mod)


    avg_temp = (dmax_mod + dmin_mod) / 2
    daily_gdd = avg_temp - base_temp

    return daily_gdd
    station_query('WA_Hist.db', ['USC00450008', 'USW00094298'], ['2010-03-10','2010-04-10'], ['SNOW'])
