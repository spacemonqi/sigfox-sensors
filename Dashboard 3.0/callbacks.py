from dash.dependencies import Input, Output

from app import app
import channels

@app.callback(Output("h6_channel_string_configuration", "children"),
              [Input("in_alias_1", "value"),
              Input("in_scaling_factor_1", "value"),
              Input("in_alias_2", "value"),
              Input("in_scaling_factor_2", "value"),
              Input("in_alias_3", "value"),
              Input("in_scaling_factor_3", "value"),
              Input("in_alias_4", "value"),
              Input("in_scaling_factor_4", "value"),
              Input("in_alias_5", "value"),
              Input("in_scaling_factor_5", "value"),
              Input("in_alias_6", "value"),
              Input("in_scaling_factor_6", "value")])
def update_output(a1, s1, a2, s2, a3, s3, a4, s4, a5, s5, a6, s6):

    channels_ld = channels.get_channels()

    if a1: channels_ld[0]['alias'] = a1
    if a2: channels_ld[1]['alias'] = a2
    if a3: channels_ld[2]['alias'] = a3
    if a4: channels_ld[3]['alias'] = a4
    if a5: channels_ld[4]['alias'] = a5
    if a6: channels_ld[5]['alias'] = a6

    if s1: channels_ld[0]['scaling_fact'] = float(s1)
    if s2: channels_ld[1]['scaling_fact'] = float(s2)
    if s3: channels_ld[2]['scaling_fact'] = float(s3)
    if s4: channels_ld[3]['scaling_fact'] = float(s4)
    if s5: channels_ld[4]['scaling_fact'] = float(s5)
    if s6: channels_ld[5]['scaling_fact'] = float(s6)

    channels.update_channels(channels_ld)

    channel_name_string = channels.string_channels()

    return channel_name_string  # [channel_name_string, channel_name_string]
