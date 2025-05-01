from setuptools import setup, find_packages

setup(
    name="brim-veracity",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "requests>=2.25.0",
        "pydantic>=2.0.0",
        "rich>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "brim=python_node.cli:main",
        ],
    },
    description="Python CLI for Brim network with Veracity Protocol",
    python_requires=">=3.8",
) 