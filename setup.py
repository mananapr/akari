import setuptools
from akari import __version__, __author__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="akari",
    version=__version__,
    author=__author__,
    author_email="mananapr@gmail.com",
    description="Program to manage and tag your anime artwork",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mananapr/akari",
    packages=setuptools.find_packages(),
    install_requires=[
        'requests',
        'pyqt5',
        'beautifulsoup4',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        'console_scripts': [
            'akari = akari.cli:main'
        ]
    }
)
