# def get_item_AWS(deviceId, timestamp, dynamodb=None):
#     if not dynamodb:
#         if online:
#             dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
#         else:
#             dynamodb = boto3.resource('dynamodb',endpoint_url="http://localhost:8000")
#
#     table = dynamodb.Table(tableName)
#
#     try:
#         response = table.get_item(Key={'deviceId': deviceId, 'timestamp': timestamp})
#     except ClientError as e:
#         print(e.response['Error']['Message'])
#     else:
#         return response['Item']

# def plot_items(df):
#     fig = px.line(df, x=df.timestamp, y=df.data, title='Sigfox Data')
#     return fig

# @demo.callback(Output('sigfox-demo', 'figure'), Input('interval-component', 'n_intervals'))
# def update_graph_live(n):
#
#     print(n)
#     data = {
#         'time': [],
#         'Altitude': []
#     }
#
#     for i in range(180):
#         time = datetime.now() - timedelta(seconds=i*20)
#         alt = random.random()
#         data['Altitude'].append(alt)
#         data['time'].append(time)
#
#     fig = make_subplots(rows=1, cols=1, vertical_spacing=0.2)
#
#     fig.append_trace({
#         'x': data['time'],
#         'y': data['Altitude'],
#         'name': 'Altitude',
#         'mode': 'lines+markers',
#         'type': 'scatter'
#     }, 1, 1)
#
#     return fig

# demo.run_server(dev_tools_hot_reload=False)
