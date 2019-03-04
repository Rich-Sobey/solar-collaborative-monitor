import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# import datasets

xls = pd.ExcelFile('Product Database.xlsm')
usd_zar = pd.read_excel(xls, 'Exchange Rate')
database = pd.read_excel(xls, 'Dataset')
projects = pd.read_excel(xls, 'Project Details')

# Set project list with key
projects = projects.iloc[:, 0:2]
projects = pd.Series(list(projects['Size (kWp)']), index=list(projects['Code']))


# Set exchange rates (ensure exchange rate data is up to date)
forex = []

for i in database.index:
    for j in usd_zar.index:
        if database['Date'][i] == usd_zar['Date'][j]:
            forex.append(usd_zar['ZAR/USD'][j])

database['Exchange Rate'] = pd.DataFrame(forex)


# # PV modules

# Create module list
modules = database[database['Product Type'] == 'PV Module']

# Remove quotes
for i in modules.index:
    if str(modules['Project'][i])[0] == 'Q':
        modules = modules.drop(index=i, axis=0)

# distribution of suppliers by ZAR
g = sns.factorplot(x='Supplier', y='Cost (ZAR)', data=modules, kind='bar')

# distribution of suppliers by project numbers
g = sns.countplot(x='Supplier', data=modules)

# distribution of suppliers by kWp
modules['Size'] = [projects[i] for i in modules['Project']]
g = sns.factorplot(x='Supplier', y='Size', data=modules, kind='bar')

# average cost of panels per supplier
g = sns.factorplot(x='Supplier', y='Unit Cost (ZAR/unit)', data=modules, kind='bar')

# heatmap against exchange rate
modules = database[database['Product Type'] == 'PV Module']
c = modules[['Supplier', 'Unit Cost (ZAR/unit)', 'Exchange Rate']]
module_corr = pd.DataFrame()
module_corr['Supplier'] = c['Supplier'].drop_duplicates()
module_corr['Correlation'] = [c[c['Supplier'] == supplier].corr()['Exchange Rate'][0] for supplier in module_corr['Supplier']]
