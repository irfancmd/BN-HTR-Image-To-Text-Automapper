import streamlit as st
from PIL import Image

for line_id in range(1, 13):
  line_image_path = f"BN-HTR_Dataset/Segmentation_Images/Words/1/1_1/1_1_{line_id}.jpg"

  image = Image.open(line_image_path)

  st.image(image, caption=f"1_1_{line_id}")
