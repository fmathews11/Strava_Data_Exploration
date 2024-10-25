import streamlit as st
from modules.plotting import plot_tsb_ctl_atl

# Streamlit page
st.title("Training Stress Balance")
fig = plot_tsb_ctl_atl()
st.plotly_chart(fig, use_container_width=False)