from setuptools import setup
import os

setup(
    name='constructive_geometries',
    version="0.3.1",
    packages=["constructive_geometries"],
    package_data={'constructive_geometries': [
        "data/faces.gpkg",
        "data/faces.json"
    ]},
    author="Chris Mutel",
    author_email="cmutel@gmail.com",
    license=open('LICENSE.txt').read(),
    install_requires=["fiona", "shapely"],
    # url="https://bitbucket.org/cmutel/brightway2-data",
    long_description=open('README.rst').read(),
    description='Tool to build new geometrical definitions from the ecoinvent topology',
    # classifiers=[
    #     'Development Status :: 5 - Production/Stable',
    #     'Intended Audience :: End Users/Desktop',
    #     'Intended Audience :: Developers',
    #     'Intended Audience :: Science/Research',
    #     'License :: OSI Approved :: BSD License',
    #     'Operating System :: MacOS :: MacOS X',
    #     'Operating System :: Microsoft :: Windows',
    #     'Operating System :: POSIX',
    #     'Programming Language :: Python',
    #     'Programming Language :: Python :: 2.7',
    #     'Programming Language :: Python :: 2 :: Only',
    #     'Topic :: Scientific/Engineering :: Information Analysis',
    #     'Topic :: Scientific/Engineering :: Mathematics',
    #     'Topic :: Scientific/Engineering :: Visualization',
    # ],
)
