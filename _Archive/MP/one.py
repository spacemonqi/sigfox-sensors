import dash_core_components as dcc
import dash_html_components as html

one = html.Div([
    dcc.Dropdown(id='app-1-dropdown', options=[{'label': 'App 1 - {}'.format(i), 'value': i} for i in ['NYC', 'MTL', 'LA']]),
    html.Div(id='app-1-display-value'),
])
