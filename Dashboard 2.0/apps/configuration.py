import dash_html_components as html
import dash_bootstrap_components as dbc

from apps import channels

##################################################
# try to change the direct downlink data in the sigfox backend from here! then a server wont be needed for downlinks
##################################################

channel_name_string = channels.read_channels_to_string()

layout = html.Div([
    dbc.Container([
        dbc.Row([dbc.Col(html.H1("Sigfox Sensor Network"), className="mb-2")]),
        dbc.Row([dbc.Col(html.H6(children="Selected Channels: "))]),
        dbc.Row([dbc.Col(html.H6(children=channel_name_string), className="mb-4")]),
        dbc.Row([dbc.Col(dbc.Card(html.H3(children='Channel Configuration', className="text-center bg-primary"),
                                  body=True,
                                  color="primary"),
                 className="mb-4")]),

    ])
])
