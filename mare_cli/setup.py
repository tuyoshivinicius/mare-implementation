#!/usr/bin/env python3
"""
Setup script for MARE CLI - Multi-Agent Collaboration Framework for Requirements Engineering
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="mare-cli",
    version="1.0.0",
    author="Manus AI",
    author_email="contact@manus.ai",
    description="Multi-Agent Collaboration Framework for Requirements Engineering CLI",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/manus-ai/mare-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Requirements Engineering",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "mare=mare.cli.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "mare": [
            "config/templates/*.yaml",
            "config/templates/*.json",
        ],
    },
    keywords="requirements engineering, multi-agent, langchain, langgraph, cli, ai",
    project_urls={
        "Bug Reports": "https://github.com/manus-ai/mare-cli/issues",
        "Source": "https://github.com/manus-ai/mare-cli",
        "Documentation": "https://mare-cli.readthedocs.io/",
    },
)

