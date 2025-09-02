"""
render

Description: Has base information on drawing the DOM Elements after being parsed from DOM.PY
"""
# Libraries
import pygame, time
import pygame.freetype
pygame.init()

# Configuration
from config import (SCREEN_WIDTH, SCREEN_HEIGHT, LINE_HEIGHTS, 
                   CHAR_WIDTH, LEFT_MARGIN, fonts)

# Components
from Input import Input, wrap_text, wrap_text_pixel
from PasswordInput import PasswordInput
from Slider import Slider
from RadioButton import RadioButton
from ColorInput import ColorPicker
from SVG import parse_svg_file, scale_points, draw_svg
from Button import Button
from Link import Link
from Table import Table

pygame.init()

def get_node_text(node):
    """Recursively collect all text from node and children."""
    if node.tag == "text":
        return node.text.strip()
    text_parts = [get_node_text(c) for c in node.children]
    return " ".join([t for t in text_parts if t])


def draw_node(node, y, screen, fonts, interactive_elements, indent=0, parent_tag=None):
    padding_x = LEFT_MARGIN + indent

    # Determine current font
    current_tag = node.tag if node.tag != "text" else parent_tag or "p"
    font = fonts.get(current_tag, fonts["p"])
    line_height = int(font.get_sized_height() * 1.3)

    # --- Text nodes ---
    if node.tag in ("h1","h2","h3","h4","h5","h6","p","a","text"):
        text = node.text.strip() if node.text else ""
        if text:
            max_width_px = SCREEN_WIDTH - LEFT_MARGIN*2 - indent
            wrapped_lines = wrap_text_pixel(text, font, max_width_px)

            for line in wrapped_lines:
                font.fgcolor = (0,0,255) if current_tag == "a" else (0,0,0)
                font.render_to(screen, (padding_x, y), line)

                # Handle <a> tag links
                if current_tag == "a":
                    link_text = get_node_text(node)  # get full text from children
                    text_rect = font.get_rect(link_text)
                    rect_tuple = (padding_x, y, text_rect.width, text_rect.height)
                
                    # Safely get href
                    href = ""
                    if hasattr(node, "attrs") and "href" in node.attrs:
                        href = node.attrs["href"].strip()
                
                    # Create or update Link instance
                    if getattr(node, "link_instance", None) is None:
                        node.link_instance = Link(rect_tuple, link_text, href=href)
                    else:
                        node.link_instance.rect = pygame.Rect(*rect_tuple)
                        node.link_instance.text = link_text
                        node.link_instance.href = href
                
                    interactive_elements.append(node.link_instance)
                
                    # Draw underline
                    underline_y = y + text_rect.height - 2
                    pygame.draw.line(screen, (0,0,255),
                                     (padding_x, underline_y),
                                     (padding_x + text_rect.width, underline_y), 1)
    
                y += line_height

    # --- Line break ---
    if node.tag == "br":
        y += line_height

    # --- Lists ---
    if node.tag in ("ul", "ol"):
        child_indent = indent + 20
        counter = 1
        for child in node.children:
            if child.tag == "li":
                bullet = "• " if node.tag == "ul" else f"{counter}. "
                li_font = fonts.get("p", fonts["p"])
                li_text = " ".join(c.text.strip() for c in child.children if c.tag=="text")
                max_width_px = SCREEN_WIDTH - LEFT_MARGIN*2 - child_indent - li_font.get_rect(bullet).width
                wrapped_lines = wrap_text_pixel(li_text, li_font, max_width_px)

                for i, line in enumerate(wrapped_lines):
                    draw_x = LEFT_MARGIN + child_indent
                    if i == 0:
                        li_font.render_to(screen, (draw_x, y), bullet)
                        draw_x += li_font.get_rect(bullet).width
                    li_font.fgcolor = (0,0,0)
                    li_font.render_to(screen, (draw_x, y), line)
                    y += int(li_font.get_sized_height() * 1.3)
                if node.tag == "ol":
                    counter += 1
            else:
                y = draw_node(child, y, screen, fonts, interactive_elements, child_indent)
        return y

    # --- Input ---
    if node.tag == "input":
        width, height = 200, max(30, line_height+8)
        rect = pygame.Rect(padding_x, y, width, height)
        initial_text = node.attrs.get("value", node.text)
    
        # Determine input type
        input_type = node.attrs.get("type", "text").lower()
    
        # Create the appropriate Input/Control subclass
        if getattr(node, "input_instance", None) is None:
            if input_type == "password":
                from PasswordInput import PasswordInput
                node.input_instance = PasswordInput(rect, initial_text)
            elif input_type == "number":
                from NumberInput import NumberInput
                node.input_instance = NumberInput(rect, initial_text)
            elif input_type == "color":
                from ColorInput import ColorPicker
                node.input_instance = ColorPicker(rect)
            elif input_type == "range":
                min_val = float(node.attrs.get("min", 0))
                max_val = float(node.attrs.get("max", 100))
                value = float(node.attrs.get("value", (min_val+max_val)/2))
                from Slider import Slider
                node.input_instance = Slider(rect, min_val, max_val, value)
            elif input_type == "radio":
                group_name = node.attrs.get("name")  # HTML uses 'name' to group radios
                selected = node.attrs.get("checked") is not None
                # Make height a square for the circle button
                button_size = min(width, height)
                node.input_instance = RadioButton(
                    pygame.Rect(padding_x, y, button_size, button_size),
                    label=initial_text,
                    group=group_name,
                    selected=selected
                )
            else:
                node.input_instance = Input(rect, initial_text)
        else:
            node.input_instance.rect = rect
    
        # Draw and register the interactive element
        if hasattr(node.input_instance, "draw"):
            node.input_instance.draw(screen, fonts["p"])
        interactive_elements.append(node.input_instance)
        y += height + 10
        return y

    # --- Button ---
    if node.tag == "button":
        button_text = node.text.strip() if node.text else ""
        if not button_text:
            button_text = " ".join(c.text.strip() for c in node.children if c.tag=="text")
        if not button_text:
            button_text = "Button"

        font_btn = fonts["button"]
        text_width = font_btn.get_rect(button_text).width
        text_height = font_btn.get_sized_height()
        padding_btn_x, padding_btn_y = 12, 6
        width = max(60, text_width + padding_btn_x*2)
        height = max(text_height + padding_btn_y*2, 30)
        rect = pygame.Rect(padding_x, y, width, height)

        if getattr(node, "button_instance", None) is None:
            node.button_instance = Button(
                (rect.x, rect.y, rect.width, rect.height),
                button_text,
                callback=lambda n=node: print(f"Clicked '{button_text}'")
            )

        node.button_instance.rect = rect
        node.button_instance.label = button_text
        node.button_instance.draw(screen, font_btn)
        interactive_elements.append(node.button_instance)
        y += height + 6
        return y

    # --- Horizontal rule ---
    if node.tag == "hr":
        hr_height = 2
        hr_color = (160,160,160)
        rect = pygame.Rect(LEFT_MARGIN+indent, y + line_height//2, SCREEN_WIDTH - 2*(LEFT_MARGIN+indent), hr_height)
        pygame.draw.rect(screen, hr_color, rect)
        y += line_height

    # --- Containers ---
    if node.tag in ("div","body","html"):
        child_indent = indent + (20 if node.tag=="div" else 0)
        for child in node.children:
            y = draw_node(child, y, screen, fonts, interactive_elements, child_indent, parent_tag=node.tag)
        return y

    # --- SVG ---
    if node.tag == "svg":
        width = int(node.attrs.get("width", 200))
        height = int(node.attrs.get("height", 200))
        src = node.attrs.get("src")
        svg_offset = (LEFT_MARGIN + indent, y)

        if getattr(node, "svg_elements", None) is None and src:
            try:
                node.svg_elements = parse_svg_file(src)
                node.svg_elements = scale_points(node.svg_elements, width, height, viewBox=(0,0,100,100), margin=0)
            except FileNotFoundError:
                node.svg_elements = []

        if getattr(node, "svg_elements", None):
            draw_svg(node.svg_elements, screen, offset=svg_offset)

        y += height + 10
        return y
    
    # --- Tables ---
    if node.tag == "table":
        # Start with a reasonable initial rect height; Table will compute exact height
        initial_rect = pygame.Rect(padding_x, y, 400, 200)
    
        # Create Table instance if it doesn't exist
        if getattr(node, "table_instance", None) is None:
            node.table_instance = Table(initial_rect, node)
    
        # Draw the table
        node.table_instance.draw(screen, fonts["p"])
    
        # Increment y by the actual height of the table plus some spacing
        y += node.table_instance.height + 10
        return y
    
    # --- Recursively draw children ---
    for child in node.children:
        y = draw_node(child, y, screen, fonts, interactive_elements, indent, parent_tag=node.tag)

    return y
