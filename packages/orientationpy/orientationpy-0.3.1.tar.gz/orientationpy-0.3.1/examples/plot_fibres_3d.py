"""
Example 4: 3D example on real 3D fibres data
============================================

Here we present a 3D example, cropped out of https://zenodo.org/record/5483719#.Yyra4vFBy2A
"""

# sphinx_gallery_thumbnail_number = 3

import matplotlib
import matplotlib.pyplot as plt
import numpy
import orientationpy
import tifffile

##########################################
# Loading libraries and data
##########################################

# Load the greyscale image
# Data cropped from Salling, Hattel and Mikkelsen
#   X-ray computed tomography and scanning electron microscopy datasets of unidirectional and textured glass fibre composites
#   https://zenodo.org/record/5483719#.Yyra4vFBy2A
image = tifffile.imread("../data/3D/big-bin4.tif")
# print(f"The Z, Y and X dimensions of the image: {im.shape}")
# -- Show image
plt.imshow(image[image.shape[0] // 2], cmap="Greys_r")
plt.title("Original image, middle Z-slice")
plt.suptitle("Data from Salling, Hattel and Mikkelsen")
plt.show()


###########################################
# Compute structure tensor
###########################################
# -- Now we will now compute the Structure Tensor for each pixel https://en.wikipedia.org/wiki/Structure_tensor
# -- The result is a 2 x 2 matrix for each pixel, meaning that the resulting array is 2 x 2 x 240 x 350
# -- The main setting to provide here is "sigma", which selects the spatial scale in pixels that we're interested in. Here it is set to 2 pixels
print("Computing structure tensor...", end="")
structureTensor = orientationpy.computeGradientStructureTensor(image, sigma=1, mode="gaussian")
print("done.")


###############################################
# Compute invariants
################################################
intensity = orientationpy.computeIntensity(structureTensor)
directionality = orientationpy.computeStructureDirectionality(structureTensor)
structureType = orientationpy.computeStructureType(structureTensor)

###############################################
# Plot Intensity, Directionality
################################################
plt.figure(figsize=(10, 4))

# The intentsity represents how strong the orientation signal is
plt.subplot(1, 2, 1)
plt.imshow((intensity / intensity.max())[image.shape[0] // 2], vmin=0, vmax=1)
plt.colorbar()
plt.title("Intensity Normalised")

# The directionality measures how strongly aligned the image is locally
# directionality[numpy.isnan(directionality)] = 0
directionality[image == 0] = 0

plt.subplot(1, 2, 2)
plt.imshow(directionality[image.shape[0] // 2], norm=matplotlib.colors.LogNorm())
plt.title("Directionality")
plt.colorbar()
plt.tight_layout()
plt.show()

##########################################
# Computing Pixel-level orientations
##########################################
# We will now pass the structureTensor to the computeOrientation function, and get a dictionary back
print("Computing theta and phi...", end="")
orientations = orientationpy.computeOrientation(structureTensor, mode="fibre")
print("done.")


###############################################
# Plot Overlay of orientations on image
###############################################
fig, ax = plt.subplots()
imDisplayHSV = numpy.zeros((image.shape[0], image.shape[1], image.shape[2], 3), dtype="f4")

# Hue is the orientation (nice circular mapping)
imDisplayHSV[:, :, :, 0] = orientations["phi"] / 360
# Saturation is verticality, so white = up (z)
imDisplayHSV[:, :, :, 1] = numpy.sin(numpy.deg2rad(orientations["theta"]))
# Value is original image
imDisplayHSV[:, :, :, 2] = image / image.max()


fig.suptitle("Composition of image with 3D orientation")
ax.set_title("H = Azimuth, S = Polar Angle, V = image")
ax.imshow(matplotlib.colors.hsv_to_rgb(imDisplayHSV)[image.shape[0] // 2])

cmap = matplotlib.cm.hsv
norm = matplotlib.colors.Normalize(vmin=0, vmax=360)
fig.colorbar(
    matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap),
    ax=ax,
    orientation="vertical",
    label="azimuth angle (degrees in xy-plane from +x)",
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
boxSizePixels = 5
structureTensorBoxes = orientationpy.computeGradientStructureTensorBoxes(
    image,
    [boxSizePixels, boxSizePixels, boxSizePixels],
)

# The structure tensor in boxes is passed to the same function to compute
# The orientation
orientationsBoxes = orientationpy.computeOrientation(
    structureTensorBoxes,
    mode="fiber",
)

# We normalise the energy, to be able to hide arrows in the subsequent quiver plot
# energyBoxes /= energyBoxes.max()


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
# "directionality": directionality.ravel(),
# },
# )

boxCentresZ, boxCentresY, boxCentresX = numpy.mgrid[
    boxSizePixels // 2 : orientationsBoxes["theta"].shape[0] * boxSizePixels + boxSizePixels // 2 : boxSizePixels,
    boxSizePixels // 2 : orientationsBoxes["theta"].shape[1] * boxSizePixels + boxSizePixels // 2 : boxSizePixels,
    boxSizePixels // 2 : orientationsBoxes["theta"].shape[2] * boxSizePixels + boxSizePixels // 2 : boxSizePixels,
]

# Warning, matplotlib is XY convention, not YX!
ax = plt.figure().add_subplot(projection="3d")
ax.quiver(
    boxCentresX,
    boxCentresY,
    boxCentresZ,
    boxVectorsZYX[2],
    boxVectorsZYX[1],
    boxVectorsZYX[0],
    length=boxSizePixels,
    normalize=True,
    # scale=energyBoxes.ravel(),
    # color='r'
)
plt.show()


##########################################
# Stereoplot of orientations
##########################################
# This is a stereoplot of each box's orientation as viewed from the +Z axis
orientationVectors = boxVectorsZYX.reshape(3, -1).T
orientationpy.plotOrientations3d(orientationVectors, pointMarkerSize=1)

##########################################
# Spherical Histogram
##########################################
# This shows a histogram in 3D space, a homogeneous distribution of orientations would be a sphere
# We take every 10th one for speed
orientationpy.plotSphericalHistogram(orientationVectors[::10])

##########################################
# 3D orientation statistics
##########################################
print(orientationpy.fitVonMisesFisher(orientationVectors[::10]))
