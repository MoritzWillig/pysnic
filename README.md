# PySNIC
Python-only implementation of the SNIC superpixels algorithm (https://www.epfl.ch/labs/ivrl/research/snic-superpixels/).
```python
from pysnic.algorithms.snic import snic
from pysnic.algorithms.polygonize import polygonize
from pysnic.algorithms.ramerDouglasPeucker import RamerDouglasPeucker

# compute segmentation from image
segmentation, distance_map, centroids = snic(
    lab_image, 500, 0.01,
    update_func=lambda processed_pixels: print("processed %05.2f%%" % (processed_pixels * 100 / number_of_pixels)))

# compute polygonization from segmentation
rdp = RamerDouglasPeucker(10)
graphs = polygonize(segmentation, seeds, rdp)
```

See the [examples](pysnic/examples) folder for a minimal and more advanced example of the SNIC algorithm, as well as a
graph extraction and polygonization.

## Installing PySNIC
Install PySNIC using `pip`:
```
pip install pysnic
```

## Technical details
The algorithm in this repository differs from the originally described algorithm to improve performance:
* Adding elements to the candidate queue is a costly operation. We therefore try to reduce the number queue insertions.
  * Introducing a distance map: The algorithm maintains a distance map which stores the closest candidate distance. This allows prechecking, if another candidate is already registered with a smaller distance, before adding it to the queue.
* Removed normalization factors from metric calculation, as they do not change the item ordering.

### Performance
This repository contains a *python only* implementation. Due to large numbers of single-pixel image accesses the python
internal bounds-checking is likely to slow down the runtime compared to a C/C++ implementation.

Since the algorithm performs large amounts of single pixel accesses, the runtime is greatly reduced by **passing
'normal' python arrays** (in contrast to using `numpy.ndarray`s or `PIL.image`s) to the `snic`-method.

### Dataformats
Pixel positions are expected to be [x,y] integer coordinates. The coordinate frame for edge positions is offset by 0.5.
(Convert edge positions to image coordinates by adding 0.5). Images are expected to be 3d row-major raw python
arrays (`image[row][column][features]`).

## Publications
The SNIC algorithm implemented in this package is based on the following publication:
```
@inproceedings{snic_cvpr17,
  author = {Achanta, Radhakrishna and Susstrunk, Sabine},
  title = {Superpixels and Polygons using Simple Non-Iterative Clustering},
  booktitle = {IEEE Conference on Computer Vision and Pattern Recognition (CVPR)},
  year = {2017}
}
```

## Repository
This package is maintained under https://github.com/MoritzWillig/pysnic

## License
MIT License see [LICENSE.md](LICENSE.md)
