#
#   @file : InputOutputPairReader.py
#   @date : 18 October 2022
#   @authors : Orel Adivi and Daniel Noor
#
import csv
from pathlib import Path
from typing import Iterator

from src.objects.InputOutputPairs import InputOutputPairs


class InputOutputPairReader(object):
    """
    A class which allows conversion of input-output examples from a CSV file to an InputOutputPairs object.

    Public method:
        - readCSV - Convert a csv of input-output examples to an InputOutputPairs object.
    """

    @staticmethod
    def readCSV(root: Path) -> InputOutputPairs:
        """
        Read a csv of input-output examples and convert it to an InputOutputPairs object.

        :param root: Path of the csv file to read.
        :return: InputOutputPairs object containing the information from the CSV file.
        """
        with root.open() as file:
            file_content = list(csv.reader(file))
        variable_names = file_content[0]
        result = InputOutputPairs()
        for pair in file_content[1:]:
            inputs = {variable_names[i]: eval(value) for i, value in enumerate(pair[:-1])}
            output = eval(pair[-1])
            result.addPair(inputs=inputs, output=output)
        return result

    @staticmethod
    def readSimpleList(inputs_output_simple_list: Iterator[Iterator], variable_names: Iterator[str]) -> InputOutputPairs:
        """
        Read input-output examples in lists and convert it to an InputOutputPairs object.
        """
        result = InputOutputPairs()
        for pair in inputs_output_simple_list:
            inputs = {variable_names[i]: value for i, value in enumerate(pair[:-1])}
            output = pair[-1]
            result.addPair(inputs=inputs, output=output)
        return result
