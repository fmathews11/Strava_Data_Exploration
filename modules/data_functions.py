from typing import Iterable, Generator
import numpy as np


def generate_sliding_window_segments_from_an_array(input_array: Iterable,
                                                   window_size: int = 30) -> Generator:
    """Creates a Python generator to yield sliding window segments from an array"""
    array = np.array(input_array)
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

    for segment in generate_sliding_window_segments_from_an_array(input_array, window_size):
        output_append(np.sum(segment) / window_size)

    return np.array(output_array)


def convert_power_array_to_normalized_power_value(input_array: Iterable,
                                                  window_size: int = 30) -> int:
    """
    Returns a normalized power value from an array of data from a power meter.
    The default value for window size is 30, which is the widely accepted value
    """
    power_averages = create_moving_average_array(input_array=input_array, window_size=window_size)
    return round(np.mean(power_averages ** 4) ** 0.25)
