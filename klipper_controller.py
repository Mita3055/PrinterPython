#!/usr/bin/env python3
"""
Simplified Klipper/Moonraker Printer Controller for Raspberry Pi
Focus: Homing, Linear Movement, and Continuous Position Monitoring
"""

import requests
import json
import time
import sys
import argparse
import threading
from typing import Optional, Tuple
import signal

class PrinterError(Exception):
    """Custom exception for printer-related errors"""
    pass

class KlipperController:
    """Simplified controller class for Klipper/Moonraker interface"""
    
    def __init__(self, host="localhost", port=7125, timeout=10):
        """
        Initialize the Klipper controller
        
        Args:
            host (str): Moonraker host (localhost for local Pi)
            port (int): Moonraker port
            timeout (int): Request timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{host}:{port}"
        self.connected = False
        self.printer_info = {}
        self.monitoring = False
        self.monitor_thread = None
        
    def connect(self) -> bool:
        """
        Establish connection to the printer
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/printer/info", timeout=self.timeout)
            response.raise_for_status()
            
            self.printer_info = response.json().get('result', {})
            self.connected = True
            
            print(f"✓ Connected to {self.printer_info.get('hostname', 'Unknown')}")
            print(f"  Klipper version: {self.printer_info.get('software_version', 'Unknown')}")
            print(f"  State: {self.printer_info.get('state', 'Unknown')}")
            
            # Turn off heaters immediately upon connection
            self.turn_off_heaters()
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Connection failed: {e}")
            self.connected = False
            return False
    
    def turn_off_heaters(self):
        """Turn off all heaters (safety measure)"""
        try:
            self.send_gcode("M104 S0", silent=True)  # Turn off hotend
            self.send_gcode("M140 S0", silent=True)  # Turn off bed
            print("✓ Heaters set to 0°C")
        except:
            pass  # Ignore errors for safety commands
    
    def send_gcode(self, command: str, wait_complete: bool = False, silent: bool = False) -> bool:
        """
        Send G-code command to printer
        
        Args:
            command (str): G-code command
            wait_complete (bool): Wait for command completion
            silent (bool): Don't print command output
            
        Returns:
            bool: True if successful
        """
        if not self.connected:
            if not silent:
                print("Error: Not connected to printer")
            return False
            
        try:
            url = f"{self.base_url}/printer/gcode/script"
            data = {"script": command}
            
            response = requests.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            
            if not silent:
                print(f"→ {command}")
            
            if wait_complete:
                self.wait_for_idle()
                
            return True
            
        except requests.exceptions.RequestException as e:
            if not silent:
                print(f"✗ Failed to send '{command}': {e}")
            return False
    
    def get_position(self) -> Optional[Tuple[float, float, float, float]]:
        """
        Get current toolhead position
        
        Returns:
            Tuple: (X, Y, Z, E) positions or None if failed
        """
        if not self.connected:
            return None
            
        try:
            url = f"{self.base_url}/printer/objects/query"
            params = {"toolhead": "position,homed_axes"}
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json().get('result', {}).get('status', {})
            toolhead = result.get('toolhead', {})
            
            if 'position' in toolhead:
                pos = toolhead['position'][:4]  # X, Y, Z, E
                return tuple(pos)
                
        except requests.exceptions.RequestException:
            pass
            
        return None
    
    def get_homed_axes(self) -> str:
        """
        Get which axes are currently homed
        
        Returns:
            str: String containing homed axes (e.g., "xyz")
        """
        if not self.connected:
            return ""
            
        try:
            url = f"{self.base_url}/printer/objects/query"
            params = {"toolhead": "homed_axes"}
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json().get('result', {}).get('status', {})
            return result.get('toolhead', {}).get('homed_axes', "")
            
        except requests.exceptions.RequestException:
            return ""
    
    def wait_for_idle(self, timeout: int = 300) -> bool:
        """
        Wait for printer to become idle
        
        Args:
            timeout (int): Maximum wait time in seconds
            
        Returns:
            bool: True if idle, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                url = f"{self.base_url}/printer/objects/query"
                params = {"print_stats": "state"}
                
                response = requests.get(url, params=params, timeout=5)
                response.raise_for_status()
                
                result = response.json().get('result', {}).get('status', {})
                state = result.get('print_stats', {}).get('state', '')
                
                if state in ['ready', 'standby'] or state == '':
                    return True
                    
            except requests.exceptions.RequestException:
                pass
                
            time.sleep(0.5)
            
        print(f"⚠ Timeout waiting for idle state")
        return False
    
    def home_axes(self, axes: str = "XYZ") -> bool:
        """
        Home specified axes
        
        Args:
            axes (str): Axes to home (e.g., "XYZ", "XY", "Z")
            
        Returns:
            bool: True if successful
        """
        if axes.upper() == "XYZ" or axes.upper() == "ALL":
            command = "G28"
        else:
            axis_list = " ".join([f"{axis.upper()}" for axis in axes.upper() if axis in "XYZ"])
            if not axis_list:
                print("Error: Invalid axes specified")
                return False
            command = f"G28 {axis_list}"
            
        print(f"Homing axes: {axes}")
        return self.send_gcode(command, wait_complete=True)
    
    def move_to(self, x=None, y=None, z=None, feedrate=3000) -> bool:
        """
        Move to specified coordinates using linear movement
        
        Args:
            x, y, z (float): Target coordinates (None to keep current)
            feedrate (int): Movement speed in mm/min
            
        Returns:
            bool: True if successful
        """
        coords = []
        if x is not None:
            coords.append(f"X{x}")
        if y is not None:
            coords.append(f"Y{y}")
        if z is not None:
            coords.append(f"Z{z}")
            
        if not coords:
            print("Error: No coordinates specified")
            return False
            
        command = f"G1 {' '.join(coords)} F{feedrate}"
        return self.send_gcode(command, wait_complete=True)
    
    def print_position(self, show_homed=True):
        """Print current position"""
        pos = self.get_position()
        if pos:
            homed = self.get_homed_axes() if show_homed else ""
            homed_status = f" (Homed: {homed.upper()})" if homed else " (Not homed)"
            print(f"Position: X:{pos[0]:.3f} Y:{pos[1]:.3f} Z:{pos[2]:.3f} E:{pos[3]:.3f}{homed_status}")
        else:
            print("Failed to get position")
    
    def start_position_monitoring(self, interval=1.0):
        """
        Start continuous position monitoring in background thread
        
        Args:
            interval (float): Update interval in seconds
        """
        if self.monitoring:
            print("Position monitoring already running")
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._position_monitor, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        print(f"✓ Started position monitoring (interval: {interval}s)")
    
    def stop_position_monitoring(self):
        """Stop continuous position monitoring"""
        if self.monitoring:
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=2)
            print("✓ Stopped position monitoring")
    
    def _position_monitor(self, interval):
        """Internal position monitoring loop"""
        last_pos = None
        
        while self.monitoring and self.connected:
            try:
                current_pos = self.get_position()
                
                if current_pos and current_pos != last_pos:
                    timestamp = time.strftime("%H:%M:%S")
                    homed = self.get_homed_axes()
                    homed_status = f"[{homed.upper()}]" if homed else "[---]"
                    
                    print(f"{timestamp} {homed_status} X:{current_pos[0]:.3f} Y:{current_pos[1]:.3f} Z:{current_pos[2]:.3f} E:{current_pos[3]:.3f}")
                    last_pos = current_pos
                
                time.sleep(interval)
                
            except Exception as e:
                if self.monitoring:  # Only print error if we're supposed to be monitoring
                    print(f"Monitor error: {e}")
                time.sleep(interval)
    
    def emergency_stop(self):
        """Emergency stop the printer"""
        print("🚨 EMERGENCY STOP ACTIVATED!")
        self.send_gcode("M112")

class PrinterCLI:
    """Command line interface for the simplified printer controller"""
    
    def __init__(self):
        self.controller = KlipperController()
        self.running = True
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\nShutting down...")
        self.controller.stop_position_monitoring()
        self.running = False
        sys.exit(0)
    
    def run_interactive(self):
        """Run interactive command line interface"""
        print("Simplified Klipper Controller")
        print("Movement & Position Monitoring Only")
        print("==================================")
        
        if not self.controller.connect():
            print("Failed to connect to printer. Exiting.")
            return
        
        self.print_help()
        
        while self.running:
            try:
                command = input("\nklipper> ").strip().lower()
                
                if not command:
                    continue
                    
                self.process_command(command)
                
            except (KeyboardInterrupt, EOFError):
                break
        
        # Cleanup
        self.controller.stop_position_monitoring()
    
    def process_command(self, command: str):
        """Process user commands"""
        parts = command.split()
        cmd = parts[0] if parts else ""
        
        if cmd in ['quit', 'exit', 'q']:
            self.running = False
            
        elif cmd == 'help' or cmd == 'h':
            self.print_help()
            
        elif cmd == 'pos' or cmd == 'position':
            self.controller.print_position()
            
        elif cmd == 'home':
            axes = parts[1] if len(parts) > 1 else "XYZ"
            self.controller.home_axes(axes)
            
        elif cmd == 'move':
            self.handle_move_command(parts[1:])
            
        elif cmd == 'monitor':
            if len(parts) > 1 and parts[1] == 'stop':
                self.controller.stop_position_monitoring()
            else:
                interval = float(parts[1]) if len(parts) > 1 else 1.0
                self.controller.start_position_monitoring(interval)
                
        elif cmd == 'gcode':
            if len(parts) > 1:
                gcode = ' '.join(parts[1:])
                self.controller.send_gcode(gcode)
            else:
                print("Usage: gcode <command>")
                
        elif cmd == 'emergency' or cmd == 'estop':
            self.controller.emergency_stop()
            
        else:
            print(f"Unknown command: {cmd}. Type 'help' for available commands.")
    
    def handle_move_command(self, args):
        """Handle move command"""
        if not args:
            print("Usage: move x<value> y<value> z<value> f<feedrate>")
            return
            
        x = y = z = feedrate = None
        
        for arg in args:
            try:
                if arg.startswith('x'):
                    x = float(arg[1:])
                elif arg.startswith('y'):
                    y = float(arg[1:])
                elif arg.startswith('z'):
                    z = float(arg[1:])
                elif arg.startswith('f'):
                    feedrate = int(arg[1:])
            except ValueError:
                print(f"Invalid value: {arg}")
                return
                
        self.controller.move_to(x, y, z, feedrate or 3000)
    
    def print_help(self):
        """Print help information"""
        help_text = """
Available Commands:
==================
help, h              - Show this help
pos, position        - Show current position
home [axes]          - Home axes (default: XYZ, options: X, Y, Z, XY, etc.)
move x<val> y<val> z<val> f<feedrate> - Linear move to coordinates
monitor [interval]   - Start position monitoring (default: 1s interval)
monitor stop         - Stop position monitoring
gcode <command>      - Send raw G-code command
emergency, estop     - Emergency stop
quit, exit, q        - Exit program

Examples:
---------
home XY              - Home X and Y axes only
move x10 y20 z5      - Move to X10, Y20, Z5
move z10 f1500       - Move Z to 10mm at 1500mm/min
monitor 0.5          - Monitor position every 0.5 seconds
monitor stop         - Stop monitoring
gcode G1 X50 F6000   - Send custom linear move command
"""
        print(help_text)

def main():
    """Main function with command line argument parsing"""
    parser = argparse.ArgumentParser(description="Simplified Klipper Controller - Movement Only")
    parser.add_argument('--host', default='localhost', help='Moonraker host (default: localhost)')
    parser.add_argument('--port', type=int, default=7125, help='Moonraker port (default: 7125)')
    parser.add_argument('--timeout', type=int, default=10, help='Request timeout (default: 10s)')
    
    # Command line operations
    parser.add_argument('--home', metavar='AXES', help='Home specified axes (XYZ, XY, Z, etc.)')
    parser.add_argument('--move', nargs='+', metavar='COORD', help='Move to coordinates (x10 y20 z5)')
    parser.add_argument('--position', action='store_true', help='Show current position and exit')
    parser.add_argument('--monitor', type=float, metavar='INTERVAL', help='Start position monitoring with interval')
    parser.add_argument('--gcode', metavar='COMMAND', help='Send G-code command')
    
    args = parser.parse_args()
    
    # Create controller
    controller = KlipperController(args.host, args.port, args.timeout)
    
    if not controller.connect():
        print("Failed to connect to printer. Exiting.")
        sys.exit(1)
    
    # Handle command line operations
    if args.position:
        controller.print_position()
        return
        
    if args.home:
        controller.home_axes(args.home)
        
    if args.move:
        x = y = z = feedrate = None
        for arg in args.move:
            if arg.startswith('x'):
                x = float(arg[1:])
            elif arg.startswith('y'):
                y = float(arg[1:])
            elif arg.startswith('z'):
                z = float(arg[1:])
            elif arg.startswith('f'):
                feedrate = int(arg[1:])
        controller.move_to(x, y, z, feedrate or 3000)
        
    if args.monitor:
        controller.start_position_monitoring(args.monitor)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            controller.stop_position_monitoring()
            
    if args.gcode:
        controller.send_gcode(args.gcode)
    
    # If no specific commands, run interactive mode
    if not any([args.home, args.move, args.position, args.monitor, args.gcode]):
        cli = PrinterCLI()
        cli.run_interactive()

if __name__ == "__main__":
    main()
