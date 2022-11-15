
from setuptools import setup

setup(
    name="contador-exercicios",
    version="0.2.0",
    python_requires=">=3.6",
    install_requires=[
        "mediapipe",
        "numpy"
    ],
    package_dir={
        "cntexercicios": "cntexercicios"
    },
    packages=[
        "cntexercicios",
        "cntexercicios.exercicios",
        "cntexercicios.exercicios.flexoes",
        "cntexercicios.exercicios.polichinelos"
    ]
)

