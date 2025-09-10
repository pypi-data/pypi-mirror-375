# src/pyrendergui/elements.py
class BaseElement:
    def __init__(self, attributes):
        self.attrs = attributes
        self.name = attributes.get('name')

    def draw(self, canvas, scale):
        raise NotImplementedError # Her alt sınıf bunu kendi doldurmalı

class RectElement(BaseElement):
    def draw(self, canvas, scale):
        x = int(self.attrs.get("x")) * scale
        y = int(self.attrs.get("y")) * scale
        width = int(self.attrs.get("width")) * scale
        height = int(self.attrs.get("height")) * scale
        color = self.attrs.get("color")
        canvas.create_rectangle(x, y, x + width, y + height, fill=color, outline="")

class TextElement(BaseElement):
    def draw(self, canvas, scale):
        x = int(self.attrs.get("x")) * scale
        y = int(self.attrs.get("y")) * scale
        # Font boyutunu da ölçekle!
        font_parts = self.attrs.get("font").split()
        font_name = font_parts[0]
        font_size = int(font_parts[1]) * scale
        font_style = font_parts[2] if len(font_parts) > 2 else ""

        scaled_font = (font_name, int(font_size), font_style)

        canvas.create_text(x, y, text=self.attrs.get("value"), font=scaled_font, fill=self.attrs.get("color"))
