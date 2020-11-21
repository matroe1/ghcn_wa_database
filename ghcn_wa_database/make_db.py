def make_db():
    import datetime

    start_time = datetime.datetime.now()
    import os
    import ulmo as u
    import pandas as pd
    import sqlite3
    from sqlalchemy.dialects.sqlite import TEXT, REAL

    # call ulmo to get all stations in WA State having different available data
    # u_stations_wa = u.ncdc.ghcn_daily.get_stations(country='US', state='WA',
    #                                                 as_dataframe=True)
    # wa_station_ids = u_stations_wa.index.to_series()
    # wa_station_ids = wa_station_ids.reset_index(drop=True)
    # u_stations_wa = u_stations_wa.drop('id', axis=1).reset_index()

    #stations for wind data (41 of them)
    #get stations for each element and combine so none missed
    wind_wsf2 = u.ncdc.ghcn_daily.get_stations(country='US',
                                                    state='WA',
                                                    elements=['WSF2'],
                                                    as_dataframe=True)
    wind_wsf2 = wind_wsf2.drop('id', axis=1).reset_index()

    wind_wsfg = u.ncdc.ghcn_daily.get_stations(country='US',
                                                    state='WA',
                                                    elements=['WSFG'],
                                                    as_dataframe=True)
    wind_wsfg = wind_wsfg.drop('id', axis=1).reset_index()

    wind_stations = (pd.concat([wind_wsf2, wind_wsfg],
                              ignore_index=True)
                              .drop_duplicates()
                              .reset_index(drop=True))
    wind_station_ids = wind_stations['id']

    #stations for temperature data (566 of them)
    temp_tmax = u.ncdc.ghcn_daily.get_stations(country='US',
                                                    state='WA',
                                                    elements=['TMAX'],
                                                    as_dataframe=True)
    temp_tmax = temp_tmax.drop('id', axis=1).reset_index()
    temp_tmin = u.ncdc.ghcn_daily.get_stations(country='US',
                                                    state='WA',
                                                    elements=['TMIN'],
                                                    as_dataframe=True)
    temp_tmin = temp_tmin.drop('id', axis=1).reset_index()
    temp_stations = (pd.concat([temp_tmax, temp_tmin],
                              ignore_index=True)
                              .drop_duplicates()
                              .reset_index(drop=True))
    temp_station_ids = temp_stations['id']

    #stations for precip data (1421 of them)
    #get stations with rain data
    rain_stations = u.ncdc.ghcn_daily.get_stations(country='US',
                                                    state='WA',
                                                    elements=['PRCP'],
                                                    as_dataframe=True)
    rain_stations = rain_stations.drop('id', axis=1).reset_index()

    #get stations with snow data
    snow_stations = u.ncdc.ghcn_daily.get_stations(country='US',
                                                    state='WA',
                                                    elements=['SNOW'],
                                                    as_dataframe=True)
    snow_stations = snow_stations.drop('id', axis=1).reset_index()

    #combine snow and rain stations and drop any overlap
    precip_stations = (pd.concat([rain_stations,snow_stations], ignore_index=True)
                        .drop_duplicates()
                        .reset_index(drop=True))
    precip_station_ids = precip_stations['id']

    stations = (pd.concat([wind_stations, temp_stations, precip_stations],
                        ignore_index=True)
                        .drop_duplicates()
                        .reset_index(drop=True))

    #check if database exists. if so delete so current can be rewritten
    database = 'WA_Hist.db'

    if os.path.exists(database):
        os.remove(database)
    else:
        pass

    #create sqlite db and open connection
    conn = sqlite3.connect(database)

    # loop through each site and build DB table
    # build out wind table
    for id in wind_station_ids:
        elements = ['WSF2',
                   'WDF2',
                   'WSFG',
                   'WDFG']
        site_id = id
        data = u.ncdc.ghcn_daily.get_data(site_id, as_dataframe=True,
                                            elements=elements)

        #first iteration through the list of data to setup the table

        try:
            meas = elements.pop(0)
            print(site_id)
            site = data[meas].copy().reset_index()

            site.columns = ['date', meas, meas + '_mflag', meas + '_qflag',
                            meas + '_sflag']
            site['date'] = site['date'].astype(str)
        except:
            meas = elements.pop(1)
            print(site_id)
            site = data[meas].copy().reset_index()

            site.columns = ['date', meas, meas + '_mflag', meas + '_qflag',
                            meas + '_sflag']
            site['date'] = site['date'].astype(str)

        #build out the rest of the table
        for elem in elements:
            if elem in data.keys():
                category = data[elem].copy().reset_index()
                category.columns = ['date', elem, elem + '_mflag',
                                    elem + '_qflag', elem + '_sflag']
                category['date'] = category['date'].astype(str)
                site = site.merge(category, how='outer', on='date')
            else:
                print(elem + ' not in data set')
                pass
        site.insert(0,'station_id', site_id)

        #convert wind speeds from tenths of a m/s to mph
        try:
            site['WSF2'] = (site['WSF2'] / 10)* 2.236936
            site['WSF2'] = site['WSF2'].astype(float).round(decimals=0)
        except:
            pass

        try:
            site['WSFG'] = (site['WSFG'] / 10)* 2.236936
            site['WSFG'] = site['WSFG'].astype(float).round(decimals=0)
        except:
            pass

        #writing table to SQLLITE DB
        site.to_sql('wind', conn, if_exists = 'append')

    # build out temperature table
    for id in temp_station_ids:
        elements = ['TMAX',
                   'TMIN']
        site_id = id
        data = u.ncdc.ghcn_daily.get_data(site_id, as_dataframe=True,
                                            elements=elements)

        #first iteration through the list of data to setup the table
        try:
            meas = elements.pop(0)
            print(site_id)
            site = data[meas].copy().reset_index()

            site.columns = ['date', meas, meas + '_mflag', meas + '_qflag',
                            meas + '_sflag']
            site['date'] = site['date'].astype(str)
        except:
            meas = elements.pop(0)
            print(site_id)
            site = data[meas].copy().reset_index()

            site.columns = ['date', meas, meas + '_mflag', meas + '_qflag',
                            meas + '_sflag']
            site['date'] = site['date'].astype(str)

        #build out the rest of the table
        for elem in elements:
            if elem in data.keys():
                category = data[elem].copy().reset_index()
                category.columns = ['date', elem, elem + '_mflag',
                                    elem + '_qflag', elem + '_sflag']
                category['date'] = category['date'].astype(str)
                site = site.merge(category, how='outer', on='date')
            else:
                print(elem + ' not in data set')
                pass
        site.insert(0,'station_id', site_id)

        #convert temp measurements from celsius to fahrenheit
        try:
            site['TMAX'] = (site['TMAX'] / 10)*1.8 + 32
            site['TMAX'] = site['TMAX'].astype(float).round(decimals=0)
        except:
            pass

        try:
            site['TMIN'] = (site['TMIN'] / 10)*1.8 + 32
            site['TMIN'] = site['TMIN'].astype(float).round(decimals=0)
        except:
            pass

        #writing table to SQLLITE DB
        site.to_sql('temp', conn, if_exists = 'append')

    # building out precip table
    for id in precip_station_ids:
        elements = ['PRCP',
                   'SNOW']
        site_id = id
        data = u.ncdc.ghcn_daily.get_data(site_id, as_dataframe=True,
                                            elements=elements)

        #first iteration through the list of data to setup the table
        try:
            meas = elements.pop(0)
            print(site_id)
            site = data[meas].copy().reset_index()

            site.columns = ['date', meas, meas + '_mflag', meas + '_qflag',
                            meas + '_sflag']
            site['date'] = site['date'].astype(str)
        except:
            meas = elements.pop(0)
            print(site_id)
            site = data[meas].copy().reset_index()

            site.columns = ['date', meas, meas + '_mflag', meas + '_qflag',
                            meas + '_sflag']
            site['date'] = site['date'].astype(str)

        #build out the rest of the table
        for elem in elements:
            if elem in data.keys():
                category = data[elem].copy().reset_index()
                category.columns = ['date', elem, elem + '_mflag',
                                    elem + '_qflag', elem + '_sflag']
                category['date'] = category['date'].astype(str)
                site = site.merge(category, how='outer', on='date')
            else:
                print(elem + ' not in data set')
                pass
        site.insert(0,'station_id', site_id)

        #convert prcp from tenths of a mm and snow in mm to inches
        try:
            site['PRCP'] = (site['PRCP'] / 10)* 0.039370
            site['PRCP'] = site['PRCP'].astype(float).round(decimals=2)
        except:
            pass

        try:
            site['SNOW'] = (site['SNOW'])* 0.039370
            site['SNOW'] = site['SNOW'].astype(float).round(decimals=1)
        except:
            pass

        #write table to SQLITE DB
        site.to_sql('precip', conn, if_exists = 'append')

    stations.to_sql('stations', conn, if_exists = 'replace')
    conn.close()

    end_time=datetime.datetime.now()
    run_time=end_time-start_time
    print("""
    Database build complete. \r
    Runtime: {} HR:MI:SS.ms""".format(run_time))
    return
