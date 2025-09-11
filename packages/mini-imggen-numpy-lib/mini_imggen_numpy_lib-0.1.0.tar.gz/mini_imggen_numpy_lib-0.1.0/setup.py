from setuptools import setup, find_packages


setup(
name="mini_imggen_numpy_lib",
version="0.1.0",
description="A lightweight educational Python library for toy image & text generation using NumPy only.",
author="Léo",
url="https://github.com/Leo62-glitch/mini_imggen_numpy_lib",
py_modules=["mini_imggen_numpy_lib"],
install_requires=[
"numpy",
"pillow"
],
python_requires=">=3.8",
classifiers=[
"Programming Language :: Python :: 3",
"License :: OSI Approved :: MIT License",
"Operating System :: OS Independent",
],
)