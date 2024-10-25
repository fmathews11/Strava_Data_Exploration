import streamlit as st
from modules.data_functions import create_ride_summary_dataframe

# Streamlit page
st.title("Ride History")
st.header("Ride Summary")
df = create_ride_summary_dataframe()
st.dataframe(df)
