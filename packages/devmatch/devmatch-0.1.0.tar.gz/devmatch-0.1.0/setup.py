"""Setup script for DevMatch CLI."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="devmatch",
    version="0.1.0",
    author="DevMatch Team",
    author_email="team@devmatch.dev",
    description="A minimal developer collaborative platform client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/devmatch/devmatch-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.0.0",
        "requests>=2.25.0",
        "firebase-admin>=6.0.0",
        "python-dotenv>=0.19.0",
    ],
    package_data={
        "devmatch": ["service-key.json"],
    },
    entry_points={
        "console_scripts": [
            "devmatch=devmatch.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)