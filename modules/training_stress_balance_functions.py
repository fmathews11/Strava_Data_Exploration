from datetime import datetime, timedelta
from typing import Union
import numpy as np
import pandas as pd
from modules.data_functions import create_ride_summary_dataframe

# Alpha values for CTL and ATL (acute and chronic training loads)
ALPHA_CTL = 2 / (42 + 1)
ALPHA_ATL = 2 / (7 + 1)


def calculate_ewma(array: Union[list, np.ndarray], alpha: float) -> np.ndarray:
    """
    Calculates an exponentially weighted moving average (EWMA).
    Parameters:
    -----------
    array: A list of values (the original series).
    alpha: The smoothing factor (a float between 0 and 1).

    Returns:
    --------
    A NumPy array representing the EWMA values.
    """
    output = np.zeros(len(array))
    output[0] = array[0]
    for i in range(1, len(array)):
        output[i] = alpha * array[i] + (1 - alpha) * output[i - 1]
    return np.array(output)


def get_daily_tss_score_array() -> np.ndarray:
    """This function computes the daily TSS (training stress score) for the last 43 days.
    Days with no training are filled in with a value of zero.
    """
    cutoff_date = datetime.today() - timedelta(days=43)
    summary_df = create_ride_summary_dataframe()
    filtered_df = summary_df.loc[summary_df.start_date >= str(cutoff_date)][['start_date', 'tss']].set_index(
        'start_date')
    filtered_df.index = pd.to_datetime(filtered_df.index)
    filtered_df = filtered_df.groupby(filtered_df.index.date).tss.sum()
    date_range = pd.date_range(filtered_df.index.min(), datetime.today())
    filled_df = filtered_df.reindex(date_range, fill_value=0).reset_index(drop=True)
    return filled_df.to_numpy()


def calculate_ctl_and_atl_arrays() -> tuple[np.ndarray, np.ndarray]:
    """
        Calculates the Chronic Training Load (CTL) and Acute Training Load (ATL) arrays.

        Uses daily Training Stress Scores (TSS) to calculate Exponentially Weighted Moving Averages (EWMA)
        for CTL and ATL using respective alpha (smoothing) constants.

        The smoothing factors are 2 / (42 + 1) for Chronic Trailing Load (CTL) and
        2 / (7 + 1) for Acute Training Load (ATL). These were the values provided by Allen Hunter in his
        research.

        Returns:
        ---------
        A tuple containing:
            - Chronic Training Load (CTL) values as a numpy array.
            - Acute Training Load (ATL) values as a numpy array.
    """
    tss_values = get_daily_tss_score_array()
    atl_values = calculate_ewma(tss_values, ALPHA_ATL)
    ctl_values = calculate_ewma(tss_values, ALPHA_CTL)
    return ctl_values, atl_values
