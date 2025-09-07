import matplotlib.pyplot as plt
import numpy as np

# Generate sample data
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)
y3 = np.tan(x)
y4 = np.exp(-x)

# Create a figure with subplots (2 rows, 2 columns)
fig, axes = plt.subplots(2, 2, figsize=(10, 8))

# Plot on each subplot
axes[0, 0].plot(x, y1, 'r')
axes[0, 0].set_title("Sine Wave")

axes[0, 1].plot(x, y2, 'g')
axes[0, 1].set_title("Cosine Wave")

axes[1, 0].plot(x, y3, 'b')
axes[1, 0].set_ylim(-5, 5)  # Limit y-axis for better visibility
axes[1, 0].set_title("Tangent Wave")

axes[1, 1].plot(x, y4, 'm')
axes[1, 1].set_title("Exponential Decay")

# Adjust layout
plt.tight_layout()
plt.show()
