import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --- 1. LOAD DATA ---
filename = 'angle_dependence.csv' # Filename from your screenshot

try:
    df = pd.read_csv(filename)
except Exception as e:
    print(f"Error: {e}")
    exit()

# --- 2. CALCULATE FLUX ---
detector_area_cm2 = 62.5
df['Flux'] = df['Rate'] / detector_area_cm2
df['Flux_Error'] = df['Error'] / detector_area_cm2

# --- 3. PLOT ---
plt.figure(figsize=(8, 6))

plt.errorbar(df['Angle'], df['Flux'], yerr=df['Flux_Error'], 
             fmt='o', color='black', ecolor='#D32F2F', 
             elinewidth=1.2, capsize=3, markersize=5,
             label='Experimental Flux', zorder=5)

# --- 4. FORMATTING ---
plt.title('Cosmic Ray Muon Flux vs. Zenith Angle', fontsize=14)
# Use \mathbf{...} to make the math bold
plt.xlabel(r'Zenith Angle $\mathbf{\theta}$ (degrees)', fontsize=16, fontweight='bold')
plt.ylabel(r'Flux ($\mathbf{s^{-1} cm^{-2}}$)', fontsize=16, fontweight='bold')
# Set axis limits
plt.xlim(-5, 95)
plt.ylim(0, df['Flux'].max() * 1.1) # Auto-scale Y axis with 10% headroom

# Add grid
plt.grid(True, linestyle='--', alpha=0.6)

# Format Y-axis to scientific notation (e.g., 2.5 x 10^-3)
plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0))

plt.legend(fontsize=14)
plt.tight_layout()

# Save
plt.savefig('fig_Y_flux_vs_angle.png', dpi=300)
print("Saved 'fig_Y_flux_vs_angle.png'")
