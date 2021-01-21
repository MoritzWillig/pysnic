import setuptools


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setuptools.setup(
    name='pysnic',
    version='1.0.2',
    description='SNIC superpixels algorithm',
    long_description='''
Python-only implementation of the SNIC superpixels algorithm (https://www.epfl.ch/labs/ivrl/research/snic-superpixels/).

Typical usage example:
::

    from pysnic.algorithms.snic import snic
    from pysnic.algorithms.polygonize import polygonize
    from pysnic.algorithms.ramerDouglasPeucker import RamerDouglasPeucker

    segmentation, distance_map, number_of_segments = snic(
        lab_image, 500, 0.01,
        update_func=lambda num_pixels: print("processed %05.2f%%" % (num_pixels * 100 / number_of_pixels)))

    rdp = RamerDouglasPeucker(10)
    graphs = polygonize(segmentation, seeds, rdp)

This project is maintained under: https://github.com/MoritzWillig/pysnic
''',
    keywords=["image processing", "computer vision", "image segmentation", "superpixels", "SNIC"],
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Image Recognition"],
    url='https://github.com/MoritzWillig/pysnic',
    author='Moritz Willig',
    author_email='moritz@rise-of-light.de',
    license='MIT',
    packages=setuptools.find_packages(),
    include_package_data=True,
    extras_require={
        'examples': ["scikit-image", "numpy", "matplotlib", "pillow"],
    },
    zip_safe=False,
    python_requires='>=3.5'
)
