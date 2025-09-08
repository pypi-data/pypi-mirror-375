#!/usr/bin/env python3
"""
Setup script for Terra Command
"""

from setuptools import setup, find_packages
import os

# Read the README file
this_directory = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "Terra Command AI - A natural language shell command tool with AI for zsh/bash"

setup(
    name="tai",
    version="0.1.0",
    author="Terra AGI",
    author_email="contact@terra-agi.com",
    description="Terra Command AI - A natural language shell command tool with AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/terra-agi/terra-commands",
    packages=find_packages(),
    py_modules=[],
    entry_points={
        'console_scripts': [
            'tai=tai.cli:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Shells",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=[
        "openai>=1.0.0",
    ],
    keywords="cli shell command natural-language terminal ai openai",
    project_urls={
        "Bug Reports": "https://github.com/terra-agi/terra-commands/issues",
        "Source": "https://github.com/terra-agi/terra-commands",
        "Documentation": "https://github.com/terra-agi/terra-commands#readme",
    },
)
