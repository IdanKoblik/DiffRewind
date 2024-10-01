from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="diffrewind",
    version="0.3.1",
    packages=find_packages(),
    install_requires=[
        "requests>=2.26.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.1.2",
        ],
    },
    entry_points={
        "console_scripts": [
            "diffrewind=main:main",
        ],
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
)
