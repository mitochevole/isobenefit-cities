import argparse
import os
import time

# import yaml
import numpy as np

from isobenefit_cities import logger
from isobenefit_cities.image_io import save_image_from_2Darray
from isobenefit_cities.initialization_utils import get_central_coord
from isobenefit_cities.land_map import Land, MapBlock

LOGGER = logger.get_logger()
N_AMENITIES = 1


def main(size_x, size_y, n_steps, output_path, boundary_conditions, build_probability,
         neighboring_centrality_probability, isolated_centrality_probability, T_star, minimum_area, random_seed,
         input_filepath, initialization_mode):
    logger.configure_logging()
    LOGGER = logger.get_logger()
    np.random.seed(random_seed)
    if output_path is None:
        timestamp = time.strftime("%Y%m%d-%H%M%S", time.localtime())
        output_path = f"simulations/{timestamp}"
    os.makedirs(output_path)
    t_zero = time.time()

    land = initialize_land(size_x, size_y,
                           # amenities_list=get_random_coordinates(size_x=size_x, size_y=size_y, n_amenities=N_AMENITIES, seed=random_seed),
                           amenities_list=get_central_coord(size_x=size_x, size_y=size_y),
                           boundary_conditions=boundary_conditions,
                           neighboring_centrality_probability=neighboring_centrality_probability,
                           isolated_centrality_probability=isolated_centrality_probability,
                           build_probability=build_probability, T=T_star, minimum_area=minimum_area,
                           mode=initialization_mode,
                           filepath=input_filepath)

    canvas = np.ones(shape=(size_x, size_y)) * 0.5
    update_map_snapshot(land, canvas)
    save_snapshot(canvas, output_path=output_path, step=0)
    for i in range(n_steps):
        start = time.time()
        land.update_map()
        LOGGER.info(f"step: {i}, duration: {time.time() - start} seconds")
        update_map_snapshot(land, canvas)
        save_snapshot(canvas, output_path=output_path, step=i + 1)
    LOGGER.info(f"Simulation ended. Total duration: {time.time()-t_zero} seconds")


def initialize_land(size_x, size_y, boundary_conditions, build_probability, neighboring_centrality_probability,
                    isolated_centrality_probability, T, minimum_area, mode=None, filepath=None,
                    amenities_list=None):
    land = Land(size_x=size_x, size_y=size_y, boundary_conditions=boundary_conditions,
                neighboring_centrality_probability=neighboring_centrality_probability,
                isolated_centrality_probability=isolated_centrality_probability,
                build_probability=build_probability, T_star=T, minimum_area=minimum_area)
    if mode == 'image' and filepath is not None:
        land.set_configuration_from_image(filepath)
    elif mode == 'list':
        amenities = [MapBlock(x, y) for (x, y) in amenities_list]
        land.set_centralities(amenities)
    else:
        raise Exception('Invalid initialization mode. Valid modes are "image" and "list".')
    land.check_consistency()
    return land


def update_map_snapshot(land, canvas):
    for row in land.map:
        for block in row:
            if block.is_built:
                canvas[block.y, block.x] = 0
            if block.is_centrality:
                canvas[block.y, block.x] = 1


def save_snapshot(canvas, output_path, step, format='png'):
    final_path = os.path.join(output_path, f"{step:05d}.png")
    save_image_from_2Darray(canvas, filepath=final_path, format=format)


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

    parser.add_argument('--build-probability',
                        required=False,
                        type=float,
                        default=0.5,
                        help="probability of building a new block")

    parser.add_argument('--neighboring-centrality-probability',
                        required=False,
                        type=float,
                        default=5e-3,
                        help="probability of building a new centrality next to a constructed area")

    parser.add_argument('--isolated-centrality-probability',
                        required=False,
                        type=float,
                        default=1e-1,
                        help="probability of building a new centrality in a natural area")

    parser.add_argument('--minimum-area',
                        required=False,
                        type=int,
                        default=100,
                        help="minimum continuous area to be preserved as nature")

    parser.add_argument('--T',
                        required=False,
                        type=int,
                        default=10,
                        help="standard maximum distance from centralities and nature")

    parser.add_argument('--boundary-conditions',
                        required=False,
                        type=str,
                        default='mirror',
                        help="the boundary conditions of the land, possible options are 'mirror' and 'periodic'")

    parser.add_argument('--random-seed',
                        required=False,
                        type=int,
                        default=42,
                        help="for reproducibility set a specific random seed")

    parser.add_argument('--input-filepath',
                        required=False,
                        type=str,
                        help="image filepath for initial configuration")

    parser.add_argument('--initialization-mode',
                        required=True,
                        type=str,
                        help="initial configuration can be set via an input image or via a list of initial centralities")

    return parser


if __name__ == "__main__":
    # with open('config.yaml', "r") as config_file:
    #    SIMULATION_CONFIG = yaml.load(config_file, Loader=yaml.SafeLoader)
    # main(**SIMULATION_CONFIG)
    parser = create_arg_parser()
    args = parser.parse_args()
    size_x = args.size_x
    size_y = args.size_y
    n_steps = args.n_steps
    output_path = args.output_path
    boundary_conditions = args.boundary_conditions
    build_probability = args.build_probability
    T = args.T
    minimum_area = args.minimum_area
    random_seed = args.random_seed
    input_file_path = args.input_filepath
    initialization_mode = args.initialization_mode
    neighboring_centrality_probability = args.neighboring_centrality_probability
    isolated_centrality_probability = args.isolated_centrality_probability
    LOGGER.info(args)
    main(size_x=size_x, size_y=size_y, n_steps=n_steps, output_path=output_path,
         boundary_conditions=boundary_conditions, build_probability=build_probability,
         neighboring_centrality_probability=neighboring_centrality_probability,
         isolated_centrality_probability=isolated_centrality_probability, T_star=T, minimum_area=minimum_area,
         random_seed=random_seed, input_filepath=input_file_path, initialization_mode=initialization_mode)
