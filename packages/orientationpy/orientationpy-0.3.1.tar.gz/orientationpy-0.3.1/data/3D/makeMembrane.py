import matplotlib.pyplot as plt
import numpy
import scipy.interpolate
import skimage.morphology
import tifffile
from tqdm import tqdm

nSplinePoints = 200


def skeletonEndpoints(skel):
    # skel[skel!=0] = 1
    skel = numpy.uint8(skel > 0)

    # Apply the convolution.
    kernel = numpy.uint8([[1, 1, 1], [1, 10, 1], [1, 1, 1]])
    src_depth = -1
    filtered = scipy.ndimage.convolve(skel, kernel)

    # Look through to find the value of 11.
    # This returns a mask of the endpoints, but if you
    # just want the coordinates, you could simply
    # return np.where(filtered==11)
    out = numpy.zeros_like(skel)
    out[numpy.where(filtered == 11)] = 1
    endCoords = numpy.where(filtered == 11)
    endCoords = list(zip(*endCoords))
    startPoint = endCoords[0]
    endPoint = endCoords[1]

    # print(f"Skel starts at {startPoint} and finishes at {endPoint}")

    return startPoint, endPoint


def skelPointsInOrder(skel, startPoint=None):
    """
    put in a skel image, get the y, x points out in order
    """

    # Lazy!!
    if startPoint is None:
        startPoint, _ = skeletonEndpoints(skel)

    # get the coordinates of all points in the skeleton
    skelXY = numpy.array(numpy.where(skel))
    skelPoints = list(zip(skelXY[0], skelXY[1]))
    skelLength = len(skelPoints)

    # Loop through the skeleton starting with startPoint, deleting the starting point from the skelPoints list, and finding the closest pixel. This is appended to orderedPoints. startPoint now becomes the last point to be appended.
    startPointCopy = startPoint  # copied as we are going to loop and overwrite, but want to also keep the original startPoint
    orderedPoints = []

    while len(skelPoints) > 1:

        skelPoints.remove(startPointCopy)

        # Calculate the point that is closest to the start point
        diffs = numpy.abs(numpy.array(skelPoints) - numpy.array(startPointCopy))
        dists = numpy.sum(diffs, axis=1)  # l1-distance
        closest_point_index = numpy.argmin(dists)
        closestPoint = skelPoints[closest_point_index]
        orderedPoints.append(closestPoint)

        startPointCopy = closestPoint

    orderedPoints = numpy.array(orderedPoints)

    # YX points
    return orderedPoints


def skelSpliner(skel, smoothing=20, order=3, decimation=3):
    # view = skelPath.split("/")[2]

    # NOTE: the coordinate seem to come out with y first, then x
    startPoint, endPoint = skeletonEndpoints(skel)

    # Impose an order to points
    orderedPoints = skelPointsInOrder(skel, startPoint)

    # unzip ordered points to extract x and y arrays
    x = orderedPoints[:, 1].ravel()
    y = orderedPoints[:, 0].ravel()

    x = x[::decimation]
    y = y[::decimation]

    # EA: What does this do???
    x = x[0:-1]
    y = y[0:-1]

    # interpolate based on ordered x and y values from skeleton
    # smoothingFactor = 3
    # order = 4

    tcko, uo = scipy.interpolate.splprep([x, y], s=smoothing, k=order, per=False)

    # apply spline to the skel
    # xo, yo = interpolate.splev(numpy.linspace(0,1,len(orderedPoints)), tcko)

    return tcko


vol = numpy.zeros([150, 150, 150], dtype=float)

A = tifffile.imread("membrane-A.tif") > 0
B = tifffile.imread("membrane-B.tif") > 0
B[:, 0] = 0
B[:, -1] = 0

Askel = skimage.morphology.skeletonize(A)
Bskel = skimage.morphology.skeletonize(B)

Aspline = skelSpliner(Askel)
Bspline = skelSpliner(Bskel)

AsplinePointsXY = numpy.array(scipy.interpolate.splev(numpy.linspace(0, 1, nSplinePoints), Aspline)).T
# print(AsplinePoints)
BsplinePointsXY = numpy.array(scipy.interpolate.splev(numpy.linspace(0, 1, nSplinePoints), Bspline)).T

# plt.plot(AsplinePointsXY[:,0], AsplinePointsXY[:,1], 'ro')
# plt.plot(BsplinePointsXY[:,0], BsplinePointsXY[:,1], 'go')
# plt.show()


# Let's imagine that A is extended in X and goes up and down in Z
# Let's imagine that B is extended in Y and goes up and down in Z
abPairs = numpy.mgrid[0:nSplinePoints, 0:nSplinePoints].reshape(2, -1).T

for (
    n,
    [a, b],
) in tqdm(enumerate(abPairs)):
    aXZ = numpy.array(scipy.interpolate.splev(a / nSplinePoints, Aspline))
    bYZ = numpy.array(scipy.interpolate.splev(b / nSplinePoints, Bspline))
    z = int(aXZ[1] + bYZ[1] / 2)
    y = int(bYZ[0])
    x = int(aXZ[0])
    vol[z, y, x] = 255

# Smooth
vol = scipy.ndimage.gaussian_filter(vol, 2)

# Scale to 8-bit
vol /= vol.max()

tifffile.imwrite("membrane.tif", (vol * 255).astype("<u1"))
