from dash import dcc, html
from dash.dependencies import Input, Output

from dash_graphs.components.fileLatticesConstruct import several_lattices_selected_content
from dash_graphs.components.oneLatticeConstruct import one_lattice_selected_content
from dash_graphs.utils import reset_info_object


def create_main_layout():
    return html.Div([
        html.Div([
            html.Label("Вариант построения:", className="h6"),
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


def register_main_callbacks(dash_app):
    @dash_app.callback([
        Output('main_content', 'children'),
    ],
        [
            Input('dropdown-mode', 'value')
        ]
    )
    def update_graph(dropdown_value):
        reset_info_object()
        if dropdown_value == 'несколько решеток':
            return [several_lattices_selected_content]

        else:
            return [one_lattice_selected_content]
