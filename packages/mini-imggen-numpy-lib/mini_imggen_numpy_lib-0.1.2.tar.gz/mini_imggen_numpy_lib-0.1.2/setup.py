from setuptools import setup, find_packages

setup(
    name="mini_imggen_numpy_lib",
    version="0.1.2",  # ↑ incrémente la version avant de republier
    description="A lightweight educational Python library for toy image & text generation using NumPy only.",
    author="Léo",
    url="https://github.com/Leo62-glitch/mini_imggen_numpy_lib",
    packages=find_packages(),            # <-- au lieu de py_modules
    install_requires=["numpy", "pillow"],
    python_requires=">=3.8",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)