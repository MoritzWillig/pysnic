PySNIC
======

Python implementation of the SNIC superpixels algorithm (https://ivrl.epfl.ch/research/snic_superpixels).

::

  from pysnic.algorithms.snic import snic

  segmentation, distance_map, number_of_segments = snic(
      lab_image, 500, 0.01,
      update_func=lambda num_pixels: print("processed %05.2f%%" % (num_pixels * 100 / number_of_pixels)))


See the `examples <pysnic/examples>`_ folder for a mininimal and more advanced example.

This implementation
-------------------
The algorithm in this repository differs from the originally described algorithm to improve performance:

- Adding elements to the candidate queue is a costly operation. We therefore try to reduce the number queue insertions.

  - Introducing a distance map: The algorithm maintains a distance map which stores the closest candidate distance. This allows prechecking, if another candidate is already registered with a smaller distance, before adding it to the queue.
- Removed normalization factors from metric calculation, as they do not change the item ordering.

Publications
------------
The algorithm implemented in this package is based on the following publication:

:author: Achanta, Radhakrishna and Susstrunk, Sabine
:title: Superpixels and Polygons using Simple Non-Iterative Clustering
:booktitle: IEEE Conference on Computer Vision and Pattern Recognition (CVPR)
:year: 2017

Repository
----------
This package is maintained under https://github.com/MoritzWillig/pysnic

License
-------
MIT License see `LICENSE.md <LICENSE.md>`_