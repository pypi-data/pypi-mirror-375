"""
Example 2: 2D test on "Chirp"
=========================================

Test on a reference pattern with equal orientation probabilities in all directions,
good way to check the best way to calculate gradients
"""

# sphinx_gallery_thumbnail_number = 2


import matplotlib.pyplot as plt

##########################################
# Loading libraries and data
##########################################
#
import numpy
import orientationpy
import tifffile

# Load the greyscale image
im = tifffile.imread("../data/2D/Chirp-512.tif")
print(f"The Y and X dimensions of the image: {im.shape}")
# Show image
plt.imshow(im, cmap="Greys_r")
plt.title("Original image")
plt.show()

##########################################
# Computing Image Gradients
##########################################
# With this "chirp" image, we expect a completely homogeneous distribution of angles, in the zone where they are measurable.
mask = tifffile.imread("../data/2D/Chirp-512-mask.tif") > 0

plt.figure(figsize=(10, 10))

for n, mode in enumerate(["finite_difference", "gaussian", "splines"]):

    Gy, Gx = orientationpy.computeGradient(im, mode=mode)

    plt.subplot(4, 3, n + 1)
    plt.title(f"{mode}-Gy")
    plt.imshow(Gy, cmap="coolwarm", vmin=-64, vmax=64)

    plt.subplot(4, 3, 3 + n + 1)
    plt.title(f"{mode}-Gx")
    plt.imshow(Gx, cmap="coolwarm", vmin=-64, vmax=64)

    structureTensor = orientationpy.computeStructureTensor([Gy, Gx], sigma=2)

    orientations = orientationpy.computeOrientation(
        structureTensor,
        mode="fiber",
    )["theta"]

    plt.subplot(4, 3, 6 + n + 1)
    plt.title(f"Angular distribution\n({mode})")
    orientations[~mask] = 0
    plt.imshow(orientations, cmap="hsv", vmin=-90, vmax=90)

    plt.subplot(4, 3, 9 + n + 1)
    plt.title(f"Angular histogram\n({mode})")
    plt.hist(
        orientations[mask],
        range=[-90, 90],
        bins=90,
    )

plt.tight_layout()
plt.show()

##########################################
# Compatibility with skimage
##########################################
try:
    import skimage.feature

    structureTensorSK = numpy.array(skimage.feature.structure_tensor(im, sigma=2, order="rc"))
    orientations = orientationpy.computeOrientation(
        structureTensor,
        mode="fiber",
    )["theta"]

    plt.title(f"Angular histogram for skimage")
    plt.hist(
        orientations[mask],
        range=[-90, 90],
        bins=90,
    )
    plt.show()

except:
    print("Didn't manage to make skimage example")

###########################################
## Computing Pixel-level orientations
###########################################
## in 2D this can come directly from the structure tensor
# orientations[~mask] = 0

# fig, ax = plt.subplots()
## Alternative composition, start as HSV
# ax.imshow(im, cmap="Greys_r", vmin=0)
# ax.imshow(orientations, cmap="hsv", vmin=-90, vmax=90)

# cmap = matplotlib.cm.hsv
# norm = matplotlib.colors.Normalize(vmin=-90, vmax=90)
# fig.colorbar(matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, orientation="vertical", label="degrees from horzontal")

# plt.show()
