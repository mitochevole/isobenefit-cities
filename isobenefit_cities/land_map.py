import copy
import os
from functools import partial

import numpy as np
from scipy.ndimage import measurements as measure

from isobenefit_cities import logger
from isobenefit_cities.image_io import import_2Darray_from_image

LOGGER = logger.get_logger()

DENSITY_LEVELS = ['high', 'medium', 'low']


class MapBlock:
    def __init__(self, x, y, inhabitants=0):
        self.x = x
        self.y = y
        self.is_nature = True
        self.is_built = False
        self.is_centrality = False
        self.inhabitants = inhabitants

    def set_block_population(self, block_population, density_level, population_density):
        self.inhabitants = block_population * population_density[density_level]
        self.density_level = density_level


class Land:
    def __init__(self, size_x, size_y, build_probability=0.5, neighboring_centrality_probability=5e-3,
                 isolated_centrality_probability=1e-1, T_star=5,
                 max_population=500000, max_ab_km2=10000, prob_distribution=(0.7, 0.3, 0),
                 density_factors=(1, 0.1, 0.01)):
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
        self.probability_distribution = prob_distribution
        self.population_density = {'high': density_factors[0], 'medium': density_factors[1], 'low': density_factors[2],
                                   'empty': 0}

        self.avg_dist_from_nature = 0
        self.avg_dist_from_centr = 0
        self.max_dist_from_nature = 0
        self.max_dist_from_centr = 0
        self.current_population = 0
        self.current_centralities = 0
        self.current_built_blocks = 0
        self.current_free_nature = np.inf

    def check_consistency(self):
        for x in range(self.size_x):
            for y in range(self.size_y):
                block = self.map[x][y]
                assert (block.is_nature and not block.is_built) or (
                        block.is_built and not block.is_nature), f"({x},{y}) block has ambiguous coordinates"

    def get_map_as_array(self):
        map_array = np.zeros(shape=(self.size_x, self.size_y))
        population_array = np.ones(shape=(self.size_x, self.size_y))
        for x in range(self.size_x):
            for y in range(self.size_y):
                if self.map[x][y].is_built:
                    map_array[x, y] = 1
                if self.map[x][y].is_centrality:
                    map_array[x, y] = 2
                population_array[x, y] = self.map[x][y].inhabitants

        return map_array, population_array

    def set_centralities(self, centralities: list):
        for centrality in centralities:
            x, y = centrality.x, centrality.y
            self.map[x][y].is_centrality = True
            self.map[x][y].is_built = True
            self.map[x][y].is_nature = False
            self.map[x][y].inhabitants = 0

    def is_any_neighbor_built(self, x, y):
        assert self.T_star <= x <= self.size_x - self.T_star, f"point ({x},{y}) is not in the 'interior' of the land"
        assert self.T_star <= y <= self.size_y - self.T_star, f"point ({x},{y}) is not in the 'interior' of the land"
        return (self.map[x - 1][y].is_built or self.map[x + 1][y].is_built or self.map[x][y - 1].is_built or
                self.map[x][y + 1].is_built)

    def is_centrality_near(self, x, y):
        assert self.T_star <= x <= self.size_x - self.T_star, f"point ({x},{y}) is not in the 'interior' of the land"
        assert self.T_star <= y <= self.size_y - self.T_star, f"point ({x},{y}) is not in the 'interior' of the land"

        for i in range(x - self.T_star, x + self.T_star + 1):
            for j in range(y - self.T_star, y + self.T_star + 1):
                if self.map[i][j].is_centrality:
                    if d(x, y, i, j) <= self.T_star:
                        return True
        return False

    def nature_stays_extended(self, x, y):
        # this method assumes that x,y belongs to a natural region
        land_array, _ = self.get_map_as_array()
        land_array[x, y] = 1
        bin_array = np.where(land_array == 0, 1, 0)
        labels, num_features = measure.label(bin_array)
        is_nature_extended = False
        if num_features == 1:
            is_nature_extended = True

        is_wide_enough_height = np.apply_along_axis(partial(is_nature_wide_along_axis, T_star=self.T_star), axis=1,
                                                    arr=bin_array)
        is_wide_enough_width = np.apply_along_axis(partial(is_nature_wide_along_axis, T_star=self.T_star), axis=0,
                                                   arr=bin_array)
        narrow_places_h = len(is_wide_enough_height) - is_wide_enough_height.sum()
        narrow_places_w = len(is_wide_enough_width) - is_wide_enough_width.sum()

        return narrow_places_h == 0 and narrow_places_w == 0 and is_nature_extended

    def nature_stays_reachable(self, x, y):
        land_array, _ = self.get_map_as_array()
        land_array[x, y] = 1
        x_built, y_built = np.where(land_array > 0)
        x_nature, y_nature = np.where(land_array == 0)
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
        tot_distance_from_nature = 0
        tot_distance_from_centrality = 0
        max_dist_from_nature = self.max_dist_from_nature
        max_dist_from_centr = self.max_dist_from_centr
        land_array, population_array = self.get_map_as_array()

        self.current_population = population_array.sum()
        self.current_centralities = np.where(land_array == 2, 1, 0).sum()
        self.current_built_blocks = np.where(land_array > 0, 1, 0).sum()
        self.current_free_nature = np.where(land_array == 0, 1, 0).sum()
        tot_inhabited_blocks = np.where(land_array == 1, 1, 0).sum()
        if tot_inhabited_blocks == 0:
            self.avg_dist_from_nature = 0
            self.avg_dist_from_centr = 0
            self.max_dist_from_nature = 0
            self.max_dist_from_centr = 0

        else:
            x_centr, y_centr = np.where(land_array == 2)
            x_built, y_built = np.where(land_array == 1)
            x_nature, y_nature = np.where(land_array == 0)
            distances_from_nature = np.sqrt(
                (x_built[:, None] - x_nature) ** 2 + (y_built[:, None] - y_nature) ** 2).min(
                axis=1)
            distances_from_centr = np.sqrt((x_built[:, None] - x_centr) ** 2 + (y_built[:, None] - y_centr) ** 2).min(
                axis=1)
            self.avg_dist_from_nature = distances_from_nature.sum() / tot_inhabited_blocks
            self.avg_dist_from_centr = distances_from_centr.sum() / tot_inhabited_blocks
            self.max_dist_from_nature = distances_from_nature.max()
            self.max_dist_from_centr = distances_from_centr.max()

    def get_min_distances(self, x, y):
        r = 1
        nature_dist = np.inf
        centrality_dist = np.inf
        while (r <= self.T_star):
            for i in range(x - r, x + r + 1):
                for j in [y - r, y + r]:
                    i, j = self.adjust_boundary_coords(i, j)
                    if self.map[i][j].is_nature:
                        nature_dist = min(nature_dist, d(x, y, i, j))
                    if self.map[i][j].is_centrality:
                        centrality_dist = min(centrality_dist, d(x, y, i, j))
            for j in range(y - r + 1, y + r - 1 + 1):
                for i in [x - r, x + r]:
                    i, j = self.adjust_boundary_coords(i, j)
                    if self.map[i][j].is_nature:
                        nature_dist = min(nature_dist, d(x, y, i, j))
                    if self.map[i][j].is_centrality:
                        centrality_dist = min(centrality_dist, d(x, y, i, j))
            r += 1
        return nature_dist, centrality_dist

    def adjust_boundary_coords(self, i, j):
        if i < 0:
            i_new = 0
        elif i >= self.size_x:
            i_new = self.size_x - 1
        else:
            i_new = i
        if j < 0:
            j_new = 0
        elif j >= self.size_y:
            j_new = self.size_y - 1
        else:
            j_new = j
        return i_new, j_new

    def set_record_counts_header(self, output_path):
        filename = os.path.join(output_path, 'current_counts.csv')
        with open(filename, "a") as f:
            f.write(
                "iteration,added_blocks,added_centralities,current_built_blocks,current_centralities,"
                "current_free_nature,current_population,avg_dist_from_nature,avg_dist_from_centr,max_dist_from_nature,max_dist_from_centr\n")

    def record_current_counts(self, output_path, iteration, added_blocks, added_centralities):
        filename = os.path.join(output_path, 'current_counts.csv')
        with open(filename, "a") as f:
            f.write(
                f"{iteration},{added_blocks},{added_centralities},"
                f"{self.current_built_blocks},{self.current_centralities},"
                f"{self.current_free_nature},{self.current_population},"
                f"{self.avg_dist_from_nature},{self.avg_dist_from_centr},"
                f"{self.max_dist_from_nature},{self.max_dist_from_centr}\n")


def d(x1, y1, x2, y2):
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def is_nature_wide_along_axis(array_1d, T_star):
    features, labels = measure.label(array_1d)
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
                    if copy_land.is_any_neighbor_built(x, y):
                        if copy_land.is_centrality_near(x, y):
                            if self.nature_stays_extended(x, y):
                                if np.random.rand() < self.build_probability:
                                    if self.nature_stays_reachable(x, y):
                                        density_level = np.random.choice(DENSITY_LEVELS,
                                                                         p=self.probability_distribution)
                                        block.is_nature = False
                                        block.is_built = True
                                        block.set_block_population(self.block_pop, density_level,
                                                                   self.population_density)
                                        added_blocks += 1
                        else:
                            if np.random.rand() < self.neighboring_centrality_probability:
                                if self.nature_stays_extended(x, y):
                                    if self.nature_stays_reachable(x, y):
                                        block.is_centrality = True
                                        block.is_built = True
                                        block.is_nature = False
                                        block.set_block_population(self.block_pop, 'empty', self.population_density)
                                        added_centrality += 1

                    else:
                        if np.random.rand() < self.isolated_centrality_probability / (self.size_x * self.size_y):
                            if self.nature_stays_extended(x, y):
                                if self.nature_stays_reachable(x, y):
                                    block.is_centrality = True
                                    block.is_built = True
                                    block.is_nature = False
                                    block.set_block_population(self.block_pop, 'empty', self.population_density)
                                    added_centrality += 1
        LOGGER.info(f"added blocks: {added_blocks}")
        LOGGER.info(f"added centralities: {added_centrality}")
        return added_blocks, added_centrality


class ClassicalScenario(Land):
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
                    if copy_land.is_any_neighbor_built(x, y):
                        if np.random.rand() < self.build_probability:
                            density_level = np.random.choice(DENSITY_LEVELS, p=self.probability_distribution)
                            block.is_nature = False
                            block.is_built = True
                            block.set_block_population(self.block_pop, density_level, self.population_density)
                            added_blocks += 1

                    # todo fix generation of new centralities away from main centre
                    else:
                        if np.random.rand() < self.isolated_centrality_probability / np.sqrt(
                                self.size_x * self.size_y) and (
                                self.current_built_blocks / self.current_centralities) > 100:
                            block.is_centrality = True
                            block.is_built = True
                            block.is_nature = False
                            block.set_block_population(self.block_pop, 'empty', self.population_density)
                            added_centrality += 1
                else:
                    if not block.is_centrality:
                        if block.density_level == 'low':
                            if np.random.rand() < 0.1:
                                block.set_block_population(self.block_pop, 'medium', self.population_density)
                        elif block.density_level == 'medium':
                            if np.random.rand() < 0.01:
                                block.set_block_population(self.block_pop, 'high', self.population_density)
                        elif block.density_level == 'high' and (
                                self.current_built_blocks / self.current_centralities) > 100:
                            if self.is_any_neighbor_centrality(x, y):
                                if np.random.rand() < self.neighboring_centrality_probability:
                                    block.is_centrality = True
                                    block.is_built = True
                                    block.is_nature = False
                                    block.set_block_population(self.block_pop, 'empty', self.population_density)
                                    added_centrality += 1
                            else:
                                if np.random.rand() < self.isolated_centrality_probability:  # /np.sqrt(self.current_built_blocks):
                                    block.is_centrality = True
                                    block.is_built = True
                                    block.is_nature = False
                                    block.set_block_population(self.block_pop, 'empty', self.population_density)
                                    added_centrality += 1

        LOGGER.info(f"added blocks: {added_blocks}")
        LOGGER.info(f"added centralities: {added_centrality}")
        return added_blocks, added_centrality
