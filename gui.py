import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import networkx as nx
import matplotlib
from template import kClique

# Defining a Class
class GraphVisualization:
   
    def __init__(self):
          
        # visual is a list which stores all 
        # the set of edges that constitutes a
        # graph
        self.visual = []
          
    # addEdge function inputs the vertices of an
    # edge and appends it to the visual list
    def addEdge(self, a, b):
        temp = [a, b]
        self.visual.append(temp)
          
    # In visualize function G is an object of
    # class Graph given by networkx G.add_edges_from(visual)
    # creates a graph with a given list
    # nx.draw_networkx(G) - plots the graph
    # plt.show() - displays the graph
    def visualize(self, ax):
        G = nx.Graph()
        G.add_edges_from(self.visual)
        nx.draw_networkx(G, ax=ax)
        # plt.show()

def main():
    sg.theme('TanBlue')

    layout = [
        [sg.Text('Choose a text file for the graph:')],
        [
            sg.InputText('graph.txt', key='-FILE_PATH-'),
            sg.FileBrowse(file_types=(("Text Files", "*.txt"),)),
        ],
        [sg.Text('Choose an integer k:')],
        [sg.InputText('1', key='-K-')],
        [sg.Button('Submit')],
        [sg.Text('_' * 80)],
        [sg.Multiline(key='-OUTPUT-', visible=False)],
        [sg.Canvas(key='-CANVAS-', visible=False)],
        [sg.Button('Exit')]
    ]

    window = sg.Window('K-Clique', layout, default_element_size=(40, 1), grab_anywhere=False, size=(1000, 1000), finalize=True)

    matplotlib.use('TkAgg')
    fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
    tkcanvas = FigureCanvasTkAgg(fig, window['-CANVAS-'].TKCanvas)
    tkcanvas.get_tk_widget().pack(side='top', fill='both', expand=1)

    while True:
        event, values = window.read()

        if event == 'Submit':
            filepath = values['-FILE_PATH-']
            k = values['-K-']
            nodes, edges, _, pos_vars, error = kClique(filepath, k)
            if pos_vars is not None:
                G = nx.Graph()
                G.add_nodes_from(nodes)
                G.add_edges_from(edges)
                node_color = ['blue'] * len(nodes)
                nodes_in_clique = []
                for v in pos_vars:
                    v = v.split('_')
                    if v[0] == "n":
                        idx = int(v[1]) - 1
                        nodes_in_clique.append(nodes[idx])
                        node_color[idx] = 'red'
                edge_color = list(map(
                    lambda edge: 'red'
                        if edge[0] in nodes_in_clique and edge[1] in nodes_in_clique
                        else 'blue',
                    edges,
                ))
                fig.clear()
                nx.draw_networkx(G,
                    pos=nx.circular_layout(G),
                    ax=fig.gca(),
                    node_color=node_color,
                    edge_color=edge_color)
                fig.canvas.draw()
            else:
                window['-OUTPUT-'].update(error)
            window['-OUTPUT-'].update(visible=pos_vars is None)
            window['-CANVAS-'].update(visible=pos_vars is not None)
        elif event in ('Exit', None):
            break

    window.close()


if __name__ == '__main__':
    main()