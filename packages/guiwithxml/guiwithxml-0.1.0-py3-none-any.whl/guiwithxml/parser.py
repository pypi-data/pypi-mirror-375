# src/pyrendergui/parser.py
import xml.etree.ElementTree as ET
from .elements import RectElement, TextElement
# Diğer özel hatalarımızı import edelim
from .exceptions import XMLParsingError, UnknownElementError

TAG_MAP = {
    "Rect": RectElement,
    "Text": TextElement,
}

def parse_xml_file(file_path):
    try:
        tree = ET.parse(file_path)
    except ET.ParseError as e:
        # XML bozuksa, standart hatayı bizim özel hatamızla sarmalayalım
        raise XMLParsingError(f"XML dosyasında format hatası: {e}") from e

    root = tree.getroot()
    elements = []
    screen_config = root.attrib 

    for node in root:
        if node.tag in TAG_MAP:
            element_class = TAG_MAP[node.tag]
            elements.append(element_class(node.attrib))
        else:
            # Eğer etiket TAG_MAP içinde yoksa, hata fırlat!
            raise UnknownElementError(f"XML içinde tanınmayan etiket bulundu: <{node.tag}>")
            
    return elements, screen_config