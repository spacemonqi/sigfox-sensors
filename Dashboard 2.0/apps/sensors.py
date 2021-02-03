import plotly.graph_objects as go
import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import dash_bootstrap_components as dbc

from app import app

layout = html.Div([
    dbc.Container([
        dbc.Row([dbc.Col(html.H1("Sigfox Sensor Network"), className="mb-2")]),
        dbc.Row([dbc.Col(html.H6(children='Visualising humidity, pressure and temperature trends'), className="mb-4")]),
        dbc.Row([dbc.Col(dbc.Card(html.H3(children='All Sensors',className="text-center text-light bg-dark"),
                                  body=True,
                                  color="dark"),
                 className="mb-4")])
    ])
])
