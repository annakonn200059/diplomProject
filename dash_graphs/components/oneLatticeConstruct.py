import re
import networkx as nx
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_cytoscape as cyto
from dash.exceptions import PreventUpdate

from dash_graphs.components.utils import default_stylesheet, lattice_stylesheet
from dash_graphs.utils import get_image, progress_info, reset_info_object, create_graphml
from lattice_construct.app import get_lattice_from_upper_matrix

# Контейнер для ввода верхней матричной формы
input_container = html.Div([
    html.Div([
        dcc.Input(id='graph-source', type='text', placeholder='Введите...', className='input')
    ]),
    html.Div([], id='matrix_input_error', className='error-text')
], className='input_container', id='input_container')

input_selection = html.Div([
    html.Label("Выберите способ ввода турнира:", className="h6"),
    dcc.RadioItems(
        id='input-method',
        options=[
            {'label': ' Верхняя матричная форма', 'value': 'matrix'},
            {'label': ' Формат digraph6', 'value': 'digraph6'}
        ],
        value='matrix',  # Значение по умолчанию
        labelStyle={'display': 'block'}
    )
], className='input_method_container')

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
                ], className='input_container'),
                input_selection,
                input_container,
                html.Div([
                    html.Button('Построить', id='construct-button', className="btn btn-primary")
                ]),
                html.Div([], id="errors")
            ], className='control_container'),

            html.Div([], id="characteristics", className='characteristics_container')
        ], className='control_container', style={'justify-content': 'space-between'}),
        html.Div([
            html.Div([
                html.Label("Турнир:"),
                html.Div([
                    html.Button('import jpg', id='import-tournament-button', disabled=True,
                                className="btn btn-outline-secondary", style={'margin-right': '10px'}),
                    html.Button('import GraphML', id='import-graphml-tournament-button', disabled=True,
                                className="btn btn-outline-secondary"),
                    dcc.Download(id='download-tournament-graphml')
                ])
            ], className='title_container'),
            cyto.Cytoscape(
                id='tournament',
                elements=[],
                layout={'name': 'circle'},
                stylesheet=default_stylesheet,
                # style={'width': '100%'}
            ),
            html.Div(className="graph_bottom_container"),
        ], className='graph_container'),
        html.Div([
            html.Div([
                html.Label("Решетка:"),
                html.Div([
                    html.Button('import jpg', id='import-lattice-button', disabled=True,
                                className="btn btn-outline-secondary", style={'margin-right': '10px'}),
                    html.Button('import GraphML', id='import-graphml-lattice-button', disabled=True,
                                className="btn btn-outline-secondary"),
                    dcc.Download(id='download-lattice-graphml')
                ])
            ], className='title_container'),
            cyto.Cytoscape(
                id='lattice',
                elements=[],
                layout={'name': 'preset'},
                stylesheet=lattice_stylesheet,
                # style={'width': '100%'}
            ),
            html.Div(id='lattice-mouseoverNodeData', className="graph_bottom_container"),
        ], className='graph_container'),
        dcc.Store(id='store', storage_type='memory'),
        dcc.Interval(
            id='interval-component',
            interval=1 * 1000,  # in milliseconds
            n_intervals=0
        )
    ], className='select_content')
]


def register_one_lattice_callbacks(dash_app):
    @dash_app.callback(
        [
            Output("tournament", "generateImage"),
            Output('import-tournament-button', 'disabled'),
            Output('import-graphml-tournament-button', 'disabled')
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
            Output('import-lattice-button', 'disabled'),
            Output('import-graphml-lattice-button', 'disabled')
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

            if int(n_value) > 11:
                return {'display': 'block'}, [html.P('Количество вершин ограничено 11')]

        return {'display': 'none'}, None

    @dash_app.callback([
        Output('tournament', 'elements'),
        Output('lattice', 'elements'),
        Output('characteristics', 'style'),
        Output('characteristics', 'children'),
        Output('store', 'data'),
    ],
        [
            Input('n_input_error', 'children'),
            Input('construct-button', 'n_clicks'),
        ],
        [
            State('graph-source', 'value'),
            State('n-source', 'value'),
            State('input-method', 'value'),  # State для метода ввода
        ]
    )
    def update_graph(n_error, n_clicks, graph_value, n_value, input_method):
        reset_info_object()
        if n_error:
            raise PreventUpdate

        if n_clicks and int(n_clicks) > 0:
            new_tournament_elements, new_lattice_elements, lattice_width, lattice_height, lattice_order, congruences_list,\
            opposite_form = get_lattice_from_upper_matrix(graph_value, n_value, input_method)

            opposite_form_value = f'digraph6: ' if input_method == 'matrix' else f'Верхняя матричная форма: '

            return new_tournament_elements,\
                   new_lattice_elements,\
                   {'display': 'block'}, \
                   [
                       html.P([opposite_form_value, html.P(opposite_form, className="h6")], className="inline_p"),
                       html.Label("Характеристики решетки:", className="h5", style={"margin-bottom": "15px"}),
                       html.P([f'Порядок: ', html.P(lattice_order, className="h6")], className="inline_p"),
                       html.P([f'Ширина: ', html.P(lattice_width, className="h6")], className="inline_p"),
                       html.P([f'Высота: ', html.P(lattice_height, className="h6")], className="inline_p")
                   ], \
                   congruences_list

        raise PreventUpdate

    @dash_app.callback(
        [
            Output('errors', 'children'),  # для отображения ошибок
            Output('errors', 'style')
        ],
        Input('interval-component', 'n_intervals')
    )
    def update_progress(n):
        if len(progress_info['errors']):
            error_message = html.Div(
                [html.P(e) for e in progress_info['errors']],
                className='error-text'
            )
            return error_message, {'display': 'block'}

        return [], None

    @dash_app.callback(
        Output('lattice-mouseoverNodeData', 'children'),
        [
            Input('lattice', 'selectedNodeData'),
            Input('store', 'data')
        ]
    )
    def displayTapNodeData(data, congruences_list):
        if data:
            # data - список словарей для каждой выбранной вершины
            selected_data = data[0]  # реагировать только на первую выбранную вершину
            congruence = congruences_list[int(selected_data['id'])]
            return html.P(
                [html.P(f'Конгруэнция для вершины {selected_data["label"]}: ', className="h6"),
                 f'{list(congruence[1].values())}'],
                className="inline_p"
            )

        return ""

    @dash_app.callback(
        Output('download-tournament-graphml', 'data'),
        [Input('import-graphml-tournament-button', 'n_clicks')],
        [State('tournament', 'elements')],
        prevent_initial_call=True
    )
    def download_tournament_graphml(n_clicks, elements):
        if n_clicks is None:
            raise PreventUpdate

        G = nx.DiGraph()
        for element in elements:
            if 'source' in element['data']:
                G.add_edge(element['data']['source'], element['data']['target'])
            else:
                node_id = element['data']['id']
                G.add_node(node_id)

        # Генерация содержимого GraphML
        graphml_content = create_graphml(G)

        # Возвращаем объект для скачивания
        return dict(content=graphml_content, filename="tournament.graphml")

    @dash_app.callback(
        Output('download-lattice-graphml', 'data'),
        [Input('import-graphml-lattice-button', 'n_clicks')],
        [State('lattice', 'elements')],
        prevent_initial_call=True
    )
    def download_lattice_graphml(n_clicks, elements):
        if n_clicks is None:
            raise PreventUpdate

        G = nx.Graph()
        for element in elements:
            if 'source' in element['data']:
                G.add_edge(element['data']['source'], element['data']['target'])
            else:
                # Добавление узла с координатами
                node_id = element['data']['id']
                pos_x = element.get('position', {}).get('x', 0)
                pos_y = element.get('position', {}).get('y', 0)
                G.add_node(node_id, x=pos_x, y=pos_y)

        # Генерация содержимого GraphML
        graphml_content = create_graphml(G)

        # Возвращаем объект для скачивания
        return dict(content=graphml_content, filename="lattice.graphml")

