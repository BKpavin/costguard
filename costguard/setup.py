from setuptools import setup, find_packages

setup(
    name="costguard",
    version="0.1.0",
    description="Developer CLI tool to predict Azure infrastructure cost impact from Terraform plan JSON",
    author="CostGuard Team",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "requests>=2.31.0",
        "rich>=13.7.0",
    ],
    entry_points={
        "console_scripts": [
            "costguard=costguard.cli:main",
        ],
    },
)
