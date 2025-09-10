"""
Setup configuration for CANS (Causal Adaptive Neural System) framework.
"""

import os
import re
from setuptools import setup, find_packages

# Read version from __init__.py
def get_version():
    with open(os.path.join("cans", "__init__.py"), "r") as f:
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
        if version_match:
            return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

# Read long description from README
def get_long_description():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def get_requirements():
    with open("requirements.txt", "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Get optional dependencies
def get_extras_require():
    return {
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=5.0.0",
            "mypy>=0.990",
            "pre-commit>=2.20.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "sphinxcontrib-napoleon>=0.7",
            "myst-parser>=0.18.0",
        ],
        "notebooks": [
            "jupyter>=1.0.0",
            "jupyterlab>=3.4.0",
            "ipykernel>=6.15.0",
            "ipywidgets>=8.0.0",
        ],
        "visualization": [
            "plotly>=5.15.0",
            "seaborn>=0.12.0",
            "matplotlib>=3.7.0",
        ],
        "all": [
            # All optional dependencies
        ]
    }

# Populate 'all' extra
extras = get_extras_require()
extras["all"] = [dep for deps in extras.values() for dep in deps if isinstance(dep, str)]

setup(
    name="cans-framework",
    version=get_version(),
    author="Durai Rajamanickam",
    author_email="durai@infinidatum.net",
    description="A production-ready deep learning framework for causal inference on structured, textual, and heterogeneous data",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/rdmurugan/cans-framework",
    project_urls={
        "Bug Reports": "https://github.com/rdmurugan/cans-framework/issues",
        "Source": "https://github.com/rdmurugan/cans-framework",
        "Documentation": "https://github.com/rdmurugan/cans-framework#readme",
        "Changelog": "https://github.com/rdmurugan/cans-framework/releases",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "docs"]),
    classifiers=[
        # Development Status
        "Development Status :: 4 - Beta",
        
        # Intended Audience
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        
        # Topic
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        
        # License
        "License :: Other/Proprietary License",
        
        # Programming Language
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        
        # Operating System
        "Operating System :: OS Independent",
        
        # Environment
        "Environment :: Console",
        "Environment :: GPU :: NVIDIA CUDA",
        
        # Natural Language
        "Natural Language :: English",
    ],
    python_requires=">=3.8",
    install_requires=get_requirements(),
    extras_require=extras,
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "causal-inference", 
        "deep-learning", 
        "graph-neural-networks", 
        "transformers", 
        "counterfactual", 
        "treatment-effects",
        "machine-learning",
        "pytorch",
        "bert",
        "gnn",
        "causal-ai",
        "econometrics",
        "statistics"
    ],
    entry_points={
        "console_scripts": [
            "cans-validate=cans.cli:validate_assumptions",
            "cans-evaluate=cans.cli:evaluate_model",
        ],
    },
    package_data={
        "cans": [
            "data/*.json",
            "config/*.yaml",
            "config/*.yml",
        ],
    },
)