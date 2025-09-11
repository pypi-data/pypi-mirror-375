
from setuptools import setup, find_packages

setup(
    name="NetBridge",
    version="0.0.3",
    author="Leonardo Nery",
    description="Uma biblioteca simples para Comunicação interProgramas e Transferencia de arquivos Locais ou Remotos.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
