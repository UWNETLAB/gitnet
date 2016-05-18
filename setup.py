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
    description='Gitnet is an analysis tool for git and other VCS managed open-source projects.',
    long_description=long_description,
    url='http://networkslab.org/',
    author='Jillian Anderson, Joel Becker, Steve McColl',
    author_email='UNKNOWN',
    license='GNU 3.0',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Researchers',
        'Topic :: Research :: Quantitative Analysis',
        'License :: OSI Approved :: GNU 3.0 License',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='research open-source github social-networks collaboration',
    packages=find_packages(exclude=['tests']),
    install_requires=['bash'],
)
