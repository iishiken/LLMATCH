from setuptools import setup, find_packages

setup(
    name="medical-analyzer",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "openai",
        "openpyxl"  # Excelファイルの読み書きに必要
    ]
) 