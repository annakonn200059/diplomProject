import os
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime
import re


class DrawGraphs:
    def __init__(self):
        self.app_root = os.path.dirname(os.path.abspath(__file__))
        self.dateCur = str(datetime.utcnow())
        self.reg = re.compile('[^a-zA-Z0-9 ]')
        self.target = os.path.join(self.app_root, 'tests', self.reg.sub('', self.dateCur))

    def saveCharachteristics(self, G, destination, graph_width, graph_height):
        elements_amount = G.order()

        with open(destination + '.txt', encoding='UTF-8', mode='a') as fileCharacteristics:
            print("Порядок решётки: " + str(elements_amount), "Ширина: " + str(graph_width),
                  "Высота: " + str(graph_height), file=fileCharacteristics, sep="\n")

    def drawLattice(self, lattice_edges, folder_name, level_arr):
        # Создаем граф из ребер
        G = nx.Graph(lattice_edges)
        # Вытаскиваем узлы из ребер
        nodes = list(sorted(G.nodes()))

        # Считаем количество элементов на каждом уровне
        level_counts = {}
        for level in level_arr:
            if level[0] in level_counts:
                level_counts[level[0]] += 1
            else:
                level_counts[level[0]] = 1

        # Вычисляем позиции узлов
        pos = {}
        x_spacing = 100  # Расстояние по горизонтали между вершинами
        y_spacing = 100  # Расстояние по вертикали между уровнями
        cur_level_idx = 0
        level_el_idx = -1
        level_idx = level_arr[0][0]

        for node_id, node in enumerate(nodes):
            if not level_idx == level_arr[node_id][0]:
                level_idx = level_arr[node_id][0]
                cur_level_idx += 1
                level_el_idx = 0
            else:
                level_el_idx += 1

            # Вычисляем начальное смещение x так, чтобы узлы были центрированы
            x_offset = -(level_counts[level_idx] - 1) * x_spacing / 2
            pos[node] = (x_offset + level_el_idx * x_spacing, -cur_level_idx * y_spacing)

        nx.draw_networkx_nodes(G, pos, node_size=500)
        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G, pos, nodelist=lattice_edges)
        file_name = folder_name
        if not os.path.isdir(self.target):
            os.makedirs(self.target)
        destination = os.path.join(self.target, folder_name)
        if not os.path.isdir(destination):
            os.makedirs(destination)
        destination = os.path.join(self.target, folder_name, file_name)
        plt.savefig(destination)
        plt.close()

    def saveCharachteristicsToOneFile(self, order_dict, height_dict, width_dict, n):
        order_dict = dict(sorted(order_dict.items()))
        height_dict = dict(sorted(height_dict.items()))
        width_dict = dict(sorted(width_dict.items()))

        target = os.path.join(self.target, 'characteristics.txt')
        with open(target, encoding='UTF-8', mode='a') as fileCharacteristics:
            fileCharacteristics.write('Порядок:\n')
            for i in order_dict:
                fileCharacteristics.write(str(i)+': '+str(len(order_dict[i])) + '\n')

            fileCharacteristics.write('Ширина:\n')
            for i in width_dict:
                fileCharacteristics.write(str(i)+': '+str(len(width_dict[i])) + '\n')

            fileCharacteristics.write('Высота:\n')
            for i in height_dict:
                fileCharacteristics.write(str(i)+': '+str(len(height_dict[i])) + '\n')



