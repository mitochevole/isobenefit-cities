import numpy as np

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

    def distance_from(self, block):
        return d(self.x, self.y, block.x, block.y)

    def set_nearest_centrality(self, centralities: list):
        centralities_distances = []
        for block in centralities:
            centralities_distances.append(self.distance_from(block))
        idx = np.argmin(np.array(centralities_distances))
        self.nearest_centrality = centralities[idx]

    def set_nearest_nature_block(nature_blocks):
        pass

    def get_nearest_nature_block(self):
        return self.nearest_nature_block

    def get_nearest_centrality(self):
        return self.nearest_centrality