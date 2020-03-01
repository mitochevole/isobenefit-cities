import tkinter as tk

from isobenefit_cities.simulation import run_isobenefit_simulation

args_list = [{'arg': 'urbanism_model', 'name': 'City development model', 'type': str, 'default': 'isobenefit'},
             {'arg': 'size_x', 'name': 'X size', 'type': int, 'default': 60},
             {'arg': 'size_y', 'name': 'Y size', 'type': int, 'default': 60},
             {'arg': 'n_steps', 'name': 'Iterartions', 'type': int, 'default': 20},
             {'arg': 'max_population', 'name': 'Max Population', 'type': int, 'default': 100000},
             {'arg': 'max_ab_km2', 'name': 'Max ab/km^2', 'type': int, 'default': 10000},
             {'arg': 'build_probability',
              'name': 'Build Block Probability',
              'type': float, 'default': 0.3},
             {'arg': 'neighboring_centrality_probability',
              'name': 'New Centrality P1',
              'type': float, 'default': 0.1},
             {'arg': 'isolated_centrality_probability',
              'name': 'New Centrality P2',
              'type': float, 'default': 0},
             {'arg': 'T_star', 'name': 'T*', 'type': int, 'default': 5},
             {'arg': 'random_seed', 'name': 'random seed', 'type': int, 'default': 42}
             ]


def make_interface(root, arguments_list):
    entries = {}
    for field in arguments_list:
        print(field)
        row = tk.Frame(root)
        lab = tk.Label(row, width=22, text=field['name'] + ": ", anchor='w')
        ent = tk.Entry(row)
        ent.insert(0, field['default'])
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


def simluation_wrapper(entries, argument_list):
    input_args = {}
    for argument in argument_list:
        input_args[argument['arg']] = argument['type'](entries[argument['arg']].get())
    input_args.update({'input_filepath': None, 'initialization_mode': 'list', 'output_path': None})
    run_isobenefit_simulation(**input_args)


if __name__ == '__main__':
    root = tk.Tk()
    ents = make_interface(root, args_list)
    b1 = tk.Button(root, text='Run simulation',
                   command=(lambda e=ents: simluation_wrapper(e, args_list)))
    b1.pack(side=tk.LEFT, padx=5, pady=5)
    b3 = tk.Button(root, text='Quit', command=root.quit)
    b3.pack(side=tk.LEFT, padx=5, pady=5)
    root.mainloop()
