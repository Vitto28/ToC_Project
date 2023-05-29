import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import networkx as nx
import matplotlib
import threading
from tui import kClique

def main():
    sg.theme('TanBlue')
    sg.set_options(font=("Helvetica", 40))

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
        [sg.Text('Loading...', key='-LOADING-', visible=False)],
        [sg.Multiline(key='-OUTPUT-', visible=False)],
        [sg.Canvas(key='-CANVAS-', visible=False)]
    ]

    window = sg.Window('K-Clique', layout, grab_anywhere=False, size=(2000, 2000), finalize=True)

    matplotlib.use('TkAgg')
    fig = matplotlib.figure.Figure(figsize=(5, 5), dpi=300)
    tkcanvas = FigureCanvasTkAgg(fig, window['-CANVAS-'].TKCanvas)
    tkcanvas.get_tk_widget().pack(side='top', fill='both', expand=1)

    def calculate_output(filepath, k):
        nodes, edges, _, pos_vars, message = kClique(filepath, k)
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
            if len(pos_vars) == 0:
                window['-OUTPUT-'].update(message)
        else:
            window['-OUTPUT-'].update(message)
        window['-OUTPUT-'].update(visible=pos_vars is None or len(pos_vars) == 0)
        window['-CANVAS-'].update(visible=pos_vars is not None)
        window.write_event_value('JOB DONE', None)

    while True:
        event, values = window.read()

        if event == 'Submit':
            window['Submit'].update(disabled=True)
            window['-OUTPUT-'].update(visible=False)
            window['-CANVAS-'].update(visible=False)
            window['-LOADING-'].update(visible=True)
            filepath = values['-FILE_PATH-']
            k = values['-K-']
            threading.Thread(target=calculate_output, args=(filepath, k), daemon=True).start()
        elif event == 'JOB DONE':
            window['Submit'].update(disabled=False)
            window['-LOADING-'].update(visible=False)
        elif event in ('Exit', None):
            break

    window.close()


if __name__ == '__main__':
    main()
