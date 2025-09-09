"""Spherical harmonic vector wind analysis for Skyborn.

This module is based on the ajdawson/windspharm project (https://github.com/ajdawson/windspharm),
originally authored by Andrew Dawson. The current version is maintained by Qianye Su and is licensed under the BSD-3-Clause.

Main Classes:
    VectorWind: Enhanced interface for wind field analysis with modern Python features

Example:
    >>> from skyborn.windspharm import VectorWind
    >>> import numpy as np
    >>>
    >>> # Create sample wind data
    >>> nlat, nlon = 73, 144
    >>> u = np.random.randn(nlat, nlon)
    >>> v = np.random.randn(nlat, nlon)
    >>>
    >>> # Initialize VectorWind with type hints and modern interface
    >>> vw = VectorWind(u, v, gridtype='gaussian')
    >>>
    >>> # Calculate various fields with improved documentation
    >>> vorticity = vw.vorticity()
    >>> divergence = vw.divergence()
    >>> psi, chi = vw.sfvp()
"""

from __future__ import absolute_import

from . import standard, tools

# Import main class for easier access
from .standard import VectorWind

try:
    from ._version import __version__
except ImportError:
    __version__ = "unknown"

from . import xarray

__author__ = "Qianye Su"
__license__ = "BSD-3-Clause"
