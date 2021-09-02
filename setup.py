"""Only intended for development."""
import setuptools

setuptools.setup(
    name="audar",
    version="0.0.2",
    author="Konstantinos Dimitriou",
    author_email="const@embeddingspace.com",
    url="https://github.com/constd/audar",
    packages=setuptools.find_packages(),
    install_requires=[
        "pandas",
        "tqdm"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)