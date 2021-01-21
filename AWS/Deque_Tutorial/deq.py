import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque
import pandas as pd

# intialise data of lists.
data = {'Name':['Tom', 'nick', 'krish', 'jack'],
        'Age':[20, 21, 19, 18]}

# Create DataFrame
df = pd.DataFrame(data)

X = deque()#maxlen = 20)
X.append(1)

Y = deque()#maxlen = 20)
Y.append(1)

app = dash.Dash(__name__)

app.layout = html.Div(
	[
		dcc.Graph(id = 'live-graph', animate = True),
		dcc.Interval(
			id = 'graph-update',
			interval = 1000,
			n_intervals = 0
		),
	]
)

@app.callback(Output('live-graph', 'figure'), [ Input('graph-update', 'n_intervals') ])

def update_graph_scatter(n):
	print(df)
	X.append(X[-1]+1)
	# print(X[-1])
	# print(type(X))
	Y.append(df['Age'][random.randint(0,3)])
	# print(Y)
	# input()

	data = plotly.graph_objs.Scatter(
			x=list(X),
			y=list(Y),
			name='Scatter',
			mode= 'lines+markers'
	)

	return {'data': [data],
			'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),yaxis = dict(range = [min(Y),max(Y)]),)}

if __name__ == '__main__':
	app.run_server()
