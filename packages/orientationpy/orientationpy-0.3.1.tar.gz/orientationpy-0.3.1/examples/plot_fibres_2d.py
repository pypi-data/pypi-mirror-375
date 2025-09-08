"""
Example 1: full 2D example on real fibres data
===============================================

Start here: we present a real 2D example in detail, directly taking the data from the OrientationJ homepage: http://bigwww.epfl.ch/demo/orientation/
"""

# sphinx_gallery_thumbnail_number = 4


##########################################
# Loading libraries and data
##########################################

import matplotlib
import matplotlib.colors
import matplotlib.pyplot as plt
import numpy
import orientationpy
import tifffile

# Load the greyscale image
image = tifffile.imread("../data/2D/image1_from_OrientationJ.tif")
print(f"The Y and X dimensions of the image: {image.shape}")
# Show image
plt.imshow(image, cmap="Greys_r")
plt.suptitle("Original image")
plt.title("Courtesy of Carole Aemisegger, ZMB, University of Zürich")
plt.show()

##########################################
# Computing Image Gradients
##########################################
# This is one of the most key steps in the measurement of 2D orientations, the measurement of the local gradient for each pixel.
# For a 2D image, the result of this computation is two new images: the gradient in X and the gradient in Y.
# We have implemented several methods in our function, we believe that the gaussian method is the best for most cases.

for n, mode in enumerate(["finite_difference", "gaussian", "splines"]):
    Gy, Gx = orientationpy.computeGradient(image, mode=mode)
    plt.subplot(2, 3, n + 1)
    plt.title(f"{mode}-Gy")
    plt.imshow(Gy, cmap="coolwarm", vmin=-64, vmax=64)

    plt.subplot(2, 3, 3 + n + 1)
    plt.title(f"{mode}-Gx")
    plt.imshow(Gx, cmap="coolwarm", vmin=-64, vmax=64)
plt.show()

# In the loop we've overwriting Gy and Gx, so at this point in the code they are the last (spines) gradients

###########################################
# Compute structure tensor
###########################################
# Now we will now compute the Structure Tensor for each pixel https://en.wikipedia.org/wiki/Structure_tensor
#
# The result is in principle a 2 x 2 symmetric matrix for each pixel.
# We save only to top right side of the matrix meaning that the resulting array is 3 x 240 x 350
# The main setting to provide here is "sigma", which selects the spatial scale in pixels that we're interested in. Here it is set to 2 pixels
structureTensor = orientationpy.computeStructureTensor([Gy, Gx], sigma=2)


##########################################
# Computing Invariants
##########################################
# The first invariant of the structure tensor is a measure for the local stength of the gradients.
# The second invariant is called directionality and measures how directed the structure tensors are.
intensity = orientationpy.computeIntensity(structureTensor)
directionality = orientationpy.computeStructureDirectionality(structureTensor)

# directionality = np.log(directionality)
#
# print(directionality.flatten().max())
# print(directionality.flatten().min())
# print(numpy.sort(directionality.flatten())[-10:])
# thresh_low = numpy.quantile(directionality.flatten(), 0.02)
# print("thresh_low", thresh_low)
# thresh_high = numpy.quantile(directionality.flatten(), 0.98)
# print("thresh_high", thresh_high)
#
# plt.imshow(image, cmap="Greys_r", vmin=0)
# plt.imshow(directionality < thresh_low, cmap="Reds", alpha=0.5)
# plt.show()
# plt.imshow(image, cmap="Greys_r", vmin=0)
# plt.imshow(directionality > thresh_high, cmap="Reds", alpha=0.5)
# plt.show()
# exit()
#
# plt.figure()
# plt.hist(directionality.flatten(), bins=20)
# plt.show()
# exit()

###############################################
# Plot Intensities and Directionalities
###############################################
plt.figure(figsize=(10, 4))

# The intensity represents how strong the orientation signal is
plt.subplot(1, 2, 1)
plt.imshow(intensity / intensity.max(), vmin=0, vmax=1)
plt.colorbar(shrink=0.7)
plt.title("Intensity Normalised")


plt.subplot(1, 2, 2)
# plt.imshow(directionality / directionality.max(), vmin=0, vmax=1)
plt.imshow(directionality, norm=matplotlib.colors.LogNorm(vmin=10, vmax=1e8))
plt.title("Directionaltiy Normalised")
plt.colorbar(shrink=0.7)
plt.tight_layout()
plt.show()

##########################################
# Computing Pixel-level orientations
##########################################
# We will now pass the structureTensor to the computeOrientation function
# that will give us an angle in degrees from [90, -90] for each pixel.
orientations = orientationpy.computeOrientation(structureTensor)

###############################################
# Plot Overlay of orientations on image
###############################################
# Overlay type 1 -- requires matlplotlib >= 3.1.3

vmin, vmax = 10, 1e8
normalized_directionality = numpy.clip(directionality, vmin, vmax)
normalized_directionality = numpy.log(normalized_directionality)
normalized_directionality -= normalized_directionality.min()
normalized_directionality /= normalized_directionality.max()
normalized_directionality[image == 0] = 0

try:
    plt.suptitle("Overlay with orientation")
    plt.title("Greyscale image with HSV orientations overlaid\nwith transparency as log directionality")
    plt.imshow(image, cmap="Greys_r", vmin=0)
    plt.imshow(
        orientations["theta"],
        cmap="hsv",
        alpha=normalized_directionality * 0.5,
        vmin=-90,
        vmax=90,
    )

    plt.colorbar(shrink=0.7)
    plt.show()
except:
    print("Didn't manage to make the plot :(")

###############################################
# Plot HSV composition
###############################################
# Alternative composition, with Hue, Saturation and Value
imDisplayHSV = numpy.zeros((image.shape[0], image.shape[1], 3), dtype="f4")
# Hue is the orientation (nice circular mapping)
imDisplayHSV[:, :, 0] = (orientations["theta"] + 90) / 180
# Saturation is directionality
imDisplayHSV[:, :, 1] = normalized_directionality
# Value is original image ;)
imDisplayHSV[:, :, 2] = image / image.max()

fig, ax = plt.subplots()
fig.suptitle("Image-orientation composition")
ax.set_title("Hue = Orientation\nSaturation = log(Directionality)\nV = image greylevels")
ax.imshow(matplotlib.colors.hsv_to_rgb(imDisplayHSV))

cmap = matplotlib.cm.hsv
norm = matplotlib.colors.Normalize(vmin=-90, vmax=90)
fig.colorbar(
    matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap),
    ax=ax,
    orientation="vertical",
    label="degrees from horizontal",
    shrink=0.7,
)

plt.show()


##########################################
# Computing boxed orientations
##########################################
# Starting again from the gradients, the Structure Tensor can also be computed
# in boxes.
# Here we split the image up into regular boxes of 7 pixels a side
# and average the structure tensor in each one.
# The result is then plotted in the centre of each box
boxSizePixels = 7
structureTensorBoxes = orientationpy.computeStructureTensorBoxes(
    [Gy, Gx],
    [boxSizePixels, boxSizePixels],
)
intensityBoxes = orientationpy.computeIntensity(structureTensorBoxes)

# The structure tensor in boxes is passed to the same function to compute
# The orientation
orientationsBoxes = orientationpy.computeOrientation(
    structureTensorBoxes,
    mode="fiber",
)

# We normalise the intensity, to be able to hide arrows in the subsequent quiver plot
intensityBoxes /= intensityBoxes.max()

# Compute box centres
boxCentresY = numpy.arange(orientationsBoxes["theta"].shape[0]) * boxSizePixels + boxSizePixels // 2
boxCentresX = numpy.arange(orientationsBoxes["theta"].shape[1]) * boxSizePixels + boxSizePixels // 2

# Compute X and Y components of the vector
boxVectorsYX = orientationpy.anglesToVectors(orientationsBoxes)

# Vectors with low intensity reset
boxVectorsYX[:, intensityBoxes < 0.05] = 0.0

plt.title("Local orientation vector in boxes")
plt.imshow(image, cmap="Greys_r", vmin=0)

# Warning, matplotlib is XY convention, not YX!
plt.quiver(
    boxCentresX,
    boxCentresY,
    boxVectorsYX[1],
    boxVectorsYX[0],
    angles="xy",
    scale_units="xy",
    # scale=intensityBoxes.ravel(),
    color="r",
    headwidth=0,
    headlength=0,
    headaxislength=1,
)
plt.show()
