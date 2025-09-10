#!/usr/bin/env python3
"""Test script to verify the fill_between fix."""

import numpy as np
import sys
import os

# Add the smpl directory to the path
sys.path.insert(0, '/home/apn/git/smpl')

try:
    import smpl.plot as plot
    import matplotlib.pyplot as plt
    
    # Test data
    x = np.linspace(0, 10, 20)
    y = np.sin(x)
    
    # Test the fix for fmt="fill"
    print("Testing fmt='fill' fix...")
    plt.figure()
    result = plot.plt_data(x, y, fmt="fill", label="Test Fill", data_color="blue", alpha=0.3)
    
    # This should not raise an AttributeError anymore
    color = result.get_color()
    print(f"Success! Got color: {color}")
    
    # Test calling plot.data with fmt="fill" 
    print("Testing plot.data with fmt='fill'...")
    plt.figure()
    plot.data(x, y, fmt="fill", label="Test Fill 2", data_color="red", alpha=0.3, show=False)
    print("Success! plot.data with fmt='fill' works")
    
    print("All tests passed!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
