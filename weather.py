from darksky import forecast
from datetime import datetime as dt
import numpy as np
import pandas as pd


def get_weather_data(key, coords, start_date, end_date):
    parameters = ['datetime', 'temperature', 'uvIndex', 'windSpeed', 'summary',
                  'apparentTemperature', 'cloudCover', 'dewPoint', 'humidity', 'precipType',
                  'pressure', 'windBearing']
    df = pd.DataFrame([], columns=parameters)
    lat, long = coords
    date_range = pd.date_range(start_date, end_date, closed='left')

    for day in date_range:
        temp_df = pd.DataFrame([], columns=parameters)
        data_block = forecast(key, lat, long, time=day.isoformat(), units='si')
        for param in parameters:
            values = []
            for hour in range(0, 24):
                try:
                    if param != 'datetime':
                        value = data_block.hourly[hour][param]
                    else:
                        value = dt(day.year, day.month, day.day, hour)
                except (KeyError, IndexError):
                    if hour > 0:
                        value = values[-1]
                    else:
                        try:
                            value = df[df['datetime'] == day - pd.Timedelta(hours=1)][param].values[0]
                        except IndexError:
                            if param == 'precipType':
                                value = 'rain'
                            else:
                                value = 'NaN'
                values.append(value)

            temp_df[param] = values
        df = pd.concat([df, temp_df], sort=False)
        df['datetime'] = pd.to_datetime(df['datetime'])
    return df


def save_weather_data(site_id, df):
    df.to_csv('WeatherData/' + str(site_id) + '.csv', index=False)


def fetch_weather_data(site_id):
    df = pd.DataFrame.from_csv('WeatherData/' + str(site_id) + '.csv', index_col=None)
    df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S')
    return df


def request_weather_data(site_id, coords, start_date, end_date):
    flag = True
    try:
        df_ini = fetch_weather_data(site_id)
        recent_date = str(max(df_ini['datetime']) + pd.Timedelta(hours=1))
    except FileNotFoundError:
        recent_date = start_date
        flag = False
    weather_key = 'eb5e24e1f89af388443d2310b4114185'
    df = get_weather_data(weather_key, coords, recent_date, end_date)
    if flag:
        df = pd.concat([df_ini, df])
    save_weather_data(site_id, df)
    return df

