"""
Synthetic data generation for the testing of orientatiopy

Use generate_synthetic_data() to do just that!
"""

import numpy
import scipy.ndimage


def generate_synth_fiber_structure(shape, spacing):
    """
    This function generates a synthetic fiber-populated array
    based on a specifiec array shape and spacing between the simulated fibers.

    Parameters
    ----------
        shape : list
            Contains the dimensitons of the desired array.
        spacing : scalar (int)

    Returns
    -------
        fib_struct : ndarray
            Synthetic fiber structures

    """
    # Initializing the synthetic volume with zeros
    fib_struct = numpy.zeros(shape, dtype=numpy.float32)
    print(f"shape of synth array: {shape}")

    # Selectively filling the volume with ones to generate structure

    # 2D Case
    if len(shape) == 2:
        for i in range(1, shape[0], spacing):
            fib_struct[i, :] = 1

    elif len(shape) == 3:
        # 3D Case
        for y in range(1, shape[1], spacing):
            for x in range(1, shape[2], spacing):
                fib_struct[:, y : y + 2, x : x + 2] = 1
                # fib_struct[:, i, j] = 1

    return fib_struct


def rotate_synth_fiber_structure(array, rotation_transform, interpolationOrder=3):
    """
    This function rotates a synthetic fiber-populated array
    by the specified number of degrees.

    Parameters
    ----------
        array : ndarray (float64)
            Array to be rotated.

        deg : list
            3 element-list specifying the rotation (in degrees)
            along the Z, Y and X axes respectively.

    Returns
    -------
        rot_fib_struct : ndarray
            Synthetic fiber structures (rotated)
            Dimensionality is conserved with regards to the
            input array.

    """

    if len(array.shape) == 2:
        array = array[numpy.newaxis, ...]
    # elif (len(array.shape) == 3):
    # pass

    # Center of transformation
    centre = (numpy.array(array.shape) - 1) / 2.0

    # Initializing the rotated volume with zeros
    rot_fib_struct = numpy.zeros_like(array, dtype="<f4")

    # Getting the rotation angles from list
    rotationAngleDeg = numpy.linalg.norm(rotation_transform)

    # print(f"rotationAngleDeg = {rotationAngleDeg}")

    # If statement to evade dividing by 0
    if rotationAngleDeg == 0:
        rotationAxis = numpy.divide(rotation_transform, 0.0000000001)

    else:
        rotationAxis = numpy.divide(rotation_transform, rotationAngleDeg)

    # print(f"rotationAxis: {rotationAxis}")

    # io.imsave("../testdata/array_newshape.tif",array)

    # positive angle is clockwise
    K = numpy.array([[0, -rotationAxis[2], rotationAxis[1]], [rotationAxis[2], 0, -rotationAxis[0]], [-rotationAxis[1], rotationAxis[0], 0]])

    R = numpy.eye(3) + (numpy.sin(numpy.deg2rad(rotationAngleDeg)) * K) + ((1.0 - numpy.cos(numpy.deg2rad(rotationAngleDeg))) * numpy.dot(K, K))

    R = numpy.linalg.inv(R)

    coordinatesInitial = numpy.ones((3, array.shape[0] * array.shape[1] * array.shape[2]), dtype="<f4")

    coordinates_mgrid = numpy.mgrid[0 : array.shape[0], 0 : array.shape[1], 0 : array.shape[2]]

    # Copy into coordinatesInitial
    coordinatesInitial[0, :] = coordinates_mgrid[0].ravel() - centre[0]
    coordinatesInitial[1, :] = coordinates_mgrid[1].ravel() - centre[1]
    coordinatesInitial[2, :] = coordinates_mgrid[2].ravel() - centre[2]

    # Apply R to coordinates
    coordinatesDef = numpy.dot(R, coordinatesInitial)

    coordinatesDef[0, :] += centre[0]
    coordinatesDef[1, :] += centre[1]
    coordinatesDef[2, :] += centre[2]

    rot_fib_struct += scipy.ndimage.map_coordinates(array, coordinatesDef[0:3], order=interpolationOrder).reshape(rot_fib_struct.shape).astype("<f4")

    # assert coordinatesDef[0:3].any() != False, "rot_fib_struct is empty"

    return rot_fib_struct


def generate_synthetic_data(dim, deg, smooth=0, spacing=5, crop=0):
    """
    Alter this function to generate synthetic data.
    You can control the dimensinoality of the generated data with "dim"
    and the rotation with "deg"
    """

    # Generating synthetic fiber structure array
    fs = generate_synth_fiber_structure(dim, spacing=spacing)

    # Rotating fiber structure array along the [Z-axis, Y-axis, X-axis] in degrees
    if len(dim) == 3:
        r_fs = rotate_synth_fiber_structure(fs, deg)
    else:
        r_fs = rotate_synth_fiber_structure(fs, [deg, 0, 0])[0]
    # io.imsave(f"../testdata/rot_z_{deg[0]}_y_{deg[1]}_x_{deg[2]}_deg.tif", r_fs)

    if smooth > 0:
        r_fs = scipy.ndimage.gaussian_filter(r_fs, smooth)

    if crop == 0:
        return r_fs
    elif len(dim) == 3:
        return r_fs[crop:-crop, crop:-crop, crop:-crop]
    else:
        return r_fs[crop:-crop, crop:-crop]
