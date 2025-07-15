#!/usr/bin/env python3
"""
3D Printer Configuration GUI
Provides interface for selecting printer/capacitor profiles and building toolpaths
Compatible with Raspberry Pi and Windows
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import os
from datetime import datetime
import sys
import inspect

# Import the existing modules
try:
    from configs import *
    from g_code_comands import *
except ImportError as e:
    messagebox.showerror("Import Error", f"Failed to import required modules: {e}")
    sys.exit(1)

class PrinterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Printer Configuration & Toolpath Builder")
        self.root.geometry("1000x800")
        
        # Variables
        self.selected_printer = tk.StringVar()
        self.selected_capacitor = tk.StringVar()
        self.bed_height = tk.DoubleVar(value=1.0)
        self.print_height = tk.DoubleVar(value=1.5)
        
        # Current configurations
        self.current_printer = None
        self.current_capacitor = None
        self.toolpath = []
        
        # Load available profiles
        self.load_profiles()
        
        # Create GUI
        self.create_widgets()
        
        # Set default selections
        if self.printer_profiles:
            self.selected_printer.set(list(self.printer_profiles.keys())[0])
            self.on_printer_change()
        if self.capacitor_profiles:
            self.selected_capacitor.set(list(self.capacitor_profiles.keys())[0])
            self.on_capacitor_change()

    def load_profiles(self):
        """Load all available printer and capacitor profiles from configs.py"""
        
        # Load printer profiles
        self.printer_profiles = {}
        for name, obj in globals().items():
            if isinstance(obj, Printer):
                self.printer_profiles[name] = obj
        
        # Load capacitor profiles  
        self.capacitor_profiles = {}
        for name, obj in globals().items():
            if isinstance(obj, Capacitor):
                self.capacitor_profiles[name] = obj
                
        # Load available G-code functions
        self.gcode_functions = {}
        gcode_module = sys.modules['g_code_comands']
        
        # Get functions that generate toolpath patterns
        pattern_functions = [
            'printPrimeLine', 'printCap', 'printCap_contact_patch', 'printLayers',
            'singleLineCap', 'singleLineCap_left', 'singleLineCap_right',
            'square_wave', 'contracting_square_wave', 'lattice', 'lattice_3d',
            'straight_line', 'ZB2_test'
        ]
        
        for func_name in pattern_functions:
            if hasattr(gcode_module, func_name):
                func = getattr(gcode_module, func_name)
                if callable(func):
                    # Get function signature for parameter input
                    sig = inspect.signature(func)
                    self.gcode_functions[func_name] = {
                        'function': func,
                        'signature': sig,
                        'parameters': list(sig.parameters.keys())
                    }

    def create_widgets(self):
        """Create the main GUI widgets"""
        
        # Create main notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Configuration Tab
        config_frame = ttk.Frame(notebook)
        notebook.add(config_frame, text="Configuration")
        self.create_config_tab(config_frame)
        
        # Toolpath Tab
        toolpath_frame = ttk.Frame(notebook)
        notebook.add(toolpath_frame, text="Toolpath Builder")
        self.create_toolpath_tab(toolpath_frame)
        
        # Preview Tab
        preview_frame = ttk.Frame(notebook)
        notebook.add(preview_frame, text="Preview & Export")
        self.create_preview_tab(preview_frame)

    def create_config_tab(self, parent):
        """Create the configuration tab"""
        
        # Printer Selection
        printer_frame = ttk.LabelFrame(parent, text="Printer Profile", padding=10)
        printer_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(printer_frame, text="Select Printer Profile:").pack(anchor='w')
        printer_combo = ttk.Combobox(printer_frame, textvariable=self.selected_printer,
                                   values=list(self.printer_profiles.keys()), state='readonly')
        printer_combo.pack(fill='x', pady=5)
        printer_combo.bind('<<ComboboxSelected>>', lambda e: self.on_printer_change())
        
        # Printer details frame
        self.printer_details_frame = ttk.Frame(printer_frame)
        self.printer_details_frame.pack(fill='x', pady=5)
        
        # Capacitor Selection
        cap_frame = ttk.LabelFrame(parent, text="Capacitor Profile", padding=10)
        cap_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(cap_frame, text="Select Capacitor Profile:").pack(anchor='w')
        cap_combo = ttk.Combobox(cap_frame, textvariable=self.selected_capacitor,
                               values=list(self.capacitor_profiles.keys()), state='readonly')
        cap_combo.pack(fill='x', pady=5)
        cap_combo.bind('<<ComboboxSelected>>', lambda e: self.on_capacitor_change())
        
        # Capacitor details frame
        self.capacitor_details_frame = ttk.Frame(cap_frame)
        self.capacitor_details_frame.pack(fill='x', pady=5)
        
        # Height Configuration
        height_frame = ttk.LabelFrame(parent, text="Height Configuration", padding=10)
        height_frame.pack(fill='x', padx=5, pady=5)
        
        # Bed Height
        bed_frame = ttk.Frame(height_frame)
        bed_frame.pack(fill='x', pady=2)
        ttk.Label(bed_frame, text="Bed Height (mm):").pack(side='left')
        bed_spinbox = ttk.Spinbox(bed_frame, from_=0.1, to=10.0, increment=0.1,
                                textvariable=self.bed_height, width=10)
        bed_spinbox.pack(side='right')
        
        # Print Height
        print_frame = ttk.Frame(height_frame)
        print_frame.pack(fill='x', pady=2)
        ttk.Label(print_frame, text="Print Height (mm):").pack(side='left')
        print_spinbox = ttk.Spinbox(print_frame, from_=0.1, to=10.0, increment=0.1,
                                  textvariable=self.print_height, width=10)
        print_spinbox.pack(side='right')
        
        # Apply button
        ttk.Button(height_frame, text="Apply Height Settings",
                  command=self.apply_height_settings).pack(pady=5)

    def create_toolpath_tab(self, parent):
        """Create the toolpath builder tab"""
        
        # Left side - Function selection
        left_frame = ttk.Frame(parent)
        left_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        # Function selection
        func_frame = ttk.LabelFrame(left_frame, text="Available Functions", padding=10)
        func_frame.pack(fill='x', pady=5)
        
        self.function_var = tk.StringVar()
        func_combo = ttk.Combobox(func_frame, textvariable=self.function_var,
                                values=list(self.gcode_functions.keys()), state='readonly')
        func_combo.pack(fill='x', pady=5)
        func_combo.bind('<<ComboboxSelected>>', lambda e: self.on_function_change())
        
        # Parameters frame
        self.params_frame = ttk.LabelFrame(left_frame, text="Function Parameters", padding=10)
        self.params_frame.pack(fill='both', expand=True, pady=5)
        
        # Add to toolpath button
        ttk.Button(left_frame, text="Add to Toolpath", 
                  command=self.add_to_toolpath).pack(pady=5)
        
        # Right side - Toolpath list
        right_frame = ttk.Frame(parent)
        right_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        toolpath_frame = ttk.LabelFrame(right_frame, text="Current Toolpath", padding=10)
        toolpath_frame.pack(fill='both', expand=True)
        
        # Toolpath listbox with scrollbar
        list_frame = ttk.Frame(toolpath_frame)
        list_frame.pack(fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.toolpath_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.toolpath_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.toolpath_listbox.yview)
        
        # Toolpath controls
        controls_frame = ttk.Frame(toolpath_frame)
        controls_frame.pack(fill='x', pady=5)
        
        ttk.Button(controls_frame, text="Move Up", 
                  command=self.move_toolpath_up).pack(side='left', padx=2)
        ttk.Button(controls_frame, text="Move Down", 
                  command=self.move_toolpath_down).pack(side='left', padx=2)
        ttk.Button(controls_frame, text="Remove", 
                  command=self.remove_toolpath_item).pack(side='left', padx=2)
        ttk.Button(controls_frame, text="Clear All", 
                  command=self.clear_toolpath).pack(side='left', padx=2)

    def create_preview_tab(self, parent):
        """Create the preview and export tab"""
        
        # Preview text area
        preview_frame = ttk.LabelFrame(parent, text="G-Code Preview", padding=10)
        preview_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=20)
        self.preview_text.pack(fill='both', expand=True)
        
        # Control buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(button_frame, text="Generate Preview", 
                  command=self.generate_preview).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Save Toolpath", 
                  command=self.save_toolpath).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Load Toolpath", 
                  command=self.load_toolpath).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Export G-Code", 
                  command=self.export_gcode).pack(side='left', padx=5)

    def on_printer_change(self):
        """Handle printer selection change"""
        printer_name = self.selected_printer.get()
        if printer_name and printer_name in self.printer_profiles:
            self.current_printer = self.printer_profiles[printer_name]
            self.update_printer_details()

    def on_capacitor_change(self):
        """Handle capacitor selection change"""
        cap_name = self.selected_capacitor.get()
        if cap_name and cap_name in self.capacitor_profiles:
            self.current_capacitor = self.capacitor_profiles[cap_name]
            self.update_capacitor_details()

    def update_printer_details(self):
        """Update printer details display"""
        # Clear existing details
        for widget in self.printer_details_frame.winfo_children():
            widget.destroy()
            
        if self.current_printer:
            details = [
                f"Extrusion: {self.current_printer.extrusion}",
                f"Retraction: {self.current_printer.retraction}",
                f"Feed Rate: {self.current_printer.feed_rate}",
                f"Movement Speed: {self.current_printer.movement_speed}",
                f"Print Height: {self.current_printer.print_height}",
                f"Bed Height: {self.current_printer.bed_height}",
                f"Z Hop: {self.current_printer.z_hop}",
                f"Line Gap: {self.current_printer.line_gap}"
            ]
            
            for detail in details:
                ttk.Label(self.printer_details_frame, text=detail).pack(anchor='w')

    def update_capacitor_details(self):
        """Update capacitor details display"""
        # Clear existing details
        for widget in self.capacitor_details_frame.winfo_children():
            widget.destroy()
            
        if self.current_capacitor:
            details = [
                f"Stem Length: {self.current_capacitor.stem_len}",
                f"Arm Length: {self.current_capacitor.arm_len}",
                f"Arm Count: {self.current_capacitor.arm_count}",
                f"Gap: {self.current_capacitor.gap}",
                f"Arm Gap: {self.current_capacitor.arm_gap}",
                f"Contact Patch Width: {self.current_capacitor.contact_patch_width}"
            ]
            
            for detail in details:
                ttk.Label(self.capacitor_details_frame, text=detail).pack(anchor='w')

    def apply_height_settings(self):
        """Apply height settings to current printer"""
        if self.current_printer:
            self.current_printer.set_print_height(
                self.print_height.get(), 
                self.bed_height.get()
            )
            self.update_printer_details()
            messagebox.showinfo("Success", "Height settings applied!")
        else:
            messagebox.showwarning("Warning", "Please select a printer profile first!")

    def on_function_change(self):
        """Handle function selection change"""
        func_name = self.function_var.get()
        if func_name and func_name in self.gcode_functions:
            self.create_parameter_inputs(func_name)

    def create_parameter_inputs(self, func_name):
        """Create input fields for function parameters"""
        # Clear existing parameter inputs
        for widget in self.params_frame.winfo_children():
            widget.destroy()
            
        func_info = self.gcode_functions[func_name]
        parameters = func_info['parameters']
        signature = func_info['signature']
        
        self.param_vars = {}
        
        # Skip 'prnt' and 'cap' parameters as they're provided automatically
        skip_params = ['prnt', 'cap']
        
        for param in parameters:
            if param in skip_params:
                continue
                
            param_info = signature.parameters[param]
            
            frame = ttk.Frame(self.params_frame)
            frame.pack(fill='x', pady=2)
            
            # Parameter label
            ttk.Label(frame, text=f"{param}:").pack(side='left', padx=(0, 5))
            
            # Determine input type based on default value or annotation
            default_value = param_info.default if param_info.default != inspect.Parameter.empty else ""
            
            if isinstance(default_value, bool):
                # Boolean parameter - use checkbox
                var = tk.BooleanVar(value=default_value)
                ttk.Checkbutton(frame, variable=var).pack(side='right')
            elif isinstance(default_value, (int, float)) or param in ['start_x', 'start_y', 'x', 'y', 'z', 'length', 'width', 'height', 'spacing']:
                # Numeric parameter - use spinbox
                var = tk.DoubleVar(value=float(default_value) if default_value != "" else 0.0)
                ttk.Spinbox(frame, from_=-1000, to=1000, increment=0.1, 
                          textvariable=var, width=10).pack(side='right')
            else:
                # String parameter - use entry
                var = tk.StringVar(value=str(default_value) if default_value != "" else "")
                ttk.Entry(frame, textvariable=var, width=15).pack(side='right')
            
            self.param_vars[param] = var

    def add_to_toolpath(self):
        """Add selected function with parameters to toolpath"""
        func_name = self.function_var.get()
        if not func_name:
            messagebox.showwarning("Warning", "Please select a function!")
            return
            
        if not self.current_printer:
            messagebox.showwarning("Warning", "Please select a printer profile!")
            return
            
        # Build parameter dictionary
        params = {}
        for param, var in self.param_vars.items():
            params[param] = var.get()
            
        # Add required parameters
        params['prnt'] = self.current_printer
        if 'cap' in self.gcode_functions[func_name]['parameters']:
            if not self.current_capacitor:
                messagebox.showwarning("Warning", "This function requires a capacitor profile!")
                return
            params['cap'] = self.current_capacitor
        
        # Add to toolpath
        toolpath_item = {
            'function': func_name,
            'parameters': params.copy()  # Store copy for regeneration
        }
        
        self.toolpath.append(toolpath_item)
        
        # Update listbox display
        display_text = f"{func_name}({', '.join(f'{k}={v}' for k, v in params.items() if k not in ['prnt', 'cap'])})"
        self.toolpath_listbox.insert(tk.END, display_text)
        
        messagebox.showinfo("Success", f"Added {func_name} to toolpath!")

    def move_toolpath_up(self):
        """Move selected toolpath item up"""
        selection = self.toolpath_listbox.curselection()
        if selection and selection[0] > 0:
            idx = selection[0]
            # Swap items
            self.toolpath[idx], self.toolpath[idx-1] = self.toolpath[idx-1], self.toolpath[idx]
            self.refresh_toolpath_display()
            self.toolpath_listbox.selection_set(idx-1)

    def move_toolpath_down(self):
        """Move selected toolpath item down"""
        selection = self.toolpath_listbox.curselection()
        if selection and selection[0] < len(self.toolpath) - 1:
            idx = selection[0]
            # Swap items
            self.toolpath[idx], self.toolpath[idx+1] = self.toolpath[idx+1], self.toolpath[idx]
            self.refresh_toolpath_display()
            self.toolpath_listbox.selection_set(idx+1)

    def remove_toolpath_item(self):
        """Remove selected toolpath item"""
        selection = self.toolpath_listbox.curselection()
        if selection:
            idx = selection[0]
            del self.toolpath[idx]
            self.refresh_toolpath_display()

    def clear_toolpath(self):
        """Clear all toolpath items"""
        if messagebox.askyesno("Confirm", "Clear all toolpath items?"):
            self.toolpath.clear()
            self.refresh_toolpath_display()

    def refresh_toolpath_display(self):
        """Refresh the toolpath listbox display"""
        self.toolpath_listbox.delete(0, tk.END)
        for item in self.toolpath:
            func_name = item['function']
            params = item['parameters']
            display_text = f"{func_name}({', '.join(f'{k}={v}' for k, v in params.items() if k not in ['prnt', 'cap'])})"
            self.toolpath_listbox.insert(tk.END, display_text)

    def generate_preview(self):
        """Generate G-code preview"""
        if not self.toolpath:
            messagebox.showwarning("Warning", "Toolpath is empty!")
            return
            
        self.preview_text.delete(1.0, tk.END)
        
        try:
            # Generate header
            gcode_lines = [
                "; G-Code generated by 3D Printer GUI",
                f"; Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"; Printer: {self.selected_printer.get()}",
                f"; Capacitor: {self.selected_capacitor.get()}",
                ""
            ]
            
            # Add home command
            gcode_lines.extend(home())
            gcode_lines.append("")
            
            # Generate G-code for each toolpath item
            for item in self.toolpath:
                func_name = item['function']
                params = item['parameters']
                
                # Get function and call it
                func = self.gcode_functions[func_name]['function']
                result = func(**params)
                
                if isinstance(result, list):
                    gcode_lines.extend(result)
                else:
                    gcode_lines.append(str(result))
                gcode_lines.append("")
            
            # Add footer
            gcode_lines.extend([
                "; End of toolpath",
                "M84  ; Turn off motors"
            ])
            
            # Display in preview
            self.preview_text.insert(tk.END, '\n'.join(gcode_lines))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating preview: {e}")

    def save_toolpath(self):
        """Save current toolpath configuration"""
        if not self.toolpath:
            messagebox.showwarning("Warning", "Toolpath is empty!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                config = {
                    'printer': self.selected_printer.get(),
                    'capacitor': self.selected_capacitor.get(),
                    'bed_height': self.bed_height.get(),
                    'print_height': self.print_height.get(),
                    'toolpath': self.toolpath
                }
                
                with open(filename, 'w') as f:
                    json.dump(config, f, indent=2, default=str)
                    
                messagebox.showinfo("Success", f"Toolpath saved to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error saving toolpath: {e}")

    def load_toolpath(self):
        """Load toolpath configuration"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    config = json.load(f)
                
                # Restore configuration
                if 'printer' in config:
                    self.selected_printer.set(config['printer'])
                    self.on_printer_change()
                    
                if 'capacitor' in config:
                    self.selected_capacitor.set(config['capacitor'])
                    self.on_capacitor_change()
                    
                if 'bed_height' in config:
                    self.bed_height.set(config['bed_height'])
                    
                if 'print_height' in config:
                    self.print_height.set(config['print_height'])
                    
                if 'toolpath' in config:
                    self.toolpath = config['toolpath']
                    self.refresh_toolpath_display()
                
                messagebox.showinfo("Success", f"Toolpath loaded from {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error loading toolpath: {e}")

    def export_gcode(self):
        """Export toolpath as G-code file"""
        if not self.toolpath:
            messagebox.showwarning("Warning", "Toolpath is empty!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".gcode",
            filetypes=[("G-code files", "*.gcode"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.generate_preview()  # Generate the preview first
                gcode_content = self.preview_text.get(1.0, tk.END)
                
                with open(filename, 'w') as f:
                    f.write(gcode_content)
                    
                messagebox.showinfo("Success", f"G-code exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error exporting G-code: {e}")


def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = PrinterGUI(root)
    
    # Configure window icon and properties
    try:
        # Set window to be resizable
        root.resizable(True, True)
        
        # Center window on screen
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        root.geometry(f"+{x}+{y}")
        
    except Exception as e:
        print(f"Warning: Could not set window properties: {e}")
    
    root.mainloop()


if __name__ == "__main__":
    main()