from functools import partial
from unittest import TestCase
from scipy.ndimage import measurements as measure
import numpy as np

from isobenefit_cities.land_map import Land, MapBlock, is_nature_wide_along_axis


class TestLand(TestCase):
    @staticmethod
    def get_land():
        land = Land(size_x=20, size_y=15)
        land.set_centralities(centralities=[MapBlock(5, 5)])
        for x in range(3, 8):
            for y in range(3, 8):
                land.map[x][y].is_built = True
                land.map[x][y].is_nature = False
        return land

    @staticmethod
    def get_expected_array():
        A = np.ones(shape=(20, 10))
        A[4:9, 4:9] = 0
        A[12:17, 4:9] = 0
        return A

    def test_check_consistency(self):
        ok_land = self.get_land()
        ok_land.check_consistency()

        ok_land.map[3][3].is_nature = True
        self.assertRaises(AssertionError, ok_land.check_consistency)

    def test_get_map_as_array(self):
        land = self.get_land()
        land_array = land.get_map_as_array()
        expected_land_array = np.ones(shape=(20, 15))
        expected_land_array[3:8, 3:8] = 0
        np.testing.assert_array_equal(land_array, expected_land_array)

    def test_set_centralities(self):
        land = Land(size_x=20, size_y=10)
        self.assertFalse(land.map[5][5].is_built)
        self.assertFalse(land.map[5][5].is_centrality)
        self.assertTrue(land.map[5][5].is_nature)

        land.set_centralities(centralities=[MapBlock(5, 5)])
        self.assertTrue(land.map[5][5].is_built)
        self.assertTrue(land.map[5][5].is_centrality)
        self.assertFalse(land.map[5][5].is_nature)

    def test_is_any_neighbor_built(self):
        land = self.get_land()
        self.assertTrue(land.is_any_neighbor_built(6, 6))
        self.assertFalse(land.is_any_neighbor_built(9, 9))
        self.assertRaises(AssertionError, land.is_any_neighbor_built, x=3, y=3)

    def test_is_centrality_near(self):
        land = self.get_land()
        self.assertTrue(land.is_centrality_near(6,7))
        self.assertFalse(land.is_centrality_near(14, 7))
        self.assertRaises(AssertionError,land.is_centrality_near,x=4, y=4)

    def test_is_nature_wide_along_axis(self):
        land_array_1d = np.array([1,1,1,1,1,1,0,1,1,1,1,1,1,0,1,1,1,1,1,1])

        self.assertTrue(is_nature_wide_along_axis(land_array_1d, T_star=5))
        self.assertFalse(is_nature_wide_along_axis(land_array_1d, T_star=7))

    def test_nature_stays_extended(self):
        land = Land(20,20)
        for x in [5,14]:
            for y in [5,14]:
                land.map[x][y].is_built = True
                land.map[x][y].is_nature = False

        self.assertTrue(land.nature_stays_extended(6,14))
        self.assertFalse(land.nature_stays_extended(5, 10))

        for x in range(5,14):
            land.map[x][5].is_built = True
            land.map[x][5].is_nature = False

        self.assertTrue(land.nature_stays_extended(14, 6))
        self.assertFalse(land.nature_stays_extended(5, 10))


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

    def test_logger(self):
        from isobenefit_cities import logger
        LOGGER = logger.get_logger()
        LOGGER.info("test_logger")
        print(logger.BASE_DIR)
