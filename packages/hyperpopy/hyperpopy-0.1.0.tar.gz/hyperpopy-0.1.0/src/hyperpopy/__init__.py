"""
HyperPopy: Poisson Hyperplane Model Package

A Python package for working with Poisson hyperplane models, including:
- Analytical calculations for connectivity and color distributions
- Generation and visualization of Poisson hyperplane realizations
- Monte Carlo simulation utilities

This package provides tools for:
- Calculating conditional probability functions for color in Poisson hyperplane models
- Generating and plotting realizations of the Poisson hyperplane process
- Monte Carlo estimation of connectivity distributions and color probabilities
- Visualization of conditional probability functions and convergence analysis
"""

__version__ = "0.1.0"
__author__ = "Alec Shelley"
__email__ = "ams01@stanford.edu"

# Import main functions from each module for easy access
from .analytic_utils import (
    rate,
    generate_all_connectivity_tuples,
    allowed_tuples_colors,
    graph_cutter,
    hitrate_1d,
    hitrate_2d,
    hitrate_3d,
    slash_rates,
    color_distribution,
    color_from_partitions,
)

from .generation_utils import (
    sample_from_ball,
    hyperplane_partition,
    hyperplane_colorer_2d,
    plot_hyperplanes_color_2d,
    frozen_lake_colors,
)

from .mc_utils import (
    monte_carlo_hyperplane_partitions,
    monte_carlo_convergence_with_error_bars,
    plot_mc_colors_with_errorbars,
    plot_mc_chord_lengths_with_errorbars,
    probability_landscape,
    figure_3_helper,
)

# Define what gets imported with "from popy import *"
__all__ = [
    # Version info
    "__version__",
    "__author__", 
    "__email__",
    
    # Analytic utilities
    "rate",
    "generate_all_connectivity_tuples",
    "allowed_tuples_colors", 
    "graph_cutter",
    "hitrate_1d",
    "hitrate_2d", 
    "hitrate_3d",
    "slash_rates",
    "color_distribution",
    "color_from_partitions",
    
    # Generation utilities
    "sample_from_ball",
    "hyperplane_partition",
    "hyperplane_colorer_2d", 
    "plot_hyperplanes_color_2d",
    "frozen_lake_colors",
    
    # Monte Carlo utilities
    "monte_carlo_hyperplane_partitions",
    "monte_carlo_convergence_with_error_bars",
    "plot_mc_colors_with_errorbars",
    "plot_mc_chord_lengths_with_errorbars", 
    "probability_landscape",
    "figure_3_helper",
]
