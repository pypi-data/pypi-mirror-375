The PowerBin Package
====================

**PowerBin: Fast Adaptive Data Binning with Centroidal Power Diagrams**

.. image:: https://img.shields.io/pypi/v/powerbin.svg
    :target: https://pypi.org/project/powerbin/
.. image:: https://img.shields.io/badge/arXiv-2509.06903-orange.svg
    :target: https://arxiv.org/abs/2509.06903

This ``PowerBin`` package provides a Python implementation of the **PowerBin** algorithm — 
a modern alternative to the classic Voronoi binning method. Like Voronoi binning, it performs 
2D adaptive spatial binning to achieve a nearly constant value per bin of a chosen *capacity* 
(e.g., signal‑to‑noise ratio or any other user‑defined function of the bin spaxels).

**Key advances over the classic method include:**

- **Centroidal Power Diagram tessellation:** Produces bins that are nearly round, convex, 
  and connected, and eliminates the disconnected or nested bins that could occur with 
  earlier approaches.

- **Scalability:** Uses a new bin‑accretion algorithm with **O(N log N)** complexity, 
  removing the O(N^2) bottleneck of the original method and making million‑pixel datasets 
  practical.

- **Stable CPD construction:** Generates the tessellation via a heuristic inspired by 
  packed soap bubbles, avoiding the numerical fragility of formal CPD solvers with 
  realistic non-additive capacities (e.g., correlated noise).

The algorithm combines a fast initial bin‑accretion phase with iterative regularization, 
and is described in detail in `Cappellari (2025) <https://arxiv.org/abs/2509.06903>`_.

.. contents:: :depth: 2

Attribution
-----------

If you use this software for your research, please cite `Cappellari (2025)`_.
The BibTeX entry for the paper is::

    @ARTICLE{Cappellari2025,
        author = {{Cappellari}, M.},
        title = "{PowerBin: Fast adaptive data binning with Centroidal Power Diagrams}",
        journal = {MNRAS},
        eprint = {2509.06903},
        year = 2025,
        note = {submitted}
    }

Installation
------------

install with::

    pip install powerbin

Without write access to the global ``site-packages`` directory, use::

    pip install --user powerbin

To upgrade ``PowerBin`` to the latest version use::

    pip install --upgrade powerbin

Usage Examples
--------------

To learn how to use the ``PowerBin`` package, copy, modify and run
the example programs in the ``powerbin/examples`` directory.
It can be found within the main ``powerbin`` package installation folder
inside `site-packages <https://stackoverflow.com/a/46071447>`_.
The detailed documentation is contained in the docstring of the file
``powerbin/core.py``, or on `PyPi <https://pypi.org/project/powerbin/>`_.

Minimal example
---------------

Below is a minimal usage example you can copy into a script (or run the
provided example in ``powerbin/examples/example.py``).

In this example, the bin capacity function is defined as ``(S/N)^2``. This is a
convenient choice for illustration because, in the Poissonian limit,
``(S/N)^2`` equals the total signal, which is an additive quantity. This setup
lets us compare the behaviour of binning with an additive capacity versus a
non‑additive one. PowerBin does not require the capacity to be additive — you
can verify this in the example by setting ``covariance = True``.

.. code-block:: python

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

###########################################################################
