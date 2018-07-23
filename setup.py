import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mtgtools",
    version="0.8",
    author="Esko-Kalervo Salaka",
    author_email="esko.salaka@gmail.com",
    description="mtgtools is a collection of tools for easy and convenient handling and downloading of Magic: The Gathering card and set data on your computer from Scryfall and/or magicthegathering.io.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EskoSalaka/mtgtools",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Zope Public License (ZPL) Version 2.1",
        "Operating System :: OS Independent",
    ),
)