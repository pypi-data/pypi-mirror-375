# Don't understand the new analytical decomposition, trying something brute-force
#
import os.path
import sys

import matplotlib.pyplot as plt
import numpy
import orientationpy
import pytest
import scipy
import tifffile
from tqdm import tqdm

sys.path.append("./")
sys.path.append("./test/")
import generateFibres

nPoints = 100

points = orientationpy.generateIsotropic(nPoints)

# orientationpy.plotOrientations3d(points)

zUnit = numpy.array([1.0, 0.0, 0.0])

diff = numpy.zeros(nPoints)
orientationsOut = numpy.zeros((nPoints, 3))

for n, point in enumerate(tqdm(points)):
    point /= numpy.linalg.norm(point)
    fileName = f"./data/3D/fibreTest/{point[0]:+0.3f}{point[1]:+0.3f}{point[2]:+0.3f}.tif"
    # print(fileName)
    if os.path.isfile(fileName):
        # load
        im = tifffile.imread(fileName)
    else:
        angle = numpy.rad2deg(numpy.arccos(numpy.dot(point, zUnit)))
        axis = numpy.cross(point, zUnit)
        # print(angle, axis)
        # print()
        im = generateFibres.generateFibres3D(50, angle * axis)
        tifffile.imwrite(fileName, im)

    structureTensor = orientationpy.computeGradientStructureTensorBoxes(im, 50, mode="gaussian")
    orientations = orientationpy.computeOrientation(structureTensor, mode="fiber")
    orientationsOut[n] = orientationpy.anglesToVectors(orientations).ravel()
    # print(orientations)
    # print(vec.ravel(), point)
    # diff[n] = numpy.rad2deg(numpy.arccos(numpy.dot(point, orientationsOut[n])))
    diff[n] = numpy.abs(point[0]) - numpy.abs(orientationsOut[n, 0])
    # plt.hist(orientations["theta"].ravel(), bins=90, range=[0, 360], label="theta")
    # plt.hist(orientations["phi"].ravel(), bins=90,q range=[0, 360], label="phi")
    # plt.legend()
    # plt.show()

orientationpy.plotOrientations3d(points)
orientationpy.plotOrientations3d(orientationsOut)

plt.plot(diff)
plt.show()
