"""Orientation analysis"""

import math
import multiprocessing
import warnings

import numba
import numba_progress
import numpy
import scipy.ndimage
from scipy.interpolate import CubicSpline
from tqdm import tqdm

gradientModes = ["finite_difference", "splines", "gaussian"]
orientationModes = ["fibre", "fiber", "membrane"]
symmetricComponents3d = numpy.array([[0, 0], [0, 1], [0, 2], [1, 1], [1, 2], [2, 2]])
symmetricComponents2d = numpy.array([[0, 0], [0, 1], [1, 1]])
nProcessesDefault = multiprocessing.cpu_count()


@numba.njit(cache=True)
def _unfoldMatrix(a):
    """
    Takes an array of length 3 or 6 and repacks it into a full symmetric matrix 2x2 or 3x3
    """
    if len(a) == 6:
        m = numpy.empty((3, 3), dtype="<f8")
        symmetricComponents = symmetricComponents3d
    elif len(a) == 3:
        m = numpy.empty((2, 2), dtype="<f8")
        symmetricComponents = symmetricComponents2d

    for n, [i, j] in enumerate(symmetricComponents):
        m[i, j] = a[n]
        # if not on diagonal fill in other side
        if i != j:
            m[j, i] = a[n]

    return m


def computeGradient(im, mode="gaussian", mask=None, anisotropy=numpy.ones(3)):
    """
    Returns the gradient of passed greylevel image.

    Parameters
    -----------
        im : array_like
            Input greyscale image, 2D or 3D

        mode : string, optional
            Selects method to compute gradients, can be either "splines", "gaussian" or "finite_difference".
            Default is "gaussian"

        anisotropy : array_like
            Relative pixel size for all axis. If your z-step is e.g. 2 times bigger than the pixel size in
            x and y, this parameter should be set to [2, 1, 1].

    Returns
    --------
        gradients : tuple of arrays
            2 or 3-component tuple of arrays (depending on 2D or 3D input)
            corresponding to (DZ) DY DX
    """
    # The sigma for the gaussian derivative, unlikely to change
    sigma = 1

    im = numpy.squeeze(im)

    twoD = im.ndim == 2

    if mode not in gradientModes:
        raise ValueError(f"{mode} not in allowable options: {gradientModes}")

    if not twoD:
        # Computing derivatives (scipy implementation truncates filter at 4 sigma).
        # 3D case
        if mode == "gaussian":
            Gx = scipy.ndimage.gaussian_filter(im, sigma, order=[0, 0, 1], mode="nearest", output=float)
            Gy = scipy.ndimage.gaussian_filter(im, sigma, order=[0, 1, 0], mode="nearest", output=float)
            Gz = scipy.ndimage.gaussian_filter(im, sigma, order=[1, 0, 0], mode="nearest", output=float)

        elif mode == "splines":
            cs_x = CubicSpline(numpy.linspace(0, im.shape[2] - 1, im.shape[2]), im, axis=2)
            Gx = cs_x(numpy.linspace(0, im.shape[2] - 1, im.shape[2]), 1)

            cs_y = CubicSpline(numpy.linspace(0, im.shape[1] - 1, im.shape[1]), im, axis=1)
            Gy = cs_y(numpy.linspace(0, im.shape[1] - 1, im.shape[1]), 1)

            cs_z = CubicSpline(numpy.linspace(0, im.shape[0] - 1, im.shape[0]), im, axis=0)
            Gz = cs_z(numpy.linspace(0, im.shape[0] - 1, im.shape[0]), 1)

        elif mode == "finite_difference":
            Gz, Gy, Gx = numpy.gradient(im)

        Gz = Gz / anisotropy[0]
        Gy = Gy / anisotropy[1]
        Gx = Gx / anisotropy[2]
        return (Gz, Gy, Gx)

    else:
        # 2D case
        if mode == "gaussian":
            Gx = scipy.ndimage.gaussian_filter(im, sigma, order=[0, 1], mode="nearest", output=float)
            Gy = scipy.ndimage.gaussian_filter(im, sigma, order=[1, 0], mode="nearest", output=float)

        elif mode == "splines":
            cs_x = CubicSpline(numpy.linspace(0, im.shape[1] - 1, im.shape[1]), im, axis=1)
            Gx = cs_x(numpy.linspace(0, im.shape[1] - 1, im.shape[1]), 1)

            cs_y = CubicSpline(numpy.linspace(0, im.shape[0] - 1, im.shape[0]), im, axis=0)
            Gy = cs_y(numpy.linspace(0, im.shape[0] - 1, im.shape[0]), 1)

        elif mode == "finite_difference":
            Gy, Gx = numpy.gradient(im)

        Gy = Gy / anisotropy[0]
        Gx = Gx / anisotropy[1]
        return (Gy, Gx)


def computeStructureTensor(gradients, sigma, mask=None):
    """
    Computes the structure tensor for every pixel of the image, averaging in a Gaussian window defined by sigma.
    Sigma is a very important parameter defining the spatial scale of interest.

    In 2D the structure tensor is a 2x2 matrix attached to each pixel and in 3D it is a 3x3 matrix, but since this tensor is symmetric
    this matrix is flattened to keep only to top-right half, and so in 2D that makes 3 components to store and
    in 3D that makes 6.
    We save in this flattened format to save memory, but also for pseudo-compatibility with skimage.feature.structure_tensor (they output a list rather than a big array)
    See https://en.wikipedia.org/wiki/Structure_tensor

    Parameters
    -----------
        gradients : tuple of array_like
            Tuple of gradient images from orientationpy.compute_gradient(im),
            This means in the 2D case a tuple of 2x2D arrays of gradients Y, X
            and in the 3D case a tuple of 3x3D arrays of Z, Y, X gradients

        sigma : float
            An integration scale giving the size over the neighbourhood in which the
            orientation is to be analysed.

        mask : boolean array, optional
            Array the same size as one of the gradients, indicating which pixels to include in the computation.

    Returns
    -------
        S : ndarray
            An array containing the computed structure tensor for each pixel.
            Output shape in 2D: 3 x Y x X
            Output shape in 2D: 6 x Z x Y x X
    """

    def multiplyAndFilter(gradients, i, j, sigma):
        return scipy.ndimage.gaussian_filter(numpy.multiply(gradients[i], gradients[j]), sigma, mode="nearest")

    if len(gradients) == 3:  # 3D
        symmetricComponents = symmetricComponents3d
    elif len(gradients) == 2:  # 2D
        symmetricComponents = symmetricComponents2d
    else:
        return None

    # Initializing structureTensor
    structureTensor = numpy.empty((len(symmetricComponents), *gradients[0].shape), dtype=float)

    # Integrating elements of structure tensor (scipy uses sequence of 1D).
    for n, [i, j] in enumerate(symmetricComponents):
        structureTensor[n] = multiplyAndFilter(gradients, i, j, sigma)

    return structureTensor


def computeGradientStructureTensor(im, sigma, mode="gaussian", anisotropy=numpy.ones(3)):
    """
    This function calls `computeGradient` with the mode and anisotropy factors passed in `mode` and `anisotropy_factors` respectively and then computes the structure tensor for each pixel (integrating in a Gaussian window of size `sigma`) with `computeStructureTensor` and returns that directly as a 3 x N x M or a 6 x N x M x O array.
    """
    # print("Computing gradients...", end="")
    g = computeGradient(im, mode=mode, anisotropy=anisotropy)
    # print("done")
    # print("Computing structure tensor...", end="")
    st = computeStructureTensor(g, sigma)
    # print("done")
    return st


def computeGradientStructureTensorBoxes(im, boxSize, mode="gaussian", anisotropy=numpy.ones(3)):
    """
    This function calls `computeGradient` with the mode and anisotropy factors passed in `mode` and `anisotropy_factors` respectively and then computes the structure tensor in touching 2/3D boxes with `computeStructureTensorBoxes` and returns the structure tensor for each box as a flattened 3 x N x M or a 6 x N x M x O array
    """
    # print("Computing gradients...", end="")
    g = computeGradient(im, mode=mode, anisotropy=anisotropy)
    # print("done")
    # print("Computing structure tensor...", end="")
    st = computeStructureTensorBoxes(g, boxSize)
    # print("done")
    return st


def computeStructureTensorBoxes(gradients, boxSize, mask=None, returnBoxCenters=False):
    """
    Computes the structure tensor in touching (no gaps and no overlaps) squares/cubes.
    This means first computing it per-pixel and then summing it in boxes.

    In 2D the structure tensor is a 2x2 matrix attached to each pixel and in 3D it is a 3x3 matrix, but since this tensor is symmetric
    this matrix is flattened to keep only to top-right half, and so in 2D that makes 3 components to store and
    in 3D that makes 6.
    We save in this flattened format to save memory, but also for pseudo-compatibility with skimage.feature.structure_tensor (they output a list rather than a big array)
    See https://en.wikipedia.org/wiki/Structure_tensor

    Parameters
    -----------
        gradients : tuple of array_like
            Tuple of gradient images from orientationpy.compute_gradient(im),
            This means in the 2D case a tuple of 2x2D arrays of gradients Y, X
            and in the 3D case a tuple of 3x3D arrays of Z, Y, X gradients

        boxSize : int or tuple
            If int, the box size in pixels in all directions.
            If tuple, should have have as many items as dimensions of the input image, and is the box size,
            in pixels in (Z), Y, X directions

        mask : boolean array, optional
            Array the same size as one of the gradients, indicating which pixels to include in the computation.

        returnBoxCenters : bool, optional
            Return the centers of the boxes?
            Optional, default = False

    Returns
    -------
        structureTensor : ndarray
            An array containing the computed structure tensor for each box.
            Output shape in 2D: 3 x Yboxes x Xboxes
            Output shape in 2D: 6 x Zboxes x Yboxes x Xboxes
    """
    if len(gradients) == 3:
        if type(boxSize) == list or type(boxSize) == tuple:
            if len(boxSize) != 3:
                print(f"computeStructureTensorBoxes(): Received 3D gradients but got len(boxSize) = {len(boxSize)}")
                return
            else:
                boxSizeZYX = boxSize
        else:
            boxSize = int(boxSize)
            boxSizeZYX = (boxSize, boxSize, boxSize)

        # Compute number of boxes, assuming top one at 0,0
        nBoxesZ = gradients[0].shape[0] // boxSizeZYX[0]
        nBoxesY = gradients[0].shape[1] // boxSizeZYX[1]
        nBoxesX = gradients[0].shape[2] // boxSizeZYX[2]

        # New empty variable to fill per-box
        structureTensorBoxes = numpy.empty((6, nBoxesZ, nBoxesY, nBoxesX))

        # Loop over boxes and integrate
        # for boxZ in tqdm(range(nBoxesZ)):
        for boxZ in range(nBoxesZ):
            for boxY in range(nBoxesY):
                for boxX in range(nBoxesX):
                    for n, [i, j] in enumerate(symmetricComponents3d):
                        # Compute i, j component of the structure tensor for all pixels in the box
                        structureTensorComponentPixelsInBox = numpy.multiply(
                            gradients[i][
                                boxZ * boxSizeZYX[0] : (boxZ + 1) * boxSizeZYX[0],
                                boxY * boxSizeZYX[1] : (boxY + 1) * boxSizeZYX[1],
                                boxX * boxSizeZYX[2] : (boxX + 1) * boxSizeZYX[2],
                            ],
                            gradients[j][
                                boxZ * boxSizeZYX[0] : (boxZ + 1) * boxSizeZYX[0],
                                boxY * boxSizeZYX[1] : (boxY + 1) * boxSizeZYX[1],
                                boxX * boxSizeZYX[2] : (boxX + 1) * boxSizeZYX[2],
                            ],
                        )

                        # Average it into the value for this box
                        structureTensorBoxes[n, boxZ, boxY, boxX] = numpy.mean(structureTensorComponentPixelsInBox)

        if returnBoxCenters:
            print("returnBoxCenters not yet implemented, just returning ST")
            return structureTensorBoxes
        else:
            return structureTensorBoxes

    elif len(gradients) == 2:
        # Check box sizes is either a two-element list or a single int
        if type(boxSize) == list or type(boxSize) == tuple:
            if len(boxSize) != 2:
                print(f"computeStructureTensorBoxes(): Received 2D gradients but got len(boxSize) = {len(boxSize)}")
                return
            else:
                boxSizeYX = boxSize
        else:
            boxSize = int(boxSize)
            boxSizeYX = (boxSize, boxSize)

        # Compute number of boxes, assuming top one at 0,0
        nBoxesY = gradients[0].shape[0] // boxSizeYX[0]
        nBoxesX = gradients[0].shape[1] // boxSizeYX[1]

        # New empty variable to fill per-box
        structureTensorBoxes = numpy.empty((3, nBoxesY, nBoxesX))

        # Loop over boxes and integrate
        for boxY in tqdm(range(nBoxesY)):
            for boxX in range(nBoxesX):
                for n, [i, j] in enumerate(symmetricComponents2d):
                    # Compute i, j component of the structure tensor for all pixels in the box
                    structureTensorComponentPixelsInBox = numpy.multiply(
                        gradients[i][
                            boxY * boxSizeYX[0] : (boxY + 1) * boxSizeYX[0],
                            boxX * boxSizeYX[1] : (boxX + 1) * boxSizeYX[1],
                        ],
                        gradients[j][
                            boxY * boxSizeYX[0] : (boxY + 1) * boxSizeYX[0],
                            boxX * boxSizeYX[1] : (boxX + 1) * boxSizeYX[1],
                        ],
                    )
                    # Average it!
                    structureTensorBoxes[n, boxY, boxX] = numpy.mean(structureTensorComponentPixelsInBox)

        if returnBoxCenters:
            print("returnBoxCenters not yet implemented, just returning ST")
            return structureTensorBoxes
        else:
            return structureTensorBoxes
    else:
        print(f"computeStructureTensorBoxes(): Unknown number of gradient dimensions: {len(gradients)}")


@numba.njit(cache=True)
def computeIntensity(structureTensor):
    """
    Computes the intesity of the gradients.
    This is the first principle invariant :math:`I_1` of the structure tensor.
    In OrientationJ this quantity is called energy.

    Parameters
    ----------
    structureTensor : tuple of numpy arrays
        The structure tensors as they are returned by
        :func:`orientationpy.main.computeStructureTensor`.

    Returns
    -------
    intentisy : numpy array
        The intensity of the gradients.
    """
    if len(structureTensor) == 6:
        # 3D
        I1 = structureTensor[0] + structureTensor[3] + structureTensor[5]
    else:
        # 2D
        I1 = structureTensor[0] + structureTensor[2]
    return I1


# @numba.njit(cache=True)
def computeStructureDirectionality(structureTensor):
    """
    Measure for how directed the structure tensor is.
    A point has no directionality but fibres and membranes do.
    This is the second main invariant :math:`J2`.

    For a mechanics interpretatin look at radial Lode coordinate.

    Parameters
    ----------
    structureTensor : tuple of numpy arrays
        The structure tensors as they are returned by
        :func:`orientationpy.main.computeStructureTensor`.

    Returns
    -------
    directionality : numpy array
        The directionality of the structure tensors.
        Zero means there is not directionality, e.g. for a point.
    """
    a = structureTensor
    if len(a) == 6:
        # 3D
        J2 = 1 / 6 * ((a[0] - a[3]) ** 2 + (a[3] - a[5]) ** 2 + (a[5] - a[0]) ** 2) + a[1] ** 2 + a[4] ** 2 + a[2] ** 2
    else:
        # 2D
        J2 = a[1] ** 2 - ((a[0] - a[2]) * (a[2] - a[0])) / 2
    return J2


@numba.njit(cache=True)
def _computeStructureType(a, I1, J2):
    """
    Numba function for computeStructureType.
    This is necessary because numba does not support
    optional arguments.
    """
    # Compute J3 as the determinant of the deviatroic tensor
    J3 = (a[0] - I1 / 3) * (a[3] - I1 / 3) * (a[5] - I1 / 3) + 2 * a[1] * a[2] * a[4] - a[2] ** 2 * (a[3] - I1 / 3) - a[1] ** 2 * (a[5] - I1 / 3) - a[4] ** 2 * (a[0] - I1 / 3)

    sin_theta_s = (J3 / 2) * (3 / J2) ** (3 / 2)

    return sin_theta_s


def computeStructureType(structureTensor, intensity=None, directionality=None):
    r"""
    Returns a value between -1 an 1 for each structure tensor, where
    -1 corresponds to a perfect fibre and 1 corresponds to a perfect plane.
    It is based on the Lode angle :math:`\theta_s` from mechanics.
    The value returned is :math:`\sin(3 \theta_s)`.

    Parameters
    ----------
    structureTensor : tuple of numpy arrays
        The structure tensors as they are returned by
        :func:`orientationpy.main.computeStructureTensor`.
    intensity : optional, numpy array
        The intensity as returned by :func:`orientationpy.main.computeIntensity`.
        If it is not provided, this function will compute it.
    directionality : optional, numpy array
        The directionality as returned by :func:`orientationpy.main.computeStructureDirectionality`.
        If it is not provided, this function will compute it.

    Returns
    -------
    structureType : numpy array
        Array of value between -1 and 1, where -1 corresponds to a fibres
        and 1 corresponds to a membrane.
    """
    if len(structureTensor) != 6:
        raise RuntimeError("The structure type is only defined in 3D.")
    if intensity is None:
        intensity = computeIntensity(structureTensor)
    if directionality is None:
        directionality = computeStructureDirectionality(structureTensor)
    structureType = _computeStructureType(structureTensor, intensity, directionality)
    mask = numpy.isclose(directionality, 0)
    if numpy.sum(mask) > 0:
        warnings.warn(
            "Some of the structure tensors provided have very low directionality. Setting their structure type to zero.",
            RuntimeWarning,
        )
        structureType[mask] = 0
    return structureType


@numba.njit(cache=True)
def _eigen_2D(arr):
    """
    This is a helper function for _eigen.
    It computes the eigen values (lambdas) and eigen vectors
    for a 2x2 matrix.
    """
    lambdas = numpy.zeros(2, dtype="<f8")
    vectors = numpy.zeros((2, 2), dtype="<f8")

    a = arr[0, 0]
    b = arr[1, 1]
    c = arr[0, 1]

    trace = a + b
    D = a * b - c**2

    lambdas[0] = trace / 2 - numpy.sqrt(trace**2 / 4 - D)
    lambdas[1] = trace / 2 + numpy.sqrt(trace**2 / 4 - D)

    vectors[0, 0] = lambdas[0] - b
    vectors[1, 0] = c
    vectors[0, 1] = lambdas[1] - b
    vectors[1, 1] = c

    return lambdas, vectors


@numba.njit(cache=True)
def _eigen(arr):
    """
    Computes the eigen values (lambdas) and eigen vectors
    for a symmetric 3x3 matrix.
    It uses closed form solutions when possible and eventaully falls
    back to numpy's eigh if non-of the closed form solutions are
    appropriate.
    It is based on an example from Pyxu's plugins
    (https://github.com/pyxu-org/cookiecutter-pyxu/blob/main/%7B%7Bcookiecutter.plugin_name%7D%7D/src/%7B%7Bcookiecutter.module_name%7D%7D/math/__init__.py)
    which is based on wikipedia:
    https://en.wikipedia.org/wiki/Eigenvalue_algorithm
    """
    lambdas = numpy.zeros(3, dtype="<f8")
    vectors = numpy.zeros((3, 3), dtype="<f8")

    a = arr[0, 0]
    d = arr[0, 1]
    f = arr[0, 2]
    b = arr[1, 1]
    e = arr[1, 2]
    c = arr[2, 2]

    p1 = d**2 + f**2 + e**2
    # Check if the case is trivial, i.e. diagonal matrix
    if p1 == 0:
        # A is diagonal.
        lambdas[0] = a
        lambdas[1] = b
        lambdas[2] = c
        vectors[0, 0] = 1
        vectors[0, 1] = 0
        vectors[0, 2] = 0
        vectors[1, 0] = 0
        vectors[1, 1] = 1
        vectors[1, 2] = 0
        vectors[2, 0] = 0
        vectors[2, 1] = 0
        vectors[2, 2] = 1
    elif f == 0 and e == 0:
        # A is an upper block matrix
        lambdas[0] = c
        vectors[:, 0] = numpy.array([0, 0, 1])
        arr2d = numpy.array([[a, d], [d, b]])
        lambdas[1:], vectors[:-1, 1:] = _eigen_2D(arr2d)
    elif d == 0 and f == 0:
        # A is a lower block matrix
        lambdas[0] = a
        vectors[:, 0] = numpy.array([1, 0, 0])
        arr2d = numpy.array([[b, e], [e, c]])
        lambdas[1:], vectors[1:, 1:] = _eigen_2D(arr2d)
    elif d == 0 and e == 0:
        # A is a "cross" matrix. This is a special case of a block
        # matrix
        lambdas[0] = b
        vectors[:, 0] = numpy.array([0, 1, 0])
        arr2d = numpy.array([[a, f], [f, c]])
        lambdas[1:], vectors2D = _eigen_2D(arr2d)
        vectors[0, 1] = vectors2D[0, 0]
        vectors[2, 1] = vectors2D[1, 0]
        vectors[0, 2] = vectors2D[0, 1]
        vectors[2, 2] = vectors2D[1, 1]
    else:
        # This part is from https://en.wikipedia.org/wiki/Eigenvalue_algorithm
        q = (a + b + c) / 3  # trace(A) is the sum of all diagonal values
        p2 = (a - q) ** 2 + (b - q) ** 2 + (c - q) ** 2 + 2 * p1
        p = (p2 / 6) ** 0.5
        det_b = (a - q) * ((b - q) * (c - q) - e**2) - d * (d * (c - q) - e * f) + f * (d * e - (b - q) * f)
        r = det_b / (2 * p**3)

        # In exact arithmetic for a symmetric matrix -1 <= r <= 1
        # but computation error can leave it slightly lambdasside this range.
        if r <= -1:
            phi = numpy.pi / 3
        elif r >= 1:
            phi = 0
        else:
            phi = numpy.arccos(r) / 3

        # the eigenvalues satisfy lambdas[2] <= lambdas[1] <= lambdas[0]
        lambdas[0] = q + 2 * p * numpy.cos(phi + (2 * numpy.pi / 3))
        lambdas[2] = q + 2 * p * numpy.cos(phi)
        lambdas[1] = 3 * q - lambdas[0] - lambdas[2]  # since trace(A) = eig1 + eig2 + eig3

        # Compute the eigen vectors
        for i in range(3):
            if not numpy.isclose((f * (b - lambdas[i]) - d * e), 0):
                m = (d * (c - lambdas[i]) - e * f) / (f * (b - lambdas[i]) - d * e)
                vectors[0, i] = (lambdas[i] - c - e * m) / f
                vectors[1, i] = m
                vectors[2, i] = 1
            elif not numpy.isclose((e * (a - lambdas[i]) - d * f), 0):
                m = (f * (b - lambdas[i]) - d * e) / (e * (a - lambdas[i]) - d * f)
                vectors[0, i] = m
                vectors[1, i] = 1
                vectors[2, i] = (lambdas[i] - b - d * m) / e
            elif not numpy.isclose((d * (c - lambdas[i]) - f * e), 0):
                m = (e * (a - lambdas[i]) - f * d) / (d * (c - lambdas[i]) - f * e)
                vectors[0, i] = 1
                vectors[1, i] = (lambdas[i] - a - f * m) / d
                vectors[2, i] = m
            else:
                lambdas, vectors = numpy.linalg.eigh(arr)

    # Make unit vectors
    vectors[:, 0] /= numpy.linalg.norm(vectors[:, 0])
    vectors[:, 1] /= numpy.linalg.norm(vectors[:, 1])
    vectors[:, 2] /= numpy.linalg.norm(vectors[:, 2])

    # Sort by eigenvalues
    sort_indices = numpy.argsort(lambdas)
    lambdas = lambdas[sort_indices]
    vectors = vectors[:, sort_indices]

    return lambdas, vectors


@numba.njit(parallel=True, cache=True)
def orientationFunction(
    structureTensor,
    progressProxy,
    fibre=True,
):
    theta = numpy.zeros(structureTensor.shape[1:], dtype="<f8")
    phi = numpy.zeros(structureTensor.shape[1:], dtype="<f8")

    for z in numba.prange(0, structureTensor.shape[1]):
        for y in range(0, structureTensor.shape[2]):
            for x in range(0, structureTensor.shape[3]):
                g = _unfoldMatrix(structureTensor[:, z, y, x])
                w, v = _eigen(g)

                if not fibre:
                    m = numpy.argmax(w)
                else:  # (mode == "fibre")
                    m = numpy.argmin(w)

                selectedEigenVector = v[:, m]

                # Flip over -z
                if selectedEigenVector[0] < 0:
                    selectedEigenVector *= -1

                # polar angle
                theta[z, y, x] = numpy.rad2deg(math.acos(numpy.abs(selectedEigenVector[0])))
                # azimuthal angle
                phi[z, y, x] = numpy.rad2deg(math.atan2(selectedEigenVector[1], selectedEigenVector[2]))
                if phi[z, y, x] < 0:
                    phi[z, y, x] += 360
                elif phi[z, y, x] >= 360:
                    phi[z, y, x] -= 360

        progressProxy.update(1)
    return theta, phi


def computeOrientation(
    structureTensor,
    mode="fibre",
    nProcesses=nProcessesDefault,
):
    """
    Takes in a pre-computed field of Structure Tensors and returns orientations.

    Parameters
    -----------
        structureTensor : numpy array
            2D or 3D structureTensor array from computeStructureTensor() or computeStructureTensorBoxes()

        mode : string, optional
            What mode to use for orientations -- N.B., this is only relevant in 3D.
            Are you looking for a "fibre" (1D object) or "membrane" (2D object)?
            Default = "fibre"

    Returns
    --------
        A dictionary containing:
          - theta
          - phi (only for 3D data)
    """
    outputDict = {}

    if mode not in orientationModes:
        raise ValueError(f"orientation mode {mode} not in supported modes: {orientationModes}")

    if len(structureTensor.shape) == 4:
        # We're in 3D!
        assert structureTensor.shape[0] == 6

        with numba_progress.ProgressBar(total=structureTensor.shape[1]) as progress:
            theta, phi = orientationFunction(
                structureTensor,
                progress,
                fibre=not (mode == "membrane"),
            )

        outputDict["theta"] = theta
        outputDict["phi"] = phi

        return outputDict

    elif len(structureTensor.shape) == 3:
        # We're in 2D!
        assert structureTensor.shape[0] == 3

        if mode == "membrane":
            raise ValueError(f"membrane doesn't exist in 2D")

        outputDict["theta"] = numpy.rad2deg(
            1
            / 2
            * numpy.arctan2(
                structureTensor[1, :, :] + structureTensor[1, :, :],
                structureTensor[0, :, :] - structureTensor[2, :, :],
            )
        )

        return outputDict

    else:
        raise ValueError(f"structure tensor has unexpected shape {len(structureTensor)}, should be 3 for 2D and 4 for 3D")


def anglesToVectors(orientations):
    """
    Takes in angles in degrees and returns corresponding unit vectors in Z Y X.

    Parameters
    ----------
        orientations : dictionary
            Dictionary containing a numpy array of  'theta' in degrees in 2D,
            and also a numpy array of 'phi' if 3D.

    Returns
    -------
        unitVectors : 2 or 3 x N x M (x O)
            YX or ZYX unit vectors
    """
    if type(orientations) is not dict:
        raise TypeError(f"dictionary with 'theta' (and optionally 'phi') key needed, you passed a {type(orientations)}")

    if "phi" in orientations.keys():
        # print("orientationAngleToOrientationVector(): 3D!")
        theta = numpy.deg2rad(orientations["theta"])
        phi = numpy.deg2rad(orientations["phi"])
        coordsZYX = numpy.zeros(
            (
                3,
                theta.shape[0],
                theta.shape[1],
                theta.shape[2],
            )
        )
        coordsZYX[2, :, :] = numpy.sin(theta) * numpy.cos(phi)
        coordsZYX[1, :, :] = numpy.sin(theta) * numpy.sin(phi)
        coordsZYX[0, :, :] = numpy.cos(theta)

        return coordsZYX
    # if type(orientations) == numpy.array:
    elif "theta" in orientations.keys():
        # print("orientationAngleToOrientationVector(): 2D!")
        # 2D case
        coordsYX = numpy.zeros(
            (
                2,
                orientations["theta"].shape[0],
                orientations["theta"].shape[1],
            )
        )

        coordsYX[0] = -numpy.sin(numpy.deg2rad(orientations["theta"]))
        coordsYX[1] = numpy.cos(numpy.deg2rad(orientations["theta"]))

        return coordsYX

    else:
        raise KeyError("couldn't find 'theta' (and optionally 'phi') key in passed orientations")


def _decomposeStructureTensor(structureTensor):
    """
    Returns the structure tensor of input structure tensor.
    Note: this function only works for 3D and 2D image data

    Parameters
    -----------
        structure_tensor : Array of shape (2/3, 2/3, ...)
            The second moment matrix of the im that you want to calculate
            the orientation of.

    Returns
    -------
        eigenvalues : Array of shape (..., M)
            The eigenvalues, each repeated according to its multiplicity.
            The eigenvalues are not necessarily ordered. The resulting
            array will be of complex type, unless the imaginary part is
            zero in which case it will be cast to a real type. When `structure_tensor`
            is real the resulting eigenvalues will be real (0 imaginary
            part) or occur in conjugate pairs

        eigenvectors : (..., M, M) array
            The normalized (unit "length") eigenvectors, such that the
            column ``eigenvectors[:,i]`` is the eigenvector corresponding to the
            eigenvalue ``eigenvalues[i]``.

    Notes
    -----
        Built upon the numpy.linalg.eig function, for more information:
        https://github.com/numpy/numpy/blob/v1.23.0/numpy/linalg/linalg.py#L1182-L1328
    """

    # 2D
    if len(structureTensor.shape) == 3:
        assert structureTensor.shape[0] == 3
        # Initializing eigen images
        eigenvectors = numpy.zeros(shape=(2, 2, structureTensor.shape[1], structureTensor.shape[2]))
        eigenvalues = numpy.zeros(shape=(2, structureTensor.shape[1], structureTensor.shape[2]))
        for y in range(0, structureTensor.shape[1]):
            for x in range(0, structureTensor.shape[2]):
                eigenvalues[:, y, x], eigenvectors[:, :, y, x] = numpy.linalg.eig(_unfoldMatrix(structureTensor[:, y, x]))
    # else:
    # print(f"_decomposeStructureTensor(): Passed structure tensor has {len(structureTensor.shape)} dimensions, don't know what to do")

    return eigenvalues, eigenvectors
