from configs import *
from .patterns import *
from .comands import *

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
    output.extend(moveZ(5,prnt))
    output.extend(movePrintHead(start_x, start_y-5, 5, prnt))
    output.extend(relative())

    current_width = width
    output.extend(movePrintHead(0, 5, -5, prnt))

    for i in range(iterations):
        output.extend(printY(height, prnt))
        output.extend(printX(current_width, prnt))
        current_width = current_width * shrink_rate

        output.extend(printY(-height, prnt))
        output.extend(printX(current_width, prnt))
        current_width = current_width * shrink_rate

    output.extend(moveZ(10, prnt))
    return output


def layered_FFT(prnt, layer_height, layers, start_x=60, start_y = 50, height = 30 , width=10, iterations=12, shrink_rate = 0.85):
    initilZ = prnt.print_height
    currentLayerHeight = 0

    output = ["",
                "",
                ";Printing Layered FFT"]

    currentLayerHeight = prnt.print_height
    
    
    for layer in range(layers):

        prnt.print_height = currentLayerHeight
        output.extend(printPrimeLine(20, 10, 30, prnt))
        output.extend(contracting_square_wave(start_x, start_y, height, width, iterations, shrink_rate, prnt))
        output.extend(capture_print(camera=1, x=90, y=10, z=60, file_name=f"FFT_{layer+1}", time_lapse=False))

        prnt.print_height += layer_height

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

    for layer in range(layers):
    # Vertical Sections:
        output.extend(printPrimeLine(20, 10, 30, prnt))
        output.extend(absolute())
        output.extend(movePrintHead(start_x, start_y-spacing, 5, prnt))
        output.extend(moveZ(prnt.print_height, prnt))
        output.extend(relative())

        output.extend(printY(5,prnt))

        for i in range(rows):
            if i % 2 == 0:
                output.extend(printY(spacing * cols, prnt))
            else:
                output.extend(printY(-spacing * cols, prnt))
            output.extend(printX(spacing, prnt))
        
        # Adjust layer Height        
        currentLayerHeight += layer_height
        prnt.set_print_height(initialZ + currentLayerHeight)

        # Capture Layer
        #output.extend(capture_print(1, x=65, y=10, z=currentLayerHeight+60, file_name=f"lattice_layer_{layer}_Vertical", time_lapse=False))

        #Wait for user input
        #output.extend(send_message("Continue to next layer"))
        #output.extend(waitForInput())

        # Horizontal Sections:
        output.extend(relative())
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
        prnt.set_print_height(initialZ + currentLayerHeight)

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
    output.extend(moveZ(prnt.print_height+5,prnt))
    output.extend(movePrintHead(start_x, start_y-5, prnt.print_height+5,prnt))

    for line in range(qty):
        output.extend(relative())
        output.extend(movePrintHead(0,5,-5,prnt))

        output.extend(printY(length,prnt))

        output.extend(movePrintHead(0,5,5,prnt))

        output.extend(moveZ(10,prnt))
        
        if line != qty - 1:
            output.extend(movePrintHead(spacing, -length-10,0,prnt))
            output.extend(absolute())
            output.extend(moveZ(prnt.print_height+5,prnt))
    
    output.extend(absolute())
    output.extend(moveZ(60,prnt))
    output.extend(capture_print(1, 90, 10, 60, file_name="straight_line_test", time_lapse=False))
    
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

def FCT(start_x, start_y, start_z, len, prnt):
    output = []


    # Set to absolute positioning
    output.extend(absolute())
    # Move print head Z to 40
    output.extend(moveZ(40, prnt))
    # Move to (5, 10, 40)
    output.extend(movePrintHead(5, 10, 40, prnt))
    # Print 3 prime lines
    output.extend(printPrimeLine(5,10,20,prnt))
    output.extend(printPrimeLine(10,10,30,prnt))
    output.extend(printPrimeLine(15,10,40,prnt))

    # Raise Z
    output.extend(moveZ(45, prnt))
    # Ask to continue
    output.extend(send_message("Prime lines complete. Ready to continue?"))
    output.extend(waitForInput())

    # Set to absolute positioning
    output.extend(absolute())
    # Move Z to start_z + 5
    output.extend(moveZ(start_z + 5, prnt))
    # Move print head to (start_x, start_y - 5, start_z + 5)
    output.extend(movePrintHead(start_x, start_y - 5, start_z + 5, prnt))
    # Set to relative positioning
    output.extend(relative())
    # Move print head: 0 in X, 5 in Y, -5 in Z
    output.extend(movePrintHead(0, 5, -5, prnt))
    # Print in the Y direction for distance len
    output.extend(movePrintHead(0, len, 0, prnt))
    # Move print head: 0 in X, 5 in Y, 5 in Z
    output.extend(movePrintHead(0, 5, 5, prnt))
    # Move Z up 55 (relative)
    output.extend(moveZ(55, prnt))

    return output

