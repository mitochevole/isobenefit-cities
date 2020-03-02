import copy
from functools import partial

import numpy as np
from scipy.ndimage.measurements import label

from isobenefit_cities import logger
from isobenefit_cities.image_io import import_2Darray_from_image

LOGGER = logger.get_logger()

DENSITY_LEVELS = ['high', 'medium', 'low']
POPULATION_DENSITY = {'high': 1, 'medium': 0.1, 'low': 0.01, 'empty': 0}


class MapBlock:
    def __init__(self, x, y, inhabitants):
        self.x = x
        self.y = y
        self.is_nature = True
        self.is_built = False
        self.is_centrality = False
        self.inhabitants = inhabitants

    def set_block_population(self, block_population, density_level):
        self.inhabitants = block_population * POPULATION_DENSITY[density_level]
        self.density_level = density_level


class Land:
    def __init__(self, size_x, size_y, build_probability=0.5, neighboring_centrality_probability=5e-3,
                 isolated_centrality_probability=1e-1, T_star=10,
                 max_population=500000, max_ab_km2=10000):
        self.size_x = size_x
        self.size_y = size_y
        self.T_star = T_star
        self.map = [[MapBlock(x, y, inhabitants=0) for x in range(size_y)] for y in range(size_x)]
        self.build_probability = build_probability
        self.neighboring_centrality_probability = neighboring_centrality_probability
        self.isolated_centrality_probability = isolated_centrality_probability
        self.max_population = max_population
        # the assumption is that T_star is the number of blocks
        # that equals to a 15 minutes walk, i.e. roughly 1 km. 1 block has size 1000/T_star metres
        self.block_pop = max_ab_km2 / (T_star ** 2)

    def check_consistency(self):
        for x in range(self.size_x):
            for y in range(self.size_y):
                block = self.map[x][y]
                assert (block.is_nature and not block.is_built) or (
                        block.is_built and not block.is_nature), f"({x},{y}) block has ambiguous coordinates"

    def get_map_as_array(self):
        A = np.ones(shape=(self.size_x, self.size_y))
        for x in range(self.size_x):
            for y in range(self.size_y):
                if self.map[x][y].is_built:
                    A[x, y] = 0
        return A

    def set_centralities(self, centralities: list):
        for centrality in centralities:
            x, y = centrality.x, centrality.y
            self.map[x][y].is_centrality = True
            self.map[x][y].is_built = True
            self.map[x][y].is_nature = False

    def get_neighborhood(self, x, y):

        neighborhood = Land(size_x=2 * self.T_star + 1, size_y=2 * self.T_star + 1, T_star=self.T_star)
        for i in range(x - self.T_star, x + self.T_star + 1):
            for j in range(y - self.T_star, y + self.T_star + 1):
                try:
                    neighborhood.map[i + self.T_star - x][j + self.T_star - y] = self.map[i][j]
                except Exception as e:
                    print("i: {}, j: {}, x: {}, y: {}, T: {}".format(i, j, x, y, self.T_star))
                    raise e
        return neighborhood

    def is_any_neighbor_built(self, x, y):
        return (self.map[x - 1][y].is_built or self.map[x + 1][y].is_built or self.map[x][y - 1].is_built or
                self.map[x][y + 1].is_built)

    def has_centrality_nearby(self):
        for x in range(self.size_x):
            for y in range(self.size_y):
                try:
                    if self.map[x][y].is_centrality:
                        if d(x, y, self.T_star, self.T_star) <= self.T_star:
                            return True
                except Exception as e:
                    print("invalid position: x={}, y={}".format(x, y))
                    raise e
        return False

    def is_nature_extended(self, x, y):
        # this method assumes that x,y belongs to a natural region
        land_array = self.get_map_as_array()
        land_array[x, y] = 0
        labels, num_features = label(land_array)
        is_nature_extended = False
        if num_features == 1:
            is_nature_extended = True

        is_wide_enough_height = np.apply_along_axis(partial(is_nature_wide_along_axis, T_star=self.T_star), axis=1,
                                                    arr=land_array)
        is_wide_enough_width = np.apply_along_axis(partial(is_nature_wide_along_axis, T_star=self.T_star), axis=0,
                                                   arr=land_array)
        narrow_places_h = len(is_wide_enough_height) - is_wide_enough_height.sum()
        narrow_places_w = len(is_wide_enough_width) - is_wide_enough_width.sum()

        return narrow_places_h == 0 and narrow_places_w == 0 and is_nature_extended

    def is_nature_reachable(self, x, y):
        land_array = self.get_map_as_array()
        land_array[x, y] = 0
        x_built, y_built = np.where(land_array == 0)
        x_nature, y_nature = np.where(land_array == 1)
        return np.sqrt((x_built[:, None] - x_nature) ** 2 + (y_built[:, None] - y_nature) ** 2).min(
            axis=1).max() <= self.T_star

    def set_configuration_from_image(self, filepath):
        array_map = import_2Darray_from_image(filepath)
        for x in range(self.size_x):
            for y in range(self.size_y):
                if array_map[x, y] == 1:
                    self.map[x][y].is_built = True
                    self.map[x][y].is_centrality = True
                    self.map[x][y].is_nature = False

                if array_map[x, y] == 0:
                    self.map[x][y].is_built = True
                    self.map[x][y].is_centrality = False
                    self.map[x][y].is_nature = False

    def set_current_counts(self):
        tot_population = 0
        tot_centralities = 0
        tot_built = 0
        tot_nature = 0
        for x in range(self.size_x):
            for y in range(self.size_y):
                tot_population += self.map[x][y].inhabitants
                tot_centralities += int(self.map[x][y].is_centrality)
                tot_built += int(self.map[x][y].is_built)
                tot_nature += int(self.map[x][y].is_nature)
        self.current_population = tot_population
        self.current_centralities = tot_centralities
        self.current_built_blocks = tot_built
        self.current_free_nature = tot_nature


def d(x1, y1, x2, y2):
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def is_nature_wide_along_axis(array_1d, T_star):
    features, labels = label(array_1d)
    unique, counts = np.unique(features, return_counts=True)
    if len(counts) > 1:
        return counts[1:].min() >= T_star
    else:
        return True


class IsobenefitScenario(Land):
    def update_map(self):
        added_blocks = 0
        added_centrality = 0
        copy_land = copy.deepcopy(self)
        for x in range(self.T_star, self.size_x - self.T_star):
            for y in range(self.T_star, self.size_y - self.T_star):
                block = self.map[x][y]
                assert (block.is_nature and not block.is_built) or (
                        block.is_built and not block.is_nature), f"({x},{y}) block has ambiguous coordinates"
                if block.is_nature:
                    neighborhood = copy_land.get_neighborhood(x, y)
                    if neighborhood.is_any_neighbor_built(self.T_star, self.T_star):
                        if neighborhood.has_centrality_nearby():
                            if self.is_nature_extended(x, y):
                                if np.random.rand() < self.build_probability:
                                    if self.is_nature_reachable(x, y):
                                        density_level = np.random.choice(DENSITY_LEVELS, p=[0.7, 0.3, 0])
                                        block.is_nature = False
                                        block.is_built = True
                                        block.set_block_population(self.block_pop, density_level)
                                        added_blocks += 1
                        else:
                            if np.random.rand() < self.neighboring_centrality_probability:
                                if self.is_nature_extended(x, y):
                                    if self.is_nature_reachable(x, y):
                                        block.is_centrality = True
                                        block.is_built = True
                                        block.is_nature = False
                                        block.set_block_population(self.block_pop, 'empty')
                                        added_centrality += 1

                    else:
                        if np.random.rand() < self.isolated_centrality_probability / (self.size_x * self.size_y):
                            if self.is_nature_extended(x, y):
                                if self.is_nature_reachable(x, y):
                                    block.is_centrality = True
                                    block.is_built = True
                                    block.is_nature = False
                                    block.set_block_population(self.block_pop, 'empty')
                                    added_centrality += 1
        LOGGER.info(f"added blocks: {added_blocks}")
        LOGGER.info(f"added centralities: {added_centrality}")


class StandardScenario(Land):
    def is_any_neighbor_centrality(self, x, y):
        return (self.map[x - 1][y].is_centrality or self.map[x + 1][y].is_centrality or self.map[x][
            y - 1].is_centrality or
                self.map[x][y + 1].is_centrality)

    def update_map(self):
        added_blocks = 0
        added_centrality = 0
        copy_land = copy.deepcopy(self)
        for x in range(self.T_star, self.size_x - self.T_star):
            for y in range(self.T_star, self.size_y - self.T_star):
                block = self.map[x][y]
                assert (block.is_nature and not block.is_built) or (
                        block.is_built and not block.is_nature), f"({x},{y}) block has ambiguous coordinates"
                if block.is_nature:
                    neighborhood = copy_land.get_neighborhood(x, y)
                    if neighborhood.is_any_neighbor_built(self.T_star, self.T_star):
                        if np.random.rand() < self.build_probability:
                            density_level = np.random.choice(DENSITY_LEVELS, p=[0.01, 0.10, 0.89])
                            block.is_nature = False
                            block.is_built = True
                            block.set_block_population(self.block_pop, density_level)
                            added_blocks += 1
                else:
                    if not block.is_centrality:
                        if block.density_level == 'low':
                            if np.random.rand() < 0.1:
                                block.set_block_population(self.block_pop, 'medium')
                        elif block.density_level == 'medium':
                            if np.random.rand() < 0.01:
                                block.set_block_population(self.block_pop, 'high')
                        elif block.density_level == 'high' and (self.current_built_blocks/self.current_centralities) > 100:
                            if self.is_any_neighbor_centrality(x, y):
                                if np.random.rand() < self.neighboring_centrality_probability:
                                    block.is_centrality = True
                                    block.is_built = True
                                    block.is_nature = False
                                    block.set_block_population(self.block_pop, 'empty')
                                    added_centrality += 1
                            else:
                                if np.random.rand() < self.isolated_centrality_probability:
                                    block.is_centrality = True
                                    block.is_built = True
                                    block.is_nature = False
                                    block.set_block_population(self.block_pop, 'empty')
                                    added_centrality += 1

        LOGGER.info(f"added blocks: {added_blocks}")
        LOGGER.info(f"added centralities: {added_centrality}")
