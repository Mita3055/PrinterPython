#!/usr/bin/env python3
"""
Profile CLI - Complete printer setup and toolpath generation interface
Dynamically loads profiles, connects to printer, and generates toolpaths from g_code/printibility
"""

import sys
import os
import inspect
import time
from datetime import datetime
from configs import Printer, Capacitor
from hardware.klipper_controller import KlipperController
from main_helper import data_directory, save_toolpath, execute_toolpath

# Import g_code modules
try:
    from g_code import printibility, patterns, comands
    print("✅ G-code modules loaded successfully")
except ImportError as e:
    print(f"❌ Failed to import g_code modules: {e}")
    sys.exit(1)

class PrinterSetupCLI:
    def __init__(self):
        self.printer_profiles = {}
        self.capacitor_profiles = {}
        self.selected_printer = None
        self.selected_capacitor = None
        self.selected_printer_name = ""
        self.selected_capacitor_name = ""
        self.klipper = None
        self.connected = False
        self.available_functions = {}
        
        # Load profiles and functions
        self.load_profiles()
        self.load_printibility_functions()
    
    def load_profiles(self):
        """Dynamically discover all Printer and Capacitor profiles"""
        import configs
        
        for name in dir(configs):
            obj = getattr(configs, name)
            
            if isinstance(obj, Printer):
                self.printer_profiles[name] = obj
            elif isinstance(obj, Capacitor):
                self.capacitor_profiles[name] = obj
        
        print(f"✅ Loaded {len(self.printer_profiles)} printer profiles and {len(self.capacitor_profiles)} capacitor profiles")
    
    def load_printibility_functions(self):
        """Load available functions from printibility module"""
        for name, obj in inspect.getmembers(printibility):
            if inspect.isfunction(obj) and not name.startswith('_'):
                sig = inspect.signature(obj)
                self.available_functions[name] = {
                    'function': obj,
                    'signature': sig,
                    'description': obj.__doc__ or f"Printibility function: {name}"
                }
        
        print(f"✅ Loaded {len(self.available_functions)} printibility functions")
    
    def display_printer_details(self, printer, profile_name):
        """Display detailed printer information"""
        print(f"\n{'='*50}")
        print(f"🖨️  PRINTER PROFILE: {profile_name}")
        print(f"{'='*50}")
        print(f"Extrusion Rate:     {printer.extrusion}")
        print(f"Retraction:         {printer.retraction}")
        print(f"Feed Rate:          {printer.feed_rate} mm/min")
        print(f"Movement Speed:     {printer.movement_speed} mm/min")
        print(f"Print Height:       {printer.print_height} mm")
        print(f"Bed Height:         {printer.bed_height} mm")
        print(f"Z Hop:              {printer.z_hop} mm")
        print(f"Line Gap:           {printer.line_gap} mm")
        
        if hasattr(printer, 'pressure_passed_extrusion'):
            print(f"Pressure Control:   {'Enabled' if printer.pressure_passed_extrusion else 'Disabled'}")
        if hasattr(printer, 'target_pressure') and printer.target_pressure > 0:
            print(f"Target Pressure:    {printer.target_pressure} N")
    
    def display_capacitor_details(self, capacitor, profile_name):
        """Display detailed capacitor information"""
        print(f"\n{'='*50}")
        print(f"🔧 CAPACITOR PROFILE: {profile_name}")
        print(f"{'='*50}")
        print(f"Stem Length:        {capacitor.stem_len} mm")
        print(f"Arm Length:         {capacitor.arm_len} mm")
        print(f"Arm Count:          {capacitor.arm_count}")
        print(f"Gap:                {capacitor.gap} mm")
        print(f"Arm Gap:            {capacitor.arm_gap} mm")
        print(f"Contact Patch Width: {capacitor.contact_patch_width} mm")
    
    def select_printer_profile(self):
        """Allow user to select a printer profile"""
        print(f"\n📋 STEP 1: SELECT PRINTER PROFILE")
        print("-" * 50)
        
        profile_list = list(self.printer_profiles.keys())
        for i, profile_name in enumerate(profile_list, 1):
            description = ""
            if "PVA" in profile_name:
                description = "(PVA Material)"
            elif "MXene" in profile_name:
                description = "(MXene Material)"
            elif "NanoParticles" in profile_name:
                description = "(With Nanoparticles)"
            
            print(f"{i:2d}. {profile_name} {description}")
        
        while True:
            try:
                choice = input(f"\nSelect printer profile (1-{len(profile_list)}) or 'q' to quit: ").strip()
                
                if choice.lower() == 'q':
                    return False
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(profile_list):
                    self.selected_printer_name = profile_list[choice_num - 1]
                    self.selected_printer = self.printer_profiles[self.selected_printer_name]
                    
                    self.display_printer_details(self.selected_printer, self.selected_printer_name)
                    return True
                else:
                    print(f"❌ Please enter a number between 1 and {len(profile_list)}")
                    
            except ValueError:
                print("❌ Please enter a valid number or 'q' to quit")
    
    def select_capacitor_profile(self):
        """Allow user to select a capacitor profile"""
        print(f"\n📋 STEP 2: SELECT CAPACITOR PROFILE")
        print("-" * 50)
        
        profile_list = list(self.capacitor_profiles.keys())
        for i, profile_name in enumerate(profile_list, 1):
            description = ""
            if "Large" in profile_name:
                description = "(Large Size)"
            elif "std" in profile_name:
                description = "(Standard Size)"
            elif "small" in profile_name:
                description = "(Small Size)"
            elif "electro" in profile_name:
                description = "(Electrochemical Cell)"
            
            print(f"{i:2d}. {profile_name} {description}")
        
        while True:
            try:
                choice = input(f"\nSelect capacitor profile (1-{len(profile_list)}) or 'q' to quit: ").strip()
                
                if choice.lower() == 'q':
                    return False
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(profile_list):
                    self.selected_capacitor_name = profile_list[choice_num - 1]
                    self.selected_capacitor = self.capacitor_profiles[self.selected_capacitor_name]
                    
                    self.display_capacitor_details(self.selected_capacitor, self.selected_capacitor_name)
                    return True
                else:
                    print(f"❌ Please enter a number between 1 and {len(profile_list)}")
                    
            except ValueError:
                print("❌ Please enter a valid number or 'q' to quit")
    
    def initialize_printer(self):
        """Initialize Klipper controller and connect to printer"""
        print(f"\n📋 STEP 3: INITIALIZE PRINTER CONNECTION")
        print("-" * 50)
        
        try:
            # Initialize controller
            print("🔌 Initializing Klipper controller...")
            self.klipper = KlipperController()
            
            # Connect to printer
            print("🔌 Connecting to printer...")
            if not self.klipper.connect():
                print("❌ Failed to connect to printer!")
                print("Please check:")
                print("  1. Moonraker is running (sudo systemctl status moonraker)")
                print("  2. Printer is powered on and connected")
                print("  3. Network connection to printer")
                return False
            
            print("✅ Successfully connected to printer!")
            
            # Check homing status
            homed_axes = self.klipper.get_homed_axes()
            if not homed_axes or len(homed_axes) < 3:
                print("🏠 Printer not homed. Homing all axes...")
                if not self.klipper.home_axes("XYZ"):
                    print("❌ Homing failed!")
                    return False
                print("✅ Homing completed successfully!")
            else:
                print(f"✅ Printer already homed on axes: {homed_axes.upper()}")
            
            # Display current position
            self.klipper.print_position()
            self.connected = True
            return True
            
        except Exception as e:
            print(f"❌ Error initializing printer: {e}")
            return False
    
    def select_printibility_function(self):
        """Allow user to select a function from printibility module"""
        print(f"\n📋 STEP 4: SELECT PRINTIBILITY FUNCTION")
        print("-" * 50)
        
        func_list = list(self.available_functions.keys())
        for i, func_name in enumerate(func_list, 1):
            func_info = self.available_functions[func_name]
            desc = func_info['description']
            # Truncate long descriptions
            if len(desc) > 50:
                desc = desc[:47] + "..."
            print(f"{i:2d}. {func_name:<25} - {desc}")
        
        while True:
            try:
                choice = input(f"\nSelect function (1-{len(func_list)}) or 'q' to quit: ").strip()
                
                if choice.lower() == 'q':
                    return None
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(func_list):
                    func_name = func_list[choice_num - 1]
                    func_info = self.available_functions[func_name]
                    
                    print(f"\n✅ Selected: {func_name}")
                    print(f"Description: {func_info['description']}")
                    return func_name, func_info
                else:
                    print(f"❌ Please enter a number between 1 and {len(func_list)}")
                    
            except ValueError:
                print("❌ Please enter a valid number or 'q' to quit")
    
    def get_function_parameters(self, func_name, func_info):
        """Get parameters for the selected function"""
        print(f"\n📋 STEP 5: CONFIGURE FUNCTION PARAMETERS")
        print("-" * 50)
        
        signature = func_info['signature']
        parameters = {}
        
        # Skip 'prnt' and 'cap' parameters as they're provided automatically
        skip_params = ['prnt', 'cap']
        
        for param_name, param in signature.parameters.items():
            if param_name in skip_params:
                continue
            
            # Get default value
            default_value = param.default if param.default != inspect.Parameter.empty else ""
            
            # Get user input
            while True:
                try:
                    if isinstance(default_value, bool):
                        prompt = f"{param_name} (y/n, default={default_value}): "
                        user_input = input(prompt).strip().lower()
                        if user_input == '':
                            parameters[param_name] = default_value
                        elif user_input in ['y', 'yes', 'true', '1']:
                            parameters[param_name] = True
                        elif user_input in ['n', 'no', 'false', '0']:
                            parameters[param_name] = False
                        else:
                            print("❌ Please enter y/n")
                            continue
                    
                    elif isinstance(default_value, (int, float)) or param_name in [
                        'start_x', 'start_y', 'x', 'y', 'z', 'length', 'width', 'height', 
                        'spacing', 'iterations', 'layers', 'feedrate', 'delay'
                    ]:
                        prompt = f"{param_name} (number, default={default_value}): "
                        user_input = input(prompt).strip()
                        if user_input == '':
                            parameters[param_name] = default_value if default_value != "" else 0
                        else:
                            # Try to determine if it should be int or float
                            if '.' in user_input:
                                parameters[param_name] = float(user_input)
                            else:
                                parameters[param_name] = int(user_input)
                    
                    else:
                        prompt = f"{param_name} (text, default='{default_value}'): "
                        user_input = input(prompt).strip()
                        if user_input == '':
                            parameters[param_name] = default_value
                        else:
                            parameters[param_name] = user_input
                    
                    break
                    
                except ValueError:
                    print("❌ Invalid input. Please try again.")
        
        # Add required parameters
        parameters['prnt'] = self.selected_printer
        if 'cap' in [p.name for p in signature.parameters.values()]:
            parameters['cap'] = self.selected_capacitor
        
        return parameters
    
    def generate_and_execute_toolpath(self, func_name, func_info, parameters):
        """Generate and execute the toolpath"""
        print(f"\n📋 STEP 6: GENERATE AND EXECUTE TOOLPATH")
        print("-" * 50)
        
        try:
            # Create data directory
            folder_name = f"{func_name}_{self.selected_printer_name}_{self.selected_capacitor_name}"
            data_folder = data_directory(folder_name=folder_name)
            print(f"📁 Created data folder: {data_folder}")
            
            # Generate toolpath
            print("🔧 Generating toolpath...")
            func = func_info['function']
            toolpath = func(**parameters)
            
            if not toolpath:
                print("❌ Failed to generate toolpath!")
                return False
            
            print(f"✅ Generated toolpath with {len(toolpath)} commands")
            
            # Save toolpath
            print("💾 Saving toolpath...")
            save_toolpath(toolpath, data_folder)
            
            # Preview toolpath (first 10 commands)
            print("\n📋 TOOLPATH PREVIEW (first 10 commands):")
            print("-" * 50)
            for i, cmd in enumerate(toolpath[:10]):
                print(f"{i+1:2d}. {cmd}")
            if len(toolpath) > 10:
                print(f"... and {len(toolpath) - 10} more commands")
            
            # Ask user to confirm execution
            print("-" * 50)
            confirm = input("\n⚠️  Execute toolpath on printer? (y/N): ").strip().lower()
            
            if confirm in ['y', 'yes']:
                print("🚀 Executing toolpath...")
                success = execute_toolpath(
                    klipper_ctrl=self.klipper,
                    printer=self.selected_printer,
                    toolpath=toolpath,
                    data_folder=data_folder
                )
                
                if success:
                    print("✅ Toolpath executed successfully!")
                else:
                    print("❌ Toolpath execution failed!")
                
                return success
            else:
                print("⏭️  Toolpath execution skipped")
                return True
                
        except Exception as e:
            print(f"❌ Error generating/executing toolpath: {e}")
            return False
    
    def run_complete_workflow(self):
        """Run the complete workflow: profiles -> connect -> function -> execute"""
        print("="*60)
        print("🖨️  COMPLETE PRINTER SETUP & TOOLPATH GENERATION")
        print("="*60)
        
        # Step 1: Select printer profile
        if not self.select_printer_profile():
            return False
        
        # Step 2: Select capacitor profile
        if not self.select_capacitor_profile():
            return False
        
        # Show configuration summary
        print(f"\n💡 CONFIGURATION SUMMARY:")
        print(f"   Printer:   {self.selected_printer_name}")
        print(f"   Capacitor: {self.selected_capacitor_name}")
        
        # Step 3: Initialize printer
        if not self.initialize_printer():
            return False
        
        # Step 4: Select function
        func_result = self.select_printibility_function()
        if not func_result:
            return False
        
        func_name, func_info = func_result
        
        # Step 5: Get parameters
        parameters = self.get_function_parameters(func_name, func_info)
        
        # Step 6: Generate and execute
        return self.generate_and_execute_toolpath(func_name, func_info, parameters)
    
    def main_menu(self):
        """Display main menu"""
        print("\n" + "="*60)
        print("🖨️  PRINTER SETUP CLI")
        print("="*60)
        print("1. Complete Workflow (Profiles → Connect → Generate → Execute)")
        print("2. View Printer Profiles Only")
        print("3. View Capacitor Profiles Only")
        print("4. List Available Functions")
        print("5. Test Printer Connection")
        print("6. Exit")
        print("="*60)
        
        while True:
            choice = input("Select an option (1-6): ").strip()
            
            if choice == '1':
                return 'workflow'
            elif choice == '2':
                return 'printer'
            elif choice == '3':
                return 'capacitor'
            elif choice == '4':
                return 'functions'
            elif choice == '5':
                return 'test'
            elif choice == '6':
                return 'exit'
            else:
                print("❌ Please enter a number between 1 and 6")
    
    def list_functions(self):
        """List all available printibility functions"""
        print(f"\n📋 AVAILABLE PRINTIBILITY FUNCTIONS ({len(self.available_functions)}):")
        print("-" * 60)
        
        for i, (func_name, func_info) in enumerate(self.available_functions.items(), 1):
            signature = func_info['signature']
            params = [p for p in signature.parameters.keys() if p not in ['prnt', 'cap']]
            param_str = ", ".join(params[:3])  # Show first 3 parameters
            if len(params) > 3:
                param_str += "..."
            
            print(f"{i:2d}. {func_name:<25} ({param_str})")
        
        print("-" * 60)
    
    def test_connection(self):
        """Test printer connection without full workflow"""
        print(f"\n🧪 TESTING PRINTER CONNECTION")
        print("-" * 50)
        
        if self.initialize_printer():
            print("✅ Connection test successful!")
            if self.klipper:
                self.klipper.print_status()
        else:
            print("❌ Connection test failed!")
    
    def run(self):
        """Main application loop"""
        try:
            while True:
                choice = self.main_menu()
                
                if choice == 'exit':
                    print("\n👋 Goodbye!")
                    if self.klipper:
                        print("🔌 Disconnecting from printer...")
                    break
                    
                elif choice == 'workflow':
                    self.run_complete_workflow()
                    input("\nPress Enter to continue...")
                    
                elif choice == 'printer':
                    self.select_printer_profile()
                    input("\nPress Enter to continue...")
                    
                elif choice == 'capacitor':
                    self.select_capacitor_profile()
                    input("\nPress Enter to continue...")
                    
                elif choice == 'functions':
                    self.list_functions()
                    input("\nPress Enter to continue...")
                    
                elif choice == 'test':
                    self.test_connection()
                    input("\nPress Enter to continue...")
                    
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
        except Exception as e:
            print(f"\n❌ Error: {e}")

def main():
    """Main entry point"""
    try:
        cli = PrinterSetupCLI()
        cli.run()
    except Exception as e:
        print(f"❌ Failed to start CLI: {e}")
        print("Make sure you're running this script from the correct directory")
        print("and that all required modules are available.")

if __name__ == "__main__":
    main()