import dash_useful_components as duc
import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
from dash.exceptions import PreventUpdate

app = dash.Dash(__name__)

# DEFINE THE CHECKBOX TREE
checkboxtree_nodes = [
    {
        "value": "P1",
        "label": "ParentOne",
        "children": [
            {
                "value": "N1.1",
                "label": "SectionOneChild",
                "children": [
                    {
                        "value": "N1.1.1",
                        "label": "SectionOneChil-of-Child-1",
                        "children": [
                            {
                                "value": "C1",
                                "label": "SectionOneChil-of-Child-1-of-Child"
                            }
                        ]
                    },
                    {
                        "value": "C2",
                        "label": "SectionOneChil-of-Child-2"
                    }
                ]
            },
            {
                "value": "N1.2",
                "label": "SectionTwo",
                "children": [
                    {
                        "value": "C3",
                        "label": "SectionTwo-Child"
                    }
                ]
            }
        ]
    },
    {
        "value": "P2",
        "label": "ParentTwo",
        "children": [
            {
                "value": "C5",
                "label": "ParentTwo-Child-1"
            },
            {
                "value": "C6",
                "label": "ParentTwo-Child-2"
            }
        ]
    }
]

# DEFINE THE LAYOUT
app.layout = html.Div([
    # CHECKBOX TREE
    html.Div(duc.CheckBoxTree(id="cb_input", nodes=checkboxtree_nodes, showNodeIcon=False)),
    html.Div([
        dcc.Checklist(
            id='options',
            options=[
                {'label': 'Disabled', 'value': 'disabled'},
                {'label': 'Expand Disabled', 'value': 'expandDisabled'},
                {'label': 'Expand on click', 'value': 'expandOnClick'},
                {'label': 'No cascade', 'value': 'noCascade'},
                {'label': 'Only Leaf Checkboxes', 'value': 'onlyLeafCheckboxes'},
                {'label': 'Optimistic Toggle', 'value': 'optimisticToggle'},
                {'label': 'Show Nodes Icons', 'value': 'showNodeIcon'},
            ],
            value=['optimisticToggle', 'showNodeIcon']
        )
    ]),
    html.Div(id='checked-output'),
    html.Div(id='expanded-output'),
])


@app.callback(
    [Output('checked-output', 'children'),
     Output('expanded-output', 'children')],
    [Input('cb_input', 'checked'),
     Input('cb_input', 'expanded')])
def display_output(checked, expanded):
    if checked and len(checked) > 0:
        res1 = 'You have checked {}'.format(' '.join(checked))
    else:
        res1 = 'No node is checked'

    if expanded and len(expanded) > 0:
        res2 = 'You have expanded {}'.format(' '.join(expanded))
    else:
        res2 = 'No node is expanded'

    return [res1, res2]


@app.callback(
    [Output('cb_input', 'disabled'),
     Output('cb_input', 'expandDisabled'),
     Output('cb_input', 'expandOnClick'),
     Output('cb_input', 'noCascade'),
     Output('cb_input', 'onlyLeafCheckboxes'),
     Output('cb_input', 'optimisticToggle'),
     Output('cb_input', 'showNodeIcon')],
    [Input('options', 'value')]
)
def configure_display(value):
    list_options = ['disabled',
                    'expandDisabled',
                    'expandOnClick',
                    'noCascade',
                    'onlyLeafCheckboxes',
                    'optimisticToggle',
                    'showNodeIcon']
    if value:
        return [list_option in value for list_option in list_options]
    else:
        raise PreventUpdate


if __name__ == '__main__':
    app.run_server(debug=True)
