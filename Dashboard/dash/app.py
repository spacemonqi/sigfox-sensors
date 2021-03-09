import dash

# https://bootswatch.com/lux/
# external_stylesheets = [dbc.themes.SLATE]

app = dash.Dash(
    __name__,
    # meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=2"}],
    suppress_callback_exceptions=True,
)
server = app.server
