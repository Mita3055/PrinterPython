#!/usr/bin/env python3
"""
Complete Printer Profile & Routine Selector Program
Integrates all existing components for automated 3D printing routines
"""

import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Import existing modules
from hardware.klipper_controller import KlipperController
from data_collection import DataCollector
from configs import *
from g_code import *
from main_helper import data_directory, save_toolpath, execute_toolpath
from hardware.camera_integration import initialize_cameras, get_available_cameras

class PrinterRoutineSelector:
    """Main program for printer profile selection and routine execution"""
    
    def __init__(self):
        self.controller = None
        self.data_collector = None
        self.selected_printer = None
        self.selected_capacitor = None
        self.data_folder = None
        self.cameras_initialized = False
        
        # Available profiles (from configs.py)
        self.printer_profiles = {
            'pvaPrintProfile': pvaPrintProfile,
            'MXeneInkPrintProfile': MXeneInkPrintProfile,
            'MXeneProfile2_20': MXeneProfile2_20,
            'MXeneProfile2_20_slide': MXeneProfile2_20_slide,
            'MXeneProfile_pet_25G': MXeneProfile_pet_25G,
            'MXeneProfile_pet_30G': MXeneProfile_pet_30G,
            'MXeneProfile_1pNanoParticles_25G': MXeneProfile_1pNanoParticles_25G,
            'MXeneProfile_2pNanoParticles_25G': MXeneProfile_2pNanoParticles_25G,
            'MXeneProfile_3pNanoParticles_22G': MXeneProfile_3pNanoParticles_22G,
            'MXeneProfile_5pNanoParticles_22G': MXeneProfile_5pNanoParticles_22G,
            'MXeneProfile_10pNanoParticles_22G': MXeneProfile_10pNanoParticles_22G
        }
        
        self.capacitor_profiles = {
            'LargeCap': LargeCap,
            'stdCap': stdCap,
            'electroCellCap': electroCellCap,
            'smallCap': smallCap
        }
        
        # Available print routines (from g_code_comands.py)
        self.print_routines = {
            'lattice': {
                'name': 'Lattice/Grid Pattern',
                'function': lattice,
                'params': ['start_x', 'start_y', 'rows', 'cols', 'spacing'],
                'defaults': [60, 50, 5, 5, 3],
                'description': 'Print a lattice/grid pattern'
            },
            'square_wave': {
                'name': 'Square Wave Pattern',
                'function': square_wave,
                'params': ['start_x', 'start_y', 'height', 'width', 'iterations'],
                'defaults': [60, 50, 20, 5, 10],
                'description': 'Print square wave pattern'
            },
            'contracting_square_wave': {
                'name': 'Contracting Square Wave',
                'function': contracting_square_wave,
                'params': ['start_x', 'start_y', 'height', 'width', 'iterations', 'shrink_rate'],
                'defaults': [60, 50, 20, 5, 8, 0.9],
                'description': 'Print contracting square wave pattern'
            },
            'straight_line': {
                'name': 'Straight Line Test',
                'function': straight_line,
                'params': ['start_x', 'start_y', 'length', 'qty', 'spacing'],
                'defaults': [60, 50, 40, 5, 5],
                'description': 'Print straight line test pattern'
            },
            'printCap': {
                'name': 'Print Capacitor',
                'function': printCap,
                'params': ['xStart', 'yStart'],
                'defaults': [60, 50],
                'description': 'Print capacitor pattern (requires capacitor profile)'
            },
            'printCap_contact_patch': {
                'name': 'Print Capacitor with Contact Patch',
                'function': printCap_contact_patch,
                'params': ['xStart', 'yStart'],
                'defaults': [60, 50],
                'description': 'Print capacitor with contact patches'
            },
            'singleLineCap_left': {
                'name': 'Single Line Capacitor (Left)',
                'function': singleLineCap_left,
                'params': ['xStart', 'yStart', 'layers', 'layer_height', 'delay'],
                'defaults': [60, 50, 1, 0.2, 30],
                'description': 'Print single line capacitor - left side only'
            },
            'singleLineCap_right': {
                'name': 'Single Line Capacitor (Right)',
                'function': singleLineCap_right,
                'params': ['xStart', 'yStart', 'layers', 'layer_height', 'delay'],
                'defaults': [60, 50, 1, 0.2, 30],
                'description': 'Print single line capacitor - right side only'
            }
        }
    
    def print_banner(self):
        """Print program banner"""
        print("=" * 80)
        print("🖨️  AUTOMATED 3D PRINTER ROUTINE SELECTOR")
        print("=" * 80)
        print("Complete system for profile selection and routine execution")
        print()
    
    def select_printer_profile(self) -> bool:
        """Select printer profile from available options"""
        print("📋 PRINTER PROFILE SELECTION")
        print("-" * 40)
        
        profiles = list(self.printer_profiles.keys())
        
        for i, profile_name in enumerate(profiles, 1):
            profile = self.printer_profiles[profile_name]
            print(f"{i:2d}. {profile_name}")
            print(f"     Extrusion: {profile.extrusion}, Feed Rate: {profile.feed_rate}")
            print(f"     Print Height: {profile.print_height}, Bed Height: {profile.bed_height}")
            print()
        
        while True:
            try:
                choice = input(f"Select printer profile (1-{len(profiles)}): ").strip()
                if choice.lower() == 'q':
                    return False
                
                index = int(choice) - 1
                if 0 <= index < len(profiles):
                    profile_name = profiles[index]
                    self.selected_printer = self.printer_profiles[profile_name]
                    print(f"✓ Selected printer profile: {profile_name}")
                    return True
                else:
                    print("❌ Invalid selection. Try again.")
            except (ValueError, KeyboardInterrupt):
                print("\n❌ Cancelled by user")
                return False
    
    def select_capacitor_profile(self) -> bool:
        """Select capacitor profile from available options"""
        print("\n📋 CAPACITOR PROFILE SELECTION")
        print("-" * 40)
        
        profiles = list(self.capacitor_profiles.keys())
        
        for i, profile_name in enumerate(profiles, 1):
            cap = self.capacitor_profiles[profile_name]
            print(f"{i:2d}. {profile_name}")
            print(f"     Stem: {cap.stem_len}mm, Arms: {cap.arm_len}mm x {cap.arm_count}")
            print(f"     Gap: {cap.gap}mm, Arm Gap: {cap.arm_gap}mm")
            print()
        
        while True:
            try:
                choice = input(f"Select capacitor profile (1-{len(profiles)}): ").strip()
                if choice.lower() == 'q':
                    return False
                
                index = int(choice) - 1
                if 0 <= index < len(profiles):
                    profile_name = profiles[index]
                    self.selected_capacitor = self.capacitor_profiles[profile_name]
                    print(f"✓ Selected capacitor profile: {profile_name}")
                    return True
                else:
                    print("❌ Invalid selection. Try again.")
            except (ValueError, KeyboardInterrupt):
                print("\n❌ Cancelled by user")
                return False
    
    def connect_printer(self) -> bool:
        """Connect to the printer"""
        print("\n🔌 CONNECTING TO PRINTER")
        print("-" * 40)
        
        self.controller = KlipperController()
        
        if self.controller.connect():
            print("✓ Successfully connected to printer")
            return True
        else:
            print("❌ Failed to connect to printer")
            return False
    
    def initialize_systems(self) -> bool:
        """Initialize camera and data collection systems"""
        print("\n📷 INITIALIZING SYSTEMS")
        print("-" * 40)
        
        # Initialize cameras
        if initialize_cameras():
            cameras = get_available_cameras()
            print(f"✓ Initialized {len(cameras)} cameras")
            self.cameras_initialized = True
        else:
            print("⚠ Camera initialization failed - continuing without cameras")
            self.cameras_initialized = False
        
        # Create data directory
        self.data_folder = data_directory()
        print(f"✓ Created data directory: {self.data_folder}")
        
        # Initialize data collector
        self.data_collector = DataCollector(self.data_folder)
        print("✓ Data collector initialized")
        
        return True
    
    def home_printer(self) -> bool:
        """Home the printer"""
        print("\n🏠 HOMING PRINTER")
        print("-" * 40)
        
        print("Homing all axes...")
        if self.controller.home_axes("XYZ"):
            print("✓ Printer homed successfully")
            self.controller.get_position()
            return True
        else:
            print("❌ Homing failed")
            return False
    
    def prime_printer(self) -> bool:
        """Prime the printer"""
        print("\n🔧 PRIMING PRINTER")
        print("-" * 40)
        
        print("Running priming sequence...")
        
        # Generate priming toolpath
        prime_toolpath = []
        prime_toolpath.extend(absolute())
        prime_toolpath.extend(printPrimeLine(xStart=5, yStart=10, len=15, prnt=self.selected_printer))
        prime_toolpath.extend(printPrimeLine(xStart=10, yStart=10, len=20, prnt=self.selected_printer))
        prime_toolpath.extend(printPrimeLine(xStart=15, yStart=10, len=30, prnt=self.selected_printer))
        
        # Execute priming
        try:
            for command in prime_toolpath:
                if command.strip() and not command.strip().startswith(";"):
                    self.controller.send_gcode(command)
                    time.sleep(0.01)
            
            print("✓ Priming completed successfully")
            return True
        except Exception as e:
            print(f"❌ Priming failed: {e}")
            return False
    
    def select_routine(self) -> Optional[Dict[str, Any]]:
        """Select print routine from available options"""
        print("\n📋 PRINT ROUTINE SELECTION")
        print("-" * 40)
        
        routines = list(self.print_routines.keys())
        
        for i, routine_name in enumerate(routines, 1):
            routine = self.print_routines[routine_name]
            print(f"{i:2d}. {routine['name']}")
            print(f"     {routine['description']}")
            print()
        
        while True:
            try:
                choice = input(f"Select print routine (1-{len(routines)}): ").strip()
                if choice.lower() == 'q':
                    return None
                
                index = int(choice) - 1
                if 0 <= index < len(routines):
                    routine_name = routines[index]
                    return {
                        'name': routine_name,
                        **self.print_routines[routine_name]
                    }
                else:
                    print("❌ Invalid selection. Try again.")
            except (ValueError, KeyboardInterrupt):
                print("\n❌ Cancelled by user")
                return None
    
    def get_routine_parameters(self, routine: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get parameters for selected routine"""
        print(f"\n⚙️ CONFIGURING {routine['name'].upper()}")
        print("-" * 40)
        print(f"Description: {routine['description']}")
        print()
        
        params = {}
        param_names = routine['params']
        defaults = routine['defaults']
        
        # Add required parameters (printer and capacitor)
        params['prnt'] = self.selected_printer
        if 'cap' in param_names or any('Cap' in routine['name'] for _ in [routine['name']]):
            params['cap'] = self.selected_capacitor
        
        # Get user input for other parameters
        for i, param_name in enumerate(param_names):
            if param_name in ['prnt', 'cap']:
                continue
                
            default_value = defaults[i] if i < len(defaults) else 0
            
            while True:
                try:
                    user_input = input(f"Enter {param_name} (default: {default_value}): ").strip()
                    
                    if user_input == "":
                        params[param_name] = default_value
                        break
                    elif user_input.lower() == 'q':
                        return None
                    else:
                        # Try to convert to appropriate type
                        if isinstance(default_value, int):
                            params[param_name] = int(user_input)
                        elif isinstance(default_value, float):
                            params[param_name] = float(user_input)
                        else:
                            params[param_name] = user_input
                        break
                except ValueError:
                    print(f"❌ Invalid input for {param_name}. Try again.")
        
        return params
    
    def execute_routine(self, routine: Dict[str, Any], params: Dict[str, Any]) -> bool:
        """Execute the selected routine"""
        print(f"\n🚀 EXECUTING {routine['name'].upper()}")
        print("-" * 40)
        
        try:
            # Generate toolpath
            print("Generating toolpath...")
            routine_function = routine['function']
            
            # Generate G-code commands
            toolpath = []
            toolpath.extend(home())
            
            # Call the routine function with parameters
            routine_commands = routine_function(**params)
            toolpath.extend(routine_commands)
            
            # Add final commands
            toolpath.extend(moveZ(10, self.selected_printer))
            toolpath.extend(motorOff())
            
            # Save toolpath
            save_toolpath(toolpath, self.data_folder)
            print("✓ Toolpath generated and saved")
            
            # Start data collection
            print("Starting data collection...")
            self.data_collector.record_print_data(self.controller, interval=0.05)
            
            # Execute toolpath
            print("Executing print routine...")
            success = execute_toolpath(
                klipper_ctrl=self.controller,
                printer=self.selected_printer,
                toolpath=toolpath,
                data_folder=self.data_folder
            )
            
            # Stop data collection
            self.data_collector.stop_record_data()
            
            if success:
                print("✅ Routine executed successfully!")
                return True
            else:
                print("❌ Routine execution failed")
                return False
                
        except Exception as e:
            print(f"❌ Error executing routine: {e}")
            if self.data_collector:
                self.data_collector.stop_record_data()
            return False
    
    def run_another_routine(self) -> bool:
        """Ask if user wants to run another routine"""
        print("\n🔄 RUN ANOTHER ROUTINE?")
        print("-" * 40)
        
        while True:
            choice = input("Would you like to run another routine? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                return True
            elif choice in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'")
    
    def cleanup(self):
        """Cleanup resources"""
        print("\n🧹 CLEANING UP")
        print("-" * 40)
        
        if self.data_collector:
            self.data_collector.stop_record_data()
        
        if self.cameras_initialized:
            from hardware.camera_integration import cleanup_all
            cleanup_all()
            print("✓ Camera system cleaned up")
        
        print("✓ Cleanup completed")
    
    def run(self):
        """Main program execution"""
        try:
            self.print_banner()
            
            # Step 1: Select profiles
            if not self.select_printer_profile():
                print("❌ Printer profile selection cancelled")
                return
                
            if not self.select_capacitor_profile():
                print("❌ Capacitor profile selection cancelled")
                return
            
            # Step 2: Connect to printer
            if not self.connect_printer():
                print("❌ Cannot proceed without printer connection")
                return
            
            # Step 3: Initialize systems
            if not self.initialize_systems():
                print("❌ System initialization failed")
                return
            
            # Step 4: Home printer
            if not self.home_printer():
                print("❌ Cannot proceed without homing")
                return
            
            # Step 5: Prime printer
            if not self.prime_printer():
                print("❌ Priming failed - continuing anyway")
            
            # Step 6: Main routine loop
            while True:
                # Select routine
                routine = self.select_routine()
                if not routine:
                    print("❌ Routine selection cancelled")
                    break
                
                # Get parameters
                params = self.get_routine_parameters(routine)
                if not params:
                    print("❌ Parameter configuration cancelled")
                    continue
                
                # Execute routine
                self.execute_routine(routine, params)
                
                # Ask for another routine
                if not self.run_another_routine():
                    break
            
            print("\n✅ Program completed successfully!")
            
        except KeyboardInterrupt:
            print("\n\n❌ Program interrupted by user")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
        finally:
            self.cleanup()


def main():
    """Main entry point"""
    program = PrinterRoutineSelector()
    program.run()


if __name__ == "__main__":
    main()