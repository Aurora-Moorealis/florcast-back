import pandas as pd
import requests
import os
import time
import random
'''
metadata_csv = "data/csv/FReD_Metadata.csv"  

out_dir = "data/csv/FReD_reflectances"
os.makedirs(out_dir, exist_ok=True)

samples_per_colour = 18

csv_base = "http://www.reflectance.co.uk/csvdownloader.php"

# Delay between requests to avoid overloading server
delay = 0.2

meta = pd.read_csv(metadata_csv)
meta["ID"] = meta["ID"].astype(int)


meta['colour'] = meta['Human Colour'].map(color_mapping)

drop_colors = ['black', 'grey', 'brown', 'green']

meta_filtered = meta[~meta['colour'].isin(drop_colors)].copy()
print(meta_filtered['colour'].value_counts())

sample_ids = []
meta_filtered = meta_filtered.dropna(subset=["Human Colour"])
for col in sorted(meta_filtered["Human Colour"].unique()):
    subset = meta_filtered[meta_filtered["Human Colour"] == col]
    ids = subset["ID"].tolist()
    if samples_per_colour is None:
        chosen = ids
    else:
        if len(ids) <= samples_per_colour:
            chosen = ids
        else:
            chosen = random.sample(ids, samples_per_colour)
    sample_ids.extend(chosen)

print("Sampled IDs:", sample_ids)

# Subset metadata to just these IDs
meta_sel = meta[meta["ID"].isin(sample_ids)].copy()

def download_spectrum(id_):
    """
    Download the reflectance CSV for sample id_.
    Returns True if success, False otherwise.
    """
    params = {"csv": id_}
    try:
        resp = requests.get(csv_base, params=params, timeout=2)
    except Exception as e:
        print(f"Request error for ID {id_}: {e}")
        return False

    if resp.status_code != 200:
        print(f"HTTP {resp.status_code} for ID {id_}")
        return False

    text = resp.text.strip()
    lines = text.splitlines()
    if not lines:
        print(f"No content returned for ID {id_}")
        return False
    
    first_line = text.splitlines()[0].lower()
    if ("wavelength" in first_line or "," in first_line) and len(text) > 0:
        fname = os.path.join(out_dir, f"FReD_ID_{id_}.csv")
        with open(fname, "w", encoding="utf-8") as f:
            f.write(text)
        return True
    else:
        print(f"Failed CSV check for ID {id_} — likely HTML or error page")
        return False

for sid in sample_ids:
    fname = os.path.join(out_dir, f"FReD_ID_{sid}.csv")
    if os.path.exists(fname):
        continue
    ok = download_spectrum(sid)
    if not ok:
        print(f"Download failed for ID {sid}")
    time.sleep(delay)

# === Read downloaded spectra, merge with metadata ===

spec_list = []
for sid in sample_ids:
    fpath = os.path.join(out_dir, f"FReD_ID_{sid}.csv")
    if not os.path.exists(fpath):
        print(f"No file for ID {sid}, skipping")
        continue
    try:
        df = pd.read_csv(fpath, header=None, names=["ID", "wavelength", "reflectance"])
        df.columns = df.columns.str.strip()
    except Exception as e:
        print(f"Error reading CSV for ID {sid}: {e}")
        continue

    cols = [c.strip().lower() for c in df.columns]
    # find which column is wavelength, which reflectance

    df2 = df[["wavelength", "reflectance"]].copy()
    df2["ID"] = sid
    row = meta_sel[meta_sel["ID"] == sid].iloc[0]
    df2["colour"] = row["Human Colour"]
    df2["material"] = row["Species"]
    spec_list.append(df2)

# Combine
if spec_list:
    combined = pd.concat(spec_list, ignore_index=True)
    combined.to_csv("FReD_sampled_spectra_long.csv", index=False)
    print("Saved merged spectra:", "FReD_sampled_spectra_long.csv")
else:
    print("No spectra merged; spec_list empty")
'''


colour_mapping = {
    'lilac': 'violet',
    'pink-purple': 'pink',
    'pale orange': 'orange',
    'yellow-orange': 'yellow',
    'yellow-green': 'yellow',
    'blue-violet': 'blue',
    'light blue': 'blue',
    'light yellow': 'yellow',
    'red-brown': 'red',
    'off-white': 'white',
    'white-light purple': 'white',
    'purple': 'violet',
    'dark off-white': 'white',
    'cream-white': 'white',
    'dark blue': 'blue',
    'light green': 'green',
    'dark red': 'red',
    'pink-white': 'pink',
    'dark purple': 'violet',
    'dark violet': 'violet',
    'white-pink': 'white',
    'yellow-white': 'yellow',
    'white-light pink': 'white',
    'green-pink': 'green',
    'dark pink': 'pink',
    'dark green-violet': 'green',
    'yellow-brown': 'yellow',
    'white-blue': 'white',
    'yellow-cream': 'yellow',
    'pink-green': 'pink',
    'green-brown': 'green',
    'white-green': 'white',
    'white-red': 'white',
    'violet-blue': 'violet',
    'light violet': 'violet',
    'orange-yellow': 'orange',
    'dark purple-green': 'violet',
    'red-orange': 'red',
    'red-yellow': 'red',
    'yellow-red': 'yellow',
    'cream-yellow': 'yellow',
    'lilac-violet': 'violet',
    'dark blue-violet': 'blue',
    'white-yellow': 'white',
    'red-green': 'red',
    'violet-pink': 'violet',
    'blue-green': 'blue',
    'violet-white': 'violet',
    'white-violet': 'white',
    'pink-brown': 'pink',
    'red-pink': 'red',
    'yellow-green-violet': 'yellow',
    'violet-green': 'violet',
    'violet-brown': 'violet',
    'pink-violet': 'pink',
    'lilac-pink': 'violet',
    'deep blue': 'blue',
    'purple-green': 'violet',
    'red-white': 'red',
    'grey-white': 'grey',
    'white-green-pink': 'white',
    'violet-brown-green': 'violet',
    'orange-black': 'orange',
    'orange': 'orange',
    'red': 'red',
    'yellow': 'yellow',
    'pink': 'pink',
    'white': 'white',
    'grey': 'grey',
    'black': 'black',
    'blue': 'blue',
    'violet': 'violet',
    'green': 'green'
}

sampled_spectra = pd.read_csv("data/csv/FReD_sampled_spectra_long.csv")

wide_df = sampled_spectra.pivot_table(index="ID",
                         columns="wavelength",
                         values="reflectance").reset_index()
wide_df = wide_df.merge(sampled_spectra[["ID", "colour", "material"]].drop_duplicates(), on="ID")
wide_df.columns = [str(c) if isinstance(c, (int, float)) else c for c in wide_df.columns]
wide_df.drop(columns=["ID"], inplace=True)
col = wide_df.pop("colour")
wide_df.insert(0, "colour", col)

mat = wide_df.pop("material")
wide_df.insert(1, "material", mat)

unique_colors = wide_df['colour'].unique()
print(unique_colors)

wide_df['colour'] = wide_df['colour'].map(colour_mapping)

drop_colors = ['black', 'grey', 'brown', 'green']
wide_df_filtered = wide_df[~wide_df['colour'].isin(drop_colors)].copy()
wide_df_filtered.to_csv("FReD_sampled_spectra_wide.csv", index=False)

print(wide_df_filtered.shape)