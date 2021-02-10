import dash

# https://bootswatch.com/lux/
# external_stylesheets = [dbc.themes.SLATE]

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server
