class Canvas():
    """
    Canvas to draw with braille characters
    """
    offset = 0x2800

    pixel_map = ((0x01, 0x08),
                 (0x02, 0x10),
                 (0x04, 0x20),
                 (0x40, 0x80))

    color_map = ('\033[39m', '\033[31m', '\033[36m', '\033[33m',
                 '\033[32m', '\033[35m', '\033[34m', '\033[37m',
                 '\033[90m', '\033[91m', '\033[96m', '\033[93m',
                 '\033[92m', '\033[95m', '\033[94m', '\033[97m')

    def __init__(self, rows, cols):
        """
        :param rows: height of the canvas in characters
        :type rows: int

        :param cols: width of the canvas in characters
        :type cols: int
        """
        assert rows > 0
        assert cols > 0

        self.rows = rows
        self.cols = cols
        self.clear()

    def clear(self):
        """
        Clear all dots
        """
        self.chars = [[0 for x in range(self.cols)] for y in range(self.rows)]
        self.colors = [[0 for x in range(self.cols)] for y in range(self.rows)]

    def transform_coords(self, x, y):
        """
        Transform coordinates from [0, 1] to given range

        :param x: x-coordinate between 0.0 and 1.0
        :type x: float

        :param y: y-coordinate between 0.0 and 1.0
        :type y: float

        :return: transformed (x, y)
        """
        h_dots = self.rows * 4 - 4
        w_dots = self.cols * 2 - 2

        x = int(round(x * w_dots + 0.5))
        y = int(round((1.0 - y) * h_dots + 1.0))

        return x, y

    def set(self, x, y, color=0):
        """
        Set a dot at a given position

        :param x: x-coordinate between 0.0 and 1.0
        :type x: float

        :param y: y-coordinate between 0.0 and 1.0
        :type y: float

        :param color: color as int between 0 and 15
        :type color: int
        """
        x, y = self.transform_coords(x, y)

        cy = y // 4
        cx = x // 2

        if cy < 0 or cy >= self.rows or cx < 0 or cx >= self.cols:
            return

        self.chars[cy][cx] |= Canvas.pixel_map[y % 4][x % 2]
        self.colors[cy][cx] = color % 16

    def line(self, x1, y1, x2, y2, color=0):
        """
        Draw a line between (x1, y1), (x2, y2)

        :param x1: x coordinate of the startpoint
        :type x1: float

        :param y1: y coordinate of the startpoint
        :type y1: float

        :param x2: x coordinate of the endpoint
        :type x2: float

        :param y2: y coordinate of the endpoint
        :type y2: float

        :param color: color as int between 0 and 15
        :type color: int
        """
        x1, y1 = self.transform_coords(x1, y1)
        x2, y2 = self.transform_coords(x2, y2)

        xdiff = max(x1, x2) - min(x1, x2)
        ydiff = max(y1, y2) - min(y1, y2)
        xdir = 1 if x1 <= x2 else -1
        ydir = 1 if y1 <= y2 else -1

        r = max(xdiff, ydiff)

        for i in range(r+1):
            x = x1
            y = y1

            if ydiff:
                y += (float(i) * ydiff) / r * ydir
            if xdiff:
                x += (float(i) * xdiff) / r * xdir

            x = int(round(x))
            y = int(round(y))
            cy = y // 4
            cx = x // 2

            if cy < 0 or cy >= self.rows or cx < 0 or cx >= self.cols:
                continue

            self.chars[cy][cx] |= Canvas.pixel_map[y % 4][x % 2]
            self.colors[cy][cx] = color % 16

    def get_rows(self):
        """
        Get a list of lines for printing

        :return: list(str)
        """
        ret = []
        for y in range(self.rows):
            row = ''
            for x in range(self.cols):
                row += Canvas.color_map[self.colors[y][x]]
                row += chr(self.chars[y][x] + Canvas.offset)
            ret.append(row + Canvas.color_map[0])

        return ret

    def __str__(self):
        return '\n'.join(self.get_rows())
