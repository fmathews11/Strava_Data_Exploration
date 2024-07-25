from typing import Iterable, Generator
import numpy as np


def _generate_sliding_window_segments_from_an_array(input_array: Iterable,
                                                    window_size: int = 30) -> Generator:
    """Creates a Python generator to yield sliding window segments from an array"""
    array = np.array(input_array)
    # Remove None/np.NaN values
    array = array[(array != np.array(None)) & (array != np.nan)]
    left_pointer, right_pointer = 0, window_size
    while right_pointer <= len(array) + 1:
        yield array[left_pointer:right_pointer]
        right_pointer += 1
        left_pointer += 1


def create_moving_average_array(input_array: Iterable,
                                window_size: int = 30) -> np.ndarray:
    """Creates a moving average from an array of size `window_size`"""
    output_array = []
    output_append = output_array.append

    for segment in _generate_sliding_window_segments_from_an_array(input_array, window_size):
        output_append(np.sum(segment) / window_size)

    return np.array(output_array)
