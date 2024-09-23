import plotly.graph_objects as go
from datetime import datetime, timedelta
from modules.data_functions import get_daily_tss_score_array
from modules.training_stress_balance_functions import calculate_ewma

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


def plot_tsb_ctl_atl():
    """Produces a plot showing CTL, ATL, and TSB over the last 42 days"""
    date_array = list(reversed([(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(42)]))
    tss_array = get_daily_tss_score_array()
    ctl = calculate_ewma(tss_array, alpha=2 / 43)
    atl = calculate_ewma(tss_array, alpha=2 / 8)
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
