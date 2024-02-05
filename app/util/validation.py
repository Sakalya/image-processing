import os

COLUMNS_NR = int(os.getenv('COLUMNS_NR', 200))


class Validator:
    def __init__(self):
        pass

    def is_lines_valid(self, line):
        if len(line) != COLUMNS_NR + 1:
            return False

        for index, value in enumerate(line):
            if index == 0:
                continue
            if value is not None and value != '':
                if 0 <= int(value) <= 255:
                    continue
            return False
        return True
