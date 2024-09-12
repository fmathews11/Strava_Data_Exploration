from typing import Union
import numpy as np

alpha_value_for_ctl = 2/(42+1)
alpha_value_for_atl = 2/(7+1)

def calculate_ewma(daily_tss_array: Union[list, np.ndarray],
                   alpha: float) -> np.ndarray:
    """
    Calculates an exponentially weighted moving average (EWMA).

    This utilizes the method designed by Allen Hunter.

    Parameters:
    ------------
    daily_tss_array: A list of values (the original series).
    alpha: The smoothing factor (a float between 0 and 1).

    Returns:
    ---------
    A NumPy array representing the EWMA values

    """

    # Instantiate a list of zeroes
    output_array = [0] * len(daily_tss_array)
    # Set the first value of S to the first value of X
    output_array[0] = daily_tss_array[0]

    for day in range(1, len(daily_tss_array)):
        output_array[day] = alpha * daily_tss_array[day] + (1 - alpha) * output_array[day - 1]

    return np.array(output_array)