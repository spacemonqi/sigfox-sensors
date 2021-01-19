import pandas as pd
import plotly.graph_objs as go

data = [['Ravi',21,67],['Kiran',24,61],['Anita',18,46],['Smita',20,78],['Sunil',17,90]]
df = pd.DataFrame(data,columns = ['name','age','marks'],dtype = float)
trace = go.Bar(x = df.name, y = df.marks)
fig = go.Figure(data = [trace])
iplot(fig)
