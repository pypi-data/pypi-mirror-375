import streamlit as st
from my_clicker import my_clicker

st.title("My Streamlit React Component")

# Call the custom component
num_clicks = my_clicker(name="Sarvesh")

st.write(f"Button clicked {num_clicks} times")
