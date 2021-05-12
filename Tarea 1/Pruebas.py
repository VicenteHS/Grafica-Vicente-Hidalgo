import freesvg_sample
import xml.etree.ElementTree as ET
tree = ET.parse('pencil_sharpener.svg')
root = tree.getroot()

print(root.tag)