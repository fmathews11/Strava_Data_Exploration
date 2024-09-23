from datetime import datetime, timedelta
from typing import Union
import numpy as np
import pandas as pd
from modules.data_functions import create_ride_summary_dataframe

# Alpha values for CTL and ATL (acute and chronic training loads)
alpha_value_for_ctl = 2 / (42 + 1)
alpha_value_for_atl = 2 / (7 + 1)


def _calculate_ewma(input_array: Union[list, np.ndarray],
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
    output_array = [0] * len(input_array)
    # Set the first value of S to the first value of the input array
    output_array[0] = input_array[0]

    for i in range(1, len(input_array)):
        output_array[i] = alpha * input_array[i] + (1 - alpha) * output_array[i - 1]

    return np.array(output_array)


def get_daily_tss_score_array() -> np.ndarray:
    """This function computes the daily TSS (training stress score) for the last 43 days.
    Days with no training are filled in with a value of zero.

    Each value in the returned array represents the daily TSS for that day. Value zero represents today minus 43
    days, and value 43 represents today.  Any days with no training receive a value of zero.
    """
    # Get today, subtract 43 days.  Only 42 will be shown, but we need 43 days back to calculate the TSB for day 1
    cutoff_date = datetime.today() - timedelta(days=43)
    summary_df = create_ride_summary_dataframe()
    target_df = summary_df.loc[summary_df.start_date >= str(cutoff_date)][['start_date', 'tss']].set_index(
        'start_date').copy()
    target_df.index = pd.DatetimeIndex(target_df.index)
    target_df.index = pd.DatetimeIndex(target_df.index.strftime('%m/%d/%Y'))
    target_df = target_df.groupby('start_date').tss.sum().copy()
    start_date, end_date = target_df.index.min(), datetime.today()
    date_range_to_apply = pd.date_range(start_date, end_date)
    target_df = target_df.reindex(date_range_to_apply, fill_value=0).reset_index().copy()
    return target_df.tss.to_numpy()


def calculate_ctl_and_atl_arrays() -> tuple[np.ndarray, np.ndarray]:
    """
    Returns a tuple of two values.
    The first value represents the CTL array.
    The second value represents the ATL array
    """
    tss_array = get_daily_tss_score_array()
    ctl = _calculate_ewma(tss_array, alpha_value_for_ctl)
    atl = _calculate_ewma(tss_array, alpha_value_for_atl)
    return ctl, atl
