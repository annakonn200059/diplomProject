import re

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_cytoscape as cyto
import base64
import io

from dash_graphs.utils import get_image
from lattice_construct.app import get_lattice_from_upper_matrix, get_all_lattices_from_file

dash_app = dash.Dash(__name__, suppress_callback_exceptions=True)

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

one_lattice_selected_content = [
    html.Div([
        html.Div([
            html.Div([
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
            html.Div([
                html.Label("Турнир:"),
                html.Button('import as jpg', id='import-tournament-button', disabled=True),
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
                html.Button('import as jpg', id='import-lattice-button', disabled=True),
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

several_lattices_selected_content = [
    html.Div([
        dcc.Upload(
            id='upload-txt-file',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select a .txt File with tournaments')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Only accept .txt files
            accept='.txt',
            # Not allow multiple files to be uploaded
            multiple=False
        ),
        html.Div(id='output-txt-content')
    ])
]

dash_app.layout = html.Div([
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
    html.Div(children=one_lattice_selected_content, id='main_content')
], className='container')


'''
отрисовываем контент в зависимости от выбранного режима:
для одного турнира либо список турниров из файла
'''
@dash_app.callback([
    Output('main_content', 'children'),
],
    [
        Input('dropdown-mode', 'value')
    ]
)
def update_graph(dropdown_value):
    if dropdown_value == 'несколько решеток':
        return [several_lattices_selected_content]

    else:
        return [one_lattice_selected_content]


@dash_app.callback(
    Output('output-txt-content', 'children'),
    [
        Input('upload-txt-file', 'contents')
    ],
    [
        State('upload-txt-file', 'filename')
    ]
)
def update_file_content(contents, filename):
    if contents is not None:
        # Decode the uploaded file content
        content_string = contents.split(',')[1]
        decoded_string = base64.b64decode(content_string).decode('utf-8')

        file_like_object = io.StringIO(decoded_string)

        get_all_lattices_from_file(file_like_object)

        children = [
            html.Div([
                html.Hr(),
                f'File Name: {filename}',
                html.Br(),
                'Content:',
                html.Pre(decoded_string, style={'whiteSpace': 'pre-wrap', 'wordBreak': 'break-all'})
            ])
        ]
        return children
    return None


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


def app():
    dash_app.run_server(debug=True)
