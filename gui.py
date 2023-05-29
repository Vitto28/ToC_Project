import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import networkx as nx
import matplotlib
from subprocess import Popen
from subprocess import PIPE
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
            sg.InputText(key='-FILE_PATH-'),
            sg.FileBrowse(file_types=(("Text Files", "*.txt"),)),
        ],
        [sg.Text('Choose an integer k:')],
        [sg.InputText(key='-K-')],
        [sg.Button('Submit')],
        [sg.Text('_' * 80)],
        [sg.Multiline(key='-OUTPUT-', visible=False)],
        [sg.Canvas(key='-CANVAS-')],
        [sg.Button('Exit')]
    ]

    window = sg.Window('K-Clique', layout, default_element_size=(40, 1), grab_anywhere=False, size=(1000, 1000), finalize=True)

    matplotlib.use('TkAgg')
    fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
    # add the plot to the window
    def draw_figure(canvas, figure):
      tkcanvas = FigureCanvasTkAgg(figure, canvas)
      tkcanvas.get_tk_widget().pack(side='top', fill='both', expand=1)
      return tkcanvas
    draw_figure(window['-CANVAS-'].TKCanvas, fig)
    # Driver code
    G = GraphVisualization()
    G.addEdge(0, 2)
    G.addEdge(1, 2)
    G.addEdge(1, 3)
    G.addEdge(5, 3)
    G.addEdge(3, 4)
    G.addEdge(1, 0)
    G.visualize(fig.gca())

    while True:
        event, values = window.read()

        if event == 'Submit':
            filepath = values['-FILE_PATH-']
            k = values['-K-']
            graph, error = kClique(filepath, k)
            if graph is not None:
                graph.visualize(fig.gca())
            else:
                window['-OUTPUT-'].update(error)
            window['-OUTPUT-'].update(visible=graph is None)
            window['-CANVAS-'].update(visible=graph is not None)
        elif event in ('Exit', None):
            break

    window.close()


if __name__ == '__main__':
    main()
