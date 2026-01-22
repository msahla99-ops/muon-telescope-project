import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# --- 1. CONFIGURATION ---
filename = '3ch_angle_0_evening_5min11.csv' 

# --- 2. LOAD AND TRIM TO 24 HOURS ---
try:
    df = pd.read_csv(filename)
    df['Start Time'] = pd.to_datetime(df['Start Time'])
    
    # Define start time and cut off exactly 24 hours later
    start_time = df['Start Time'].iloc[0]
    end_time_24h = start_time + pd.Timedelta(hours=24)
    
    # Create a new dataframe with ONLY the first 24 hours
    df_24 = df[df['Start Time'] <= end_time_24h].copy()
    
except Exception as e:
    print(f"Error: {e}")
    exit()

# --- 3. CALCULATE STATS (For Table 6) ---
total_events = df_24['Events'].sum()
total_duration_sec = 24 * 3600
average_rate_hz = total_events / total_duration_sec
error_hz = np.sqrt(total_events) / total_duration_sec

print("="*40)
print("   TABLE 6 VALUES (24 Hours)")
print("="*40)
print(f"Total Hits (N): {total_events}")
print(f"Rate (R):       {average_rate_hz:.5f} Hz")
print(f"Error (dR):     {error_hz:.5f} Hz")
print("="*40)

# ... (Keep your existing data loading code above) ...

# --- 4. PLOT ---
# We use a slightly smaller figure size so the text appears larger relatively
plt.figure(figsize=(8, 5)) 

# Plot Data Points (Increased markersize for visibility)
plt.plot(df_24['Start Time'], df_24['Events'], 
         marker='o', linestyle='None', markersize=3,  # Changed size from 3 to 5
         color='#003366', label='Muon Counts (5-min)')

# Plot Mean Line (Thicker line)
mean_counts = df_24['Events'].mean()
plt.axhline(mean_counts, color='#D32F2F', linestyle='--', linewidth=2.5, 
            label=f'Mean: {mean_counts:.1f}')

# --- AXIS FORMATTING ---
# Removed title since it was empty
# Increased label size and made them bold
plt.ylabel('Counts per 5 min', fontsize=16, fontweight='bold')
plt.xlabel('Time of Day (HH:MM)', fontsize=16, fontweight='bold')

# --- NEW: TICK PARAMETERS (Crucial for visibility) ---
# This makes the numbers on the X and Y axis larger
plt.tick_params(axis='both', which='major', labelsize=14)

# --- Y-AXIS SETTINGS ---
plt.ylim(0, 100)
plt.yticks(np.arange(0, 101, 20))

# --- X-AXIS SETTINGS ---
locator = mdates.HourLocator(interval=3)
formatter = mdates.DateFormatter('%H:%M')
plt.gca().xaxis.set_major_locator(locator)
plt.gca().xaxis.set_major_formatter(formatter)

plt.xlim(start_time, end_time_24h)

plt.grid(True, linestyle=':', alpha=0.6)

# Make legend larger and place it so it doesn't block data
plt.legend(loc='upper right', frameon=True, fontsize=12)

plt.tight_layout()
plt.savefig('stability_24h_exact_time.png', dpi=300)
print("Saved 'stability_24h_exact_time.png' with corrected font sizes.")
