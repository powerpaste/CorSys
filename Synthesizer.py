#
#   @file : Synthesizer.py
#   @date : 18 October 2022
#   @authors : Orel Adivi and Daniel Noor
#
import ast
from functools import partial
from pathlib import Path

from src.io.InputOutputPairReader import InputOutputPairReader
from src.io.SearchSpaceReader import SearchSpaceReader
from src.io.MetricReader import MetricReader

from src.synthesizer.BestEffortProgramGenerator import BestEffortProgramGenerator


def synthesize(input_output_file: str, search_space_file: str,
               metric: str = 'DefaultMetric', metric_parameter: str = '',
               tactic: str = 'match', tactic_parameter: str = '0',
               max_height: int = 2, statistics: bool = False):
    """
    Run the synthesizer based on the given parameters.

    :param input_output_file: the root for the input-output file
    :param search_space_file: the root for the search space file
    :param metric: the metric for the synthesizer (default = 'DefaultMetric')
    :param metric_parameter: the parameter for the metric
    :param tactic: the tactic for the synthesizer (default = 'height')
    :param tactic_parameter: the parameter for the tactic
    :param max_height: the max height for the synthesizer to search (default = 2)
    :param statistics: whether to present statistics
    :return: None
    """
    input_output_file = Path(input_output_file)
    search_space_file = Path(search_space_file)
    
    input_output_pairs = InputOutputPairReader.readCSV(input_output_file)
    search_space = SearchSpaceReader.readTXT(search_space_file)
    metric = MetricReader.parseMetric(metric, metric_parameter)
    generator = BestEffortProgramGenerator(search_space, max_height)

    if tactic == 'match':
        generation_function = partial(generator.findBestEffortMatchProgram,
                                      error_sum=eval(tactic_parameter))
    elif tactic == 'accuracy':
        generation_function = partial(generator.findBestEffortAccuracyProgram,
                                      error_rate=eval(tactic_parameter))
    elif tactic == 'height':
        generation_function = partial(generator.findBestEffortByHeightProgram)
    elif tactic == 'top':
        generation_function = partial(generator.findBestEffortPrograms,
                                      programs=eval(tactic_parameter))
    elif tactic == 'best_by_height':
        generation_function = partial(generator.findBestEffortByHeightPrograms)
    elif tactic == 'penalized_height':
        generation_function = partial(generator.findBestEffortPrioritizingHeightProgram,
                                      penalty=eval(tactic_parameter))
    elif tactic == 'interrupt':
        generation_function = partial(generator.findBestEffortUntilInterruptProgram)
    else:
        assert False

    inputs = input_output_pairs.inputs
    outputs = input_output_pairs.outputs
    result = generation_function(inputs, outputs, metric=metric)
    if not isinstance(result, list):
        result = [result]
    
    programs = []
    
    for program in result:
        if program is None:
            print('No valid program was found.')
        else:
            programs.append(ast.unparse(program.node))

    if statistics:
        print(f'The synthesizer searched {generator.program_counter} programs '
                        f'up to height #{generator.current_height}.')
    
    return programs
