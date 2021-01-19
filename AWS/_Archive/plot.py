import pandas as pd
import numpy as np
import chart_studio.plotly as py
import cufflinks as cf
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objs import *

from matplotlib import pyplot as plt

# Create a DataFrame
columns = ['deviceId', 'timestamp', 'data', 'deviceTypeId', 'seqNumber', 'time']
index = range(0, 100)
df_sigfox = pd.DataFrame(index=index, columns=columns)
df_sigfox.head()

# Plot the data
input("Press Enter")
fig = go.FigureWidget()
fig.update_layout(title='Sigfox Demo Data', xaxis_title='Timestamp', yaxis_title='Data')
fig.show()

input("Press Enter")
for i in range(20):
    item_dict = {'deviceId': '12CAC94', 'timestamp': 161044204530+i, 'data': i**2, 'deviceTypeId': '5ff717c325643206e8d57c11', 'seqNumber' : 25, 'time' : 161044204530+i}
    df_sigfox.loc[i] = item_dict
fig.add_trace(go.Scatter(x=df_sigfox.timestamp, y=df_sigfox.data, mode='lines+markers', name='Sigfox Data'))
fig.show()

input("Press Enter")
for i in range(20):
    item_dict = {'deviceId': '12CAC94', 'timestamp': 161044204530+i, 'data': i**3, 'deviceTypeId': '5ff717c325643206e8d57c11', 'seqNumber' : 25, 'time' : 161044204530+i}
    df_sigfox.loc[i] = item_dict
fig.add_trace(go.Scatter(x=df_sigfox.timestamp, y=df_sigfox.data, mode='lines+markers', name='Sigfox Data'))
fig.show()
