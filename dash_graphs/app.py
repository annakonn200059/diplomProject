import dash
import matplotlib

from dash_graphs.components.fileLatticesConstruct import register_file_callbacks
from dash_graphs.components.oneLatticeConstruct import register_one_lattice_callbacks
from dash_graphs.components.main import create_main_layout, register_main_callbacks

matplotlib.use('Agg')

dash_app = dash.Dash(__name__, suppress_callback_exceptions=True)
dash_app.layout = create_main_layout()
register_main_callbacks(dash_app)
register_one_lattice_callbacks(dash_app)
register_file_callbacks(dash_app)


def app():
    dash_app.run_server(debug=True)
