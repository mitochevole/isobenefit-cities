import numpy as np


def get_circular_coords(radius, center_x, center_y, n_amenities):
    [(center_x + int(radius * np.sin(2 * t * np.pi)), center_y + int(radius * np.cos(2 * t * np.pi))) for t in np.linspace(0, 1, n_amenities)]

def get_random_coordinates(size_x,size_y, n_amenities, seed=42):
    np.random.seed(seed)
    return [(int(size_x*np.random.random()),int(size_y*np.random.random())) for _ in range(n_amenities)]

def get_central_coord(size_x,size_y):
    return [(int(size_x/2), int(size_y/2))]