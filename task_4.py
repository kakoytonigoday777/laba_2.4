import re

def serialize(obj, indent=0, level=0):
    if indent > 0:
        space = ' ' * (level * indent)
        next_space = ' ' * ((level + 1) * indent)
    else:
        space = next_space = ''

    if isinstance(obj, dict):
        if not obj:
            return "{}"
        items = []
        for k, v in obj.items():
            items.append(f"{next_space}{json_escape(str(k))}: {serialize(v, indent, level+1)}")
        return "{\n" + ",\n".join(items) + f"\n{space}}}"
    elif isinstance(obj, list):
        if not obj:
            return "[]"
        items = [f"{next_space}{serialize(item, indent, level+1)}" for item in obj]
        return "[\n" + ",\n".join(items) + f"\n{space}]"
    elif isinstance(obj, str):
        return f'"{json_escape(obj)}"'
    elif isinstance(obj, bool):
        return "true" if obj else "false"
    elif obj is None:
        return "null"
    elif isinstance(obj, (int, float)):
        return str(obj)
    else:
        raise TypeError(f"Type {type(obj)} not serializable")

def json_escape(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')

def deserialize(json_str):
    tokenizer = Tokenizer(json_str)
    result = parse_value(tokenizer)
    tokenizer.skip_whitespace()
    if not tokenizer.is_end():
        raise ValueError(f"Unexpected token at line {tokenizer.line}, column {tokenizer.col}")
    return result

class Tokenizer:
    def __init__(self, s):
        self.s = s
        self.pos = 0
        self.line = 1
        self.col = 1

    def peek(self):
        if self.pos >= len(self.s):
            return ''
        return self.s[self.pos]

    def next(self):
        ch = self.s[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def skip_whitespace(self):
        while self.pos < len(self.s) and self.s[self.pos] in ' \t\n\r':
            self.next()

    def is_end(self):
        return self.pos >= len(self.s)

    def expect(self, expected):
        if self.peek() != expected:
            raise ValueError(f"Expected '{expected}' at line {self.line}, column {self.col}")
        self.next()

def parse_value(tok):
    tok.skip_whitespace()
    ch = tok.peek()
    if ch == '{':
        return parse_object(tok)
    elif ch == '[':
        return parse_array(tok)
    elif ch == '"':
        return parse_string(tok)
    elif ch == 't':
        tok.expect('t')
        tok.expect('r')
        tok.expect('u')
        tok.expect('e')
        return True
    elif ch == 'f':
        tok.expect('f')
        tok.expect('a')
        tok.expect('l')
        tok.expect('s')
        tok.expect('e')
        return False
    elif ch == 'n':
        tok.expect('n')
        tok.expect('u')
        tok.expect('l')
        tok.expect('l')
        return None
    elif ch == '-' or ch.isdigit():
        return parse_number(tok)
    else:
        raise ValueError(f"Unexpected character '{ch}' at line {tok.line}, column {tok.col}")

def parse_object(tok):
    tok.expect('{')
    tok.skip_whitespace()
    obj = {}
    if tok.peek() == '}':
        tok.next()
        return obj
    while True:
        key = parse_string(tok)
        tok.skip_whitespace()
        tok.expect(':')
        value = parse_value(tok)
        obj[key] = value
        tok.skip_whitespace()
        ch = tok.peek()
        if ch == '}':
            tok.next()
            break
        elif ch == ',':
            tok.next()
            tok.skip_whitespace()
        else:
            raise ValueError(f"Expected ',' or '}}' at line {tok.line}, column {tok.col}")
    return obj

def parse_array(tok):
    tok.expect('[')
    tok.skip_whitespace()
    arr = []
    if tok.peek() == ']':
        tok.next()
        return arr
    while True:
        arr.append(parse_value(tok))
        tok.skip_whitespace()
        ch = tok.peek()
        if ch == ']':
            tok.next()
            break
        elif ch == ',':
            tok.next()
            tok.skip_whitespace()
        else:
            raise ValueError(f"Expected ',' or ']' at line {tok.line}, column {tok.col}")
    return arr

def parse_string(tok):
    tok.expect('"')
    result = []
    while tok.peek() != '"':
        ch = tok.next()
        if ch == '\\':
            ch = tok.next()
            if ch == '"':
                result.append('"')
            elif ch == '\\':
                result.append('\\')
            elif ch == '/':
                result.append('/')
            elif ch == 'b':
                result.append('\b')
            elif ch == 'f':
                result.append('\f')
            elif ch == 'n':
                result.append('\n')
            elif ch == 'r':
                result.append('\r')
            elif ch == 't':
                result.append('\t')
            else:
                raise ValueError(f"Invalid escape sequence at line {tok.line}, column {tok.col}")
        else:
            result.append(ch)
    tok.next()
    return ''.join(result)

def parse_number(tok):
    start_line, start_col = tok.line, tok.col
    num_str = ''
    if tok.peek() == '-':
        num_str += tok.next()
    while tok.peek().isdigit():
        num_str += tok.next()
    if tok.peek() == '.':
        num_str += tok.next()
        while tok.peek().isdigit():
            num_str += tok.next()
    if tok.peek() in 'eE':
        num_str += tok.next()
        if tok.peek() in '+-':
            num_str += tok.next()
        while tok.peek().isdigit():
            num_str += tok.next()
    try:
        if '.' in num_str or 'e' in num_str or 'E' in num_str:
            return float(num_str)
        else:
            return int(num_str)
    except ValueError:
        raise ValueError(f"Invalid number at line {start_line}, column {start_col}")

def validate_json(json_str):
    try:
        deserialize(json_str)
        return True
    except ValueError as e:
        print("Ошибка валидации JSON:", e)
        return False

if __name__ == '__main__':
    json_correct = '{"name": "John", "age": 30, "cars": ["Ford", "BMW"]}'
    print("Сериализация Python-объекта:")
    obj = {"name": "John", "age": 30, "cars": ["Ford", "BMW"]}
    print(serialize(obj, indent=2))
    print("\nДесериализация JSON:")
    print(deserialize(json_correct))
    print("\nВалидация корректного JSON:", validate_json(json_correct))

    json_incorrect = '{"name": "John", "age": 30,}'
    print("Валидация некорректного JSON:", validate_json(json_incorrect))