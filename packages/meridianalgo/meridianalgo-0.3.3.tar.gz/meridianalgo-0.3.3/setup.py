"""
Setup script for MeridianAlgo library
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="meridianalgo",
    version="0.3.3",
    author="MeridianAlgo",
    author_email="meridianalgo@gmail.com",
    description="Advanced stock prediction system using Yahoo Finance - Zero setup, no API keys required",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/MeridianAlgo/Packages",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    keywords="stock prediction, yahoo finance, machine learning, AI, financial analysis, no api keys, zero setup",
    project_urls={
        "Bug Reports": "https://github.com/MeridianAlgo/Packages/issues",
        "Source": "https://github.com/MeridianAlgo/Packages",
        "Documentation": "https://github.com/MeridianAlgo/Packages#readme",
    },
) 