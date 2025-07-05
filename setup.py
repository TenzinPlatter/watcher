"""
Setup configuration for watcher package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = requirements_file.read_text().strip().split('\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="watcher",
    version="0.1.0",
    author="Tenzin",
    description="Multi-directory file watcher with automated git commits",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'watcher': ['../templates/*'],
    },
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'watcher=watcher.cli:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Version Control :: Git",
        "Topic :: System :: Filesystems",
        "Topic :: System :: Monitoring",
    ],
    keywords="git automation file-watcher commit dotfiles",
    project_urls={
        "Source": "https://github.com/TenzinPlatter/watcher",
        "Bug Reports": "https://github.com/TenzinPlatter/watcher/issues",
    },
)