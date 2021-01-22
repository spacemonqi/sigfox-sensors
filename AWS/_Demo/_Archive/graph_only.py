from datetime import datetime
from datetime import timedelta
import dash
import dash_core_components as dcc
import dash_html_components as html
from plotly.subplots import make_subplots
import random
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    html.Div([
        html.H4('Sigfox Demo Data'),
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        )
    ])
)

@app.callback(Output('live-update-graph', 'figure'), Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    data = {
        'time': [],
        'Altitude': []
    }

    for i in range(180):
        time = datetime.now() - timedelta(seconds=i*20)
        alt = random.random()
        data['Altitude'].append(alt)
        data['time'].append(time)
    print(data['Altitude'])
    print(data['time'])

    fig = make_subplots(rows=1, cols=1, vertical_spacing=0.2)
    fig['layout']['margin'] = {'l': 30, 'r': 10, 'b': 30, 't': 10}
    fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}

    fig.append_trace({
        'x': data['time'],
        'y': data['Altitude'],
        'name': 'Altitude',
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 1, 1)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
