import os
import sys
from setuptools import setup, find_packages
from pathlib import Path

# Read version
version_file = Path(__file__).parent / "python" / "yirage" / "version.py"
version_globals = {}
with open(version_file, "r") as f:
    exec(f.read(), version_globals)
__version__ = version_globals["__version__"]

# Read requirements (filtered for Python-only packages)
python_only_deps = [
    "torch>=2.4",
    "numpy>=1.21.0", 
    "tqdm",
    "accelerate==1.8.0",
]

# Read README
readme_file = Path(__file__).parent / "README.md"
try:
    with open(readme_file, "r", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "YiRage: A Multi-Level Superoptimizer for Tensor Algebra with Multi-Backend Support"

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
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=python_only_deps,
    extras_require={
        "dev": ["pytest>=6.0", "pytest-cov", "black", "flake8"],
        "docs": ["sphinx>=4.0", "sphinx-rtd-theme", "myst-parser"],
        "full": ["cmake>=3.24", "cython>=0.28", "z3-solver==4.15", "graphviz"],
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
    keywords=["tensor", "compiler", "optimization", "llm", "inference", "cuda", "cpu", "mps", "llvm"],
    license="Apache-2.0",
    zip_safe=False,
)