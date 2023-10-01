import numpy as np
import pandas as pd
import streamlit as st

st.title("Stremlit widgets")

st.write("Dataframe")

df = pd.DataFrame({ "x": np.random.rand(10), "y": np.random.rand(10)})
st.dataframe(df)

st.write("Slider")

x = st.slider("x", min_value=1, max_value=100)
st.write(f"x^2 is {x ** 2}")

st.write("Checkbox")

if st.checkbox("Show Text"):
  st.write("This is the text that can be toggled by the checkbox")

st.write("Selectbox")
st.selectbox("Choose a number:", options=np.random.rand(10))
