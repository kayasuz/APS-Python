
from setuptools import setup

setup(
    name="package",
    version="0.0.1",
    python_requires=">=3.6",
    package_dir={"package": "src/package"},
    packages=["package", "package.exercicios"]
)

