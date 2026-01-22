import pandas as pd
import numpy as np
from scipy.optimize import curve_fit

# --- 1. LOAD DATA ---
filename = 'angle_dependence.csv'
try:
    df = pd.read_csv(filename)
except:
    # Fallback to manual data if file not found (for testing)
    data = {
        'Angle': [0, 10, 20, 30, 40, 50, 60, 70, 80],
        'Rate':  [0.15167, 0.14166, 0.1308, 0.1077, 0.0875, 0.07722, 0.04833, 0.0286, 0.01694],
        'Error': [0.0065, 0.00627, 0.006028, 0.00547, 0.00493, 0.004631, 0.00366, 0.00281, 0.00217]
    }
    df = pd.DataFrame(data)

# Calculate Flux (This is what we fit to)
detector_area_cm2 = 62.5
flux = df['Rate'] / detector_area_cm2
flux_err = df['Error'] / detector_area_cm2
theta_rad = np.radians(df['Angle'])

# --- 2. DEFINE MODELS ---

# A: Standard Cos^2
def model_cos2(theta, I0):
    return I0 * (np.cos(theta)**2)

# B: General Cos^n (Fit determines n)
def model_cosn(theta, I0, n):
    return I0 * (np.cos(theta)**n)

# C: Shukla & Sankrith (Fit determines n)
# Formula: I = I0 * D^{-(n-1)}
def model_shukla(theta, I0, n):
    R = 6371.0 
    d = 15.0   
    k = R/d
    # D is path length ratio (approx sec(theta))
    D = np.sqrt( (k**2)*(np.cos(theta)**2) + 2*k + 1 ) - k*np.cos(theta)
    # If flux ~ cos^p, then p = n-1. 
    return I0 * (D**-(n-1))

# D: Schwerdt (Empirical) - 4 Parameters
def model_schwerdt(theta, a, b, c, d_offset):
    return a * (np.cos(b*theta + c)**2) + d_offset

# --- 3. FITTING ROUTINE ---

def fit_and_report(model_func, p0, bounds, name):
    popt, pcov = curve_fit(model_func, theta_rad, flux, sigma=flux_err, 
                           absolute_sigma=True, p0=p0, bounds=bounds, maxfev=10000)
    perr = np.sqrt(np.diag(pcov))
    
    # Calculate Stats
    residuals = flux - model_func(theta_rad, *popt)
    chi2 = np.sum((residuals / flux_err) ** 2)
    dof = len(flux) - len(popt)
    red_chi2 = chi2 / dof
    
    # R-squared
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((flux - np.mean(flux))**2)
    r2 = 1 - (ss_res / ss_tot)
    
    return popt, perr, red_chi2, r2

# --- 4. EXECUTE FITS ---

# Cos^2
popt_A, perr_A, chi2_A, r2_A = fit_and_report(
    model_cos2, [0.002], (-np.inf, np.inf), "Cos^2")

# General Cos^n
popt_B, perr_B, chi2_B, r2_B = fit_and_report(
    model_cosn, [0.002, 2.0], (-np.inf, np.inf), "Cos^n")

# Shukla
popt_C, perr_C, chi2_C, r2_C = fit_and_report(
    model_shukla, [0.002, 3.0], (-np.inf, np.inf), "Shukla")

# Schwerdt 
# Bounds: a>0, b~1, c small, d>=0
popt_D, perr_D, chi2_D, r2_D = fit_and_report(
    model_schwerdt, 
    p0=[0.002, 1.0, 0.0, 0.0], 
    bounds=([0, 0.5, -3.14, 0], [np.inf, 1.5, 3.14, np.inf]), 
    name="Schwerdt")

# --- 5. PRINT CORRECTED TABLE DATA ---
print("\n" + "="*70)
print("   CORRECTED DATA FOR TABLE 8 (Use these values)")
print("="*70)

print(f"1. Simple Cos^2")
print(f"   Reduced Chi2: {chi2_A:.2f}")
print(f"   R^2:          {r2_A:.4f}")
print(f"   I0:           {popt_A[0]:.2e}")
print("-" * 40)

print(f"2. General Cos^n")
print(f"   Reduced Chi2: {chi2_B:.2f}")
print(f"   R^2:          {r2_B:.4f}")
print(f"   I0:           {popt_B[0]:.2e}")
print(f"   n:            {popt_B[1]:.2f} +/- {perr_B[1]:.2f}")
print("-" * 40)

print(f"3. Shukla & Sankrith")
print(f"   Reduced Chi2: {chi2_C:.2f}")
print(f"   R^2:          {r2_C:.4f}")
print(f"   n:            {popt_C[1]:.2f} (Note: This should be approx n_general + 1)")
print("-" * 40)

print(f"4. Schwerdt (All 4 Parameters)")
print(f"   Reduced Chi2: {chi2_D:.2f}")
print(f"   R^2:          {r2_D:.4f}")
print(f"   a (Amp):      {popt_D[0]:.2e}")
print(f"   b (Freq):     {popt_D[1]:.3f}")
print(f"   c (Phase):    {popt_D[2]:.3f}")
print(f"   d (Bg):       {popt_D[3]:.2e}")
print("="*70)
