#!/usr/bin/env python3
"""
Printer Command Line Interface
Controls the MXene printer via command line with immediate connection and homing
"""

import sys
import time
import argparse
from hardware.klipper_controller import KlipperController
from configs import *


class PrinterCLI:
    def __init__(self):
        self.controller = None
        self.connected = False
        
    def connect_and_home(self):
        """Connect to printer and perform homing sequence"""
        print("=" * 60)
        print("🖨️  MXENE PRINTER CLI")
        print("=" * 60)
        
        # Initialize controller
        self.controller = KlipperController()
        
        # Connect to printer
        print("\n🔌 Connecting to printer...")
        if not self.controller.connect():
            print("❌ Failed to connect to printer!")
            print("Please check:")
            print("  1. Moonraker is running (sudo systemctl status moonraker)")
            print("  2. Printer is powered on and connected")
            print("  3. Network connection to printer")
            return False
        
        self.connected = True
        print("✅ Successfully connected to printer!")
        
        # Display current status
        self.controller.print_status()
        
        # Check if already homed
        homed_axes = self.controller.get_homed_axes()
        if homed_axes and len(homed_axes) >= 3:
            print(f"🏠 Printer is already homed on axes: {homed_axes.upper()}")
            return True
        
        # Perform homing
        print("\n🏠 Homing printer...")
        if self.controller.home_axes("XYZ"):
            print("✅ Homing completed successfully!")
            self.controller.print_position()
            return True
        else:
            print("❌ Homing failed!")
            return False
    
    def show_menu(self):
        """Display the main menu"""
        print("\n" + "=" * 40)
        print("PRINTER CONTROL MENU")
        print("=" * 40)
        print("1.  Show printer status")
        print("2.  Move to position")
        print("3.  Home axes")
        print("4.  Send G-code command")
        print("5.  Emergency stop")
        print("6.  Set print profile")
        print("7.  Move to safe position")
        print("8.  Get current position")
        print("9.  Wait for idle")
        print("0.  Exit")
        print("=" * 40)
    
    def move_to_position(self):
        """Move to a specific position"""
        try:
            print("\n📍 Move to position")
            print("Enter coordinates (press Enter to skip):")
            
            x = input("X coordinate: ").strip()
            y = input("Y coordinate: ").strip()
            z = input("Z coordinate: ").strip()
            
            # Convert to float, None if empty
            x = float(x) if x else None
            y = float(y) if y else None
            z = float(z) if z else None
            
            if x is None and y is None and z is None:
                print("❌ No coordinates provided")
                return
            
            feedrate = input("Feedrate (mm/min, default 3000): ").strip()
            feedrate = int(feedrate) if feedrate else 3000
            
            print(f"\n🚀 Moving to X:{x} Y:{y} Z:{z} at {feedrate} mm/min...")
            
            if self.controller.move_to(x=x, y=y, z=z, feedrate=feedrate):
                print("✅ Movement completed!")
                self.controller.print_position()
            else:
                print("❌ Movement failed!")
                
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
        except KeyboardInterrupt:
            print("\n⏹️  Movement cancelled")
    
    def home_axes(self):
        """Home specific axes"""
        print("\n🏠 Home axes")
        print("Options: XYZ, XY, Z, X, Y")
        axes = input("Enter axes to home (default XYZ): ").strip().upper()
        
        if not axes:
            axes = "XYZ"
        
        if self.controller.home_axes(axes):
            print(f"✅ Homed axes: {axes}")
            self.controller.print_position()
        else:
            print(f"❌ Failed to home axes: {axes}")
    
    def send_gcode(self):
        """Send a G-code command"""
        print("\n📝 Send G-code command")
        command = input("Enter G-code command: ").strip()
        
        if not command:
            print("❌ No command provided")
            return
        
        print(f"📤 Sending: {command}")
        if self.controller.send_gcode(command, wait_complete=True):
            print("✅ Command executed successfully!")
        else:
            print("❌ Command failed!")
    
    def set_print_profile(self):
        """Set a print profile"""
        print("\n⚙️  Set print profile")
        print("Available profiles:")
        print("1. PVA Print Profile")
        print("2. MXene Ink Print Profile")
        print("3. MXene Profile 2_20")
        print("4. MXene Profile 2_20_slide")
        print("5. MXene Profile PET 25G")
        print("6. MXene Profile PET 30G")
        print("7. MXene Profile 1pNanoParticles 25G")
        print("8. MXene Profile 2pNanoParticles 25G")
        print("9. MXene Profile 3pNanoParticles 22G")
        
        try:
            choice = input("Select profile (1-9): ").strip()
            profiles = {
                '1': pvaPrintProfile,
                '2': MXeneInkPrintProfile,
                '3': MXeneProfile2_20,
                '4': MXeneProfile2_20_slide,
                '5': MXeneProfile_pet_25G,
                '6': MXeneProfile_pet_30G,
                '7': MXeneProfile_1pNanoParticles_25G,
                '8': MXeneProfile_2pNanoParticles_25G,
                '9': MXeneProfile_3pNanoParticles_22G
            }
            
            if choice in profiles:
                profile = profiles[choice]
                print(f"✅ Selected profile: {choice}")
                print(f"   Extrusion: {profile.extrusion}")
                print(f"   Retraction: {profile.retraction}")
                print(f"   Feed rate: {profile.feed_rate}")
                print(f"   Movement speed: {profile.movement_speed}")
                print(f"   Print height: {profile.print_height}")
                print(f"   Bed height: {profile.bed_height}")
                print(f"   Z hop: {profile.z_hop}")
                print(f"   Line gap: {profile.line_gap}")
                
                # Store the profile for later use
                self.current_profile = profile
            else:
                print("❌ Invalid choice")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def move_to_safe_position(self):
        """Move to a safe position"""
        print("\n🛡️  Moving to safe position...")
        if self.controller.move_to(x=50, y=50, z=10, feedrate=3000):
            print("✅ Moved to safe position (X:50, Y:50, Z:10)")
            self.controller.print_position()
        else:
            print("❌ Failed to move to safe position")
    
    def emergency_stop(self):
        """Emergency stop the printer"""
        print("\n🚨 EMERGENCY STOP!")
        confirm = input("Are you sure? Type 'YES' to confirm: ").strip()
        
        if confirm == "YES":
            self.controller.emergency_stop()
            print("✅ Emergency stop executed!")
        else:
            print("❌ Emergency stop cancelled")
    
    def run(self):
        """Main CLI loop"""
        # Connect and home
        if not self.connect_and_home():
            return
        
        # Main menu loop
        while True:
            try:
                self.show_menu()
                choice = input("\nEnter your choice (0-9): ").strip()
                
                if choice == '0':
                    print("\n👋 Goodbye!")
                    break
                elif choice == '1':
                    self.controller.print_status()
                elif choice == '2':
                    self.move_to_position()
                elif choice == '3':
                    self.home_axes()
                elif choice == '4':
                    self.send_gcode()
                elif choice == '5':
                    self.emergency_stop()
                elif choice == '6':
                    self.set_print_profile()
                elif choice == '7':
                    self.move_to_safe_position()
                elif choice == '8':
                    self.controller.print_position()
                elif choice == '9':
                    print("\n⏳ Waiting for printer to be idle...")
                    if self.controller.wait_for_idle():
                        print("✅ Printer is idle")
                    else:
                        print("❌ Timeout waiting for idle")
                else:
                    print("❌ Invalid choice. Please enter 0-9.")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("Press Enter to continue...")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="MXene Printer CLI")
    parser.add_argument("--no-home", action="store_true", help="Skip automatic homing")
    parser.add_argument("--test", action="store_true", help="Run connection test only")
    
    args = parser.parse_args()
    
    cli = PrinterCLI()
    
    if args.test:
        # Just test connection
        print("🧪 Testing printer connection...")
        if cli.connect_and_home():
            print("✅ Connection test passed!")
        else:
            print("❌ Connection test failed!")
            sys.exit(1)
    else:
        # Run full CLI
        cli.run()


if __name__ == "__main__":
    main() 