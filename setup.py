from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Description found in README.
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='gitnet',
    version='0.0.1',
    description='An analysis tool for git and other VCS managed open-source projects.',
    long_description=long_description,
    url='http://networkslab.org/gitnet',
    download_url='https://github.com/networks-lab/gitnet',
    author='Jillian Anderson, Joel Becker, Steve McColl, John McLevey',
    author_email='janderes@uwaterloo.ca, jbwbecker@uwaterloo.ca, s2mccoll@uwaterloo.ca',
    license='GPL',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'Topic :: Sociology',
        'Topic :: Text Processing',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='research open-source github social-networks collaboration linux',
    packages=find_packages(exclude=['tests']),
    install_requires=['bash', 'networkx', 'matplotlib'],
    test_suite='gitnet.tests',
)
