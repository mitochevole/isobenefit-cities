import argparse

from isobenefit_cities import logger
from isobenefit_cities.simulation import run_isobenefit_simulation

# import yaml

LOGGER = logger.get_logger()


def create_arg_parser():
    parser = argparse.ArgumentParser(
        description="""Start simulation.
        """,
        epilog="Example: ...",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('--n-steps',
                        required=True,
                        type=int,
                        help="number of steps for the simulation")

    parser.add_argument('--size-x',
                        required=True,
                        type=int,
                        help="width of the land map")

    parser.add_argument('--size-y',
                        required=True,
                        type=int,
                        help="height of the land map")

    parser.add_argument('--output-path',
                        required=False,
                        type=str,
                        help="output path to store simulation results")

    parser.add_argument('--build-probability',
                        required=False,
                        type=float,
                        default=0.5,
                        help="probability of building a new block")

    parser.add_argument('--neighboring-centrality-probability',
                        required=False,
                        type=float,
                        default=5e-3,
                        help="probability of building a new centrality next to a constructed area")

    parser.add_argument('--isolated-centrality-probability',
                        required=False,
                        type=float,
                        default=1e-1,
                        help="probability of building a new centrality in a natural area")

    parser.add_argument('--T',
                        required=False,
                        type=int,
                        default=10,
                        help="standard maximum distance from centralities and nature")

    parser.add_argument('--random-seed',
                        required=False,
                        type=int,
                        default=42,
                        help="for reproducibility set a specific random seed")

    parser.add_argument('--input-filepath',
                        required=False,
                        type=str,
                        help="image filepath for initial configuration")

    parser.add_argument('--initialization-mode',
                        required=True,
                        type=str,
                        help="initial configuration can be set via an input image or via a list of initial centralities")

    parser.add_argument('--max-population',
                        required=False,
                        type=int,
                        default=1000000,
                        help="maximum population reachable by the simulation")

    parser.add_argument('--max-ab-km2',
                        required=False,
                        type=int,
                        default=10000,
                        help="maximum population density (ab/km^2) in the simulation")

    parser.add_argument('--urbanism-model',
                        required=False,
                        type=str,
                        default='isobenefit',
                        help="City urbanism model. Choose one of 'isobenefit' and 'standard'")

    return parser


if __name__ == "__main__":
    parser = create_arg_parser()
    args = parser.parse_args()
    size_x = args.size_x
    size_y = args.size_y
    n_steps = args.n_steps
    output_path = args.output_path
    build_probability = args.build_probability
    T = args.T
    random_seed = args.random_seed
    input_file_path = args.input_filepath
    initialization_mode = args.initialization_mode
    neighboring_centrality_probability = args.neighboring_centrality_probability
    isolated_centrality_probability = args.isolated_centrality_probability
    max_population = args.max_population
    max_ab_km2 = args.max_ab_km2
    urbanism_model = args.urbanism_model
    LOGGER.info(args)
    run_isobenefit_simulation(size_x=size_x, size_y=size_y, n_steps=n_steps, output_path_prefix=output_path,
                              build_probability=build_probability,
                              neighboring_centrality_probability=neighboring_centrality_probability,
                              isolated_centrality_probability=isolated_centrality_probability, T_star=T,
                              random_seed=random_seed, input_filepath=input_file_path,
                              initialization_mode=initialization_mode, max_population=max_population,
                              max_ab_km2=max_ab_km2, urbanism_model=urbanism_model)
