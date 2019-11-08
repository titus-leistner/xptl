import sys
import os
import math

from .canvas import Canvas

usage = """
Usage: xptl-plot INPUT [COLUMNS]

INPUT       csv-file with one header line followed by comma-separated floats

COLUMNS     comma-separated list of y-columns csv-file to plot. E.g. 2,4,5
"""


# http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
def get_terminal_size():
    """
    Returns terminal height, width

    :return: (int, int)
    """
    env = os.environ

    def ioctl_GWINSZ(fd):
        try:
            import fcntl
            import termios
            import struct
            cr = struct.unpack('hh', fcntl.ioctl(
                fd, termios.TIOCGWINSZ, '1234'))
        except Exception:
            return
        return cr

    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)

    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except Exception:
            pass

    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))

    return int(cr[0]), int(cr[1])


ASPECT = 2


def main():
    if len(sys.argv) < 2:
        print(usage)
        exit()

    fname = sys.argv[1]

    cols = 'all'
    if len(sys.argv) > 2:
        cols = sys.argv[2]

    data = []
    headers = []
    split = None

    with open(fname, 'r', newline='') as f:
        headers = f.readline().rstrip('\n')

        # split at commas or semicolon if it appears
        if ';' in headers:
            split = ';'
        elif ',' in headers:
            split = ','

        headers = headers.split(split)

        data = [[] for i in range(len(headers))]
        for l in f:
            for i, f in enumerate(l.strip('\n').split(split)):
                try:
                    data[i].append(float(f))
                except ValueError:
                    data[i].append(0.0)

    x_axis = data[0]
    x_header = headers[0]
    headers = headers[1:]
    y_axes = data[1:]

    # only include some axes
    if cols != 'all':
        cols = [int(col) - 1 for col in cols.split(',')]
        if min(cols) < 0 or max(cols) >= len(headers):
            print('Error: the provided columns are out of range!')
            exit(1)

        y_axes = [y_axes[i] for i in cols]
        headers = [headers[i] for i in cols]

    # get data interval
    x_min = min(x_axis)
    x_max = max(x_axis)

    y_min = min(min(y_axes))
    y_max = max(max(y_axes))

    def normalize(x, y):
        """
        Normalize the coordinates to be between 0 and 1

        :param x: x-coordinate
        :type x: float

        :patam y: y-coordinate
        :type y: float
        """
        return (x - x_min) / (x_max - x_min), (y - y_min) / (y_max - y_min)

    y_digits = max(1, int(math.log10(abs(y_max))))

    if y_min != 0.0:
        y_digits = max(y_digits, int(math.log10(abs(y_min))))
    y_digits += 7

    h, w = get_terminal_size()
    w -= y_digits + 2
    h = min(w // (2 * ASPECT), h)
    canvas = Canvas(h, w)

    # plot graphs
    color = 1
    step = max(1, len(x_axis) // canvas.cols * 4)
    for axis in y_axes:
        for i in range(0, len(axis) - step, step):
            x1, y1 = normalize(x_axis[i], axis[i])
            x2, y2 = normalize(x_axis[i + step], axis[i + step])
            canvas.line(x1, y1, x2, y2, color)

        color += 1

    # print axis numbers
    y = y_max
    for row in canvas.get_rows():
        print(('{:' + str(y_digits) + '.5f} \u2524').format(y) + row)
        y -= (y_max - y_min) / (h - 1)

    print(y_digits * ' ' + ' \u2514\u252c', end='')
    print((w - 2) * '\u2500' + '\u252c')

    print(y_digits * ' ', end='')

    x_label = f'  {x_min:<10} '
    w_remain = w - len(x_label) + 2
    x_label += '{:' + str(w_remain) + '}'
    x_label = x_label.format(x_max)
    print(x_label)

    # print legend
    color = 1
    print('')
    print((y_digits + 2) * ' ', end='')
    vertical = chr(
        (canvas.pixel_map[1][0] | canvas.pixel_map[1][1]) + canvas.offset)
    vertical += chr(canvas.pixel_map[1][0] + canvas.offset)

    print(f'x-axis: {x_header}   y-axis: ', end='')
    for header in headers:
        print(f'{canvas.color_map[color]}{vertical}{header}    ', end='')
        color += 1
    print(canvas.color_map[0])


if __name__ == '__main__':
    main()
