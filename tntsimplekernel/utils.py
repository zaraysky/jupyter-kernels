class TNTCodeParser:
    def __init__(self):
        self.code = ''

    @classmethod
    def parse(cls, code: str) -> str:
        lines = code.split('\n')
        top_line = lines[0]
        if top_line[:3] == '-- ':  # magic line
            new_lines = lines[1:]
            new_lines.append(top_line[3:])
        return '\n'.join(lines)
