import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
import chart_studio.plotly as plt
from dash.dependencies import Input, Output
import random

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    html.Div([
        html.H4('TERRA Satellite Bruh Feed'),
        html.Div(id='live-update-text'),
        dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        )
    ])
)

@app.callback(Output('live-update-text', 'children'), Input('interval-component', 'n_intervals'))
def update_metrics(n):
    lon  = random.random()
    return [
        html.Span(lon),
    ]

if __name__ == '__main__':
    app.run_server(debug=True)
