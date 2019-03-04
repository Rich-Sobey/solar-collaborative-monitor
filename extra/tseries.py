import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.arima_model import ARIMA

series = pd.read_csv('seriesexample.csv')

series.drop(index=series.index.values[-1], axis=0, inplace=True)

dates = []
for date in series['Month']:
    dates.append(pd.datetime.strptime('200' + date, '%Y-%m'))

series['Date'] = dates
series.drop(columns='Month', axis=0, inplace=True)
series.set_index('Date', inplace=True)

plt.plot(series)

pd.tools.plotting.autocorrelation_plot(series)

# looks like lag at 5 with order of 1

model = ARIMA(series, order=(5, 1, 0))
_fit = model.fit()

residuals = pd.DataFrame(_fit.resid)
residuals.plot()
residuals.plot(kind='kde')

residuals.describe()

print(_fit.summary())

split = 0.8
val_idx = int(len(series)*split)
train, test = series[:val_idx], series[val_idx:]

def plot_arima():
    p = int(input('Enter p:'))
    d = int(input('Enter d:'))
    q = int(input('Enter q:'))
    parameters = (p, d, q)
    model = ARIMA(train, order=parameters)
    _fit = model.fit()

    res = _fit.forecast(steps=len(test))[0]
    preds = pd.DataFrame(test.index.values, columns=['Date'])
    preds['forecasts'] = res
    preds.set_index('Date', inplace=True)

    plt.plot(series)
    plt.plot(preds, color='red')

