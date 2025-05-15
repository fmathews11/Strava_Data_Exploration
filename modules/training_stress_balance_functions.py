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


def get_daily_tss_score_dataframe() -> pd.DataFrame:
    """
        Returns a DataFrame containing the daily Training Stress Score (TSS) for the past 42 days plus the current
        day for a total of 43 days.

        Values dates with no training are filled in with a value of zero.

        Returns:
            pd.DataFrame: A DataFrame with columns 'date' and daily TSS score for the past 42 days.
    """
    summary_df = create_ride_summary_dataframe()

    filtered_df = summary_df[['start_date', 'tss']].set_index('start_date')
    filtered_df.index = pd.to_datetime(filtered_df.index)
    filtered_df = filtered_df.groupby(filtered_df.index.date).tss.sum()
    date_range = pd.date_range(filtered_df.index.min(), datetime.today())
    return filtered_df.reindex(date_range, fill_value=0).rename_axis('date').reset_index()


def get_daily_tss_score_array() -> np.ndarray:
    """This function computes the daily TSS (training stress score) for the last 43 days.
    Days with no training are filled in with a value of zero.
    """
    return get_daily_tss_score_dataframe().tss.to_numpy()


def calculate_ctl_and_atl_arrays(tss_values):
    """
    Calculates the Chronic Training Load (CTL) and Acute Training Load (ATL) arrays.

    Uses daily Training Stress Scores (TSS) to calculate Exponentially Weighted Moving Averages (EWMA)
    for CTL and ATL using respective alpha (smoothing) constants.

    The smoothing factors are 2 / (42 + 1) for Chronic Trailing Load (CTL) and
    2 / (7 + 1) for Acute Training Load (ATL).
    These were the values provided by Allen Hunter in his research.

    Args:
        tss_values (list of float): A list containing TSS values for each day.

    Returns:
        tuple: Two lists containing ATL and CTL values for each day, respectively.
    """
    # Start with TSS on day 1
    atl_values, ctl_values = [tss_values[0]], [tss_values[0]]

    # Iterate through the array once and calculate ATL and CTL as we go
    for i in range(1, len(tss_values)):
        # Calculate ATL and CTL for the day based on the previous day
        atl_today = tss_values[i] * ALPHA_ATL + (1 - ALPHA_ATL) * atl_values[-1]
        ctl_today = tss_values[i] * ALPHA_CTL + (1 - ALPHA_CTL) * ctl_values[-1]
        atl_values.append(atl_today)
        ctl_values.append(ctl_today)

    return ctl_values, atl_values


def get_ctl_and_atl_dataframe() -> pd.DataFrame:
    """
    Fetches and processes a DataFrame containing daily TSS (Training Stress Score) values.

    The function performs the following steps:
     - 1. Retrieves a DataFrame containing daily TSS scores.
     - 2. Computes the CTL (Chronic Training Load) and ATL (Acute Training Load) arrays from the TSS values.
     - 3. Adds the computed CTL and ATL data as new columns to the DataFrame.
     - 4. Sorts the DataFrame by the 'date' column in descending order.

    Returns:
        pd.DataFrame: A DataFrame containing the original TSS scores along with the computed CTL and ATL values, sorted by date in descending order.
    """
    tss_df = get_daily_tss_score_dataframe()
    tss_df['ctl'],tss_df['atl'] = calculate_ctl_and_atl_arrays(tss_df.tss.to_numpy())
    return tss_df.sort_values('date',ascending=False)
