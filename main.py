"""
*****************************************
Project: BN-HTR Image to Text Automapper
Author: Chowdhury Mohammad Irfanuddin
Created: 12 October 2023
Updated: 22 October 2023
*****************************************
"""

import os
import glob
import pandas as pd
import streamlit as st
from natsort import natsorted
from xml.etree import ElementTree as ET
import cv2
from pathlib import Path


PATH = "./BN-HTR_Dataset"
IMAGE_TO_EXCLUDE = [34, 60]


# This function loads article ids. Its output is cached.
@st.cache_data
def load_article_ids(line_images_path):
  return natsorted([int(e) for e in os.listdir(line_images_path)])


# This function loads image paths of the current article. Its output is cached.
@st.cache_data
def load_image_paths(line_images_dir, current_article_id):
  image_list = glob.glob(f"{line_images_dir}/{current_article_id}/*.jpg")
  image_list.extend(glob.glob(f"{line_images_dir}/{current_article_id}/*.png"))
  image_list.extend(glob.glob(f"{line_images_dir}/{current_article_id}/*.JPG"))

  return natsorted(image_list)


# This function loads the line images contained in a page. Its output is cached.
@st.cache_data
def load_lines_images(word_images_dir, current_article_id, current_image_id):
  line_list = glob.glob(f"{word_images_dir}/{current_article_id}/{current_article_id}_{current_image_id + 1}/*.jpg")
  line_list.extend(glob.glob(f"{word_images_dir}/{current_article_id}/{current_article_id}_{current_image_id + 1}/*.png"))
  line_list.extend(glob.glob(f"{word_images_dir}/{current_article_id}/{current_article_id}_{current_image_id + 1}/*.JPG"))

  return natsorted(line_list)


# This function loads the word images contained in a line. Its output is cached.
@st.cache_data
def load_word_images(word_images_dir, current_article_id, current_image_id, current_line_id):
  word_list = glob.glob(f"{word_images_dir}/{current_article_id}/{current_article_id}_{current_image_id + 1}/{current_article_id}_{current_image_id + 1}_{current_line_id + 1}/*.jpg")
  word_list.extend(glob.glob(f"{word_images_dir}/{current_article_id}/{current_article_id}_{current_image_id + 1}/{current_article_id}_{current_image_id + 1}_{current_line_id + 1}/*.png"))
  word_list.extend(glob.glob(f"{word_images_dir}/{current_article_id}/{current_article_id}_{current_image_id + 1}/{current_article_id}_{current_image_id + 1}_{current_line_id + 1}/*.JPG"))

  return natsorted(word_list)


# This function loads excel file of words contained in the current article. Its output is cached.
@st.cache_data
def load_excel_dataframe(excel_files_dir, current_article_id):
  return pd.read_excel(f"{excel_files_dir}/{current_article_id}/{current_article_id}.xlsx")


# This function extracts and loads the bounding rectangle co-ordinates of any labelimg label XML file. Its output is cached.
@st.cache_data
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


def prev_image():
  if st.session_state["current_image_file_index"] > 0:
    st.session_state["current_image_file_index"] -= 1
    st.session_state["current_line_index"] = 0
    st.session_state["current_word_index"] = 0
  else:
    if st.session_state["current_article_id"] > article_ids[0]:
      st.session_state["current_article_id"] -= 1
      st.session_state["current_image_file_index"] = len(load_image_paths(st.session_state['current_article_id']))
      st.session_state["current_line_index"] = 0
      st.session_state["current_word_index"] = 0


def next_image():
  if st.session_state["current_image_file_index"] < len(image_paths) - 1:
    st.session_state["current_image_file_index"] += 1
    st.session_state["current_line_index"] = 0
    st.session_state["current_word_index"] = 0
  else:
    if st.session_state["current_article_id"] < len(article_ids):
      st.session_state["current_article_id"] += 1
      st.session_state["current_image_file_index"] = 0
      st.session_state["current_line_index"] = 0
      st.session_state["current_word_index"] = 0


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
      words = load_word_images(word_path, st.session_state['current_article_id'], st.session_state['current_image_file_index'], st.session_state['current_line_index'])
      st.session_state["current_word_index"] = len(words) - 1


def next_word():
  if st.session_state["current_word_index"] < len(words) - 1:
    st.session_state["current_word_index"] += 1
  else:
    # Go to next line
    if next_line():
      # Select the first word of the next line
      st.session_state["current_word_index"] = 0


# This function initializes session variables.
def setup(excel_path, line_path, word_path):
  global article_ids, image_paths, line_rectangle_start_points, line_rectangle_end_points, lines, word_rectangle_start_points, word_rectangle_end_points, words, excel_dataframe, excel_current_word_key, has_line_bounding_box, has_word_bounding_box

  # Enabling wide mode. The "set_page_config" has to be the first Streamlit function to be called
  st.set_page_config(layout="wide")

  # Fetching articles
  article_ids = load_article_ids(line_path)

  # Setting up session variables
  if not st.session_state.get("current_article_id"):
    st.session_state["current_article_id"] = article_ids[0]

  if not st.session_state.get("current_image_file_index"):
    st.session_state["current_image_file_index"] = 0

  if not st.session_state.get("current_line_index"):
    st.session_state["current_line_index"] = 0

  if not st.session_state.get("current_word_index"):
    st.session_state["current_word_index"] = 0

  # Fetching page images
  image_paths = load_image_paths(line_path, st.session_state['current_article_id'])

  # Fetching line bounding box co-ordinates
  has_line_bounding_box = True

  try:
    line_rectangle_start_points, line_rectangle_end_points = get_bounding_box_points(f"{line_path}/{st.session_state['current_article_id']}/{st.session_state['current_article_id']}_{st.session_state['current_image_file_index'] + 1}.xml")
  except:
    has_line_bounding_box = False

  # Fetching lines
  lines = load_lines_images(word_path, st.session_state['current_article_id'], st.session_state['current_image_file_index'])

  # Fetching word bounding box co-ordinates
  has_word_bounding_box = True

  try:
    word_rectangle_start_points, word_rectangle_end_points = get_bounding_box_points(f"{word_path}/{st.session_state['current_article_id']}/{st.session_state['current_article_id']}_{st.session_state['current_image_file_index'] + 1}/{st.session_state['current_article_id']}_{st.session_state['current_image_file_index'] + 1}_{st.session_state['current_line_index'] + 1}.xml")
  except:
    has_word_bounding_box = False

  # Fetching image words
  words = load_word_images(word_path, st.session_state['current_article_id'], st.session_state['current_image_file_index'], st.session_state['current_line_index'])

  # Fetching excel words
  excel_dataframe = load_excel_dataframe(excel_path, st.session_state['current_article_id'])

  excel_current_word_key = f"{st.session_state['current_article_id']}_{st.session_state['current_image_file_index'] + 1}_{st.session_state['current_line_index'] + 1}_{st.session_state['current_word_index'] + 1}"


# This function draws the component to the web page
def render():
  left_column, right_column = st.columns(2)

  image = cv2.imread(image_paths[st.session_state["current_image_file_index"]])

  # Drawing line bounding box
  if has_line_bounding_box:
    image = cv2.rectangle(image, line_rectangle_start_points[st.session_state["current_line_index"]], line_rectangle_end_points[st.session_state["current_line_index"]], (255, 0, 0), 5)
  image = cv2.resize(image, (600, 700))

  # ***** Left Column *****

  left_column.header("Current Image")
  left_column.subheader(f"Article: {st.session_state['current_article_id']} Image: {st.session_state['current_image_file_index'] + 1}")
  left_column.image(image)

  with left_column.container():
    lc, rc = st.columns(2)

    lc.button("Previous Image", on_click=prev_image)
    rc.button("Next Image", on_click=next_image)

  # ***** Right Column *****

  right_column.header("Image Details")

  if st.session_state["current_line_index"] > 0:
    right_column.subheader("Previous Line")
    previous_line_image = cv2.imread(lines[st.session_state["current_line_index"] - 1])
    previous_line_image = cv2.resize(previous_line_image, (400, 70))
    right_column.image(previous_line_image)

  right_column.subheader("Current Line")

  current_line_image = cv2.imread(lines[st.session_state["current_line_index"]])

  # Drawing word bounding box
  if has_word_bounding_box:
    current_line_image = cv2.rectangle(current_line_image, word_rectangle_start_points[st.session_state["current_word_index"]], word_rectangle_end_points[st.session_state["current_word_index"]], (255, 0, 0), 5)

  right_column.image(current_line_image)

  if st.session_state["current_line_index"] < len(lines) - 1:
    right_column.subheader("Next Line")
    next_line_image = cv2.imread(lines[st.session_state["current_line_index"] + 1])
    next_line_image = cv2.resize(next_line_image, (400, 70))
    right_column.image(next_line_image)

  with right_column.container():
    lc, rc = st.columns(2)

    lc.subheader("Current Word (Image)")
    current_word_image = cv2.imread(words[st.session_state["current_word_index"]])
    current_word_image = cv2.resize(current_word_image, (200, 100))
    lc.image(current_word_image)

    rc.subheader("Current Word (Excel)")

    try:
      rc.subheader(excel_dataframe[excel_dataframe["Id"] == excel_current_word_key].iloc[0]["Word"])
    except Exception as e:
      print(e)

  with right_column.container():
    lc, rc = st.columns(2)

    if st.session_state["current_word_index"] > 0:
      lc.subheader("Previous Word (Image)")
      previous_word_image = cv2.imread(words[st.session_state["current_word_index"] - 1])
      previous_word_image = cv2.resize(previous_word_image, (150, 70))
      lc.image(previous_word_image)

    if st.session_state["current_word_index"] < len(words) - 1:
      rc.subheader("Next Word (Image)")
      next_word_image = cv2.imread(words[st.session_state["current_word_index"] + 1])
      next_word_image = cv2.resize(next_word_image, (150, 70))
      rc.image(next_word_image)

  with right_column.container():
    lc, rc = st.columns(2)

    lc.button("Previous Word", on_click=prev_word)
    rc.button("Next Word", on_click=next_word)


def main():
  global line_path, word_path

  excel_path = f"{PATH}/Recognition_Ground_Truth_Texts"
  line_path = f"{PATH}/Segmentation_Images/Lines"
  word_path = f"{PATH}/Segmentation_Images/Words"

  setup(excel_path, line_path, word_path)
  render()


if __name__ == "__main__":
  main()
