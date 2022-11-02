
from setuptools import setup

setup(
    name="contador-exercicios",
    version="0.0.1",
    python_requires=">=3.6",
    install_requires=["mediapipe"],
    package_dir={"cntexercicios": "src/cntexercicios"},
    packages=["cntexercicios", "cntexercicios.exercicios", "cntexercicios.exercicios.flexoes"]
)

