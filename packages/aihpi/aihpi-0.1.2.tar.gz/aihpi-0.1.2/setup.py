"""Setup script for aihpi package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="aihpi",
    version="0.1.0",
    author="Felix Boelter",
    author_email="felix.boelter@example.com",
    description="AI High Performance Infrastructure - Distributed job submission for SLURM clusters",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/aihpi",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: System :: Distributed Computing",
    ],
    python_requires=">=3.8",
    install_requires=[
        "submitit>=1.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black",
            "flake8",
            "mypy",
        ],
        "huggingface": [
            "huggingface_hub",
        ],
        "tracking": [
            "wandb",
            "mlflow",
        ],
        "all": [
            "huggingface_hub",
            "wandb", 
            "mlflow",
        ],
    },
    entry_points={
        "console_scripts": [
            "aihpi=aihpi.cli:main",
        ],
    },
    keywords="slurm distributed training ai ml pytorch llamafactory",
    project_urls={
        "Bug Reports": "https://github.com/username/aihpi/issues",
        "Source": "https://github.com/username/aihpi",
        "Documentation": "https://github.com/username/aihpi#readme",
    },
)