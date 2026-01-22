import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# --- 1. LOAD DATA ---
filename = 'angle_dependence.csv'
try:
    df = pd.read_csv(filename)
except Exception as e:
    print(f"Error: {e}")
    exit()

# Calculate Flux
detector_area_cm2 = 62.5
flux = df['Rate'] / detector_area_cm2
flux_err = df['Error'] / detector_area_cm2
theta_deg = df['Angle']
theta_rad = np.radians(theta_deg)

# --- 2. DEFINE MODELS ---

# Model A: Standard Cos^2 (Fixed n=2)
def model_cos2(theta, I0):
    return I0 * (np.cos(theta)**2)

# Model B: General Cos^n (Free n)
def model_cosn(theta, I0, n):
    return I0 * (np.cos(theta)**n)

# Model C: Shukla & Sankrith (Curved Atmosphere)
def model_shukla(theta, I0, n):
    R = 6371.0 # Earth Radius km
    d = 15.0   # Atmosphere production height km
    k = R/d
    # Path length factor D
    D = np.sqrt( (k**2)*(np.cos(theta)**2) + 2*k + 1 ) - k*np.cos(theta)
    return I0 * (D**-(n-1))

# Model D: Schwerdt (Empirical)
def model_schwerdt(theta, a, b, c, d_offset):
    return a * (np.cos(b*theta + c)**2) + d_offset

# --- 3. PERFORM FITS ---

# A: Cos^2
popt_A, pcov_A = curve_fit(model_cos2, theta_rad, flux, sigma=flux_err, absolute_sigma=True, p0=[0.002])

# B: General Cos^n
popt_B, pcov_B = curve_fit(model_cosn, theta_rad, flux, sigma=flux_err, absolute_sigma=True, p0=[0.002, 2.0])
perr_B = np.sqrt(np.diag(pcov_B))

# C: Shukla (n approx 3 is a good start)
popt_C, pcov_C = curve_fit(model_shukla, theta_rad, flux, sigma=flux_err, absolute_sigma=True, p0=[0.002, 3.0])

# D: Schwerdt (Tricky fit, needs good guess)
popt_D, pcov_D = curve_fit(model_schwerdt, theta_rad, flux, sigma=flux_err, absolute_sigma=True, 
                           p0=[0.002, 1.0, 0.0, 0.0001], maxfev=10000)

# --- 4. CALCULATE STATS (Chi-Squared & R^2) ---
def get_stats(func, popt, y_data):
    residuals = y_data - func(theta_rad, *popt)
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y_data - np.mean(y_data))**2)
    r_squared = 1 - (ss_res / ss_tot)
    
    chi2 = np.sum((residuals / flux_err) ** 2)
    dof = len(y_data) - len(popt)
    red_chi2 = chi2 / dof
    return red_chi2, r_squared

stats_A = get_stats(model_cos2, popt_A, flux)
stats_B = get_stats(model_cosn, popt_B, flux)
stats_C = get_stats(model_shukla, popt_C, flux)
stats_D = get_stats(model_schwerdt, popt_D, flux)

# --- 5. PRINT RESULTS (For Table 7) ---
print("\n" + "="*50)
print("   FIT RESULTS FOR TABLE 7")
print("="*50)
print(f"1. Cos^2:      Chi2/dof={stats_A[0]:.2f}, R2={stats_A[1]:.4f}")
print(f"               I0 = {popt_A[0]:.2e}")
print("-" * 30)
print(f"2. Pethuraj:   Chi2/dof={stats_B[0]:.2f}, R2={stats_B[1]:.4f}")
print(f"               I0 = {popt_B[0]:.2e}, n = {popt_B[1]:.3f} +/- {perr_B[1]:.3f}")
print("-" * 30)
print(f"3. Shukla:     Chi2/dof={stats_C[0]:.2f}, R2={stats_C[1]:.4f}")
print(f"               n = {popt_C[1]:.3f}")
print("-" * 30)
print(f"4. Schwerdt:   Chi2/dof={stats_D[0]:.2f}, R2={stats_D[1]:.4f}")
print(f"               d (background) = {popt_D[3]:.2e}")
print("="*50)

# --- 6. PLOT ---
plt.figure(figsize=(9, 7))

# Plot Data
plt.errorbar(theta_deg, flux, yerr=flux_err, 
             fmt='o', color='black', ecolor='gray', capsize=3, label='Experimental Flux', zorder=5)

# Generate smooth lines
x_smooth_deg = np.linspace(0, 85, 200)
x_smooth_rad = np.radians(x_smooth_deg)

# Plot Fit Lines
plt.plot(x_smooth_deg, model_cos2(x_smooth_rad, *popt_A), 
         'b--', linewidth=1.5, label='Standard $\cos^2(\\theta)$')

# --- CHANGED LABEL HERE ---
plt.plot(x_smooth_deg, model_cosn(x_smooth_rad, *popt_B), 
         'g-', linewidth=2, label=f'Pethuraj et al. ($n={popt_B[1]:.2f}$)')

plt.plot(x_smooth_deg, model_shukla(x_smooth_rad, *popt_C), 
         'orange', linestyle='-.', label='Shukla & Sankrith')

plt.plot(x_smooth_deg, model_schwerdt(x_smooth_rad, *popt_D), 
         'r:', linewidth=2, label='Schwerdt (Empirical)')

plt.title('Comparison of Muon Flux Models', fontsize=14)
# Use \mathbf{...} to make the math bold
plt.xlabel(r'Zenith Angle $\mathbf{\theta}$ (degrees)', fontsize=16, fontweight='bold')
plt.ylabel(r'Flux ($\mathbf{s^{-1} cm^{-2}}$)', fontsize=16, fontweight='bold')
plt.legend(fontsize=14)
plt.grid(True, linestyle=':', alpha=0.6)

plt.tight_layout()
plt.savefig('fig_Z_model_comparison.png', dpi=300)
print("\nPlot saved as 'fig_Z_model_comparison.png'")
