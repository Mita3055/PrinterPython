#!/usr/bin/env python3
"""
Klipper Printer Control Script for Ender 5 S1
Connects to Klipper via Moonraker API to control printer movements
"""

import requests
import json
import time
import sys

class KlipperController:
    def __init__(self, host="192.168.1.100", port=7125):
        """
        Initialize Klipper controller
        
        Args:
            host (str): IP address of the Raspberry Pi running Klipper
            port (int): Moonraker API port (default: 7125)
        """
        self.base_url = f"http://{host}:{port}"
        self.api_url = f"{self.base_url}/printer"
        
    def send_gcode(self, gcode_command):
        """
        Send G-code command to Klipper
        
        Args:
            gcode_command (str): G-code command to send
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}/printer/gcode/script"
            data = {"script": gcode_command}
            
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            
            print(f"Sent G-code: {gcode_command}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Error sending G-code '{gcode_command}': {e}")
            return False
    
    def get_printer_status(self):
        """
        Get current printer status including position
        
        Returns:
            dict: Printer status information
        """
        try:
            url = f"{self.base_url}/printer/objects/query"
            params = {
                "toolhead": "position,homed_axes",
                "extruder": "position"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting printer status: {e}")
            return None
    
    def wait_for_completion(self, timeout=60):
        """
        Wait for printer to complete current operations
        
        Args:
            timeout (int): Maximum time to wait in seconds
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                url = f"{self.base_url}/printer/objects/query"
                params = {"print_stats": "state"}
                
                response = requests.get(url, params=params, timeout=5)
                response.raise_for_status()
                
                data = response.json()
                state = data.get("result", {}).get("status", {}).get("print_stats", {}).get("state", "")
                
                if state in ["ready", "standby"]:
                    return True
                    
                time.sleep(1)
                
            except requests.exceptions.RequestException:
                time.sleep(1)
                continue
        
        print("Warning: Timeout waiting for printer to complete operations")
        return False
    
    def print_position(self):
        """Print current X, Y, Z, and extruder positions"""
        status = self.get_printer_status()
        
        if status:
            result = status.get("result", {}).get("status", {})
            toolhead = result.get("toolhead", {})
            extruder = result.get("extruder", {})
            
            position = toolhead.get("position", [0, 0, 0, 0])
            extruder_pos = extruder.get("position", 0)
            homed_axes = toolhead.get("homed_axes", "")
            
            print("\n=== Current Printer Position ===")
            print(f"X: {position[0]:.3f} mm")
            print(f"Y: {position[1]:.3f} mm") 
            print(f"Z: {position[2]:.3f} mm")
            print(f"Extruder: {extruder_pos:.3f} mm")
            print(f"Homed axes: {homed_axes}")
            print("================================\n")
        else:
            print("Failed to get printer position")
    
    def check_connection(self):
        """
        Check if we can connect to the printer
        
        Returns:
            bool: True if connected, False otherwise
        """
        try:
            url = f"{self.base_url}/printer/info"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            print(f"Connected to Klipper - State: {data.get('result', {}).get('state', 'unknown')}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Connection failed: {e}")
            return False

def run_example_sequence(printer_ip="192.168.1.100", printer_port=7125):
    """
    Example function that demonstrates the full printer control sequence
    
    Args:
        printer_ip (str): IP address of the Raspberry Pi
        printer_port (int): Moonraker API port
    """
    print("Klipper Printer Control Script")
    print("==============================")
    
    # Initialize controller
    klipper = KlipperController(printer_ip, printer_port)
    
    # Check connection
    print("Checking connection to printer...")
    if not klipper.check_connection():
        print("Failed to connect to printer. Please check:")
        print("1. Raspberry Pi IP address is correct")
        print("2. Moonraker is running on the Pi")
        print("3. Network connectivity")
        return False
    
    print("\nStarting printer control sequence...")
    
    # Home all axes
    print("Homing all axes...")
    if not klipper.send_gcode("G28"):
        print("Failed to send homing command")
        return False
    
    # Wait for homing to complete
    print("Waiting for homing to complete...")
    klipper.wait_for_completion(timeout=120)  # Homing can take a while
    
    # Print position after homing
    print("Position after homing:")
    klipper.print_position()
    
    # Move to X10 Y10 using linear movement
    print("Moving to X10 Y10...")
    move_command = "G1 X10 Y10 F3000"  # F3000 = 3000mm/min feedrate
    
    if not klipper.send_gcode(move_command):
        print("Failed to send movement command")
        return False
    
    # Wait for movement to complete
    print("Waiting for movement to complete...")
    klipper.wait_for_completion(timeout=30)
    
    # Print final position
    print("Final position:")
    klipper.print_position()
    
    print("Printer control sequence completed successfully!")
    return True

def main():
    """Main function for standalone execution"""
    # Configuration - Update this IP address to match your Raspberry Pi
    PRINTER_IP = "192.168.1.100"  # Change this to your Pi's IP address
    PRINTER_PORT = 7125
    
    run_example_sequence(PRINTER_IP, PRINTER_PORT)

if __name__ == "__main__":
    main()