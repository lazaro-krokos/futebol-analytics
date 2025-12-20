from setuptools import setup, find_packages

setup(
    name="futebol-analytics",
    version="1.0.0",
    author="Seu Nome",
    description="Sistema de análise de dados de futebol",
    packages=find_packages(),
    install_requires=[
        line.strip() for line in open('requirements.txt').readlines()
    ],
    python_requires=">=3.8",
)