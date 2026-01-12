'''
Code Purpose: Query the NASA Exoplanet Archive for up-to-date list of confirmed exoplanets and return values within a given distance constraint with the option to plot the exoplanets in the Galactic coordinate system.
Author(s): Owen A. Johnson
Last Modified: 2023-11-30
'''
#%%
import pandas as pd 
from glob import glob
import requests
from io import StringIO
import numpy as np
import datetime
import argparse

args = argparse.ArgumentParser(description='NEA Data Handler')
args.add_argument('-d', '--distance', type=float, default=100, help='Distance constraint in parsecs')
args.add_argument('-p', '--plot', default=False, action='store_true', help='Plot and save exoplanets in the Galactic Plane')
args = args.parse_args()

# --- Query Up-to-date list of Exoplanets from NASA Exoplanet Archive ---
url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select pl_name,default_flag,pl_masse,ra,dec,glon,glat,st_teff,sy_dist,sy_disterr1,sy_disterr2 from ps where default_flag = 1&format=csv"
response = requests.get(url)

if response.status_code == 200:
    # The response text contains the data returned by the query
    data = response.text
    data_io = StringIO(data) # Convert to a file-like object
    df = pd.read_csv(data_io, sep=',')
    print('Number of confirmed exoplanets:', len(df))

else:
    print(f"Error: {response.status_code}, {response.text}")

# --- Distance Contraint --- 
dist_constraint = args.distance # pc
df = df[df['sy_dist'] < dist_constraint].reset_index(drop=True)
proxcenB_idx = df[df['pl_name'] == 'Proxima Cen b'].iloc[0].name
print('Number of confirmed exoplanets within %s pc:' % int(dist_constraint), len(df))

# --- Save to CSV ---
date = datetime.datetime.now().strftime("%Y-%m-%d")
df.to_csv('NExSci_data/%s-NEA-Exoplanets-within-%s-pc.csv' % (date, int(dist_constraint)), index=False)

# --- Plot of the Galactic Plane --- 
if args.plot == True:
    from matplotlib.cm import ScalarMappable
    import matplotlib.pyplot as plt; import scienceplots; plt.style.use(['science','ieee'])
    import astropy.coordinates as coord
    import astropy.units as u
    from astropy.coordinates import SkyCoord

    eq = SkyCoord(df['glon'], df['glat'], unit=u.deg); gal = eq.galactic

    fig, ax = plt.subplots(subplot_kw={'projection': 'aitoff'}); plt.grid(True)
    points = ax.scatter(gal.l.wrap_at('180d').radian, gal.b.radian, s=0.1, c=df['sy_dist'], cmap='magma')

    # --- Adding Colorbar --- 
    sm = ScalarMappable(cmap='magma')
    sm.set_array(df['sy_dist'])
    cbar = plt.colorbar(sm, ax=ax, orientation='horizontal')
    cbar.set_label('Distance [pc]',  fontsize=6)
    cbar.ax.tick_params(axis='x', labelsize=4)
    # --- Plot shaded region of the Galactic Plane ---
    plt.axhspan(np.deg2rad(-5), np.deg2rad(5), alpha=0.2, color='grey', label = 'Galactic Plane')
    # --- Plotting Proxima Centauri B --- 
    ax.scatter(gal.l.wrap_at('180d').radian[proxcenB_idx], gal.b.radian[proxcenB_idx], s=10, c='hotpink', marker='*', label='Proxima Centauri B')
    
    ax.set_xlabel('Galactic Longitude [deg]'); ax.set_ylabel('Galactic Latitude [deg]')
    ax.tick_params(axis='both', labelsize=6)
    # plt.legend(fontsize=6, loc = 'upper right')
    plt.savefig('plots/exoplanets_galactic_plane.png', dpi=300, bbox_inches='tight')