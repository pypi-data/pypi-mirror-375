import numpy
import scipy.ndimage
import scipy.signal


def generateFibres3D(dim: int, rotationVector=[0, 0, 0], crop=25, nPoints=None, sigma=0.4, radius=1.2, debug=False):
    if debug:
        import matplotlib.pyplot as plt
        import tifffile

    if nPoints is None:
        # Rough stab at something that looks good
        nPoints = int(dim * dim / 1.5 / radius)

    dim = dim + 2 * crop
    # dim = 150
    # crop = 25
    f = 8  # Scale-up factor for making template

    if debug:
        print("making points...", end="")
    points = numpy.random.randint(0, high=dim - 1, size=[nPoints, 2])

    im2d = numpy.zeros([dim, dim])

    X, Y = numpy.mgrid[-radius * 2 * f : radius * 2 * f, -radius * 2 * f : radius * 2 * f]
    R = ((X**2 + Y**2) ** 0.5 < radius * f).astype(float)
    R = scipy.ndimage.gaussian_filter(R, sigma * f)
    template = scipy.ndimage.zoom(R, 1 / f, order=3)
    # if debug:
    # plt.imshow(template)
    # plt.show()

    for point in points:
        im2d[point[0], point[1]] = 1.0
    if debug:
        print("done")

    if debug:
        print("convolving...", end="")
    imDots = scipy.signal.fftconvolve(im2d, template, mode="same")
    # imDots = scipy.signal.convolve2d(im2d, template, mode='same')
    if debug:
        print("done")

    im3d = numpy.zeros([dim, dim, dim], dtype="<f4")
    for z in range(dim):
        im3d[z] = imDots

    # if debug: tifffile.imwrite("imFib.tif", im3d[crop:-crop, crop:-crop, crop:-crop])

    def rotateImage(im, rotationVector, interpolationOrder=3):
        """
        This function rotates a 3D image

        Parameters
        ----------

            im : ndarray (float64)
                Array to be rotated.

            rotationVector : list
                rotation vector in degrees

        Returns
        -------
            rot_fib_struct : ndarray
                Synthetic fiber structures (rotated)
                Dimensionality is conserved with regards to the
                input array.

        """

        if len(im.shape) == 2:
            im = im[numpy.newaxis, ...]
        # elif (len(im.shape) == 3):
        # pass

        # Center of transformation
        centre = (numpy.array(im.shape) - 1) / 2.0

        # Initializing the rotated volume with zeros
        # imRot = numpy.zeros_like(im, dtype="<f4")

        # Getting the rotation angles from list
        rotationAngleDeg = numpy.linalg.norm(rotationVector)

        # print(f"rotationAngleDeg = {rotationAngleDeg}")

        # If statement to evade dividing by 0
        if rotationAngleDeg == 0:
            return im

        else:
            rotationAxis = numpy.divide(rotationVector, rotationAngleDeg)

        # positive angle is clockwise
        K = numpy.array([[0, -rotationAxis[2], rotationAxis[1]], [rotationAxis[2], 0, -rotationAxis[0]], [-rotationAxis[1], rotationAxis[0], 0]])

        R = numpy.eye(3) + (numpy.sin(numpy.deg2rad(rotationAngleDeg)) * K) + ((1.0 - numpy.cos(numpy.deg2rad(rotationAngleDeg))) * numpy.dot(K, K))

        R = numpy.linalg.inv(R)

        coordinatesInitial = numpy.ones((3, im.shape[0] * im.shape[1] * im.shape[2]), dtype="<f4")

        coordinates_mgrid = numpy.mgrid[0 : im.shape[0], 0 : im.shape[1], 0 : im.shape[2]]

        # Copy into coordinatesInitial
        coordinatesInitial[0, :] = coordinates_mgrid[0].ravel() - centre[0]
        coordinatesInitial[1, :] = coordinates_mgrid[1].ravel() - centre[1]
        coordinatesInitial[2, :] = coordinates_mgrid[2].ravel() - centre[2]

        # Apply R to coordinates
        coordinatesDef = numpy.dot(R, coordinatesInitial)

        coordinatesDef[0, :] += centre[0]
        coordinatesDef[1, :] += centre[1]
        coordinatesDef[2, :] += centre[2]

        imRot = scipy.ndimage.map_coordinates(im, coordinatesDef[0:3], order=interpolationOrder).reshape(im.shape).astype("<f4")

        return imRot

    if debug:
        print("rotating...", end="")
    im3dRot = rotateImage(im3d, rotationVector)
    if debug:
        print("done")

    if debug:
        tifffile.imwrite("imFibRot.tif", im3dRot[crop:-crop, crop:-crop, crop:-crop])
    return im3dRot[crop:-crop, crop:-crop, crop:-crop]


if __name__ == "__main__":
    generateFibres3D(50, rotationVector=numpy.random.rand(3) * 90, debug=True)
