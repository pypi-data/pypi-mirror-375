============
Installation
============

Requirements
##############

You need **python 3.6+**

Setup
##############

We recommend setting up a virtual environment to keep this installation separate from your system python.

Option 1 (recommended)
-----------------------
This means installing from pip. Activate your virtual environment and then do:

.. code-block:: bash

    pip install orientationpy


Option 2 (for developers)
--------------------------
You can clone our `gitlab repository`_. Make sure your virtual environment is activated:

.. code-block:: bash

    # Download code
    git clone https://gitlab.com/epfl-center-for-imaging/orientationpy.git

    # Enter code folder
    cd orientationpy

    # Install orientationpy and dependencies into your virtualenv
    pip install .


Congratulations, you have `orientationpy` installed!
If you installed from git you can check it's working like this:

.. code-block:: bash

    cd examples

    pip install tifffile

    python plot_fibres_2d.py



.. _gitlab repository: https://gitlab.com/epfl-center-for-imaging/orientationpy/
