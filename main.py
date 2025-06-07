#!/usr/bin/env python3
"""
Example main.py showing how to use the KlipperController
"""

from printer import KlipperController, run_example_sequence
import time

def main():
    # Your Raspberry Pi IP address
    PRINTER_IP = "192.168.1.100"  # Change this to your Pi's IP
    PRINTER_PORT = 7125
    
    print("=== Main.py Klipper Control Demo ===\n")
    
    # Method 1: Use the example sequence function
    print("Method 1: Running the built-in example sequence")
    success = run_example_sequence(PRINTER_IP, PRINTER_PORT)
    
    if not success:
        print("Example sequence failed!")
        return
    
    print("\n" + "="*50 + "\n")
    
    # Method 2: Create your own controller instance for custom control
    print("Method 2: Custom printer control")
    
    # Create controller instance
    printer = KlipperController(PRINTER_IP, PRINTER_PORT)
    
    # Check connection
    if not printer.check_connection():
        print("Failed to connect to printer")
        return
    
    # Custom sequence example
    print("\nStarting custom movement sequence...")
    
    # Move to different positions
    positions = [
        (50, 50),   # Move to center-ish
        (0, 100),   # Move to back-left
        (100, 0),   # Move to front-right
        (10, 10)    # Move back to our target position
    ]
    
    for x, y in positions:
        print(f"\nMoving to X{x} Y{y}...")
        
        # Send movement command
        if printer.send_gcode(f"G1 X{x} Y{y} F3000"):
            # Wait for movement to complete
            printer.wait_for_completion(timeout=30)
            
            # Show current position
            printer.print_position()
            
            # Small delay between moves
            time.sleep(1)
        else:
            print(f"Failed to move to X{x} Y{y}")
            break
    
    # Example of other useful commands
    print("\n=== Other Examples ===")
    
    # Get just the position data without printing
    status = printer.get_printer_status()
    if status:
        result = status.get("result", {}).get("status", {})
        toolhead = result.get("toolhead", {})
        position = toolhead.get("position", [0, 0, 0, 0])
        print(f"Current XY: ({position[0]:.2f}, {position[1]:.2f})")
    
    # Send some other G-code commands
    print("\nSending additional G-code commands...")
    
    # Set absolute positioning mode
    printer.send_gcode("G90")
    
    # Set units to millimeters
    printer.send_gcode("G21")
    
    # Move Z axis up a bit (be careful with Z movements!)
    print("Moving Z axis up 5mm...")
    printer.send_gcode("G1 Z5 F1000")  # Slower speed for Z
    printer.wait_for_completion()
    
    # Show final position
    print("\nFinal position after all movements:")
    printer.print_position()
    
    print("\nCustom control sequence completed!")

def simple_connection_test():
    """Simple function to just test connection"""
    printer = KlipperController("192.168.1.100")  # Update IP
    
    if printer.check_connection():
        print("✓ Connection successful!")
        printer.print_position()
        return True
    else:
        print("✗ Connection failed!")
        return False

def home_and_move_example():
    """Simple home and move function"""
    printer = KlipperController("192.168.1.100")  # Update IP
    
    if not printer.check_connection():
        return False
    
    # Home all axes
    print("Homing...")
    printer.send_gcode("G28")
    printer.wait_for_completion(timeout=120)
    
    # Move to specific position
    print("Moving to X10 Y10...")
    printer.send_gcode("G1 X10 Y10 F3000")
    printer.wait_for_completion()
    
    # Show result
    printer.print_position()
    return True

if __name__ == "__main__":
    # You can call any of these functions:
    
    # Full demo
    main()
    
    # Or just test connection
    # simple_connection_test()
    
    # Or just home and move
    # home_and_move_example()