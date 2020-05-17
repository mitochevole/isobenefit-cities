import json
import os
import time

import numpy as np

from isobenefit_cities import logger
from isobenefit_cities.image_io import save_image_from_2Darray
from isobenefit_cities.initialization_utils import get_central_coord
from isobenefit_cities.land_map import MapBlock, IsobenefitScenario, ClassicalScenario

N_AMENITIES = 1


def run_isobenefit_simulation(size_x, size_y, n_steps, output_path, build_probability,
                              neighboring_centrality_probability, isolated_centrality_probability, T_star,
                              random_seed,
                              input_filepath, initialization_mode, max_population, max_ab_km2, urbanism_model,
                              prob_distribution, density_factors):
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
                'urbanism_model': urbanism_model,
                'prob_distribution': prob_distribution,
                'density_factors': density_factors}
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
                           urbanism_model=urbanism_model, prob_distribution=prob_distribution, density_factors=density_factors)

    canvas = np.ones(shape=(size_x, size_y, 4))
    update_map_snapshot(land, canvas)
    snapshot_path = save_snapshot(canvas, output_path=output_path, step=0)
    land.set_record_counts_header(output_path=output_path)
    land.set_current_counts()
    i = 0
    added_blocks, added_centralities = (0, 0)
    land.record_current_counts(output_path=output_path, iteration=i, added_blocks=added_blocks,
                               added_centralities=added_centralities)

    while i <= n_steps and land.current_population <= land.max_population:
        start = time.time()
        added_blocks, added_centralities = land.update_map()
        land.set_current_counts()
        i += 1
        land.record_current_counts(output_path=output_path, iteration=i, added_blocks=added_blocks,
                                   added_centralities=added_centralities)
        LOGGER.info(f"step: {i}, duration: {time.time() - start} seconds")
        LOGGER.info(f"step: {i}, current population: {land.current_population} inhabitants")
        update_map_snapshot(land, canvas)
        snapshot_path = save_snapshot(canvas, output_path=output_path, step=i)

    LOGGER.info(f"Simulation ended. Total duration: {time.time() - t_zero} seconds")


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
                    isolated_centrality_probability, T, max_population, max_ab_km2, mode,
                    filepath,
                    amenities_list, urbanism_model, prob_distribution, density_factors):
    assert size_x > 2 * T and size_y > 2 * T, f"size of the map is too small: {size_x}x{size_y}. Dimensions should be larger than {2 * T}"
    assert sum(
        prob_distribution) == 1, f"pobability distribution does not sum-up to 1: sum{prob_distribution} = {sum(prob_distribution)}."
    assert density_factors[0] >= density_factors[1] >= density_factors[
        2], f"density factors are not decreasing in value: {density_factors}."

    if urbanism_model == 'isobenefit':
        land = IsobenefitScenario(size_x=size_x, size_y=size_y,
                                  neighboring_centrality_probability=neighboring_centrality_probability,
                                  isolated_centrality_probability=isolated_centrality_probability,
                                  build_probability=build_probability, T_star=T,
                                  max_population=max_population, max_ab_km2=max_ab_km2,
                                  prob_distribution=prob_distribution, density_factors=density_factors)
    elif urbanism_model == 'classical':
        land = ClassicalScenario(size_x=size_x, size_y=size_y,
                                 neighboring_centrality_probability=neighboring_centrality_probability,
                                 isolated_centrality_probability=isolated_centrality_probability,
                                 build_probability=build_probability, T_star=T,
                                 max_population=max_population, max_ab_km2=max_ab_km2,
                                 prob_distribution=prob_distribution, density_factors=density_factors)
    else:
        raise ("Invalid urbanism model. Choose one of 'isobenefit' and 'classical'")

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
            if block.is_nature:
                color = (0 / 255, 158 / 255, 96 / 255)  # green
            elif block.is_centrality:
                color = np.ones(3)
            else:
                if block.is_built and block.density_level == 'high':
                    color = np.zeros(3)
                if block.is_built and block.density_level == 'medium':
                    color = np.ones(3) / 3
                if block.is_built and block.density_level == 'low':
                    color = np.ones(3) * 2 / 3

            canvas[block.y, block.x] = np.array([color[0], color[1], color[2], 1])


def save_snapshot(canvas, output_path, step, format='png'):
    final_path = os.path.join(output_path, f"{step:05d}.png")
    save_image_from_2Darray(canvas, filepath=final_path, format=format)
    return final_path
