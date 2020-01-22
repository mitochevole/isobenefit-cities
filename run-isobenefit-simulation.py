import os
import time

import matplotlib.pyplot as plt
import numpy as np

from isobenefit_cities.land_map import Land
from isobenefit_cities.map_block import MapBlock
from simulation_config import AMENITIES_COORDINATES

def main(size_x, size_y, n_steps):
    t_zero = time.time()
    amenities_list = AMENITIES_COORDINATES
    land = initialize_land(size_x, size_y, amenities_list)
    canvas = np.zeros(shape=(size_x, size_y))
    update_map_snapshot(land, canvas)
    save_snapshot(canvas)
    for i in range(n_steps):
        start = time.time()
        land.update_map()
        print(f"step: {i}, duration: {time.time() - start} seconds")
        update_map_snapshot(land, canvas)
        save_snapshot(canvas)
    print(f"Simulation ended. Total duration: {time.time()-t_zero}")



def initialize_land(size_x, size_y, amenities_list):
    land = Land(size_x=size_x, size_y=size_y)
    amenities = [MapBlock(x,y) for (x,y) in amenities_list]
    land.set_centralities(amenities)
    return land

def update_map_snapshot(land, canvas):
    for row in land.map:
        for block in row:
            if block.is_built:
                canvas[block.x, block.y] = 1
            if block.is_centrality:
                canvas[block.x, block.y] = 2

def save_snapshot(canvas, output_path, step, format='png'):
    if format == 'png':
        plt.imshow(canvas)
        plt.axis('off')
        final_path = os.path.join(output_path,step+"_png")
        plt.savefig(final_path)



if __name__ == "__main__":
    main()
