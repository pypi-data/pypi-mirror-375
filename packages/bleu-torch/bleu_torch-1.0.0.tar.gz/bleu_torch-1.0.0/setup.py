"""
setup.py for BLEU-Torch

This file is included for backwards compatibility.
The main configuration is in pyproject.toml
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="bleu-torch",
    version="1.0.0",
    description="PyTorch module for differentiable BLEU score computation that supports end-to-end training",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="bleu-torch contributors",
    # author_email="your-email@example.com",
    url="https://github.com/Ghost---Shadow/bleu-torch",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=[
        "torch>=1.9.0",
        "numpy>=1.19.0",
    ],
    keywords=[
        "bleu",
        "pytorch",
        "nlp",
        "differentiable",
        "neural-machine-translation",
        "evaluation",
        "training",
    ],
    project_urls={
        "Documentation": "https://github.com/Ghost---Shadow/bleu-torch#readme",
        "Repository": "https://github.com/Ghost---Shadow/bleu-torch.git",
        "Issues": "https://github.com/Ghost---Shadow/bleu-torch/issues",
    },
)
