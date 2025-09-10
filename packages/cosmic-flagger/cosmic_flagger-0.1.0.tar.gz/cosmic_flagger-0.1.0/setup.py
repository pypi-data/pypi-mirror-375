from setuptools import setup

setup(
    name='cosmic-flagger',
    version='0.1.0',    
    description='A small package for flagging, verifying, and removing cosmic ray contamination from data.',
    url='https://github.com/Autumn10677/cosmic-flagger',
    author='Autumn Stephens',
    author_email='aust8150@colorado.edu',
    packages=['cosmic-flagger'],
    install_requires=['astropy',
                      'matplotlib',
                      'numpy',
                      'tqdm',
                      'jax',               
                      ],
)