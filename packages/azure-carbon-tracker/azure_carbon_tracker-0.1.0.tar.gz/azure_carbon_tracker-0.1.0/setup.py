from setuptools import setup, find_packages

setup(
    name="azure-carbon-tracker",
    version="0.1.0",
    description="Azure carbon tracking via Cost Management API",
    author="Boris Ruf",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pandas",
        "requests",
        "azure-identity"
    ],
    package_data={
        "azure-carbon-tracker": ["data/*.csv"]
    },
    python_requires=">=3.8",
)