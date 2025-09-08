"""
Example 6: 3D example on a ball
===================================

Synthetic ball example also in "membrane" mode
"""

# sphinx_gallery_thumbnail_number = 3


import matplotlib.pyplot as plt

##########################################
# Loading libraries and data
##########################################
import numpy
import orientationpy

try:
    import spam.kalisphera

    image = spam.kalisphera.makeBlurryNoisySphere(
        [100, 100, 100],
        [50, 50, 50],
        40,
        blur=2,
    )

except:
    import scipy.ndimage

    coords = numpy.mgrid[0:100, 0:100, 0:100].reshape(3, -1).T
    image = (numpy.sum((coords - 49.5) ** 2, axis=1) ** 0.5).reshape(100, 100, 100) < 40
    image = scipy.ndimage.gaussian_filter(image, 2)

# Identify surface points...
surfZYX = numpy.array(numpy.where(image > 0.6)).T

ax = plt.figure().add_subplot(projection="3d")
# Matplotlib is not smart...
ax.plot(
    surfZYX[:, 2],
    surfZYX[:, 1],
    surfZYX[:, 0],
)
plt.show()


##########################################
# Computing boxed orientations
##########################################
# Starting again from the gradients, the Structure Tensor can also be computed
# in boxes.
# Here we split the image up into regular cubes of 3 pixels a side
# and average the structure tensor in each one.
# The result is then plotted in the centre of each box
boxSizePixels = 3
structureTensorBoxes = orientationpy.computeGradientStructureTensorBoxes(
    image,
    [boxSizePixels, boxSizePixels, boxSizePixels],
)

# The structure tensor in boxes is passed to the same function to compute
# The orientation
orientationsBoxes = orientationpy.computeOrientation(
    structureTensorBoxes,
    mode="membrane",
)
intensityBoxes = orientationpy.computeIntensity(structureTensorBoxes)


# Compute X and Y components of the vector
boxVectorsZYX = orientationpy.anglesToVectors(orientationsBoxes)

mask = intensityBoxes > 0.5 * intensityBoxes.max()

boxCentresZ, boxCentresY, boxCentresX = numpy.mgrid[
    boxSizePixels // 2 : orientationsBoxes["theta"].shape[0] * boxSizePixels + boxSizePixels // 2 : boxSizePixels,
    boxSizePixels // 2 : orientationsBoxes["theta"].shape[1] * boxSizePixels + boxSizePixels // 2 : boxSizePixels,
    boxSizePixels // 2 : orientationsBoxes["theta"].shape[2] * boxSizePixels + boxSizePixels // 2 : boxSizePixels,
]

# Warning, matplotlib is XY convention, not YX!
ax = plt.figure().add_subplot(projection="3d")
# Matplotlib is not smart...
ax.quiver(
    boxCentresX[mask],
    boxCentresY[mask],
    boxCentresZ[mask],
    boxVectorsZYX[2][mask],
    boxVectorsZYX[1][mask],
    boxVectorsZYX[0][mask],
    length=boxSizePixels * 3,
    normalize=True,
    # angles='xy',
    # scale_units='xy'
    # scale=intensityBoxes.ravel(),
    # color='r'
)
plt.show()


##########################################
# Stereoplot of orientations
##########################################
# This is a stereoplot of each box's orientation as viewed from the +Z axis
orientationVectors = boxVectorsZYX[:, mask].reshape(3, -1).T
orientationpy.plotOrientations3d(orientationVectors, pointMarkerSize=1)

##########################################
# Spherical Histogram
##########################################
# This shows a histogram in 3D space, a homogeneous distribution of orientations would be a sphere... and so it should be now!
orientationpy.plotSphericalHistogram(orientationVectors)
