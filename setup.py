from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="mtgtools",
    version="0.9.62",
    author="Esko-Kalervo Salaka",
    author_email="esko.salaka@gmail.com",
    description=
    "Collection of tools for easy handling of Magic: The Gathering card and set data on your computer from Scryfall and/or magicthegathering.io.",
    long_description=long_description,
    KEYWORDS=["Magic: The Gathering", "Developer", "Scryfall", "mtg"],
    long_description_content_type="text/markdown",
    url="https://github.com/EskoSalaka/mtgtools",
    packages=find_packages(exclude=("tests", )),
    namespace_packages=['mtgtools'],
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    install_requires=['ZODB', 'requests', 'PIL'],
)
