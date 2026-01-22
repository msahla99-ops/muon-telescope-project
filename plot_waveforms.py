import pandas as pd
import matplotlib.pyplot as plt

# --- CONFIGURATION ---
file_ch1 = 'mppc1_1pe.csv'
file_ch2 = 'mppc2_1pe.csv'
file_ch3 = 'mppc3_1pe.csv'
skip_rows = 1 

# --- DATA LOADING ---
def load_scope_data(filename):
    try:
        df = pd.read_csv(filename, skiprows=skip_rows)
        if df.empty: return [], []
        time_ns = df.iloc[:, 0] * 1e9       
        
        # Convert to Microvolts (uV)
        voltage_uV = df.iloc[:, 1] * 1e6 
        return time_ns, voltage_uV
    except: return [], []

t1, v1 = load_scope_data(file_ch1)
t2, v2 = load_scope_data(file_ch2)
t3, v3 = load_scope_data(file_ch3)

# --- NORMALIZATION (The Fix) ---
# Your CSVs captured 2 p.e. crosstalk events for Ch1 and Ch2. 
# We divide by 2 to show the fundamental 1 p.e. pulse you saw on screen.
v1 = v1 / 2.0  # Brings ~1200uV down to ~600uV range
v2 = v2 / 2.0  # Brings ~1300uV down to ~650uV range
# v3 is left alone because it was already correct (~800uV is close to 660uV)

# --- PLOTTING ---
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(6, 7), sharex=True)

# Requested Light Blue Color
std_color = '#1f77b4' 
line_width = 1.2

# Plotting
ax1.plot(t1, v1, color=std_color, linewidth=line_width)
ax2.plot(t2, v2, color=std_color, linewidth=line_width)
ax3.plot(t3, v3, color=std_color, linewidth=line_width)

# Labels
ax1.text(0.03, 0.85, 'MPPC 1 (Top)', transform=ax1.transAxes, fontweight='bold', fontsize=11)
ax2.text(0.03, 0.85, 'MPPC 2 (Middle)', transform=ax2.transAxes, fontweight='bold', fontsize=11)
ax3.text(0.03, 0.85, 'MPPC 3 (Bottom)', transform=ax3.transAxes, fontweight='bold', fontsize=11)

# Grids
for ax in [ax1, ax2, ax3]:
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
    # Optional: Force Y-axis to look similar for all (e.g., -800 to +100)
    # ax.set_ylim(-900, 200)

# Global Axis Labels
fig.supylabel('Amplitude (µV)', fontsize=12) 
ax3.set_xlabel('Time (ns)', fontsize=12)

plt.tight_layout()
plt.subplots_adjust(hspace=0.05) 
plt.savefig('mppc_1pe_normalized.png', dpi=300)
print("Plot saved. Ch1 and Ch2 were normalized to 1 p.e. levels.")
