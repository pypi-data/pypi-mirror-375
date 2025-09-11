from setuptools import setup, find_packages

setup(
    name="mypackages-ashutosh",
    version="1.0.0",
    description="A simple demo package with math and string utilities",
    author="Ashutosh",
    packages=find_packages(),  # automatically finds 'mypackage'
    install_requires=[],  # add dependencies if needed
)
