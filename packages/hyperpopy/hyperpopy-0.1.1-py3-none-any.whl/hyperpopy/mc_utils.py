"""Monte Carlo utilities for Poisson hyperplane partitions and related plots.

This module provides functions to:
- simulate hyperplane-induced partitions and estimate connectivity distributions,
- compute and plot convergence with error bars against analytic results,
- sample and visualize conditional color probability fields in 2D/3D,
- estimate chord length statistics across dimensions,
- generate helper figures used in analyses.
"""

# Allow short/non-snake-case variable names used in plotting/math
# pylint: disable=invalid-name

from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

from .analytic_utils import (
    rate,
    generate_all_connectivity_tuples,
    color_distribution,
)
from .generation_utils import (
    sample_from_ball,
    hyperplane_partition,
    hyperplane_colorer_2d,
)

### Beyond this point, the functions are for Monte Carlo simulations and
### wrappers for plotting the figures from the paper.

def monte_carlo_hyperplane_partitions(
    dimension,
    radius,
    gridpoints,
    num_samples,
):
    """Return distribution of connectivity tuples for hyperplane partitions.

    - dimension: int, dimension of the space
    - radius: float, radius of the ball
    - gridpoints: np.ndarray of shape (n, d), points to partition
    - num_samples: int, number of Monte Carlo samples
    """

    connectivity_counts = defaultdict(int)  # Store the counts of each connectivity

    for _ in range(num_samples):
        # Sample hyperplanes
        n_hyperplanes = np.random.poisson(rate(dimension, radius))
        hyperplanes = sample_from_ball(dimension, n_hyperplanes) * radius

        # Determine regions using the safe partition function
        region_hashes = hyperplane_partition(hyperplanes, gridpoints)

        # Convert region hashes to tuples for hashability
        region_hashes_tuples = [tuple(row) for row in region_hashes]

        # Create connectivity tuple with sorted components
        connectivity_components = defaultdict(list)
        for i, region_hash in enumerate(region_hashes_tuples):
            connectivity_components[region_hash].append(i)

        # Convert to connectivity tuple (sorted by components)
        connectivity_tuple = tuple(
            tuple(sorted(component))
            for component in connectivity_components.values()
        )

        # Increment the count of this connectivity tuple
        connectivity_counts[connectivity_tuple] += 1

    # Convert counts to probabilities
    connectivity_distribution = {k: v / num_samples for k, v in connectivity_counts.items()}
    return connectivity_distribution

def plot_convergence_all_partitions_mc(dimension, gridpoints, samples_array):
    """Plot convergence of probabilities for each connectivity graph.

    - dimension: dimension of the hyperplane
    - gridpoints: list of points to generate the hyperplanes
    - samples_array: array of sample counts for the simulation
    - analytic_probs: optional dictionary of analytic probabilities per graph
    """
    radius = max(np.linalg.norm(p) for p in gridpoints)  # Maximum distance from origin
    # Use empty arrays for nonexistent keys
    all_partition_probs = defaultdict(
        lambda: np.zeros(len(samples_array))
    )
    possible_partitions = generate_all_connectivity_tuples(len(gridpoints))

    cumulative_counts = defaultdict(int)

    for i, num_samples in enumerate(np.diff(np.insert(samples_array, 0, 0))):
        partition_probs = monte_carlo_hyperplane_partitions(
            dimension,
            radius,
            gridpoints,
            num_samples,
        )

        # Accumulate counts for each partition
        for partition, probability in partition_probs.items():
            cumulative_counts[partition] += probability * num_samples

        # Calculate probabilities at this step
        total_count = sum(cumulative_counts.values())
        for partition in possible_partitions:
            all_partition_probs[partition][i] = (
                cumulative_counts[partition] / total_count
            )

    return all_partition_probs

def monte_carlo_convergence_with_error_bars(
    dimension,
    gridpoints,
    samples_array,
    num_runs,
    analytic_probs=None,
):
    """Run convergence multiple times and plot average with error bars."""
    # Initialize sums and squared sums for averaging and std deviation
    all_partition_probs_sum = defaultdict(lambda: np.zeros(len(samples_array)))
    all_partition_probs_sq_sum = defaultdict(lambda: np.zeros(len(samples_array)))
    possible_partitions = generate_all_connectivity_tuples(len(gridpoints))

    # Run the Monte Carlo convergence multiple times
    for _ in range(num_runs):
        all_partition_probs = plot_convergence_all_partitions_mc(
            dimension,
            gridpoints,
            samples_array,
        )

        # Accumulate sum and squared sum for each partition
        for partition in possible_partitions:
            all_partition_probs_sum[partition] += all_partition_probs[partition]
            all_partition_probs_sq_sum[partition] += all_partition_probs[partition] ** 2

    # Calculate the mean and standard deviation for each partition
    all_partition_probs_mean = defaultdict(lambda: np.zeros(len(samples_array)))
    all_partition_probs_std = defaultdict(lambda: np.zeros(len(samples_array)))

    for partition in possible_partitions:
        mean = all_partition_probs_sum[partition] / num_runs
        variance = (all_partition_probs_sq_sum[partition] / num_runs) - (mean ** 2)
        stddev = np.sqrt(variance)

        all_partition_probs_mean[partition] = mean
        all_partition_probs_std[partition] = stddev

    # Plot the mean with error bars
    fig, axes_main = plt.subplots(figsize=(12, 8))
    for partition, mean_probs in all_partition_probs_mean.items():
        std_probs = all_partition_probs_std[partition]
        axes_main.errorbar(
            samples_array,
            mean_probs,
            yerr=std_probs,
            marker='o',
            label=f"H = {partition}",
            markersize=2,
            capsize=3,
        )

    # Plot analytic probabilities as horizontal lines
    if analytic_probs:
        label_added = False
        for partition, analytic_prob in analytic_probs.items():
            if not label_added:
                axes_main.axhline(
                    y=analytic_prob,
                    linestyle='--',
                    color='grey',
                    label='Analytic Solution',
                )
                label_added = True  # Set the flag to True after adding the label
            else:
                axes_main.axhline(y=analytic_prob, linestyle='--', color='grey')

    axes_main.set_xlabel('Number of Samples', fontsize=20)
    axes_main.set_ylabel('Probability of Graph H', fontsize=20)
    axes_main.set_title(
        'Connectivity Graphs of Points '
        f'{list(map(list, gridpoints))}',
        fontsize=26,
    )
    axes_main.legend(loc='upper left', borderaxespad=0., fontsize=20)
    axes_main.tick_params(axis='both', which='major', labelsize=14)  # Major ticks
    axes_main.tick_params(axis='both', which='minor', labelsize=12)  # Minor ticks
    axes_main.set_xscale('log')

    # Add inset for log error
    if analytic_probs:
        inset_ax = fig.add_axes(
            [0.51, 0.55, 0.25, 0.25], facecolor='white'
        )
        inset_ax.patch.set_alpha(.8)  # Adjust transparency of the inset background
        for partition, mean_probs in all_partition_probs_mean.items():
            if partition in analytic_probs:
                analytic_prob = analytic_probs[partition]
                log_error = np.log10(np.abs(mean_probs - analytic_prob))
                inset_ax.plot(samples_array, log_error, label=f"H = {partition}")

        inset_ax.set_xscale('log')
        inset_ax.set_title(r'$\log_{10}$ Error', fontsize=20)
        inset_ax.tick_params(axis='both', which='major', labelsize=14)
        for spine in inset_ax.spines.values():
            spine.set_edgecolor('black')  # Ensure spine color stands out
            spine.set_linewidth(1.2)     # Make spines slightly thicker
            spine.set_zorder(5)          # Draw spines above background
        inset_ax.text(
            0.5,
            0.05,
            'Samples',
            fontsize=20,
            transform=inset_ax.transAxes,
            ha='center',
            va='bottom',
            color='black',
            bbox={'facecolor': 'white', 'alpha': 0.8, 'edgecolor': 'none'},
        )

    return fig, axes_main, all_partition_probs_mean, all_partition_probs_std

def hyperplane_colorer_3d(points, gridpoints, colorcutoffs):
    """Assign color indices to 3D regions formed by hyperplanes.

    Parameters
    ----------
    points : np.array
        Points that define hyperplanes
    gridpoints : np.array
        Points at which to evaluate the partition
    colorcutoffs : np.array
        Cutoffs for digitizing random uniforms into color bins
    """
    region_hashes = hyperplane_partition(points, gridpoints)

    # Use tuple-based representation instead of strings
    region_hashes_tuples = [tuple(row) for row in region_hashes]
    unique_dict = {}
    inverse_indices = []
    counter = 0

    # Manual uniqueness detection
    for row in region_hashes_tuples:
        if row not in unique_dict:
            unique_dict[row] = counter
            counter += 1
        inverse_indices.append(unique_dict[row])

    unique_regions = list(unique_dict.keys())
    num_unique_regions = len(unique_regions)

    # Assign random colors
    colors = np.random.uniform(size=num_unique_regions)
    color_indices = np.digitize(colors, colorcutoffs)

    # Map color indices to gridpoints
    regions = np.array(
        [color_indices[inverse_indices[i]] for i in range(len(gridpoints))],
        dtype=np.int32,
    )
    return regions

def colors_mc(dimension, gridpoints, color_dist, colors, samples_array):
    """Estimate conditional color probabilities at the last point.

    - dimension: dimension of the hyperplane
    - r: radius to generate the hyperplanes
    - gridpoints: numpy array of points to evaluate probabilities for
    - color_dist: tuple, probability distribution of colors
    - colors: tuple of colors for points[:-1]
    - samples_array: array of sample sizes (e.g., from np.logspace)

    Returns an array of shape (num_colors, len(samples_array)) with probabilities.
    """

    # cumulative sum of color distribution to get cutoff values for each color
    colorcutoffs = np.cumsum(color_dist)[:-1]
    # maximum distance from origin
    r = max(np.linalg.norm(p) for p in gridpoints) * 1.25
    if dimension == 2:
        hyperplane_colorer = hyperplane_colorer_2d
    elif dimension == 3:
        hyperplane_colorer = hyperplane_colorer_3d
    else:
        raise ValueError("Unsupported dimension for colors_mc: expected 2 or 3")
    
    conditional_count = 0  # times colors[::-1] equals colors of gridpoints[::-1]

    color_counts = np.zeros(len(color_dist))  # counts of last point's color
    color_probs = np.zeros((len(color_dist), len(samples_array)))  # probs per color/sample

    for i, num_samples in enumerate(np.diff(np.insert(samples_array, 0, 0))):
        for _ in range(num_samples):
            n_hyper = np.random.poisson(rate(dimension, r))  # num hyperplanes
            points = sample_from_ball(dimension, n_hyper) * r  # sample points

            color_values = hyperplane_colorer(points, gridpoints, colorcutoffs)
            if np.all(color_values[:-1] == colors):
                conditional_count += 1
                color_counts[color_values[-1]] += 1  # record last point's color
        color_probs[:, i] = (
            color_counts / conditional_count if conditional_count > 0 else 0
        )

    return color_probs

def plot_mc_colors_with_errorbars(
    dimension,
    gridpoints,
    color_dist,
    colors,
    samples_array,
    num_runs,
    analytic_probs=False,
):
    """Wrapper: run convergence multiple times and plot average with error bars.
    dimension: dimension of the hyperplane
    gridpoints: numpy array of points, all but the last are conditioned on with colors from "colors"
    color_dist: tuple, the probability distribution of colors
    colors: tuple of colors for points[:-1]
    samples_array: array of number of samples to run the simulation
    num_runs: number of epochs, used to calculate the mean and standard deviation"""

    # Run the Monte Carlo convergence multiple times
    color_probs_sum = np.zeros((len(color_dist), len(samples_array)))
    color_probs_sq_sum = np.zeros((len(color_dist), len(samples_array)))
    for _ in range(num_runs):
        color_probs = colors_mc(dimension, gridpoints, color_dist, colors, samples_array)
        color_probs_sum += color_probs
        color_probs_sq_sum += color_probs**2

    # Calculate the mean and standard deviation for each color
    color_probs_mean = color_probs_sum / num_runs
    variance = (color_probs_sq_sum / num_runs) - (color_probs_mean ** 2)
    stdev = np.sqrt(variance)

    # Calculate analytic probabilities if requested
    analytic_color_dist = None
    if analytic_probs:
        analytic_color_dist = color_distribution(
            gridpoints, colors, color_dist
        )

    # Plot the mean with error bars
    fig, ax = plt.subplots(figsize=(12, 8))
    for color in range(len(color_dist)):
        ax.errorbar(
            samples_array,
            color_probs_mean[color],
            yerr=stdev[color],
            marker='o',
            label=f"Color {color}",
            markersize=2,
            capsize=3,
        )

    if analytic_probs:
        label_added = False
        for color in range(len(color_dist)):
            if not label_added:
                ax.axhline(
                    y=analytic_color_dist[color],
                    linestyle='--',
                    color='grey',
                    label='Analytic Solution',
                )
                label_added = True  # Add the label only once
            else:
                ax.axhline(
                    y=analytic_color_dist[color], linestyle='--', color='grey'
                )

    ax.set_xlabel('Number of Samples', fontsize=20)
    ax.set_ylabel('Probability of Color', fontsize=20)
    ax.set_title(
        'Color of '
        f'{list(map(list, gridpoints))[-1]} '
        'Given '
        f'{list(map(list, gridpoints))[:-1]}',
        fontsize=26,
    )
    ax.legend(loc='upper left', borderaxespad=0., fontsize=20)
    ax.tick_params(axis='both', which='major', labelsize=14)  # Major ticks
    ax.tick_params(axis='both', which='minor', labelsize=12)  # Minor ticks
    ax.set_xscale('log')

    # Add inset for log error
    if analytic_probs:
        inset_ax = fig.add_axes(
            [0.5, 0.4, 0.25, 0.25], facecolor="white", alpha=.3
        )  # [left, bottom, width, height]
        inset_ax.patch.set_alpha(.4)  # Adjust transparency of the inset background
        for color in range(len(color_dist)):
            log_error = np.log10(
                np.abs(analytic_color_dist[color] - color_probs_mean[color])
            )
            inset_ax.plot(samples_array, log_error, label=f"Color {color}")

        inset_ax.set_xscale('log')
        inset_ax.set_ylabel(r'$\log_{10}$ Error', fontsize=20)
        inset_ax.tick_params(axis='both', which='major', labelsize=14)
        inset_ax.text(
            0.5,
            0.05,
            'Samples',
            fontsize=20,
            transform=inset_ax.transAxes,
            ha='center',
            va='bottom',
            color='black',
            bbox={'facecolor': 'white', 'alpha': 0.8, 'edgecolor': 'none'},
        )

    return fig, ax, color_probs_mean, stdev

### code for checking chord length convergence ###

def hyperplane_colorer_1d(points, gridpoints, colorcutoffs = np.array([0.5])):
    """Returns the colors of regions of a 1-dimensional ball partitioned by hyperplnes (points)
    
    points: np.array, shape (n,d), of points defining the hyperplanes
    gridpoints: np.array, shape (N,d), the points at which to evaluate the hyperplanes
    colorcutoffs: np.array, the cutoffs for the colors

    returns: np.array, the color values for the gridpoints
    """

    points = np.sort(points, axis=0)
    colors = np.random.uniform(size=len(points)+1)  # number of regions is num hyperpoints + 1
    color_indices = np.digitize(colors, colorcutoffs)

    color_field = np.zeros(len(gridpoints), dtype=int)

    current_point_index = 0
    for i, gridpoint in enumerate(gridpoints):
        if (current_point_index == len(points)) or gridpoint < points[current_point_index]:
            color_field[i] = color_indices[current_point_index]
        else:
            current_point_index += 1
            color_field[i] = color_indices[current_point_index]
    return color_field

def check_chord_length(color_field, resolution):
    """Returns the sum of left and right chord lengths for a color_field line of colors
    color_field: numpy array of colors along a line
    resolution: int, the linear density of the gridpoints defining the color_field
    returns: int, sum of left and right chord lengths (furthest we can go before color changes)
    """

    if len(color_field.shape) != 1:
        color_field = color_field[:, 0]  # disregard coordinates outside the line direction
    left_idx = len(color_field) // 2
    right_idx = len(color_field) // 2
    mid_idx = len(color_field) // 2

    while left_idx >= 0 and color_field[left_idx] == color_field[mid_idx]:
        left_idx -= 1
    while right_idx < len(color_field) and color_field[right_idx] == color_field[mid_idx]:
        right_idx += 1

    return (right_idx - left_idx - 1) / resolution  # convert index length to distance



def mc_chord_length(dimension, radius, resolution, color_dist, samples_array):
    """Average chord length (distnce until material boundary) in Poisson media.
    dimension: int, dimension of the hyperplane
    radius: int, radius of ball to generate hyperplanes in
    resolution: int, the linear density of gridpoints
    color_dist: tuple, the probability distribution of colors
    samples_array: array of number of samples to run the simulation
    """
    if dimension == 1:
        hyperplane_colorer = hyperplane_colorer_1d
    elif dimension == 2:
        hyperplane_colorer = hyperplane_colorer_2d
    elif dimension == 3:
        hyperplane_colorer = hyperplane_colorer_3d
    else:
        raise ValueError("Unsupported dimension for mc_chord_length: expected 1, 2 or 3")

    chord_lengths = np.zeros(len(samples_array))
    chord_length_sum = 0
    count = 0
    for i, num_samples in enumerate(np.diff(np.insert(samples_array, 0, 0))):
        for _ in range(num_samples):
            num_hyperplanes = np.random.poisson(rate(dimension, radius))
            points = sample_from_ball(dimension, num_hyperplanes) * radius
            num_gridpoints = 2 * radius * resolution
            gridpoints_x = np.linspace(-radius, radius, num_gridpoints)  # points lie along a line
            gridpoints = np.zeros((num_gridpoints, dimension))
            gridpoints[:,0] = gridpoints_x

            colorcutoffs = np.cumsum(color_dist)[:-1]
            color_values = hyperplane_colorer(points, gridpoints, colorcutoffs)
            # divide by 2 to average left and right chords
            chord_length_sum += check_chord_length(color_values, resolution) / 2
            count += 1
        chord_lengths[i] = chord_length_sum/count

    return chord_lengths

def plot_mc_chord_lengths_with_errorbars(radius, resolution, color_dist, samples_array, num_runs):
    """Wrapper function that runs the convergence of chord lengths multiple times and plots
    the convergence with error bars to a common value for dimensions d=1,2, and 3.

    radius: int, radius of ball to generate hyperplanes in
    resolution: int, the linear density of gridpoints
    color_dist: tuple, the probability distribution of colors
    samples_array: array of number of samples to run the simulation
    num_runs: number of epochs, used to calculate the mean and standard deviation"""
    
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlabel('Number of Samples', fontsize=20)
    ax.set_ylabel('Average Chord Length', fontsize=20)
    ax.set_title('Dimension Independant Chord Lengths', fontsize=26)
    ax.tick_params(axis='both', which='major', labelsize=14)  # Major ticks
    ax.tick_params(axis='both', which='minor', labelsize=12)  # Minor ticks

    chord_lengths_mean_ret = np.zeros((3, len(samples_array)))
    stdev_ret = np.zeros((3, len(samples_array)))

    analytic_solution = sum(color_prob / (1 - color_prob) for color_prob in color_dist)

    for dimension in (1, 2, 3):

        chord_lengths_sum = np.zeros(len(samples_array))
        chord_lengths_sq_sum = np.zeros(len(samples_array))
        for _ in range(num_runs):
            #print(f"dimension={dimension}, {_/num_runs*100}% done")
            chord_lengths = mc_chord_length(
                dimension, radius, resolution, color_dist, samples_array
            )
            chord_lengths_sum += chord_lengths
            chord_lengths_sq_sum += chord_lengths**2

        chord_lengths_mean = chord_lengths_sum / num_runs
        variance = (chord_lengths_sq_sum / num_runs) - (chord_lengths_mean ** 2)
        stdev = np.sqrt(variance)

        ax.errorbar(
            samples_array,
            chord_lengths_mean,
            yerr=stdev,
            marker='o',
            markersize=2,
            capsize=3,
            label=f"d = {dimension}",
        )
        chord_lengths_mean_ret[dimension-1] = chord_lengths_mean
        stdev_ret[dimension-1] = stdev

    ax.axhline(
        y=analytic_solution,
        linestyle='--',
        color='grey',
        label='Analytic Solution',
    )
    ax.legend(loc='upper left', borderaxespad=0., fontsize=20)

    return fig, ax, chord_lengths_mean_ret, stdev_ret

### End of chord length code ###

def probability_landscape(
    points,
    colors,
    color_dist,
    region_size=1,
    grid_resolution=10,
    save=False,
    all_colors=False,
    plot=False,
    explicit_region=None,
):
    """
    Plots the probability landscape of color distribution for the given points in
    2D space, both as 3D and contour plot.
    
    Parameters:
    points: np.array, shape (n, 2), n points in 2D space whose colors are
      conditioned on.
    colors: tuple, length n, representing the color assigned to each point.
    color_dist: tuple, the initial probabilities of each color.
    region_size: float, size of the region around the points to visualize.
      Default is 1.
    grid_resolution: int, resolution of the grid in the region to plot.
      Default is 10.
    all_colors: bool, whether to plot all colors or just the first one.
      Default False.
    explicit_region: tuple, explicit region (x_min, x_max, y_min, y_max).
      Default None.

    Returns: list, containing tuples for both the 3D and contour plots for each color
            Each tuple contains (fig, ax, z) for 3D and (fig, ax, z) for the contour plot.
    """
    
    num_colors = len(color_dist)  # Number of color categories
    
    if not explicit_region:
        # Determine the region to plot based on the min/max of the points
        x_min, y_min = np.min(points, axis=0) - region_size
        x_max, y_max = np.max(points, axis=0) + region_size
    else:
        x_min, x_max, y_min, y_max = explicit_region
    dimension = points.shape[1]  # Dimension of the points
    if dimension == 2:
        dummy_point = np.array([x_min, y_min])  # Dummy point to represent the grid point
    else:
        dummy_point = np.array([x_min, y_min, 0])
    # Create a grid of points in the region
    x = np.linspace(x_min, x_max, grid_resolution)
    y = np.linspace(y_min, y_max, grid_resolution)
    xx, yy = np.meshgrid(x, y)
    grid_points = np.c_[xx.ravel(), yy.ravel()]  # Flatten the grid into (x, y) coordinates

    # Array to store color probabilities for each grid point
    color_probs_grid = np.zeros((grid_resolution, grid_resolution, num_colors))

    # Loop through grid points and calculate color distribution for each point
    for i, grid_point in enumerate(grid_points):
        # Print progress every 5%
        #if i % (grid_resolution * grid_resolution // 20) == 0:
            #print(f"{i / (grid_resolution * grid_resolution) * 100}% of the grid done")
        
        # Build fresh array for each grid point to avoid mutation issues
        if dimension == 2:
            pts = np.vstack([points, grid_point])
        elif dimension == 3:
            pts = np.vstack([points, np.append(grid_point, 0)])
        else:
            raise ValueError(f"Unsupported dimension: {dimension}")
        color_probs = color_distribution(pts, colors, color_dist)  # Get color distribution

        # Compute the corresponding 2D index for storing results
        grid_x_idx = i // grid_resolution
        grid_y_idx = i % grid_resolution

        # Avoid index errors by ensuring valid indices
        if grid_x_idx < grid_resolution and grid_y_idx < grid_resolution:
            # Store the color probabilities at the correct grid location
            color_probs_grid[grid_x_idx, grid_y_idx, :] = color_probs

    # Plot the probability landscape for each color in both 3D and contour form
    for color_index in range(num_colors):
        if not all_colors and color_index > 0:
            continue

        z = color_probs_grid[:, :, color_index]  # Extract the probabilities for the current color
        if not plot:
            return (((None, None, z), (None, None, z)))  # keep output consistent

        # Plot the 3D surface for the current color
        fig_3d = plt.figure()
        ax_3d = fig_3d.add_subplot(111, projection='3d')
        ax_3d.plot_surface(xx, yy, z, cmap='viridis', alpha=1, zorder=1)

        # Add labels and titles for 3D plot
        geometry = "Poisson"
        pointslist = list(map(list, np.round(points, 2)))
        colorlist = list(map(int, colors))
        title_3d = (
            f"{geometry} Probability Landscape (3D) for Color {color_index}\n"
            f"Points: {pointslist} \n"
            f"Colors: {colorlist}, Color Distribution: {color_dist}"
        )
        ax_3d.set_title(title_3d, multialignment='center')
        ax_3d.set_xlabel('X axis')
        ax_3d.set_ylabel('Y axis')
        ax_3d.set_zlabel(f"Probability (Color {color_index})")

        # Create contour plot for the same data
        fig_contour, ax_contour = plt.subplots()
        levels = np.linspace(0, 1, 20)  #Contour levels
        contour = ax_contour.contourf(xx, yy, z, levels=levels, cmap='viridis')
        # Add contour line specifically at the raw probability value
        ax_contour.contour(
            xx,
            yy,
            z,
            levels=[color_dist[color_index]],
            colors='red',
            linewidths=2,
        )
        fig_contour.colorbar(contour, ax=ax_contour)

        # Add labels and titles for contour plot
        title_contour = (
            f"{geometry} Probability for Color {color_index}\n"
            f"Points: {pointslist} \n"
            f"Colors: {colorlist}, Color Distribution: {color_dist}"
        )
        ax_contour.set_title(title_contour, multialignment='center')
        ax_contour.set_xlabel('X axis')
        ax_contour.set_ylabel('Y axis')

        if save:
            random_index = np.random.randint(10000000)
            fig_3d.savefig(f'{geometry}_landscape_color_{color_index}_{random_index}.pdf')
            fig_contour.savefig(f'{geometry}_contour_color_{color_index}_{random_index}.pdf')

        # Show the plots
        plt.show()

    return (((fig_3d, ax_3d, z), (fig_contour, ax_contour, z)))

def figure_3_helper(color_dist=(.5, .5), grid_resolution=30):
    """Generate data and plots for Figure 3 helper visualization."""
    all_landscape_data = []

    ### Beggining with subfigures a,b,c ###

    fig, axs = plt.subplots(3, 2, figsize=(10, 18))
    subplot_labels = ['(a)', '(b)', '(c)', '(d)', '(e)', '(f)']
    m = 1  # effectively controls the length scale/hyperplane arrival rate for the entire plot

    axs = axs.ravel()
    x_min, y_min = -1 * m, -1 * m
    x_max, y_max = 2 * m, 2 * m
    x = np.linspace(x_min, x_max, grid_resolution)
    y = np.linspace(y_min, y_max, grid_resolution)
    xx, yy = np.meshgrid(x, y)
    explicit_region = (x_min, x_max, y_min, y_max)  # xmin xmax ymin ymax

    points = np.array([[0, 0], [0, 1 * m]])
    colors = (0, 1)
    z = probability_landscape(
        points,
        colors,
        color_dist,
        grid_resolution=grid_resolution,
        explicit_region=explicit_region,
    )[1][-1]
    all_landscape_data.append({
        'xx': xx.copy(),
        'yy': yy.copy(),
        'z': z.copy(),
        'points': points.copy(),
        'colors': np.array(colors)
    })
    ax = axs[0]
    contour_levels = np.linspace(0, 1, 21)
    contour = ax.contourf(xx, yy, z, levels=contour_levels, cmap='viridis')
    #ax.set_title("CPF For Points [0,0], [0,1]", fontsize = 20)
    ax.set_aspect('equal')
    ax.text(
        -0.1,
        1.1,
        subplot_labels[0],
        transform=ax.transAxes,
        fontsize=20,
        fontweight='bold',
        va='top',
        ha='right',
    )
    ax.tick_params(axis='both', which='major', labelsize=14)  # Major ticks
    ax.tick_params(axis='both', which='minor', labelsize=12)  # Minor ticks
    ax.contour(xx, yy, z, levels=[0.5], colors='blue', linewidths=2)  # Add blue contour at 50%
    #now add red dots where the points are
    color_map = {0: 'black', 1: 'orange'}  # Define your mapping
    for point, c in zip(points, colors):
        ax.scatter(*point[:2], marker="+", color=color_map[c], s=100)

    points = np.array([[0, 0], [0, 1 * m], [1 * m, 0]])
    colors = (0, 1, 1)
    z = probability_landscape(
        points,
        colors,
        color_dist,
        grid_resolution=grid_resolution,
        explicit_region=explicit_region,
    )[1][-1]
    all_landscape_data.append({
        'xx': xx.copy(),
        'yy': yy.copy(),
        'z': z.copy(),
        'points': points.copy(),
        'colors': np.array(colors)
    })
    ax = axs[2]
    contour = ax.contourf(xx, yy, z, levels=contour_levels, cmap='viridis')
    #ax.set_title("[0,0], [0,1], [1,0]", fontsize = 20)
    ax.set_aspect('equal')
    ax.text(
        -0.1,
        1.1,
        subplot_labels[1],
        transform=ax.transAxes,
        fontsize=20,
        fontweight='bold',
        va='top',
        ha='right',
    )
    ax.tick_params(axis='both', which='major', labelsize=14)  # Major ticks
    ax.tick_params(axis='both', which='minor', labelsize=12)  # Minor ticks
    ax.contour(xx, yy, z, levels=[0.5], colors='blue', linewidths=2)  # Add blue contour at 50%
    color_map = {0: 'black', 1: 'orange'}  # Define your mapping
    for point, c in zip(points, colors):
        ax.scatter(*point[:2], marker="+", color=color_map[c], s=100)

    points = np.array([[0, 1 * m, 0], [1 * m, 0, 0], [0, 0, .5 * m]])
    colors = (1, 1, 0)
    z = probability_landscape(
        points,
        colors,
        color_dist,
        grid_resolution=grid_resolution,
        explicit_region=explicit_region,
    )[1][-1]
    all_landscape_data.append({
        'xx': xx.copy(),
        'yy': yy.copy(),
        'z': z.copy(),
        'points': points.copy(),
        'colors': np.array(colors)
    })
    ax = axs[4]
    contour = ax.contourf(xx, yy, z, levels=contour_levels, cmap='viridis')
    #ax.set_title("[0,1,0], [1,0,0], [0,0,.5]", fontsize = 20)
    ax.set_aspect('equal')
    ax.text(
        -0.1,
        1.1,
        subplot_labels[2],
        transform=ax.transAxes,
        fontsize=20,
        fontweight='bold',
        va='top',
        ha='right',
    )
    ax.tick_params(axis='both', which='major', labelsize=14)  # Major ticks
    ax.tick_params(axis='both', which='minor', labelsize=12)  # Minor ticks
    ax.contour(xx, yy, z, levels=[0.5], colors='blue', linewidths=2)  # Add blue contour at 50%
    color_map = {0: 'black', 1: 'orange'}  # Define your mapping
    for point, c in zip(points, colors):
        ax.scatter(*point[:2], marker="+", color=color_map[c], s=100)

    ### Now do subfigures d,e,f ###
    m = .05  # effectively controls the length scale/hyperplane arrival rate for the entire plot

    axs = axs.ravel()
    x_min, y_min = -1 * m, -1 * m
    x_max, y_max = 2 * m, 2 * m
    x = np.linspace(x_min, x_max, grid_resolution)
    y = np.linspace(y_min, y_max, grid_resolution)
    xx, yy = np.meshgrid(x, y)
    explicit_region = (x_min, x_max, y_min, y_max)  # xmin xmax ymin ymax

    points = np.array([[0, 0], [0, 1 * m]])
    colors = (0, 1)
    z = probability_landscape(
        points,
        colors,
        color_dist,
        grid_resolution=grid_resolution,
        explicit_region=explicit_region,
    )[1][-1]
    all_landscape_data.append({
        'xx': xx.copy(),
        'yy': yy.copy(),
        'z': z.copy(),
        'points': points.copy(),
        'colors': np.array(colors)
    })
    ax = axs[1]
    contour_levels = np.linspace(0, 1, 21)
    contour = ax.contourf(xx, yy, z, levels=contour_levels, cmap='viridis')
    #ax.set_title("CPF For Points [0,0], [0,1]", fontsize = 20)
    ax.set_aspect('equal')
    ax.text(
        -0.1,
        1.1,
        subplot_labels[3],
        transform=ax.transAxes,
        fontsize=20,
        fontweight='bold',
        va='top',
        ha='right',
    )
    ax.tick_params(axis='both', which='major', labelsize=14)  # Major ticks
    ax.tick_params(axis='both', which='minor', labelsize=12)  # Minor ticks
    ax.contour(xx, yy, z, levels=[0.5], colors='blue', linewidths=2)  # Add blue contour at 50%
    color_map = {0: 'black', 1: 'orange'}  # Define your mapping
    for point, c in zip(points, colors):
        ax.scatter(*point[:2], marker="+", color=color_map[c], s=100)


    points = np.array([[0, 0], [0, 1 * m], [1 * m, 0]])
    colors = (0, 1, 1)
    z = probability_landscape(
        points,
        colors,
        color_dist,
        grid_resolution=grid_resolution,
        explicit_region=explicit_region,
    )[1][-1]
    all_landscape_data.append({
        'xx': xx.copy(),
        'yy': yy.copy(),
        'z': z.copy(),
        'points': points.copy(),
        'colors': np.array(colors)
    })
    ax = axs[3]
    contour = ax.contourf(xx, yy, z, levels=contour_levels, cmap='viridis')
    #ax.set_title("[0,0], [0,1], [1,0]", fontsize = 20)
    ax.set_aspect('equal')
    ax.text(
        -0.1,
        1.1,
        subplot_labels[4],
        transform=ax.transAxes,
        fontsize=20,
        fontweight='bold',
        va='top',
        ha='right',
    )
    ax.tick_params(axis='both', which='major', labelsize=14)  # Major ticks
    ax.tick_params(axis='both', which='minor', labelsize=12)  # Minor ticks
    ax.contour(xx, yy, z, levels=[0.5], colors='blue', linewidths=2)  # Add blue contour at 50%
    color_map = {0: 'black', 1: 'orange'}  # Define your mapping
    for point, c in zip(points, colors):
        ax.scatter(*point[:2], marker="+", color=color_map[c], s=100)


    points = np.array([[0, 1 * m, 0], [1 * m, 0, 0], [0, 0, .5 * m]])
    colors = (1, 1, 0)
    z = probability_landscape(
        points,
        colors,
        color_dist,
        grid_resolution=grid_resolution,
        explicit_region=explicit_region,
    )[1][-1]
    all_landscape_data.append({
        'xx': xx.copy(),
        'yy': yy.copy(),
        'z': z.copy(),
        'points': points.copy(),
        'colors': np.array(colors)
    })
    ax = axs[5]
    contour = ax.contourf(xx, yy, z, levels=contour_levels, cmap='viridis')
    #ax.set_title("[0,1,0], [1,0,0], [0,0,.5]", fontsize = 20)
    ax.set_aspect('equal')
    ax.text(
        -0.1,
        1.1,
        subplot_labels[5],
        transform=ax.transAxes,
        fontsize=20,
        fontweight='bold',
        va='top',
        ha='right',
    )
    ax.tick_params(axis='both', which='major', labelsize=14)  # Major ticks
    ax.tick_params(axis='both', which='minor', labelsize=12)  # Minor ticks
    ax.contour(xx, yy, z, levels=[0.5], colors='blue', linewidths=2)  # Add blue contour at 50%
    color_map = {0: 'black', 1: 'orange'}  # Define your mapping
    for point, c in zip(points, colors):
        ax.scatter(*point[:2], marker="+", color=color_map[c], s=100)

    cbar = fig.colorbar(contour, ax=axs, orientation='horizontal', shrink=.9, pad=0.05)
    cbar.set_ticks(np.linspace(0, 1, 11))
    plt.show()

    # No explicit return value needed


if __name__ == "__main__":
    import doctest
    doctest.testmod()
