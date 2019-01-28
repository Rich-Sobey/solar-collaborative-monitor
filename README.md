# solar-collaborative-monitor
Machine learning application which is designed to predict the production of multiple commercial rooftop solar installations to aid in automated monitoring

#main notes
These scripts are purely data extraction scripts written in python which uses API calls to pull data from solar production API (SolarEdge), weather data and geocode data. Data exploration, modelling and evaluation are to be uploaded soon in a Jupyter Notebook.

#pull_data.py
This script are the high-level extraction steps. SolarEdge API key has been ommitted due to privacy policies however the raw data has been extracted already and uploaded in csv format to be used.

#utilities.py
Holds functions mainly dealing with data preprocessing, transformations, formatting and consolidating into single dataframe.

#geocode.py
Uses MapQuest API to find GPS coordinates given a string address. Functions involve the API calls

#weather.py
API calls to weather app to find hourly weather data for given GPS. Used to consolidate with PV production data

#maintenance.py
Functions which pull maintenance csv files and adds data points corresponding to any maintenance done on sites
