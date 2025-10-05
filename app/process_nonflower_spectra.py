import os
import numpy as np
import pandas as pd

target_wavelengths = np.arange(300, 700, 1)  

folder_path = "data/text_spectra"

def process_file(filename):
    with open(filename) as f:
        lines = f.readlines()
    
    header_line = lines[0].strip()
    parts = header_line.split()
    record_part = [p for p in parts if p.startswith("Record=")][0]
    record_id = record_part.split("=")[1]

    material_name = header_line.split(":")[1].strip().split()[0]
    
    reflectances = np.array([float(x) for x in lines[1:]])
    
    wl_start = 350  
    wl_end   = 2500
    wavelengths = np.linspace(wl_start, wl_end, len(reflectances))
    
    # Interpolate to target wavelengths
    reflectances_interp = np.interp(target_wavelengths, wavelengths, reflectances)
    
    df = pd.DataFrame({
        "wavelength": target_wavelengths,
        "reflectance": reflectances_interp,
        "material": material_name
    })
    df['reflectance'] = df['reflectance'].mask(df['reflectance'] < 0, 0)
    df['reflectance'] = df['reflectance'].clip(lower=0, upper=1)
    df_wide = df.pivot(index='material', columns='wavelength', values='reflectance')
    df_wide = df_wide.reset_index()

    df_wide.columns = ['material'] + df_wide.columns[1:].astype(int).tolist()
    return df_wide


all_dfs = []
for fname in os.listdir(folder_path):
    if fname.endswith(".txt"):  
        file_path = os.path.join(folder_path, fname)
        df = process_file(file_path)
        all_dfs.append(df)

all_spectra_df = pd.concat(all_dfs, ignore_index=True)

all_spectra_df.to_csv("splib07a_converted.csv", index=False)


