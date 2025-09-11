from setuptools import setup, find_packages

setup(
    name="mesh_decimator",
    version="0.1.0",
    description="Fast mesh decimation using RTIN",
    author="Audun Skau Hansen",
    author_email="audunsh4@gmail.com",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "numba>=0.50.0",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
