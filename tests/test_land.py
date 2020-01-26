from unittest import TestCase

import numpy as np

from isobenefit_cities.land_map import Land, MapBlock


class TestLand(TestCase):
    @staticmethod
    def get_land_array():
        land = Land(size_x=10, size_y=10)
        land.set_centralities(centralities=[MapBlock(5, 5)])
        for x in range(3, 8):
            for y in range(3, 8):
                land.map[x][y].is_built = True
        return land

    def test_get_map_as_array(self):
        land = self.get_land_array()
        land_array = land.get_map_as_array()

        expected_land_array = np.ones(shape=(10, 10))
        expected_land_array[3:8,3:8] = 0
        np.testing.assert_array_equal(land_array, expected_land_array)
