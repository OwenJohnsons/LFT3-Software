'''
Code Purpose: CLI Script that calls pulls all lunar_obs functions together for quick parameter sweeps. 
Author(s): Owen A. Johnson 
Last Modified: 2023-11-30
'''
#%%
import argparse
import numpy as np
# import scienceplots; plt.style.use(['science','ieee'])
import lunar_sys
import lunar_obs
from observer import Observe

obs = Observe(N=100, deck_diameter=3.0, element_low=400.0, array_low=None, start=300.0, stop=900, step=10)
obs.run()
