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

import heapq

import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage, spatial

from plotbin.display_pixels import display_pixels

#----------------------------------------------------------------------------

def voronoi_tessellation(x, y, xbin, ybin):
    """Computes Voronoi Tessellation of pixels (x, y) given generators (xbin, ybin)"""

    tree = spatial.KDTree(np.column_stack([xbin, ybin]))
    _, bin_num = tree.query(np.column_stack([x, y]))

    return bin_num

#----------------------------------------------------------------------------

def reassign_bad_bins(bin_num, x, y):
    """Implements steps (vi)-(vii) in section 5.1 of Cappellari & Copin (2003)"""

    # Find the geometric centroid of all successful bins.
    # bin_num = 0 are unbinned pixels which are excluded.
    good = np.unique(bin_num[bin_num > 0])
    xnode = ndimage.mean(x, labels=bin_num, index=good)
    ynode = ndimage.mean(y, labels=bin_num, index=good)

    # Reassign pixels of bins with S/N < target_sn
    # to the closest centroid of a good bin
    bad = bin_num == 0

    # Use an array of ones with the same length as generators so weighted
    # tessellation routines receive an array (not a Python list).
    index = voronoi_tessellation(x[bad], y[bad], xnode, ynode)
    bin_num[bad] = good[index]

    # Recompute geometric centroids of the reassigned bins.
    # These will be used as starting points for the CVT.
    good = np.unique(bin_num)
    xnode = ndimage.mean(x, labels=bin_num, index=good)
    ynode = ndimage.mean(y, labels=bin_num, index=good)

    return xnode, ynode

#----------------------------------------------------------------------------

def calculate_roundness(x, y):
    """Implements equation (5) of Cappellari & Copin (2003)"""

    equivalent_radius = np.sqrt(x.size/np.pi)
    x_bar, y_bar = np.mean(x), np.mean(y)  # Geometric centroid here!
    max_distance = np.sqrt(np.max((x - x_bar)**2 + (y - y_bar)**2))
    roundness = max_distance/equivalent_radius - 1

    return roundness

#----------------------------------------------------------------------------

def accretion(x, y, target_capacity, fun_capacity, verbose=1, args=()):
    """
    Generates initial bin centers using a bin-accretion algorithm.

    This function provides an initial guess for the bin generators, which can
    then be refined by the regularization step. The method is based on the
    bin-accretion algorithm described in Cappellari & Copin (2003) [1]_, but with
    several key modifications for efficiency and generality, as described in
    Cappellari (2025) [2]_.

    The algorithm proceeds as follows:
    1.  It starts by identifying the "brightest" (highest capacity) unbinned
        pixel to use as a seed for a new bin.
    2.  It then iteratively "accretes" the nearest unbinned neighboring
        pixels into the current bin.
    3.  Accretion for a bin stops when the bin is disconnected, becomes too
        non-circular, or its capacity starts moving away from the target.
    4.  A new bin is then seeded from the next brightest available pixel, and
        the process repeats until all pixels are binned.
    5.  Finally, pixels belonging to bins that failed to reach a significant
        fraction of the target capacity are reassigned to the nearest
        successful bin.

    Key differences from the original Cappellari & Copin (2003) algorithm:
    - **Neighbor Finding**: Pixel neighbors are pre-computed once using a
      Delaunay triangulation for efficiency, instead of being searched at
      each step.
    - **Bin Seeding**: A max-heap data structure is used to efficiently
      select the brightest unbinned pixel as the next seed in O(log N) time,
      which is a significant improvement over the original O(N) search.
    - **Stopping Criterion**: The accretion is guided by a generic `target_capacity`
      and stops when the bin's capacity overshoots or moves away from this
      target, rather than simply exceeding a signal-to-noise threshold.

    Parameters
    ----------
    x, y : array_like
        Coordinates of the pixels to be binned.
    target_capacity : float
        The target capacity for each bin.
    fun_capacity : callable
        Function to compute the capacity of a set of pixels, with the
        signature `fun_capacity(indices, *args)`.
    verbose : int, optional
        Controls the level of printed output (default is 1).
    args : tuple, optional
        Additional positional arguments to pass to `fun_capacity`.

    Returns
    -------
    xbin, ybin : np.ndarray
        Coordinates of the centroids of the generated bins.
    dens : np.ndarray
        The initial capacity density for each input pixel.

    References
    ----------
    .. [1] Cappellari, M. & Copin, Y. 2003, MNRAS, 342, 345
       (Section 5.1)
    .. [2] Cappellari, M. 2025, MNRAS submitted, https://arxiv.org/abs/2509.06903
       (Section 6)

    """
    if verbose >= 1:
        print('Bin-accretion Delaunay...')

    n = x.size
    bin_num = np.zeros(n, dtype=int)     # bin label per pixel
    bad = np.ones(n, dtype=bool)         # True means "potentially bad" until bin reaches threshold
    dens = np.array([fun_capacity(j, *args) for j in range(n)])  # per-pixel capacity ("brightness")

    # Rough estimate of expected final bin count (informational only)
    # This number is meaningless if dens is not additive.
    w = dens < target_capacity
    maxnum = int(np.sum(dens[w]) / target_capacity + np.sum(~w))

    # Precompute neighbors once via Delaunay
    xy = np.column_stack([x, y])
    tri = spatial.Delaunay(xy, qhull_options="QJ")  # QJ needed for regular grids
    indices, indptr = tri.vertex_neighbor_vertices

    def neighbours(j):
        return indptr[indices[j]:indices[j + 1]]

    # Build a max-heap of seeds keyed by brightness (dens).
    # Python heapq is a min-heap; use negative key for max behavior.
    density_heap = [(-dens[i], i) for i in range(n)]
    heapq.heapify(density_heap)

    # Helper: pop the brightest unbinned pixel or return None if none remains
    def pop_next_seed():
        while density_heap:
            _, idx = heapq.heappop(density_heap)
            if bin_num[idx] == 0:
                return idx
        return None

    # Select the first seed by brightness
    current_bin = pop_next_seed()

    # Outer loop: at most n bins
    for ind in range(1, n + 1):

        if verbose >= 2 and (ind % 1000 == 0):
            print(f'{ind} / {maxnum}')

        # Initialize a new bin with the current seed (single pixel)
        bin_num[current_bin] = ind
        x_bar, y_bar = x[current_bin], y[current_bin]
        capacity = dens[current_bin]  # start capacity from seed brightness
        neigh = neighbours(current_bin)

        # Inner accretion loop
        while True:

            ok = (bin_num[neigh] == 0)
            if np.any(ok):
                unbin_neigh = neigh[ok]

                # Candidate: unbinned neighbor closest to current bin centroid
                d2 = (x[unbin_neigh] - x_bar)**2 + (y[unbin_neigh] - y_bar)**2
                newpix = unbin_neigh[np.argmin(d2)]
                disconnected = False

                # Test roundness of the possible new bin
                next_bin = np.append(current_bin, newpix)
                roundness = calculate_roundness(x[next_bin], y[next_bin])

                # Update capacity for candidate bin
                capacity_old = capacity
                capacity = fun_capacity(next_bin, *args)

            else:
                disconnected = True

            # Acceptance tests: connectivity, shape, and approach to target capacity
            if (disconnected or roundness > 0.8 or
                abs(capacity - target_capacity) > abs(capacity_old - target_capacity) or
                capacity_old > capacity):

                # Bin considered "good enough" if it approached target capacity
                if capacity > 0.8 * target_capacity:
                    bad[current_bin] = False
                break

            # Accept candidate pixel and continue accretion
            bin_num[newpix] = ind
            current_bin = next_bin
            new_neigh = neighbours(newpix)
            neigh = np.unique(np.append(unbin_neigh, new_neigh))
            x_bar, y_bar = np.mean(x[current_bin]), np.mean(y[current_bin])

        # Start next bin: pick brightest unbinned pixel from the heap
        current_bin = pop_next_seed()
        if current_bin is None:
            # No unbinned pixels remain in heap
            break

    # Zero out pixels that remained "bad" (bins that did not reach threshold)
    bin_num[bad] = 0

    if verbose >= 3:
        rng = np.random.default_rng(826)
        rnd = rng.permutation(x.size)   # Randomize bin colors
        bins = np.unique(bin_num[bin_num > 0])
        xbin_plot = ndimage.mean(x, labels=bin_num, index=bins)
        ybin_plot = ndimage.mean(y, labels=bin_num, index=bins)

        plt.clf()
        display_pixels(x, y, rnd[bin_num], 1, cmap='Set3')
        plt.plot(x[bad], y[bad], 'k+')
        plt.plot(xbin_plot, ybin_plot, 'o', mfc='none', mec='k', ms=4)
        plt.show(block=1)

    # Final reassignment of bad bins as in original
    xbin, ybin = reassign_bad_bins(bin_num, x, y)

    if verbose >= 1:
        print(np.max(bin_num), ' initial bins.')
        print('Reassign bad bins...')
        print(xbin.size, ' good bins.')

    return xbin, ybin, dens

#----------------------------------------------------------------------------
