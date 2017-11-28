pyzem: A Python library for connectome analysis
-----------------------------------------------

pyzem is a Python library designed for analyzing connectomes produced from microscope data. In such a connectome, there are often neurons represented by the SWC format and connections represented by synaptic puncta. Therefore, pyzem has several modules for those components.

Installation
------------

Prerequisite: Python 3

1. Clone the source code from github:

.. code-block:: bash

    $ git clone https://github.com/janelia-flyem/pyzem.git pyzem

2. Go to the source directory and run installation:

.. code-block:: bash

    $ make init
    $ make install

If your system does not have Python 3, you can install miniconda to set up the environment: https://conda.io/miniconda.html

Examples
--------

.. code-block:: python

    from pyzem import swc
    tree = swc.SwcTree()
    #Load a SWC file
    tree.load('tests/data/test.swc')
    #Print the overall length of the structure
    print(tree.length())

