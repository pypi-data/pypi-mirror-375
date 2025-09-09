from setuptools import setup, find_packages

setup(
    name="pycutwm",
    version="0.1.0",
    description="Modelling tools for package cuTWM(3+1)D",
    author="Alfredo Daniel Sanchez",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib",
        "imageio"
    ],
    python_requires=">=3.8",
)
