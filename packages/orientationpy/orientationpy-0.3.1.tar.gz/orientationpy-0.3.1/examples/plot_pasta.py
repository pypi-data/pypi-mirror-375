"""
Example 7: Spaghetti & Lasagne
==============================

This example shows how to deal with a dataset that containes membranes and
fibres. The data we use is an x-ray tomography of spaghetti and lasagne broken
into pieces.
"""

import matplotlib.animation
import matplotlib.pyplot as plt
import numpy
import numpy as np
import orientationpy
import pyvista as pv
import scipy
import skimage
import tifffile

##########################################
# Load and inspect data
##########################################
#
img = tifffile.imread("../data/3D/pasta_med2_crop128_8bit.tif")


def _update(i):
    mpl_img.set_array(img[i])
    return (mpl_img,)


fig, ax = plt.subplots(figsize=(7, 3))
mpl_img = ax.imshow(img[0], cmap="Greys_r")
animation = matplotlib.animation.FuncAnimation(fig, _update, len(img), interval=100, blit=True)
plt.show()

gradients = orientationpy.computeGradient(img, mode="gaussian")

structure_tensors = orientationpy.computeGradientStructureTensor(img, sigma=7, mode="gaussian")

structure_type = orientationpy.computeStructureType(structure_tensors)

orientations = orientationpy.computeOrientation(structure_tensors, mode="fibre")

##########################################
# Visualize in 3D
##########################################
#
grid = pv.ImageData()
grid.dimensions = numpy.array(img.shape) + 1

grid.origin = (0, 0, 0)
# Set the pixel size
grid.spacing = (0.1, 0.1, 0.1)

grid.cell_data["values"] = img.flatten(order="C")
grid.cell_data["phi"] = orientations["phi"].flatten(order="C")
grid.cell_data["theta"] = orientations["theta"].flatten(order="C")
grid.cell_data["structure_type"] = structure_type.flatten(order="C")

thresh = skimage.filters.threshold_otsu(img)
pasta = grid.threshold([thresh, numpy.max(img)])

plotter = pv.Plotter(shape=(1, 2), border=False)
plotter.subplot(0, 0)
plotter.add_mesh(pasta, scalars="theta", cmap="plasma", clim=(0, 90))
plotter.show_grid()
plotter.subplot(0, 1)
plotter.add_mesh(pasta, scalars="phi", cmap="hsv", clim=(0, 360), copy_mesh=True)
plotter.show_grid()
plotter.link_views()
plotter.show()

##########################################
# Plot Structure Type
##########################################
#
pasta.plot(scalars="structure_type", cmap="bwr", show_grid=True, clim=(-1.0, 1.0))

##########################################
# Instance Segmentation
##########################################
#
mask = img > thresh
distance = scipy.ndimage.distance_transform_edt(mask)
eroded_mask = scipy.ndimage.binary_erosion(mask, iterations=7)
markers, _ = scipy.ndimage.label(eroded_mask)

labels = skimage.segmentation.watershed(-distance, markers, mask=mask)

grid.cell_data["labels"] = labels.flatten(order="C")
pasta = grid.threshold([thresh, numpy.max(img)])

pasta.plot(scalars="labels", cmap="tab20", show_grid=True)

grid.set_active_scalars("labels")
components = grid.split_values()
# Remove background component
_ = components.pop(0)

for key in components.keys():
    component = components[key]
    component_type = 1 if np.median(component["structure_type"]) > 0 else -1
    component_theta = np.median(component["theta"])
    component_phi = np.median(component["phi"])
    component.cell_data["component_type"] = np.full(component.n_cells, component_type)
    component.cell_data["component_theta"] = np.full(component.n_cells, component_theta)
    component.cell_data["component_phi"] = np.full(component.n_cells, component_phi)

components.plot(scalars="component_type", cmap="bwr", show_grid=True)
# components.plot(scalars="component_theta", cmap="plasma", show_grid=True)
# components.plot(scalars="component_phi", cmap="hsv", show_grid=True)

##########################################
# Plot angles per object
##########################################
#
plotter = pv.Plotter(shape=(1, 2), border=False)
plotter.subplot(0, 0)
plotter.add_mesh(components, scalars="component_theta", cmap="plasma", clim=(0, 90))
plotter.subplot(0, 1)
plotter.add_mesh(components, scalars="component_phi", cmap="hsv", clim=(0, 360), copy_mesh=True)
plotter.link_views()
plotter.show()
