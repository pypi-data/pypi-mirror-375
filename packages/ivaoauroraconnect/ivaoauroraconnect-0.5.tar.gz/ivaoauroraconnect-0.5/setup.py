from setuptools import setup, find_packages


def readme():
    with open("README.md", "r") as f:
        return f.read()


setup(
    name="ivaoauroraconnect",
    version="0.5",
    author="LevLvovich1",
    author_email="levlogvinov@gmail.com",
    description="This is library for work with IVAO Aurora",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/LevLvovich1/ivaoauroraconnect",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="ivao",
    project_urls={"GitHub": "https://github.com/LevLvovich1/ivaoauroraconnect"},
    python_requires=">=3.13",
)
