"""

PD controller for pressure passed extrussion
- for pressure passed extrussion 
    - if printing measure the pressure based on the loadcell reading
    - feed to the pressure controller
    - Given current extrussion seed and pressure passed through, determin new extrussion seed

if pressure is too low:
- increase extrussion speed
if pressure is too high:
- decrease extrussion speed

"""

import time
import numpy as np

class PressureController:
    def __init__(self, kp=0.1, kd=0.05, min_extrusion=0.001, max_extrusion=0.2, 
                 pressure_tolerance=0.5, sample_time=0.01):
        """
        Initialize the pressure controller
        
        Args:
            kp: Proportional gain
            kd: Derivative gain  
            min_extrusion: Minimum extrusion rate
            max_extrusion: Maximum extrusion rate
            pressure_tolerance: Acceptable pressure deviation (N)
            sample_time: Controller sample time (seconds)
        """
        self.kp = kp
        self.kd = kd
        self.min_extrusion = min_extrusion
        self.max_extrusion = max_extrusion
        self.pressure_tolerance = pressure_tolerance
        self.sample_time = sample_time
        
        # Controller state
        self.prev_error = 0
        self.prev_time = time.time()
        self.integral = 0
        
        # Pressure history for smoothing
        self.pressure_history = []
        self.history_length = 5
        
    def calculate_extrusion_rate(self, current_pressure, target_pressure, current_extrusion_rate):
        """
        Calculate corrected extrusion rate based on pressure feedback
        
        Args:
            current_pressure: Current pressure reading from loadcell (N)
            target_pressure: Target pressure (N)
            current_extrusion_rate: Current extrusion rate
            
        Returns:
            corrected_extrusion_rate: New extrusion rate
        """
        current_time = time.time()
        dt = current_time - self.prev_time
        
        # Skip if not enough time has passed
        if dt < self.sample_time:
            return current_extrusion_rate
            
        # Calculate error
        error = target_pressure - current_pressure
        
        # Add to pressure history for smoothing
        self.pressure_history.append(current_pressure)
        if len(self.pressure_history) > self.history_length:
            self.pressure_history.pop(0)
        
        # Use smoothed pressure if we have enough history
        if len(self.pressure_history) >= 3:
            smoothed_pressure = np.mean(self.pressure_history)
            error = target_pressure - smoothed_pressure
        
        # Calculate derivative term
        if dt > 0:
            derivative = (error - self.prev_error) / dt
        else:
            derivative = 0
            
        # PD control law
        correction = self.kp * error + self.kd * derivative
        
        # Apply correction to extrusion rate
        corrected_extrusion_rate = current_extrusion_rate + correction
        
        # Clamp to limits
        corrected_extrusion_rate = max(self.min_extrusion, 
                                     min(self.max_extrusion, corrected_extrusion_rate))
        
        # Update state
        self.prev_error = error
        self.prev_time = current_time
        
        return corrected_extrusion_rate
    
    def is_pressure_stable(self, current_pressure, target_pressure):
        """
        Check if pressure is within acceptable tolerance
        
        Args:
            current_pressure: Current pressure reading (N)
            target_pressure: Target pressure (N)
            
        Returns:
            bool: True if pressure is stable
        """
        return abs(current_pressure - target_pressure) <= self.pressure_tolerance
    
    def reset(self):
        """Reset controller state"""
        self.prev_error = 0
        self.prev_time = time.time()
        self.integral = 0
        self.pressure_history = []
    
    def tune_gains(self, kp=None, kd=None):
        """
        Tune controller gains
        
        Args:
            kp: New proportional gain
            kd: New derivative gain
        """
        if kp is not None:
            self.kp = kp
        if kd is not None:
            self.kd = kd

def pressure_passed_extrusion(current_pressure, target_pressure, current_extrusion):
    """
    Calculate new extrusion rate based on pressure feedback
    
    Args:
        current_pressure: Current pressure reading from loadcell (N)
        target_pressure: Target pressure (N)
        current_extrusion: Current extrusion rate
        
    Returns:
        new_extrusion_rate: Corrected extrusion rate
    """
    # Create controller instance if not exists (static variable)
    if not hasattr(pressure_passed_extrusion, 'controller'):
        pressure_passed_extrusion.controller = PressureController()
    
    # Calculate corrected extrusion rate
    new_extrusion_rate = pressure_passed_extrusion.controller.calculate_extrusion_rate(
        current_pressure, target_pressure, current_extrusion
    )
    
    return new_extrusion_rate

# Example usage and testing
if __name__ == "__main__":
    # Create a test controller
    controller = PressureController(kp=0.1, kd=0.05)
    
    # Simulate pressure control
    target_pressure = 5.0  # N
    current_extrusion = 0.05
    
    print("Testing pressure controller:")
    print(f"Target pressure: {target_pressure} N")
    print(f"Initial extrusion rate: {current_extrusion}")
    print("-" * 50)
    
    # Simulate some pressure readings
    test_pressures = [3.0, 4.2, 4.8, 5.1, 5.3, 4.9, 5.0, 5.0]
    
    for i, pressure in enumerate(test_pressures):
        new_extrusion = controller.calculate_extrusion_rate(
            pressure, target_pressure, current_extrusion
        )
        current_extrusion = new_extrusion
        
        stable = controller.is_pressure_stable(pressure, target_pressure)
        print(f"Step {i+1}: Pressure={pressure:.1f}N, "
              f"Extrusion={new_extrusion:.4f}, Stable={stable}")





