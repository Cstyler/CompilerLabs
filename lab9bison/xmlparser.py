import xml.etree.ElementTree as ET

tree = ET.parse('test.xml')
ET.dump(tree)
