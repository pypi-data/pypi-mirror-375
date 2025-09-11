"""
#####################################################################
Copyright (C) 2025 Michele Cappellari  
E-mail: michele.cappellari_at_physics.ox.ac.uk  

Updated versions of this software are available at:  
https://pypi.org/project/powerbin/  

If you use this software in published research, please acknowledge it as:  
“PowerBin method by Cappellari (2025, MNRAS submitted)”  
https://arxiv.org/abs/2509.06903  

This software is provided “as is”, without any warranty of any kind,  
express or implied.  

Permission is granted for:  
 - Non-commercial use.  
 - Modification for personal or internal use, provided that this  
   copyright notice and disclaimer remain intact and unaltered  
   at the beginning of the file.  

All other rights are reserved. Redistribution of the code, in whole or in part,  
is strictly prohibited without prior written permission from the author.  

#####################################################################

V1.0.0: PowerBin created — MC, Oxford, 10 September 2025

"""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from powerbin import PowerBin

#-----------------------------------------------------------------------------

"""
Usage example for the procedure PowerBin.

Columns 1–4 of the text file sample_data_ngc2273 contain, respectively:

    x, y coordinates of each spaxel, followed by their Signal and Noise.

In this example, the bin capacity function is defined as ``(S/N)^2``. This is a
convenient choice for illustration because, in the Poissonian limit,
``(S/N)^2`` equals the total signal, which is an additive quantity. This setup
lets us compare the behaviour of binning with an additive capacity versus a
non‑additive one. PowerBin does not require the capacity to be additive — you
can verify this in the example by setting ``covariance = True``.
"""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from powerbin import PowerBin

file_dir = Path(__file__).resolve().parent
x, y, signal, noise = np.loadtxt(file_dir / 'sample_data_ngc2273.txt').T

target_sn = 50

# Set covariance = True to simulate correlated noise
covariance = False

def fun_capacity(index):
    """Return (S/N)^2, which is additive in the Poissonian case."""
    index = np.atleast_1d(index)
    sn = np.sum(signal[index]) / np.sqrt(np.sum(noise[index]**2))
    if covariance:
        sn /= 1 + 1.07 * np.log10(len(index))
    return sn**2

# Here target capacity = target_sn^2, consistent with our choice of capacity definition
pow = PowerBin(x, y, fun_capacity, target_sn**2, verbose=1)

# PowerBin reports the fractional RMS of the bin capacity (here, (S/N)^2).
# To obtain the fractional scatter in S/N itself, take the square root of the capacity values.
# (By error propagation, dividing the capacity scatter by 2 gives the same result.)
sn_bin = np.sqrt(pow.capacity[~pow.single])
rms_frac = np.std(sn_bin, ddof=1) / np.mean(sn_bin) * 100
print(f'Fractional S/N Scatter: {rms_frac:.1f} %')

# The binning was performed on (S/N)^2, but for plotting we want S/N.
# Apply a square-root scaling to the capacity before plotting.
pow.plot(capacity_scale='sqrt', ylabel='S/N')
plt.pause(5)
