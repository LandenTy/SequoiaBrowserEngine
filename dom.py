"""
dom.py

Description:
Parses elements of a provided HTML file as a DOM Tree and outputs it
so it can be rendered in render.py. Supports SVG elements.
"""
import re

class Node:
    def __init__(self, tag, attrs=None, text="", children=None):
        self.tag = tag
        self.attrs = attrs if attrs else {}
        self.text = text
        self.children = children if children else []
        self.link_instance = None

    def add_child(self, child):
        self.children.append(child)

    def __repr__(self, level=0):
        indent = "  " * level
        if self.tag == "text":
            return f'{indent}#text: "{self.text.strip()}"\n'

        s = f"{indent}<{self.tag}"
        if self.attrs:
            s += " " + " ".join(f'{k}="{v}"' for k, v in self.attrs.items())
        s += ">\n"

        for child in self.children:
            s += child.__repr__(level + 1)

        return s


def parse_html(html):
    """Improved HTML parser -> DOM tree (handles self-closing and optional tags)"""
    # Remove DOCTYPE, <title>, <style> blocks
    html = re.sub(r"<!DOCTYPE[^>]*>", "", html, flags=re.IGNORECASE)
    html = re.sub(r"<title>.*?</title>", "", html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.IGNORECASE | re.DOTALL)

    # Regex to match tags (opening, closing, self-closing)
    tag_regex = re.compile(r"<(/?)(\w+)([^>]*)>", flags=re.DOTALL)

    # Updated self-closing tags including svg
    self_closing_tags = {"br", "img", "hr", "meta", "link", "input", "svg"}

    stack = []
    root = Node("document")
    stack.append(root)
    pos = 0

    for match in tag_regex.finditer(html):
        # Capture text between tags
        text_between = html[pos:match.start()]
        text_between = text_between.replace("\n", " ").strip()
        if text_between:
            stack[-1].add_child(Node("text", text=text_between))

        closing, tag, attr_str = match.groups()
        tag = tag.lower()

        # --- Parse attributes ---
        attrs = {}
        for attr_match in re.finditer(r'(\w+(?:-\w+)?)(?:="([^"]*)")?', attr_str):
            key, value = attr_match.groups()
            attrs[key] = value if value is not None else ""

        # Determine if self-closing
        is_self_closing = (tag in self_closing_tags) or attr_str.strip().endswith("/")

        if not closing:  # opening tag
            new_node = Node(tag, attrs)
            stack[-1].add_child(new_node)
            if not is_self_closing:
                stack.append(new_node)
        else:  # closing tag
            # Pop stack until matching tag or optional tags
            for i in range(len(stack)-1, 0, -1):
                if stack[i].tag == tag or stack[i].tag in {"head", "body"}:
                    stack = stack[:i]
                    break

        pos = match.end()

    # Remaining text after last tag
    if pos < len(html):
        remaining_text = html[pos:].replace("\n", " ").strip()
        if remaining_text:
            stack[-1].add_child(Node("text", text=remaining_text))

    return root
