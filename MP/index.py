import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from one import one
from two import two
import callbacks

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/one':
        return one
    if pathname == '/two':
        return two

if __name__ == '__main__':
    app.run_server(debug=True)
