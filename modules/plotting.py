import json
import plotly.graph_objects as go
from datetime import datetime, timedelta
from modules.objects.RideHub import RideHub
from modules.training_stress_balance_functions import calculate_ctl_and_atl_arrays
import matplotlib.pyplot as plt
import seaborn as sns


with open('data/saved_strava_rides.json','r') as f:
    ride_hub = RideHub(*json.load(f))

# Global layout parameters
LAYOUT_KWARGS = {
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


def plot_tsb_ctl_atl() -> None:
    """Produces a plot showing CTL, ATL, and TSB over the last 42 days"""
    date_array = list(reversed([(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(42)]))
    ctl,atl = calculate_ctl_and_atl_arrays()
    tsb = [ctl[idx - 1] - atl[idx - 1] for idx in range(1, len(ctl))]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=date_array,
                             y=ctl[1:],
                             mode='lines',
                             name='CTL',
                             line={'width': 4, 'color': 'blue'},
                             hovertemplate='CTL: %{y}<br>Date: %{x}<extra></extra>'))
    fig.add_trace(go.Scatter(x=date_array,
                             y=atl[1:],
                             mode='lines',
                             name='ATL',
                             line={'width': 4, 'color': 'red'},
                             hovertemplate='ATL: %{y}<br>Date: %{x}<extra></extra>'))
    fig.add_trace(go.Scatter(x=date_array,
                             y=tsb,
                             mode='lines',
                             name='TSB',
                             line={'width': 4, 'color': 'limegreen'},
                             hovertemplate='TSB: %{y}<br>Date: %{x}<extra></extra>'))

    # Update the global kwargs with the figure-specific title
    title_params = {
        "title":
            {"text": f"Training Stress Balance/Load | CTL:{round(ctl[-1])}  ATL:{round(atl[-1])}  TSB:{round(tsb[-1])}",
             "x": 0.5,
             "font": {
                 'size': 24,
                 'color': 'black'}
             }
    }

    figure_kwargs = LAYOUT_KWARGS.copy()
    figure_kwargs.update(title_params)
    fig.update_layout(figure_kwargs)

    fig.show()
    return


def create_individual_ride_power_curve_plot(ride_id: int) -> None:

    """
    Produces a simple plot showing the power curve for an individual ride.
    The 20-minute average power is highlighted via a vertical yellow line
    """
    power_curve = ride_hub[ride_id].metrics_dict['power_curve']
    plt.figure(figsize=(16, 10))
    sns.lineplot(x=[i for i in range(len(power_curve))],
                 y=power_curve)
    xmin, xmax, ymin, ymax = plt.axis()
    annotation_value = power_curve[1200]
    plt.vlines(x=1200, ymax=ymax, ymin=ymin, colors='yellow', linestyles="--")
    plt.annotate(text=f"20-minute average: {round(annotation_value)} watts", xy=(1400, annotation_value + 30), size=12)
    plt.show()