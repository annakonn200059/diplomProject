def diff_arrays(arr1, arr2) -> list:
    list_difference = []
    for element in arr1:
        if len(element) == 1 and element[0] not in arr2:
            list_difference.append(element[0])
        else:
            flag = True
            for j in element:
                if j in arr2:
                    flag = False
                    break
            if flag:
                list_difference.append(element)

    return list_difference


def fill_dict(dict, el, upper_matrix_form):
    if not el in dict:
        dict[el] = [upper_matrix_form]
    else:
        dict[el].append(upper_matrix_form)


def edges_to_cytoscape_format(edges):
    # Создаем множество нод
    nodes = set()
    for edge in edges:
        nodes.add(edge[0])
        nodes.add(edge[1])

    # Преобразуем ноды в формат для Cytoscape
    node_elements = [{'data': {'id': str(node), 'label': str(node)}} for node in nodes]

    # Преобразуем дуги в формат для Cytoscape
    edge_elements = [{'data': {'source': str(edge[0]), 'target': str(edge[1])}} for edge in edges]

    # Объединяем узлы и дуги
    return node_elements + edge_elements