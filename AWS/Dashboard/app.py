import pandas as pd

import dash
import dash_html_components as html
import dash_core_components as dcc

import plotly.express as px

def get_options(list_stocks):
    dict_list = []
    for i in list_stocks:
        dict_list.append({'label':i, 'value':i})

    return dict_list


# Load data
df = pd.read_csv('data/stockdata2.csv', index_col=0, parse_dates=True)
df.index = pd.to_datetime(df['Date'])

# Initialize the app
app = dash.Dash(__name__);

# Define the app
app.layout = html.Div(children=[
                          html.Div(className='row',                                               # Define the row element
                                   children=[
                                      html.Div(className='four columns div-user-controls',        # Define the left element
                                               children = [
                                                    html.H2('Dash - Sigfox Demo'),
                                                    html.P('''Visualising sensor data from the STM32WL55'''),
                                                    html.P('''Select one or more readings from the dropdown below.'''),
                                                    html.Div(className='div-for-dropdown',
                                                             children=[
                                                                dcc.Dropdown(id='stockselector',
                                                                options=get_options(df['stock'].unique()),
                                                                multi=True,
                                                                value=[df['stock'].sort_values()[0]],
                                                                style={'backgroundColor': '#1E1E1E'},
                                                                className='stockselector')
                                                             ],
                                                             style={'color': '#1E1E1E'}
                                                    )
                                               ]
                                      ),
                                      html.Div(className='eight columns div-for-charts bg-grey',  # Define the right element
                                               children = [
                                                    dcc.Graph(id='timeseries', config={'displayModeBar': False}, animate=True)
                                                    dcc.Graph(id='change', config={'displayModeBar': False}, animate=True)
                                               ]
                                      )
                                   ]
                          )
                      ]
             )

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
