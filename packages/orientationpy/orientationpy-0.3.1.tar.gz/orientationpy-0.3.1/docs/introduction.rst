OrientationPy
==============

Welcome to orientationpy, a small python package to help you analyse orientations in 2D and 3D.
It offers tools to:

  - measure local orientations in an image
    (either at each pixel or in boxes)

  - plot orientation maps

  - plot and analyse orientation distributions

OrientationPy is the pythonic successor to the well-loved `OrientationJ`_ Fiji Plugin (`github`_) from the BIG (`Biomedical Imaging Group`_) in EPFL.
It is a library that takes in 2D images or 3D volumes and computes the orientation of the greylevels.
A key step is the computation of image gradients, for which we offer a number of different techniques.

Please have a read of the :ref:`definitions`, and check out the :ref:`orientationpyExamples`!


.. _OrientationJ: http://bigwww.epfl.ch/demo/orientation/
.. _github: https://github.com/Biomedical-Imaging-Group/OrientationJ
.. _Biomedical Imaging Group: https://github.com/Biomedical-Imaging-Group/OrientationJ
