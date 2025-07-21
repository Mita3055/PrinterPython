from configs import *
from .comands import *

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

