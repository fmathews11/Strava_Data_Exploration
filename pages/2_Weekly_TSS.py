import streamlit as st
from modules.plotting import plot_weekly_tss

# Streamlit page
st.title("Weekly TSS")
fig2 = plot_weekly_tss()
st.plotly_chart(fig2, use_container_width=False)
