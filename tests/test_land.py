from unittest import TestCase

import numpy as np

from isobenefit_cities.land_map import Land, MapBlock


class TestLand(TestCase):
    @staticmethod
    def get_land():
        land = Land(size_x=20, size_y=10)
        land.set_centralities(centralities=[MapBlock(5, 5)])
        for x in range(3, 8):
            for y in range(3, 8):
                land.map[x][y].is_built = True
        return land

    @staticmethod
    def get_expected_array():
        A = np.ones(shape=(20, 10))
        A[4:9, 4:9] = 0
        A[12:17, 4:9] = 0
        return A

    def test_get_map_as_array(self):
        land = self.get_land()
        land_array = land.get_map_as_array()
        expected_land_array = np.ones(shape=(20, 10))
        expected_land_array[3:8, 3:8] = 0
        np.testing.assert_array_equal(land_array, expected_land_array)

    def test_initialize_map_from_image(self):
        land = Land(20, 10)
        test_image_path = 'fixtures/test_land_map.png'
        land.set_configuration_from_image(test_image_path)
        land.check_consistency()
        array_map = land.get_map_as_array()
        expected_array = self.get_expected_array()
        expected_centralities = [(6, 6), (14, 6)]
        np.testing.assert_array_equal(array_map, expected_array)
        assert land.map[0][0].is_built == False
        assert land.map[0][0].is_nature == True

        for x, y in expected_centralities:
            assert land.map[x][y].is_centrality == True

