import numpy as np
import copy
from scipy.ndimage.measurements import label


def d(x1, y1, x2, y2):
    # return abs(x1-x2) + abs(y1-y2)
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


class MapBlock:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_nature = True
        self.is_built = False
        self.is_centrality = False
        self.built_size = 0
        self.nature_size = 0

class Land:
    def __init__(self, size_x, size_y, probability=0.5, T=10, minimum_area=100, boundary_conditions='reflect'):
        self.size_x = size_x
        self.size_y = size_y
        self.T = T
        self.map = [[MapBlock(x, y) for x in range(size_y)] for y in range(size_x)]
        self.boundary_conditions = boundary_conditions
        self.minimum_area = minimum_area
        self.probability = probability

    def boundary_transform(self, i, j):
        if self.boundary_conditions == 'reflect':
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
        neighborhood = Land(2 * self.T +1, 2 * self.T+1)
        for i in range(x - self.T , x + self.T + 1):
            for j in range(y - self.T, y + self.T + 1):
                i2, j2 = self.boundary_transform(i, j)
                try:
                    neighborhood.map[i + self.T - x][j + self.T - y] = self.map[i2][j2]
                except Exception as e:
                    print("i: {}, j: {}, i2: {}, j2: {}, x: {}, y: {}, T: {}".format(i, j, i2, j2, x, y, self.T))
                    raise e
        return neighborhood

    def is_any_neighbor_built(self, x, y):
        return (self.map[x - 1][y].is_built or self.map[x + 1][y].is_built or self.map[x][y - 1].is_built or
                self.map[x][y + 1].is_built)

    def has_centrality_nearby(self):
        for x in range(2 * self.T):
            for y in range(2 * self.T):
                if self.map[x][y].is_centrality:
                    if d(x, y, self.T, self.T) <= self.T:
                        return True
        return False

    def obstructs_access_to_nature(self):
        #TODO this is not working
        for x in range(self.size_x):
            for y in range(self.size_y):
                if self.map[x][y].is_nature:
                    if d(x, y, self.T, self.T) <= self.T:
                        return True

        return False

    def is_nature_extended(self, x, y):
        # this method assumes that x,y belongs to a natural region
        land_array = self.get_map_as_array()
        labels, num_features = label(land_array)
        if num_features == 1:
            return True
        elif num_features > 1:
            xy_label = labels[x, y]
            size_of_region = np.where(labels == xy_label, True, False).sum()
            # print(size_of_region)
            return size_of_region >= self.minimum_area + 1 #or size_of_region < self.minimum_area

    def update_map(self):
        np.random.seed(42)
        copy_land = copy.deepcopy(self)
        for x in range(self.size_x):
            for y in range(self.size_y):
                block = self.map[x][y]
                assert (block.is_nature and not block.is_built) or (block.is_built and not block.is_nature)
                if block.is_nature:
                    neighborhood = copy_land.get_neighborhood(x, y)
                    if neighborhood.is_any_neighbor_built(self.T, self.T):
                        if neighborhood.has_centrality_nearby():
                            if self.is_nature_extended(x, y):
                                if np.random.rand() > self.probability:
                                    #if not self.obstructs_access_to_nature():
                                        block.is_nature = False
                                        block.is_built = True

