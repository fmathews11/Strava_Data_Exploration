import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from modules.data_functions import create_ride_summary_dataframe
from modules.objects.RideHub import RideHub
from modules.training_stress_balance_functions import calculate_ctl_and_atl_arrays, get_ctl_and_atl_dataframe

# import matplotlib.pyplot as plt
# import seaborn as sns


with open('data/saved_strava_rides.json', 'r') as f:
    ride_hub = RideHub(*json.load(f))

# Global layout parameters
GLOBAL_LAYOUT_KWARGS = {
    "width": 1000,
    "height": 600,
    "paper_bgcolor": 'white',
    "plot_bgcolor": 'lightgray',
    "legend": {
        "font": {
            'color': 'black',
            'size': 14
        }
    },
    "xaxis": {
        "tickfont": {
            'color': 'black',
            'size': 12
        }
    },
    "yaxis": {
        "tickfont": {
            'color': 'black',
            'size': 12
        }
    }

}


def plot_tsb_ctl_atl():
    """Produces a plot showing CTL, ATL, and TSB over the last 42 days"""
    plot_df = get_ctl_and_atl_dataframe().head(43).sort_values('date', ascending=True)
    ctl, atl = plot_df.ctl.to_numpy(), plot_df.atl.to_numpy()
    tsb = [0]
    tsb.extend([ctl[idx - 1] - atl[idx - 1] for idx in range(1, len(ctl))])
    plot_df['tsb'] = tsb
    plot_df = plot_df.sort_values('date', ascending=False).head(42).reset_index(drop=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=plot_df.date.tolist(),
                             y=plot_df.ctl,
                             mode='lines',
                             name='CTL',
                             line={'width': 4, 'color': 'blue'},
                             hovertemplate='CTL: %{y}<br>Date: %{x}<extra></extra>'))
    fig.add_trace(go.Scatter(x=plot_df.date.tolist(),
                             y=plot_df.atl,
                             mode='lines',
                             name='ATL',
                             line={'width': 4, 'color': 'red'},
                             opacity=0.7,
                             hovertemplate='ATL: %{y}<br>Date: %{x}<extra></extra>'))
    fig.add_trace(go.Scatter(x=plot_df.date.tolist(),
                             y=plot_df.tsb,
                             mode='lines',
                             name='TSB',
                             line={'width': 4, 'color': 'limegreen'},
                             hovertemplate='TSB: %{y}<br>Date: %{x}<extra></extra>'))

    fig.add_shape(type="line",
                  x0=plot_df.date.tolist()[0], x1=plot_df.date.tolist()[-1], y0=0, y1=0,
                  line={'color': 'black', 'dash': 'dash', "width": 3})

    # Update the global kwargs with the figure-specific title
    title_params = {
        "title":
            {"text": f"Training Stress Balance/Load | "
                     f"CTL:{round(plot_df.ctl.tolist()[0])}  "
                     f"ATL:{round(plot_df.atl.tolist()[0])}  "
                     f"TSB:{round(plot_df.tsb.tolist()[0])}",
             "x": 0.5,
             "font": {
                 'size': 24,
                 'color': 'black'}
             }
    }

    figure_kwargs = GLOBAL_LAYOUT_KWARGS.copy()
    figure_kwargs.update(title_params)
    fig.update_layout(figure_kwargs)
    return fig


# def create_individual_ride_power_curve_plot(ride_id: int) -> None:
#
#     """
#     Produces a simple plot showing the power curve for an individual ride.
#     The 20-minute average power is highlighted via a vertical yellow line
#     """
#     power_curve = ride_hub[ride_id].metrics_dict['power_curve']
#     plt.figure(figsize=(16, 10))
#     sns.lineplot(x=[i for i in range(len(power_curve))],
#                  y=power_curve)
#     xmin, xmax, ymin, ymax = plt.axis()
#     annotation_value = power_curve[1200]
#     plt.vlines(x=1200, ymax=ymax, ymin=ymin, colors='yellow', linestyles="--")
#     plt.annotate(text=f"20-minute average: {round(annotation_value)} watts", xy=(1400, annotation_value + 30), size=12)
#     plt.show()

def plot_weekly_tss():
    """
    Generates a weekly Total Stress Score (TSS) plot.

    This function creates a bar chart representing the weekly Total Stress Score (TSS)
    by summarizing data from the ride summary dataframe. It also adds a smooth trend
    line to the plot, which is computed using a rolling mean over 3 weeks. The plot is
    prepared using Plotly's Graph Objects library and customized with layout parameters.

    Returns:
        fig (plotly.graph_objs._figure.Figure): A Plotly figure object containing the bar chart with a trend line.
    """
    temp_df = create_ride_summary_dataframe()
    temp_df['date_group'] = pd.to_datetime(temp_df.start_date) - pd.to_timedelta(7, unit='d')
    plot_df = temp_df.groupby([pd.Grouper(key='date_group', freq="W")]).tss.sum() \
        .reset_index().sort_values('date_group', ascending=False).copy()

    plot_df['tss_smooth'] = plot_df['tss'].rolling(window=3, center=True).mean()

    title_params = {
        "title":
            {"text": f"Weekly TSS - 2024",
             "x": 0.5,
             "font": {
                 'size': 24,
                 'color': 'black'}
             }
    }

    # Create the bar chart
    fig = go.Figure()

    # Add the bar trace for TSS values
    fig.add_trace(go.Bar(x=plot_df['date_group'], y=plot_df['tss'], name='Weekly TSS'))

    # Add the trend line (line plot over the bars)
    fig.add_trace(go.Scatter(x=plot_df['date_group'], y=plot_df['tss_smooth'], mode='lines', showlegend=False))
    figure_kwargs = GLOBAL_LAYOUT_KWARGS.copy()
    figure_kwargs.update(title_params)
    fig.update_layout(GLOBAL_LAYOUT_KWARGS)
    return fig
