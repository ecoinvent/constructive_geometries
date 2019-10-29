from setuptools import setup
import os

setup(
    name='constructive_geometries',
    version="0.7",
    packages=["constructive_geometries"],
    package_data={'constructive_geometries': [
        "data/faces.gpkg",
        "data/faces.json"
    ]},
    author="Chris Mutel",
    author_email="cmutel@gmail.com",
    license=open('LICENSE', encoding='utf-8').read(),
    install_requires=[
        "country_converter",
        "wrapt",
    ],
    url="https://github.com/cmutel/constructive_geometries",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    description='Simple tools to define world locations from a set of topological faces and set algebra',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
    ],
)
