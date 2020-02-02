import copy
from functools import partial

import numpy as np
from matplotlib import cm
from scipy.ndimage.measurements import label

from isobenefit_cities.image_io import save_image_from_2Darray, import_2Darray_from_image


def d(x1, y1, x2, y2):
    # return abs(x1-x2) + abs(y1-y2)
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def is_nature_wide_along_axis(array_1d, T_star):
    features, labels = label(array_1d)
    unique, counts = np.unique(features, return_counts=True)
    if len(counts)>1:
        return counts[1:].min() >= T_star
    else:
        return True

class MapBlock:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_nature = True
        self.is_built = False
        self.is_centrality = False


class Land:
    def __init__(self, size_x, size_y, probability=0.5, T_star=10, minimum_area=100, boundary_conditions='mirror'):
        self.size_x = size_x
        self.size_y = size_y
        self.T_star = T_star
        self.map = [[MapBlock(x, y) for x in range(size_y)] for y in range(size_x)]
        self.boundary_conditions = boundary_conditions
        self.minimum_area = minimum_area
        self.probability = probability

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
        # elif num_features > 1:
        #     xy_label = labels[x, y]
        #     size_of_region = np.where(labels == xy_label, True, False).sum()
        #     is_nature_extended = (size_of_region >= self.minimum_area + 1)

        is_wide_enough_height = np.apply_along_axis(partial(is_nature_wide_along_axis, T_star=self.T_star), axis=1, arr=land_array)
        is_wide_enough_width = np.apply_along_axis(partial(is_nature_wide_along_axis, T_star=self.T_star), axis=0, arr=land_array)
        narrow_places_h = len(is_wide_enough_height) - is_wide_enough_height.sum()
        narrow_places_w = len(is_wide_enough_width) - is_wide_enough_width.sum()

        return narrow_places_h < 5 and narrow_places_w < 5 and is_nature_extended

        #xy_label = labels[x, y]
        #width_of_region = np.where(labels == xy_label, True, False).sum()
        #labels_after, num_features_after = label(land_array)
        #nature_sizes = [np.where(labels_after == l, True, False).sum() for l in range(1, num_features_after + 1)]


    def is_nature_reachable(self, x, y):
        land_array = self.get_map_as_array()
        land_array[x, y] = 0
        x_built, y_built = np.where(land_array == 0)
        x_nature, y_nature = np.where(land_array == 1)
        return np.sqrt((x_built[:, None] - x_nature) ** 2 + (y_built[:, None] - y_nature) ** 2).min(
            axis=1).max() <= self.T_star

    def update_map(self):
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
                                if np.random.rand() < self.probability:
                                    if self.is_nature_reachable(x, y):
                                        block.is_nature = False
                                        block.is_built = True
                        else:
                            if np.random.rand() < 1.e-2:
                                if self.is_nature_extended(x, y):
                                    block.is_centrality = True
                                    block.is_built = True
                                    block.is_nature = False

                    else:
                        if np.random.rand() < -1:#1/(self.size_x*self.size_y*10):
                            block.is_centrality = True
                            block.is_built = True
                            block.is_nature = False

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
