from configs import *
import math

# G Code Commands

def movePrintHead(x_move, y_move, z_move, prnt, extrusion=False):
    if extrusion:
        output = [f"G1 X{x_move} Y{y_move} Z{z_move} E{-prnt.extrusion*abs(math.sqrt(x_move**2 + y_move**2)):f} F{prnt.feed_rate}"]
    else:
        output = [f"G1 X{x_move} Y{y_move} Z{z_move} F{prnt.movement_speed} "]
    return output

def retract(prnt):
    output = [f"G1 E{prnt.retraction}"]
    return output

def printX(x_move, prnt):
    output = [f"G1 X{x_move} E{-prnt.extrusion*abs(x_move):f} F{prnt.feed_rate}"]
    return output

def printY(y_move, prnt):
    output = [f"G1 Y{y_move} E{-prnt.extrusion*abs(y_move):f} F{prnt.feed_rate}"]
    return output

def moveX(x_move, prnt):
    output = [f"G1 X{x_move} F{prnt.movement_speed}"]
    return output

def moveY(y_move, prnt):
    output = [f"G1 Y{y_move} F{prnt.movement_speed}"]
    return output

def moveZ(z_move, prnt):
    output = [f"G1 Z{z_move} F{prnt.movement_speed}"]
    return output
def absolute():
    output = [f"G90; Absolute Cordinates"]
    return output

def relative():
    output = [f"G91; Relative Cordinates"]
    return output

def home():
    output = ["G28"]
    return output

def preExtrussion(prnt):
    output = [f"G1 E{prnt.preExtrussionE} F{prnt.preExtrussionF}"]
    return output



def pause(delay):
    output = ["",
              ";Pausing for {delay} seconds",
              f"PASUE, {delay}",
              ""]
    return output

def send_message(message):
    output = ["", f"PRINT_MESSAGE, {message}", ""]
    return output

def waitForInput():
    output = ["","WAIT",""]
    return output


def capture_print(camera, x, y, z, file_name=None, time_lapse=False, time_lapse_interval=30, time_lapse_duration=1800):
    if time_lapse is None or time_lapse == False:
            output = ["",
              ";Capturing Immage",
              f"CAPTURE,  {camera}, {x}, {y}, {z}, {file_name}, {time_lapse}",
              ""]
    else:
        output = ["",
              ";Capturing Time Lapse",
              f"CAPTURE,  {camera}, {x}, {y}, {z}, {file_name}, {time_lapse} , {time_lapse_interval}, {time_lapse_duration}",
              ""]
    return output


def motorOff():
    output = ["M84"]
    return output


# Pattern Print Commands

def printPrimeLine(xStart, yStart, len, prnt):
    output = ["",
              "",
              ";Printing Priming Line ",
              f";\txStart : {xStart}",
              f";\tyStart : {yStart}"]

    output.extend(absolute())
    output.extend(movePrintHead(xStart, yStart, 10, prnt))
    output.extend(moveZ(prnt.bed_height, prnt))
    output.extend(relative())
    output.extend(printY(len,prnt)) 


    return output


def primeRoutine(prnt, x_start=5, y_start=10):

    output = ["",
              ";Starting Prime Routine:"
              ";Prime Routine: Detailed xStart/yStart Information",
              f";\tx_start : {x_start}",
              f";\ty_start : {y_start}",
              ]

    output.extend(printPrimeLine(x_start, y_start, len=10, prnt=prnt))

    new_x = x_start+5
    output.extend(printPrimeLine(new_x, y_start,20, prnt))

    new_x = x_start+5
    output.extend(printPrimeLine(new_x, y_start,30, prnt))

    output.extend(moveZ(10, prnt))

    return output





