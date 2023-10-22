import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_cytoscape as cyto

from lattice_construct.app import get_lattice_from_upper_matrix

dash_app = dash.Dash(__name__)

default_stylesheet = [
    {
        "selector": "edge",
        "style": {
            "curve-style": "bezier",  # Добавьте это для кривых стрелок
            "target-arrow-shape": "triangle",  # Это делает рёбра ориентированными
        },
    },
    {
        "selector": "node",
        "style": {
            "label": "data(label)",
        },
    },
]

dash_app.layout = html.Div([
    html.Div([
        html.Div([
            html.Label("Вариант построения:"),
            dcc.Dropdown(
                id='dropdown-mode',
                value='одна решетка',
                clearable=False,
                options=[
                    {'label': name.capitalize(), 'value': name}
                    for name in ['одна решетка', 'несколько решеток']
                ]
            )
        ], className='dropdown'),
        html.Div([
            html.Label("Введите количество вершин:"),
            html.Div([
                dcc.Input(id='n-source', type='text', placeholder='n', className='input')
            ])
        ], className='matrix_input_container'),
        html.Div([
            html.Label("Введите турнир в верхней матричной форме:"),
            html.Div([
                dcc.Input(id='matrix-source', type='text', placeholder='Введите...', className='input')
            ])
        ], className='matrix_input_container'),
        html.Div([
            html.Button('Построить', id='construct-button')
        ])
    ], className='control_container'),
    html.Div([
        html.Label("Турнир:"),
        cyto.Cytoscape(
            id='tournament',
            elements=[],
            layout={'name': 'circle'},
            stylesheet=default_stylesheet,
        )
    ], className='graph_container'),
    html.Div([
        html.Label("Решетка:"),
        cyto.Cytoscape(
            id='lattice',
            elements=[],
            layout={'name': 'circle'},
        )
    ], className='graph_container'),
], className='container')


@dash_app.callback(
    [
        Output('tournament', 'elements'),
        Output('lattice', 'elements')
    ],
    Input('construct-button', 'n_clicks'),
    State('matrix-source', 'value'),
    State('n-source', 'value'),
    State('tournament', 'elements'),
    State('lattice', 'elements'),
)
def update_graph(n_clicks, matrix_value, n_value, tournament_elements, lattice_elements):
    if n_clicks and n_clicks > 0:
        tournament_elements, lattice_elements, lattice_width, lattice_height, lattice_order = \
            get_lattice_from_upper_matrix(matrix_value, n_value)

    return tournament_elements, lattice_elements


def app():
    dash_app.run_server(debug=True)
