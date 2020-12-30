from unittest import TestCase

from isobenefit_cities.simulation import run_isobenefit_simulation


class TestSimulation(TestCase):
    def test_simulation_1(self):
        size_x=100
        size_y=100
        n_steps=50
        output_path_prefix='tmp'
        build_probability=0.5
        neighboring_centrality_probability=1
        isolated_centrality_probability=0.1
        T_star=5
        random_seed=0
        input_filepath=None
        initialization_mode='list'
        max_population=250000
        max_ab_km2=10000
        urbanism_model='isobenefit'
        prob_distribution=(0.7,0.3,0)
        density_factors=(1,0.1,0.01)
        run_isobenefit_simulation(size_x, size_y, n_steps, output_path_prefix, build_probability,
                                  neighboring_centrality_probability, isolated_centrality_probability, T_star,
                                  random_seed,
                                  input_filepath, initialization_mode, max_population, max_ab_km2, urbanism_model,
                                  prob_distribution, density_factors)