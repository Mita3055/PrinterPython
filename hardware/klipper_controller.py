#!/usr/bin/env python3
"""
Simplified and Robust Klipper/Moonraker Controller
Enhanced connection diagnostics and error handling
"""

import requests
import json
import time
import sys
import threading
from typing import Optional, Tuple, Dict, Any
import urllib3

# Disable SSL warnings for local connections
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class PrinterConnectionError(Exception):
    """Exception raised when printer connection fails"""
    pass

class KlipperController:
    """Simplified and robust Klipper controller with enhanced diagnostics"""
    
    def __init__(self, host="localhost", port=7125, timeout=30):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{host}:{port}"
        self.connected = False
        self.printer_state = "unknown"
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'SimplifiedKlipperController/1.0'})
        
        print(f"Initialized controller for {self.base_url}")
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to Moonraker with detailed diagnostics
        
        Returns:
            dict: Connection test results
        """
        results = {
            'moonraker_reachable': False,
            'printer_info_available': False,
            'printer_state': 'unknown',
            'klipper_connected': False,
            'error_message': None
        }
        
        try:
            print("Testing Moonraker connection...")
            
            # Test 1: Basic connectivity to Moonraker
            response = self.session.get(f"{self.base_url}/server/info", timeout=5)
            if response.status_code == 200:
                results['moonraker_reachable'] = True
                server_info = response.json().get('result', {})
                print(f"✓ Moonraker reachable - Version: {server_info.get('moonraker_version', 'unknown')}")
            else:
                results['error_message'] = f"Moonraker returned status {response.status_code}"
                return results
                
        except requests.exceptions.ConnectionError:
            results['error_message'] = f"Cannot connect to {self.base_url} - Is Moonraker running?"
            return results
        except requests.exceptions.Timeout:
            results['error_message'] = "Connection timeout - Moonraker may be slow to respond"
            return results
        except Exception as e:
            results['error_message'] = f"Unexpected error: {str(e)}"
            return results
        
        try:
            # Test 2: Get printer info
            print("Testing printer info endpoint...")
            response = self.session.get(f"{self.base_url}/printer/info", timeout=self.timeout)
            
            if response.status_code == 200:
                results['printer_info_available'] = True
                printer_info = response.json().get('result', {})
                results['printer_state'] = printer_info.get('state', 'unknown')
                
                if results['printer_state'] == 'ready':
                    results['klipper_connected'] = True
                    print(f"✓ Printer info available - State: {results['printer_state']}")
                else:
                    print(f"⚠ Printer state: {results['printer_state']}")
                    
            else:
                results['error_message'] = f"Printer info endpoint returned {response.status_code}"
                
        except Exception as e:
            results['error_message'] = f"Error getting printer info: {str(e)}"
            
        return results
    
    def connect(self) -> bool:
        """
        Connect to printer with comprehensive diagnostics
        
        Returns:
            bool: True if successful connection
        """
        print("=" * 50)
        print("CONNECTING TO PRINTER")
        print("=" * 50)
        
        # Run connection test
        test_results = self.test_connection()
        
        # Print detailed results
        print("\nConnection Test Results:")
        print(f"  Moonraker reachable: {'✓' if test_results['moonraker_reachable'] else '✗'}")
        print(f"  Printer info available: {'✓' if test_results['printer_info_available'] else '✗'}")
        print(f"  Printer state: {test_results['printer_state']}")
        print(f"  Klipper connected: {'✓' if test_results['klipper_connected'] else '✗'}")
        
        if test_results['error_message']:
            print(f"  Error: {test_results['error_message']}")
        
        # Determine if we can proceed
        if not test_results['moonraker_reachable']:
            print("\n❌ FAILED: Cannot reach Moonraker")
            self._print_troubleshooting_tips()
            return False
        
        if not test_results['printer_info_available']:
            print("\n❌ FAILED: Cannot get printer information")
            self._print_klipper_troubleshooting()
            return False
        
        # Check printer state
        state = test_results['printer_state']
        if state == 'ready':
            print("\n✅ SUCCESS: Printer is ready!")
            self.connected = True
            self.printer_state = state
            
            # Get additional info
            self._get_printer_details()
            
            # Safety: Turn off heaters
            self._safety_shutdown_heaters()
            
            return True
            
        elif state == 'error':
            print("\n⚠ WARNING: Printer is in error state")
            print("You may need to resolve printer errors before proceeding.")
            
            # Still mark as connected for basic operations
            self.connected = True
            self.printer_state = state
            return True
            
        elif state == 'shutdown':
            print("\n❌ FAILED: Klipper is shutdown")
            print("Try running 'FIRMWARE_RESTART' or restart Klipper service")
            return False
            
        else:
            print(f"\n⚠ WARNING: Printer state '{state}' - proceeding with caution")
            self.connected = True
            self.printer_state = state
            return True
    
    def _get_printer_details(self):
        """Get and display printer details"""
        try:
            response = self.session.get(f"{self.base_url}/printer/info", timeout=self.timeout)
            if response.status_code == 200:
                info = response.json().get('result', {})
                print(f"\nPrinter Details:")
                print(f"  Hostname: {info.get('hostname', 'unknown')}")
                print(f"  Software: {info.get('software_version', 'unknown')}")
                print(f"  MCU: {info.get('mcu_version', 'unknown')}")
                
        except Exception as e:
            print(f"Could not get printer details: {e}")
    
    def _safety_shutdown_heaters(self):
        """Turn off heaters for safety"""
        try:
            print("\nSafety: Turning off heaters...")
            self.send_gcode("M104 S0", silent=True)  # Hotend off
            self.send_gcode("M140 S0", silent=True)  # Bed off
            print("✓ Heaters set to 0°C")
        except:
            print("⚠ Could not turn off heaters")
    
    def _print_troubleshooting_tips(self):
        """Print troubleshooting information"""
        print("\nTroubleshooting Tips:")
        print("1. Check if Moonraker is running:")
        print("   sudo systemctl status moonraker")
        print("   sudo systemctl start moonraker")
        print()
        print("2. Check if port 7125 is open:")
        print("   ss -tulpn | grep :7125")
        print()
        print("3. Test manually with curl:")
        print(f"   curl {self.base_url}/server/info")
        print()
        print("4. Check Moonraker logs:")
        print("   sudo journalctl -u moonraker -f")
    
    def _print_klipper_troubleshooting(self):
        """Print Klipper-specific troubleshooting"""
        print("\nKlipper Troubleshooting:")
        print("1. Check if Klipper is running:")
        print("   sudo systemctl status klipper")
        print("   sudo systemctl start klipper")
        print()
        print("2. Check Klipper logs:")
        print("   sudo journalctl -u klipper -f")
        print()
        print("3. Try firmware restart:")
        print("   Send 'FIRMWARE_RESTART' command via web interface")
    
    def send_gcode(self, command: str, wait_complete: bool = False, silent: bool = False) -> bool:
        """
        Send G-code command to printer
        
        Args:
            command: G-code command string
            wait_complete: Wait for command completion
            silent: Don't print command output
            
        Returns:
            bool: True if successful
        """
        if not self.connected:
            if not silent:
                print("❌ Error: Not connected to printer")
            return False
        
        try:
            url = f"{self.base_url}/printer/gcode/script"
            data = {"script": command}
            
            response = self.session.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            
            if not silent:
                print(f"→ {command}")
            
            if wait_complete:
                self.wait_for_idle()
            
            return True
            
        except requests.exceptions.RequestException as e:
            if not silent:
                print(f"❌ Failed to send '{command}': {e}")
            return False
    
    def get_position(self) -> Optional[Tuple[float, float, float, float]]:
        """
        Get current toolhead position
        
        Returns:
            Tuple of (X, Y, Z, E) or None if failed
        """
        if not self.connected:
            return None
        
        try:
            url = f"{self.base_url}/printer/objects/query"
            params = {"toolhead": "position"}
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json().get('result', {}).get('status', {})
            position = result.get('toolhead', {}).get('position', [])
            
            if len(position) >= 4:
                #print(f"📍 Current Position: X:{position[0]:.3f} Y:{position[1]:.3f} Z:{position[2]:.3f} E:{position[3]:.3f}")
                return tuple(position[:4])
                
        except Exception as e:
            print(f"Error getting position: {e}")
        
        return None
    
    def get_live_position(self) -> Optional[Dict[str, float]]:
        """
        Get live position from motion_report (real-time during moves)
        
        Returns:
            Dict: {'X': float, 'Y': float, 'Z': float, 'E': float} or None
        """
        if not self.connected:
            return None
        
        try:
            url = f"{self.base_url}/printer/objects/query?motion_report"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            
            result = response.json().get('result', {}).get('status', {})
            motion_report = result.get('motion_report', {})
            live_position = motion_report.get('live_position', [])
            
            if len(live_position) >= 4:
                return {
                    'X': live_position[0],
                    'Y': live_position[1],
                    'Z': live_position[2],
                    'E': live_position[3]
                }
            else:
                # Fallback to regular position if live_position unavailable
                return self.get_position()
                
        except Exception as e:
            print(f"Error getting live position: {e}")
            # Fallback to regular position on error
            return self.get_position()
        
    def get_homed_axes(self) -> str:
        """
        Get which axes are homed
        
        Returns:
            String of homed axes (e.g., "xyz")
        """
        if not self.connected:
            return ""
        
        try:
            url = f"{self.base_url}/printer/objects/query"
            params = {"toolhead": "homed_axes"}
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json().get('result', {}).get('status', {})
            return result.get('toolhead', {}).get('homed_axes', "")
            
        except Exception:
            return ""
    
    def get_printer_state(self) -> str:
        """
        Get current printer state
        
        Returns:
            String representing printer state
        """
        if not self.connected:
            return "disconnected"
        
        try:
            url = f"{self.base_url}/printer/objects/query"
            params = {"print_stats": "state"}
            

            
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json().get('result', {}).get('status', {})
            print(f"📊 Printer State: {result.get('print_stats', {}).get('state', 'unknown')}")
            return result.get('print_stats', {}).get('state', 'unknown')
            
        except Exception:
            return "unknown"
        
    def is_printer_moving(self) -> bool:
        """Check if printer is actually moving"""
        try:
            url = f"{self.base_url}/printer/objects/query?motion_report"
            response = self.session.get(url, timeout=5)
            result = response.json().get('result', {}).get('status', {})
            
            motion_report = result.get('motion_report', {})
            live_velocity = motion_report.get('live_velocity', 0)
            
            # If velocity > 0.1 mm/s, printer is moving
            return live_velocity > 0.1
            
        except Exception:
            return False

    # Replace your wait_for_idle() method with:
    def wait_for_idle(self, timeout: int = 300) -> bool:
        """Wait for printer to stop moving"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if not self.is_printer_moving():
                # Double-check after brief delay
                time.sleep(0.2)
                if not self.is_printer_moving():
                    return True
            time.sleep(0.1)
        
        return False
    
    def home_axes(self, axes: str = "XYZ") -> bool:
        """
        Home specified axes
        
        Args:
            axes: Axes to home (e.g., "XYZ", "XY", "Z")
            
        Returns:
            bool: True if successful
        """
        if axes.upper() in ["XYZ", "ALL"]:
            command = "G28"
        else:
            axis_list = []
            for axis in axes.upper():
                if axis in "XYZ":
                    axis_list.append(axis)
            
            if not axis_list:
                print("❌ Error: Invalid axes specified")
                return False
            
            command = f"G28 {' '.join(axis_list)}"
        
        print(f"🏠 Homing axes: {axes}")
        return self.send_gcode(command, wait_complete=True)
    
    def move_to(self, x=None, y=None, z=None, feedrate=3000) -> bool:
        """
        Move to specified coordinates
        
        Args:
            x, y, z: Target coordinates (None to keep current)
            feedrate: Movement speed in mm/min
            
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
            print("❌ Error: No coordinates specified")
            return False
        
        command = f"G1 {' '.join(coords)} F{feedrate}"
        print(f"🚀 Moving to: {' '.join(coords)}")
        return self.send_gcode(command, wait_complete=True)
    
    def print_position(self):
        """Print current position and homing status"""
        pos = self.get_position()
        homed = self.get_homed_axes()
        
        if pos:
            homed_status = f"[{homed.upper()}]" if homed else "[NOT HOMED]"
            print(f"📍 Position {homed_status}: X:{pos[0]:.3f} Y:{pos[1]:.3f} Z:{pos[2]:.3f} E:{pos[3]:.3f}")
        else:
            print("❌ Failed to get position")
    
    def print_status(self):
        """Print comprehensive printer status"""
        print("\n" + "="*40)
        print("PRINTER STATUS")
        print("="*40)
        
        print(f"Connection: {'✓ Connected' if self.connected else '✗ Disconnected'}")
        print(f"Printer State: {self.get_printer_state()}")
        
        homed = self.get_homed_axes()
        print(f"Homed Axes: {homed.upper() if homed else 'None'}")
        
        self.print_position()
        print("="*40)
    
    def emergency_stop(self):
        """Emergency stop the printer"""
        print("🚨 EMERGENCY STOP!")
        self.send_gcode("M112")


def test_connection():
    """Test function to verify connection"""
    print("Klipper Connection Test")
    print("=" * 40)
    
    controller = KlipperController()
    
    if controller.connect():
        print("\n✅ Connection successful!")
        controller.print_status()
        
        # Test basic operations
        print("\nTesting basic operations...")
        controller.print_position()
        
        return True
    else:
        print("\n❌ Connection failed!")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_connection()
    else:
        # Create controller instance
        controller = KlipperController()
        
        # Test connection
        if controller.connect():
            print("\n✅ Ready for operations!")
            
            # Example usage
            controller.print_status()
            
            # Fetch all available parameters for diagnostics
            response_all_params = controller.session.get(f"{controller.base_url}/printer/objects/query", timeout=controller.timeout)
            if response_all_params.status_code == 200:
                all_params = response_all_params.json().get('result', {}).get('status', {})
                print("\n📊 Available Parameters:")
                for key, value in all_params.items():
                    print(f"  {key}: {value}")

            # Uncomment these lines to test movement:
            controller.home_axes("XYZ")
            controller.move_to(x=50, y=50, z=10)
            controller.print_position()
            
        else:
            print("\n❌ Failed to connect to printer")
            sys.exit(1)