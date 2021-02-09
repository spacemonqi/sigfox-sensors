import dash_core_components as dcc
import dash_html_components as html

two = html.Div([
    dcc.Dropdown(id='app-2-dropdown', options=[{'label': 'App 2 - {}'.format(i), 'value': i} for i in ['NYC', 'MTL', 'LA']]),
    html.Div(id='app-2-display-value'),
])
