#!/usr/bin/env python3
"""
Test script for loadcell calibration functionality
This script tests the calibration logic without requiring actual hardware
"""

import os
import json
import tempfile
import shutil
from unittest.mock import Mock, patch

# Import the loadcell module
import loadcell

def test_calibration_data_structure():
    """Test that calibration data structure is correct"""
    print("Testing calibration data structure...")
    
    expected_keys = ['background_mean', 'background_std', 'one_kg_reading', 
                    'two_kg_reading', 'calibration_factor', 'calibration_date']
    
    for key in expected_keys:
        assert key in loadcell.calibration_data, f"Missing key: {key}"
    
    print("✓ Calibration data structure is correct")

def test_save_and_load_calibration():
    """Test saving and loading calibration data"""
    print("Testing save and load calibration...")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        original_loadcell_dir = 'loadcell'
        
        # Mock the loadcell directory
        if os.path.exists(original_loadcell_dir):
            shutil.move(original_loadcell_dir, f"{original_loadcell_dir}_backup")
        
        try:
            # Set up test calibration data
            test_data = {
                'background_mean': 100.5,
                'background_std': 2.3,
                'one_kg_reading': 1000.0,
                'two_kg_reading': 2000.0,
                'calibration_factor': 1000.0,
                'calibration_date': '2024-01-01T00:00:00'
            }
            
            # Test save_calibration function
            loadcell.calibration_data.update(test_data)
            loadcell.save_calibration()
            
            # Verify files were created
            assert os.path.exists('loadcell/calibration_data.json')
            assert os.path.exists('loadcell/calibration_summary.txt')
            
            # Test load_calibration function
            loadcell.calibration_data.clear()
            loadcell.load_calibration()
            
            # Verify data was loaded correctly
            for key, value in test_data.items():
                if key != 'calibration_date':  # Skip date comparison
                    assert loadcell.calibration_data[key] == value, f"Data mismatch for {key}"
            
            print("✓ Save and load calibration works correctly")
            
        finally:
            # Clean up
            if os.path.exists('loadcell'):
                shutil.rmtree('loadcell')
            if os.path.exists(f"{original_loadcell_dir}_backup"):
                shutil.move(f"{original_loadcell_dir}_backup", original_loadcell_dir)

def test_getLoad_function():
    """Test the getLoad function with mock data"""
    print("Testing getLoad function...")
    
    # Mock the HX711 object
    mock_hx = Mock()
    mock_hx.get_weight.return_value = 1500.0  # Simulate 1.5kg reading
    
    # Set up calibration data
    loadcell.calibration_data['calibration_factor'] = 1000.0
    
    with patch('loadcell.hx', mock_hx):
        result = loadcell.getLoad()
        
        # Verify return format
        assert len(result) == 4, "getLoad should return 4 values"
        assert isinstance(result[0], float), "Weight in newtons should be float"
        assert isinstance(result[1], float), "Weight in pounds should be float"
        assert isinstance(result[2], float), "Weight in kg should be float"
        assert isinstance(result[3], float), "Raw reading should be float"
        
        # Verify calculations
        expected_kg = 1500.0 / 1000.0  # 1.5 kg
        expected_lbs = expected_kg * 2.20462
        expected_newtons = expected_kg * 9.80665
        
        assert abs(result[2] - expected_kg) < 0.001, "Kg calculation incorrect"
        assert abs(result[1] - expected_lbs) < 0.001, "Pounds calculation incorrect"
        assert abs(result[0] - expected_newtons) < 0.001, "Newtons calculation incorrect"
        assert result[3] == 1500.0, "Raw reading should match input"
        
        print("✓ getLoad function works correctly")

def test_error_handling():
    """Test error handling in loadcell functions"""
    print("Testing error handling...")
    
    # Test getLoad with uninitialized load cell
    with patch('loadcell.hx', None):
        result = loadcell.getLoad()
        assert result == [0.0, 0.0, 0.0, 0.0], "Should return zeros when hx is None"
    
    # Test getLoad with uncalibrated load cell
    mock_hx = Mock()
    loadcell.calibration_data['calibration_factor'] = 0
    
    with patch('loadcell.hx', mock_hx):
        result = loadcell.getLoad()
        assert result == [0.0, 0.0, 0.0, 0.0], "Should return zeros when not calibrated"
    
    print("✓ Error handling works correctly")

def main():
    """Run all tests"""
    print("Load Cell Calibration Tests")
    print("===========================")
    
    try:
        test_calibration_data_structure()
        test_save_and_load_calibration()
        test_getLoad_function()
        test_error_handling()
        
        print("\n✓ All tests passed!")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main() 