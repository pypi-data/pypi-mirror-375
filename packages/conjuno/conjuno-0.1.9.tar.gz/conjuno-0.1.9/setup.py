import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
version_ns = {}  # type: ignore
with open(os.path.join(here, "conjuno", "_version.py")) as f:
    exec(f.read(), {}, version_ns)

setup(
    name="conjuno",
    version=version_ns["__version__"],
    url="https://conjuno.com",
    author="Michael Tatton",
    description="Console Jupyter Notebook",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=["conjuno"],
    python_requires=">=3.9",
    install_requires=[
        "kernel_driver>=0.0.6",
        "jupyter_client",
        "ipykernel",
    ],
    extras_require={
        "test": [
            "pytest",
        ],
    },
    entry_points={
        "console_scripts": ["conjuno = conjuno.main:cli"],
    },
    classifiers=(
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ),
)
