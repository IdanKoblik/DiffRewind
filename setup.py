from setuptools import setup, find_packages

setup(
    name="diffdewind",
    version="0.1.0",
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
            "diffdewind=src.main:main",
        ],
    },
)