from asyncio import new_event_loop
from re import S
from tkinter import LEFT
from tracemalloc import start
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

def pause(delay):
    output = ["",
              ";Pausing for {delay} seconds",
              f"PASUE, {delay}",
              ""]
    return output

def send_message(message):
    output = ["", "PRINT_MESSAGE", f"{message}", ""]
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

def printCap(cap, prnt, xStart, yStart):
    output = ["",
              "",
              ";Printing Capasitor (double Line no lift)",
              f";\txStart : {xStart}",
              f";\tyStart : {yStart}"]
    #Moving to Start 
    output.extend(absolute())
    output.extend(movePrintHead(xStart, yStart, 10, prnt))
    output.extend(moveZ(prnt.print_height, prnt))
    output.extend(relative())
    #Left Side
    output.extend(printY(cap.stem_len-cap.arm_gap, prnt)) #Stem

    for arm in range (0, cap.arm_count, 1):  # arms
        output.extend(printY(cap.arm_gap - prnt.line_gap/2, prnt))
        output.extend(printX(cap.arm_len, prnt))
        output.extend(printY(prnt.line_gap, prnt))
        output.extend(printX(-cap.arm_len, prnt))

    output.extend(printX(-prnt.line_gap, prnt))
    downTravel = cap.stem_len + (cap.arm_count*(prnt.line_gap))+(cap.arm_count-1)*(cap.arm_gap)
    output.extend(printY(-downTravel, prnt))

    moveZ(prnt.z_hop,prnt)

    #Moving to new Start

    output.extend(absolute())
    output.extend(movePrintHead(xStart + cap.arm_len + cap.gap, yStart, 10, prnt))
    output.extend(moveZ(prnt.print_height, prnt))
    output.extend(relative())
    output.extend(printY(cap.stem_len-(3*cap.arm_gap/2) - prnt.line_gap, prnt))
    for arm in range (0, cap.arm_count, 1):
        output.extend(printY(cap.arm_gap, prnt))
        output.extend(printX(-cap.arm_len, prnt))
        output.extend(printY(prnt.line_gap, prnt))
        output.extend(printX(cap.arm_len, prnt))

    downTravel = cap.stem_len + cap.arm_count*prnt.line_gap + (cap.arm_count-1)*cap.arm_gap - cap.arm_gap/2
    output.extend(printY(-downTravel, prnt))

    output.extend(moveZ(10, prnt))


    return output



def printCap_contact_patch(cap, prnt, xStart, yStart):
    prntPre = prnt
    prntPre.extrusion = prnt.extrusion + 0.005
    
    output = ["",
              "",
              ";Printing Capasitor (double Line no lift)",
              f";\txStart : {xStart}",
              f";\tyStart : {yStart}"]
    #Moving to Start 
    output.extend(absolute())

    output.extend(movePrintHead(xStart, yStart-6, 10, prnt))
    output.extend(moveZ(prnt.print_height, prnt))
    output.extend(relative())
    output.extend(printY(2, prntPre))
    output.extend(absolute())
    output.extend(moveZ(prnt.print_height+2, prnt))
    output.extend(movePrintHead(xStart, yStart, prnt.print_height, prnt))
    output.extend(relative())

    output.extend(printX(-cap.contact_patch_width/2, prnt))
    output.extend(printY(cap.contact_patch_width, prnt))
    output.extend(printX(cap.contact_patch_width, prnt))
    output.extend(printY(-cap.contact_patch_width, prnt))
    output.extend(printX(-cap.contact_patch_width/2, prnt))

    #Left Side
    output.extend(printY(cap.stem_len-cap.arm_gap, prnt)) #Stem

    for arm in range (0, cap.arm_count, 1):  # arms
        output.extend(printY(cap.arm_gap, prnt))
        output.extend(printX(cap.arm_len, prnt))
        output.extend(printY(prnt.line_gap, prnt))
        output.extend(printX(-cap.arm_len, prnt))

    output.extend(printX(-prnt.line_gap, prnt))
    downTravel = cap.stem_len + (cap.arm_count*(prnt.line_gap))+(cap.arm_count-1)*(cap.arm_gap)
    output.extend(printY(-downTravel, prnt))

    movePrintHead(0,-3, 3, prnt) #Lift Nozzle
   

    #Moving to new Start

    output.extend(absolute())
    output.extend(movePrintHead(xStart + cap.arm_len + cap.gap, yStart-6, 10, prnt))
    output.extend(moveZ(prnt.print_height, prnt))

    output.extend(relative())

    output.extend(printY(2, prntPre))

    output.extend(absolute())

    output.extend(moveZ(prnt.print_height+2, prnt))

    output.extend(movePrintHead(xStart + cap.arm_len + cap.gap, yStart, prnt.print_height, prnt))

    output.extend(relative())

    output.extend(printX(-cap.contact_patch_width/2, prnt))
    output.extend(printY(cap.contact_patch_width, prnt))
    output.extend(printX(cap.contact_patch_width, prnt))
    output.extend(printY(-cap.contact_patch_width, prnt))
    output.extend(printX(-cap.contact_patch_width/2, prnt))


    output.extend(printY(cap.stem_len-(3*cap.arm_gap/2)-prnt.line_gap ,prnt))

    for arm in range (0, cap.arm_count, 1):
        output.extend(printY(cap.arm_gap, prnt))
        output.extend(printX(-cap.arm_len, prnt))
        output.extend(printY(prnt.line_gap, prnt))
        output.extend(printX(cap.arm_len, prnt))

    downTravel = cap.stem_len + cap.arm_count*prnt.line_gap + (cap.arm_count-1)*cap.arm_gap - cap.arm_gap/2
    output.extend(printY(-downTravel, prnt))
    output.extend(movePrintHead(0,-3, 3, prnt)) #Lift Nozzle

    return output

def printLayers(cap, prnt, xStart, yStart, xOffset, yOffset):
    prntPre = prnt
    prntPre.extrusion = prnt.extrusion + 0.005     
    prnt.extrusion = prnt.extrusion + 0.001
    xStart = xStart + xOffset
    yStart = yStart + yOffset


    output = [
        f"; Print Layers: cap={cap}, prnt={prnt}, xStart={xStart}, yStart={yStart}, xOffset={xOffset}, yOffset={yOffset}",
        ";",
        ";",
        ";"
    ]

    output.extend(absolute())
    output.extend(movePrintHead(xStart - 5, yStart+ cap.stem_len, 5, prnt)) #move to lefy of the first finger
    output.extend(moveZ(prnt.print_height, prnt))
    #loop
    for i in range(0, cap.arm_count, 1):
        output.extend(relative())
        output.extend(printX(2.5, prntPre))
        output.extend(moveZ(2.5, prnt))
        output.extend(movePrintHead(2.5, 0, -2.5, prnt))

        #Printing Arm 
        output.extend(relative())
        output.extend(printX(cap.arm_len, prnt))
        output.extend(printY(prnt.line_gap, prnt))
        output.extend(printX(-cap.arm_len, prnt))
        output.extend(movePrintHead(-5, 0, 5, prnt))

        
        if i < cap.arm_count - 1:  # moving to the next arm
            output.extend(moveY(cap.arm_gap, prnt))
            output.extend(absolute())
            output.extend(moveZ(prnt.print_height, prnt))

        else:
            output.extend(moveZ(5, prnt))

    output.extend(absolute())
    output.extend(movePrintHead(xStart+cap.arm_len + cap.gap + 5, yStart+cap.stem_len-(cap.arm_gap/2)-prnt.line_gap, prnt.print_height, prnt))
    
    for i in range(0, cap.arm_count, 1):
        output.extend(relative())
        output.extend(printX(-2, prntPre))
        output.extend(moveZ(2, prnt))
        output.extend(movePrintHead(-3, 0, -2, prnt))

        #Printing Arm 
        output.extend(relative())
        output.extend(printX(-cap.arm_len, prnt))
        output.extend(printY(prnt.line_gap, prnt))
        output.extend(printX(cap.arm_len, prnt))
        output.extend(movePrintHead(5, 0, 5, prnt))

        
        if i < cap.arm_count - 1:  # moving to the next arm
            output.extend(moveY(cap.arm_gap, prnt))
            output.extend(absolute())
            output.extend(moveZ(prnt.print_height, prnt))
        else:
            output.extend(moveZ(5, prnt))

    return output

def singleLineCap(cap, prnt, layers, layer_height, delay, xStart, yStart):
    output = ["",
              "",
              ";Printing Capasitor (single Line)",
              f";\txStart : {xStart}",
              f";\tyStart : {yStart}"]
    
    #Moving to Start 
    output.extend(absolute())
    output.extend(movePrintHead(xStart, yStart, 10, prnt))
    output.extend(moveZ(prnt.print_height, prnt))
    output.extend(relative())
    
    #Left Side
    output.extend(printY(cap.stem_len + (cap.arm_count-1)*cap.arm_gap, prnt))

    for arm in range (0, cap.arm_count, 1):
        output.extend(printX(cap.arm_len, prnt))
        output.extend(moveZ(2, prnt))
        output.extend(movePrintHead(-cap.arm_len, -cap.arm_gap, -2, prnt))

    output.extend(moveZ(10, prnt))
    output.extend(absolute())
    output.extend(movePrintHead(xStart + cap.arm_len + cap.arm_gap, yStart, prnt.print_height, prnt))
    output.extend(relative())
    output.extend(printY(cap.stem_len + (cap.arm_count-1/2)*cap.arm_gap, prnt))

    for arm in range (0, cap.arm_count, 1):
        output.extend(printX(-cap.arm_len, prnt))
        output.extend(moveZ(2, prnt))
        output.extend(movePrintHead(cap.arm_len, -cap.arm_gap, -2, prnt))

    output.extend(moveZ(10, prnt))

    if layers == 1:
        return output
    
    else:
        for layer in range(1, layers, 1):
            output.extend(pause(delay))
            output.extend(absolute())
            output.extend(movePrintHead(xStart, yStart + cap.stem_len + (cap.arm_count-1)*cap.arm_gap, 10, prnt))
            output.extend(moveZ(prnt.print_height + layer_height * (layer + 1), prnt))
            output.extend(relative())

            for arm in range (0, cap.arm_count, 1):
                output.extend(printX(cap.arm_len, prnt))
                output.extend(moveZ(2, prnt))
                output.extend(movePrintHead(-cap.arm_len, -cap.arm_gap, -2, prnt))    
            
            output.extend(absolute())
            output.extend(movePrintHead(xStart + cap.arm_len + cap.arm_gap, yStart + cap.stem_len + (cap.arm_count-1/2)*cap.arm_gap, 10, prnt))
            output.extend(moveZ(prnt.print_height + layer_height * (layer + 1), prnt))
            output.extend(relative())

            for arm in range (0, cap.arm_count, 1):
                output.extend(printX(-cap.arm_len, prnt))
                output.extend(moveZ(2, prnt))
                output.extend(movePrintHead(cap.arm_len, -cap.arm_gap, -2, prnt))
        return output

def singleLineCap_left(cap, prnt, layers, layer_height, delay, xStart, yStart):
    output = ["",
              "",
              ";Printing Capasitor (single Line - left)",
              f";\txStart : {xStart}",
              f";\tyStart : {yStart}",
              f";\tLayers: {layers}",
              f";\tLayer Height: {layer_height}",
              f";\tDelay: {delay}",
              f";\tPrinter: {prnt}",
              f";\tExtrusion Rate: {prnt.extrusion}"]
    
    #Moving to Start 
    output.extend(absolute())
    output.extend(movePrintHead(xStart, yStart, 10, prnt))
    output.extend(moveZ(prnt.print_height, prnt))
    output.extend(relative())
    
    #Left Side
    output.extend(printY(cap.stem_len + (cap.arm_count-1)*cap.arm_gap, prnt))

    for arm in range (0, cap.arm_count, 1):
        output.extend(printX(cap.arm_len, prnt))
        output.extend(retract(prnt))
        output.extend(moveZ(2, prnt))
        output.extend(movePrintHead(-cap.arm_len, -cap.arm_gap, -2, prnt))
    output.extend(retract(prnt))
    output.extend(moveZ(10, prnt))

    if layers == 1:
        return output
    
    else:
        for layer in range(1, layers, 1):
            output.extend(pause(delay))
            output.extend(absolute())
            output.extend(movePrintHead(xStart, yStart + cap.stem_len + (cap.arm_count-1)*cap.arm_gap, 10, prnt))
            output.extend(moveZ(prnt.print_height + layer_height * (layer + 1), prnt))
            output.extend(relative())

            for arm in range (0, cap.arm_count, 1):
                output.extend(printX(cap.arm_len, prnt))
                output.extend(retract(prnt))
                output.extend(moveZ(2, prnt))
                output.extend(movePrintHead(-cap.arm_len, -cap.arm_gap, -2, prnt))    
        
        output.extend(moveZ(10, prnt))
        return output
    
def singleLineCap_right(cap, prnt, layers, layer_height, delay, xStart, yStart):
    output = ["",
              "",
              ";Printing Capasitor (single Line - right)",
              f";\txStart : {xStart}",
              f";\tyStart : {yStart}",
              f";\tLayers: {layers}",
              f";\tLayer Height: {layer_height}",
              f";\tDelay: {delay}",
              f";\tPrinter: {prnt}",
              f";\tExtrusion Rate: {prnt.extrusion}"]
    
    #Moving to Start 
    output.extend(absolute())
    output.extend(movePrintHead(xStart + cap.arm_len + cap.arm_gap, yStart, 10, prnt))
    output.extend(moveZ(prnt.print_height, prnt))
    output.extend(relative())

    output.extend(printY(cap.stem_len + (cap.arm_count-1/2)*cap.arm_gap, prnt))

    for arm in range (0, cap.arm_count, 1):
        output.extend(printX(-cap.arm_len, prnt))
        output.extend(retract(prnt))
        output.extend(moveZ(2, prnt))
        output.extend(movePrintHead(cap.arm_len, -cap.arm_gap, -2, prnt))

    output.extend(moveZ(10, prnt))

    if layers == 1:
        return output
    
    else:
        for layer in range(1, layers, 1):
            output.extend(pause(delay))
            output.extend(absolute())    
            output.extend(movePrintHead(xStart + cap.arm_len + cap.arm_gap, yStart + cap.stem_len + (cap.arm_count-1/2)*cap.arm_gap, 10, prnt))
            output.extend(moveZ(prnt.print_height + layer_height * (layer + 1), prnt))
            output.extend(relative())

            for arm in range (0, cap.arm_count, 1):
                output.extend(printX(-cap.arm_len, prnt))
                output.extend(retract(prnt))
                output.extend(moveZ(2, prnt))
                output.extend(movePrintHead(cap.arm_len, -cap.arm_gap, -2, prnt))
        return output
def square_wave(start_x, start_y, height, width, iterations, prnt):
    output = ["",
                "",
                ";Printing Square Wave",
                f";\tstart_x : {start_x}",
                f";\tstart_y : {start_y}",
                f";\theight : {height}",
                f";\twidth : {width}",
                f";\titerations : {iterations}"]

    output.extend(absolute())
    output.extend(movePrintHead(start_x, start_y, prnt.print_height, prnt))
    output.extend(relative())

    for i in range(iterations):
        output.extend(printY(height, prnt))
        output.extend(printX(width, prnt))
        output.extend(printY(-height, prnt))
        output.extend(printX(width, prnt))

    output.extend(moveZ(10, prnt))
    return output

def contracting_square_wave(start_x, start_y, height, width, iterations, shrink_rate, prnt):
    output = ["",
                "",
                ";Printing Contracting Square Wave",
                f";\tstart_x : {start_x}",
                f";\tstart_y : {start_y}",
                f";\theight : {height}",
                f";\twidth : {width}",
                f";\titerations : {iterations}",
                f";\tshrink_rate : {shrink_rate}"]

    output.extend(absolute())
    output.extend(movePrintHead(start_x, start_y-5, 10, prnt))
    output.extend(moveZ(prnt.print_height, prnt))
    output.extend(relative())

    current_width = width
    output.extend(printY(5, prnt))

    for i in range(iterations):
        output.extend(printY(height, prnt))
        output.extend(printX(current_width, prnt))
        current_width = current_width * shrink_rate

        output.extend(printY(-height, prnt))
        output.extend(printX(current_width, prnt))
        current_width = current_width * shrink_rate

    output.extend(moveZ(10, prnt))
    return output

def layered_FFT(prnt, start_x=60, start_y = 50, height = 30 , width=5, iterations=12, shrink_rate = 0.9, layer_height = 0.5, layers=5):
    initilZ = prnt.print_height
    currentLayerHeight = 0

    output = ["",
                "",
                ";Printing Layered FFT"]
    
    output.extend(absolute())
    output.extend(moveZ(5, prnt))
    output.extend(movePrintHead(start_x, start_y-10, 5+initilZ, prnt))

    output.extend(relative())
    output.extend(movePrintHead(0, 5, -5, prnt))
    output.extend(printY(5, prnt))

    for layer in range(layers):

        for i in range(iterations):
            output.extend(printY(height, prnt))
            output.extend(printX(width, prnt))
            height = height * shrink_rate
            output.extend(printY(-height, prnt))
            output.extend(printX(width, prnt))
            height = height * shrink_rate

        # Adjust layer Height
        currentLayerHeight += layer_height
        prnt.set_print_height(initilZ + currentLayerHeight)

        # Capture Layer
        output.extend(capture_print(1, x=65, y=10, z=currentLayerHeight+60, file_name=f"layered_FFT_layer_{layer}", time_lapse=False))

        # Wait for user input
        if layer != layers - 1:
            output.extend(send_message("Continue to next layer"))
            output.extend(waitForInput())

    output.extend(moveZ(60, prnt))
    output.extend(movePrintHead(65, 10, 60, prnt))


    return output


def lattice(start_x, start_y, rows, cols, spacing, prnt):
    output = ["",
                "",
                ";Printing Lattice/Grid",
                f";\tstart_x : {start_x}",
                f";\tstart_y : {start_y}",
                f";\thorizontal_lines : {cols}",
                f";\tvertical_lines : {rows}",
                f";\tspacing : {spacing}"]

    output.extend(absolute())
    output.extend(movePrintHead(start_x, start_y-spacing, 5, prnt))
    output.extend(moveZ(prnt.print_height, prnt))
    output.extend(relative())

    output.extend(printY(5,prnt))
    # Vertical Sections:
    for i in range(rows):
        if i % 2 == 0:
            output.extend(printY(spacing * cols, prnt))
        else:
            output.extend(printY(-spacing * cols, prnt))
        output.extend(printX(spacing, prnt))
    # Horizontal Sections:
    if rows % 2 == 0:
        output.extend(printY(spacing * cols, prnt))

        for i in range(cols):
            if i % 2 == 0:
                output.extend(printX(-spacing * rows, prnt))
                output.extend(printY(-spacing, prnt))
            else:
                output.extend(printX(spacing * rows, prnt))
                output.extend(printY(-spacing, prnt))
        output.extend(printX(-5-spacing-spacing*cols, prnt))

    else:
        output.extend(printY(-spacing * cols, prnt))

        for i in range(cols):
            if i % 2 == 0:
                output.extend(printX(-spacing * rows, prnt))
                output.extend(printY(spacing, prnt))
            else:
                output.extend(printX(spacing * rows, prnt))
                output.extend(printY(spacing, prnt))

        output.extend(printX(5+cols*spacing, prnt))

    return output

def lattice_3d(prnt, start_x=60, start_y=50, rows=5, cols=5, spacing=3, layers=5, layer_height= 0.5):
    
    initialZ = prnt.print_height
    currentLayerHeight = 0

    output = ["",
                "",
                ";Printing Lattice/Grid",
                f";\tstart_x : {start_x}",
                f";\tstart_y : {start_y}",
                f";\thorizontal_lines : {cols}",
                f";\tvertical_lines : {rows}",
                f";\tspacing : {spacing}"]
    # Moving to Start

    output.extend(absolute())
    output.extend(movePrintHead(start_x, start_y-spacing, 5, prnt))
    output.extend(moveZ(prnt.print_height, prnt))
    output.extend(relative())

    output.extend(printY(5,prnt))
    for layer in range(layers):
    # Vertical Sections:
        for i in range(rows):
            if i % 2 == 0:
                output.extend(printY(spacing * cols, prnt))
            else:
                output.extend(printY(-spacing * cols, prnt))
            output.extend(printX(spacing, prnt))
        
        # Adjust layer Height        
        currentLayerHeight += layer_height
        prnt.setPrintHeight(initialZ + currentLayerHeight)

        # Capture Layer
        output.extend(capture_print(1, x=65, y=10, z=currentLayerHeight+60, file_name=f"lattice_layer_{layer}_Vertical", time_lapse=False))

        #Wait for user input
        output.extend(send_message("Continue to next layer"))
        output.extend(waitForInput())

        # Horizontal Sections:
        if rows % 2 == 0:
            output.extend(printY(spacing * cols, prnt))

            for i in range(cols):
                if i % 2 == 0:
                    output.extend(printX(-spacing * rows, prnt))
                    output.extend(printY(-spacing, prnt))
                else:
                    output.extend(printX(spacing * rows, prnt))
                    output.extend(printY(-spacing, prnt))
            output.extend(printX(-5-spacing-spacing*cols, prnt))

        else:
            output.extend(printY(-spacing * cols, prnt))

            for i in range(cols):
                if i % 2 == 0:
                    output.extend(printX(-spacing * rows, prnt))
                    output.extend(printY(spacing, prnt))
                else:
                    output.extend(printX(spacing * rows, prnt))
                    output.extend(printY(spacing, prnt))

            output.extend(printX(5+cols*spacing, prnt))
     
        # Adjust layer Height        
        currentLayerHeight += layer_height
        prnt.setPrintHeight(initialZ + currentLayerHeight)

        # Capture Layer
        output.extend(capture_print(1, x=65, y=10, z=currentLayerHeight+60, file_name= f"lattice_layer_{layer}_Horizontal", time_lapse=False))

        #Wait for user input
        if layer != layers-1:  # No need to wait after the last layer
            output.extend(send_message("Continue to next layer"))
            output.extend(waitForInput())

    # Final Move
    output.extend(absolute())
    output.extend(moveZ(60, prnt))
    output.extend(movePrintHead(65, 10, 60, prnt))

    return output


# Stright Line Test

def straight_line(prnt, start_x=60, start_y=50, length=40, qty=5, spacing=5):

    output = []

    output.extend(absolute())
    output.extend(moveZ(15,prnt))
    output.extend(movePrintHead(start_x, start_y-5, prnt.print_height+5,prnt))

    for line in range(qty):
        output.extend(relative())
        output.extend(movePrintHead(0,5,-5,prnt))

        output.extend(printY(length,prnt))
        output.extend(movePrintHead(0,5,5,prnt))

        output.extend(moveZ(10,prnt))
        
        if line != qty - 1:
            output.extend(movePrintHead(spacing, -length,0,prnt))
            output.extend(absolute())
            output.extend(moveZ(prnt.print_height+5,prnt))
    
    output.extend(absolute())
    output.extend(moveZ(60,prnt))
    output.extend(movePrintHead(70,15,60,prnt))
    
    return output
    

def straigtLineRoutine(prnt, start_x=60, start_y=50, length=40, qty=5, spacing=5, sheerRates=None):
    output = []
    if sheerRates is None:
        sheerRates = [0.1,0.2,0.5,1,2,5,10,20,50,100,200,500]
   
    def calcParamiters(rates):

        return prnt.extrussion,prnt.feed_rate

    for rate in sheerRates:
        newe, newf = calcParamiters(rate)
        prnt.extrusion = newe
        prnt.feed_rate = newf

        output.extend(straight_line(prnt))
        output.extend(capture_print(1,start_x, 0, 60, f"staigt_line_rate{rate}"))
        output.extend(send_message( "Please Clean Print Surface" ))
        output.extend(send_message( "Ready to Continue" ))
        output.extend(waitForInput())

    return output

def massFlowTest(prnt, Feedrates):
    output = []
    
    if Feedrates is None:
        Feedrates = [0.1,0.2,0.5,1,2,5,10,20,50,100,200,500]
   
   
    def extrudeOnly(E,F):
        return [f"G1 E{E} F{F}"]
         
    for rate in Feedrates:
        E = 35
        output.extend(extrudeOnly(E, rate))
        output.extend(waitForInput())
    
    return output




def ZB2_test(start_x, start_y, length, qty, spacing, prnt):
    output = ["", "", ";3D ZB2 Test",
              f";\tstart_x : {start_x}",
              f";\tstart_y : {start_y}",
              f";\tlength : {length}",
              f";\tqty : {qty}"]
    
    output.extend(absolute())
    output.extend(movePrintHead(start_x, start_y-5, 5+prnt.print_height, prnt))

    for i in range(qty):
        output.extend(relative())
        output.extend(movePrintHead(0, 5, -5, prnt, extrusion=True))
        output.extend(printY(length, prnt))
        output.extend(movePrintHead(0, 5, 5, prnt, extrusion=False))
        output.extend(movePrintHead(spacing, -5, -5, prnt, extrusion=True))
        output.extend(printY(-length, prnt))
        output.extend(movePrintHead(spacing, -5, -5, prnt, extrusion=True))

    return output







