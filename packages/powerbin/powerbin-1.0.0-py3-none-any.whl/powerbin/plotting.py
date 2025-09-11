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


"""
Plot final bins of PowerBin and fix Matplotlib 'asinh' scale
Michele Cappellari, Oxford, 7 September 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import collections, ticker

from plotbin.display_pixels import display_pixels

#----------------------------------------------------------------------------

def plot_power_diagram(x, y, dens, bin_num, xbin, ybin, rbin, npix, magrange=20):

    single = npix == 1

    rng = np.random.default_rng(826)
    rnd = rng.permutation(xbin.size)   # Randomize bin colors
    display_pixels(x, y, rnd[bin_num], cmap='Set3')

    plt.xlabel('x (pixels)')
    plt.ylabel('y (pixels)')

    xy = np.column_stack([xbin, ybin])
    ax = plt.gca()
    circles = collections.EllipseCollection(
        2*rbin[~single], 2*rbin[~single], 0, offsets=xy[~single], units='x',
        facecolor='none', edgecolors='k', lw=0.5, transOffset=ax.transData)
    ax.add_collection(circles)
    circles = collections.EllipseCollection(
        2*rbin/10, 2*rbin/10, 0, offsets=xy, units='x',
        facecolor='k', edgecolors='k', lw=0.5, transOffset=ax.transData)
    ax.add_collection(circles)

    levels = np.max(dens)*10**(-0.4*np.arange(magrange)[::-1])  # 1 mag contours
    plt.tricontour(x, y, dens, levels=levels, colors='indigo', linewidths=1)

#----------------------------------------------------------------------------

def format_asinh_axis(ax, axis='y', linear_width=1.0):
    """
    Install major and minor formatters/locators for an 'asinh' axis.

    This uses a combined locator: inside [-linear_width, linear_width] majors
    come from a linear locator, outside that range majors come from an
    AsinhLocator (decades). Minor ticks are placed with AsinhLocator and
    selectively labelled.
    """
    class CustomAsinhLocator(ticker.AutoLocator):

        def __init__(self, linear_width=linear_width, subs=None):
            super().__init__()
            self._asinh = ticker.AsinhLocator(linear_width, subs=subs)
            self._linear = ticker.MaxNLocator(steps=[1, 2, 5])

        def tick_values(self, vmin, vmax):
            asinh_ticks = self._asinh.tick_values(vmin, vmax)
            linear_ticks = self._linear.tick_values(vmin, vmax)
            return np.union1d(asinh_ticks[abs(asinh_ticks) >= 1],
                              linear_ticks[abs(linear_ticks) < 1])

    def major_formatter(x, pos):
        if abs(x) < 1000:
            fmt = ".2g" if abs(x) < 1 else ".0f"
            return rf"${x:{fmt}}$"
        ex = int(np.floor(np.log10(abs(x))))
        ma = x / 10**ex
        if np.isclose(abs(ma), 1):
            return rf"${np.sign(ma)*10:.0f}^{ex}$"
        return rf"${ma:.1f}\times10^{ex}$"
        
    def minor_formatter(x, pos):
        if abs(x) < 1:
            return ''
        ex = int(np.floor(np.log10(abs(x))))
        ma = x / 10**ex
        if abs(ma) not in {2, 3, 4, 6}:
            return ''
        if abs(x) < 1000:
            return rf"${x:.0f}$"
        return rf"${ma:.0f}\times10^{ex}$"

    ax_obj = ax.xaxis if axis == 'x' else ax.yaxis
    ax_obj.set_major_locator(CustomAsinhLocator())
    ax_obj.set_major_formatter(major_formatter)
    vmin, vmax = ax_obj.get_view_interval()
    maj = ax_obj.get_majorticklocs()
    if np.sum((maj >= vmin) & (maj <= vmax) & (abs(maj) > 1)) < 3:
        ax_obj.set_minor_formatter(minor_formatter)
    ax_obj.set_minor_locator(ticker.AsinhLocator(linear_width, subs=range(1, 10)))

#----------------------------------------------------------------------------
