#!/usr/bin/env python3
"""
G-Code Generation GUI
Simple interface for generating G-code toolpaths with printer and capacitor profiles
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import inspect
from datetime import datetime
from typing import Dict, List, Any

# Import your existing modules
import sys
import os
import inspect

# If needed, add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from configs import Printer, Capacitor

try:
    from .g_code.g_code_comands import *
    from .g_code.patterns import *
    from .g_code.printibility import *
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all required modules are available")

class GCodeGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("G-Code Generator")
        self.root.geometry("1200x800")
        
        # Variables
        self.selected_printer = tk.StringVar()
        self.selected_capacitor = tk.StringVar()
        self.selected_function = tk.StringVar()
        self.filename = tk.StringVar(value="toolpath")
        self.save_directory = tk.StringVar(value="toolpaths")
        
        # State
        self.current_printer = None
        self.current_capacitor = None
        self.toolpath_sequence = []
        self.available_functions = {}
        self.param_widgets = {}
        
        # Load profiles and functions
        self.load_profiles()
        self.load_functions()
        
        # Create GUI
        self.create_widgets()
        
        # Set defaults
        self.set_defaults()

    def load_profiles(self):
        """Load all available printer and capacitor profiles"""
        printer_profiles = []
        capacitor_profiles = []

        for name, obj in vars(configs).items():
            if isinstance(obj, Printer):
                printer_profiles.append((name, obj))
            elif isinstance(obj, Capacitor):
                capacitor_profiles.append((name, obj))
        
        self.printer_profiles = dict(printer_profiles)
        self.capacitor_profiles = dict(capacitor_profiles)

    def load_functions(self):
        """Load all available functions from patterns and printibility modules"""
        self.available_functions = {}
        
        # Load from patterns module
        patterns_module = __import__('g_code.patterns', fromlist=[''])
        printibility_module = __import__('g_code.printibility', fromlist=[''])
        
        # Get functions from patterns
        for name, obj in inspect.getmembers(patterns_module):
            if inspect.isfunction(obj) and not name.startswith('_'):
                sig = inspect.signature(obj)
                self.available_functions[f"patterns.{name}"] = {
                    'function': obj,
                    'signature': sig,
                    'module': 'patterns',
                    'description': obj.__doc__ or f"Pattern function: {name}"
                }
        
        # Get functions from printibility
        for name, obj in inspect.getmembers(printibility_module):
            if inspect.isfunction(obj) and not name.startswith('_'):
                sig = inspect.signature(obj)
                self.available_functions[f"printibility.{name}"] = {
                    'function': obj,
                    'signature': sig,
                    'module': 'printibility',
                    'description': obj.__doc__ or f"Printibility function: {name}"
                }

    def create_widgets(self):
        """Create the main GUI widgets"""
        # Create main container with scrollable frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left panel - Configuration and Function Selection
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Right panel - Toolpath and Preview
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Create sections
        self.create_profile_section(left_panel)
        self.create_function_section(left_panel)
        self.create_parameter_section(left_panel)
        self.create_toolpath_section(right_panel)
        self.create_save_section(right_panel)

    def create_profile_section(self, parent):
        """Create profile selection section"""
        profile_frame = ttk.LabelFrame(parent, text="1. Select Profiles", padding=10)
        profile_frame.pack(fill='x', pady=(0, 10))
        
        # Printer Profile
        ttk.Label(profile_frame, text="Printer Profile:").grid(row=0, column=0, sticky='w', padx=(0, 10))
        printer_combo = ttk.Combobox(profile_frame, textvariable=self.selected_printer,
                                   values=list(self.printer_profiles.keys()), state='readonly', width=30)
        printer_combo.grid(row=0, column=1, sticky='ew', pady=2)
        printer_combo.bind('<<ComboboxSelected>>', self.on_printer_change)
        
        # Capacitor Profile
        ttk.Label(profile_frame, text="Capacitor Profile:").grid(row=1, column=0, sticky='w', padx=(0, 10))
        cap_combo = ttk.Combobox(profile_frame, textvariable=self.selected_capacitor,
                               values=list(self.capacitor_profiles.keys()), state='readonly', width=30)
        cap_combo.grid(row=1, column=1, sticky='ew', pady=2)
        cap_combo.bind('<<ComboboxSelected>>', self.on_capacitor_change)
        
        # Configure grid weights
        profile_frame.columnconfigure(1, weight=1)
        
        # Profile info display
        self.profile_info = ttk.Label(profile_frame, text="Select profiles to see details", 
                                    foreground='gray', wraplength=400)
        self.profile_info.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(10, 0))

    def create_function_section(self, parent):
        """Create function selection section"""
        func_frame = ttk.LabelFrame(parent, text="2. Add Functions to Toolpath", padding=10)
        func_frame.pack(fill='x', pady=(0, 10))
        
        # Function selection
        ttk.Label(func_frame, text="Available Functions:").grid(row=0, column=0, sticky='w')
        func_combo = ttk.Combobox(func_frame, textvariable=self.selected_function,
                                values=list(self.available_functions.keys()), state='readonly', width=40)
        func_combo.grid(row=0, column=1, columnspan=2, sticky='ew', pady=2)
        func_combo.bind('<<ComboboxSelected>>', self.on_function_change)
        
        # Function description
        self.func_description = ttk.Label(func_frame, text="Select a function to see description", 
                                        foreground='gray', wraplength=400)
        self.func_description.grid(row=1, column=0, columnspan=3, sticky='ew', pady=(5, 0))
        
        # Configure grid weights
        func_frame.columnconfigure(1, weight=1)

    def create_parameter_section(self, parent):
        """Create parameter input section"""
        self.param_frame = ttk.LabelFrame(parent, text="3. Function Parameters", padding=10)
        self.param_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Scrollable parameter area
        self.param_canvas = tk.Canvas(self.param_frame)
        param_scrollbar = ttk.Scrollbar(self.param_frame, orient="vertical", command=self.param_canvas.yview)
        self.param_scroll_frame = ttk.Frame(self.param_canvas)
        
        self.param_scroll_frame.bind(
            "<Configure>",
            lambda e: self.param_canvas.configure(scrollregion=self.param_canvas.bbox("all"))
        )
        
        self.param_canvas.create_window((0, 0), window=self.param_scroll_frame, anchor="nw")
        self.param_canvas.configure(yscrollcommand=param_scrollbar.set)
        
        self.param_canvas.pack(side="left", fill="both", expand=True)
        param_scrollbar.pack(side="right", fill="y")
        
        # Add to toolpath button
        add_button_frame = ttk.Frame(parent)
        add_button_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(add_button_frame, text="Add to Toolpath", 
                  command=self.add_to_toolpath, style='Accent.TButton').pack(side='right')

    def create_toolpath_section(self, parent):
        """Create toolpath sequence section"""
        toolpath_frame = ttk.LabelFrame(parent, text="4. Toolpath Sequence", padding=10)
        toolpath_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Toolpath listbox with scrollbar
        list_frame = ttk.Frame(toolpath_frame)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.toolpath_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=10)
        self.toolpath_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.toolpath_listbox.yview)
        
        # Toolpath controls
        controls_frame = ttk.Frame(toolpath_frame)
        controls_frame.pack(fill='x')
        
        ttk.Button(controls_frame, text="↑ Move Up", 
                  command=self.move_toolpath_up).pack(side='left', padx=(0, 5))
        ttk.Button(controls_frame, text="↓ Move Down", 
                  command=self.move_toolpath_down).pack(side='left', padx=(0, 5))
        ttk.Button(controls_frame, text="Remove", 
                  command=self.remove_toolpath_item).pack(side='left', padx=(0, 5))
        ttk.Button(controls_frame, text="Clear All", 
                  command=self.clear_toolpath).pack(side='right')
        
        # Add defaults section
        defaults_frame = ttk.Frame(toolpath_frame)
        defaults_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Label(defaults_frame, text="Add Default Sequences:").pack(anchor='w')
        default_buttons_frame = ttk.Frame(defaults_frame)
        default_buttons_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Button(default_buttons_frame, text="Add G-code Start", 
                  command=self.add_gcode_start).pack(side='left', padx=(0, 5))
        ttk.Button(default_buttons_frame, text="Add Prime Routine", 
                  command=self.add_prime_routine).pack(side='left')

    def create_save_section(self, parent):
        """Create save and preview section"""
        save_frame = ttk.LabelFrame(parent, text="5. Generate & Save", padding=10)
        save_frame.pack(fill='x', pady=(0, 0))
        
        # File settings
        file_frame = ttk.Frame(save_frame)
        file_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(file_frame, text="Filename:").grid(row=0, column=0, sticky='w', padx=(0, 10))
        ttk.Entry(file_frame, textvariable=self.filename, width=20).grid(row=0, column=1, sticky='ew')
        ttk.Label(file_frame, text=".gcode").grid(row=0, column=2, sticky='w')
        
        ttk.Label(file_frame, text="Directory:").grid(row=1, column=0, sticky='w', padx=(0, 10))
        ttk.Entry(file_frame, textvariable=self.save_directory, width=20).grid(row=1, column=1, sticky='ew')
        ttk.Button(file_frame, text="Browse", 
                  command=self.browse_directory).grid(row=1, column=2, sticky='w', padx=(5, 0))
        
        file_frame.columnconfigure(1, weight=1)
        
        # Action buttons
        action_frame = ttk.Frame(save_frame)
        action_frame.pack(fill='x')
        
        ttk.Button(action_frame, text="Preview G-Code", 
                  command=self.preview_gcode).pack(side='left', padx=(0, 5))
        ttk.Button(action_frame, text="Save G-Code", 
                  command=self.save_gcode, style='Accent.TButton').pack(side='right')

    def set_defaults(self):
        """Set default selections"""
        if self.printer_profiles:
            first_printer = list(self.printer_profiles.keys())[0]
            self.selected_printer.set(first_printer)
            self.on_printer_change()
        
        if self.capacitor_profiles:
            first_cap = list(self.capacitor_profiles.keys())[0]
            self.selected_capacitor.set(first_cap)
            self.on_capacitor_change()

    def on_printer_change(self, event=None):
        """Handle printer selection change"""
        printer_name = self.selected_printer.get()
        if printer_name:
            self.current_printer = self.printer_profiles[printer_name]
            self.update_profile_info()

    def on_capacitor_change(self, event=None):
        """Handle capacitor selection change"""
        cap_name = self.selected_capacitor.get()
        if cap_name:
            self.current_capacitor = self.capacitor_profiles[cap_name]
            self.update_profile_info()

    def update_profile_info(self):
        """Update profile information display"""
        info_text = ""
        
        if self.current_printer:
            info_text += f"Printer: {self.selected_printer.get()}\n"
            info_text += f"  Extrusion: {self.current_printer.extrusion}, "
            info_text += f"Feed Rate: {self.current_printer.feed_rate}\n"
        
        if self.current_capacitor:
            info_text += f"Capacitor: {self.selected_capacitor.get()}\n"
            info_text += f"  Arms: {self.current_capacitor.arm_count}, "
            info_text += f"Gap: {self.current_capacitor.gap}"
        
        self.profile_info.config(text=info_text or "Select profiles to see details")

    def on_function_change(self, event=None):
        """Handle function selection change"""
        func_name = self.selected_function.get()
        if func_name and func_name in self.available_functions:
            func_info = self.available_functions[func_name]
            self.func_description.config(text=func_info['description'])
            self.create_parameter_inputs(func_name)

    def create_parameter_inputs(self, func_name):
        """Create input widgets for function parameters"""
        # Clear existing parameter widgets
        for widget in self.param_scroll_frame.winfo_children():
            widget.destroy()
        
        self.param_widgets = {}
        
        func_info = self.available_functions[func_name]
        signature = func_info['signature']
        
        # Skip 'prnt' and 'cap' parameters as they're provided automatically
        skip_params = ['prnt', 'cap']
        
        row = 0
        for param_name, param in signature.parameters.items():
            if param_name in skip_params:
                continue
            
            # Create label
            ttk.Label(self.param_scroll_frame, text=f"{param_name}:").grid(
                row=row, column=0, sticky='w', padx=(0, 10), pady=2)
            
            # Determine input type and default value
            default_value = param.default if param.default != inspect.Parameter.empty else ""
            
            if isinstance(default_value, bool):
                # Boolean parameter - checkbox
                var = tk.BooleanVar(value=default_value)
                ttk.Checkbutton(self.param_scroll_frame, variable=var).grid(
                    row=row, column=1, sticky='w', pady=2)
            elif isinstance(default_value, (int, float)) or param_name in [
                'start_x', 'start_y', 'x', 'y', 'z', 'length', 'width', 'height', 
                'spacing', 'iterations', 'layers', 'feedrate', 'delay'
            ]:
                # Numeric parameter - spinbox
                var = tk.DoubleVar(value=float(default_value) if default_value != "" else 0.0)
                spinbox = ttk.Spinbox(self.param_scroll_frame, from_=-1000, to=1000, 
                                    increment=0.1, textvariable=var, width=15)
                spinbox.grid(row=row, column=1, sticky='ew', pady=2)
            else:
                # String parameter - entry
                var = tk.StringVar(value=str(default_value) if default_value != "" else "")
                ttk.Entry(self.param_scroll_frame, textvariable=var, width=15).grid(
                    row=row, column=1, sticky='ew', pady=2)
            
            self.param_widgets[param_name] = var
            row += 1
        
        # Configure grid weights
        self.param_scroll_frame.columnconfigure(1, weight=1)

    def add_to_toolpath(self):
        """Add selected function with parameters to toolpath"""
        func_name = self.selected_function.get()
        if not func_name:
            messagebox.showwarning("Warning", "Please select a function!")
            return
        
        if not self.current_printer:
            messagebox.showwarning("Warning", "Please select a printer profile!")
            return
        
        # Build parameter dictionary
        params = {}
        for param_name, var in self.param_widgets.items():
            params[param_name] = var.get()
        
        # Add required parameters
        params['prnt'] = self.current_printer
        if 'cap' in self.available_functions[func_name]['signature'].parameters:
            if not self.current_capacitor:
                messagebox.showwarning("Warning", "This function requires a capacitor profile!")
                return
            params['cap'] = self.current_capacitor
        
        # Store toolpath item
        toolpath_item = {
            'type': 'function',
            'function_name': func_name,
            'parameters': params.copy(),
            'display_name': func_name.split('.')[-1]
        }
        
        self.toolpath_sequence.append(toolpath_item)
        self.refresh_toolpath_display()
        
        messagebox.showinfo("Success", f"Added {func_name} to toolpath!")

    def add_gcode_start(self):
        """Add default G-code start sequence"""
        start_sequence = {
            'type': 'gcode_start',
            'display_name': 'G-code Start (Home + Setup)',
            'commands': home() + absolute()
        }
        self.toolpath_sequence.insert(0, start_sequence)  # Add at beginning
        self.refresh_toolpath_display()
        messagebox.showinfo("Success", "Added G-code start sequence!")

    def add_prime_routine(self):
        """Add prime routine"""
        if not self.current_printer:
            messagebox.showwarning("Warning", "Please select a printer profile first!")
            return
        
        prime_sequence = {
            'type': 'prime_routine',
            'display_name': 'Prime Routine',
            'parameters': {'prnt': self.current_printer}
        }
        
        # Insert after start sequence if it exists, otherwise at beginning
        insert_pos = 1 if self.toolpath_sequence and self.toolpath_sequence[0]['type'] == 'gcode_start' else 0
        self.toolpath_sequence.insert(insert_pos, prime_sequence)
        self.refresh_toolpath_display()
        messagebox.showinfo("Success", "Added prime routine!")

    def refresh_toolpath_display(self):
        """Refresh the toolpath listbox display"""
        self.toolpath_listbox.delete(0, tk.END)
        for i, item in enumerate(self.toolpath_sequence):
            display_text = f"{i+1}. {item['display_name']}"
            if item['type'] == 'function' and 'parameters' in item:
                # Show key parameters
                params = item['parameters']
                param_str = ', '.join(f"{k}={v}" for k, v in params.items() 
                                    if k not in ['prnt', 'cap'] and v != "")
                if param_str:
                    display_text += f" ({param_str})"
            self.toolpath_listbox.insert(tk.END, display_text)

    def move_toolpath_up(self):
        """Move selected toolpath item up"""
        selection = self.toolpath_listbox.curselection()
        if selection and selection[0] > 0:
            idx = selection[0]
            self.toolpath_sequence[idx], self.toolpath_sequence[idx-1] = \
                self.toolpath_sequence[idx-1], self.toolpath_sequence[idx]
            self.refresh_toolpath_display()
            self.toolpath_listbox.selection_set(idx-1)

    def move_toolpath_down(self):
        """Move selected toolpath item down"""
        selection = self.toolpath_listbox.curselection()
        if selection and selection[0] < len(self.toolpath_sequence) - 1:
            idx = selection[0]
            self.toolpath_sequence[idx], self.toolpath_sequence[idx+1] = \
                self.toolpath_sequence[idx+1], self.toolpath_sequence[idx]
            self.refresh_toolpath_display()
            self.toolpath_listbox.selection_set(idx+1)

    def remove_toolpath_item(self):
        """Remove selected toolpath item"""
        selection = self.toolpath_listbox.curselection()
        if selection:
            idx = selection[0]
            del self.toolpath_sequence[idx]
            self.refresh_toolpath_display()

    def clear_toolpath(self):
        """Clear all toolpath items"""
        if messagebox.askyesno("Confirm", "Clear all toolpath items?"):
            self.toolpath_sequence.clear()
            self.refresh_toolpath_display()

    def browse_directory(self):
        """Browse for save directory"""
        directory = filedialog.askdirectory(initialdir=self.save_directory.get())
        if directory:
            self.save_directory.set(directory)

    def generate_gcode(self):
        """Generate G-code from toolpath sequence"""
        if not self.toolpath_sequence:
            return []
        
        gcode_lines = [
            "; G-Code generated by G-Code Generator GUI",
            f"; Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"; Printer: {self.selected_printer.get()}",
            f"; Capacitor: {self.selected_capacitor.get()}",
            ""
        ]
        
        for item in self.toolpath_sequence:
            try:
                if item['type'] == 'gcode_start':
                    gcode_lines.extend(item['commands'])
                elif item['type'] == 'prime_routine':
                    prime_commands = primeRoutine(item['parameters']['prnt'])
                    gcode_lines.extend(prime_commands)
                elif item['type'] == 'function':
                    func_info = self.available_functions[item['function_name']]
                    func = func_info['function']
                    params = item['parameters']
                    result = func(**params)
                    if isinstance(result, list):
                        gcode_lines.extend(result)
                    else:
                        gcode_lines.append(str(result))
                
                gcode_lines.append("")  # Add blank line between sections
                
            except Exception as e:
                gcode_lines.append(f"; ERROR in {item['display_name']}: {e}")
        
        # Add footer
        gcode_lines.extend([
            "; End of toolpath",
            "M84  ; Turn off motors"
        ])
        
        return gcode_lines

    def preview_gcode(self):
        """Preview generated G-code"""
        if not self.toolpath_sequence:
            messagebox.showwarning("Warning", "Toolpath is empty!")
            return
        
        gcode_lines = self.generate_gcode()
        
        # Create preview window
        preview_window = tk.Toplevel(self.root)
        preview_window.title("G-Code Preview")
        preview_window.geometry("800x600")
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(preview_window)
        text_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD)
        text_widget.pack(fill='both', expand=True)
        
        # Insert G-code
        text_widget.insert(tk.END, '\n'.join(gcode_lines))
        text_widget.config(state='disabled')  # Make read-only

    def save_gcode(self):
        """Save G-code to file"""
        if not self.toolpath_sequence:
            messagebox.showwarning("Warning", "Toolpath is empty!")
            return
        
        try:
            # Create directory if it doesn't exist
            save_dir = self.save_directory.get()
            os.makedirs(save_dir, exist_ok=True)
            
            # Generate filename
            filename = self.filename.get()
            if not filename.endswith('.gcode'):
                filename += '.gcode'
            
            filepath = os.path.join(save_dir, filename)
            
            # Generate and save G-code
            gcode_lines = self.generate_gcode()
            
            with open(filepath, 'w') as f:
                f.write('\n'.join(gcode_lines))
            
            messagebox.showinfo("Success", f"G-code saved to:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save G-code:\n{e}")


def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    
    # Configure style
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configure colors and styles
    style.configure('Accent.TButton', background='#0078d4', foreground='white')
    
    app = GCodeGeneratorGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()