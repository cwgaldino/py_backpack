.. Lines starting with two dots are special commands. But if no command can be found, the line is considered as a comment

===========
py_backpack
===========

This repository aims at providing useful modules and code snippets that I use almost everyday.




Installation
==================

1) Using pip straight from GitHub

.. code-block:: bash

  pip install git+https://github.com/cwgaldino/py_backpack

2) Without installing. Clone (or download) the GitHub repository and use

>>> import sys
>>> sys.path.append('<path-to-py_backpack>')


Usage
======

>>> import backpack.filemanip as fm
>>> import backpack.figmanip as figm
>>> import backpack.arraymanip as am
>>> import backpack.interact as interact
>>> from backpack.model_functions import gaussian_fwhm
