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

    def drawTournaments(self, tournament_list, folder_name):
        for i in range(len(tournament_list)):
            if len(tournament_list[i]) == 0:
                G = nx.Graph([[0, 0]])
                pos = nx.spring_layout(G)
                nx.draw_networkx_nodes(G, pos, node_size=500)
                nx.draw_networkx_labels(G, pos)
            else:
                G = nx.DiGraph(tournament_list[i])
                pos = nx.spring_layout(G)
                nx.draw_networkx_nodes(G, pos, node_size=500)
                nx.draw_networkx_labels(G, pos)
                nx.draw_networkx_edges(G, pos, nodelist=tournament_list[i])
            file_name = str(i + 1) + '.png'
            if not os.path.isdir(self.target):
                os.makedirs(self.target)
            destination = os.path.join(self.target, folder_name)
            if not os.path.isdir(destination):
                os.makedirs(destination)
            destination = os.path.join(self.target, folder_name, file_name)
            plt.savefig(destination)
            plt.close()

    def drawLattice(self, lattice_edges, folder_name):
        G = nx.Graph(lattice_edges)
        pos = nx.spring_layout(G)
        nx.draw_networkx_nodes(G, pos, node_size=500)
        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G, pos, nodelist=lattice_edges)
        file_name = folder_name
        if not os.path.isdir(self.target):
            os.makedirs(self.target)
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
                #for j in order_dict[i]:
                    #fileCharacteristics.write(j + '\n')
                #fileCharacteristics.write('\n')

            fileCharacteristics.write('Ширина:\n')
            for i in width_dict:
                fileCharacteristics.write(str(i)+': '+str(len(width_dict[i])) + '\n')
                #for j in width_dict[i]:
                    #fileCharacteristics.write(j + '\n')
                #fileCharacteristics.write('\n')

            fileCharacteristics.write('Высота:\n')
            for i in height_dict:
                fileCharacteristics.write(str(i)+': '+str(len(height_dict[i])) + '\n')
                #for j in height_dict[i]:
                    #fileCharacteristics.write(j + '\n')
                #fileCharacteristics.write('\n')



