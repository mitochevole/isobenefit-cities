import json
import os
import time

import numpy as np

from isobenefit_cities import logger
from isobenefit_cities.image_io import save_image_from_2Darray
from isobenefit_cities.initialization_utils import get_central_coord
from isobenefit_cities.land_map import Land, MapBlock

N_AMENITIES = 1


def run_isobenefit_simulation(size_x, size_y, n_steps, output_path, boundary_conditions, build_probability,
                              neighboring_centrality_probability, isolated_centrality_probability, T_star, minimum_area,
                              random_seed,
                              input_filepath, initialization_mode):
    metadata = {}
    logger.configure_logging()
    LOGGER = logger.get_logger()
    np.random.seed(random_seed)
    if output_path is None:
        timestamp = time.strftime("%Y%m%d-%H%M%S", time.localtime())
        output_path = f"simulations/{timestamp}"
    os.makedirs(output_path)
    metadata['output_path'] = output_path
    t_zero = time.time()
    land = initialize_land(size_x, size_y,
                           amenities_list=get_central_coord(size_x=size_x, size_y=size_y),
                           boundary_conditions=boundary_conditions,
                           neighboring_centrality_probability=neighboring_centrality_probability,
                           isolated_centrality_probability=isolated_centrality_probability,
                           build_probability=build_probability, T=T_star, minimum_area=minimum_area,
                           mode=initialization_mode,
                           filepath=input_filepath)

    canvas = np.ones(shape=(size_x, size_y)) * 0.5
    update_map_snapshot(land, canvas)
    snapshot_path = save_snapshot(canvas, output_path=output_path, step=0)
    i = 0
    current_population = 0
    while i <= n_steps and current_population <= land.max_population:
        start = time.time()
        land.update_map()
        current_population = land.get_current_population()
        LOGGER.info(f"step: {i}, duration: {time.time() - start} seconds")
        LOGGER.info(f"step: {i}, current population: {current_population} inhabitants")
        update_map_snapshot(land, canvas)
        snapshot_path = save_snapshot(canvas, output_path=output_path, step=i + 1)
        i+=1

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
        amenities = [MapBlock(x, y, inhabitants=0) for (x, y) in amenities_list]
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
    return final_path
