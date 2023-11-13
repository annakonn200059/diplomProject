import networkx as nx

from dash_graphs.utils import add_progress_message
from lattice_construct.files.draw_module import DrawGraphs
from lattice_construct.lattices.lattice import Lattice
from lattice_construct.tournaments.tournaments import Tournaments
from lattice_construct.tournaments.formatInput import FormatInput
from lattice_construct.utils import fill_dict, edges_to_cytoscape_format


def get_lattice_from_upper_matrix(upper_matrix, n):
    n = int(n)
    tournament_edges_list, adjacency_list, vertexes = FormatInput(upper_matrix, n).upperTriangleToEdgeList()
    factor_arr = Tournaments(tournament_edges_list, adjacency_list, vertexes, n, upper_matrix).main_fun(0)
    lattice = Lattice(factor_arr)
    lattice_edges, lattice_width, lattice_height = lattice.main_fun()
    G = nx.Graph(lattice_edges)
    elements_amount = G.order()

    return edges_to_cytoscape_format(tournament_edges_list), edges_to_cytoscape_format(lattice_edges, lattice.flatten_arr), lattice_width, lattice_height, elements_amount, lattice.flatten_arr


def get_all_lattices_from_file(fileWithTournaments):
    add_progress_message("Прогресс: начало обработки")
    n = int("".join(fileWithTournaments.readline()))
    # app_root = os.path.dirname(os.path.abspath(__file__))
    # target = os.path.join(app_root, 'tests', 'charachteristics')
    draw = DrawGraphs()
    order_dict = {}
    height_dict = {}
    width_dict = {}
    i = 0
    # считываем турниры в формате верхней матричной формы и находим список дуг и список смежности
    # with open(target + '.txt', encoding='UTF-8', mode='a') as fileCharacteristics:
    while True:
        line = fileWithTournaments.readline()
        i += 1
        if not line.strip():
            break
        upper_matrix_form = line.strip()
        tournament_edges_list, adjacency_list, vertexes = FormatInput(upper_matrix_form,
                                                                      n).upperTriangleToEdgeList()
        factor_arr = Tournaments(tournament_edges_list, adjacency_list, vertexes, n, upper_matrix_form).main_fun(i)
        lattice_edges, lattice_width, lattice_height = Lattice(factor_arr).main_fun()
        # folder_name_for_lattice = upper_matrix_form
        # draw.drawTournaments(tournament_list, folder_name_for_lattice)
        # draw.saveCharachteristicsToOneFile(lattice_edges, folder_name_for_lattice, lattice_width, lattice_height)
        G = nx.Graph(lattice_edges)
        elements_amount = G.order()
        fill_dict(order_dict, elements_amount, upper_matrix_form)
        fill_dict(height_dict, lattice_height, upper_matrix_form)
        fill_dict(width_dict, lattice_width, upper_matrix_form)
        folder_name_for_lattice = upper_matrix_form
        #draw.drawTournaments(tournament_list, folder_name_for_lattice)
        draw.drawLattice(lattice_edges, folder_name_for_lattice)
    #print('order_dict', order_dict)
    #print('height_dict', height_dict)
    #print('width_dict', width_dict)
    draw.saveCharachteristicsToOneFile(order_dict, height_dict, width_dict, n)
    add_progress_message("", True)

