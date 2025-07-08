from configs import *
from g_code_comands import *


def generate_toolpath(prnt, cap):
    toolpath = []

    toolpath.extend(home())
    toolpath.extend(printPrimeLine(xStart=5, yStart=10, len=10, prnt=prnt))
    toolpath.extend(printPrimeLine(xStart=10, yStart=10, len=10, prnt=prnt))
    toolpath.extend(printPrimeLine(xStart=15, yStart=10, len=10, prnt=prnt))
    # Tool Path Generation
    toolpath = []

    # Spape Fidelity Test
    toolpath.extend(lattice(start_x=10, start_y=40, rows=5, cols=5, spacing=3, prnt=prnt))
    toolpath.extend(capture_print(camera=1, x=17.5, y=0, z=60, prnt=prnt))
    toolpath.extend(contracting_square_wave(start_x=40, start_y=40, height=40, width=5, iterations=5, shrink_rate=0.95, prnt=prnt))
    toolpath.extend(capture_print(camera=1, x=7.5, y=17.5, z=0, prnt=prnt))


    # Striaght Line Test
    toolpath.extend(straight_line(40, 90, 40, 5, 5, prnt))
    toolpath.extend(capture_print(camera=1, x=7.5, y=17.5, z=0, prnt=prnt))
    return toolpath

