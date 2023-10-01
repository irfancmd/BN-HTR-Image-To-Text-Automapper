import numpy as np
import pandas as pd
import streamlit as st

st.title("Layout Tutorial")

# Sidebar layout

# Adding widgets to the sidebar
st.sidebar.write("This is a sidebar text")

st.sidebar.selectbox("Choose a color: ", options=("Red", "Green", "Blue"))

# Layout columns
left_column, right_column = st.columns(2)

with left_column:
  click_counter = 0

  def handle_button_click():
    global click_counter

    click_counter += 1
    st.write("You clicked the button ", click_counter, " times")

  st.button("Click Me!", on_click= handle_button_click)

with right_column:
  st.radio("Favorite fruit:", options=("Apple", "Grape", "Peach"))
