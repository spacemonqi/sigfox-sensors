#Imports=========================================================================================================================#
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_useful_components as duc
from dash.exceptions import PreventUpdate
import dash
import pandas as pd
import numpy as np
from app import app
import utils



#Global==========================================================================================================================#
colorlist = ['#FF4F00', '#FFF400', '#FF0056', '#5E0DAC', '#60AAED', '#1CA776']
disabled_dict = {'Enabled': False, 'Disabled': True}

data_locations = pd.read_csv("../data/data_locations.csv")
fig_map = px.scatter_mapbox(data_locations,
                            lat="lat",
                            lon="lon",
                            hover_name="deviceid",
                            hover_data=["state"],
                            color_discrete_sequence=["#FF4F00"],
                            zoom=14,
                            height=858)
fig_map.update_layout(mapbox_style="open-street-map")
fig_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
map = dbc.Card(dcc.Graph(id='graph_map', animate=True, figure=fig_map), color='primary', className='mb-1')



#Data============================================================================================================================#
df = utils.get_df('../data/sensor_data.csv')
data = utils.get_store_data()
tree_nodes = utils.update_tree_nodes(data)



#Layout Components===============================================================================================================#
COMP_nav_bar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src='/assets/divigraph.png', height='40px'), width=1, align='center'),
                        dbc.Col(dbc.NavbarBrand('Divigraph', className='ml-2'), width=1, align='center'),
                    ],
                    align='center',
                    no_gutters=True,
                ),
                href='/monitoring',
            ),
        ],
        fluid = True
    ),
    color='primary',
    dark=True,
    className='mb-4',
)

COMP_nav_tree = dbc.CardBody(
    [
        dbc.Row(html.Div(duc.CheckBoxTree(
                            id='nav_tree',
                            nodes=tree_nodes,
                            disabled = False,
                            expandDisabled = False,
                            expandOnClick = True,
                            noCascade = True,
                            onlyLeafCheckboxes = False,
                            optimisticToggle = True,
                            showNodeIcon = False,
                        )), className='mb-2'),
        dbc.Row(html.Div(id='checked-output'), className='mb-4'),
        dbc.Row(html.Div(id='expanded-output'), className='mb-4'),
    ],
    style = {'color': 'white'}
),

COMP_metrics = html.Div([
    dbc.Card(
        children = [
            dbc.CardBody(
                [
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon('Device ID', addon_type='prepend'),
                            dbc.Input(value='22229D7'),
                        ],
                        className='mb-2',
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon('Device Type', addon_type='prepend'),
                            dbc.Input(value='Dev Kit'),
                        ],
                        className='mb-2',
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon('Time', addon_type='prepend'),
                            dbc.Input(value=str(datetime.now().time())),
                        ],
                        className='mb-2',
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon('SeqNumber', addon_type='prepend'),
                            dbc.Input(value='Engaged'),
                        ],
                        className='mb-2',
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon('LQI', addon_type='prepend'),
                            dbc.Input(value='Good'),
                        ],
                        className='mb-2',
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon('Sampling Rate', addon_type='prepend'),
                            dbc.Input(value='1/day'),
                        ],
                        className='mb-2',
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon('Battery', addon_type='prepend'),
                            dbc.Input(value='100%'),
                        ],
                        className='mb-2',
                    ),
                ],
            )
        ],
        color='primary',
        style={'height': '452px'},
    )
])

COMP_graph_ch1 = dbc.Row([
    dbc.Col(dbc.Card(dcc.Graph(id='COMP_graph_ch1', animate=True), color='primary', className='mb-1'), width=8),
    dbc.Col(COMP_metrics, width=4)
], id='row_COMP_graph_ch1', style={'display': 'none'})
COMP_graph_ch2 = dbc.Row([
    dbc.Col(dbc.Card(dcc.Graph(id='COMP_graph_ch2', animate=True), color='primary', className='mb-1'), width=8),
    dbc.Col(COMP_metrics, width=4)
], id='row_COMP_graph_ch2', style={'display': 'none'})
COMP_graph_ch3 = dbc.Row([
    dbc.Col(dbc.Card(dcc.Graph(id='COMP_graph_ch3', animate=True), color='primary', className='mb-1'), width=8),
    dbc.Col(COMP_metrics, width=4)
], id='row_COMP_graph_ch3', style={'display': 'none'})
COMP_graph_ch4 = dbc.Row([
    dbc.Col(dbc.Card(dcc.Graph(id='COMP_graph_ch4', animate=True), color='primary', className='mb-1'), width=8),
    dbc.Col(COMP_metrics, width=4)
], id='row_COMP_graph_ch4', style={'display': 'none'})
COMP_graph_ch5 = dbc.Row([
    dbc.Col(dbc.Card(dcc.Graph(id='COMP_graph_ch5', animate=True), color='primary', className='mb-1'), width=8),
    dbc.Col(COMP_metrics, width=4)
], id='row_COMP_graph_ch5', style={'display': 'none'})



#Layout Divisions================================================================================================================#
DIV_channels = html.Div(
    id='DIV_channels',
    children = [
        dbc.Card(
                dbc.Row([
                    dbc.Col(html.H3(children='Sensor Monitoring', className='text-center bg-primary mb-4', style = {'margin-top': '21px', 'margin-left': '3px'}), width=8),
                    dbc.Col(width=2),
                    dbc.Col(dbc.Button(children='Run', id='btn_pause', size='lg', color='primary', style={'width': '100px', 'margin-top': '17px', 'margin-left': '80px'}), width=2)
                ]),
                color='primary',
                className='mb-1',
        ),
        html.Div(
            children = [
                dbc.Col([
                    COMP_graph_ch1,
                    COMP_graph_ch2,
                    COMP_graph_ch3,
                    COMP_graph_ch4,
                    COMP_graph_ch5,
                ]),
            ],
            style = {'maxHeight': '100vh', 'overflow': 'scroll'},
            className="no-scrollbars",
        )
    ]
)

DIV_devices = html.Div([
    dcc.Store(id='nav_tree_trigger', storage_type='local'),
    dbc.Container([
        dbc.Row([dbc.Col(dbc.Card(html.H3(id='devconfig', children='Device Configuration', className='text-center bg-primary'),
                                  body=True,
                                  color='primary'),
                 className='mb-4')]),
        dbc.Row([
                dbc.Col(width=2),
                dbc.Col(children=[html.P('''Device Alias:''')], width=3),
                dbc.Col(width=7),
        ]),
        dbc.Row([
            dbc.Col(html.H4(id='h4_device_id', children='DeviceID'), width=2),
            dbc.Col(
                dcc.Input(
                    id='in_a_dev',
                    type='text',
                    style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                ),
                width=3,
            ),
            dbc.Col(width=7),
        ], no_gutters=True),

        dbc.Row([dbc.Col(dbc.Card(html.H3(id='ch_config', children='Channel Configuration', className='text-center bg-primary'),
                                  body=True,
                                  color='primary'),
                 className='mb-4')]),
        dbc.Row([
            dbc.Col(width=2),
            dbc.Col(children=[html.P('''Channel Alias:''')], width=3),
            dbc.Col(children=[html.P('''Scaling Factor:''')], width=3),
            dbc.Col(children=[html.P('''Unit:''')], width=2),
            dbc.Col(children=[html.P('''Enable/Disable:''')], width=2),
        ], no_gutters=True),
        dbc.Row([
            dbc.Col(html.H4('''Channel 1:'''), width=2),
            dbc.Col(dcc.Input(id='in_a_ch1',
                              type='text',
                              style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                    ),
                    width=3,
            ),
            dbc.Col(dcc.Input(id='in_sf_ch1',
                              type='number',
                              style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                    ),
                    width=3,
            ),
            dbc.Col(dcc.Input(id='in_u_ch1',
                              type='text',
                              style = {'width': '120px', 'height': '35px', 'margin-bottom': '30px'}
                    ),
                    width=2,
            ),
            dbc.Col(dbc.Button(id='btn_disable1', children='Enabled', color='primary', style={'height': '35px', 'width': '120px'}), width=2),
        ], no_gutters=True),
        dbc.Row([
            dbc.Col(html.H4('''Channel 2:'''), width=2),
            dbc.Col(dcc.Input(id='in_a_ch2',
                              type='text',
                              style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                    ),
                    width=3,
            ),
            dbc.Col(dcc.Input(id='in_sf_ch2',
                              type='number',
                              style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                    ),
                    width=3,
            ),
            dbc.Col(dcc.Input(id='in_u_ch2',
                              type='text',
                              style = {'width': '120px', 'height': '35px', 'margin-bottom': '30px'}
                    ),
                    width=2,
            ),
            dbc.Col(dbc.Button(id='btn_disable2', children='Enabled', color='primary', style={'height': '35px', 'width': '120px'}), width=2),
        ], no_gutters=True),
        dbc.Row([
            dbc.Col(html.H4('''Channel 3:'''), width=2),
            dbc.Col(dcc.Input(id='in_a_ch3',
                              type='text',
                              style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                    ),
                    width=3,
            ),
            dbc.Col(dcc.Input(id='in_sf_ch3',
                              type='number',
                              style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                    ),
                    width=3,
            ),
            dbc.Col(dcc.Input(id='in_u_ch3',
                              type='text',
                              style = {'width': '120px', 'height': '35px', 'margin-bottom': '30px'}
                    ),
                    width=2,
            ),
            dbc.Col(dbc.Button(id='btn_disable3', children='Enabled', color='primary', style={'height': '35px', 'width': '120px'}), width=2),
        ], no_gutters=True),
        dbc.Row([
            dbc.Col(html.H4('''Channel 4:'''), width=2),
            dbc.Col(dcc.Input(id='in_a_ch4',
                              type='text',
                              style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                    ),
                    width=3,
            ),
            dbc.Col(dcc.Input(id='in_sf_ch4',
                              type='number',
                              style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                    ),
                    width=3,
            ),
            dbc.Col(dcc.Input(id='in_u_ch4',
                              type='text',
                              style = {'width': '120px', 'height': '35px', 'margin-bottom': '30px'}
                    ),
                    width=2,
            ),
            dbc.Col(dbc.Button(id='btn_disable4', children='Enabled', color='primary', style={'height': '35px', 'width': '120px'}), width=2),
        ], no_gutters=True),
        dbc.Row([
            dbc.Col(html.H4('''Channel 5:'''), width=2),
            dbc.Col(dcc.Input(id='in_a_ch5',
                              type='text',
                              style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                    ),
                    width=3,
            ),
            dbc.Col(dcc.Input(id='in_sf_ch5',
                              type='number',
                              style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                    ),
                    width=3,
            ),
            dbc.Col(dcc.Input(id='in_u_ch5',
                              type='text',
                              style = {'width': '120px', 'height': '35px', 'margin-bottom': '30px'}
                    ),
                    width=2,
            ),
            dbc.Col(dbc.Button(id='btn_disable5', children='Enabled', color='primary', style={'height': '35px', 'width': '120px'}), width=2),
        ], no_gutters=True),
        dbc.Row([
            dbc.Col(dbc.Button(id='btn_reset', children='Reset App', size='lg', color='primary', style={'width': '70%'}), width=2),
        ], no_gutters=True),
    ])
])

DIV_locations = html.Div(map)

DIV_home = html.Div()



#Layout==========================================================================================================================#
layout = html.Div([
    dbc.Container(
        [
            dbc.Row(
                [
                    dcc.Interval(id='graph_update', interval=1*1000, n_intervals=0),
                    dbc.Col(
                        [
                            dbc.Card(COMP_nav_tree, color='primary', style={'height': '100%'})
                        ],
                        style={'height': '90%'},
                        width=2
                    ),
                    dbc.Col(
                        id = 'col',
                        children = DIV_home,
                        width=10,
                    )
                ],
                className='h-100',
            )
        ],
        style={'height': '100vh'},
        fluid=True
    )
])

app.layout = html.Div(
    [
        dcc.Location(id='url', refresh=False),
        dcc.Location(id='reset', refresh=True),
        COMP_nav_bar,
        layout,
    ]
)



#Views===========================================================================================================================#
# Switch between views
@app.callback([Output('nav_tree', 'checked'),
               Output('col', 'children')],
              Input('nav_tree', 'checked'))
def switch_views(checked):

    if checked is None:
        checked = []

    with open('temp/tree.txt', 'r') as file:
        checked_global = [current_place.rstrip() for current_place in file.readlines()]

    checked_diff = list(set(checked).difference(checked_global))

    if not checked:
        checked_global = checked
    elif not checked_global:
        checked_global = checked
    elif not checked_diff:
        checked_global = checked
    elif (checked_global[0].find('ch') > -1) and (checked_diff[0].find('ch') > -1):
        checked_global = checked
    else:
        checked_global = checked_diff

    with open('temp/tree.txt', 'w') as file:
        file.writelines('%s\n' % item for item in checked_global)

    if checked_global:
        if checked_global[0].find('ch') > -1:
            return checked_global, DIV_channels

        if checked_global[0].find('dev') > -1:
            return checked_global, DIV_devices

        if checked_global[0].find('loc') > -1:
            return checked_global, DIV_locations

    return checked_global, DIV_home



#Home============================================================================================================================#



#Locations=======================================================================================================================#



#Devices=========================================================================================================================#
# Update h4_device_id children
@app.callback(Output('h4_device_id', 'children'),
              Input('nav_tree', 'checked'))
def update_h4_device_id_children(checked):

    page_dict = utils.get_current_page_dict()
    device = page_dict['dev']

    return device

# Update in_a_dev placeholders
@app.callback(Output('in_a_dev', 'placeholder'),
              Input('nav_tree', 'checked'))
def update_in_a_dev_placeholders(checked):

    page_dict = utils.get_current_page_dict()
    location = page_dict['loc']
    device = page_dict['dev']
    data = utils.get_store_data()
    placeholder = data[0][location]['children'][device]['alias']

    return placeholder

# Get in_a_ch and in_a_dev - THIS ONE SETS THE NAV_TREE
@app.callback(Output('nav_tree', 'nodes'),
              [Input('in_a_ch1', 'value'),
               Input('in_a_ch2', 'value'),
               Input('in_a_ch3', 'value'),
               Input('in_a_ch4', 'value'),
               Input('in_a_ch5', 'value'),
               Input('in_a_dev', 'value'),
               Input('nav_tree_trigger', 'data')],
              prevent_initial_call=True)
def get_in_a_ch_values(a1, a2, a3, a4, a5, a_dev, nav_tree_trigger_data):

    arguments = locals()
    page_dict = utils.get_current_page_dict()
    location = page_dict['loc']
    device = page_dict['dev']
    data = utils.get_store_data()
    for i in range(1, len(arguments)-1):
        if arguments['a'+str(i)]:
            channel = 'ch'+str(i)
            data[0][location]['children'][device]['children'][channel]['alias'] = arguments['a'+str(i)]
    if arguments['a_dev']: data[0][location]['children'][device]['alias'] = arguments['a_dev']
    utils.update_store_data(data)
    nodes = utils.update_tree_nodes(data)

    return nodes

# Update in_a_ch
for input_box in ('in_a_ch1', 'in_a_ch2', 'in_a_ch3', 'in_a_ch4', 'in_a_ch5'):
    @app.callback(Output(input_box, 'placeholder'),
                  Input('nav_tree', 'checked'),
                  State(input_box, 'id'))
    def update_in_a_ch_placeholders(checked, id):

        page_dict = utils.get_current_page_dict()
        location = page_dict['loc']
        device = page_dict['dev']
        channel = id.split('_')[-1]
        data = utils.get_store_data()
        placeholder = data[0][location]['children'][device]['children'][channel]['alias']

        return placeholder

# Get and Update in_sf_ch
for input_box in ('in_sf_ch1', 'in_sf_ch2', 'in_sf_ch3', 'in_sf_ch4', 'in_sf_ch5'):
    @app.callback(Output(input_box, 'type'),
                  Input(input_box, 'value'),
                  State(input_box, 'id'),
                  prevent_initial_call=True)
    def get_in_sf_ch_values(value, id):

        page_dict = utils.get_current_page_dict()
        location = page_dict['loc']
        device = page_dict['dev']
        channel = id.split('_')[-1]
        data = utils.get_store_data()
        data[0][location]['children'][device]['children'][channel]['scaling_fact'] = value
        utils.update_store_data(data)

        return 'number'

    @app.callback(Output(input_box, 'placeholder'),
                  Input('nav_tree', 'checked'),
                  State(input_box, 'id'))
    def update_in_sf_ch_placeholders(checked, id):

        page_dict = utils.get_current_page_dict()
        location = page_dict['loc']
        device = page_dict['dev']
        channel = id.split('_')[-1]
        data = utils.get_store_data()
        placeholder = data[0][location]['children'][device]['children'][channel]['scaling_fact']

        return placeholder

# Get and Update in_u_ch
for input_box in ('in_u_ch1', 'in_u_ch2', 'in_u_ch3', 'in_u_ch4', 'in_u_ch5'):
    @app.callback(Output(input_box, 'type'),
                  Input(input_box, 'value'),
                  State(input_box, 'id'),
                  prevent_initial_call=True)
    def get_in_u_ch_values(value, id):

        page_dict = utils.get_current_page_dict()
        location = page_dict['loc']
        device = page_dict['dev']
        channel = id.split('_')[-1]
        data = utils.get_store_data()
        data[0][location]['children'][device]['children'][channel]['unit'] = value
        utils.update_store_data(data)

        return 'text'

    @app.callback(Output(input_box, 'placeholder'),
                  Input('nav_tree', 'checked'),
                  State(input_box, 'id'))
    def update_in_u_ch_placeholders(checked, id):

        page_dict = utils.get_current_page_dict()
        location = page_dict['loc']
        device = page_dict['dev']
        channel = id.split('_')[-1]
        data = utils.get_store_data()
        placeholder = data[0][location]['children'][device]['children'][channel]['unit']

        return placeholder

# Get btn_disable
@app.callback([Output('in_a_ch1', 'disabled'),
               Output('in_sf_ch1', 'disabled'),
               Output('in_u_ch1', 'disabled'),
               Output('btn_disable1', 'children'),
               Output('in_a_ch2', 'disabled'),
               Output('in_sf_ch2', 'disabled'),
               Output('in_u_ch2', 'disabled'),
               Output('btn_disable2', 'children'),
               Output('in_a_ch3', 'disabled'),
               Output('in_sf_ch3', 'disabled'),
               Output('in_u_ch3', 'disabled'),
               Output('btn_disable3', 'children'),
               Output('in_a_ch4', 'disabled'),
               Output('in_sf_ch4', 'disabled'),
               Output('in_u_ch4', 'disabled'),
               Output('btn_disable4', 'children'),
               Output('in_a_ch5', 'disabled'),
               Output('in_sf_ch5', 'disabled'),
               Output('in_u_ch5', 'disabled'),
               Output('btn_disable5', 'children'),
               Output('nav_tree_trigger', 'data')],
              [Input('btn_disable1', 'n_clicks'),
               Input('btn_disable2', 'n_clicks'),
               Input('btn_disable3', 'n_clicks'),
               Input('btn_disable4', 'n_clicks'),
               Input('btn_disable5', 'n_clicks'),
               Input('nav_tree_trigger', 'data')])
def get_btn_disable(n1, n2, n3, n4, n5, nav_tree_trigger_data):

    out = []

    page_dict = utils.get_current_page_dict()
    location = page_dict['loc']
    device = page_dict['dev']

    data = utils.get_store_data()

    clicked_btns = [p['prop_id'] for p in dash.callback_context.triggered][0]
    for i in range(5):
        if 'btn_disable'+str(i+1) in clicked_btns:
            if data[0][location]['children'][device]['children']['ch'+str(i+1)]['disabled'] == 'Enabled':
                data[0][location]['children'][device]['children']['ch'+str(i+1)]['disabled'] = 'Disabled'
            else:
                data[0][location]['children'][device]['children']['ch'+str(i+1)]['disabled'] = 'Enabled'

    utils.update_store_data(data)

    for i in range(5):
        if data[0][location]['children'][device]['children']['ch'+str(i+1)]['disabled'] == 'Disabled':
            out.append(True)
            out.append(True)
            out.append(True)
            out.append('Disabled')
        else:
            out.append(False)
            out.append(False)
            out.append(False)
            out.append('Enabled')

    if nav_tree_trigger_data:
        out.append(False)
    else:
        out.append(True)

    return out

# Get btn_reset
@app.callback(Output('reset', 'href'),
              Input('btn_reset', 'n_clicks'),
              prevent_initial_call = True)
def get_btn_reset(n):

    clicked_btns = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_reset' not in clicked_btns:
        raise PreventUpdate
    if not n:
        raise PreventUpdate
    utils.write_store_data()

    return '/'



#Channels========================================================================================================================#
# Get btn_pause
@app.callback([Output('graph_update', 'interval'),
               Output('btn_pause', 'children')],
              [Input('btn_pause', 'n_clicks'),
               Input('btn_pause', 'children')])
def get_btn_pause(n, current):
    if current == 'Pause':
        return [1000*1000, 'Run']
    else:
        return [1*1000, 'Pause']

# Update COMP_graph_ch
@app.callback([Output('COMP_graph_ch1', 'figure'),
               Output('COMP_graph_ch2', 'figure'),
               Output('COMP_graph_ch3', 'figure'),
               Output('COMP_graph_ch4', 'figure'),
               Output('COMP_graph_ch5', 'figure')],
              [Input('graph_update', 'n_intervals'),
               Input('nav_tree', 'checked')])
def update_graphs(n, checked):

    page_dict = utils.get_current_page_dict()
    location = page_dict['loc']
    device = page_dict['dev']

    channels_ld = utils.get_channels(location, device)
    scaling_fact = 1.0
    df_scaled = pd.read_csv('../data/sensor_data.csv')
    df_scaled['value'] = df_scaled['value'].astype(float)
    for channel_dict in channels_ld:
        channel = channel_dict['name']
        scaling_fact = float(channel_dict['scaling_fact'])
        if not scaling_fact: scaling_fact = 1
        df_scaled.loc[df_scaled['data']==channel, 'value'] = df_scaled[df_scaled['data']==channel]['value'] * scaling_fact
    df_scaled.index = pd.to_datetime(df_scaled['timestamp'])

    figures = []
    i = 0
    for channel in channels_ld:

        trace = []

        if checked:
            df_data = df_scaled[df_scaled['data'] == channel['name']]
            df_data_id = df_data[df_data['deviceId'] == device]
            xmin = df_data_id.index.min()
            xmax = df_data_id.index.max()
            ymin = df_data_id['value'].min() - 0.05 * np.abs(df_data_id['value'].max())
            ymax = df_data_id['value'].max() + 0.05 * np.abs(df_data_id['value'].max())
            trace.append(go.Scatter(x=df_data_id.index,
                                    y=df_data_id['value'],
                                    mode='lines+markers',
                                    line={'width': 3},
                                    opacity=0.7,
                                    name=device,
                                    textposition='bottom center',
                                    # fill='tozeroy'
                        )
            )
        else:
            df_clear = df_scaled
            df_clear['value'].values[:] = 0
            xmin = df_scaled.index.min()
            xmax = df_scaled.index.max()
            ymin = -100
            ymax = 100
            trace.append(go.Scatter(x=df_clear.index,
                                    y=df_clear['value'],
                                    mode='lines',
                                    line={'width': 3},
                                    opacity=0.7,
                                    textposition='bottom center'
                        )
            )

        traces = [trace]
        data = [val for sublist in traces for val in sublist]

        figure = {'data': data,
                  'layout': go.Layout(
                      colorway=colorlist,
                      template='plotly_dark',
                      paper_bgcolor='rgba(0, 0, 0, 0)',
                      plot_bgcolor='rgba(0, 0, 0, 0)',
                      hovermode='x',
                      autosize=True,
                      margin={'t': 50, 'l': 50, 'b': 10, 'r': 20},
                      title={'text': channels_ld[i]['alias'], 'font': {'color': 'white'}, 'x': 0.5},
                      xaxis={'range': [xmin, xmax], 'gridcolor': 'white', 'gridwidth': 0.5},
                      yaxis={'range': [ymin, ymax], 'gridcolor': 'white'},
                  ),
                  }

        figures.append(figure)

        i += 1

    return figures

# Show/Hide Graphs
@app.callback([Output('row_COMP_graph_ch1', 'style'),
               Output('row_COMP_graph_ch2', 'style'),
               Output('row_COMP_graph_ch3', 'style'),
               Output('row_COMP_graph_ch4', 'style'),
               Output('row_COMP_graph_ch5', 'style')],
              Input('nav_tree', 'checked'))
def display_graphs(checked):

    channels = []

    page_dict = utils.get_current_page_dict()
    location = page_dict['loc']
    device = page_dict['dev']
    channels_ld = utils.get_channels(location, device)

    graphs_to_display = []

    if checked:
        for item in checked:
            substrings = item.split('_')
            channels.append(substrings[2])

    for channels_dict in channels_ld:
        if channels_dict['name'] in channels:
            graphs_to_display.append({})
        else:
            graphs_to_display.append({'display': 'none'})

    return graphs_to_display



#Main============================================================================================================================#
if __name__ == '__main__':
    # app.run_server(debug=False, dev_tools_ui=False, dev_tools_props_check=False, port=8050, threaded=True)
    app.run_server(debug=True, port=8050, threaded=True)
