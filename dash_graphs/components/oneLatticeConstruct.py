import re

from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_cytoscape as cyto
from dash.exceptions import PreventUpdate

from dash_graphs.components.utils import default_stylesheet
from dash_graphs.utils import get_image, progress_info, reset_info_object
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
                html.Button('import as jpg', id='import-tournament-button', disabled=True,
                            className="btn btn-outline-secondary"),
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
                html.Button('import as jpg', id='import-lattice-button', disabled=True,
                            className="btn btn-outline-secondary"),
            ], className='title_container'),
            cyto.Cytoscape(
                id='lattice',
                elements=[],
                layout={'name': 'preset'}
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

            if int(n_value) > 9:
                return {'display': 'block'}, [html.P('Количество вершин ограничено 8')]

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


