import pandas as pd
import numpy as np

# --- CONSTANTS ---
R_scope = 50.0          # Oscilloscope impedance (Ohms)
e_charge = 1.60218e-19  # Elementary charge (Coulombs)

# --- FILES & NORMALIZATION ---
# 'factor': 1.0 for a real 1 p.e. pulse.
# 'factor': 2.0 if you captured a crosstalk (2 p.e.) pulse and need to halve it.
files = {
    'Channel 1': {'file': 'mppc1_1pe.csv', 'factor': 2.0}, # Was ~1.2mV (Crosstalk)
    'Channel 2': {'file': 'mppc2_1pe.csv', 'factor': 2.0}, # Was ~1.3mV (Crosstalk)
    'Channel 3': {'file': 'mppc3_1pe.csv', 'factor': 1.0}  # Was ~0.8mV (Real 1 p.e.)
}

skip_rows = 1 

def analyze_pulse(name, info):
    filename = info['file']
    factor = info['factor']
    
    try:
        # Load Data
        df = pd.read_csv(filename, skiprows=skip_rows)
        if df.empty: return
        
        # Get raw arrays
        time_s = df.iloc[:, 0].to_numpy()
        volts = df.iloc[:, 1].to_numpy()
        
        # 1. BASELINE CORRECTION
        baseline_points = int(len(volts) * 0.1)
        baseline_voltage = np.mean(volts[:baseline_points])
        volts_corrected = volts - baseline_voltage
        
        # 2. INTEGRATION (Area under curve)
        # We take absolute value because pulses are negative
        voltage_time_area = np.abs(np.trapz(volts_corrected, time_s)) 
        
        # 3. CALCULATE TOTAL CHARGE OF THE PULSE (Q_total = Area / R)
        charge_total = voltage_time_area / R_scope
        
        # 4. CALCULATE 1 P.E. CHARGE (Q_1pe = Q_total / factor)
        # This fixes the crosstalk issue
        charge_1pe = charge_total / factor
        
        # 5. CALCULATE GAIN (G = Q_1pe / e)
        gain = charge_1pe / e_charge
        
        # --- PRINT RESULTS ---
        print(f"--- {name} (Correction Factor: {factor}) ---")
        print(f"Pulse Area:   {voltage_time_area:.2e} V.s")
        print(f"Total Charge: {charge_total:.2e} C")
        print(f"1 p.e. Charge:{charge_1pe:.2e} C  <-- Use this for Table")
        print(f"Gain:         {gain:.2e}      <-- Use this for Table")
        print("-" * 30)
        
    except Exception as e:
        print(f"Error processing {name}: {e}")

# Run analysis
print("CALCULATING CORRECTED GAIN...\n")
for name, info in files.items():
    analyze_pulse(name, info)
