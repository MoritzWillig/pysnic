from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='pysnic',
      version='0.1',
      description='SNIC super pixel algorithm',
      long_description='Python implementation of the SNIC algorithm (https://ivrl.epfl.ch/research/snic_superpixels)',
      keywords=['SNIC', 'super pixel', 'super pixels', 'superpixels'],
      classifiers=[
          'Programming Language :: Python :: 3.*',
          'Topic :: Image Segmentation :: Super Pixels'],
      url='https://github.com/MoritzWillig/pysnic',
      author='Moritz Willig (python translation)',
      author_email='moritz@rise-of-light.de',
      license='MIT',
      packages=['pysnic'],
      include_package_data=True,
      extras_require={
          'examples': ["skimage", "numpy", "matplotlib", "pillow"],
      },
      zip_safe=False)
