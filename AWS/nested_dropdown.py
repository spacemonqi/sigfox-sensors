import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from plotly import graph_objs as go
import dash_bootstrap_components as dbc
import plotly.express as px
from dash.dependencies import Input, Output, State

# this is the data of the city
data = [['a','b','d','h'],
       ['a','b','d','i'],
       ['a','b','e','j'],
       ['a','b','e','k'],
       ['a','c','f','l'],
       ['a','c','f','m'],
       ['a','c','g','n'],
       ['a','c','g','o'],
       ['z','x','p','a1'],
       ['z','x','p','a2'],
       ['z','x','q','a3'],
       ['z','x','q','a4'],
       ['z','y','r','a5'],
       ['z','y','r','a6'],
       ['z','y','s','a7'],
       ['z','y','s','a8']]

df = pd.DataFrame(data)
df.columns = ['city', 'district', 'area', 'subarea']


# now I want to create 4 dropdown menu that represented the area level.
# I want to make every time I change the higher level of area,
# the options in the lower dropdown menu that representative lower area change.

city_list = list(set(df['city'].to_list()))
city_list.insert(0,'all city')



# subarea
# ===============
def search_area_from_subarea(area_name):
    area_level = list(set(df[df.loc[:, 'subarea'] == area_name]['area'].to_list()))[0]
    return area_level

def search_district_from_subarea(area_name):
    area_level = list(set(df[df.loc[:, 'subarea'] == area_name]['district'].to_list()))[0]
    return area_level

def search_city_from_subarea(area_name):
    area_level = list(set(df[df.loc[:, 'subarea'] == area_name]['city'].to_list()))[0]
    return area_level

# area
# ===============
def search_district_from_area(area_name):
    area_level = list(set(df[df.loc[:, 'area'] == area_name]['district'].to_list()))[0]
    return area_level

def search_city_from_area(area_name):
    area_level = list(set(df[df.loc[:, 'area'] == area_name]['city'].to_list()))[0]
    return area_level

# district
# ============
def search_city_from_district(area_name):
    area_level = list(set(df[df.loc[:, 'district'] == area_name]['city'].to_list()))[0]
    return area_level

app = dash.Dash()
app.layout= html.Div([
   dbc.Nav(
       [
        dcc.Dropdown(
             id='menu_city', clearable=False,
             value='all city', options=[
             {'label': c1, 'value': c1}
             for c1 in city_list]),

          dcc.Dropdown(
             id='menu_district', clearable=False,
             value='all district'),
            dcc.Dropdown(
             id='menu_area', clearable=False,
             value='all area'),
                dcc.Dropdown(
             id='menu_subarea', clearable=False,
             value='all subarea'),
           html.Hr(),
           dbc.Button(id='button_show',children="SHOW DATA", color="info", className="mr-1")
         ]),
 html.Div([
    dbc.Row(
        dbc.Col([
            html.H2(id='title_for_test')],
            align='right', width={'size': '10', 'offset': '2'}
        )
          )
       ])
  ])

# CALLBACK SECTION

# ========================================
# CALLBACK CONFIGURATION FOR DROPDOWN LIST
# ========================================
# confifuration to set district dropdown menu change base selection on city dropdown menu

@app.callback(dash.dependencies.Output('menu_district','options'),
              [Input('menu_city', 'value')])

def set_list(selected_options):
    if selected_options == 'all city':
        temp_list = list(set(df['district'].to_list()))
        temp_list.insert(0, 'all district')
        return [{'label': i, 'value': i} for i in temp_list]
    else:
        temp_list = list(set(df[df.loc[:,'city'] == selected_options]['district'].to_list()))
        temp_list.insert(0, 'all district')
        return [{'label': i, 'value': i} for i in temp_list]
# -----------------------------
# configuration to prevent district dropdown menu error
@app.callback(dash.dependencies.Output('menu_district','value'),
              [Input('menu_district', 'options')])

def set_list(selected_options):
    return selected_options[0]['value']




# =======================================
# confifuration to set area dropdown menu change base selection on district dropdown menu

@app.callback(dash.dependencies.Output('menu_area','options'),
              [Input('menu_city', 'value')],
              [Input('menu_district', 'value')],
             multi = True)

def set_list(selected_options1, selected_options2):
    # 2 input, means: 2**2 possibility
    #print('1',selected_options1)
    #print('2', selected_options2)

    if selected_options1 == 'all city' and selected_options2 == 'all district':
        temp_list = list(set(df['area'].to_list()))
        temp_list.insert(0, 'all area')
        return [{'label': i, 'value': i} for i in temp_list]

    if selected_options1 != 'all city' and selected_options2 == 'all district':
        temp_list = list(set(df[(df.loc[:,'district'] == selected_options2)]['area'].to_list()))
        temp_list.insert(0, 'all area')
        return [{'label': i, 'value': i} for i in temp_list]

    if selected_options1 == 'all city' and selected_options2 != 'all district':
        temp_list = list(set(df[(df.loc[:,'district'] == selected_options2)]['area'].to_list()))
        temp_list.insert(0, 'all area')
        return [{'label': i, 'value': i} for i in temp_list]

    if selected_options1 != 'all city' and selected_options2 != 'all district':
        temp_list = list(set(df[(df.loc[:,'city'] == selected_options1) & (df.loc[:,'district'] == selected_options2)]['area'].to_list()))
        temp_list.insert(0, 'all area')
        return [{'label': i, 'value': i} for i in temp_list]

# -----------------------------
# configuration to prevent area dropdown menu error

@app.callback(dash.dependencies.Output('menu_area','value'),
              [Input('menu_area', 'options')])




# ========================================
# confifuration to set subarea dropdown menu change base selection on area dropdown menu

@app.callback(dash.dependencies.Output('menu_subarea','options'),
              [Input('menu_city', 'value')],
              [Input('menu_district', 'value')],
              [Input('menu_area', 'value')],
              multi=True
             )

def set_list(selected_options1,selected_options2, selected_options3):
    # 3 input = 2**3 possibility

    # possibility 1:
    if selected_options1 == 'all city' and selected_options2 == 'all district' and selected_options3 == 'all area':
        temp_list = list(set(df['subarea'].to_list()))
        temp_list.insert(0, 'all subarea')
        return [{'label': i, 'value': i} for i in temp_list]

    # possibility 2:
    if selected_options1 == 'all city' and selected_options2 == 'all district' and selected_options3 != 'all area':
        temp_list = list(set(df[(df.loc[:,'area'] == selected_options3)]['subarea'].to_list()))
        temp_list.insert(0, 'all subarea')
        return [{'label': i, 'value': i} for i in temp_list]
    # possibility 3:
    if selected_options1 == 'all city' and selected_options2 != 'all district' and selected_options3 == 'all area':
        temp_list = list(set(df[(df.loc[:,'district'] == selected_options2)]['subarea'].to_list()))
        temp_list.insert(0, 'all subarea')
        return [{'label': i, 'value': i} for i in temp_list]
    # possibility 4:
    if selected_options1 != 'all city' and selected_options2 == 'all district' and selected_options3 == 'all area':
        temp_list = list(set(df[(df.loc[:,'city'] == selected_options1)]['subarea'].to_list()))
        temp_list.insert(0, 'all subarea')
        return [{'label': i, 'value': i} for i in temp_list]


    # possibility 5:
    if selected_options1 != 'all city' and selected_options2 != 'all district' and selected_options3 == 'all area':
        temp_list = list(set(df[(df.loc[:,'city'] == selected_options1) & (df.loc[:,'district'] == selected_options2)]['subarea'].to_list()))
        temp_list.insert(0, 'all subarea')
        return [{'label': i, 'value': i} for i in temp_list]

    # possibility 6:
    if selected_options1 != 'all city' and selected_options2 == 'all district' and selected_options3 != 'all area':
        temp_list = list(set(df[(df.loc[:,'city'] == selected_options1) & (df.loc[:,'area'] == selected_options3)]['subarea'].to_list()))
        temp_list.insert(0, 'all subarea')
        return [{'label': i, 'value': i} for i in temp_list]

    # possibility 7:
    if selected_options1 == 'all city' and selected_options2 != 'all district' and selected_options3 != 'all area':
        temp_list = list(set(df[(df.loc[:,'district'] == selected_options2) & (df.loc[:,'area'] == selected_options3)]['subarea'].to_list()))
        temp_list.insert(0, 'all subarea')
        return [{'label': i, 'value': i} for i in temp_list]

    # possibility 8:
    if selected_options1 != 'all city' and selected_options2 != 'all district' and selected_options3 != 'all area':
        temp_list = list(set(df[(df.loc[:,'city'] == selected_options1) & (df.loc[:,'district'] == selected_options2) & (df.loc[:,'area'] == selected_options3)]['subarea'].to_list()))
        temp_list.insert(0, 'all subarea')
        return [{'label': i, 'value': i} for i in temp_list]


# -----------------------------
# configuration to prevent subarea dropdown menu error
@app.callback(dash.dependencies.Output('menu_subarea','value'),
              [Input('menu_subarea', 'options')])

def set_list(selected_options):
    return selected_options[0]['value']


# ================================
# CONFIGURATION SECTION FOR CALLBACK BUTTON
# ================================
#configuration callback button
@app.callback(dash.dependencies.Output('title_for_test','children'),
              [Input('button_show', 'n_clicks' )],
              [State('menu_city', 'value')],
              [State('menu_district', 'value')],
              [State('menu_area', 'value')],
              [State('menu_subarea', 'value')],
             multi=True)

def executor(n_clicks, number1, number2, number3, number4):


    # provinsi
    if number1 == 'all city' and number2 == 'all district' and number3 == 'all area' and number4 == 'all subarea':
        return 'demografic data of my state'


    # city / city
    if number1 != 'all city' and number2 == 'all district' and number3 == 'all area' and number4 == 'all subarea':
        return 'demografic data of ' + number1 + ' city'


    # district
    if (number1 == 'all city' or number1 != 'all city') and number2 != 'all district' and number3 == 'all area' and number4 == 'all subarea':
        return 'demografic data district ' + number2 + ', city ' + search_city_from_district(number2)


    # area
    if (number1 == 'all city' or number1 != 'all city') and (number2 == 'all district' or number2 != 'all district') and number3  != 'all area' and number4 == 'all subarea':
        return 'demografic data area ' + number3 ,html.Br(), 'district ' + search_district_from_area(number3) +  ', city ' + search_city_from_area(number3)

    # subarea
    if (number1 == 'all city' or number1 != 'all city') and (number2 != 'all district' or number2 == 'all district') and (number3  != 'all area' or number3  == 'all area') and number4 != 'all subarea':
        return 'demografic data subarea ' + number4 + ', area ' + search_area_from_subarea(number4),html.Br(),'district ' + search_district_from_subarea(number4) + ', city ' + search_city_from_subarea(number4)


if __name__ == "__main__":
    app.run_server()
