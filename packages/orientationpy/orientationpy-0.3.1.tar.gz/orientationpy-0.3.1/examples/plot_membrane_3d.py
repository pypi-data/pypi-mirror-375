"""
Example 5: 3D example on synthetic single 3D membrane
=========================================================

Example of 3D "membrane" mode
"""

# sphinx_gallery_thumbnail_number = 2

import matplotlib.pyplot as plt
import numpy
import orientationpy
import tifffile

##########################################
# Loading libraries and data
##########################################

image = tifffile.imread("../data/3D/membrane.tif")
zSlice = 100

# Identify surface points...
surfZYX = numpy.array(numpy.where(image > 0.1)).T

ax = plt.figure().add_subplot(projection="3d")
# Matplotlib is not smart...
ax.set_box_aspect(aspect=(1, 1, 0.2))
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
# Here we split the image up into regular cubes of 5 pixels a side
# and average the structure tensor in each one.
# The result is then plotted in the centre of each box
boxSizePixels = 10
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
directionalityBoxes = orientationpy.computeStructureDirectionality(structureTensorBoxes)

# We normalise the intensity, to be able to hide arrows in the subsequent quiver plot
# intensityBoxes /= intentsityBoxes.max()


# Compute X and Y components of the vector
boxVectorsZYX = orientationpy.anglesToVectors(orientationsBoxes)

# import spam.helpers
# spam.helpers.writeGlyphsVTK(
# numpy.mgrid[
# boxSizePixels // 2 : thetaBoxes.shape[0] * boxSizePixels + boxSizePixels // 2 : boxSizePixels,
# boxSizePixels // 2 : thetaBoxes.shape[1] * boxSizePixels + boxSizePixels // 2 : boxSizePixels,
# boxSizePixels // 2 : thetaBoxes.shape[2] * boxSizePixels + boxSizePixels // 2 : boxSizePixels,
# ]
# .reshape(3, -1)
# .T,
# pointData={
# "n": boxVectorsZYX.reshape(3, -1).T,
# "intensity": intensityBoxes.ravel(),
# "directionality": directionalityBoxes.ravel(),
# },
# )

mask = directionalityBoxes > 0.00001

boxCentresZ, boxCentresY, boxCentresX = numpy.mgrid[
    boxSizePixels // 2 : orientationsBoxes["theta"].shape[0] * boxSizePixels + boxSizePixels // 2 : boxSizePixels,
    boxSizePixels // 2 : orientationsBoxes["theta"].shape[1] * boxSizePixels + boxSizePixels // 2 : boxSizePixels,
    boxSizePixels // 2 : orientationsBoxes["theta"].shape[2] * boxSizePixels + boxSizePixels // 2 : boxSizePixels,
]

# Warning, matplotlib is XY convention, not YX!
ax = plt.figure().add_subplot(projection="3d")
# Matplotlib is not smart...
ax.set_box_aspect(aspect=(1, 1, 0.2))
ax.quiver(
    boxCentresX[mask],
    boxCentresY[mask],
    boxCentresZ[mask],
    boxVectorsZYX[2][mask],
    boxVectorsZYX[1][mask],
    boxVectorsZYX[0][mask],
    length=boxSizePixels,
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
orientationVectors = boxVectorsZYX.reshape(3, -1).T
orientationpy.plotOrientations3d(orientationVectors, pointMarkerSize=1)
