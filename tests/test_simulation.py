import os, shutil
from unittest import TestCase

import numpy as np

from isobenefit_cities.image_io import import_2Darray_from_image
from isobenefit_cities.simulation import run_isobenefit_simulation


class TestSimulation(TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        folder = "simulations/tmp/"
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

    def test_simulation_isobenefit(self):
        size_x = 100
        size_y = 100
        n_steps = 50
        output_path_prefix = 'tmp'
        build_probability = 0.5
        neighboring_centrality_probability = 1
        isolated_centrality_probability = 0.1
        T_star = 5
        random_seed = 0
        input_filepath = None
        initialization_mode = 'list'
        max_population = 250000
        max_ab_km2 = 10000
        urbanism_model = 'isobenefit'
        prob_distribution = (0.7, 0.3, 0)
        density_factors = (1, 0.1, 0.01)
        run_isobenefit_simulation(size_x, size_y, n_steps, output_path_prefix, build_probability,
                                  neighboring_centrality_probability, isolated_centrality_probability, T_star,
                                  random_seed,
                                  input_filepath, initialization_mode, max_population, max_ab_km2, urbanism_model,
                                  prob_distribution, density_factors)
        results = np.loadtxt("simulations/tmp/current_counts.csv", skiprows=1, delimiter=',')

        last_iteration = results[-1, 0]
        final_population = results[-1, 6]
        self.assertEqual(40, last_iteration)
        self.assertEqual(263840, final_population)

        result_image = import_2Darray_from_image(f"simulations/tmp/{int(last_iteration):05d}.png")
        test_image_path = 'fixtures/test_simulation_final_map.png'
        test_image = import_2Darray_from_image(test_image_path)
        np.testing.assert_equal(test_image, result_image)

        final_min_dist = np.loadtxt("simulations/tmp/minimal_distances_map.csv", skiprows=1, delimiter=',')
        test_final_min_dist = np.loadtxt("fixtures/test_minimal_distances_map.csv", skiprows=1, delimiter=',')
        np.testing.assert_equal(test_final_min_dist, final_min_dist)
