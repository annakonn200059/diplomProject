import re

from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_cytoscape as cyto

from dash_graphs.components.utils import default_stylesheet
from dash_graphs.utils import get_image
from lattice_construct.app import get_lattice_from_upper_matrix

one_lattice_selected_content = [
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Label("Введите количество вершин:", className="h6"),
                    html.Div([
                        dcc.Input(id='n-source', type='text', placeholder='n', className='input')
                    ]),
                    html.Div([], id='n_input_error', className='error-text'),
                ], className='matrix_input_container'),
                html.Div([
                    html.Label("Введите турнир в верхней матричной форме:", className="h6"),
                    html.Div([
                        dcc.Input(id='matrix-source', type='text', placeholder='Введите...', className='input')
                    ]),
                    html.Div([], id='matrix_input_error', className='error-text')
                ], className='matrix_input_container'),
                html.Div([
                    html.Button('Построить', id='construct-button', className="btn btn-primary")
                ])
            ], className='control_container'),

            html.Div([], id="characteristics", className='characteristics_container')
        ], className='control_container', style={'justify-content': 'space-between'}),
        html.Div([
            html.Div([
                html.Label("Турнир:"),
                html.Button('import as jpg', id='import-tournament-button', disabled=True,
                            className="btn btn-outline-secondary"),
            ], className='title_container'),
            cyto.Cytoscape(
                id='tournament',
                elements=[],
                layout={'name': 'circle'},
                stylesheet=default_stylesheet,
                # style={'width': '100%'}
            )
        ], className='graph_container'),
        html.Div([
            html.Div([
                html.Label("Решетка:"),
                html.Button('import as jpg', id='import-lattice-button', disabled=True,
                            className="btn btn-outline-secondary"),
            ], className='title_container'),
            cyto.Cytoscape(
                id='lattice',
                elements=[],
                layout={'name': 'circle'},
                # style={'width': '100%'}
            )
        ], className='graph_container')
    ], className='select_content')
]


def register_one_lattice_callbacks(dash_app):
    @dash_app.callback(
        [
            Output("tournament", "generateImage"),
            Output('import-tournament-button', 'disabled')
        ],
        [
            Input('import-tournament-button', 'n_clicks'),
            Input('tournament', 'elements')
        ]
    )
    def tournament_image(get_jpg_clicks, elements):
        return get_image(get_jpg_clicks, elements)

    @dash_app.callback(
        [
            Output("lattice", "generateImage"),
            Output('import-lattice-button', 'disabled')
        ],
        [
            Input('import-lattice-button', 'n_clicks'),
            Input('lattice', 'elements')
        ]
    )
    def lattice_image(get_jpg_clicks, elements):
        return get_image(get_jpg_clicks, elements)

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

    @dash_app.callback([
        Output('tournament', 'elements'),
        Output('lattice', 'elements'),
        Output('characteristics', 'style'),
        Output('characteristics', 'children'),
    ],
        [
            Input('n_input_error', 'children'),
            Input('construct-button', 'n_clicks'),
        ],
        [
            State('matrix-source', 'value'),
            State('n-source', 'value'),
            State('tournament', 'elements'),
            State('lattice', 'elements'),
            State('characteristics', 'style'),
            State('characteristics', 'children'),
        ]
    )
    def update_graph(n_error, n_clicks, matrix_value, n_value, tournament_elements,
                     lattice_elements, characteristics_style, characteristics_children):
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
