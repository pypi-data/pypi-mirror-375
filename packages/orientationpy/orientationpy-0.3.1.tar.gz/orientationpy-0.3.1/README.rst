========================================================================
OrientationPy - greylevel orientation computation for 2D and 3D images
========================================================================

.. image:: https://badge.fury.io/py/orientationpy.png
    :target: http://badge.fury.io/py/orientationpy

.. image:: https://gitlab.com/epfl-center-for-imaging/orientationpy/badges/main/pipeline.svg
    :target: https://gitlab.com/epfl-center-for-imaging/orientationpy/-/commits/main

.. image:: https://gitlab.com/epfl-center-for-imaging/orientationpy/badges/main/coverage.svg
   :target: https://epfl-center-for-imaging.gitlab.io/orientationpy/coverage/

OrientationPy is the pythonic successor to the well-loved `OrientationJ`_ Fiji Plugin (`github`_) from the BIG (`Biomedical Imaging Group`_) in EPFL.
It is a library that takes in 2D images or 3D volumes and computes the orientation of the greylevels.
A key step is the computation of image gradients, for which we offer a number of different techniques.

Please visit the `OrientationPy online docs`_.


Highlights
===========

Please see the `Example Gallery`_ for some small examples of the use of the code, allowing the computation of orientations maps like this:


.. figure:: https://epfl-center-for-imaging.gitlab.io/orientationpy/_images/sphx_glr_plot_fibres_2d_005.png
    :width: 400
    :align: center



Other noteworthy python projects
=================================

Other orientation or structure tensor software that we're aware of in python:

  - `skimage.feature.structure_tensor`_: Sobel filter for gradient
  - `structure-tensor`_: Only using finite differences for gradient
  - `pynamix.measure.orientation_map`_: FFT-based approach
  - `PyTextureAnalysis`_: 2D orientation package with overlay rendering


Acknowledgements
=================

 - The initial prototype was coded by Alexandru Vasile during a 6-week visit to the EPFL Center for Imaging, supported by Mariana Verezhak from PSI

 - We used some of this data for testing: https://zenodo.org/record/5483719#.Yyra4vFBy2A

 - We initialised this repository from a cookie-cutter: https://github.com/Nekroze/cookiecutter-pypackage

.. _OrientationJ: http://bigwww.epfl.ch/demo/orientation/
.. _github: https://github.com/Biomedical-Imaging-Group/OrientationJ
.. _Biomedical Imaging Group: https://github.com/Biomedical-Imaging-Group/OrientationJ

.. _OrientationPy online docs: https://epfl-center-for-imaging.gitlab.io/orientationpy/index.html
.. _Example Gallery: https://epfl-center-for-imaging.gitlab.io/orientationpy/orientationpy_examples/index.html


.. _skimage.feature.structure_tensor: https://scikit-image.org/docs/stable/api/skimage.feature.html#skimage.feature.structure_tensor
.. _structure-tensor: https://pypi.org/project/structure-tensor/
.. _pynamix.measure.orientation_map: https://scigem.github.io/PynamiX/build/html/notebooks/Fibres.html
.. _PyTextureAnalysis: https://github.com/ajinkya-kulkarni/PyTextureAnalysis


History
========

 - 0.3.0.0 (2023-08-07) Closed form solution for eigenvalue decomposition

 - 0.2.0.4 (2023-01-20) Anisotropy of voxel sizes implemented

 - 0.2.0.3 (2023-01-13) Moved code to `/src/orientationpy` so it gets packaged?

 - 0.2.0.2 (2023-01-13) Moved code to `/src` so it gets packaged?

 - 0.2.0.1 (2023-01-13) Moved to `pyproject.toml`

 - 0.2.0.0 (2023-01-13) First version on pip (non-working due to requirements.txt)
