#!/usr/bin/env python3
"""Setup script for rouge-torch package."""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    with open(readme_path, 'r', encoding='utf-8') as f:
        return f.read()

# Read version from __init__.py
def get_version():
    try:
        version = {}
        with open("rouge_torch/__init__.py") as fp:
            exec(fp.read(), version)
        return version['__version__']
    except (FileNotFoundError, KeyError):
        return "0.1.0"  # Fallback version

setup(
    name="rouge-torch",
    version=get_version(),
    author="Rouge-Torch Contributors",
    author_email="contact@rouge-torch.dev",
    description="Fast differentiable ROUGE scores for PyTorch neural network training",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/username/rouge-torch",
    project_urls={
        "Bug Tracker": "https://github.com/username/rouge-torch/issues",
        "Documentation": "https://rouge-torch.readthedocs.io/",
        "Source Code": "https://github.com/username/rouge-torch",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
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
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "isort",
            "flake8",
            "mypy",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "rouge", 
        "pytorch", 
        "nlp", 
        "natural language processing",
        "text generation",
        "evaluation metrics",
        "differentiable",
        "neural networks",
        "machine learning",
        "summarization",
        "translation"
    ],
)