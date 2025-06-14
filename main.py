#!/usr/bin/env python3
"""
Main function for automated printer movement sequence
Connects, homes, and moves through specified coordinates
"""

import sys
import time
from klipper_controller import KlipperController

def main():
    """
    Main function that:
    1. Connects to the printer
    2. Homes the printer
    3. Moves to X=30 Y=30
    4. Moves to X=60 Y=30
    5. Moves to X=60 Y=60
    """
    print("Automated Printer Movement Sequence")
    print("===================================")
    
    # Initialize controller (localhost since running on Pi)
    print("Initializing printer controller...")
    controller = KlipperController(host="localhost", port=7125)
    
    # Step 1: Connect to printer
    print("\n1. Connecting to printer...")
    if not controller.connect():
        print("✗ Failed to connect to printer")
        print("Make sure Klipper and Moonraker are running")
        return False
    
    print("✓ Connected successfully")
    
    # Show initial position
    print("\nInitial position:")
    controller.print_position()
    
    # Step 2: Home the printer
    print("\n2. Homing printer...")
    if not controller.home_axes("XYZ"):
        print("✗ Failed to home printer")
        return False
    
    print("✓ Homing completed")
    
    # Show position after homing
    print("\nPosition after homing:")
    controller.print_position()
    
    # Step 3: Move to X=30 Y=30
    print("\n3. Moving to X=30 Y=30...")
    if not controller.move_to(x=30, y=30, feedrate=3000):
        print("✗ Failed to move to X=30 Y=30")
        return False
    
    print("✓ Reached X=30 Y=30")
    controller.print_position()
    
    # Small pause between moves
    time.sleep(1)
    
    # Step 4: Move to X=60 Y=30
    print("\n4. Moving to X=60 Y=30...")
    if not controller.move_to(x=60, y=30, feedrate=3000):
        print("✗ Failed to move to X=60 Y=30")
        return False
    
    print("✓ Reached X=60 Y=30")
    controller.print_position()
    
    # Small pause between moves
    time.sleep(1)
    
    # Step 5: Move to X=60 Y=60
    print("\n5. Moving to X=60 Y=60...")
    if not controller.move_to(x=60, y=60, feedrate=3000):
        print("✗ Failed to move to X=60 Y=60")
        return False
    
    print("✓ Reached X=60 Y=60")
    controller.print_position()
    
    # Movement sequence complete
    print("\n" + "="*50)
    print("✓ MOVEMENT SEQUENCE COMPLETED SUCCESSFULLY!")
    print("Final position:")
    controller.print_position()
    print("="*50)
    
    return True

def main_with_monitoring():
    """
    Alternative main function that includes position monitoring
    """
    print("Automated Movement with Position Monitoring")
    print("==========================================")
    
    controller = KlipperController(host="localhost", port=7125)
    
    # Connect
    if not controller.connect():
        print("✗ Failed to connect to printer")
        return False
    
    # Start position monitoring
    print("Starting position monitoring...")
    controller.start_position_monitoring(interval=0.5)
    
    try:
        # Home
        print("\nHoming printer...")
        controller.home_axes("XYZ")
        time.sleep(2)  # Allow monitoring to show homing complete
        
        # Movement sequence
        movements = [
            (30, 30, "First position"),
            (60, 30, "Second position"), 
            (60, 60, "Final position")
        ]
        
        for x, y, description in movements:
            print(f"\nMoving to {description}: X={x} Y={y}")
            controller.move_to(x=x, y=y, feedrate=3000)
            time.sleep(2)  # Allow monitoring to show completion
        
        print("\n✓ All movements completed!")
        
    except KeyboardInterrupt:
        print("\nMovement interrupted by user")
    finally:
        # Stop monitoring
        controller.stop_position_monitoring()
    
    return True

if __name__ == "__main__":
    try:
        # Check if user wants monitoring version
        if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
            success = main_with_monitoring()
        else:
            success = main()
            
        if success:
            print("\nProgram completed successfully")
            sys.exit(0)
        else:
            print("\nProgram failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
