import base64
import io

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State

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
        dcc.Interval(
            id='interval-component',
            interval=1 * 1000,  # in milliseconds
            n_intervals=0
        )
    ])
]

''' 
Колбэк для обработки файла с турнирами и отображения лоадера во время этого
'''


def register_file_callbacks(dash_app):
    @dash_app.callback(
        Output('output-txt-content', 'children'),
        [Input('upload-txt-file', 'contents')],
        [State('upload-txt-file', 'filename')]
    )
    def update_file_content(contents, filename):
        reset_info_object()

        if contents is None:
            raise dash.exceptions.PreventUpdate

        # Декодирование и отображение содержимого файла
        content_string = contents.split(',')[1]
        decoded_string = base64.b64decode(content_string).decode('utf-8')
        file_like_object = io.StringIO(decoded_string)
        # file_content = html.Div([
        #     html.Hr(),
        #     f'File Name: {filename}',
        #     html.Br(),
        #     'Content:',
        #     html.Pre(decoded_string, style={'whiteSpace': 'pre-wrap', 'wordBreak': 'break-all'})
        # ])

        get_all_lattices_from_file(file_like_object)

        # Как только функция завершится, лоадер исчезнет, поскольку мы обновляем 'output-txt-content'
        return [html.Div(html.P(f'File Name: {filename}', className="h4"))]

    @dash_app.callback(
        Output('messages-div', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_progress(n):
        last_message = [html.Div(progress_info['messages'][-1], className="h3") if progress_info['messages'] else None]

        if progress_info['complete']:
            return [html.Div("Обработка завершена", className="display-6")]
        return last_message
