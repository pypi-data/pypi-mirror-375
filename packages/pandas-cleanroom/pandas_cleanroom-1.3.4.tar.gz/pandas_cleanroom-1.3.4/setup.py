"""Setup script for cleanroom package."""

from setuptools import setup, find_packages

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read version from the package
with open("cleanroom/__init__.py", "r", encoding="utf-8") as fh:
    for line in fh:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break
    else:
        version = "1.0.0"

setup(
    name="pandas-cleanroom",
    version=version,
    author="Your Name",
    author_email="your.email@example.com",
    description="Tiny, extensible pandas utilities for aliasing and basic data cleaning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/cleanroom",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
    },
    keywords="pandas data cleaning preprocessing etl",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/cleanroom/issues",
        "Source": "https://github.com/yourusername/cleanroom",
        "Documentation": "https://github.com/yourusername/cleanroom#readme",
    },
)
