"""
YiRage PyPI Distribution Setup

This setup file is for distributing YiRage on PyPI without requiring 
users to have CUDA, Rust, or other build tools installed.
"""

import os
import sys
from pathlib import Path
from setuptools import setup, find_packages

# Read version
version_file = Path(__file__).parent / "python" / "yirage" / "version.py"
version_globals = {}
with open(version_file, "r") as f:
    exec(f.read(), version_globals)
__version__ = version_globals["__version__"]

# Read README
readme_file = Path(__file__).parent / "README.md"
try:
    with open(readme_file, "r", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "YiRage: A Multi-Level Superoptimizer for Tensor Algebra with Multi-Backend Support"

# Core dependencies (no build-time dependencies)
install_requires = [
    "torch>=2.4",
    "numpy>=1.21.0",
    "tqdm",
    "accelerate==1.8.0",
]

setup(
    name="yica-yirage",
    version=__version__,
    description="YiRage: A Multi-Level Superoptimizer for Tensor Algebra with Multi-Backend Support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="YICA Team",
    author_email="team@yica.ai",
    url="https://github.com/chenxingqiang/yica-yirage",
    project_urls={
        "Bug Tracker": "https://github.com/chenxingqiang/yica-yirage/issues",
        "Documentation": "https://yica-yirage.readthedocs.io",
        "Source Code": "https://github.com/chenxingqiang/yica-yirage",
    },
    packages=find_packages(where="python"),
    package_dir={"": "python"},
    package_data={
        "yirage": [
            "*.py",
            "backends/*.py",
            "utils/*.py",
        ],
    },
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=install_requires,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
            "pre-commit",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme",
            "myst-parser",
        ],
        "full": [
            "cmake>=3.24",
            "cython>=0.28",
            "z3-solver==4.15",
            "graphviz",
        ],
        "llvm": [
            "llvmlite>=0.40.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: C++",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Compilers",
        "Topic :: System :: Hardware",
    ],
    keywords=[
        "tensor", "compiler", "optimization", "llm", "inference",
        "cuda", "cpu", "mps", "llvm", "deep-learning", "ai",
        "performance", "multi-backend", "hardware-acceleration"
    ],
    license="Apache-2.0",
    zip_safe=False,
)
