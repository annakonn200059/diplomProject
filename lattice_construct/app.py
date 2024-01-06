import networkx as nx

from dash_graphs.utils import add_progress_message
from lattice_construct.lattices.lattice import Lattice
from lattice_construct.tournaments.congruences import find_all_congruences
from lattice_construct.tournaments.tournaments import Tournaments
from lattice_construct.tournaments.formatInput import FormatInput
from lattice_construct.utils import edges_to_cytoscape_format


def get_lattice_from_upper_matrix(graph_value, n, input_method):
    n = int(n)
    format_input = FormatInput(graph_value, n)
    vertexes = list(range(n))
    # opposite_form - другая форма графа. Для digraph6 это будет верхняя матричная форма и наоборот
    if input_method == 'matrix':
        tournament_edges_list, adjacency_list, opposite_form = format_input.upperTriangleToEdgeList()
    else:
        tournament_edges_list, adjacency_list, vertexes, opposite_form = format_input.digraph6_to_directed_edges()
    factor_arr = find_all_congruences(vertexes, n)
    factor_arr = Tournaments(tournament_edges_list, adjacency_list, vertexes, n, graph_value).main_fun(0, factor_arr)
    lattice = Lattice(factor_arr)
    lattice_edges, lattice_width, lattice_height = lattice.main_fun()
    G = nx.Graph(lattice_edges)
    elements_amount = G.order()

    return edges_to_cytoscape_format(tournament_edges_list), edges_to_cytoscape_format(lattice_edges, lattice.flatten_arr),\
           lattice_width, lattice_height, elements_amount, lattice.flatten_arr, opposite_form


def get_all_lattices_from_file(fileWithTournaments, n):
    add_progress_message("Прогресс: начало обработки")
    fileWithTournaments.readline()
    n = int(n)
    i = 0
    tournaments, lattices, upper_matrixes, lattice_order_list, lattice_width_list, lattice_height_list = [], [], [], [], [], []
    vertexes = list(range(n))
    #Все возможные потенциальные конгруэнции исходного турнира
    all_factor_arr = find_all_congruences(vertexes, n)
    # считываем турниры в формате верхней матричной формы и находим список дуг и список смежности
    while True:
        line = fileWithTournaments.readline()
        i += 1
        if not line.strip():
            break
        upper_matrix_form = line.strip()
        tournament_edges_list, adjacency_list, opposite_form = FormatInput(upper_matrix_form,
                                                                      n).upperTriangleToEdgeList()
        factor_arr = Tournaments(tournament_edges_list, adjacency_list, vertexes, n, upper_matrix_form).main_fun(i, all_factor_arr)
        lattice = Lattice(factor_arr)
        lattice_edges, lattice_width, lattice_height = lattice.main_fun()
        G = nx.Graph(lattice_edges)
        elements_amount = G.order()
        tournaments.append(edges_to_cytoscape_format(tournament_edges_list))
        lattices.append(edges_to_cytoscape_format(lattice_edges, lattice.flatten_arr))
        upper_matrixes.append(upper_matrix_form)
        lattice_order_list.append(elements_amount)
        lattice_width_list.append(lattice_width)
        lattice_height_list.append(lattice_height)

    add_progress_message("", True)
    return tournaments, lattices, upper_matrixes, lattice_order_list, lattice_width_list, lattice_height_list

