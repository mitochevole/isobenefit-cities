import json
import os
import time

import numpy as np

from isobenefit_cities import logger
from isobenefit_cities.image_io import save_image_from_2Darray
from isobenefit_cities.initialization_utils import get_central_coord
from isobenefit_cities.land_map import MapBlock, IsobenefitScenario, StandardScenario

N_AMENITIES = 1


def run_isobenefit_simulation(size_x, size_y, n_steps, output_path, build_probability,
                              neighboring_centrality_probability, isolated_centrality_probability, T_star,
                              random_seed,
                              input_filepath, initialization_mode, max_population, max_ab_km2, urbanism_model):
    metadata = {'size_x': size_x,
                'size_y': size_y,
                'n_steps': n_steps,
                'output_path': output_path,
                'build_probability': build_probability,
                'neighboring_centrality_probability': neighboring_centrality_probability,
                'isolated_centrality_probability': isolated_centrality_probability,
                'T_star': T_star,
                'random_seed': random_seed,
                'input_filepath': input_filepath,
                'initialization_mode': initialization_mode,
                'max_population': max_population,
                'max_ab_km2': max_ab_km2,
                'urbanism_model': urbanism_model}
    logger.configure_logging()
    LOGGER = logger.get_logger()
    np.random.seed(random_seed)

    output_path = make_output_path(output_path)
    os.makedirs(output_path)
    save_metadata(metadata, output_path)

    t_zero = time.time()
    land = initialize_land(size_x, size_y,
                           amenities_list=get_central_coord(size_x=size_x, size_y=size_y),
                           neighboring_centrality_probability=neighboring_centrality_probability,
                           isolated_centrality_probability=isolated_centrality_probability,
                           build_probability=build_probability, T=T_star,
                           mode=initialization_mode,
                           filepath=input_filepath, max_population=max_population, max_ab_km2=max_ab_km2,
                           urbanism_model=urbanism_model)

    canvas = np.ones(shape=(size_x, size_y, 4))
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
        i += 1

    LOGGER.info(f"Simulation ended. Total duration: {time.time()-t_zero} seconds")


def make_output_path(output_path):
    if output_path is None:
        timestamp = time.strftime("%Y%m%d-%H%M%S", time.localtime())
        output_path = f"simulations/{timestamp}"

    return output_path


def save_metadata(metadata, output_path: str):
    metadata['output_path'] = output_path
    metadata_filepath = os.path.join(output_path, 'metadata.json')
    with open(metadata_filepath, 'w') as f:
        f.write(json.dumps(metadata))


def initialize_land(size_x, size_y, build_probability, neighboring_centrality_probability,
                    isolated_centrality_probability, T, max_population, max_ab_km2, mode=None,
                    filepath=None,
                    amenities_list=None, urbanism_model='isobenefit'):
    assert size_x > 2 * T and size_y > 2 * T, f"size of the map is too small: {size_x}x{size_y}. Dimensions should be larger than {2*T}"
    if urbanism_model == 'isobenefit':
        land = IsobenefitScenario(size_x=size_x, size_y=size_y,
                                  neighboring_centrality_probability=neighboring_centrality_probability,
                                  isolated_centrality_probability=isolated_centrality_probability,
                                  build_probability=build_probability, T_star=T,
                                  max_population=max_population, max_ab_km2=max_ab_km2)
    elif urbanism_model == 'standard':
        land = StandardScenario(size_x=size_x, size_y=size_y,
                                neighboring_centrality_probability=neighboring_centrality_probability,
                                isolated_centrality_probability=isolated_centrality_probability,
                                build_probability=build_probability, T_star=T,
                                max_population=max_population, max_ab_km2=max_ab_km2)
    else:
        raise ("Invalid urbanism model. Choose one of 'isobenefit' and 'standard'")

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
                color = np.ones(3) * (-0.33 * np.log10(block.inhabitants / land.block_pop))
                if block.is_centrality:
                    color = np.ones(3)
            else:
                color = (0 / 255, 158 / 255, 96 / 255)  # green
            canvas[block.y, block.x] = np.array([color[0], color[1], color[2], 1])


def save_snapshot(canvas, output_path, step, format='png'):
    final_path = os.path.join(output_path, f"{step:05d}.png")
    save_image_from_2Darray(canvas, filepath=final_path, format=format)
    return final_path
