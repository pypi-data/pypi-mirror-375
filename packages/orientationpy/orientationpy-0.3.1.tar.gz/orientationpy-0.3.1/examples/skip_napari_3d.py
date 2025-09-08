"""
3D fibres visualisation with napari
=========================================================

Using synthetic scattered 3D fibres
"""

import matplotlib.colors
import matplotlib.pyplot as plt
import numpy

# sphinx_gallery_thumbnail_number = 1
import orientationpy as opy

###############################################################
# Loading libraries and data
###############################################################

try:
    import napari
    from napari.experimental import link_layers
except:
    raise ImportError("It looks like you do not have Napari installed.")

import tifffile

image = tifffile.imread("../data/3D/skeleton.tif")

# Compute orientations
###############################################################
gradients = opy.computeGradient(image)
structureTensor = opy.computeStructureTensor(gradients, sigma=2.0)
orientations = opy.computeOrientation(structureTensor)

theta = orientations.get("theta")
phi = orientations.get("phi")


# Synthesize colour image
###############################################################
rx, ry, rz = image.shape
imDisplayHSV = numpy.zeros((rx, ry, rz, 3), dtype="f4")
imDisplayHSV[..., 0] = phi / 360
imDisplayHSV[..., 1] = numpy.sin(numpy.deg2rad(theta))
imDisplayHSV[..., 2] = image / image.max()

imDisplayRGB = matplotlib.colors.hsv_to_rgb(imDisplayHSV)

red, green, blue = numpy.rollaxis(imDisplayRGB, axis=-1)

# Push image to napari for 3D rendering and screenshot it
###############################################################
viewer = napari.Viewer()
red_channel_layer = viewer.add_image(red, blending="additive", colormap="red")
green_channel_layer = viewer.add_image(green, blending="additive", colormap="green")
blue_channel_layer = viewer.add_image(blue, blending="additive", colormap="blue")
link_layers([red_channel_layer, green_channel_layer, blue_channel_layer])
viewer.camera.angles = (0, 15, 35)


sc = viewer.screenshot(canvas_only=True, flash=False)
fig, ax = plt.subplots(figsize=(7, 7))
ax.imshow(sc)
ax.axis("off")
plt.tight_layout()
plt.show()

# Interactive napari plot?
###############################################################

# Uncomment below if you want an interactive 3D plot to look at
# napari.run()
