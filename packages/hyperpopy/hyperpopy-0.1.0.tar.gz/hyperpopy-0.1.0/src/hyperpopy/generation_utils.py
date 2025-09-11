"""
Generation utilities for Poisson hyperplane model.

This module provides functions for generating and visualizing realizations
of the Poisson hyperplane process, including sampling from balls,
hyperplane partitioning, and 2D plotting with color coding.
"""
import hashlib

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle
from numba import jit

from .analytic_utils import rate

### The following functions can create and plot realizations of the Poisson model. ###


def sample_from_ball(dimension, num_points):
    """Sample num_points points from interior of unit d-ball by uniformly 
    sampling angle and then offset.

    Parameters
    ----------
    dimension : int
        The dimension of the space
    num_points : int
        The number of points to sample

    Returns
    -------
    np.array, shape (n, d)
        The sampled points
    """
    points = np.random.normal(size=(num_points, dimension))
    scales = np.random.uniform(size=(num_points, 1))
    norms = np.linalg.norm(points, axis=1, keepdims=True)
    unit_ball_points = points / norms * scales
    return unit_ball_points


@jit(nopython=True)
def hyperplane_partition(points, gridpoints):
    """Return a unique hash for each grid point for unlimited number of hyperplanes.

    Parameters
    ----------
    points : np.array, shape (n,d)
        The points defining the hyperplanes
    gridpoints : np.array, shape (N,d)
        The points at which to evaluate the hyperplanes

    Returns
    -------
    np.array
        The region hashes for the gridpoints
    """
    num_hyperplanes = points.shape[0]
    num_regions = gridpoints.shape[0]
    region_hashes = np.zeros((num_regions, (num_hyperplanes + 63) // 64), dtype=np.int64)
    # region hashes assigns each gridpoint to a region based on the hyperplanes
    # each set of 64 hyperplanes forms a bitwise hash map for each gridpoint
    for i, point in enumerate(points):
        gridpoints_cont = np.ascontiguousarray(gridpoints - point)
        point_cont = np.ascontiguousarray(point)
        signs = np.sign(np.dot(gridpoints_cont, point_cont)).astype(np.int8)
        bucket, offset = divmod(i, 64)
        region_hashes[:, bucket] += (signs > 0).astype(np.int64) << offset

    return region_hashes


def _hash_tuple_to_unit_interval(tup, salt=0):
    """Return deterministic float in [0,1) from an integer tuple.

    Parameters
    ----------
    tup : tuple
        The integer tuple to hash
    salt : int, optional
        Salt value for the hash (default 0)

    Returns
    -------
    float
        Deterministic value in [0,1)
    """
    hash_obj = hashlib.blake2b(digest_size=8)
    hash_obj.update(np.array([salt], dtype=np.int64).tobytes())
    hash_obj.update(np.array(tup, dtype=np.int64).tobytes())
    val = int.from_bytes(hash_obj.digest(), 'little')
    return (val & ((1 << 53) - 1)) / float(1 << 53)  # map to [0,1)


def hyperplane_colorer_2d(points, gridpoints, colorcutoffs, salt=12345):
    """Return color indices for a 2D ball partitioned by hyperplanes.

    Color is deterministic per-region using a hash of the region's bit-signature,
    so changing N (grid resolution) won't reshuffle colors.

    Parameters
    ----------
    points : np.array
        The hyperplane points
    gridpoints : np.array
        The grid points to color
    colorcutoffs : np.array
        The color cutoff values
    salt : int, optional
        Salt for deterministic coloring (default 12345)

    Returns
    -------
    np.array
        The color indices for each region
    """
    region_hashes = hyperplane_partition(points, gridpoints)

    # Convert per-point multi-int signatures to tuples (hashable)
    region_hashes_tuples = [tuple(row) for row in region_hashes]

    # Build a stable mapping: region tuple -> color index
    color_lookup = {}
    def color_index_for_region(t):
        if t not in color_lookup:
            u = _hash_tuple_to_unit_interval(t, salt=salt)   # deterministic in [0,1)
            color_lookup[t] = np.digitize(u, colorcutoffs)   # 0..len(colorcutoffs)
        return color_lookup[t]

    regions = np.fromiter(
        (color_index_for_region(t) for t in region_hashes_tuples),
        dtype=np.int32,
        count=len(region_hashes_tuples)
    )
    return regions


# Default color schemes
frozen_lake_colors = ['#043765', "#edf8fe", 'green', 'purple', 'orange',
                      'yellow', 'pink', 'cyan', 'magenta', 'navy']


def plot_hyperplanes_color_2d(radius, grid_resolution=100, colorcutoffs=None,
                              cmap_list=None, figsize=(6, 6), preview_dpi=100):
    """Plot the Poisson hyperplane process in a ball in 2D, colored by region.

    Parameters
    ----------
    radius : float
        The radius of the enveloping ball of the Poisson hyperplane process
    grid_resolution : int, optional
        The number of points in the grid in each direction (default 100)
    colorcutoffs : np.array, optional
        The cutoffs for coloring the regions from a uniform [0,1] variable
        (default np.array([0.5]))
    cmap_list : list, optional
        The colors corresponding to the cutoffs (default frozen_lake_colors)
    figsize : tuple, optional
        The size of the figure (default (6, 6))
    preview_dpi : int, optional
        The dpi of the displayed figure (default 100)

    Returns
    -------
    matplotlib.figure.Figure
        The figure object
    """
    if colorcutoffs is None:
        colorcutoffs = np.array([0.5])
    if cmap_list is None:
        cmap_list = frozen_lake_colors

    if len(colorcutoffs) > len(cmap_list) - 1:
        raise ValueError(
            f"Too many colors: got {len(colorcutoffs)} cutoffs but only "
            f"{len(cmap_list) - 1} colors available.")

    cmap = mcolors.ListedColormap(cmap_list)

    dimension = 2
    num_points = np.random.poisson(rate(dimension, radius))
    points = sample_from_ball(dimension, num_points) * radius

    x_coords = np.linspace(-radius, radius, grid_resolution)
    y_coords = np.linspace(-radius, radius, grid_resolution)
    xx_coords, yy_coords = np.meshgrid(x_coords, y_coords)
    gridpoints = np.c_[xx_coords.ravel(), yy_coords.ravel()]

    # Use the updated safe colorer
    values = hyperplane_colorer_2d(points, gridpoints, colorcutoffs).reshape(
        grid_resolution, grid_resolution)

    fig, axes = plt.subplots(figsize=figsize, dpi=preview_dpi)
    # the first set of colors is for fig. 1.a., the second set is for fig. 1.b.
    bounds = np.linspace(-0.5, len(cmap.colors) - 0.5, len(cmap.colors) + 1)
    norm = mcolors.BoundaryNorm(bounds, cmap.N)

    axes.imshow(values, extent=(-radius, radius, -radius, radius), origin='lower',
                cmap=cmap, norm=norm, interpolation='nearest', resample=False)

    # Create a circular clip path
    clip_circle = Circle((0, 0), radius, transform=axes.transData)
    for artist in axes.get_children():
        artist.set_clip_path(clip_circle)
    axes.set_aspect('equal')
    axes.axis('off')
    plt.show()

    return fig
    