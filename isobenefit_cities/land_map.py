import copy
from functools import partial

import numpy as np
from matplotlib import cm
from scipy.ndimage.measurements import label

from isobenefit_cities import logger
from isobenefit_cities.image_io import save_image_from_2Darray, import_2Darray_from_image

LOGGER = logger.get_logger()


def d(x1, y1, x2, y2):
    # return abs(x1-x2) + abs(y1-y2)
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def is_nature_wide_along_axis(array_1d, T_star):
    features, labels = label(array_1d)
    unique, counts = np.unique(features, return_counts=True)
    if len(counts) > 1:
        return counts[1:].min() >= T_star
    else:
        return True


class MapBlock:
    def __init__(self, x, y, inhabitants):
        self.x = x
        self.y = y
        self.is_nature = True
        self.is_built = False
        self.is_centrality = False
        self.inhabitants = inhabitants



class Land:
    def __init__(self, size_x, size_y, build_probability=0.5, neighboring_centrality_probability=5e-3,
                 isolated_centrality_probability=1e-1, T_star=10, minimum_area=100, boundary_conditions='mirror',
                 max_population=500000, max_ab_km2=5000):
        self.size_x = size_x
        self.size_y = size_y
        self.T_star = T_star
        self.map = [[MapBlock(x, y, inhabitants=0) for x in range(size_y)] for y in range(size_x)]
        self.boundary_conditions = boundary_conditions
        self.minimum_area = minimum_area
        self.build_probability = build_probability
        self.neighboring_centrality_probability = neighboring_centrality_probability
        self.isolated_centrality_probability = isolated_centrality_probability
        self.max_population = max_population
        #the assumption is that T_star is the number of blocks
        # that equals to a 15 minutes walk, i.e. roughly 1 km. 1 block has size 1000/T_star metres
        self.block_pop = max_ab_km2/(T_star**2)


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

    def save_land(self, filepath, color_map=cm.gist_earth, format='png'):
        land = self.get_map_as_array()
        save_image_from_2Darray(land_array=land, filepath=filepath, color_map=color_map, format=format)

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
                i2, j2 = self.boundary_transform(i, j)
                try:
                    neighborhood.map[i + self.T_star - x][j + self.T_star - y] = self.map[i2][j2]
                except Exception as e:
                    print("i: {}, j: {}, i2: {}, j2: {}, x: {}, y: {}, T: {}".format(i, j, i2, j2, x, y, self.T_star))
                    raise e
        return neighborhood

    def boundary_transform(self, i, j):
        if self.boundary_conditions == 'mirror':
            if i < 0:
                i = -i
            if j < 0:
                j = -j
            if i >= self.size_x:
                i = self.size_x - i % self.size_x - 1
            if j >= self.size_y:
                j = self.size_y - j % self.size_y - 1

        if self.boundary_conditions == 'periodic':
            if i < 0:
                i = self.size_x + i
            if j < 0:
                j = self.size_y + j
            if i >= self.size_x:
                i = i - self.size_x
            if j >= self.size_y:
                j = j - self.size_y
        return i, j

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

    def update_map(self):
        added_blocks = 0
        added_centrality = 0
        copy_land = copy.deepcopy(self)
        for x in range(self.size_x):
            for y in range(self.size_y):
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
                                        random_factor = np.random.choice([1,0.1,0.001],p=[0.7,0.3,0])
                                        block.is_nature = False
                                        block.is_built = True
                                        block.inhabitants = self.block_pop * random_factor
                                        added_blocks += 1
                        else:
                            if np.random.rand() < self.neighboring_centrality_probability:
                                if self.is_nature_extended(x, y):
                                    if self.is_nature_reachable(x, y):
                                        block.is_centrality = True
                                        block.is_built = True
                                        block.is_nature = False
                                        added_centrality += 1

                    else:
                        if np.random.rand() < self.isolated_centrality_probability / (self.size_x * self.size_y):
                            if self.is_nature_extended(x, y):
                                if self.is_nature_reachable(x, y):
                                    block.is_centrality = True
                                    block.is_built = True
                                    block.is_nature = False
                                    added_centrality += 1
        LOGGER.info(f"added blocks: {added_blocks}")
        LOGGER.info(f"added centralities: {added_centrality}")

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


    def get_current_population(self):
        tot_population = 0
        for x in range(self.size_x):
            for y in range(self.size_y):
                tot_population+=self.map[x][y].inhabitants
        return tot_population
