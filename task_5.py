import re

class XMLElement:
    def __init__(self, tag, attrib=None, text="", children=None):
        self.tag = tag
        self.attrib = attrib or {}
        self.text = text
        self.children = children or []

def serialize_xml(node, indent=0, level=0):
    space = ' ' * (level * indent) if indent > 0 else ''
    attrs = ''.join(f' {k}="{escape_xml(v)}"' for k, v in node.attrib.items())
    if not node.children and not node.text.strip():
        return f"{space}<{node.tag}{attrs} />"
    opening = f"{space}<{node.tag}{attrs}>"
    closing = f"{space}</{node.tag}>"
    if node.children:
        inner = ''.join(serialize_xml(child, indent, level + 1) for child in node.children)
        return opening + '\n' + inner + '\n' + closing
    else:
        return opening + escape_xml(node.text) + closing

def escape_xml(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')

def deserialize_xml(xml_str):
    xml_str = re.sub(r'<!--.*?-->', '', xml_str, flags=re.DOTALL)
    tokens = re.finditer(r'<(\/?)([^\s>]+)([^>]*)>|([^<]+)', xml_str)
    stack = []
    root = None

    for match in tokens:
        if match.group(0).startswith('<'):
            is_closing = match.group(1) == '/'
            tag = match.group(2)
            attrs_str = match.group(3).strip()
            if not is_closing:
                attrib = {}
                if attrs_str:
                    for attr in re.findall(r'(\w+)="([^"]*)"', attrs_str):
                        attrib[attr[0]] = attr[1]
                elem = XMLElement(tag, attrib)
                if stack:
                    stack[-1].children.append(elem)
                else:
                    root = elem
                stack.append(elem)
                # Проверка на самозакрывающийся тег
                if attrs_str.endswith('/') or match.group(0).endswith('/>'):
                    stack.pop()
            else:
                if not stack or stack[-1].tag != tag:
                    raise ValueError(f"Closing tag mismatch: </{tag}> not matching {stack[-1].tag if stack else 'None'}")
                stack.pop()
        else:
            text = match.group(0)
            if stack and text.strip():
                stack[-1].text += text
    if stack:
        raise ValueError("Unclosed tags")
    return root

def validate_xml(xml_str):
    try:
        deserialize_xml(xml_str)
        return True
    except Exception as e:
        print("Ошибка валидации XML:", e)
        return False

if __name__ == '__main__':
    root = XMLElement("book")
    root.attrib = {"id": "1"}
    title = XMLElement("title", text="Python Programming")
    author = XMLElement("author", text="John Doe")
    root.children = [title, author]

    print("Сериализация XML с отступом 2:")
    print(serialize_xml(root, indent=2))

    xml_string = '<book id="1"><title>Python Programming</title><author>John Doe</author></book>'
    print("\nДесериализация XML:")
    parsed = deserialize_xml(xml_string)
    print(f"Корневой тег: {parsed.tag}, атрибуты: {parsed.attrib}")

    print("\nВалидация корректного XML:", validate_xml(xml_string))
    invalid_xml = '<book><title>Test</title></book'
    print("Валидация некорректного XML:", validate_xml(invalid_xml))