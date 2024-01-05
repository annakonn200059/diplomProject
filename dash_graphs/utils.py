import xml.etree.ElementTree as ET

import networkx as nx

progress_info = {
    'errors': [],
    'messages': [],
    'complete': False
}


def reset_info_object():
    progress_info['messages'] = []
    progress_info['errors'] = []
    progress_info['complete'] = False


def get_image(get_jpg_clicks, elements):
    if elements and len(elements):
        # File type to output of 'svg, 'png', 'jpg', or 'jpg'
        ftype = 'jpg'
        action = 'store'

        if get_jpg_clicks and int(get_jpg_clicks) > 0:
            action = "download"

        return {
                   'type': ftype,
                   'action': action,
               }, False, False

    return {}, True, True


def add_progress_message(message, is_last_message=False):
    global progress_info
    progress_info['messages'].append(message)

    if is_last_message:
        progress_info['complete'] = True  # если последнее сообщение


def add_error_message(message):
    global progress_info
    progress_info['errors'].append(message)


def create_graphml(G):
    graphml = ET.Element("graphml", xmlns="http://graphml.graphdrawing.org/xmlns")
    is_directed = nx.is_directed(G)
    graph = ET.SubElement(graphml, "graph", edgedefault="directed" if is_directed else "undirected")

    for node, data in G.nodes(data=True):
        node_element = ET.SubElement(graph, "node", id=str(node))
        for key, value in data.items():
            # Добавление координат узла непосредственно в тег <node>
            node_element.set(key, str(value))

    for source, target, data in G.edges(data=True):
        edge_element = ET.SubElement(graph, "edge", source=str(source), target=str(target), isDirect="true" if is_directed else "false")
        for key, value in data.items():
            # Если есть дополнительные данные для рёбер, добавляем их в <data>
            ET.SubElement(edge_element, "data", key=key).text = str(value)

    return ET.tostring(graphml, encoding='utf8', method='xml').decode()