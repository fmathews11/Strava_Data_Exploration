import numpy as np
from typing import Iterable, Generator


def _remove_None_objects_and_coerce_nan_values_to_zero(input_array: np.ndarray) -> np.ndarray:
    """Removes None values and coerces all np.NaN values to zero."""
    filtered_array = np.array([x for x in input_array if x is not None], dtype=np.float64)
    # Coerce np.NaN to zero
    return np.nan_to_num(filtered_array)


def _generate_sliding_window_segments_from_an_array(input_array: Iterable,
                                                    window_size: int = 30) -> Generator:
    """Creates a Python generator to yield sliding window segments from an array."""
    array = np.array(input_array, dtype=np.float64)
    array = _remove_None_objects_and_coerce_nan_values_to_zero(array)

    # Fail fast
    if len(array) < window_size:
        return

    # Use NumPy's strides to create sliding windows without explicit loops
    shape = (len(array) - window_size + 1, window_size)
    strides = array.strides * 2
    sliding_windows = np.lib.stride_tricks.as_strided(array, shape=shape, strides=strides)

    for window in sliding_windows:
        yield window


def create_moving_average_array(input_array: Iterable,
                                window_size: int = 30) -> np.ndarray:
    """Creates a moving average from an array of size `window_size`."""
    array = np.array(input_array, dtype=np.float64)
    array = _remove_None_objects_and_coerce_nan_values_to_zero(array)

    if len(array) < window_size:
        return np.array([])

    kernel = np.ones(window_size) / window_size
    return np.convolve(array, kernel, mode='valid')
