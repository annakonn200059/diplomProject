from dash_graphs.utils import add_error_message


class FormatInput:
    def __init__(self, upper_matrix_form, n):
        self.n = n
        self.edges_list = []
        self.upper_matrix_form = upper_matrix_form
        self.vertexes = []
        self.adjacency_list = {}

    def add_to_adj_list(self, node1, node2):
        temp = []
        if node1 not in self.adjacency_list:
            temp.append(node2)
            self.adjacency_list[node1] = temp

        elif node1 in self.adjacency_list:
            temp.extend(self.adjacency_list[node1])
            temp.append(node2)
            self.adjacency_list[node1] = temp

    def upperTriangleToEdgeList(self):
        # количество элементов над главной диагональю матрицы смежности
        upper_form_len = (self.n * (self.n - 1)) // 2
        if not upper_form_len == len(self.upper_matrix_form):
            add_error_message("Матричная форма не соответствует количеству вершин")
            return

        cur = 0
        stop = self.n - 1
        for i in range(0, self.n - 1):
            column = i + 1
            for j in range(cur, stop):
                if j >= len(self.upper_matrix_form):
                    add_error_message("Количество вершин не соответствует введенному турниру")
                if self.upper_matrix_form[j] == '1':
                    self.edges_list.append([i, column])
                    self.add_to_adj_list(i, column)
                    self.vertexes.extend([i, column])
                else:
                    self.edges_list.append([column, i])
                    self.add_to_adj_list(column, i)
                    self.vertexes.extend([column, i])
                column += 1
            copy_cur = cur
            cur = stop
            stop += stop - copy_cur - 1
        self.vertexes = list(set(self.vertexes))
        return self.edges_list, self.adjacency_list, self.vertexes
