import argparse
import os
import time

import matplotlib.pyplot as plt
import numpy as np

from isobenefit_cities.land_map import Land, MapBlock
from simulation_config import AMENITIES_COORDINATES


def main(size_x, size_y, n_steps, output_path):
    if output_path is None:
        timestamp = time.strftime("%Y%m%d-%H%M%S",time.localtime())
        output_path = f"simulations/{timestamp}"
    os.makedirs(output_path)
    t_zero = time.time()
    amenities_list = AMENITIES_COORDINATES
    land = initialize_land(size_x, size_y, amenities_list)
    canvas = np.zeros(shape=(size_x, size_y))
    update_map_snapshot(land, canvas)
    save_snapshot(canvas, output_path=output_path, step=0)
    for i in range(n_steps):
        start = time.time()
        land.update_map()
        print(f"step: {i}, duration: {time.time() - start} seconds")
        update_map_snapshot(land, canvas)
        save_snapshot(canvas, output_path=output_path, step=i + 1)
    print(f"Simulation ended. Total duration: {time.time()-t_zero} seconds")


def initialize_land(size_x, size_y, amenities_list):
    land = Land(size_x=size_x, size_y=size_y, boundary_conditions='periodic')
    amenities = [MapBlock(x, y) for (x, y) in amenities_list]
    land.set_centralities(amenities)
    return land


def update_map_snapshot(land, canvas):
    for row in land.map:
        for block in row:
            if block.is_built:
                canvas[block.x, block.y] = 1
            if block.is_centrality:
                canvas[block.x, block.y] = 2


def save_snapshot(canvas, output_path, step, format='png'):
    if format == 'png':
        plt.imshow(canvas)
        plt.axis('off')
        final_path = os.path.join(output_path, f"{step}.png")
        plt.savefig(final_path)


def create_arg_parser():
    parser = argparse.ArgumentParser(
        description="""Start simulation.
        """,
        epilog="Example: ...",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('--n-steps',
                        required=True,
                        type=int,
                        help="number of steps for the simulation")

    parser.add_argument('--size-x',
                        required=True,
                        type=int,
                        help="width of the land map")

    parser.add_argument('--size-y',
                        required=True,
                        type=int,
                        help="height of the land map")

    parser.add_argument('--output-path',
                        required=False,
                        type=str,
                        help="output path to store simulation results")

    return parser


if __name__ == "__main__":
    parser = create_arg_parser()
    args = parser.parse_args()
    size_x = args.size_x
    size_y = args.size_y
    n_steps = args.n_steps
    output_path = args.output_path

    main(size_x=size_x, size_y=size_y, n_steps=n_steps, output_path=output_path)
