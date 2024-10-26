import streamlit as st
from modules.plotting import plot_tsb_ctl_atl

# Streamlit page
st.title("Training Stress Balance")

# Fetch the figure and update its layout
fig = plot_tsb_ctl_atl()
fig.update_layout(
    autosize=False,
    width=800,  # Adjust the width as needed
    height=600,  # Adjust the height as needed
)

# Centers the chart using CSS
st.markdown(
    """
    <style>
    .centered {
        display: flex;
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Centering the chart container and using the full width
st.markdown('<div class="centered">', unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=False)  # Set use_container_width to False since we define size
st.markdown('</div>', unsafe_allow_html=True)
