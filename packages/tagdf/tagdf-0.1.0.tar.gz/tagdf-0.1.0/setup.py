"""Setup configuration for tagdf.

tagdf is a minimal scaffold at this stage to validate package naming
and distribution. It will provide tools for annotating and labelling
Pandas DataFrames and general Python objects.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tagdf",
    version="0.1.0",
    author="Idin",
    author_email="py@idin.net",
    description="Tools for annotating and labelling DataFrames and Python objects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/idin/tagdf",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.11",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
        ],
    },
)
