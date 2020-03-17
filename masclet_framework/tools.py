"""
MASCLET framework

Provides several functions to read MASCLET outputs and perform basic operations.
Also, serves as a bridge between MASCLET data and the yt package (v 3.5.1).

tools module
Contains several useful functions that other modules might need

Created by David Vallés
"""

#  Last update on 17/3/20 20:22

# GENERAL PURPOSE AND SPECIFIC LIBRARIES USED IN THIS MODULE

# numpy
import numpy as np

# FUNCTIONS DEFINED IN THIS MODULE


def create_vector_levels(npatch):
    """
    Creates a vector containing the level for each patch. Nothing really important, just for ease

    Args:
        npatch: number of patches in each level, starting in l=0 (numpy vector of NLEVELS integers)

    Returns:
        numpy array containing the level for each patch

    """
    vector = [[0]] + [[i+1]*x for (i, x) in enumerate(npatch[1:])]
    vector = [item for sublist in vector for item in sublist]
    return np.array(vector)


def find_absolute_grid_position(ipatch, npatch, patchx, patchy, patchz, pare):
    """
    Given a patch in a certain iteration, finds the grid (natural) coordinates of its left corner.
    Written as a recursive function this time.

    Args:
        ipatch: number of the patch (in the given iteration)
        npatch: number of patches in each level, starting in l=0 (numpy vector of NLEVELS integers)
        patchx: vector containing the X-position of the leftmost corner of all the patches (numpy vector of integers)
        patchy: vector containing the Y-position of the leftmost corner of all the patches (numpy vector of integers)
        patchz: vector containing the Z-position of the leftmost corner of all the patches (numpy vector of integers)
        pare: vector containing the ipatch of each patch progenitor (numpy vector of integers)

    Returns:
        tuple with the patches left-corner NX, NY, NZ values

    """
    level = create_vector_levels(npatch)[ipatch]
    if ipatch < patchx.size:
        if level == 1:
            return patchx[ipatch], patchy[ipatch], patchz[ipatch]
        else:
            parevalues = find_absolute_grid_position(pare[ipatch], npatch, patchx, patchy, patchz, pare)
            return ((patchx[ipatch] - 1) / 2 ** (level - 1) + parevalues[0],
                    (patchy[ipatch] - 1) / 2 ** (level - 1) + parevalues[1],
                    (patchz[ipatch] - 1) / 2 ** (level - 1) + parevalues[2])
    else:
        raise ValueError('Provide a valid patchnumber (ipatch)')


def find_absolute_real_position(ipatch, side, nmax, npatch, patchx, patchy, patchz, pare):
    """
    Given a patch in a certain iteration, finds the real coordinates of its left corner with no numerical error.
    This function depends on find_absolute_grid_position, which must be also loaded.

    Args:
        ipatch: number of the patch (in the given iteration) (int)
        side: side of the simulation box in the chosen units (typically Mpc or kpc) (float)
        nmax: number of cells along each directions at level l=0 (can be loaded from masclet_parameters; NMAX = NMAY =
        = NMAZ is assumed) (int)
        npatch: number of patches in each level, starting in l=0 (numpy vector of NLEVELS integers)
        patchx: vector containing the X-position of the leftmost corner of all the patches (numpy vector of integers)
        patchy: vector containing the Y-position of the leftmost corner of all the patches (numpy vector of integers)
        patchz: vector containing the Z-position of the leftmost corner of all the patches (numpy vector of integers)
        pare: vector containing the ipatch of each patch progenitor (numpy vector of integers)

    Returns:
    numpy array with the patches left corner X, Y and Z values (assuming box centered in 0; same units than SIDE)

    """
    return (np.asarray(
        find_absolute_grid_position(ipatch, npatch, patchx, patchy, patchz, pare)) - nmax / 2 - 1) * side / nmax


def patch_vertices(level, nx, ny, nz, rx, ry, rz, size, nmax):
    """
    Returns, for a given patch, the comoving coordinates of its 8 vertices.

    Args:
        level: refinement level of the given patch
        nx, ny, nz: extension of the patch (in cells at level n)
        rx, ry, rz: comoving coordinates of the center of the leftmost cell of the patch
        size: comoving box side (preferred length units)
        nmax: cells at base level

    Returns:
        List containing 8 tuples, each one containing the x, y, z coordinates of the vertex.

    """

    cellsize = size/nmax/2**level

    leftmost_x = rx - cellsize / 2
    leftmost_y = ry - cellsize / 2
    leftmost_z = rz - cellsize / 2

    vertices = []

    for i in range(2):
        for j in range(2):
            for k in range(2):
                x = leftmost_x + i * nx * cellsize
                y = leftmost_y + j * ny * cellsize
                z = leftmost_z + k * nz * cellsize

                vertices.append((x,y,z))

    return vertices