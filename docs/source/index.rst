.. Gitnet documentation master file, created by
   sphinx-quickstart on Mon Jun  6 14:28:27 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: gitnet.png
  :height: 200px
  :width: 200 px
  :align: center


**gitnet**
==================================

``gitnet`` is a Python 3 library with user friendly tools for collecting, cleaning, and exporting datasets from local Git repositories, as well as creating network models and visualizations. The primary purpose of `gitnet` is to provide scholarly tools to study the collaboration structure of free and open source software development projects, but may also be of use to organizations, project managers, and curious coders.

``gitnet`` is currently under active development by the University of Waterloo's **NetLab**. The current build offers flexible tools for working with local Git repositories. Future iterations will include support for collecting and modelling issue report and pull request data, tools for analyzing contributors' communication networks, reproducible data collection, and more tools for increased flexibility. If you are curious about our project, want tips regarding how to use ``gitnet``, find a bug, or wish to request a feature, please feel free to email a contributor or submit an issue report.

Contents:

.. toctree::
   :maxdepth: 2

.. automodule:: gitnet
  :members:
  :member-order: alphabetical

.. autoclass:: CommitLog
  :members:
  :member-order: alphabetical

.. autoclass:: Log
  :members:
  :member-order: alphabetical

.. autoclass:: MultiGraphPlus
  :members:
  :member-order: alphabetical

.. autoclass:: Get_Log
  :members:
  :member-order: alphabetical

.. autoclass:: helpers
  :members:
  :member-order: alphabetical

.. autoexception:: Exceptions
  :members:
  :inherited-members:
  :member-order: alphabetical

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
* :ref:`gitnet`
