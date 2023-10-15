import os
import glob
from PIL import Image
import pandas as pd
import streamlit as st
from natsort import natsorted
from xml.etree import ElementTree as ET
import cv2


def get_bounding_box_points(xml_path):
  xml_file = ET.parse(xml_path)

  rectangle_start_points = []
  rectangle_end_points = []

  for child in xml_file.getroot():
    if child.tag == "object":
      start_point = (int(child[4][0].text), int(child[4][1].text))
      end_point = (int(child[4][2].text), int(child[4][3].text))

      rectangle_start_points.append(start_point)
      rectangle_end_points.append(end_point)

  return rectangle_start_points, rectangle_end_points


PATH = "./BN-HTR_Dataset"
IMAGE_TO_EXCLUDE = [34, 60]

left_column, right_column = st.columns(2)

excel_path = f"{PATH}/Recognition_Ground_Truth_Texts"
line_path = f"{PATH}/Segmentation_Images/Lines"
word_path = f"{PATH}/Segmentation_Images/Words"

# Fetching articles
article_ids = natsorted([int(e) for e in os.listdir(line_path)])

if not st.session_state.get("current_article_id"):
  st.session_state["current_article_id"] = article_ids[0]

# Fetching images
image_paths = natsorted(glob.glob(f"{line_path}/{st.session_state['current_article_id']}/*.jpg"))

if not st.session_state.get("current_image_file_index"):
  st.session_state["current_image_file_index"] = 0

if not st.session_state.get("current_line_index"):
  st.session_state["current_line_index"] = 0

if not st.session_state.get("current_word_index"):
  st.session_state["current_word_index"] = 0

# Fetching line bounding box co-ordinates
line_rectangle_start_points, line_rectangle_end_points = get_bounding_box_points(f"{line_path}/{st.session_state['current_article_id']}/{st.session_state['current_article_id']}_{st.session_state['current_image_file_index'] + 1}.xml")

image = cv2.imread(image_paths[st.session_state["current_image_file_index"]])

# Drawing line bounding box
image = cv2.rectangle(image, line_rectangle_start_points[st.session_state["current_line_index"]], line_rectangle_end_points[st.session_state["current_line_index"]], (255, 0, 0), 5)

# ***** Left Column *****

left_column.header("Current Image")
left_column.subheader(f"Article: {st.session_state['current_article_id']} Image: {st.session_state['current_image_file_index'] + 1}")
# left_column.image(Image.open(image_paths[st.session_state["current_image_file_index"]]))
left_column.image(image)

def prev_image():
  if st.session_state["current_image_file_index"] > 0:
    st.session_state["current_image_file_index"] -= 1
  else:
    if st.session_state["current_article_id"] > article_ids[0]:
      st.session_state["current_article_id"] -= 1
      st.session_state["current_image_file_index"] = len(glob.glob(f"{line_path}/{st.session_state['current_article_id']}/*.jpg")) - 1


def next_image():
  if st.session_state["current_image_file_index"] < len(image_paths) - 1:
    st.session_state["current_image_file_index"] += 1
  else:
    if st.session_state["current_article_id"] < len(article_ids) - 1:
      st.session_state["current_article_id"] += 1
      st.session_state["current_image_file_index"] = 0


st.button("Previous Image", on_click=prev_image)
st.button("Next Image", on_click=next_image)

# ***** Right Column *****

# Fetching lines
lines = natsorted(glob.glob(f"{word_path}/{st.session_state['current_article_id']}/{st.session_state['current_article_id']}_{st.session_state['current_image_file_index'] + 1}/*.jpg"))

right_column.header("Image Details")

if st.session_state["current_line_index"] > 0:
  right_column.subheader("Previous Line")
  right_column.image(Image.open(lines[st.session_state["current_line_index"] - 1]))

right_column.subheader("Current Line")

# Fetching word bounding box co-ordinates
word_rectangle_start_points, word_rectangle_end_points = get_bounding_box_points(f"{word_path}/{st.session_state['current_article_id']}/{st.session_state['current_article_id']}_{st.session_state['current_image_file_index'] + 1}/{st.session_state['current_article_id']}_{st.session_state['current_image_file_index'] + 1}_{st.session_state['current_line_index'] + 1}.xml")

current_line_image = cv2.imread(lines[st.session_state["current_line_index"]])

# Drawing word bounding box
current_line_image = cv2.rectangle(current_line_image, word_rectangle_start_points[st.session_state["current_word_index"]], word_rectangle_end_points[st.session_state["current_word_index"]], (255, 0, 0), 5)

# right_column.image(Image.open(lines[st.session_state["current_line_index"]]))
right_column.image(current_line_image)

if st.session_state["current_line_index"] < len(lines) - 1:
  right_column.subheader("Next Line")
  right_column.image(Image.open(lines[st.session_state["current_line_index"] + 1]))

# Fetching image words
words = natsorted(glob.glob(f"{word_path}/{st.session_state['current_article_id']}/{st.session_state['current_article_id']}_{st.session_state['current_image_file_index'] + 1}/{st.session_state['current_article_id']}_{st.session_state['current_image_file_index'] + 1}_{st.session_state['current_line_index'] + 1}/*.jpg"))

if st.session_state["current_word_index"] > 0:
  right_column.subheader("Previous Word (Image)")
  right_column.image(Image.open(words[st.session_state["current_word_index"] - 1]))

right_column.subheader("Current Word (Image)")
right_column.image(Image.open(words[st.session_state["current_word_index"]]))

if st.session_state["current_word_index"] < len(words) - 1:
  right_column.subheader("Next Word (Image)")
  right_column.image(Image.open(words[st.session_state["current_word_index"] + 1]))

# Fetching excel words
excel_file = f"{excel_path}/{st.session_state['current_article_id']}/{st.session_state['current_article_id']}.xlsx"
df = pd.read_excel(excel_file)

right_column.subheader("Current Word (Excel)")
excel_word_key = f"{st.session_state['current_article_id']}_{st.session_state['current_image_file_index'] + 1}_{st.session_state['current_line_index'] + 1}_{st.session_state['current_word_index'] + 1}"
right_column.write(df[df["Id"] == excel_word_key].iloc[0]["Word"])


def prev_line():
  if st.session_state["current_line_index"] > 0:
    st.session_state["current_line_index"] -= 1

    return True
  else:
    return False


def next_line():
  if st.session_state["current_line_index"] < len(lines) - 1:
    st.session_state["current_line_index"] += 1

    return True
  else:
    return False


def prev_word():
  if st.session_state["current_word_index"] > 0:
    st.session_state["current_word_index"] -= 1
    # st.session_state["article_word_cursor"] -= 1
  else:
    # Go to previous line
    if prev_line():
      # Select the last word of the previous line
      words = glob.glob(f"{word_path}/{st.session_state['current_article_id']}/{st.session_state['current_article_id']}_{st.session_state['current_image_file_index'] + 1}/{st.session_state['current_article_id']}_{st.session_state['current_image_file_index'] + 1}_{st.session_state['current_line_index'] + 1}/*.jpg")
      st.session_state["current_word_index"] = len(words) - 1


def next_word():
  if st.session_state["current_word_index"] < len(words) - 1:
    st.session_state["current_word_index"] += 1
  else:
    # Go to next line
    if next_line():
      # Select the first word of the next line
      st.session_state["current_word_index"] = 0


right_column.button("Previous Word", on_click=prev_word)
right_column.button("Next Word", on_click=next_word)

# left_column.image(Image.open(f"{line_path}/{st.session_state.get('current_image_id')}/{st.session_state.get('current_image_id')}.jpg"))

# for image_id in image_ids:
#   print("Excel file: ", image_id)

#   if image_id not in IMAGE_TO_EXCLUDE:
#     excel_file = f"{excel_path}/{image_id}/{image_id}.xlsx"
#     df = pd.read_excel(excel_file)
#     print(df.head())
