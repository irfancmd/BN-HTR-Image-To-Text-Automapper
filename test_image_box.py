import matplotlib.pyplot as plt
import cv2
import xml.etree.ElementTree as ET

PATH = "./BN-HTR_Dataset"

line_path = f"{PATH}/Segmentation_Images/Lines"
word_path = f"{PATH}/Segmentation_Images/Words"

article_no = 1
image_no = 1

image = cv2.imread(f"{line_path}/{article_no}/{article_no}_{image_no}.jpg")

line_label_xml = ET.parse(f"{line_path}/{article_no}/{article_no}_{image_no}.xml")

rectangle_start_points = []
rectangle_end_points = []

for child in line_label_xml.getroot():
  if child.tag == "object":
    start_point = (int(child[4][0].text), int(child[4][1].text))
    end_point = (int(child[4][2].text), int(child[4][3].text))

    rectangle_start_points.append(start_point)
    rectangle_end_points.append(end_point)


rectangle_start_point = rectangle_start_points[0]
rectangle_end_point = rectangle_end_points[0]

print(rectangle_start_point)
print(rectangle_end_point)

image = cv2.rectangle(image, rectangle_start_point, rectangle_end_point, (255, 0, 0), 2)

plt.imshow(image)
plt.show()
