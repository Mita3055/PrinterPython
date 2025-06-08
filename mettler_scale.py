# -*- coding: utf-8 -*-
"""
Mettler Toledo Device Library
Clean version for project folder usage
"""
import serial
import time
import platform
import os

# Constants
DEBUG = False
BAUDRATE = 9600
TIMEOUT = 0.05
WRITE_DELAY = 0.05
RESET_DELAY = 2.0

class MettlerToledoError(Exception):
    """Custom exception for Mettler Toledo device errors"""
    pass

class MettlerToledoDevice:
    """
    Interface to Mettler Toledo balances and scales using MT-SICS commands.
    
    Example Usage:
    
    # Auto-detect device
    dev = MettlerToledoDevice()
    
    # Or specify port manually
    dev = MettlerToledoDevice(port='COM3')  # Windows
    dev = MettlerToledoDevice(port='/dev/ttyUSB0')  # Linux
    dev = MettlerToledoDevice(port='/dev/tty.usbmodem262471')  # Mac
    
    # Get device information
    serial_num = dev.get_serial_number()
    balance_data = dev.get_balance_data()
    
    # Get weight readings
    stable_weight = dev.get_weight_stable()  # Returns None if not stable
    current_weight = dev.get_weight()        # Always returns current weight
    
    # Zero the balance
    success = dev.zero_stable()  # Returns True/False
    status = dev.zero()          # Returns 'S' or 'D'
    
    # Close when done
    dev.close()
    """
    
    def __init__(self, port=None, baudrate=BAUDRATE, timeout=TIMEOUT, debug=DEBUG, **serial_kwargs):
        self.debug = debug
        self.baudrate = baudrate if baudrate else BAUDRATE
        self.timeout = timeout if timeout else TIMEOUT
        self._last_write_time = 0
        
        # Find port if not specified
        if not port:
            port = self._find_device_port()
        
        # Connect to device
        try:
            self.serial_conn = serial.Serial(
                port=port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                **serial_kwargs
            )
            self.port = port
        except Exception as e:
            raise MettlerToledoError(f"Failed to connect to port {port}: {e}")
        
        # Initialize device
        time.sleep(RESET_DELAY)
        self._debug_print(f"Connected to Mettler Toledo device on {port}")
    
    def _debug_print(self, *args):
        if self.debug:
            print(*args)
    
    def _find_device_port(self):
        """Find a Mettler Toledo device port automatically"""
        import serial.tools.list_ports
        
        ports = [port.device for port in serial.tools.list_ports.comports()]
        
        # Filter ports by OS
        if platform.system() == 'Darwin':  # macOS
            ports = [p for p in ports if 'tty.usbmodem' in p or 'tty.usbserial' in p]
        
        # Test each port
        for port in ports:
            if self._test_port(port):
                return port
        
        if not ports:
            raise MettlerToledoError("No serial ports found")
        else:
            raise MettlerToledoError(f"No Mettler Toledo devices found on ports: {ports}")
    
    def _test_port(self, port):
        """Test if a port has a Mettler Toledo device"""
        try:
            test_conn = serial.Serial(port=port, baudrate=self.baudrate, timeout=self.timeout)
            time.sleep(0.5)  # Give device time to initialize
            
            # Try to get serial number
            test_conn.write(b'I4\r\n')
            test_conn.flush()
            response = test_conn.readline().decode('utf-8', errors='ignore').strip()
            test_conn.close()
            
            # Check if response looks like a Mettler Toledo response
            if response and len(response.split()) >= 3:
                self._debug_print(f"Found potential Mettler Toledo device on {port}: {response}")
                return True
            
        except Exception as e:
            self._debug_print(f"Port {port} test failed: {e}")
        
        return False
    
    def _send_command(self, command):
        """Send a command and get response"""
        if not self.serial_conn or not self.serial_conn.is_open:
            raise MettlerToledoError("Serial connection not open")
        
        # Add delay between writes if needed
        current_time = time.time()
        if (current_time - self._last_write_time) < WRITE_DELAY:
            time.sleep(WRITE_DELAY - (current_time - self._last_write_time))
        
        # Send command
        full_command = f"{command}\r\n"
        self._debug_print(f"Sending: {repr(full_command)}")
        
        try:
            self.serial_conn.write(full_command.encode('utf-8'))
            self.serial_conn.flush()
            self._last_write_time = time.time()
            
            # Read response
            response = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
            self._debug_print(f"Received: {repr(response)}")
            
            if not response:
                raise MettlerToledoError("No response from device")
            
            # Parse response
            response_parts = response.replace('"', '').split()
            
            # Check for errors in response
            if len(response_parts) >= 2:
                status = response_parts[1]
                if 'ES' in status:
                    raise MettlerToledoError('Syntax Error')
                elif 'ET' in status:
                    raise MettlerToledoError('Transmission Error')
                elif 'EL' in status:
                    raise MettlerToledoError('Logical Error')
            
            return response_parts
            
        except Exception as e:
            if isinstance(e, MettlerToledoError):
                raise
            raise MettlerToledoError(f"Communication error: {e}")
    
    def close(self):
        """Close the serial connection"""
        try:
            if self.serial_conn and self.serial_conn.is_open:
                self.serial_conn.close()
        except:
            pass
    
    def get_port(self):
        """Get the current serial port"""
        return self.port
    
    def get_serial_number(self):
        """Get device serial number"""
        response = self._send_command('I4')
        if len(response) >= 3:
            if 'I' in response[1]:
                raise MettlerToledoError('Command not executable at present')
            return response[2]
        return None
    
    def get_balance_data(self):
        """Get balance identification data"""
        response = self._send_command('I2')
        if len(response) >= 3:
            if 'I' in response[1]:
                raise MettlerToledoError('Command not executable at present')
            return response[2:]
        return []
    
    def get_software_version(self):
        """Get software version information"""
        response = self._send_command('I3')
        if len(response) >= 3:
            if 'I' in response[1]:
                raise MettlerToledoError('Command not executable at present')
            return response[2:]
        return []
    
    def get_weight_stable(self):
        """Get weight only if stable, returns None if not stable"""
        try:
            response = self._send_command('S')
            if len(response) >= 3:
                status = response[1]
                if 'I' in status:
                    raise MettlerToledoError('Command not executable at present')
                elif '+' in status:
                    raise MettlerToledoError('Balance in overload range')
                elif '-' in status:
                    raise MettlerToledoError('Balance in underload range')
                
                weight = float(response[2])
                unit = response[3] if len(response) > 3 else 'g'
                return [weight, unit]
        except (ValueError, IndexError):
            return None
        except MettlerToledoError:
            raise
        except:
            return None
    
    def get_weight(self):
        """Get current weight regardless of stability"""
        response = self._send_command('SI')
        if len(response) >= 3:
            status = response[1]
            if 'I' in status:
                raise MettlerToledoError('Command not executable at present')
            elif '+' in status:
                raise MettlerToledoError('Balance in overload range')
            elif '-' in status:
                raise MettlerToledoError('Balance in underload range')
            
            try:
                weight = float(response[2])
                unit = response[3] if len(response) > 3 else 'g'
                stability = status  # 'S' for stable, 'D' for dynamic
                return [weight, unit, stability]
            except (ValueError, IndexError):
                raise MettlerToledoError('Invalid weight response format')
        
        raise MettlerToledoError('Invalid response format')
    
    def zero_stable(self):
        """Zero the balance, only if stable"""
        try:
            response = self._send_command('Z')
            if len(response) >= 2:
                status = response[1]
                if 'I' in status:
                    return False  # Not stable or busy
                elif '+' in status:
                    raise MettlerToledoError('Upper limit of zero range exceeded')
                elif '-' in status:
                    raise MettlerToledoError('Lower limit of zero range exceeded')
                return True
        except MettlerToledoError:
            raise
        except:
            return False
    
    def zero(self):
        """Zero the balance immediately regardless of stability"""
        response = self._send_command('ZI')
        if len(response) >= 2:
            status = response[1]
            if 'I' in status:
                raise MettlerToledoError('Zero setting failed')
            elif '+' in status:
                raise MettlerToledoError('Upper limit of zero range exceeded')
            elif '-' in status:
                raise MettlerToledoError('Lower limit of zero range exceeded')
            return status
        
        raise MettlerToledoError('Invalid zero response')
    
    def reset(self):
        """Reset the balance"""
        self._send_command('@')


def find_mettler_toledo_ports(debug=False):
    """Find all available Mettler Toledo device ports"""
    import serial.tools.list_ports
    
    ports = [port.device for port in serial.tools.list_ports.comports()]
    mettler_ports = []
    
    for port in ports:
        try:
            # Test connection
            test_conn = serial.Serial(port=port, baudrate=BAUDRATE, timeout=TIMEOUT)
            time.sleep(0.5)
            
            # Try to identify as Mettler Toledo
            test_conn.write(b'I4\r\n')
            test_conn.flush()
            response = test_conn.readline().decode('utf-8', errors='ignore').strip()
            test_conn.close()
            
            if response and len(response.split()) >= 3:
                mettler_ports.append(port)
                if debug:
                    print(f"Found Mettler Toledo device on {port}")
        
        except Exception as e:
            if debug:
                print(f"Port {port} test failed: {e}")
    
    return mettler_ports


# Example usage and testing
if __name__ == '__main__':
    import sys
    
    # Simple command line interface
    if len(sys.argv) > 1:
        if sys.argv[1] == '--list-ports':
            print("Scanning for Mettler Toledo devices...")
            ports = find_mettler_toledo_ports(debug=True)
            if ports:
                print(f"Found devices on: {ports}")
            else:
                print("No Mettler Toledo devices found")
            sys.exit(0)
        elif sys.argv[1] == '--help':
            print("Usage:")
            print("  python mettler_toledo_device.py --list-ports  # Find devices")
            print("  python mettler_toledo_device.py --test        # Test device")
            print("  python mettler_toledo_device.py              # Interactive test")
            sys.exit(0)
    
    # Test the device
    try:
        print("Connecting to Mettler Toledo device...")
        dev = MettlerToledoDevice(debug=True)
        
        print(f"Connected to port: {dev.get_port()}")
        
        # Get device info
        try:
            serial_num = dev.get_serial_number()
            print(f"Serial Number: {serial_num}")
        except Exception as e:
            print(f"Could not get serial number: {e}")
        
        try:
            balance_data = dev.get_balance_data()
            print(f"Balance Data: {balance_data}")
        except Exception as e:
            print(f"Could not get balance data: {e}")
        
        # Test weight reading
        print("\nTesting weight readings (5 samples):")
        for i in range(5):
            try:
                weight = dev.get_weight()
                stable_weight = dev.get_weight_stable()
                
                print(f"Sample {i+1}:")
                if weight:
                    stability = "Stable" if weight[2] == 'S' else "Dynamic"
                    print(f"  Current: {weight[0]:.4f} {weight[1]} ({stability})")
                
                if stable_weight:
                    print(f"  Stable:  {stable_weight[0]:.4f} {stable_weight[1]}")
                else:
                    print(f"  Stable:  Not stable")
                
                time.sleep(1)
                
            except Exception as e:
                print(f"  Error: {e}")
        
        dev.close()
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Failed to connect: {e}")
        print("\nTry:")
        print("  python mettler_toledo_device.py --list-ports")
        sys.exit(1)
