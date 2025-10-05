import pandas
import numpy as np

speclib = pandas.read_csv('data/csv/spectral_library.csv')
speclib['material'] = np.where(speclib['colour'].notna(), 'flower', speclib['material'])

speclib.to_csv("spectral_library_classified.csv", index=False)