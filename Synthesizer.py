#
#   @file : Synthesizer.py
#   @date : 18 October 2022
#   @authors : Orel Adivi and Daniel Noor
#
import ast
import pathlib
import argparse
from functools import partial

from src.io.InputOutputPairReader import InputOutputPairReader
from src.io.SearchSpaceReader import SearchSpaceReader

from src.objects.Metric import Metric
from src.metrics.DefaultMetric import DefaultMetric
from src.metrics.NormalMetric import NormalMetric
from src.metrics.CalculationMetric import CalculationMetric
from src.metrics.VectorMetric import VectorMetric
from src.metrics.HammingMetric import HammingMetric
from src.metrics.LevenshteinMetric import LevenshteinMetric
from src.metrics.PermutationMetric import PermutationMetric
from src.metrics.KeyboardMetric import KeyboardMetric
from src.metrics.HomophoneMetric import HomophoneMetric
# from src.metrics.CombinedMetric import CombinedMetric
# from src.metrics.WeightedMetric import WeightedMetric

from src.synthesizer.BestEffortProgramGenerator import BestEffortProgramGenerator


def get_metric(metric_name: str, metric_parameter: str) -> Metric:
    """
    Convert metric name and parameter from string form to a metric object.

    :param metric_name: Metric name is string form
    :param metric_parameter: Metric parameter (if there is one) in string form
    :return: A metric object
    """
    metrics = {
        'DefaultMetric': lambda: DefaultMetric(),
        'NormalMetric': lambda: NormalMetric(),     # todo support change std
        'CalculationMetric': lambda: CalculationMetric(),
        'VectorMetric': lambda: VectorMetric(dist_func=metric_parameter),
        'HammingMetric': lambda: HammingMetric(),
        'LevenshteinMetric': lambda: LevenshteinMetric(solve_recursively=eval(metric_parameter)),
        'PermutationMetric': lambda: PermutationMetric(),
        'KeyboardMetric': lambda: KeyboardMetric(),
        'HomophoneMetric': lambda: HomophoneMetric()
        # 'CombinedMetric': lambda: CombinedMetric()
        # 'WeightedMetric': lambda: WeightedMetric()
    }
    return metrics[metric_name]()


def main() -> None:
    """
    Parse command line arguments and run the synthesizer based on the given parameters.

    :return: None
    """
    cl_parser = argparse.ArgumentParser(description='CorSys - Synthesizing best-effort python expressions while '
                                                    'weighting the chance for mistakes in given user outputs.',
                                        epilog='For help with the synthesizer please read SUPPORT.md .',
                                        allow_abbrev=False)
    cl_parser.add_argument('-io', '--input-output', action='store', type=pathlib.Path, required=True,
                           help='the root for the input-output file', dest='input_output_file')
    cl_parser.add_argument('-s', '--search-space', action='store', type=pathlib.Path, required=True,
                           help='the root for the search space file', dest='search_space_file')
    cl_parser.add_argument('-m', '--metric', action='store', type=str, default='DefaultMetric',
                           choices=['DefaultMetric', 'NormalMetric', 'CalculationMetric', 'VectorMetric',
                                    'HammingMetric', 'LevenshteinMetric', 'PermutationMetric', 'KeyboardMetric',
                                    'HomophoneMetric'],
                           # 'CombinedMetric', 'WeightedMetric'
                           help='the metric for the synthesizer (default = \'DefaultMetric\')', dest='metric')
    cl_parser.add_argument('-mp', '--metric-parameter', action='store', type=str, default='',
                           help='the parameter for the metric', dest='metric_parameter')
    cl_parser.add_argument('-t', '--tactic', action='store', type=str, default='match',
                           choices=['match', 'accuracy', 'height', 'top', 'best_by_height', 'penalized_height',
                                    'interrupt'],
                           help='the tactic for the synthesizer (default = \'height\')', dest='tactic')
    cl_parser.add_argument('-tp', '--tactic-parameter', action='store', type=str, default='0',
                           help='the parameter for the tactic', dest='tactic_parameter')
    cl_parser.add_argument('-mh', '--max-height', action='store', type=int, default=2,
                           help='the max height for the synthesizer to search (default = 2)', dest='max_height')
    cl_parser.add_argument('--statistics', action='store_const', const=True, default=False,
                           help='whether to present statistics', dest='statistics')
    arguments = cl_parser.parse_args()

    input_output_pairs = InputOutputPairReader.readCSV(arguments.input_output_file)
    inputs = input_output_pairs.inputs
    outputs = input_output_pairs.outputs
    search_space = SearchSpaceReader.readCSV(arguments.search_space_file)
    metric = get_metric(arguments.metric, arguments.metric_parameter)
    generator = BestEffortProgramGenerator(search_space, arguments.max_height)

    if arguments.tactic == 'match':
        generation_function = partial(generator.findBestEffortMatchProgram,
                                      error_sum=eval(arguments.tactic_parameter))
    elif arguments.tactic == 'accuracy':
        generation_function = partial(generator.findBestEffortAccuracyProgram,
                                      error_rate=eval(arguments.tactic_parameter))
    elif arguments.tactic == 'height':
        generation_function = partial(generator.findBestEffortByHeightProgram)
    elif arguments.tactic == 'top':
        generation_function = partial(generator.findBestEffortPrograms,
                                      programs=eval(arguments.tactic_parameter))
    elif arguments.tactic == 'best_by_height':
        generation_function = partial(generator.findBestEffortByHeightPrograms)
    elif arguments.tactic == 'penalized_height':
        generation_function = partial(generator.findBestEffortPrioritizingHeightProgram,
                                      penalty=eval(arguments.tactic_parameter))
    elif arguments.tactic == 'interrupt':
        generation_function = partial(generator.findBestEffortUntilInterruptProgram)
    else:
        return

    result = generation_function(inputs, outputs, metric=metric)
    if not isinstance(result, list):
        result = [result]
    for program in result:
        if program is None:
            print('No valid program was found.')
        else:
            print(ast.unparse(program.node))

    if arguments.statistics:
        print('')
        print(f'The synthesizer searched {generator.program_counter} programs '
              f'up to height #{generator.current_height}.')


if __name__ == '__main__':
    """
    If this file is run as the main file, it calls main function.
    """
    main()
