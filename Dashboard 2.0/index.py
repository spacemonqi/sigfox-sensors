# import all pages in the app
from apps import configuration, sensors, home, callbacks

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

# must add this line in order for the app to be deployed successfully on Heroku
# from app import server
from app import app

dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Home", href="/home", style={'color': 'white'}),
        dbc.DropdownMenuItem("Configuration", href="/configuration", style={'color': 'white'}),
        dbc.DropdownMenuItem("Sensors", href="/sensors", style={'color': 'white'}),
    ],
    nav = True,
    in_navbar = True,
    label = "Explore",
    toggle_style = {'color': 'white'}
)

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src="/assets/divigraph.png", height="40px")),
                        dbc.Col(dbc.NavbarBrand("Divigraph", className="ml-2")),
                    ],
                    align="center",
                    no_gutters=True,
                ),
                href="/home",
            ),
            dbc.NavbarToggler(id="navbar-toggler2"),
            dbc.Collapse(
                dbc.Nav(
                    # right align dropdown menu with ml-auto className
                    [dropdown], className="ml-auto", navbar=True
                ),
                id="navbar-collapse2",
                navbar=True,
            ),
        ]
    ),
    color="primary",
    dark=True,
    className="mb-4",
)

def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

for i in [2]:
    app.callback(
        Output(f"navbar-collapse{i}", "is_open"),
        [Input(f"navbar-toggler{i}", "n_clicks")],
        [State(f"navbar-collapse{i}", "is_open")],
    )(toggle_navbar_collapse)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/configuration':
        return configuration.layout
    elif pathname == '/sensors':
        return sensors.layout
    else:
        return home.layout

if __name__ == '__main__':
    app.run_server(debug=True)
