from setuptools import setup
import os

setup(
    name='constructive_geometries',
    version="0.4.1",
    packages=["constructive_geometries"],
    package_data={'constructive_geometries': [
        "data/faces.gpkg",
        "data/faces.json"
    ]},
    author="Chris Mutel",
    author_email="cmutel@gmail.com",
    license=open('LICENSE.txt', encoding='utf-8').read(),
    install_requires=["fiona", "shapely"],
    url="https://bitbucket.org/cmutel/py-constructive-geometries",
    long_description=open('README.rst', encoding='utf-8').read(),
    description='Tool to build new geometrical definitions from the ecoinvent topology',
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
