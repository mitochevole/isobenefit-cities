import glob
import json
import tkinter as tk
import os
from PIL import Image, ImageTk

from isobenefit_cities.simulation import run_isobenefit_simulation


args_list = [{'arg': 'size_x', 'name': 'X size', 'type': int},
             {'arg': 'size_y', 'name': 'Y size', 'type': int},
             {'arg': 'n_steps', 'name': 'Iterartions', 'type': int},
             # {'arg': 'output_path', 'name': 'Output path', 'type': str},
             {'arg': 'boundary_conditions', 'name': 'Boundary Conditions', 'type': str},
             {'arg': 'build_probability',
              'name': 'Build Block Probability',
              'type': float},
             {'arg': 'neighboring_centrality_probability',
              'name': 'New Centrality P1',
              'type': float},
             {'arg': 'isolated_centrality_probability',
              'name': 'New Centrality P2',
              'type': float},
             {'arg': 'T_star', 'name': 'T*', 'type': int},
             {'arg': 'random_seed', 'name': 'random seed generator', 'type': int}]


def make_interface(root, arguments_list):
    entries = {}
    for field in arguments_list:
        print(field)
        row = tk.Frame(root)
        lab = tk.Label(row, width=22, text=field['name'] + ": ", anchor='w')
        ent = tk.Entry(row)
        ent.insert(0, "0")
        row.pack(side=tk.TOP,
                 fill=tk.X,
                 padx=5,
                 pady=5)
        lab.pack(side=tk.LEFT)
        ent.pack(side=tk.RIGHT,
                 expand=tk.YES,
                 fill=tk.X)
        entries[field['arg']] = ent
    return entries


def simluation_wrapper(entries, argument_list, ):
    input_args = {}
    for argument in argument_list:
        input_args[argument['arg']] = argument['type'](entries[argument['arg']].get())
    input_args.update({'minimum_area': 100, 'input_filepath': None, 'initialization_mode': 'list', 'output_path': None})
    run_isobenefit_simulation(**input_args)


def get_most_recent_snapshot_filepath(metadata):
    with open(metadata, 'r') as f:
        output_path =json.loads(f.read())['output_path']
    list_of_files = glob.glob(output_path+'/*.png')  # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


def update_gui_canvas(gui_canvas, final_path):
    print(final_path)
    pilImage = Image.open(final_path)
    image = ImageTk.PhotoImage(pilImage)
    gui_canvas.create_image(100, 100, image=image)

# TODO add inside simulation wrapper another window that opens the canvas and plots the images

if __name__ == '__main__':
    root = tk.Tk()
    ents = make_interface(root, args_list)
    b1 = tk.Button(root, text='Run simulation',
                   command=(lambda e=ents: simluation_wrapper(e, args_list)))
    b1.pack(side=tk.LEFT, padx=5, pady=5)
    b3 = tk.Button(root, text='Quit', command=root.quit)
    b3.pack(side=tk.LEFT, padx=5, pady=5)
    root.mainloop()
