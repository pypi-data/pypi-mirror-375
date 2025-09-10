#!/usr/bin/env python3
"""Test script to verify the new ratio feature works correctly."""

import numpy as np
import matplotlib.pyplot as plt
import smpl.plot as splot

# Create test data
x = np.linspace(0, 10, 50)
y_true = 2 * x + 3
y_data = y_true + np.random.normal(0, 0.5, len(x))  # Add some noise

# Define a linear function for fitting
def linear_func(x, a, b):
    return a * x + b

# Test the ratio feature
print("Testing ratio feature...")

# Test 1: Basic ratio plot
fig1 = plt.figure(figsize=(10, 8))
result = splot.plot(x, y_data, linear_func, 
                   params=[2.1, 2.9],  # Initial guess close to true values
                   ratio=True, 
                   ratio_err=True,
                   title="Test: Data vs Fit with Ratio Plot",
                   xlabel="X values",
                   ylabel="Y values",
                   save="test_ratio_plot.png")

print("Ratio plot test completed. Check 'test_ratio_plot.png' for output.")

# Test 2: Compare with residue plot  
fig2 = plt.figure(figsize=(10, 8))
result = splot.plot(x, y_data, linear_func, 
                   params=[2.1, 2.9],
                   residue=True, 
                   residue_err=True,
                   title="Test: Data vs Fit with Residue Plot",
                   xlabel="X values", 
                   ylabel="Y values",
                   save="test_residue_plot.png")

print("Residue plot test completed. Check 'test_residue_plot.png' for comparison.")
print("Test completed successfully!")
