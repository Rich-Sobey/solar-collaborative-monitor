import pandas as pd
import numpy as np


def offline(df, site_id, remove=True, full_days=False):
    path = 'MaintenanceData/'
    f = pd.read_csv(path + 'offline.csv')
    f['start_time'] = pd.to_datetime(f['start_time'], format='%d-%m-%y %H:%M')
    f['end_time'] = pd.to_datetime(f['end_time'], format='%d-%m-%y %H:%M')
    f = f[f['site_id'] == site_id].reset_index(drop=True)

    maint_days = []
    maint_days.append([v for v in f.start_time.dt.date.dropna(0)])
    maint_days.append([v for v in f.end_time.dt.date.dropna(0)])

    if len(f) > 0:
        f.loc[f['start_time'].isna(), 'start_time'] = df.loc[0, 'date']

        offline_df = pd.DataFrame(columns=['date', 'status'])

        for i in range(len(f)):
            start_time = f.loc[i, 'start_time']
            end_time = f.loc[i, 'end_time']
            temp_range = pd.date_range(start_time, end_time, freq='H')
            temp_df = pd.DataFrame(columns=['date', 'status'])
            temp_df['date'] = temp_range
            temp_df['status'] = ['offline' for j in range(len(temp_range))]
            offline_df = pd.concat([offline_df, temp_df])

        df = df.merge(offline_df, how='left', left_on='date', right_on='date', copy=False)
        df['status'] = df['status'].fillna('online')

    else:
        df['status'] = ['online' for j in range(len(df))]

    if remove:
        if full_days:
            for t in maint_days:
                for d in t:
                    df = df[df.date.dt.date != d]
        else:
            df = df[df['status'] == 'online']
        df = df.drop(columns=['status'])

    return df


def export_lim(df, site_id, remove=False, full_days=False):
    path = 'MaintenanceData/'
    f = pd.read_csv(path + 'export_limitation.csv')
    f['start_time'] = pd.to_datetime(f['start_time'], format='%d-%m-%y %H:%M')
    f['end_time'] = pd.to_datetime(f['end_time'], format='%d-%m-%y %H:%M')
    f = f[f['site_id'] == site_id].reset_index(drop=True)

    if len(f) > 0:
        f.loc[f['start_time'].isna(), 'start_time'] = df.loc[0, 'date']
        f.loc[f['end_time'].isna(), 'end_time'] = df.iloc[-1]['date']

        export_df = pd.DataFrame(columns=['date', 'export_limitation'])

        for i in range(len(f)):
            start_time = f.loc[i, 'start_time']
            end_time = f.loc[i, 'end_time']
            temp_range = pd.date_range(start_time, end_time, freq='H')
            temp_df = pd.DataFrame(columns=['date', 'export_limitation'])
            temp_df['date'] = temp_range
            temp_df['export_limitation'] = ['on' for j in range(len(temp_range))]
            export_df = pd.concat([export_df, temp_df])

        df = df.merge(export_df, how='left', left_on='date', right_on='date', copy=False)
        df['export_limitation'] = df['export_limitation'].fillna('off')

    else:
        df['export_limitation'] = ['off' for j in range(len(df))]

    if remove:
        df = df[df['export_limitation'] == 'off']
        df.drop(columns=['export_limitation'], inplace=True)

    return df

