import re

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
                ]),
                html.Div([], id='n_input_error', className='error-text'),
            ], className='matrix_input_container'),
            html.Div([
                html.Label("Введите турнир в верхней матричной форме:"),
                html.Div([
                    dcc.Input(id='matrix-source', type='text', placeholder='Введите...', className='input')
                ]),
                html.Div([], id='matrix_input_error', className='error-text')
            ], className='matrix_input_container'),
            html.Div([
                html.Button('Построить', id='construct-button')
            ])
        ], className='control_container'),


        html.Div([], id="characteristics", className='characteristics_container')
    ], className='control_container', style={'justify-content': 'space-between'}),
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
    ], className='graph_container')
], className='container')


@dash_app.callback(
    [
        Output('n_input_error', 'style'),
        Output('n_input_error', 'children'),
    ],
    Input('construct-button', 'n_clicks'),
    State('n-source', 'value')
)
def update_n_errors(n_clicks, n_value):
    if n_clicks and n_clicks > 0:
        if not re.match(r'^\d+$', n_value):
            return {'display': 'block'}, [html.P('n должно быть числом')]

        if int(n_value) > 6:
            return {'display': 'block'}, [html.P('Количество вершин ограничено 6')]

    return {'display': 'none'}, None


@dash_app.callback(
    [
        Output('tournament', 'elements'),
        Output('lattice', 'elements'),
        Output('characteristics', 'style'),
        Output('characteristics', 'children'),
    ],
    Input('n_input_error', 'children'),
    State('construct-button', 'n_clicks'),
    State('matrix-source', 'value'),
    State('n-source', 'value'),
    State('tournament', 'elements'),
    State('lattice', 'elements'),
    State('characteristics', 'style'),
    State('characteristics', 'children'),
)
def update_graph(n_error, n_clicks, matrix_value, n_value, tournament_elements, lattice_elements, characteristics_style, characteristics_children):
    if n_error:
        return tournament_elements, lattice_elements, characteristics_style, characteristics_children

    if n_clicks and int(n_clicks) > 0:
        tournament_elements, lattice_elements, lattice_width, lattice_height, lattice_order = \
            get_lattice_from_upper_matrix(matrix_value, n_value)
        return tournament_elements, lattice_elements, {'display': 'block'}, \
        [
            html.Label("Характеристики решетки:", className="h5", style={"margin-bottom": "15px"}),
            html.P([f'Порядок: ', html.P(lattice_order, className="h6")], className="inline_p"),
            html.P([f'Ширина: ', html.P(lattice_width, className="h6")], className="inline_p"),
            html.P([f'Высота: ', html.P(lattice_height, className="h6")], className="inline_p")
        ]

    return tournament_elements, lattice_elements, {'display': 'none'}, None


def app():
    dash_app.run_server(debug=True)
