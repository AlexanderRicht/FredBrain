import pathlib
from setuptools import setup, find_packages

setup(
    name="FredBrain",
    version="0.2.0",
    description="A Python API for retrieving Federal Reserve Economic Data at Scale and feeding it to OpenAI",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    license=pathlib.Path("LICENSE").read_text(),
    url="https://github.com/AlexanderRicht/FredBrain",
    project_urls={
        "Documentation": "https://pypi.org/project/FredBrain/",
        "Source": "https://github.com/AlexanderRicht/FredBrain",
    },
    author="Alexander Richt",
    author_email="alexander.richt1@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Utilities",
    ],
    python_requires=">=3.10",
    install_requires=["requests", "pandas", "datetime", "openai"],
    packages=find_packages(),
    include_package_data=True
)
