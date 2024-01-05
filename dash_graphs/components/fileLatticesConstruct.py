import base64
import io

import dash
import dash_cytoscape as cyto
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from dash_graphs.components.utils import default_stylesheet, lattice_stylesheet
from dash_graphs.utils import progress_info, reset_info_object
from lattice_construct.app import get_all_lattices_from_file

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
        html.Div([
            html.Div([
                html.Div(id='messages-div', className="messages-container"),
                dcc.Loading(
                    id="loading-1",
                    children=[
                        html.Div(id='output-txt-content')
                    ],
                    type="dot",  # Можете выбрать "circle", "dot", или другой
                    fullscreen=False,
                ),
            ], className="loading_status_container"),
            html.Div(
                [
                    html.Button('<', id='prev-button', className="btn btn-outline-secondary slider-button left"),
                    html.Button('>', id='next-button', className="btn btn-outline-secondary slider-button right"),
                    html.Div([
                        html.Div([
                            html.Label("Турнир:"),
                        ], className='title_container'),
                        cyto.Cytoscape(
                            id='slider_tournament',
                            elements=[],
                            layout={'name': 'circle'},
                            stylesheet=default_stylesheet,
                            # style={'width': '100%'}
                        ),
                        html.Div(className="graph_bottom_container"),
                    ]),
                    html.Div([
                        html.Div([
                            html.Label("Решетка:"),
                        ], className='title_container'),
                        cyto.Cytoscape(
                            id='slider_lattice',
                            elements=[],
                            layout={'name': 'preset'},
                            stylesheet=lattice_stylesheet,
                            # style={'width': '100%'}
                        )
                    ], className='graph_container'),
                    html.Div(id="upper-matrix", className="inline_p", style={'align-items': 'flex-start'}),
                    html.Div([], id="slider-characteristics", className='characteristics_container padding-container')
                ],
                style={'display': 'none'},
                id='graphs-content',
                className='slider_graphs_container'
            )
            ],
            className='content_container'
        ),
        dcc.Interval(
            id='interval-component',
            interval=1 * 1000,  # in milliseconds
            n_intervals=0
        ),
        dcc.Store(id='graphs_store', storage_type='memory'),
        dcc.Store(id='current-graph-index', storage_type='memory', data=0)
    ])
]

''' 
Колбэк для обработки файла с турнирами и отображения лоадера во время этого
'''


def register_file_callbacks(dash_app):
    @dash_app.callback(
        [
            Output('output-txt-content', 'children'),
            Output('graphs_store', 'data'),
            Output('graphs-content', 'style'),
        ],
        [Input('upload-txt-file', 'contents')]
    )
    def update_file_content(contents):
        reset_info_object()

        if contents is None:
            raise dash.exceptions.PreventUpdate

        # Декодирование и отображение содержимого файла
        content_string = contents.split(',')[1]
        decoded_string = base64.b64decode(content_string).decode('utf-8')
        file_like_object = io.StringIO(decoded_string)
        tournaments,\
        lattices,\
        upper_matrixes,\
        lattice_order_list,\
        lattice_width_list,\
        lattice_height_list = get_all_lattices_from_file(file_like_object)

        # Как только функция завершится, лоадер исчезнет, поскольку мы обновляем 'output-txt-content'
        return None, \
               [tournaments, lattices, upper_matrixes, lattice_order_list, lattice_width_list, lattice_height_list], \
               {'display': 'grid', 'width': '100%', 'height': '100%', 'grid-template-columns': '1fr 1fr'}

    # Колбэк для обновления графов при нажатии на кнопки
    @dash_app.callback(
        [
            Output('slider_tournament', 'elements'),
            Output('slider_lattice', 'elements'),
            Output('upper-matrix', 'children'),
            Output('current-graph-index', 'data'),  # Скрытый div для хранения текущего индекса
            Output('prev-button', 'disabled'),
            Output('next-button', 'disabled'),
            Output('slider-characteristics', 'children'),
        ],
        [
            Input('prev-button', 'n_clicks'),
            Input('next-button', 'n_clicks'),
        ],
        [
            State('graphs_store', 'data'),
            State('current-graph-index', 'data')
        ]
    )
    def update_graph(prev_clicks, next_clicks, store, current_index):
        if not store:
            raise PreventUpdate

        ctx = dash.callback_context
        if not ctx.triggered:
            button_id = 'No clicks yet'
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'prev-button' and current_index > 0:
            current_index -= 1
        elif button_id == 'next-button' and current_index < len(store[0]) - 1:
            current_index += 1

        disable_prev = current_index == 0
        disable_next = current_index >= len(store[0]) - 1

        tournaments, lattices, upper_matrix, lattice_order_list, lattice_width_list, lattice_height_list = store
        return tournaments[current_index],\
               lattices[current_index], \
               html.P([f'Верхняя матричная форма: ', html.P(upper_matrix[current_index], className="h6")], className="inline_p"),\
               current_index,\
               disable_prev,\
               disable_next,\
               [
                    html.Label("Характеристики решетки:", className="h5", style={"margin-bottom": "15px"}),
                    html.P([f'Порядок: ', html.P(lattice_order_list[current_index], className="h6")], className="inline_p"),
                    html.P([f'Ширина: ', html.P(lattice_width_list[current_index], className="h6")], className="inline_p"),
                    html.P([f'Высота: ', html.P(lattice_height_list[current_index], className="h6")], className="inline_p")
                ]

    @dash_app.callback(
        [
            Output('messages-div', 'children'),
            Output('messages-div', 'style'),
        ],
        Input('interval-component', 'n_intervals')
    )
    def update_progress(n):
        last_message = [html.Div(progress_info['messages'][-1], className="h3") if progress_info['messages'] else None]

        if progress_info['complete']:
            return None, {'display': 'none'}
        return last_message, {'display': 'block'}
