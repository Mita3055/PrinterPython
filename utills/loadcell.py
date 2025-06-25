import time
import csv
import os
import argparse
import numpy as np
from datetime import datetime
from hx711 import HX711  # Make sure you have installed the HX711 library

# Set up HX711 (update pin numbers as needed for your wiring)
DT_PIN = 5   # Example GPIO pin for DT
SCK_PIN = 6  # Example GPIO pin for SCK

# Global variables
hx = None
_last_call = 0
calibration_data = {
    'background_mean': 0,
    'background_std': 0,
    'one_kg_reading': 0,
    'two_kg_reading': 0,
    'calibration_factor': 0,
    'calibration_date': None
}

def initialize_loadcell():
    """Initialize the HX711 load cell"""
    global hx
    try:
        hx = HX711(DT_PIN, SCK_PIN)
        hx.set_reading_format("MSB", "MSB")
        hx.reset()
        time.sleep(1)
        
        # Tare the scale (zero it)
        hx.tare()
        time.sleep(1)
        print("✓ Load cell initialized and tared")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize load cell: {e}")
        return False

def record_background_noise(duration=30, sample_rate=0.1):
    """Record background noise for specified duration"""
    global hx
    
    if hx is None:
        print("Error: Load cell not initialized")
        return None
        
    print(f"\nRecording background noise for {duration} seconds...")
    print("Make sure the load cell is empty and stable")
    
    # Create loadcell directory if it doesn't exist
    os.makedirs('loadcell', exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"loadcell/background_noise_{timestamp}.csv"
    
    readings = []
    start_time = time.time()
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'raw_reading', 'elapsed_time'])
        
        while time.time() - start_time < duration:
            try:
                raw_reading = hx.get_weight(1)
                elapsed = time.time() - start_time
                readings.append(raw_reading)
                
                writer.writerow([time.time(), raw_reading, elapsed])
                csvfile.flush()
                
                # Progress indicator
                progress = (elapsed / duration) * 100
                print(f"\rProgress: {progress:.1f}%", end='', flush=True)
                
                time.sleep(sample_rate)
                
            except Exception as e:
                print(f"\nError reading load cell: {e}")
                break
    
    print(f"\n✓ Background noise recorded and saved to {filename}")
    
    # Calculate statistics
    if readings:
        calibration_data['background_mean'] = np.mean(readings)
        calibration_data['background_std'] = np.std(readings)
        print(f"Background mean: {calibration_data['background_mean']:.2f}")
        print(f"Background std: {calibration_data['background_std']:.2f}")
    
    return filename

def get_weight_reading(weight_name, target_weight):
    """Get stable weight reading from user"""
    global hx
    
    if hx is None:
        print("Error: Load cell not initialized")
        return None
        
    print(f"\nPlease place a {target_weight}kg weight on the load cell")
    input("Press Enter when the weight is stable...")
    
    # Take multiple readings for stability
    readings = []
    print("Taking readings...")
    
    for i in range(10):
        try:
            reading = hx.get_weight(5)
            readings.append(reading)
            print(f"Reading {i+1}: {reading:.2f}")
            time.sleep(0.5)
        except Exception as e:
            print(f"Error reading load cell: {e}")
            return None
    
    # Calculate average reading
    avg_reading = np.mean(readings)
    std_reading = np.std(readings)
    
    print(f"Average reading: {avg_reading:.2f} ± {std_reading:.2f}")
    
    # Store in calibration data
    if weight_name == "1kg":
        calibration_data['one_kg_reading'] = avg_reading
    elif weight_name == "2kg":
        calibration_data['two_kg_reading'] = avg_reading
    
    return avg_reading

def calculate_calibration_factor():
    """Calculate calibration factor from 1kg and 2kg readings"""
    if calibration_data['one_kg_reading'] == 0 or calibration_data['two_kg_reading'] == 0:
        print("Error: Missing weight readings for calibration")
        return False
    
    # Calculate factor using 1kg reading
    calibration_data['calibration_factor'] = calibration_data['one_kg_reading']
    calibration_data['calibration_date'] = datetime.now().isoformat()
    
    print(f"\nCalibration factor: {calibration_data['calibration_factor']:.2f}")
    print(f"1kg reading: {calibration_data['one_kg_reading']:.2f}")
    print(f"2kg reading: {calibration_data['two_kg_reading']:.2f}")
    
    return True

def save_calibration():
    """Save calibration data to file"""
    os.makedirs('loadcell', exist_ok=True)
    
    # Save calibration data
    calibration_file = 'loadcell/calibration_data.json'
    import json
    
    with open(calibration_file, 'w') as f:
        json.dump(calibration_data, f, indent=2)
    
    print(f"✓ Calibration data saved to {calibration_file}")
    
    # Save calibration summary
    summary_file = 'loadcell/calibration_summary.txt'
    with open(summary_file, 'w') as f:
        f.write("Load Cell Calibration Summary\n")
        f.write("=============================\n\n")
        f.write(f"Calibration Date: {calibration_data['calibration_date']}\n")
        f.write(f"Background Mean: {calibration_data['background_mean']:.2f}\n")
        f.write(f"Background Std: {calibration_data['background_std']:.2f}\n")
        f.write(f"1kg Reading: {calibration_data['one_kg_reading']:.2f}\n")
        f.write(f"2kg Reading: {calibration_data['two_kg_reading']:.2f}\n")
        f.write(f"Calibration Factor: {calibration_data['calibration_factor']:.2f}\n")
    
    print(f"✓ Calibration summary saved to {summary_file}")

def load_calibration():
    """Load calibration data from file"""
    global calibration_data
    calibration_file = 'loadcell/calibration_data.json'
    
    if os.path.exists(calibration_file):
        import json
        with open(calibration_file, 'r') as f:
            calibration_data = json.load(f)
        print("✓ Calibration data loaded")
        return True
    else:
        print("No calibration data found. Please run calibration first.")
        return False

def getLoad():
    """Get current weight reading in kg"""
    global _last_call, hx
    
    if hx is None:
        print("Error: Load cell not initialized")
        return [0.0, 0.0, 0.0, 0.0]
    
    if calibration_data['calibration_factor'] == 0:
        print("Error: Load cell not calibrated")
        return [0.0, 0.0, 0.0, 0.0]
    
    now = time.time()
    if now - _last_call < 0.01:  # 10ms = 0.01s
        time.sleep(0.01 - (now - _last_call))
    _last_call = time.time()
    
    try:
        raw = hx.get_weight(5)
        # Convert raw value to kg using calibration factor
        weight_kg = raw / calibration_data['calibration_factor']
        weight_lbs = weight_kg * 2.20462
        weight_newtons = weight_kg * 9.80665
        return [weight_newtons, weight_lbs, weight_kg, raw]
    except Exception as e:
        print(f"Error reading load cell: {e}")
        return [0.0, 0.0, 0.0, 0.0]

def run_calibration():
    """Run the full calibration process"""
    print("Load Cell Calibration")
    print("=====================")
    
    # Initialize load cell
    if not initialize_loadcell():
        return False
    
    # Step 1: Record background noise
    record_background_noise(duration=30)
    
    # Step 2: Get 1kg reading
    one_kg_reading = get_weight_reading("1kg", 1)
    if one_kg_reading is None:
        print("Failed to get 1kg reading")
        return False
    
    # Step 3: Get 2kg reading
    two_kg_reading = get_weight_reading("2kg", 2)
    if two_kg_reading is None:
        print("Failed to get 2kg reading")
        return False
    
    # Step 4: Calculate calibration factor
    if not calculate_calibration_factor():
        return False
    
    # Step 5: Save calibration data
    save_calibration()
    
    print("\n✓ Calibration completed successfully!")
    return True

def main():
    parser = argparse.ArgumentParser(description='Load Cell Control and Calibration')
    parser.add_argument('--calibrate', action='store_true', 
                       help='Run calibration process')
    parser.add_argument('--test', action='store_true',
                       help='Test current calibration')
    
    args = parser.parse_args()
    
    if args.calibrate:
        run_calibration()
    elif args.test:
        if initialize_loadcell() and load_calibration():
            print("\nTesting load cell readings...")
            print("Place weights on the load cell to test:")
            try:
                while True:
                    weight_data = getLoad()
                    print(f"Weight: {weight_data[2]:.3f} kg ({weight_data[1]:.2f} lbs)")
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nTest stopped")
    else:
        # Default behavior - initialize and load calibration
        if initialize_loadcell() and load_calibration():
            print("Load cell ready for use")
        else:
            print("Failed to initialize load cell")

if __name__ == "__main__":
    main()


