def 3D_lattice(start_x, start_y, rows, cols, spacing, layers, layer_height, prnt):
    output = ["",
                "",
                ";Printing Lattice/Grid",
                f";\tstart_x : {start_x}",
                f";\tstart_y : {start_y}",
                f";\thorizontal_lines : {cols}",
                f";\tvertical_lines : {rows}",
                f";\spacing : {spacing}"]

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