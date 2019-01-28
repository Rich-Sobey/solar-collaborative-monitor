import numpy as np
import pandas as pd
import solaredge as se
from weather import *
from geocode import *
from maintenance import *


def get_site_details(key, site_id):
    details = key.get_details(site_id)
    inv = key.get_inventory(site_id)

    parameters = ['peak_power', 'install_date', 'country', 'city', 'address1', 'address2', 'zip_code', 'module_brand',
                  'module_model', 'module_power', 'module_temp_co', 'n_inverters']

    name = details['details']['name']

    info = []
    info.append(details['details']['peakPower'])
    info.append(details['details']['installationDate'])
    info.append(details['details']['location']['country'])
    info.append(details['details']['location']['city'])
    info.append(details['details']['location']['address'])
    info.append(details['details']['location']['address2'])
    info.append(details['details']['location']['zip'])
    info.append(details['details']['primaryModule']['manufacturerName'])
    info.append(details['details']['primaryModule']['modelName'])
    info.append(details['details']['primaryModule']['maximumPower'])

    try:
        info.append(details['details']['primaryModule']['temperatureCoef'])
    except KeyError:
        info.append(0)
    info.append(len(inv['Inventory']['inverters']))

    df_info = pd.DataFrame([])
    df_info['parameter'] = parameters
    df_info['value'] = info
    df_info.to_csv('SiteData/' + name + '_info.csv', index=False)


def get_dates(start_date, end_date):
    dates = []

    starts = pd.date_range(start_date, end_date, freq='MS').astype(str)
    ends = pd.date_range(start_date, end_date, freq='MS').astype(str)

    try:
        if starts[0] != start_date:
            starts = starts.insert(0, start_date)
        else:
            ends = ends[1:]
    except IndexError:
        starts = [start_date]

    try:
        if ends[-1] != end_date:
            ends = ends.insert(len(ends), end_date)
    except IndexError:
        ends = [end_date]

    for end, start in list(zip(ends, starts)):
        dates.append(start)
        dates.append(end)

    return dates


def get_site_power(key, site_id, meters, start_date, end_date):
    data_dates = get_dates(start_date, end_date)

    meters_input = [m.upper() for m in meters]
    meters_input = ','.join(meters_input)

    production = []
    consumption = []
    dates = []
    counter = 0

    for i in range(int(len(data_dates)/2)):

        i_start = data_dates[counter] + ' 00:00:00'
        i_end = data_dates[counter + 1] + ' 00:00:00'
        pwr = key.get_power_details(site_id, i_start, i_end, meters_input)['powerDetails']['meters']

        prod = False
        cons = False

        for j in pwr:
            if j['type'] == 'Production':
                prod = j['values']
            if j['type'] == 'Consumption':
                cons = j['values']

        for p in prod:
            try:
                production.append(p['value'])
            except KeyError:
                production.append(0)
            dates.append(p['date'])

        if cons:
            for c in cons:
                try:
                    consumption.append(c['value'])
                except KeyError:
                    consumption.append(0)

        counter += 2

    df = pd.DataFrame([])
    df['date'] = dates
    df['production'] = production

    if len(consumption) == len(production):
        df['consumption'] = consumption

    return df


def save_sites_power(key, site_ids):
    meters = ['Production', 'Consumption']
    for site in site_ids:
        details = key.get_details(site)
        name = details['details']['name']
        df = get_site_power(key, site, meters)
        df.to_csv('SiteData/' + name + '-power.csv', index=False)


def consolidate_data(key, site_ids, end_date):
    df = pd.DataFrame([])
    meters = ['Production', 'Consumption']

    for site in site_ids:
        details = key.get_details(site)
        data_period = key.get_data_period(site)
        start_date = data_period['dataPeriod']['startDate']
        df_site = get_site_power(key, site, meters, start_date, end_date)
        df_site['date'] = pd.to_datetime(df_site['date'])
        df_site = preprocess(df_site, site, method='mean', cons=False)
        df_site = export_lim(df_site, site, full_days=False)
        df_site = offline(df_site, site, remove=True, full_days=True)
        df_site = previous(df_site)
        try:
            coords = (details['details']['lat'], details['details']['long'])
        except KeyError:
            address = retrieve_address(details)
            coords = geocode(address)
        weather_df = request_weather_data(site, coords, start_date, end_date)
        df_site = df_site.merge(weather_df, how='left', left_on='date', right_on='datetime', copy=False)
        df_site.drop(columns=['datetime'], inplace=True)
        if len(df) == 0:
            df = df_site
            continue
        df = pd.concat([df, df_site], sort=False)
    return df


def preprocess(df, site, strip=True, method='single', cons=False):
    if not cons and 'consumption' in df.columns:
        df.drop(columns='consumption', inplace=True)
    if strip:
        if method == 'single':
            df = df[df.date.dt.minute == 0]
        elif method == 'mean':
            hm = [h + 1 if m != 0 else h for h, m in zip(df.date.dt.hour, df.date.dt.minute)]
            hm = [h if h < 24 else 0 for h in hm]
            dg = df.date.dt.date
            dates = [str(d) + ' ' + str(h) + ':00' for d, h in zip(dg, hm)]
            df['date'] = pd.to_datetime(dates)
            if not cons or 'consumption' not in df.columns:
                group = ['date', 'production']
            else:
                group = ['date', 'production', 'consumption']
            df = df.groupby(['date']).agg('mean')
        df.reset_index(inplace=True)
    df = installation_days(df)
    df['id'] = [site for s in range(len(df))]

    return df


def installation_days(df):
    df['install_date'] = (df['date'] - df['date'][0]).dt.days
    return df


def save_data(df):
    df.to_csv('MasterData/dataset.csv', index=False)
    return


def check_data(site_ids, end_date):
    rem_sites = []
    try:
        df = pd.DataFrame.from_csv('MasterData/dataset.csv', index_col=None)
        for site in site_ids:
            dates = df[df['id'] == site]['date']
            if len(dates) > 0:
                if max(dates) < end_date:
                    rem_sites.append(site)
            else:
                rem_sites.append(site)
    except FileNotFoundError:
        rem_sites = site_ids

    return rem_sites


def previous(df, look_back=1):
    for i in range(look_back):
        temp = list(df['production'])
        for j in range(i+1):
            temp.insert(0, temp[0])
        temp = temp[:-(i+1)]
        if len(temp) > 0:
            df['previous_' + str(i + 1)] = temp

    df = df.iloc[look_back:]

    return df

