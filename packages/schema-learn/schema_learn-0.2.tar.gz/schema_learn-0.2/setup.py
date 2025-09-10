from setuptools import setup

setup(name='schema_learn',
      version='0.2',
      description='Framework for integrating heterogeneous modalities of data',
      url='http://github.com/rs239/schema',
      author='Rohit Singh',
      author_email='rsingh@alum.mit.edu',
      license='MIT',
      packages=['schema'],
      install_requires = 'numpy,scipy,pandas,scikit-learn,cvxopt'.split(','),
      zip_safe=False)
