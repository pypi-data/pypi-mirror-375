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

from collections import deque
import numpy as np

class EarlyStopper:
    """
    Detects when an iterative algorithm has stalled or entered an approximate
    oscillatory cycle and should be stopped early.

    The class implements two complementary heuristics:
    - patience: stop after N consecutive updates with no meaningful improvement
      relative to the best value seen so far.
    - oscillation detection: on a sliding window, detect near-zero downward
      trend combined with frequent sign changes in successive differences.

    Parameters
    ----------
    rel_tol : float, optional
        Relative improvement threshold considered significant. A new value v
        is considered an improvement if (best - v) / max(1.0, |best|) > rel_tol.
        Default is 1e-3.
    abs_tol : float or None, optional
        Absolute improvement threshold. If provided, an absolute decrease in
        (best - v) greater than abs_tol is considered improvement. Default None.
    patience : int, optional
        Number of consecutive non-improving iterations before declaring
        stagnation (default 20).
    window : int, optional
        Size of the sliding window used for the oscillation heuristic
        (default 30).
    slope_tol : float, optional
        Tolerance for the least-squares slope fit over the window. If the
        slope is >= -slope_tol the window is considered not trending downwards.
        Default 1e-5.
    min_updown_ratio : float, optional
        Minimum fraction of sign changes in successive differences within the
        window to regard the behavior as oscillatory (default 0.6).
    min_iters : int, optional
        Minimum number of update() calls before stopping may trigger
        (default 10).

    Attributes
    ----------
    best : float
        Best (lowest) value observed so far.
    no_improve : int
        Count of consecutive iterations without significant improvement.
    iter : int
        Total number of update() calls processed.
    window : collections.deque
        Sliding window containing the most recent values.
    """
    def __init__(self, rel_tol=1e-3, abs_tol=None, patience=20,
                 window=30, slope_tol=1e-5, min_updown_ratio=0.6, min_iters=10):
        self.rel_tol = rel_tol
        self.abs_tol = abs_tol
        self.patience = patience
        self.window = deque(maxlen=window)
        self.slope_tol = slope_tol
        self.min_updown_ratio = min_updown_ratio
        self.min_iters = min_iters

        self.best = np.inf
        self.no_improve = 0
        self.iter = 0

    def _improved(self, v):
        """
        Determine whether the provided value constitutes a meaningful
        improvement over the current best.

        Parameters
        ----------
        v : float
            New scalar measurement to evaluate.

        Returns
        -------
        bool
            True if `v` is considered an improvement, False otherwise.
        """
        if (self.abs_tol is not None) and (self.best - v > self.abs_tol) or (self.best == np.inf):
            return True
        rel = (self.best - v) / max(1.0, abs(self.best))
        return rel > self.rel_tol

    def update(self, current):
        """
        Feed the next scalar measurement and decide whether to stop.

        Parameters
        ----------
        diff_value : float
            Latest scalar value (e.g. current "Diff" from an iteration).

        Returns
        -------
        bool
            True if the stopper recommends terminating the iterative process
            (stalled or oscillating without meaningful progress); False otherwise.

        Notes
        -----
        The method updates internal counters and the sliding window. It first
        checks the patience/stagnation condition, then — if enough values are
        available — evaluates the oscillation heuristic based on slope and
        sign changes inside the window.
        """
        self.iter += 1
        self.window.append(current)

        # 1) Patience on best-so-far
        if self._improved(current):
            self.best = min(self.best, current)
            self.no_improve = 0
        else:
            self.no_improve += 1
            if self.no_improve >= self.patience and self.iter >= self.min_iters:
                return True  # stop: stalled

        # 2) Oscillation heuristic on window
        if len(self.window) == self.window.maxlen and self.iter >= self.min_iters:
            y = np.array(self.window)
            x = np.arange(len(y))
            x0 = x - x.mean()
            y0 = y - y.mean()
            slope = (x0 @ y0) / (x0 @ x0)      # least-squares slope

            s = np.sign(np.diff(y))
            sign_changes = np.sum(s[1:] * s[:-1] < 0)
            updown_ratio = sign_changes / max(1, len(s) - 1)

            window_best = y.min()
            recent_rel_impr = (self.best - window_best) / max(1.0, abs(self.best))

            if slope >= -self.slope_tol and updown_ratio >= self.min_updown_ratio and recent_rel_impr <= self.rel_tol:
                return True  # stop: oscillating with no meaningful progress

        return False
